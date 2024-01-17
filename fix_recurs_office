    @classmethod
    @atomic()
    @to_dump_log
    async def update(cls, model: Office, entity_id: EntityId, protection: "UserIdentity",
                     dto: PdModel, **kwargs) -> GenericDbType:
        if dto.parent_office_id and entity_id == dto.parent_office_id:
            raise InconsistencyError(message="The office cannot be the ancestor of itself")

        office = await cls._update(model=model, entity_id=entity_id,
                                   protection=protection, dto=dto)
        if dto.parent_office_id:

            async def raise_recursion(offices_input: list[Office]) -> None:
                inheritor_offices = await Office.filter(parent_office_id__in=[i.id for i in offices_input])
                if not inheritor_offices:
                    return
                if dto.parent_office_id in [i.parent_office_id for i in inheritor_offices]:
                    raise InconsistencyError(message="Recursive Office!")
                return await raise_recursion(inheritor_offices)

            await raise_recursion([office])
        return office
