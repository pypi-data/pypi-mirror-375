import json
import re
from typing import Optional

import httpx
from pydantic import TypeAdapter

from pesapal_client.exceptions import PesapalException
from pesapal_client.utils import deep_json_parse, is_jwt_expired

from .schemas import (
    GetPaymentOrderStatusResponse,
    GetRegisteredIPNsResponse,
    GetSubscriptionStatusResponse,
    InitiatePaymentOrderRequest,
    InitiatePaymentOrderResponse,
    InitiateSubscriptionRequest,
    IPNRegistrationRequest,
    IPNRegistrationResponse,
    RefundRequest,
    RefundResponse,
)


class _IPNAPI:
    def __init__(self, client: httpx.Client):
        self._client = client

    def register_ipn(self, ipn_request_data: IPNRegistrationRequest) -> IPNRegistrationResponse:
        endpoint = "/URLSetup/RegisterIPN"
        response = self._client.post(endpoint, json=ipn_request_data.model_dump(mode="json"))
        data = response.json()
        # Fix the typo in the response key, pesapal returns "ipn_status_decription" instead of "ipn_status_description"
        data["ipn_status_description"] = data["ipn_status_decription"]
        return IPNRegistrationResponse.model_validate(data)

    def get_registered_ipns(self) -> list[GetRegisteredIPNsResponse]:
        endpoint = "/URLSetup/GetIpnList"
        response = self._client.get(endpoint)
        ipn_list_adapter = TypeAdapter(list[GetRegisteredIPNsResponse])
        return ipn_list_adapter.validate_python(response.json())


class _OneTimePaymentAPI:
    def __init__(self, client: httpx.Client):
        self._client = client

    def initiate_payment_order(
        self, payment_order_request: InitiatePaymentOrderRequest
    ) -> InitiatePaymentOrderResponse:
        endpoint = "/Transactions/SubmitOrderRequest"
        response = self._client.post(endpoint, json=payment_order_request.model_dump(mode="json"))
        return InitiatePaymentOrderResponse.model_validate(response.json())

    def get_payment_order_status(self, payment_order_tracking_id: str) -> GetPaymentOrderStatusResponse:
        endpoint = "/Transactions/GetTransactionStatus"
        response = self._client.get(endpoint, params={"orderTrackingId": payment_order_tracking_id})
        return GetPaymentOrderStatusResponse.model_validate(response.json())

    def cancel_payment(self, payment_order_tracking_id: str) -> None:
        raise NotImplementedError

    def initiate_refund(self, refund: RefundRequest) -> RefundResponse:
        endpoint = "/Transactions/RefundRequest"
        response = self._client.post(endpoint, data=refund.model_dump())
        print("=" * 100)
        print(response.json())
        return RefundResponse.model_validate(response.json())


class _SubscriptionAPI:
    def __init__(self, client: httpx.Client):
        self._client = client

    def initiate_subscription(self, subscription_request: InitiateSubscriptionRequest) -> InitiatePaymentOrderResponse:
        endpoint = "/Transactions/SubmitOrderRequest"
        response = self._client.post(endpoint, data=subscription_request.model_dump())
        return InitiatePaymentOrderResponse.model_validate(response.json())

    def get_subscription_status(self, subscription_tracking_id: str) -> GetSubscriptionStatusResponse:
        endpoint = "/Transactions/GetTransactionStatus"
        response = self._client.get(endpoint, params={"orderTrackingId": subscription_tracking_id})
        return GetSubscriptionStatusResponse.model_validate(response.json())


class PesapalClientV3:
    SANDBOX_BASE_URL = "https://cybqa.pesapal.com/pesapalv3/api"
    PRODUCTION_BASE_URL = "https://pay.pesapal.com/v3/api"

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        *,
        base_url: Optional[str] = None,
        is_sandbox: bool = True,
    ):
        if base_url is None:
            base_url = self.SANDBOX_BASE_URL if is_sandbox else self.PRODUCTION_BASE_URL
        self._base_url = base_url
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._auth_token = None
        self._auth_token_expiry = None
        self._client = httpx.Client(
            base_url=self._base_url,
            event_hooks={
                "request": [self._ensure_valid_auth_token],
                "response": [self._raise_on_pesapal_errors],
            },
        )
        self.ipn = _IPNAPI(self._client)
        self.one_time_payment = _OneTimePaymentAPI(self._client)
        self.subscription = _SubscriptionAPI(self._client)

    def _raise_on_pesapal_errors(self, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
            response_data = deep_json_parse(response.read().decode("utf-8"))
            # Sometimes the API returns 200 OK but with an error message(+ the actual status) in the body
            status_code = (
                str(response_data.get("status")) if response_data and isinstance(response_data, dict) else "200"
            )
            if status_code.startswith("4") or status_code.startswith("5"):
                error_data = self._parse_error_response(response)
                if error_data:
                    raise PesapalException(
                        typ=str(error_data.get("error_type", "unknown")),
                        code=str(error_data.get("code", "unknown")),
                        message=str(error_data.get("message", "An error occurred")),
                    )
        except httpx.HTTPStatusError as exc:
            error_data = self._parse_error_response(response)
            if error_data:
                raise PesapalException(
                    typ=str(error_data.get("error_type", "unknown")),
                    code=str(error_data.get("code", "unknown")),
                    message=str(error_data.get("message", "An error occurred")),
                ) from exc

    def _parse_error_response(self, response: httpx.Response) -> Optional[dict]:
        """Parse error response from Pesapal API."""
        # I have seen errors returned in different formats, so we try to handle them gracefully
        # 1. {"error": {"code": "...", "message": "...", "error_type": "..."}}
        # 2. {"message": {"error": {"code": "...", "message": "...", "error_type": "..."}}}
        try:
            data = deep_json_parse(response.read().decode("utf-8"))
            if "error" in data:
                return data["error"]
            elif "message" in data and isinstance(data["message"], dict) and "error" in data["message"]:
                return data["message"]["error"]
            else:
                return None
        except json.JSONDecodeError:
            return None

    def _get_auth_token(self) -> str:
        endpoint = "/Auth/RequestToken"
        payload = {
            "consumer_key": self._consumer_key,
            "consumer_secret": self._consumer_secret,
        }
        response = self._client.post(endpoint, json=payload)
        data = response.json()
        self._auth_token = data["token"]
        self._auth_token_expiry = data["expiryDate"]
        return self._auth_token

    def _is_token_expired(self) -> bool:
        return not self._auth_token or is_jwt_expired(self._auth_token)

    def _ensure_valid_auth_token(self, request: httpx.Request) -> None:
        if re.search(r"/Auth/RequestToken/?$", request.url.path):
            return
        is_authorization_header_present = "Authorization" in request.headers
        if is_authorization_header_present:
            current_token = request.headers["Authorization"].replace("Bearer ", "")
            if is_jwt_expired(current_token):
                token = self._get_auth_token()
                request.headers["Authorization"] = f"Bearer {token}"
        else:
            token = self._get_auth_token()
            request.headers["Authorization"] = f"Bearer {token}"

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "PesapalClientV3":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        self.close()
