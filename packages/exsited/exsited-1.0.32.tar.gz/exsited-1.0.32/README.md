# Exsited Python SDK

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![PyPI Version](https://img.shields.io/badge/pypi-v1.0.31-green.svg)](https://pypi.org/project/exsited/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

The **Exsited Python SDK** provides a comprehensive, easy-to-use library for integrating with the Exsited platform. Whether you're building custom integrations, onsite solutions, or leveraging the full API suite, this SDK offers a streamlined approach to interact with all Exsited services.

## 🚀 What is Exsited?

Exsited is a powerful business management platform that provides:
- **Account Management**: Complete customer lifecycle management
- **Order Processing**: End-to-end order management and fulfillment  
- **Billing & Invoicing**: Automated billing with flexible pricing models
- **Payment Processing**: Integrated payment gateway solutions
- **Usage Tracking**: Metered billing and usage analytics
- **Custom Objects**: Flexible data modeling for your business needs
- **Portal Management**: Customer self-service portals

---

## 📋 Table of Contents

- [🔧 Requirements](#-requirements)
- [⚡ Installation](#-installation)
  - [PyPI Installation](#pypi-installation)
  - [Development Installation](#development-installation)
- [🔑 Authentication & Configuration](#-authentication--configuration)
- [🏁 Quick Start](#-quick-start)
- [📚 Available Modules](#-available-modules)
- [💡 Usage Examples](#-usage-examples)
- [📖 Documentation](#-documentation)
- [🆘 Support](#-support)

---

## 🔧 Requirements

- **Python 3.12+** (Recommended: Python 3.12 or later)
- **Dependencies**: `requests`, `setuptools`, `peewee`, `mysql-connector-python`, `portalocker`

---

## ⚡ Installation

### PyPI Installation

Install the Exsited SDK directly from PyPI:

```bash
pip install exsited
```

### Development Installation

For development or to access the latest features:

```bash
# Clone the repository
git clone https://github.com/exsited/exsited-python.git
cd exsited-python

# Create and activate virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install setuptools

# Install in development mode
pip install -e .

# Optional: Install additional dependencies for usage tracking
pip install peewee mysql-connector-python
```

---

## 🔑 Authentication & Configuration

### Getting Credentials

To use the Exsited SDK, you'll need:
- **Client ID**
- **Client Secret**  
- **Redirect URI**
- **Exsited Server URL**

Contact your Exsited representative to obtain these credentials.

### Configuration Setup

Create a configuration file or set up your credentials:

```python
from exsited.exsited.auth.dto.token_dto import RequestTokenDTO

def get_request_token_dto():
    return RequestTokenDTO(
        grantType="client_credentials",
        clientId="[YOUR_CLIENT_ID]",
        clientSecret="[YOUR_CLIENT_SECRET]", 
        redirectUri="[YOUR_REDIRECT_URI]",
        exsitedUrl="[YOUR_EXSITED_SERVER_URL]"
    )
```

### Credentials Reference

| Parameter | Description | Example |
|-----------|-------------|---------|
| `clientId` | Your unique client identifier | `"your-client-id-here"` |
| `clientSecret` | Your client secret key | `"your-secret-key-here"` |
| `redirectUri` | Authorized redirect URL | `"https://your-app.com/callback"` |
| `exsitedUrl` | Exsited server endpoint | `"https://api.exsited.com"` |

---

## 🏁 Quick Start

### Basic Usage

```python
from exsited.exsited.exsited_sdk import ExsitedSDK
from exsited.http.file_token_manager import FileTokenManager
from exsited.common.ab_exception import ABException

# Initialize token manager
token_file_path = "shared_token.json"
file_token_mgr = FileTokenManager(token_file_path)

# Initialize SDK
exsited_sdk = ExsitedSDK().init_sdk(
    request_token_dto=get_request_token_dto(),
    file_token_mgr=file_token_mgr
)

# Example: Create an account
try:
    from exsited.exsited.account.dto.account_dto import AccountCreateDTO, AccountDataDTO
    
    request_data = AccountCreateDTO(
        account=AccountDataDTO(
            name="John Doe",
            emailAddress="john.doe@example.com"
        )
    )
    
    response = exsited_sdk.account.create(request_data=request_data)
    print(f"Account created: {response.account.id}")
    
except ABException as e:
    print(f"Error: {e}")
    print(f"Details: {e.get_errors()}")
```

### Alternative Initialization

```python
# Direct initialization with credentials
exsited_sdk = ExsitedSDK(
    exsited_url="https://api.exsited.com",
    grant_type="client_credentials",
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="https://your-app.com/callback"
)
```

---

## 📚 Available Modules

The Exsited SDK provides comprehensive modules for all platform features:

### Core Business Modules
| Module | Description | Key Features |
|--------|-------------|--------------|
| **Account** | Customer management | Create, update, delete accounts; manage payment methods |
| **Order** | Order processing | Create orders, manage order lines, cancel orders |
| **Invoice** | Billing management | Generate invoices, track payments |
| **Payment** | Payment processing | Process payments, manage payment methods |

### Advanced Modules
| Module | Description | Key Features |
|--------|-------------|--------------|
| **Custom Objects** | Flexible data modeling | Create custom business objects |
| **Custom Attributes** | Dynamic field management | Add custom fields to entities |
| **Custom Components** | Component management | Manage custom UI components |
| **External Database** | External data integration | Connect with external databases |

### Business Operations
| Module | Description | Key Features |
|--------|-------------|--------------|
| **Purchase Order** | Procurement management | Manage supplier orders |
| **Purchase Invoice** | Vendor billing | Handle supplier invoices |
| **Purchase Payments** | Vendor payments | Process supplier payments |
| **Return Merchandise** | Returns processing | Handle product returns |

### Additional Services
| Module | Description | Key Features |
|--------|-------------|--------------|
| **Gift Certificates** | Gift card management | Issue and redeem gift certificates |
| **Credit Note** | Credit management | Issue credits and refunds |
| **Refund** | Refund processing | Process customer refunds |
| **Express** | Quick operations | Streamlined workflows |
| **Notes** | Note management | Attach notes to entities |
| **Portal** | Customer portals | Manage customer self-service |
| **Setting** | Configuration management | System and user settings |

---

## 💡 Usage Examples

### Account Management

```python
# Create an account
request_data = AccountCreateDTO(
    account=AccountDataDTO(
        name="ABC Company",
        emailAddress="contact@abc-company.com",
        phoneNumber="+1-555-0123"
    )
)
account_response = exsited_sdk.account.create(request_data=request_data)

# Get account details
account_details = exsited_sdk.account.details(id="ACCT-001")

# List accounts with pagination
accounts = exsited_sdk.account.list(limit=50, offset=0)
```

### Order Processing

```python
# Create an order
from exsited.exsited.order.dto.order_dto import OrderCreateDTO, OrderDataDTO

order_data = OrderCreateDTO(
    order=OrderDataDTO(accountId="ACCT-001")
        .add_line(item_id="ITEM-001", quantity="2")
        .add_line(item_id="ITEM-002", quantity="1")
)

order_response = exsited_sdk.order.create(request_data=order_data)
print(f"Order created: {order_response.order.id}")

# Get order details
order_details = exsited_sdk.order.details(id="ORDER-001")

# Cancel an order
cancel_response = exsited_sdk.order.cancel(
    id="ORDER-001",
    effective_date="2024-12-31"
)
```

### Usage Tracking (Metered Billing)

```python
# Add usage data for metered items
from exsited.exsited.order.dto.usage_dto import UsageCreateDTO

usage_data = UsageCreateDTO(
    chargeItemUuid="charge-uuid-here",
    chargingPeriod="2024-01",
    quantity=100,
    startTime="2024-01-01T00:00:00Z",
    endTime="2024-01-31T23:59:59Z",
    type="usage"
)

usage_response = exsited_sdk.order.usage_add(request_data=usage_data)
```

### Custom Objects

```python
# Work with custom objects
from exsited.exsited.custom_objects.dto.custom_objects_dto import CustomObjectsCreateDTO

custom_obj = CustomObjectsCreateDTO(
    name="Product Specification",
    type="specification",
    properties={
        "dimensions": "10x20x30",
        "weight": "5kg",
        "color": "blue"
    }
)

custom_response = exsited_sdk.custom_objects.create(request_data=custom_obj)
```

### Payment Processing

```python
# Add a payment method
from exsited.exsited.payment.dto.payment_dto import CardPaymentCreateDTO

payment_method = CardPaymentCreateDTO(
    processorType="stripe",
    cardType="visa",
    cardNumber="4111111111111111",
    expiryMonth="12",
    expiryYear="2025",
    cvv="123"
)

payment_response = exsited_sdk.payment.add_card_method(request_data=payment_method)
```

## 📖 Documentation

### Official Documentation
- **SDK Guide**: [https://developer.exsited.com/exsited-sdk-introduction](https://developer.exsited.com/exsited-sdk-introduction)

### Error Handling

All SDK methods use the `ABException` class for error handling:

```python
from exsited.common.ab_exception import ABException

try:
    # SDK operation
    response = exsited_sdk.account.create(request_data)
except ABException as e:
    # Handle specific errors
    errors = e.get_errors()  # List of error messages
    raw_response = e.raw_response  # Raw API response
    
    # Log error details
    print(f"Operation failed: {e}")
    for error in errors:
        print(f"- {error}")
```

## 🆘 Support

### Getting Help

1. **Documentation**: Check the [official documentation](https://developer.exsited.com)
2. **GitHub Issues**: Report bugs or request features on our [GitHub repository](https://github.com/exsited/exsited-python/issues)
3. **Contact Support**: Reach out to your Exsited representative
4. **Email**: Technical support at [support@exsited.com](mailto:support@exsited.com)

### Common Issues

| Issue | Solution |
|-------|----------|
| Authentication errors | Verify your credentials and server URL |
| Import errors | Ensure you're using the latest import paths |
| Token expiration | The SDK handles token refresh automatically |
| Connection timeouts | Check your network connection and server status |

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **PyPI**: [https://pypi.org/project/exsited/](https://pypi.org/project/exsited/)
- **GitHub**: [https://github.com/exsited/exsited-python](https://github.com/exsited/exsited-python)
- **Documentation**: [https://developer.exsited.com](https://developer.exsited.com)
- **Website**: [https://exsited.com](https://exsited.com)

---

*Built with ❤️ by the Exsited team*