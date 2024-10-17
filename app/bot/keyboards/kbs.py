from aiogram.types import ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.config import settings


def main_keyboard(user_id: int, first_name: str) -> ReplyKeyboardMarkup:
    """Основная клавиатура бота"""
    kb = ReplyKeyboardBuilder()
    url_applications = f"{settings.BASE_SITE}/applications?user_id={user_id}"
    kb.button(text="🌐 Мои заявки", web_app=WebAppInfo(url=url_applications))
    kb.button(text="📝 Оставить заявку", web_app=WebAppInfo(url=f'{settings.BASE_SITE}'))
    kb.button(text="ℹ️ О нас")
    if user_id == settings.ADMIN_ID:
        kb.button(text="🔑 Админ панель")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def back_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой "Назад" """
    kb = ReplyKeyboardBuilder()
    kb.button(text="🔙 Назад")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def admin_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 На главную", callback_data="back_home")
    kb.button(text="📝 Смотреть заявки", callback_data="view_applications")
    kb.adjust(1)
    return kb.as_markup()


def admin_watch_applications(user_id: int) -> InlineKeyboardMarkup:
    url_applications = f"{settings.BASE_SITE}/admin_applications?user_id={user_id}"
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 На главную", callback_data="back_home")
    kb.button(text="🦺 Заявки в работе", web_app=WebAppInfo(url=f'{url_applications}&work=True'))
    kb.button(text="💾 Архивные заявки", web_app=WebAppInfo(url=f'{url_applications}&work=False'))
    kb.button(text="🧮 Статистика", web_app=WebAppInfo(url=url_applications))
    kb.adjust(1)
    return kb.as_markup()


def app_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-клавиатура для добавления заявки"""
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Оставить заявку", web_app=WebAppInfo(url=f'{settings.BASE_SITE}'))
    kb.adjust(1)
    return kb.as_markup()


async def greet_user(message: Message, is_new_user: bool) -> None:
    """
    Приветствует пользователя и отправляет соответствующее сообщение.
    """
    greeting = "Добро пожаловать" if is_new_user else "С возвращением"
    status = "Вы успешно зарегистрированы!" if is_new_user else "Рады видеть вас снова!"
    await message.answer(
        f"{greeting}, <b>{message.from_user.full_name}</b>! {status}\n"
        "Чем я могу помочь вам сегодня?",
        reply_markup=main_keyboard(user_id=message.from_user.id, first_name=message.from_user.first_name)
    )


def get_about_us_text() -> str:
    return """
🏫 Темрюкский центр профессиональной подготовки 🏫

📕 Программы соответствуют требованиям законодательства
Программы разработаны в соответствии с требованиями законодательства экспертами отрасли. Программы регулярно обновляются 
и дополняются материалами, когда вносятся изменения в законодательство.

📜 Официальные документы после обучения
В зависимости от программы вы получите Удостоверение о проверке знаний, Удостоверение о повышении квалификации или 
Диплом о профпереподготовке, Аттестат и Сертификат.

💰 Ценовая политика
Принцип нашей компании — самые выгодные цены и гарантия лучшей цены для постоянных клиентов.

🎓 Выпускники попадают во Всероссийский реестр квалифицированных специалистов
Погрузитесь в атмосферу уюта и релаксации. Каждый визит к нам - это не просто процедура, а настоящий ритуал красоты и 
заботы о себе.

🏅 20 лет успешной работы
Учебный центр осуществляет свою деятельность более 20 лет
"""
