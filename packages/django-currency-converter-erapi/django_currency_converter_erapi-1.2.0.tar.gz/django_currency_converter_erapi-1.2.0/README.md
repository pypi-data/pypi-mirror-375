# Django Currency Converter

A Django application for converting currencies using real-time exchange rates from ExchangeRate-API.

## Features

- Real-time currency conversion using ExchangeRate-API
- Built-in caching for improved performance
- Custom Django management commands
- Comprehensive error handling
- Support for 24+ major currencies
- Production-ready with proper logging
- Type hints and documentation

## Installation

1. Install the package:
```bash
pip install django-currency-converter-erapi
```

2. For .env file support (recommended), also install:
```bash
pip install django-currency-converter-erapi[dotenv]
```

3. Add `currency_converter` to your Django project's `INSTALLED_APPS` in `settings.py`:
```python
INSTALLED_APPS = [
    # ... other apps
    'currency_converter_erapi',
]
```

## Configuration

### API Key Configuration (Multiple Options)

The currency converter supports multiple ways to configure your API key for premium access:

#### Option 1: .env File (Recommended)
Create a `.env` file in your Django project root:
```bash
# .env file
CURRENCY_API_KEY=your_exchangerate_api_key_here
# or alternatively:
EXCHANGERATE_API_KEY=your_exchangerate_api_key_here
```

#### Option 2: Django Settings
Add to your Django `settings.py`:
```python
CURRENCY_API_KEY = 'your_api_key_here'
```

#### Option 3: Environment Variables
Set environment variables directly:
```bash
export CURRENCY_API_KEY=your_api_key_here
# or
export EXCHANGERATE_API_KEY=your_api_key_here
```

### Priority Order
The package checks for API keys in this order:
1. Django settings (`CURRENCY_API_KEY`)
2. Environment variable `CURRENCY_API_KEY`
3. Environment variable `EXCHANGERATE_API_KEY`
4. No API key (uses free tier)

### Additional Settings

Add these optional settings to your Django `settings.py`:

```python
# Currency Converter Settings (Optional)
CURRENCY_CACHE_TIMEOUT = 3600  # Cache exchange rates for 1 hour (default: 3600)

# Ensure you have caching configured
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

## Usage

### Using the Management Command

Convert currency using the management command:

```bash
# Basic conversion
python manage.py convert_currency 100 USD EUR

# Show only exchange rate
python manage.py convert_currency 100 USD EUR --rate-only

# List all supported currencies
python manage.py convert_currency 0 USD EUR --list-currencies
```

### Using the Converter Class in Your Code

```python
from currency_converter_erapi.converter import CurrencyConverter
from currency_converter_erapi.exceptions import InvalidCurrencyError, APIError

try:
    converter = CurrencyConverter()

    # Convert 100 USD to EUR
    result = converter.convert(100, 'USD', 'EUR')
    print(f"100 USD = {result} EUR")

    # Get exchange rate only
    rate = converter.get_exchange_rate('USD', 'EUR')
    print(f"1 USD = {rate} EUR")

    # Get supported currencies
    currencies = converter.get_supported_currencies()
    print(f"Supported currencies: {currencies}")

except InvalidCurrencyError as e:
    print(f"Invalid currency: {e}")
except APIError as e:
    print(f"API error: {e}")
```

### Supported Currencies

The application supports 24 major currencies:
- USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY
- SEK, NZD, MXN, SGD, HKD, NOK, TRY, RUB
- INR, BRL, ZAR, KRW, DKK, PLN, TWD, THB

## Error Handling

The package includes comprehensive error handling:

- `InvalidCurrencyError`: Raised for unsupported currency codes
- `APIError`: Raised when the exchange rate API fails
- `RateLimitError`: Raised when API rate limits are exceeded
- `NetworkError`: Raised for network connectivity issues
- `CacheError`: Raised for caching-related errors

## API Rate Limits

The free ExchangeRate-API has the following limits:
- 1,500 requests per month
- Cached responses help minimize API calls

For higher limits, consider upgrading to a paid plan and setting `CURRENCY_API_KEY`.

## Requirements

- Python 3.8+
- Django 3.2+
- requests 2.25.0+

## Development

### Running Tests

```bash
python -m pytest
```

### Code Quality

The project follows PEP 8 standards and includes:
- Type hints
- Comprehensive docstrings
- Error handling
- Logging support

## Troubleshooting

### Common Issues

1. **API Rate Limit Exceeded**
   - Solution: Wait for rate limit reset or upgrade to paid plan

2. **Network Timeout**
   - Solution: Check internet connection and firewall settings

3. **Cache Issues**
   - Solution: Ensure Django caching is properly configured

4. **Invalid Currency Code**
   - Solution: Use 3-letter ISO currency codes (e.g., USD, EUR)

### Logging

Enable logging to see detailed error information:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'currency_converter_erapi': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above

## Changelog

### Version 1.0.0
- Initial release
- Support for 24 major currencies
- Caching support
- Management commands
- Comprehensive error handling
