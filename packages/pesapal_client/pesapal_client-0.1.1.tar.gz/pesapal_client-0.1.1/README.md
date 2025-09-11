# pesapal-client

[![Release](https://img.shields.io/github/v/release/kiraboibrahim/pesapal-client)](https://img.shields.io/github/v/release/kiraboibrahim/pesapal-client)
[![Build status](https://img.shields.io/github/actions/workflow/status/kiraboibrahim/pesapal-client/main.yml?branch=main)](https://github.com/kiraboibrahim/pesapal-client/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/kiraboibrahim/pesapal-client)](https://img.shields.io/github/commit-activity/m/kiraboibrahim/pesapal-client)
[![License](https://img.shields.io/github/license/kiraboibrahim/pesapal-client)](https://img.shields.io/github/license/kiraboibrahim/pesapal-client)

A Typed Python client for the Pesapal API with sync/async support, order submission, IPN management, and optional CLI tools.

---

## Features

- **Typed models** for requests and responses using [Pydantic](https://docs.pydantic.dev/)
- **Sync and async** API support
- **Order submission** and payment status tracking
- **IPN (Instant Payment Notification) management**
- **Subscription management**
- **Automatic authentication and token refresh**
- **Custom exceptions for error handling**
- **Utility functions for JWT and JSON parsing**
- **Optional CLI tools for quick integration**

---

## Installation

```bash
pip install pesapal-client
```

---

## Quick Start

```python
from pesapal_client.client import PesapalClientV3
from pesapal_client.v3.schemas import InitiatePaymentOrderRequest

client = PesapalClientV3(
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret",
    is_sandbox=True,
)

payment_request = InitiatePaymentOrderRequest(
    amount="1000",
    currency="KES",
    description="Test payment",
    # ...other required fields...
)

response = client.one_time_payment.initiate_payment_order(payment_request)
print(response.redirect_url)
```

---

## Documentation

- [Modules Reference](modules.md)
- [API Usage Examples](usage.md)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
