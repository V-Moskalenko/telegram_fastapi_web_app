import re

from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationError


class ApplicationServiceData(BaseModel):
    training_type_id: int = Field(..., alias='training_type_id')
    training_program_id: int = Field(..., alias='training_program_id')
    training_rank: str = Field(..., alias='training_rank')
    people_count: int = Field(..., alias='people_count')

    @field_validator('training_type_id', 'training_program_id', 'people_count', mode='before')
    def convert_to_int(cls, v):
        if isinstance(v, str):
            try:
                return int(v)  # Преобразуем строку в int
            except ValueError:
                raise ValueError('Значение должно быть числом или строкой, которую можно преобразовать в int')
        return v


class ApplicationData(BaseModel):
    user_id: int = Field(..., alias='user_id', description="ID клиента")
    company_name: str = Field(..., alias='company_name', description="Наименование компании")
    phone_number: str = Field(..., alias='phone_number', description="Номер телефона")
    email: EmailStr = Field(..., alias='email', description="Почта")
    services: list[ApplicationServiceData] = Field(..., description="Список заявок")
    status: str = Field(..., alias='status', description="Статус заявки")

    @field_validator('user_id', mode='before')
    def convert_to_int(cls, v):
        if isinstance(v, str):
            try:
                return int(v)  # Преобразуем строку в int
            except ValueError:
                raise ValueError('Значение должно быть числом или строкой, которую можно преобразовать в int')
        return v

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        pattern = re.compile(r"^\+7\d{10}$|^8\d{10}$")
        if not pattern.match(v):
            raise ValidationError('Некорректный номер телефона. Ожидается формат +7XXXXXXXXXX или 8XXXXXXXXXX.')
        return v
