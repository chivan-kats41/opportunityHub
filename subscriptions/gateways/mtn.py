"""
MTN Mobile Money (Uganda) Gateway
API Docs: https://momodeveloper.mtn.com/docs/services/collection
Sandbox:  https://sandbox.momodeveloper.mtn.com

Flow:
  1. Request payment → MTN sends USSD push to user's phone
  2. User approves on phone
  3. MTN calls our callback URL with result
  4. We also poll the status endpoint as a fallback
"""
import uuid
import requests
import base64
from django.conf import settings


class MTNMoMoGateway:

    def __init__(self):
        self.base_url     = settings.MTN_MOMO_BASE_URL.rstrip('/')
        self.sub_key      = settings.MTN_MOMO_SUBSCRIPTION_KEY
        self.api_user     = settings.MTN_MOMO_API_USER
        self.api_key      = settings.MTN_MOMO_API_KEY
        self.environment  = settings.MTN_MOMO_ENVIRONMENT
        self.currency     = settings.MTN_MOMO_CURRENCY
        self.callback_url = settings.MTN_MOMO_CALLBACK_URL

    # ── INTERNAL ─────────────────────────────────────────────

    def _get_access_token(self):
        """Exchange API user + key for a Bearer token."""
        credentials = f'{self.api_user}:{self.api_key}'
        encoded     = base64.b64encode(credentials.encode()).decode()

        resp = requests.post(
            f'{self.base_url}/collection/token/',
            headers={
                'Authorization':           f'Basic {encoded}',
                'Ocp-Apim-Subscription-Key': self.sub_key,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get('access_token')

    def _headers(self, reference_id=None):
        token = self._get_access_token()
        h = {
            'Authorization':             f'Bearer {token}',
            'X-Target-Environment':      self.environment,
            'Ocp-Apim-Subscription-Key': self.sub_key,
            'Content-Type':              'application/json',
        }
        if reference_id:
            h['X-Reference-Id'] = reference_id
        return h

    # ── PUBLIC API ───────────────────────────────────────────

    def request_payment(self, phone_number: str, amount: int,
                        plan_name: str, subscription_id: int) -> dict:
        """
        Initiate a collection request — sends USSD push to the customer.

        Args:
            phone_number:    Uganda number, e.g. '256701234567' (no +)
            amount:          Amount in UGX (integer)
            plan_name:       Human-readable plan, e.g. 'JobHub Pro Plan'
            subscription_id: Our internal subscription PK (used as external ref)

        Returns:
            {
              'success':      bool,
              'reference_id': str  (UUID — use to poll status),
              'error':        str | None,
            }
        """
        reference_id = str(uuid.uuid4())

        # Normalise phone: remove leading 0, ensure 256 prefix
        phone = str(phone_number).strip().lstrip('+')
        if phone.startswith('0'):
            phone = '256' + phone[1:]
        if not phone.startswith('256'):
            phone = '256' + phone

        payload = {
            'amount':       str(amount),
            'currency':     self.currency,
            'externalId':   str(subscription_id),
            'payer': {
                'partyIdType': 'MSISDN',
                'partyId':     phone,
            },
            'payerMessage': f'Payment for {plan_name}',
            'payeeNote':    f'JobHub subscription — {plan_name}',
        }

        if self.callback_url:
            payload['callbackUrl'] = self.callback_url

        try:
            resp = requests.post(
                f'{self.base_url}/collection/v1_0/requesttopay',
                json=payload,
                headers=self._headers(reference_id=reference_id),
                timeout=30,
            )
            # MTN returns 202 Accepted on success (not 200)
            if resp.status_code == 202:
                return {'success': True, 'reference_id': reference_id, 'error': None}
            else:
                return {
                    'success':      False,
                    'reference_id': reference_id,
                    'error':        f'MTN error {resp.status_code}: {resp.text}',
                }
        except requests.RequestException as e:
            return {'success': False, 'reference_id': reference_id, 'error': str(e)}

    def check_payment_status(self, reference_id: str) -> dict:
        """
        Poll the status of a previously initiated payment.

        Returns:
            {
              'status':  'SUCCESSFUL' | 'FAILED' | 'PENDING',
              'reason':  str | None,
              'raw':     dict,
            }
        """
        try:
            resp = requests.get(
                f'{self.base_url}/collection/v1_0/requesttopay/{reference_id}',
                headers=self._headers(),
                timeout=30,
            )
            data   = resp.json()
            status = data.get('status', 'PENDING')
            return {
                'status': status,
                'reason': data.get('reason'),
                'raw':    data,
            }
        except requests.RequestException as e:
            return {'status': 'PENDING', 'reason': str(e), 'raw': {}}