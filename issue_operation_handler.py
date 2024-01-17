# В этом примере, если в операциях поле name is None, то мы берем name из объекта service_operation

async def issue_operation_handler(context: InputContext, transport: RestTransport):
    match context.request.method:
        case sanic.HTTPMethod.GET:
            groupment_items = await transport.get_service(IssueService).get_operations(context.identity.user,
                                                                                       context.r_kwargs['service_id'])
            operation_results = await transport.get_service(IssueService).get_operations_results(context.identity.user,
                                                                                                 groupment_items)
            operations = [
                await groupment_item.values_dict(fk_fields=True, drop_cols=["company", "groupment", "alteration_info"])
                for groupment_item in groupment_items]
            for operation in operations:
                if not operation.get("name"):
                    operation["name"] = operation["service_operation"].get("name")
            return {"operations": operations,
                    "results": [await op.values_dict() for op in operation_results]}
        case sanic.HTTPMethod.POST:
            operation_result = await transport.get_service(IssueService).finish_operation(context.identity.user,
                                                                                          context.dto)
            return await operation_result.values_dict(fk_fields=True, drop_cols=["company", "groupment"])
        case sanic.HTTPMethod.PATCH:
            groupment_item = await transport.get_service(IssueService).begin_operation(context.identity.user,
                                                                                       context.dto)
            return await groupment_item.values_dict(fk_fields=True, drop_cols=["company", "groupment"])
        case sanic.HTTPMethod.DELETE:
            issue_id = await transport.get_service(IssueService).cancel_operation(context.identity.user,
                                                                                  context.r_kwargs['issue_id'])
            return issue_id
