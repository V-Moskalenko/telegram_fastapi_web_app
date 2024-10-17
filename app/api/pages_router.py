import json
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from aiogram.types.input_file import FSInputFile
from pydantic import ValidationError

from app.api.schemas import ApplicationServiceData, ApplicationData
from app.bot.create_bot import bot
from app.bot.keyboards.kbs import main_keyboard
from app.config import settings
from app.dao.dao import TrainingTypeDAO, TrainingProgramDAO, ApplicationDAO, UserDAO
from app.commercial_offer.offer_docx import fill_out_docx_template

router = APIRouter(prefix='', tags=['Фронтенд'])
templates = Jinja2Templates(directory='app/templates')


@router.get("/", response_class=HTMLResponse)
async def get_application_form(request: Request):
    return templates.TemplateResponse("issue.html", {"request": request})


@router.get("/get_training_types")
async def get_training_types():
    types = await TrainingTypeDAO.find_all()
    return {"types": [{"id": t.id, "name": t.name} for t in types]}


@router.get("/get_programs")
async def get_programs(type_id: int):
    programs = await TrainingProgramDAO.find_all(training_type_id=type_id)
    return {"programs": [{"id": p.id, "name": p.name} for p in programs]}


@router.get("/applications", response_class=HTMLResponse)
async def get_applications(request: Request, user_id: int = None):
    data_page = {"request": request, "message": None}
    user_check = await UserDAO.find_one_or_none(telegram_id=user_id)
    if not user_id or not user_check:
        data_page['message'] = 'Пользователь по которому нужно отобразить заявки не указан или не найден в базе данных'
    applications = await ApplicationDAO.get_applications(user_id, admin=False)
    if not applications:
        data_page['message'] = ('У вас нет заявок! Подайте заявку по кнопке "Оформить заявку" '
                                'или нажав на кнопку приложения "Заявки"')
    data_page['active_applications'] = tuple(filter(lambda x: x['status'] == 'В работе', applications))
    data_page['completed_applications'] = tuple(filter(lambda x: x['status'] != 'В работе', applications))
    return templates.TemplateResponse("applications.html", data_page)


@router.get("/admin_applications", response_class=HTMLResponse)
async def get_applications(request: Request, user_id: int, work: bool):
    data_page = {"request": request, "message": None, "active_applications": None, "completed_applications": None}
    if work:
        applications = await ApplicationDAO.get_applications(user_id, admin=True)
        active_applications = tuple(filter(lambda x: x['status'] == 'В работе', applications))
        data_page['message'] = 'Все заявки отработаны!' if not active_applications else None
        data_page['active_applications'] = active_applications if active_applications else None
    else:
        applications = await ApplicationDAO.get_applications(user_id, admin=True)
        completed_applications = tuple(filter(lambda x: x['status'] != 'В работе', applications))
        data_page['message'] = 'Заявок в архиве нет!' if not completed_applications else None
        data_page['completed_applications'] = completed_applications if completed_applications else None
    return templates.TemplateResponse("admin_applications.html", data_page)


@router.post("/submit_application", response_class=JSONResponse)
async def get_programs(request: Request):
    data = await request.json()
    # Установим статус
    data['status'] = 'В работе'
    services_list = data.pop('services')
    # Проведем валидацию и конвертацию значений, составим модели
    try:
        services_models_list = [ApplicationServiceData(**service) for service in services_list]
        application_data = ApplicationData(**data, services=services_models_list)
    except ValidationError as e:
        msg = '\n'.join([
            f'Ошибка в поле {error['loc'][0]} - {error["msg"]}, проверьте корректность данных'
            for error in e.errors()
        ])
        return JSONResponse(content={"status": "error", "message": msg}, status_code=400)
    application_data_val = application_data.dict()
    model, model_id = await ApplicationDAO.add_model(**application_data_val)
    # Сформируем и отправим сообщения пользователю и администратору
    user_info = await UserDAO.find_one_or_none(telegram_id=application_data.user_id)
    program_name = [await TrainingProgramDAO.find_one_or_none_by_id(i.training_program_id) for i in
                    services_models_list]
    program_info = [{'Программа': i.name, 'Разряд': j.training_rank, 'Количество': j.people_count} for i, j in
                    zip(program_name, services_models_list)]
    program_str = '\n'.join([(f"    ➤ {j['Программа']}{' ' + j['Разряд'] + ' разряда' if j['Разряд'] else ''}"
                              f" в количестве {j['Количество']} человек") for j in program_info])
    message = (
        f"🎉 <b>{user_info.first_name}, ваша заявка успешно принята!</b>\n\n"
        f"📬 <b>Регистрационный номер заявки:</b> {model_id}\n"
        "💬 <b>Информация о коммерческом предложении:</b>\n"
        f"🏢 <b>Компания:</b> {application_data.company_name}\n"
        f"🎓 <b>Обучение:</b>\n"
        f"{program_str}\n\n"
        "Спасибо за выбор нашего учебного центра! ✨"
    )
    # Сообщение администратору
    admin_message = (
        "🔔 <b>Новая запись!</b>\n\n"
        "📄 <b>Детали заявки:</b>\n"
        f"📬 <b>Регистрационный номер заявки:</b> {model_id}\n"
        f"🏢 <b>Компания:</b> {application_data.company_name}\n"
        f"👤 Имя клиента: {user_info.first_name}\n"
        f"💬 Телеграм клиента: @{user_info.username}\n"
        f"📞 Телефон клиента: {application_data.phone_number}\n"
        f"📧 Почта клиента: {application_data.email}\n"
        f"🎓 <b>Обучение:</b>\n"
        f"{program_str}\n"
    )
    kb = main_keyboard(user_id=application_data.user_id, first_name=user_info.first_name)
    # Отправка сообщений ботом
    await bot.send_message(chat_id=application_data.user_id, text=message, reply_markup=kb)
    await bot.send_message(chat_id=settings.ADMIN_ID, text=admin_message, reply_markup=kb)
    return JSONResponse(content={"status": "success", "message": "Заявка успешно отправлена"})


@router.post("/enter_prices", response_class=HTMLResponse)
async def enter_prices(request: Request, application_data: Annotated[str, Form()]):
    application = json.loads(application_data)
    # Рендерим шаблон страницы с передачей данных о заявке
    return templates.TemplateResponse("enter_prices.html", {"request": request, "application": application})


@router.post("/application_work", response_class=JSONResponse)
async def get_programs(request: Request):
    data = await request.json()
    # Составим файл коммерческого предложения
    docx_offer = fill_out_docx_template(data)
    document = FSInputFile(docx_offer)
    total_sum = data.get("all_total")
    message = (
        f"🎉 <b>По вашей заявки под номером №{data['id']}, подготовлено предложение!</b>\n\n"
        f"💰 <b>Сумма контракта составит:</b> {total_sum}\n"
        "В ближайшее время Вы получите подписанное коммерческое предложение, на указанную почту."
        "Спасибо за выбор нашего учебного центра! ✨"
    )
    await bot.send_message(chat_id=data['user_id'], text=message)
    await bot.send_document(chat_id=settings.ADMIN_ID, document=document)
    # Обновим статус в БД
    await ApplicationDAO.update({'id': data['id']}, status=f'Предложение {total_sum}')
    return JSONResponse(content={"success": True})
