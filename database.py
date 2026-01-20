from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

Base = declarative_base()


class LeadStatus(enum.Enum):
    """Статусы заявки"""
    NEW = "new"                    # Новая заявка
    IN_WORK = "in_work"           # В работе / диалог с админом
    COMPLETED = "completed"        # Приехал, работа выполнена
    REJECTED = "rejected"          # Отказ / не приехал


class User(Base):
    """Пользователь бота"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)  # Telegram user_id
    username = Column(String(255), nullable=True)            # @username
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    
    # Режим диалога с админом
    in_admin_dialog = Column(Boolean, default=False)
    admin_dialog_lead_id = Column(Integer, nullable=True)   # ID заявки, по которой идёт диалог
    
    # Анти-спам
    last_lead_created_at = Column(DateTime, nullable=True)
    leads_count_last_hour = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Lead(Base):
    """Заявка / лид"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Telegram user_id
    
    # Чек-лист данных
    service = Column(String(100), nullable=True)          # Услуга (ppf/vinyl/polish/etc)
    car_brand = Column(String(100), nullable=True)        # Марка
    car_model = Column(String(100), nullable=True)        # Модель
    car_year = Column(Integer, nullable=True)             # Год
    preferred_time = Column(Text, nullable=True)          # Когда удобно (текст)
    phone = Column(String(20), nullable=True)             # Телефон
    
    # Дополнительные данные
    service_variant = Column(String(255), nullable=True)  # Вариант услуги (база/зоны риска/в круг)
    goal = Column(Text, nullable=True)                    # Цель клиента
    comment = Column(Text, nullable=True)                 # Комментарий / контекст
    
    # Признаки
    is_urgent = Column(Boolean, default=False)            # "Еду сейчас"
    is_red_flag = Column(Boolean, default=False)          # Красный флаг (претензия/нестандарт)
    
    # Статус
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)        # Когда закрыта


class Message(Base):
    """История сообщений (для диалога админ-клиент и контекста ИИ)"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, nullable=True)              # К какой заявке относится
    user_id = Column(Integer, nullable=False)
    
    # Кто отправил
    is_from_admin = Column(Boolean, default=False)
    
    # Содержимое
    text = Column(Text, nullable=True)
    message_type = Column(String(50), default="text")     # text/photo/document
    
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db(database_url: str):
    """Инициализация базы данных"""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return engine, SessionLocal
