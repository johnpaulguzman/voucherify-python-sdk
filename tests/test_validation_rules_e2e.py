from voucherify import Client as voucherifyClient

"""
Initialization
"""
voucherify = voucherifyClient(
    application_id="c70a6f00-cf91-4756-9df5-47628850002b",
    client_secret_key="3266b9f8-e246-4f79-bdf0-833929b1380c"
)

def test_validationRuleCRUD():
    payload = {
        "name": "Redeemable Once for new Customers test",
        "error":
        {
            "message": "You can not get discount because you are not our new customer or you have already used that code."
        },
        "rules":
        {
            "1":
            {
                "name": "customer.segment",
                "conditions":
                {
                    "$is":
                    [
                        "seg_n3vVcU5t0m3rs4rEPr3C1oU5"
                    ]
                },
                "error":
                {
                    "message": "You must be our new customer in order to get discount."
                }
            },
            "2":
            {
                "name": "redemption.count.per_customer",
                "conditions":
                {
                    "$less_than_or_equal":
                    [
                        1
                    ]
                }
            },
            "logic": "1 and 2"
        }
    }
# create
    result = voucherify.validation_rules.create(payload)
    assert result.get('name') == payload.get('name')
    assert result.get('rules', {}).get('logic') == payload.get('rules', {}).get('logic')
# retrieve
    validation_rule = voucherify.validation_rules.get(result.get('id'))
    assert validation_rule.get('name') == result.get('name')
    assert validation_rule.get('rules', {}).get('logic') == result.get('rules', {}).get('logic')
# update
    updatePayload = {
        "id": validation_rule.get('id'),
        "name": 'Redeemable Once for new Customers test (2)',
    }
    updated_vr = voucherify.validation_rules.update(updatePayload)
    assert updated_vr.get('name') == updatePayload.get('name')
# list
    filter_params = {
        "limit": 1,
        "page": 1,
    }
    vr_list = voucherify.validation_rules.list(query=filter_params)
    assert vr_list.get('data_ref') == 'data'
    assert isinstance(vr_list.get('data'), list)
    assert vr_list.get('data') != []
    assert vr_list['data'][0]['object'] == 'validation_rules'
# assign
    assigneePayload = {"voucher": "-"}
    vr_assignment = voucherify.validation_rules.assign(result['id'], assigneePayload)
    assert vr_assignment.get('message') == "Resource not found"
    assert vr_assignment.get('details') == "Cannot find voucher with id -"
    assert vr_assignment.get('resource_type') == "voucher"
