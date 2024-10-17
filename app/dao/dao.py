from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.models import User, TrainingType, TrainingProgram, Application, ApplicationService


class UserDAO(BaseDAO):
    model = User


class TrainingProgramDAO(BaseDAO):
    model = TrainingProgram


class TrainingTypeDAO(BaseDAO):
    model = TrainingType


class ApplicationDAO(BaseDAO):
    model = Application

    @classmethod
    async def add_model(cls, **values):
        services_data = values.pop('services', [])

        async with async_session_maker() as session:
            async with session.begin():
                # Создаем основную заявку
                new_instance = cls.model(**values)
                service_instances = [
                    ApplicationService(**service_data, application=new_instance) for service_data in services_data
                ]
                session.add(new_instance)
                session.add_all(service_instances)
                try:
                    await session.flush()  # Применяет изменения к БД и обновляет объект
                    instance_id = new_instance.id  # Получаем id до коммита
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance, instance_id

    @classmethod
    async def get_applications(cls, user_id: int, admin: bool = False):
        async with async_session_maker() as session:
            async with session.begin():
                if admin:
                    query = (
                        select(Application)
                        .options(
                            joinedload(Application.services)
                            .joinedload(ApplicationService.training_type),
                            joinedload(Application.services)
                            .joinedload(ApplicationService.training_program)
                        )
                    )
                else:
                    query = (
                        select(Application)
                        .options(
                            joinedload(Application.services)
                            .joinedload(ApplicationService.training_type),
                            joinedload(Application.services)
                            .joinedload(ApplicationService.training_program)
                        )
                        .filter_by(user_id=user_id)
                    )

                result = await session.execute(query)

                applications = result.unique().scalars().all()  # Извлекаем все экземпляры Application

                # Преобразуем объекты в словари для удобного вывода
                applications_data = [
                    {
                        "id": app.id,
                        "company_name": app.company_name,
                        "phone_number": app.phone_number,
                        "email": app.email,
                        "status": app.status,
                        "user_id": app.user_id,
                        "services": [
                            {
                                "training_type": service.training_type.name,
                                "training_program": service.training_program.name,
                                "people_count": service.people_count,
                                "training_rank": service.training_rank,
                            }
                            for service in app.services
                        ],
                    }
                    for app in applications
                ]

                return applications_data


class ApplicationServiceDAO(BaseDAO):
    model = ApplicationService
