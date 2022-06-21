from voucherify import Client as voucherifyClient

"""
Initialization
"""
voucherify = voucherifyClient(
    application_id="c70a6f00-cf91-4756-9df5-47628850002b",
    client_secret_key="3266b9f8-e246-4f79-bdf0-833929b1380c"
)

def test_productCRUD():
    payload = {
        "name": "line_item_A",
        "metadata": {"tax": 5, "description": "Line Item A Description"},
        "price": 2500,
        "created_at": "2020-06-14T09:58:39Z",
    }
# create
    result = voucherify.products.create(payload)
    assert result.get('name') == payload.get('name')
    assert result.get('price') == payload.get('price')
# retrieve
    product = voucherify.products.get(result.get('id'))
    assert product.get('name') == result.get('name')
# update
    updatePayload = {
        "id": product.get('id'),
        "price": 5000,
    }
    updatedproduct = voucherify.products.update(updatePayload)
    assert updatedproduct.get('price') == updatePayload.get('price')
# list
    filter_params = {
        "limit": 1,
        "page": 1,
    }
    productsList = voucherify.products.list(query=filter_params)
    assert productsList.get('data_ref') == 'products'
    assert isinstance(productsList.get('products'), list)
