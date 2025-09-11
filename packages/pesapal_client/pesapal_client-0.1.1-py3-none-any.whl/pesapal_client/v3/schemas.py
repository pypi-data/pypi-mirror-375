import enum
import re
from datetime import datetime
from typing import AnyStr, Literal, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    HttpUrl,
    ValidationError,
    ValidationInfo,
    field_validator,
)
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.currency_code import Currency


class IPNRegistrationRequest(BaseModel):
    url: HttpUrl
    ipn_notification_type: Literal["GET", "POST"]


class IPNRegistrationResponse(BaseModel):
    url: str
    created_date: datetime
    ipn_id: UUID
    notification_type: int
    ipn_notification_type_description: str
    ipn_status: int
    ipn_status_description: str


class GetRegisteredIPNsResponse(BaseModel):
    url: str
    created_date: datetime
    ipn_id: UUID


class BillingAddress(BaseModel):
    phone_number: Optional[str] = None
    email_address: Optional[EmailStr] = None
    country_code: Optional[CountryAlpha2] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    line_1: Optional[str] = None
    line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[int] = None
    zip_code: Optional[int] = None

    # Ensure at least one of phone or email is provided
    @field_validator("email_address", mode="after")
    @classmethod
    def email_or_phone(cls, value: AnyStr, info: ValidationInfo) -> AnyStr:
        if not value and not info.data.get("phone_number"):
            message = "Either email_address or phone_number must be provided"
            raise ValidationError(message)
        return value


class InitiatePaymentOrderRequest(BaseModel):
    id: str = Field(max_length=50)
    currency: Currency
    amount: float
    description: str = Field(max_length=100)
    callback_url: HttpUrl
    notification_id: UUID

    redirect_mode: Optional[Literal["TOP_WINDOW", "PARENT_WINDOW"]] = "TOP_WINDOW"
    cancellation_url: Optional[HttpUrl] = None
    branch: Optional[str] = None

    billing_address: BillingAddress


class InitiatePaymentOrderResponse(BaseModel):
    order_tracking_id: UUID
    merchant_reference: str
    redirect_url: str


class PaymentOrderStatusCode(enum.Enum):
    INVALID = 0
    COMPLETED = 1
    FAILED = 2
    REVERSED = 3


class GetPaymentOrderStatusResponse(BaseModel):
    payment_method: str
    amount: float
    created_date: datetime
    confirmation_code: str
    payment_status_description: str  # "INVALID", "FAILED", "COMPLETED", "REVERSED"
    description: str
    message: str
    payment_account: str
    call_back_url: str
    status_code: PaymentOrderStatusCode
    merchant_reference: str
    currency: Currency


class SubscriptionDetails(BaseModel):
    start_date: str
    end_date: str
    frequency: Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]

    @field_validator("start_date", "end_date", mode="after")
    @classmethod
    def validate_date(cls, value: str, info: ValidationInfo) -> str:
        pattern = r"\d{2}-\d{2}-\d{4}"
        if not re.match(pattern, value):
            message = f"Field: {info.field_name} should be in the format: dd-dd-yyyy"
            raise ValidationError(message)
        return value


class InitiateSubscriptionRequest(InitiatePaymentOrderRequest):
    account_number: str
    subscription_details: Optional[SubscriptionDetails]


class SubscriptionInfo(BaseModel):
    account_reference: Optional[str] = None
    first_name: str
    last_name: str
    correlation_id: int


class GetSubscriptionStatusResponse(GetPaymentOrderStatusResponse):
    subscription_transaction_info: SubscriptionInfo


class RefundRequest(BaseModel):
    confirmation_code: str
    amount: str
    username: str
    remarks: str


class RefundResponse(BaseModel):
    status: int
    message: str
