import re

from sqlalchemy import String, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.database import Base


# ------------------------------------------------------------------------
# Команды для Alembic:
#   Инициализиция Alembic с поддержкой асинхронного взаимодействия с базой данных
#   alembic init -t async migration
#
#   Создаём файл миграции
#   alembic revision --autogenerate -m "Сообщение"
#
#   Применение миграции
#   alembic upgrade head
#
#   Обновить состояние
#   alembic stamp head
# ------------------------------------------------------------------------


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'

    # Уникальный идентификатор пользователя в Telegram
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # Имя пользователя
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    # Telegram username
    username: Mapped[str] = mapped_column(String, nullable=True)
    # Связь с заявками (один пользователь может иметь несколько заявок)
    applications: Mapped[list["Application"]] = relationship(back_populates="user")


class TrainingType(Base):
    """Модель для вида обучения"""
    __tablename__ = 'training_types'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # Связь с программами обучения
    training_programs: Mapped[list["TrainingProgram"]] = relationship(
        'TrainingProgram', back_populates='training_type', cascade='all, delete-orphan'
    )


class TrainingProgram(Base):
    """Модель для программы обучения"""
    __tablename__ = 'training_programs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Внешний ключ, ссылающийся на тип обучения
    training_type_id: Mapped[int] = mapped_column(Integer, ForeignKey('training_types.id'), nullable=False)

    # Связь с типом обучения (многие к одному)
    training_type: Mapped['TrainingType'] = relationship('TrainingType', back_populates='training_programs')


class Application(Base):
    """Модель заявки на коммерческое предложение"""
    __tablename__ = 'applications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Внешний ключ для связи с пользователем
    user_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'), nullable=False)

    # Связь с пользователем (многие к одному)
    user: Mapped['User'] = relationship('User', back_populates='applications')

    # Наименование компании
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    # Номер телефона
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    # Почта
    email: Mapped[str] = mapped_column(String, nullable=False)

    # Связь с услугами заявки (один ко многим)
    services: Mapped[list['ApplicationService']] = relationship(back_populates='application',
                                                                cascade='all, delete-orphan')

    # Статус заявки
    status: Mapped[str] = mapped_column(String, nullable=False)

    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        # Регулярное выражение для проверки российского номера
        if not re.match(r'^\+7\d{10}$|^8\d{10}$', phone_number):
            raise ValueError("Номер телефона должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX")
        return phone_number


class ApplicationService(Base):
    """Модель услуги в заявке на обучение"""
    __tablename__ = 'application_services'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Вид обучения (связь с моделью TrainingType)
    training_type_id: Mapped[int] = mapped_column(ForeignKey('training_types.id'), nullable=False)
    training_type: Mapped['TrainingType'] = relationship('TrainingType')

    # Программа обучения (связь с моделью TrainingProgram)
    training_program_id: Mapped[int] = mapped_column(ForeignKey('training_programs.id'), nullable=False)
    training_program: Mapped['TrainingProgram'] = relationship('TrainingProgram')

    # Разряд обучения (опциональный)
    training_rank: Mapped[str | None] = mapped_column(String, nullable=True)

    # Количество человек на обучение
    people_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Связь с заявкой
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'), nullable=False)
    application: Mapped['Application'] = relationship('Application', back_populates='services')
