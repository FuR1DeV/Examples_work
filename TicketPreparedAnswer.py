# В этом примере реализовано переопределение методов на создание и обновлении Заранее подготовленных ответов на приоритет.
# Условия такие что "ответ" должен совпадать с "селектом" который уже есть в БД

class TicketExtraPreparedAnswerAccess(AccessMiddleware):

    @classmethod
    @atomic()
    async def create(cls, model: TicketExtraPreparedAnswer, protection: "UserIdentity",
                     dto: access_dto.TicketExtraPreparedAnswer.CreationDto,
                     transport: Transport = None, **kwargs) -> GenericDbType:
        extra_field = await cls.get_or_raise_deleted(TicketExtraField, dto.field_id)
        if extra_field.answer_type == AnswerTypes.TEXT:
            return await cls._create(model=model, protection=protection, dto=dto, **kwargs)
        await extra_field.fetch_related("selects")
        for select in extra_field.selects:
            if select.text == dto.answer:
                return await cls._create(model=model, protection=protection, dto=dto, **kwargs)
        raise InconsistencyError(message=f"Answer doesn't match "
                                         f"the current selections",
                                 context={"possible_selects": [i.text for i in extra_field.selects]})

    @classmethod
    @atomic()
    async def update(cls, model: TicketExtraPreparedAnswer, entity_id: EntityId, protection: "UserIdentity",
                     dto: access_dto.TicketExtraPreparedAnswer.UpdateDto,
                     transport: Transport = None, **kwargs) -> GenericDbType:
        extra_field = await cls.get_or_raise_deleted(TicketExtraField, dto.field_id)
        if extra_field.answer_type == AnswerTypes.TEXT:
            return await cls._update(model=model, entity_id=entity_id,
                                     protection=protection, dto=dto, **kwargs)
        await extra_field.fetch_related("selects")
        for select in extra_field.selects:
            if select.text == dto.answer:
                return await cls._update(model=model, entity_id=entity_id, protection=protection,
                                         dto=dto, **kwargs)
        raise InconsistencyError(message=f"Answer doesn't match "
                                         f"the current selections",
                                 context={"possible_selects": [i.text for i in extra_field.selects]})
