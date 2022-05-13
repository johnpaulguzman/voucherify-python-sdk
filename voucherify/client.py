import requests
import json

try:
    from urllib.parse import urlencode, quote
except ImportError:
    from urllib import urlencode
    from urllib import quote

ENDPOINT_URL = 'https://api.voucherify.io'
TIMEOUT = 180


class VoucherifyRequest(object):
    def __init__(self, application_id, client_secret_key, api_endpoint=None, timeout=TIMEOUT):
        self.timeout = timeout
        self.url = (api_endpoint if api_endpoint else ENDPOINT_URL) + "/v1"
        self.headers = {
            'X-App-Id': application_id,
            'X-App-Token': client_secret_key,
            'X-Voucherify-Channel': 'Python-SDK',
            'Content-Type': 'application/json'
        }

    def request(self, path, method='GET', **kwargs):
        try:
            url = self.url + path
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs
            )
        except requests.HTTPError as e:
            response = json.loads(e.read())
        except requests.ConnectionError as e:
            raise VoucherifyError(e)

        if response.headers.get('content-type') and 'json' in response.headers['content-type']:
            result = response.json()
        else:
            result = response.text

        return result


class Vouchers(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Vouchers, self).__init__(*args, **kwargs)
        self.base_path = "/vouchers/"

    def list(self, query):
        return self.request(self.base_path, params=query)

    def get(self, code):
        path = self.base_path + quote(code)
        return self.request(path)

    def create(self, voucher):
        code = voucher.get('code', '')
        path = self.base_path + quote(code)
        return self.request(
            path,
            data=json.dumps(voucher),
            method='POST'
        )

    def update(self, voucher_update):
        path = self.base_path + quote(voucher_update.get('code'))
        return self.request(
            path,
            data=json.dumps(voucher_update),
            method='PUT'
        )

    def enable(self, code):
        path = self.base_path + quote(code) + "/enable"
        return self.request(path, method='POST')

    def disable(self, code):
        path = self.base_path + quote(code) + "/disable"
        return self.request(path, method='POST')

    def releaseValidationSession(self, code, sessionKey):
        path = self.base_path + quote(code) + '/sessions/' + quote(sessionKey)
        return self.request(path, method='DELETE')


class Redemptions(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Redemptions, self).__init__(*args, **kwargs)
        self.base_path = "/redemptions/"

    def redeem(self, code, tracking_id=None):
        context = {}
        if code and isinstance(code, dict):
            context = code
            code = context['voucher']
            del context['voucher']

        path = "/vouchers/" + quote(code) + "/redemption"

        if tracking_id:
            path = path + "?" + urlencode({'tracking_id': tracking_id})

        return self.request(
            path,
            method='POST',
            data=json.dumps(context),
        )

    def redeemStackable(self, params):
        return self.request(
            self.base_path,
            method='POST',
            data=json.dumps(params)
        )

    def getForVoucher(self, code):
        path = '/vouchers/' + quote(code) + '/redemption'
        return self.request(path)

    def list(self, query):
        return self.request(self.base_path, params=query)

    def rollback(self, redemption_id, reason=None):
        path = self.base_path + redemption_id + "/rollback"
        if reason:
            path = path + "?" + urlencode({'reason': reason})

        return self.request(path, method='POST')


class Validations(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Validations, self).__init__(*args, **kwargs)
        self.base_path = "/validations/"

    def validateVoucher(self, code, params):
        path = '/vouchers/' + quote(code) + '/validate'
        return self.request(
            path,
            method='POST',
            data=json.dumps(params),
        )

    def validateStackable(self, params):
        return self.request(
            self.base_path,
            method='POST',
            data=json.dumps(params)
        )


class Distributions(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Distributions, self).__init__(*args, **kwargs)

    def publish(self, params):
        path = '/vouchers/publish'
        return self.request(
            path,
            method='POST',
            data=json.dumps(params)
        )


class Customers(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Customers, self).__init__(*args, **kwargs)
        self.base_path = "/customers/"

    def create(self, customer):
        return self.request(
            self.base_path,
            data=json.dumps(customer),
            method='POST'
        )

    def get(self, customer_id):
        path = self.base_path + quote(customer_id)
        return self.request(path)

    def update(self, customer):
        path = self.base_path + quote(customer.get('id'))
        return self.request(
            path,
            data=json.dumps(customer),
            method='PUT'
        )

    def delete(self, customer_id):
        path = self.base_path + quote(customer_id)
        return self.request(path, method='DELETE')

    def list(self, query):
        return self.request(self.base_path, params=query)


class Orders(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Orders, self).__init__(*args, **kwargs)
        self.base_path = "/orders/"

    def create(self, order):
        return self.request(
            self.base_path,
            data=json.dumps(order),
            method='POST'
        )

    def get(self, order_id):
        path = self.base_path + quote(order_id)
        return self.request(path)

    def update(self, order):
        path = self.base_path + quote(order.get('id'))
        return self.request(
            path,
            data=json.dumps(order),
            method='PUT'
        )

    def list(self, query):
        return self.request(self.base_path, params=query)


class Products(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Products, self).__init__(*args, **kwargs)
        self.base_path = "/products/"

    def create(self, products):
        return self.request(
            self.base_path,
            data=json.dumps(products),
            method='POST'
        )

    def get(self, products_id):
        path = self.base_path + quote(products_id)
        return self.request(path)

    def update(self, products):
        path = self.base_path + quote(products.get('id'))
        return self.request(
            path,
            data=json.dumps(products),
            method='PUT'
        )

    def list(self, query):
        return self.request(self.base_path, params=query)


class Client(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.customers = Customers(*args, **kwargs)
        self.vouchers = Vouchers(*args, **kwargs)
        self.redemptions = Redemptions(*args, **kwargs)
        self.validations = Validations(*args, **kwargs)
        self.distributions = Distributions(*args, **kwargs)
        self.orders = Orders(*args, **kwargs)
        self.products = Products(*args, **kwargs)


class VoucherifyError(Exception):
    def __init__(self, result):
        self.result = result
        self.code = None
        self.message = None

        try:
            self.type = result['error_code']
            self.message = result['error_msg']
        except:
            self.type = ''
            self.message = result

        Exception.__init__(self, self.message)


__all__ = ['Client']
