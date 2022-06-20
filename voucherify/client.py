import requests
import json

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

ENDPOINT_URL = 'https://api.voucherify.io'
TIMEOUT = 180


class VoucherifyRequest(object):
    def __init__(self, application_id, client_secret_key, api_endpoint=None, timeout=TIMEOUT, strict=False):
        self.strict = strict
        self.timeout = timeout
        self.url = (api_endpoint if api_endpoint else ENDPOINT_URL) + "/v1"
        self.headers = {
            'X-App-Id': application_id,
            'X-App-Token': client_secret_key,
            'X-Voucherify-Channel': 'Python-SDK',
            'Content-Type': 'application/json'
        }

    def request(self, path, method='GET', strict=None, **kwargs):
        try:
            url = self.url + path
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
        except (requests.HTTPError, requests.ConnectionError) as e:
            voucherify_error = VoucherifyError(e)
            raise_exception = strict if strict is not None else self.strict
            if raise_exception:
                raise voucherify_error
            return voucherify_error.body

        if response.headers.get('content-type') and 'json' in response.headers['content-type']:
            result = response.json()
        else:
            result = response.text

        return result


class Vouchers(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Vouchers, self).__init__(*args, **kwargs)
        self.base_path = "/vouchers/"

    def list(self, query, **kwargs):
        return self.request(self.base_path, params=query, **kwargs)

    def get(self, code, **kwargs):
        path = self.base_path + quote(code)
        return self.request(path, **kwargs)

    def create(self, voucher, **kwargs):
        code = voucher.get('code', '')
        path = self.base_path + quote(code)
        return self.request(
            path,
            data=json.dumps(voucher),
            method='POST',
            **kwargs
        )

    def update(self, voucher_update, **kwargs):
        path = self.base_path + quote(voucher_update.get('code'))
        return self.request(
            path,
            data=json.dumps(voucher_update),
            method='PUT',
            **kwargs
        )

    def enable(self, code, **kwargs):
        path = self.base_path + quote(code) + "/enable"
        return self.request(path, method='POST', **kwargs)

    def disable(self, code, **kwargs):
        path = self.base_path + quote(code) + "/disable"
        return self.request(path, method='POST', **kwargs)

    def releaseValidationSession(self, code, sessionKey, **kwargs):
        path = self.base_path + quote(code) + '/sessions/' + quote(sessionKey)
        return self.request(path, method='DELETE', **kwargs)


class Redemptions(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Redemptions, self).__init__(*args, **kwargs)
        self.base_path = "/redemptions/"

    def redeem(self, code, tracking_id=None, **kwargs):
        context = {}
        if code and isinstance(code, dict):
            context = code
            code = context['voucher']
            del context['voucher']

        path = "/vouchers/" + quote(code) + "/redemption"

        params = {}
        if tracking_id:
            params['tracking_id'] = tracking_id

        return self.request(
            path,
            method='POST',
            data=json.dumps(context),
            params=params,
            **kwargs
        )

    def redeemStackable(self, params, **kwargs):
        return self.request(
            self.base_path,
            method='POST',
            data=json.dumps(params),
            **kwargs
        )

    def getForVoucher(self, code, **kwargs):
        path = '/vouchers/' + quote(code) + '/redemption'
        return self.request(path, **kwargs)

    def list(self, query, **kwargs):
        return self.request(self.base_path, params=query, **kwargs)

    def rollback(self, redemption_id, reason=None, data=None, **kwargs):
        path = self.base_path + redemption_id + "/rollback"

        data = {} if data is None else data
        params = {}
        if reason:
            params['reason'] = reason

        return self.request(
            path,
            method='POST',
            data=json.dumps(data),
            params=params,
            **kwargs
        )


class Validations(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Validations, self).__init__(*args, **kwargs)
        self.base_path = "/validations/"

    def validateVoucher(self, code, params, **kwargs):
        path = '/vouchers/' + quote(code) + '/validate'
        return self.request(
            path,
            method='POST',
            data=json.dumps(params),
            **kwargs
        )

    def validateStackable(self, params, **kwargs):
        return self.request(
            self.base_path,
            method='POST',
            data=json.dumps(params),
            **kwargs
        )


