from aiogram.fsm.state import State, StatesGroup


class MainMenu(StatesGroup):
    """Главное меню"""
    choosing_service = State()  # Выбор услуги


class PPFFlow(StatesGroup):
    """Сценарий: Оклейка плёнкой (PPF)"""
    choosing_variant = State()      # База / Зоны риска / В круг
    asking_zones = State()          # Для "Зоны риска" — какие именно
    collecting_car = State()        # Сбор авто (марка/модель/год)
    collecting_time = State()       # Когда удобно заехать
    collecting_phone = State()      # Телефон


class VinylFlow(StatesGroup):
    """Сценарий: Винил / смена цвета"""
    choosing_zone = State()         # В круг / элементы
    choosing_goal = State()         # Цель (цвет/фактура/стиль)
    collecting_car = State()
    collecting_time = State()
    collecting_phone = State()


class PolishFlow(StatesGroup):
    """Сценарий: Реставрация ЛКП / полировка"""
    choosing_zone = State()         # Капот/бампер/двери/весь кузов/точечно
    collecting_car = State()
    collecting_time = State()
    collecting_phone = State()


class CeramicFlow(StatesGroup):
    """Сценарий: Керамика / защита"""
    asking_goal = State()           # Цель (удобство/блеск/защита)
    collecting_car = State()
    collecting_time = State()
    collecting_phone = State()


class CleaningFlow(StatesGroup):
    """Сценарий: Химчистка"""
    choosing_zone = State()         # Салон/сиденья/потолок/багажник/запах/пятна
    collecting_car = State()
    collecting_time = State()
    collecting_phone = State()


class WashFlow(StatesGroup):
    """Сценарий: Мойка"""
    choosing_goal = State()         # Цель (быстро/детейлинг/после зимы/предпродажная)
    asking_extras = State()         # Допы (уборка в салоне/чернение резины)
    collecting_car = State()
    collecting_time = State()
    collecting_phone = State()


class TintFlow(StatesGroup):
    """Сценарий: Тонировка"""
    choosing_zone = State()         # Задняя/передние/в круг/лобовое
    choosing_goal = State()         # Цель (солнце/приватность/ночное/эстетика)
    collecting_car = State()
    collecting_time = State()
    collecting_phone = State()


class GenericCollection(StatesGroup):
    """Универсальный сбор данных (когда услуга уже выбрана)"""
    collecting_car = State()
    collecting_time = State()
    collecting_phone = State()


class AdminDialog(StatesGroup):
    """Режим диалога: админ общается с клиентом"""
    active = State()  # Диалог открыт
