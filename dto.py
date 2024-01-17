# Это пример валидаторов в наших ДТО

class Operator:
    class CreationDto(BaseModel):
        office_id: EntityId
        company_id: EntityId | str | None
        email: constr(max_length=36) | None
        username: constr(min_length=2, max_length=25, strict=True, regex=r'^[a-z0-9_]*$',
                         strip_whitespace=True, to_lower=True) | None
        fullname: constr(min_length=1, max_length=50, strict=True, strip_whitespace=True)
        password: str | None
        pin: conint(gt=999, lt=1000000) | None
        expire_session_delta: conint(ge=3600, le=2147483647) | None
        services_id: list[EntityId] | None
        competence_group_id: EntityId | None

        _validate_fullname = validator('fullname', allow_reuse=True)(dto_validator.fullname_validator)
        _validate_password = validator('password', allow_reuse=True)(dto_validator.password_check)

        @validator("email")
        def mail_validate(cls, value):
            res = validate_email(value, allow_smtputf8=False)
            return res.email


class Auth:

    class OperatorLoginDto(BaseModel):
        username: constr(min_length=3, max_length=25, strict=True, regex=r'^[a-zA-Z0-9_]*$',
                         strip_whitespace=True, to_lower=True) | None
        password: str | None

        pin: int | None
        office_id: int | None
