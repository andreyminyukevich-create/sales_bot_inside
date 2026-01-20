import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

import config
import parser
from database import User, Lead, Message as DBMessage, LeadStatus
from states import MainMenu, PPFFlow
from keyboards import (
    get_main_menu,
    get_ppf_variants,
    get_ppf_zones_examples,
)

router = Router()
logger = logging.getLogger(__name__)


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_user_name(message: Message) -> str:
    """Получить имя пользователя для обращения"""
    if message.from_user.first_name:
        return message.from_user.first_name
    elif message.from_user.username:
        return message.from_user.username
    return "друг"


async def get_or_create_user(db: Session, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> User:
    """Получить или создать пользователя"""
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


async def save_message(db: Session, user_id: int, text: str, lead_id: int = None, is_from_admin: bool = False):
    """Сохранить сообщение в историю"""
    msg = DBMessage(
        user_id=user_id,
        text=text,
        lead_id=lead_id,
        is_from_admin=is_from_admin
    )
    db.add(msg)
    db.commit()


async def get_or_create_lead(db: Session, user_id: int) -> Lead:
    """Получить активный лид или создать новый"""
    # Ищем активный лид (NEW или IN_WORK)
    lead = db.query(Lead).filter(
        Lead.user_id == user_id,
        Lead.status.in_([LeadStatus.NEW, LeadStatus.IN_WORK])
    ).order_by(Lead.created_at.desc()).first()
    
    if not lead:
        lead = Lead(user_id=user_id)
        db.add(lead)
        db.commit()
        db.refresh(lead)
    
    return lead


async def update_lead_data(db: Session, lead: Lead, **kwargs):
    """Обновить данные лида"""
    for key, value in kwargs.items():
        if value is not None:
            setattr(lead, key, value)
    
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)


