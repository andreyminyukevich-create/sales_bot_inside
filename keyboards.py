from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


# ==================== ГЛАВНОЕ МЕНЮ ====================

def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню (5 услуг + вопрос)"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="🛡 Оклейка плёнкой")
    kb.button(text="🎨 Цветная полиуретановая плёнка")
    kb.button(text="🎭 Винил (смена цвета)")
    kb.button(text="💎 Реставрация ЛКП")
    kb.button(text="🧼 Мойка")
    kb.button(text="🔲 Тонировка")
    kb.button(text="🧴 Химчистка")
    kb.button(text="🛡️ Керамика")
    kb.button(text="❓ Задать вопрос")
    kb.adjust(2, 2, 2, 2, 1)  # По 2 в ряд, последняя одна
    return kb.as_markup(resize_keyboard=True)


# ==================== PPF (ЗАЩИТА) ====================

def get_ppf_variants() -> ReplyKeyboardMarkup:
    """Варианты PPF"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="База (только морда)")
    kb.button(text="Зоны риска")
    kb.button(text="Все элементы в цвет кузова")
    kb.button(text="Матовый полиуретан")
    kb.button(text="🏠 В главное меню")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def get_ppf_zones_examples() -> ReplyKeyboardMarkup:
    """Примеры зон для PPF"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="Капот, бампер, крылья, оптика")
    kb.button(text="+ Пороги и зона под ручками")
    kb.button(text="+ Зона погрузки")
    kb.button(text="Опишу словами")
    kb.button(text="🏠 В главное меню")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


# ==================== ВИНИЛ ====================

def get_vinyl_zones() -> ReplyKeyboardMarkup:
    """Зоны для винила"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="В круг")
    kb.button(text="Отдельные элементы")
    kb.button(text="🏠 В главное меню")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


# ==================== РЕСТАВРАЦИЯ ЛКП ====================

def get_polish_zones() -> ReplyKeyboardMarkup:
    """Зоны для полировки"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="Капот")
    kb.button(text="Бампер(а)")
    kb.button(text="Двери")
    kb.button(text="Крылья/арки")
    kb.button(text="Весь кузов")
    kb.button(text="Точечно/не знаю — опишу словами")
    kb.button(text="🏠 В главное меню")
    kb.adjust(2, 2, 1, 1, 1)
    return kb.as_markup(resize_keyboard=True)


# ==================== КЕРАМИКА ====================

def get_ceramic_goals() -> ReplyKeyboardMarkup:
    """Цели керамики"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="Удобство в уходе")
    kb.button(text="Максимум блеска")
    kb.button(text="Защита от химии/реагентов")
    kb.button(text="Всё в комплексе")
    kb.button(text="🏠 В главное меню")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


# ==================== МОЙКА ====================

def get_wash_goals() -> ReplyKeyboardMarkup:
    """Цели мойки"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="Быстро освежить")
    kb.button(text="Бережно и тщательно")
    kb.button(text="После зимы: реагенты/битум")
    kb.button(text="Под выдачу / предпродажная")
    kb.button(text="После оклейки/керамики")
    kb.button(text="Не знаю — подскажите")
    kb.button(text="🏠 В главное меню")
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup(resize_keyboard=True)


def get_wash_extras() -> ReplyKeyboardMarkup:
    """Допы для мойки"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="Влажная уборка в салоне")
    kb.button(text="Чернение резины")
    kb.button(text="Химчистка салона")
    kb.button(text="Ничего дополнительно")
    kb.button(text="🏠 В главное меню")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


# ==================== ТОНИРОВКА ====================

def get_tint_zones() -> ReplyKeyboardMarkup:
    """Зоны тонировки"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="Задняя полусфера")
    kb.button(text="Передние боковые")
    kb.button(text="В круг")
    kb.button(text="Лобовое")
    kb.button(text="Только лобовое")
    kb.button(text="Не знаю — подскажите")
    kb.button(text="🏠 В главное меню")
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup(resize_keyboard=True)


def get_tint_goals() -> ReplyKeyboardMarkup:
    """Цели тонировки"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="Солнце и жара")
    kb.button(text="Приватность")
    kb.button(text="Ночью чтобы было видно")
    kb.button(text="Эстетика/вид")
    kb.button(text="Не знаю — подскажите")
    kb.button(text="🏠 В главное меню")
    kb.adjust(2, 2, 1, 1)
    return kb.as_markup(resize_keyboard=True)


# ==================== ХИМЧИСТКА ====================

def get_cleaning_zones() -> ReplyKeyboardMarkup:
    """Зоны химчистки"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="Салон целиком")
    kb.button(text="Сиденья")
    kb.button(text="Потолок")
    kb.button(text="Багажник")
    kb.button(text="Устранение запаха (озонирование)")
    kb.button(text="Точечно/пятна")
    kb.button(text="Не знаю — подскажите")
    kb.button(text="🏠 В главное меню")
    kb.adjust(2, 2, 2, 1, 1)
    return kb.as_markup(resize_keyboard=True)


# ==================== АДМИНСКИЕ КНОПКИ ====================

def get_lead_card_buttons(lead_id: int) -> InlineKeyboardMarkup:
    """Кнопки под карточкой лида для админа"""
    kb = InlineKeyboardBuilder()
    kb.button(text="💬 Ответить клиенту", callback_data=f"admin_reply_{lead_id}")
    kb.button(text="✅ В работу", callback_data=f"admin_in_work_{lead_id}")
    kb.button(text="❌ Отказ", callback_data=f"admin_reject_{lead_id}")
    kb.adjust(1)
    return kb.as_markup()


def get_admin_dialog_buttons(lead_id: int) -> InlineKeyboardMarkup:
    """Кнопки для завершения диалога админом"""
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Завершить диалог", callback_data=f"admin_end_dialog_{lead_id}")
    kb.adjust(1)
    return kb.as_markup()


def get_leads_menu() -> InlineKeyboardMarkup:
    """Меню списка заявок"""
    kb = InlineKeyboardBuilder()
    kb.button(text="🆕 Новые заявки", callback_data="leads_new")
    kb.button(text="🔧 В работе", callback_data="leads_in_work")
    kb.adjust(1)
    return kb.as_markup()
