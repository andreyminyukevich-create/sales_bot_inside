import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import Session
from sqlalchemy import desc

import config
from database import User, Lead, LeadStatus
from keyboards import get_lead_card_buttons, get_leads_menu, get_admin_dialog_buttons

router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь админом"""
    return user_id in [config.ADMIN_CHAT_ID, config.OWNER_CHAT_ID]


# ==================== ОТПРАВКА КАРТОЧКИ ЛИДА АДМИНУ ====================

async def send_lead_card_to_admin(bot, lead: Lead, user: User):
    """
    Отправить карточку лида администратору
    
    Args:
        bot: Экземпляр бота
        lead: Объект лида
        user: Объект пользователя (клиента)
    """
    
    # Формируем заголовок
    if lead.is_urgent:
        header = "🚨 ЕДЕТ СЕЙЧАС!"
    else:
        header = "🆕 Новая заявка"
    
    # Формируем текст карточки
    service_names = {
        "ppf": "Оклейка плёнкой (PPF)",
        "color_ppf": "Цветная полиуретановая плёнка",
        "vinyl": "Винил (смена цвета)",
        "polish": "Реставрация ЛКП",
        "ceramic": "Керамика",
        "wash": "Мойка",
        "tint": "Тонировка",
        "cleaning": "Химчистка"
    }
    
    service_name = service_names.get(lead.service, lead.service or "Не указана")
    
    card_text = f"{header}\n\n"
    card_text += f"👤 Клиент: {user.first_name or 'Не указано'}"
    
    if user.username:
        card_text += f" (@{user.username})"
    
    card_text += f"\n\n📋 Услуга: {service_name}"
    
    if lead.service_variant:
        card_text += f"\nВариант: {lead.service_variant}"
    
    # Авто
    if lead.car_brand:
        card_text += f"\n\n🚗 Авто: {lead.car_brand}"
        if lead.car_model:
            card_text += f" {lead.car_model}"
        if lead.car_year:
            card_text += f" ({lead.car_year} г.)"
    
    # Когда удобно
    if lead.preferred_time:
        card_text += f"\n\n⏰ Когда удобно: {lead.preferred_time}"
    
    # Телефон
    if lead.phone:
        card_text += f"\n\n📞 Телефон: {lead.phone}"
    
    # Цель/комментарий
    if lead.goal:
        card_text += f"\n\n💬 Комментарий: {lead.goal}"
    
    # Отправляем админу
    await bot.send_message(
        chat_id=config.ADMIN_CHAT_ID,
        text=card_text,
        reply_markup=get_lead_card_buttons(lead.id)
    )
    
    # Если срочная заявка — отправляем владельцу
    if lead.is_urgent and config.OWNER_CHAT_ID != config.ADMIN_CHAT_ID:
        await bot.send_message(
            chat_id=config.OWNER_CHAT_ID,
            text=card_text,
            reply_markup=get_lead_card_buttons(lead.id)
        )


# ==================== КОМАНДА /LEADS (СПИСОК ЗАЯВОК) ====================

@router.message(Command("leads"))
async def cmd_leads(message: Message, db_session):
    """Команда /leads - список заявок для админа"""
    
    # Проверка прав
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой команде.")
        return
    
    db: Session = db_session()
    
    try:
        # Считаем заявки
        new_count = db.query(Lead).filter(Lead.status == LeadStatus.NEW).count()
        in_work_count = db.query(Lead).filter(Lead.status == LeadStatus.IN_WORK).count()
        
        text = f"📊 Заявки:\n\n"
        text += f"🆕 Новые: {new_count}\n"
        text += f"🔧 В работе: {in_work_count}\n\n"
        text += "Выберите категорию:"
        
        await message.answer(text, reply_markup=get_leads_menu())
    
    finally:
        db.close()


# ==================== КНОПКИ СПИСКА ЗАЯВОК ====================

@router.callback_query(F.data == "leads_new")
async def show_new_leads(callback: CallbackQuery, db_session):
    """Показать новые заявки"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа", show_alert=True)
        return
    
    db: Session = db_session()
    
    try:
        # Получаем новые заявки
        leads = db.query(Lead).filter(
            Lead.status == LeadStatus.NEW
        ).order_by(desc(Lead.created_at)).limit(10).all()
        
        if not leads:
            await callback.message.answer("Нет новых заявок")
            await callback.answer()
            return
        
        # Формируем карточки
        for lead in leads:
            user = db.query(User).filter(User.user_id == lead.user_id).first()
            
            if user:
                await send_lead_card_to_admin(callback.bot, lead, user)
        
        await callback.answer()
    
    finally:
        db.close()


