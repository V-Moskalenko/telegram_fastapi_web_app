from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func

from app.database import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int):
        """
        Асинхронно находит и возвращает один экземпляр модели по указанным критериям или None.

        Аргументы:
            data_id: Критерии фильтрации в виде идентификатора записи.

        Возвращает:
            Экземпляр модели или None, если ничего не найдено.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        """
        Асинхронно находит и возвращает один экземпляр модели по указанным критериям или None.

        Аргументы:
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            Экземпляр модели или None, если ничего не найдено.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by) -> list:
        """
        Асинхронно находит и возвращает все экземпляры модели, удовлетворяющие указанным критериям.

        Аргументы:
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            Список экземпляров модели, удовлетворяющих критериям. Если ничего не найдено, возвращает пустой список.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def add(cls, **values):
        """
        Асинхронно создает новый экземпляр модели с указанными значениями.

        Аргументы:
            **values: Именованные параметры для создания нового экземпляра модели.

        Возвращает:
            Созданный экземпляр модели.
        """
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance

    @classmethod
    async def add_many(cls, instances: list[dict]) -> list:
        """
        Асинхронно создает новый экземпляры моделей с указанными значениями.

        Аргументы:
            instances: Список с именованными параметрами для создания новых экземпляров моделей.

        Возвращает:
            Список созданных экземпляров модели.
        """
        async with async_session_maker() as session:
            async with session.begin():
                new_instances = [cls.model(**values) for values in instances]
                session.add_all(new_instances)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instances

    @classmethod
    async def update(cls, filter_by: dict, **values) -> int:
        """
        Асинхронно обновляет экземпляры модели, соответствующие заданным критериям.

        Аргументы:
            filter_by (dict): Критерии фильтрации в виде именованных параметров.
            **values: Именованные параметры, указывающие новые значения для обновляемых полей.

        Возвращает:
            int: Количество строк, которые были обновлены.
        """
        async with async_session_maker() as session:
            async with session.begin():
                query = (
                    sqlalchemy_update(cls.model)
                    .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
                    .values(**values)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount

    @classmethod
    async def delete(cls, delete_all: bool = False, **filter_by) -> int:
        """
        Асинхронно удаляет экземпляры модели, соответствующие заданным критериям.

        Аргументы:
            delete_all (bool): Если True, удаляет все экземпляры модели.
                               Если False (по умолчанию), требуется указать хотя бы один фильтр.
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            int: Количество строк, которые были удалены.
        """
        if not delete_all and not filter_by:
            raise ValueError("Нужен хотя бы один фильтр для удаления.")

        async with async_session_maker() as session:
            async with session.begin():
                query = sqlalchemy_delete(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount

    @classmethod
    async def count(cls, **filter_by) -> int:
        """
        Асинхронно подсчитывает количество экземпляров модели, соответствующих заданным критериям.

        Аргументы:
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            int: Количество экземпляров модели, соответствующих критериям.
        """
        async with async_session_maker() as session:
            query = select(func.count(cls.model.id)).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def exists(cls, **filter_by) -> bool:
        """
        Асинхронно проверяет существование хотя бы одного экземпляра модели, соответствующего заданным критериям.

        Аргументы:
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            bool: True, если хотя бы один экземпляр соответствует критериям; иначе False.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by).exists()
            result = await session.execute(query)
            return result.scalar()
