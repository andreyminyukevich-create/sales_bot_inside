import re
from typing import Optional, Dict, Any


# ==================== ТЕЛЕФОН ====================

def parse_phone(text: str) -> Optional[str]:
    """
    Извлекает телефон из текста и приводит к формату +7XXXXXXXXXX
    
    Args:
        text: Текст сообщения
        
    Returns:
        Телефон в формате +7XXXXXXXXXX или None
    """
    # Убираем всё кроме цифр
    digits = re.sub(r'\D', '', text)
    
    # Ищем 11 цифр (РФ формат)
    if len(digits) == 11:
        # Если начинается на 8, меняем на 7
        if digits[0] == '8':
            digits = '7' + digits[1:]
        
        # Проверяем что начинается на 7
        if digits[0] == '7':
            return f"+{digits}"
    
    # Ищем 10 цифр (без кода страны)
    elif len(digits) == 10:
        # Добавляем +7
        return f"+7{digits}"
    
    return None


def validate_phone(phone: str) -> bool:
    """Проверяет валидность телефона РФ"""
    if not phone or not phone.startswith('+7'):
        return False
    
    digits = phone[2:]  # Убираем +7
    
    # Должно быть 10 цифр
    if len(digits) != 10:
        return False
    
    # Все символы — цифры
    if not digits.isdigit():
        return False
    
    return True


# ==================== АВТО (МАРКА/МОДЕЛЬ/ГОД) ====================

def parse_car(text: str) -> Optional[Dict[str, Any]]:
    """
    Извлекает марку, модель и год из текста
    
    Args:
        text: Текст сообщения
        
    Returns:
        {"brand": str, "model": str, "year": int} или None
    """
    # Ищем год (4 цифры в диапазоне 1980-2035)
    year_match = re.search(r'\b(19[89]\d|20[0-3]\d)\b', text)
    
    if not year_match:
        return None
    
    year = int(year_match.group(1))
    
    # Берём всё до года как "марка + модель"
    car_text = text[:year_match.start()].strip()
    
    # Убираем лишние символы
    car_text = re.sub(r'[^\w\s\-]', '', car_text, flags=re.UNICODE)
    car_text = car_text.strip()
    
    if not car_text:
        return None
    
    # Разбиваем на слова
    words = car_text.split()
    
    if len(words) == 0:
        return None
    
    # Первое слово — марка, остальное — модель
    brand = words[0]
    model = ' '.join(words[1:]) if len(words) > 1 else ''
    
    return {
        "brand": brand,
        "model": model,
        "year": year
    }


def validate_car_year(year: Optional[int]) -> bool:
    """Проверяет валидность года авто"""
    if not year:
        return False
    
    return 1980 <= year <= 2035


# ==================== ДАТА/ВРЕМЯ ====================

def parse_datetime(text: str) -> Optional[str]:
    """
    Извлекает дату/время из текста (гибкий парсинг)
    
    Args:
        text: Текст сообщения
        
    Returns:
        Строка с датой/временем или None
    """
    text_lower = text.lower()
    
    # Триггеры "прошедшего времени"
    past_triggers = ['вчера', 'позавчера']
    for trigger in past_triggers:
        if trigger in text_lower:
            return None  # Прошедшее время — игнорируем
    
    # Простые паттерны
    time_patterns = [
        r'(сегодня|завтра|послезавтра)',
        r'(в|во)\s+(понедельник|вторник|среду|четверг|пятницу|субботу|воскресенье)',
        r'(на|в)\s+(\w+)',
        r'\d{1,2}[:\.]?\d{0,2}',  # Время типа "14:00" или "14"
        r'\d{1,2}\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)',
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text_lower)
        if match:
            # Возвращаем оригинальный текст (не lower)
            start = match.start()
            end = match.end()
            
            # Расширяем контекст (берём немного до и после)
            context_start = max(0, start - 20)
            context_end = min(len(text), end + 20)
            
            return text[context_start:context_end].strip()
    
    return None


# ==================== ТРИГГЕРЫ "ЕДУ СЕЙЧАС" ====================

URGENT_TRIGGERS = [
    'сейчас',
    'прямо сейчас',
    'через 10 минут',
    'через 5 минут',
    'через 15 минут',
    'через 20 минут',
    'через полчаса',
    'я рядом',
    'еду к вам',
    'уже еду',
    'сегодня через час',
    'через час',
]


def is_urgent_request(text: str) -> bool:
    """
    Проверяет, содержит ли текст триггеры "еду сейчас"
    
    Args:
        text: Текст сообщения
        
    Returns:
        True если найден триггер
    """
    text_lower = text.lower()
    
    for trigger in URGENT_TRIGGERS:
        if trigger in text_lower:
            return True
    
    return False


# ==================== КРАСНЫЕ ФЛАГИ ====================

RED_FLAG_TRIGGERS = [
    'плохо сделали',
    'верните деньги',
    'жалоба',
    'некачественно',
    'претензия',
    'дтп',
    'после ремонта',
    'после покраски',
    'хамелеон',
    'мат плёнка',  # Имеется в виду матовая плёнка с хамелеоном
    'сложный цвет',
    'дайте цену немедленно',
    'назовите точно сейчас',
]


def is_red_flag(text: str) -> bool:
    """
    Проверяет, содержит ли текст "красные флаги" (претензии, сложные кейсы)
    
    Args:
        text: Текст сообщения
        
    Returns:
        True если найден красный флаг
    """
    text_lower = text.lower()
    
    for trigger in RED_FLAG_TRIGGERS:
        if trigger in text_lower:
            return True
    
    return False


# ==================== КОМПЛЕКСНЫЙ ПАРСИНГ ====================

def parse_message(text: str) -> Dict[str, Any]:
    """
    Комплексный парсинг сообщения: извлекает все данные
    
    Args:
        text: Текст сообщения
        
    Returns:
        Словарь с извлечёнными данными
    """
    result = {
        "phone": parse_phone(text),
        "car": parse_car(text),
        "datetime": parse_datetime(text),
        "is_urgent": is_urgent_request(text),
        "is_red_flag": is_red_flag(text),
    }
    
    return result
