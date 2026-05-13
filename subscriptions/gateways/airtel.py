"""
Airtel Money (Uganda) Gateway
API Docs: https://developers.airtel.africa/documentation
Sandbox:  https://openapiuat.airtel.africa

Flow:
  1. Authenticate → get OAuth2 access token
  2. POST payment request → Airtel sends USSD push to customer
  3. Customer confirms on phone
  4. Airtel hits our callback URL with result
  5. We poll status as fallback
"""
import uuid
import requests
from django.conf import settings


class AirtelMoneyGateway:

    def __init__(self):
        self.base_url      = settings.AIRTEL_BASE_URL.rstrip('/')
        self.client_id     = settings.AIRTEL_CLIENT_ID
        self.client_secret = settings.AIRTEL_CLIENT_SECRET
        self.environment   = settings.AIRTEL_ENVIRONMENT
        self.currency      = settings.AIRTEL_CURRENCY
        self.callback_url  = settings.AIRTEL_CALLBACK_URL
        self._token_cache  = None

    # ── INTERNAL ─────────────────────────────────────────────

    def _get_access_token(self) -> str:
        """OAuth2 client credentials flow."""
        if self._token_cache:
            return self._token_cache

        resp = requests.post(
            f'{self.base_url}/auth/oauth2/token',
            json={
                'client_id':     self.client_id,
                'client_secret': self.client_secret,
                'grant_type':    'client_credentials',
            },
            headers={'Content-Type': 'application/json'},
            timeout=30,
        )
        resp.raise_for_status()
        token = resp.json().get('access_token')
        self._token_cache = token
        return token

    def _headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self._get_access_token()}',
            'Content-Type':  'application/json',
            'Accept':        'application/json',
            'X-Country':     'UG',
            'X-Currency':    self.currency,
        }

    # ── PUBLIC API ───────────────────────────────────────────

    def request_payment(self, phone_number: str, amount: int,
                        plan_name: str, subscription_id: int) -> dict:
        """
        Initiate an Airtel Money collection.

        Args:
            phone_number:    Uganda number e.g. '256751234567' (no +)
            amount:          Amount in UGX
            plan_name:       e.g. 'JobHub Growth Plan'
            subscription_id: Our internal subscription PK

        Returns:
            {
              'success':      bool,
              'reference_id': str,
              'transaction_id': str | None,
              'error':        str | None,
            }
        """
        # Normalise number
        phone = str(phone_number).strip().lstrip('+')
        if phone.startswith('0'):
            phone = '256' + phone[1:]
        if not phone.startswith('256'):
            phone = '256' + phone

        reference_id = str(uuid.uuid4())

        payload = {
            'reference': reference_id,
            'subscriber': {
                'country':  'UG',
                'currency': self.currency,
                'msisdn':   phone,
            },
            'transaction': {
                'amount':   amount,
                'country':  'UG',
                'currency': self.currency,
                'id':       str(subscription_id),
            },
        }

        try:
            resp = requests.post(
                f'{self.base_url}/merchant/v2/payments/',
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            data = resp.json()

            if resp.status_code in (200, 201) and data.get('status', {}).get('success'):
                txn_id = data.get('data', {}).get('transaction', {}).get('id')
                return {
                    'success':        True,
                    'reference_id':   reference_id,
                    'transaction_id': txn_id,
                    'error':          None,
                }
            else:
                message = data.get('status', {}).get('message', resp.text)
                return {
                    'success':        False,
                    'reference_id':   reference_id,
                    'transaction_id': None,
                    'error':          f'Airtel error: {message}',
                }
        except requests.RequestException as e:
            return {
                'success':        False,
                'reference_id':   reference_id,
                'transaction_id': None,
                'error':          str(e),
            }

    def check_payment_status(self, transaction_id: str) -> dict:
        """
        Poll the transaction status.

        Returns:
            {
              'status':  'TS' (success) | 'TF' (failed) | 'TIP' (in progress),
              'message': str,
              'raw':     dict,
            }
        """
        try:
            resp = requests.get(
                f'{self.base_url}/standard/v1/payments/{transaction_id}',
                headers=self._headers(),
                timeout=30,
            )
            data   = resp.json()
            status = data.get('data', {}).get('transaction', {}).get('status', 'TIP')
            return {
                'status':  status,
                'message': data.get('status', {}).get('message', ''),
                'raw':     data,
            }
        except requests.RequestException as e:
            return {'status': 'TIP', 'message': str(e), 'raw': {}}