def check_antispam(db: Session, user_id: int) -> tuple[bool, str]:
    """
    Проверка антиспама (лимит 2 заявки в час)
    
    Returns:
        (можно_создавать, сообщение_об_ошибке)
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        return True, ""
    
    # Проверяем время последней заявки
    if user.last_lead_created_at:
        time_since_last = datetime.utcnow() - user.last_lead_created_at
        
        # Если прошло меньше часа
        if time_since_last < timedelta(hours=1):
            # Проверяем счётчик
            if user.leads_count_last_hour >= 2:
                # Получаем последнюю заявку
                last_lead = db.query(Lead).filter(
                    Lead.user_id == user_id
                ).order_by(Lead.created_at.desc()).first()
                
                if last_lead:
                    car_info = f"{last_lead.car_brand} {last_lead.car_model} {last_lead.car_year}" if last_lead.car_brand else "ваше авто"
                    return False, f"Вы уже создали заявку на {car_info}. Хотите составить ещё одну?"
    
    return True, ""


# ==================== ОБРАБОТЧИК /START ====================

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, db_session):
    """Команда /start - главное меню"""
    db: Session = db_session()
    
    try:
        # Создаём/обновляем пользователя
        await get_or_create_user(
            db,
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        # Сбрасываем состояние
        await state.clear()
        
        name = get_user_name(message)
        
        await message.answer(
            f"Здравствуйте, {name}! 👋\n\n"
            "Я помогу вам записаться на услуги детейлинг-студии.\n\n"
            "Выберите услугу:",
            reply_markup=get_main_menu()
        )
        
        await state.set_state(MainMenu.choosing_service)
        
    finally:
        db.close()


# ==================== ГЛАВНОЕ МЕНЮ ====================

@router.message(F.text == "🏠 В главное меню")
async def back_to_menu(message: Message, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    
    await message.answer(
        "Выберите услугу:",
        reply_markup=get_main_menu()
    )
    
    await state.set_state(MainMenu.choosing_service)


# ==================== PPF (ОКЛЕЙКА ПЛЁНКОЙ) ====================

@router.message(MainMenu.choosing_service, F.text == "🛡 Оклейка плёнкой")
async def ppf_start(message: Message, state: FSMContext):
    """Начало сценария PPF"""
    await message.answer(
        "Отлично! Защитная плёнка — это сохранение ЛКП от сколов и повреждений.\n\n"
        "Выберите вариант:",
        reply_markup=get_ppf_variants()
    )
    
    await state.set_state(PPFFlow.choosing_variant)


@router.message(PPFFlow.choosing_variant, F.text.in_([
    "База (только морда)",
    "Зоны риска",
    "Все элементы в цвет кузова",
    "Матовый полиуретан"
]))
async def ppf_variant_selected(message: Message, state: FSMContext, db_session):
    """Выбран вариант PPF"""
    db: Session = db_session()
    
    try:
        variant = message.text
        
        # Сохраняем вариант в state
        await state.update_data(service="ppf", service_variant=variant)
        
        # Создаём/получаем лид
        lead = await get_or_create_lead(db, message.from_user.id)
        await update_lead_data(db, lead, service="ppf", service_variant=variant)
        
        # Сохраняем ID лида в state
        await state.update_data(lead_id=lead.id)
        
        # Разная логика в зависимости от варианта
        if variant == "Зоны риска":
            await message.answer(
                "Хороший выбор! Какие зоны хотите защитить в первую очередь?\n\n"
                "Вы можете выбрать из примеров или описать своими словами:",
                reply_markup=get_ppf_zones_examples()
            )
            await state.set_state(PPFFlow.asking_zones)
        
        elif variant == "Матовый полиуретан":
            await message.answer(
                "Отличный вариант! Матовая или сатиновая фактура + родной цвет + полная защита.\n\n"
                "Мат или сатин подберём на осмотре, дадим образцы, сравните на кузове.\n\n"
                "Подскажите марку, модель и год вашего автомобиля:"
            )
            await state.set_state(PPFFlow.collecting_car)
        
        else:
            # База или Вкруг
            if variant == "База (только морда)":
                await message.answer(
                    "Обычно это капот, бампер, крылья, полоса на крышу или целиком, оптика.\n"
                    "Состав уточним по вашему авто на осмотре.\n\n"
                    "Подскажите марку, модель и год автомобиля:"
                )
            else:  # Все элементы в цвет кузова
                await message.answer(
                    "Это полная оклейка кузова в цвет. Дополнительно по желанию можно добавить пороги, "
                    "отдельные пластиковые элементы — это точечно подскажет менеджер.\n\n"
                    "Подскажите марку, модель и год автомобиля:"
                )
            
            await state.set_state(PPFFlow.collecting_car)
    
    finally:
        db.close()


@router.message(PPFFlow.asking_zones)
async def ppf_zones_selected(message: Message, state: FSMContext, db_session):
    """Выбраны зоны для PPF"""
    db: Session = db_session()
    
    try:
        zones = message.text
        
        # Сохраняем
        data = await state.get_data()
        lead_id = data.get("lead_id")
        
        if lead_id:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if lead:
                await update_lead_data(db, lead, goal=zones)
        
        await state.update_data(zones=zones)
        
        await message.answer(
            "Понял. Подскажите марку, модель и год автомобиля:"
        )
        
        await state.set_state(PPFFlow.collecting_car)
    
    finally:
        db.close()


@router.message(PPFFlow.collecting_car)
async def ppf_collect_car(message: Message, state: FSMContext, db_session):
    """Сбор данных авто для PPF"""
    db: Session = db_session()
    
    try:
        text = message.text
        
        # Смарт-парсинг
        parsed = parser.parse_message(text)
        
        # Сохраняем сообщение
        data = await state.get_data()
        lead_id = data.get("lead_id")
        await save_message(db, message.from_user.id, text, lead_id)
        
        # Проверяем наличие авто
        if parsed["car"]:
            car = parsed["car"]
            
            # Обновляем лид
            if lead_id:
                lead = db.query(Lead).filter(Lead.id == lead_id).first()
                if lead:
                    await update_lead_data(
                        db, lead,
                        car_brand=car["brand"],
                        car_model=car["model"],
                        car_year=car["year"]
                    )
            
            await state.update_data(
                car_brand=car["brand"],
                car_model=car["model"],
                car_year=car["year"]
            )
            
            # Проверяем телефон и время
            if parsed["phone"]:
                await state.update_data(phone=parsed["phone"])
                if lead_id:
                    lead = db.query(Lead).filter(Lead.id == lead_id).first()
                    if lead:
                        await update_lead_data(db, lead, phone=parsed["phone"])
            
            if parsed["datetime"]:
                await state.update_data(preferred_time=parsed["datetime"])
                if lead_id:
                    lead = db.query(Lead).filter(Lead.id == lead_id).first()
                    if lead:
                        await update_lead_data(db, lead, preferred_time=parsed["datetime"])
            
            # Переходим к времени
            await message.answer(
                f"Отлично, {car['brand']} {car['model']} {car['year']}.\n\n"
                "Когда вам удобно заехать? (например: завтра после 18, в пятницу утром)"
            )
            
            await state.set_state(PPFFlow.collecting_time)
        
        else:
            # Год не найден
            await message.answer(
                "Подскажите, пожалуйста, год автомобиля — это важно для корректной записи.\n\n"
                "Напишите марку, модель и год (например: Toyota Camry 2020)"
            )
    
    finally:
        db.close()


@router.message(PPFFlow.collecting_time)
async def ppf_collect_time(message: Message, state: FSMContext, db_session):
    """Сбор времени для PPF"""
    db: Session = db_session()
    
    try:
        text = message.text
        
        # Смарт-парсинг
        parsed = parser.parse_message(text)
        
        # Сохраняем сообщение
        data = await state.get_data()
        lead_id = data.get("lead_id")
        await save_message(db, message.from_user.id, text, lead_id)
        
        # Извлекаем дату/время
        preferred_time = parsed["datetime"] if parsed["datetime"] else text
        
        # Проверяем "вчера"
        if "вчера" in text.lower() or "позавчера" in text.lower():
            await message.answer(
                "Это время уже прошло 🙂\n\n"
                "Подскажите, пожалуйста, ближайший день и время, когда удобно заехать."
            )
            return
        
        # Сохраняем
        await state.update_data(preferred_time=preferred_time)
        
        if lead_id:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if lead:
                await update_lead_data(db, lead, preferred_time=preferred_time)
        
        # Проверяем телефон из парсинга
        if parsed["phone"]:
            await state.update_data(phone=parsed["phone"])
            if lead_id:
                lead = db.query(Lead).filter(Lead.id == lead_id).first()
                if lead:
                    await update_lead_data(db, lead, phone=parsed["phone"])
        
        # Проверяем срочность
        if parsed["is_urgent"]:
            await state.update_data(is_urgent=True)
            if lead_id:
                lead = db.query(Lead).filter(Lead.id == lead_id).first()
                if lead:
                    await update_lead_data(db, lead, is_urgent=True)
        
        # Переходим к телефону
        phone = (await state.get_data()).get("phone")
        
        if phone:
            # Телефон уже есть — завершаем
            await finish_lead_collection(message, state, db)
        else:
            await message.answer(
                "Хорошо. Напишите, пожалуйста, номер телефона для подтверждения записи:"
            )
            await state.set_state(PPFFlow.collecting_phone)
    
    finally:
        db.close()


@router.message(PPFFlow.collecting_phone)
async def ppf_collect_phone(message: Message, state: FSMContext, db_session):
    """Сбор телефона для PPF"""
    db: Session = db_session()
    
    try:
        text = message.text
        
        # Парсинг телефона
        phone = parser.parse_phone(text)
        
        if not phone or not parser.validate_phone(phone):
            await message.answer(
                "Не увидел номер телефона 🙏\n\n"
                "Напишите, пожалуйста, в формате +7 9** *** ** **"
            )
            return
        
        # Сохраняем
        await state.update_data(phone=phone)
        
        data = await state.get_data()
        lead_id = data.get("lead_id")
        
        if lead_id:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if lead:
                await update_lead_data(db, lead, phone=phone)
        
        # Завершаем сбор
        await finish_lead_collection(message, state, db)
    
    finally:
        db.close()


async def finish_lead_collection(message: Message, state: FSMContext, db: Session):
    """Завершение сбора данных и отправка админу"""
    data = await state.get_data()
    
    lead_id = data.get("lead_id")
    car_brand = data.get("car_brand", "")
    car_model = data.get("car_model", "")
    car_year = data.get("car_year", "")
    preferred_time = data.get("preferred_time", "")
    phone = data.get("phone", "")
    service = data.get("service", "")
    service_variant = data.get("service_variant", "")
    is_urgent = data.get("is_urgent", False)
    
    # Финальное сообщение клиенту
    await message.answer(
        "Принято ✅\n\n"
        "Администратор позвонит вам, уточнит детали и подтвердит удобное время."
    )
    
    await message.answer(
        f"Ждём вас по адресу:\n\n"
        f"{config.STUDIO_ADDRESS}\n\n"
        f"Карта: {config.STUDIO_MAP_URL}"
    )
    
    await message.answer(
        f"📋 Ваша заявка:\n\n"
        f"Авто: {car_brand} {car_model} {car_year}\n"
        f"Когда: {preferred_time}\n"
        f"Телефон: {phone}"
    )
    
    # TODO: Отправка карточки админу (сделаем в следующем файле)
    
    # Сбрасываем состояние
    await state.clear()
    
    await message.answer(
        "Если есть ещё вопросы — пишите! 😊",
        reply_markup=get_main_menu()
    )
    
    await state.set_state(MainMenu.choosing_service)


# ==================== ЗАГЛУШКИ ДЛЯ ДРУГИХ УСЛУГ ====================
# Добавим в следующих задачах

@router.message(MainMenu.choosing_service)
async def service_not_implemented(message: Message):
    """Заглушка для ещё не реализованных услуг"""
    await message.answer(
        "Эта услуга пока в разработке 🔧\n\n"
        "Выберите другую услугу или напишите напрямую, чем могу помочь!"
    )