@router.callback_query(F.data == "leads_in_work")
async def show_in_work_leads(callback: CallbackQuery, db_session):
    """Показать заявки в работе"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа", show_alert=True)
        return
    
    db: Session = db_session()
    
    try:
        # Получаем заявки в работе
        leads = db.query(Lead).filter(
            Lead.status == LeadStatus.IN_WORK
        ).order_by(desc(Lead.created_at)).limit(10).all()
        
        if not leads:
            await callback.message.answer("Нет заявок в работе")
            await callback.answer()
            return
        
        # Формируем карточки
        for lead in leads:
            user = db.query(User).filter(User.user_id == lead.user_id).first()
            
            if user:
                await send_lead_card_to_admin(callback.bot, lead, user)
        
        await callback.answer()
    
    finally:
        db.close()


# ==================== КНОПКИ ПОД КАРТОЧКОЙ ЛИДА ====================

@router.callback_query(F.data.startswith("admin_in_work_"))
async def admin_set_in_work(callback: CallbackQuery, db_session):
    """Админ нажал 'В работу'"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа", show_alert=True)
        return
    
    lead_id = int(callback.data.split("_")[-1])
    
    db: Session = db_session()
    
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if lead:
            lead.status = LeadStatus.IN_WORK
            lead.updated_at = datetime.utcnow()
            db.commit()
            
            await callback.message.edit_text(
                callback.message.text + "\n\n✅ Взято в работу",
                reply_markup=None
            )
            
            await callback.answer("Заявка в работе")
        else:
            await callback.answer("Заявка не найдена", show_alert=True)
    
    finally:
        db.close()


@router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject_lead(callback: CallbackQuery, db_session):
    """Админ нажал 'Отказ'"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа", show_alert=True)
        return
    
    lead_id = int(callback.data.split("_")[-1])
    
    db: Session = db_session()
    
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if lead:
            lead.status = LeadStatus.REJECTED
            lead.updated_at = datetime.utcnow()
            db.commit()
            
            await callback.message.edit_text(
                callback.message.text + "\n\n❌ Отказ",
                reply_markup=None
            )
            
            await callback.answer("Заявка отклонена")
        else:
            await callback.answer("Заявка не найдена", show_alert=True)
    
    finally:
        db.close()


@router.callback_query(F.data.startswith("admin_reply_"))
async def admin_start_reply(callback: CallbackQuery, db_session):
    """Админ нажал 'Ответить клиенту' - начало диалога"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа", show_alert=True)
        return
    
    lead_id = int(callback.data.split("_")[-1])
    
    db: Session = db_session()
    
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            await callback.answer("Заявка не найдена", show_alert=True)
            return
        
        user = db.query(User).filter(User.user_id == lead.user_id).first()
        
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        # Переводим пользователя в режим диалога
        user.in_admin_dialog = True
        user.admin_dialog_lead_id = lead_id
        db.commit()
        
        # Меняем статус лида
        lead.status = LeadStatus.IN_WORK
        db.commit()
        
        # Обновляем карточку админа
        await callback.message.edit_text(
            callback.message.text + "\n\n💬 Диалог открыт",
            reply_markup=get_admin_dialog_buttons(lead_id)
        )
        
        # Уведомляем админа
        await callback.message.answer(
            f"💬 Диалог с клиентом открыт.\n\n"
            f"Всё, что вы напишете — увидит клиент.\n"
            f"Для завершения диалога нажмите кнопку выше."
        )
        
        await callback.answer()
    
    finally:
        db.close()


# Импортируем datetime для обновления заявок
from datetime import datetime
