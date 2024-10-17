from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards.kbs import main_keyboard, admin_keyboard, admin_watch_applications
from app.config import settings

admin_router = Router()


@admin_router.message(F.text == '🔑 Админ панель', F.from_user.id.in_([settings.ADMIN_ID]))
async def admin_panel(message: Message):
    await message.answer(
        f"Здравствуйте, <b>{message.from_user.full_name}</b>!\n\n"
        "Добро пожаловать в панель администратора. Здесь вы можете:\n"
        "• Просматривать все текущие заявки\n"
        "• Управлять статусами заявок\n"
        "• Анализировать статистику\n\n"
        "Для доступа к полному функционалу, пожалуйста, перейдите по ссылке ниже.\n"
        "Мы постоянно работаем над улучшением и расширением возможностей панели.",
        reply_markup=admin_keyboard()
    )


@admin_router.callback_query(F.data == 'view_applications')
async def admin_panel(callback: CallbackQuery):
    await callback.message.answer(
        ("<b>Выберете категорию:</b> \n\n"
         '<b>Заявки в работе</b> - позволяет просмотреть необработанные заявки и по кнопке "Отработать"'
         'отправит на страницу введения стоимости за каждое обучение, после чего проведет расчёт предложения'
         'и оформит коммерческое предложение в word формате\n\n'
         '<b>Архивные заявки</b> - открывает страницу со всеми отправленными ранее предложениями\n\n'
         '<b>Статистика</b> - данный модуль находится в разработке, по ТЗ будет введена аналитика работы\n\n'),
        reply_markup=admin_watch_applications(user_id=callback.from_user.id)
    )
    await callback.answer()


@admin_router.callback_query(F.data == 'back_home')
async def cmd_back_home_admin(callback: CallbackQuery):
    await callback.answer(f"С возвращением, {callback.from_user.full_name}!")
    await callback.message.answer(
        f"С возвращением, <b>{callback.from_user.full_name}</b>!\n\n"
        "Надеемся, что работа в панели администратора была продуктивной. "
        "Если у вас есть предложения по улучшению функционала, "
        "пожалуйста, сообщите нам.\n\n"
        "Чем еще я могу помочь вам сегодня?",
        reply_markup=main_keyboard(user_id=callback.from_user.id, first_name=callback.from_user.first_name)
    )