# В этом примере реализовано переопределение метода create на создание оператора, в котором учтены условия поставленные заказчиком


class OperatorAccess(AccessMiddleware):
    @classmethod
    @atomic()
    @to_dump_log
    async def create(cls, model: GenericDbType, protection: "UserIdentity", dto: access_dto.Operator.CreationDto,
                     **kwargs) -> GenericDbType:
        if dto.email:
            if await model.exists(username=dto.email, deleted=False):
                raise InconsistencyError(message=f"{model.__name__} already exists")
        crypted_password, salt = BaseCrypto.encrypt_password(dto.password)
        dto.password = crypted_password
        dto.__dict__['salt'] = salt

        if not dto.email and not dto.username:
            raise InconsistencyError(message="Need email or username!")
        if not dto.password and not dto.pin:
            raise InconsistencyError(message="Need password or pin")
        if dto.pin:
            if await Operator.get_or_none(pin=dto.pin, office_id=dto.office_id):
                raise InconsistencyError(message="This pin already exist at this office")
        if dto.password:
            crypted_password, salt = BaseCrypto.encrypt_password(dto.password)
            dto.password = crypted_password
            dto.__dict__['salt'] = salt
        operator = await cls._create(model=model, protection=protection, dto=dto, **kwargs)
        await operator.fetch_related("services")
        return operator
