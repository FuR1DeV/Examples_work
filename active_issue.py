# В этом примере была проблема в том что можно было удалить Service (услуга) с активной IssueSession(Сессия оператора который решает проблему клиента) 
# и с проблемами которые уже были ранее решены с этим сервисом. Теперь так сделать нельзя.  

@classmethod
@atomic()
@to_dump_log
async def delete(cls, model: GenericDbType, entity_id: EntityId, protection: "UserIdentity",
                 **kwargs) -> GenericDbType:
    service = await cls.get_or_raise_deleted(model, entity_id)
    cls.check_access(protection.user, model, service)
    unsolved_issues = await Issue.filter(Q(closed=False) |
                                         ~Q(close_code__in=[IssueCloseCode.REMOVED,
                                                            IssueCloseCode.DAILY_PURGE]),
                                         service=entity_id)
    if unsolved_issues:
        raise InconsistencyError(message="Can't delete service with active issue or "
                                         "issue with this service was successful closed")

    await cls.create_alteration(protection.user, service.alteration_info_id)
    await Service.filter(id=entity_id).update(deleted=True)