class Distributions(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Distributions, self).__init__(*args, **kwargs)

    def publish(self, params, **kwargs):
        path = '/vouchers/publish'
        return self.request(
            path,
            method='POST',
            data=json.dumps(params),
            **kwargs
        )


class Customers(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Customers, self).__init__(*args, **kwargs)
        self.base_path = "/customers/"

    def create(self, customer, **kwargs):
        return self.request(
            self.base_path,
            data=json.dumps(customer),
            method='POST',
            **kwargs
        )

    def get(self, customer_id, **kwargs):
        path = self.base_path + quote(customer_id)
        return self.request(path, **kwargs)

    def update(self, customer, **kwargs):
        path = self.base_path + quote(customer.get('id'))
        return self.request(
            path,
            data=json.dumps(customer),
            method='PUT',
            **kwargs
        )

    def delete(self, customer_id, **kwargs):
        path = self.base_path + quote(customer_id)
        return self.request(path, method='DELETE', **kwargs)

    def list(self, query, **kwargs):
        return self.request(self.base_path, params=query, **kwargs)


class Orders(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Orders, self).__init__(*args, **kwargs)
        self.base_path = "/orders/"

    def create(self, order, **kwargs):
        return self.request(
            self.base_path,
            data=json.dumps(order),
            method='POST',
            **kwargs
        )

    def get(self, order_id, **kwargs):
        path = self.base_path + quote(order_id)
        return self.request(path, **kwargs)

    def update(self, order, **kwargs):
        path = self.base_path + quote(order.get('id'))
        return self.request(
            path,
            data=json.dumps(order),
            method='PUT',
            **kwargs
        )

    def list(self, query, **kwargs):
        return self.request(self.base_path, params=query, **kwargs)


class Products(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(Products, self).__init__(*args, **kwargs)
        self.base_path = "/products/"

    def create(self, products, **kwargs):
        return self.request(
            self.base_path,
            data=json.dumps(products),
            method='POST',
            **kwargs
        )

    def get(self, products_id, **kwargs):
        path = self.base_path + quote(products_id)
        return self.request(path, **kwargs)

    def update(self, products, **kwargs):
        path = self.base_path + quote(products.get('id'))
        return self.request(
            path,
            data=json.dumps(products),
            method='PUT',
            **kwargs
        )

    def list(self, query, **kwargs):
        return self.request(self.base_path, params=query, **kwargs)


class ValidationRules(VoucherifyRequest):
    def __init__(self, *args, **kwargs):
        super(ValidationRules, self).__init__(*args, **kwargs)
        self.base_path = "/validation-rules/"

    def create(self, validation_rule, **kwargs):
        return self.request(
            self.base_path,
            data=json.dumps(validation_rule),
            method='POST',
            **kwargs
        )

    def get(self, validation_rule_id, **kwargs):
        path = self.base_path + quote(validation_rule_id)
        return self.request(path, **kwargs)

    def update(self, validation_rule, **kwargs):
        path = self.base_path + quote(validation_rule.get('id'))
        return self.request(
            path,
            data=json.dumps(validation_rule),
            method='PUT',
            **kwargs
        )

    def list(self, query, **kwargs):
        return self.request(self.base_path, params=query, **kwargs)

    def assign(self, validation_rule_id, assignee_payload, **kwargs):
        path = self.base_path + quote(validation_rule_id) + "/assignments"
        return self.request(
            path,
            data=json.dumps(assignee_payload),
            method='POST',
            **kwargs
        )


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
        self.validation_rules = ValidationRules(*args, **kwargs)


class VoucherifyError(Exception):
    def __init__(self, request_exception):
        self._e = request_exception
        self._request = request_exception.request
        self._response = request_exception.response
        if self._response is not None:
            self.body = self._response.json()
            self.code = self.body.get('code')
            self.message = self.body.get('message')
        else:
            self.code = None
            self.message = repr(self._e)
            self.body = {'message': self.message}
        Exception.__init__(self, self.message)


__all__ = ['Client']
