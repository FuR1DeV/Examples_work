# В этом примере реализовано переопределение методов на создание и удаление Рабочего Дня (WorkDay) с условиями от заказчика.
# Есть определенные временные интервалы, и при создании раб дня надо учесть чтобы эти интервалы не пересекались между собой,
# А при обновлении раб дня надо удалить лишние интервалы и создать новые.


class WorkDayAccess(AccessMiddleware):

    @classmethod
    async def _check_time_interval(cls, time_intervals_ids: list[int]) -> list[TimeInterval]:
        time_intervals = await TimeInterval.filter(id__in=time_intervals_ids)
        if len(time_intervals) != len(time_intervals_ids):
            raise InconsistencyError(message="Some Time Intervals not found")
        for interval in time_intervals:
            time_interval_id = interval.id
            begin_prev, stop_prev = interval.begin, interval.stop
            for time_interval in time_intervals:
                if time_interval.id == time_interval_id:
                    continue
                if begin_prev < time_interval.begin < stop_prev or \
                        begin_prev < time_interval.stop < stop_prev:
                    raise InconsistencyError(
                        message=f"This interval time id: {time_interval_id} already in use "
                                f"by Time interval id: {time_interval.id}")
        return time_intervals

    @classmethod
    @atomic()
    @to_dump_log
    async def create(cls, model: GenericDbType, protection: "UserIdentity",
                     dto: access_dto.WorkInterval.Day.CreationDto,
                     **kwargs) -> GenericDbType:
        workday = await AccessMiddleware._create(model=model, protection=protection, dto=dto)
        if dto.intervals_ids:
            time_intervals = await cls._check_time_interval(dto.intervals_ids)
            for time_interval in time_intervals:
                await DayInterval.create(company_id=dto.company_id,
                                         interval=time_interval, workday=workday)
        return workday

    @classmethod
    @atomic()
    @to_dump_log
    async def update(cls, model: GenericDbType, entity_id: EntityId, protection: "UserIdentity",
                     dto: access_dto.WorkInterval.Day.UpdateDto,
                     **kwargs) -> GenericDbType:
        workday = await WorkDay.get_or_none(id=entity_id).prefetch_related("dayintervals")
        if workday:
            if dto.intervals_ids:
                time_intervals = await cls._check_time_interval(dto.intervals_ids)
                if workday.dayintervals:
                    workday_interval_ids = [di.interval_id for di in workday.dayintervals]
                    original = workday_interval_ids.copy()
                    workday_interval_ids.extend(dto.intervals_ids)
                    for wdi_id in workday_interval_ids:
                        if wdi_id not in original:
                            time_interval = await TimeInterval.get_or_none(id=wdi_id)
                            await DayInterval.create(company_id=workday.company_id,
                                                     interval=time_interval, workday=workday)
                        if wdi_id not in dto.intervals_ids:
                            await DayInterval.filter(interval_id=wdi_id,
                                                     workday_id=workday.id).delete()
                else:
                    for time_interval in time_intervals:
                        await DayInterval.create(company_id=workday.company_id,
                                                 interval=time_interval, workday=workday)
                dto.intervals_ids = None
            return await AccessMiddleware._update(model=model, entity_id=entity_id, protection=protection, dto=dto)
        raise InconsistencyError(message="Work Day not found")
