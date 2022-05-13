from voucherify import Client as voucherifyClient

"""
Initialization
"""
voucherify = voucherifyClient(
    application_id="c70a6f00-cf91-4756-9df5-47628850002b",
    client_secret_key="3266b9f8-e246-4f79-bdf0-833929b1380c"
)

def test_orderCRUD():
    payload = {
        "customer": {
            "source_id": "track_+EUcXP8WDKXGf3mYmWxbJvEosmKXi3Aw",
            "name": "Alice Morgan",
            "email": "alice@morgan.com",
            "description": "Sample description of customer",
            "metadata": {
                "locale": "en-GB",
                "shoeSize": 5,
                "favourite_brands": ["Armani", "L’Autre Chose", "Vicini"],
            },
        },
        "amount": 2000,
        "items": [{"product_id": "prod_083e98e0aa861107bb", "quantity": 1}],
        "metadata": {"payment_mean": ["credit-card"]},
    }
# create
    result = voucherify.orders.create(payload)
    assert result.get('description') == payload.get('description')
    assert result.get('email') == payload.get('email')
# retrieve
    order = voucherify.orders.get(result.get('id'))
    assert order.get('status') == 'CREATED'
    assert order.get('email') == result.get('email')
# update
    updatePayload = {
        "id": order.get('id'),
        "status": 'CANCELED',
    }
    updatedorder = voucherify.orders.update(updatePayload)
    assert updatedorder.get('status') == updatePayload.get('status')
# list
    filter_params = {
        "limit": 1,
        "page": 1,
    }
    ordersList = voucherify.orders.list(query=filter_params)
    assert ordersList.get('data_ref') == 'orders'
    assert isinstance(ordersList.get('orders'), list)
