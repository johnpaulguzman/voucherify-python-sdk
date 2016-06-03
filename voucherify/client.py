import requests
import json

try:
    from urllib.parse import urlencode, quote
except ImportError:
    from urllib import urlencode
    from urllib import quote

ENDPOINT_URL = 'https://api.voucherify.io/v1'
TIMEOUT = 30 * 1000


class Client(object):
    def __init__(self, application_id, client_secret_key):
        self.timeout = TIMEOUT
        self.headers = {
            'X-App-Id': application_id,
            'X-App-Token': client_secret_key,
            'X-Voucherify-Channel': 'Python-SDK',
            'Content-Type': 'application/json'
        }

    def request(self, path, method='GET', **kwargs):
        try:
            url = ENDPOINT_URL + path

            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs
            )
        except requests.HTTPError as e:
            response = json.loads(e.read())

        if response.headers.get('content-type') and 'json' in response.headers['content-type']:
            result = response.json()
        elif response.status_code == 200:
            result = {
                "data": response.text,
                "reason": response.reason,
                "status": response.status_code
            }
        else:
            raise VoucherifyError('Content-Type of API response is not in a JSON format')

        if result and isinstance(result, dict) and result.get('error'):
            raise VoucherifyError(result)

        return result

    def list(self, query):
        path = '/vouchers/'

        return self.request(
            path,
            params=query
        )

    def get(self, code):
        path = '/vouchers/' + quote(code)

        return self.request(
            path
        )

    def create(self, voucher):
        code = voucher.get('code', '')
        path = '/vouchers/' + quote(code)

        return self.request(
            path,
            data=json.dumps(voucher),
            method='POST'
        )

    def enable(self, code):
        path = '/vouchers/' + quote(code) + '/enable'

        result = self.request(
            path,
            method='POST'
        )

        return result['status'] == 200

    def disable(self, code):
        path = '/vouchers/' + quote(code) + '/disable'

        result = self.request(
            path,
            method='POST'
        )

        return result['status'] == 200

    def redemption(self, code):
        path = '/vouchers/' + quote(code) + '/redemption'

        return self.request(
            path
        )

    def redemptions(self, query):
        path = '/redemptions'

        return self.request(
            path,
            params=query
        )

    def redeem(self, code, tracking_id=None):
        context = {}

        if code and isinstance(code, dict):
            context = code
            code = context['voucher']
            del context['voucher']

        path = '/vouchers/' + quote(code) + '/redemption'

        if tracking_id:
            path = path + '?' + urlencode({'tracking_id': tracking_id})

        return self.request(
            path,
            method='POST',
            data=json.dumps(context),
        )

    def rollback(self, redemption_id, reason=None):
        path = '/redemptions/' + redemption_id + '/rollback'

        if reason:
            path = path + '?' + urlencode({'reason': reason})

        return self.request(
            path,
            method='POST'
        )

    def publish(self, campaign_name=""):
        path = '/vouchers/publish'

        if campaign_name and isinstance(campaign_name, dict):
            path = path + '?' + urlencode(campaign_name)
        else:
            path = path + '?' + urlencode({'campaign': campaign_name})

        return self.request(
            path,
            method='POST'
        )


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
