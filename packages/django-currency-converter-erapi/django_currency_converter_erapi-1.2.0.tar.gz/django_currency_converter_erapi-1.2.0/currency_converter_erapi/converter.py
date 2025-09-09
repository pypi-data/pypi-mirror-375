"""
Main business logic for currency conversion.
"""
import logging
import requests
import json
import os
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Set, Union, Optional
from django.core.cache import cache
from django.conf import settings

try:
    from dotenv import load_dotenv
    # Load .env file if it exists
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

from .exceptions import (
    InvalidCurrencyError,
    APIError,
    RateLimitError,
    NetworkError,
)

# Set up logging
logger = logging.getLogger(__name__)


class CurrencyConverter:
    """
    Main currency converter class that handles fetching exchange rates
    and performing currency conversions.
    """
    
    # Free API endpoint (you can replace with your preferred service)
    API_BASE_URL = "https://api.exchangerate-api.com/v4/latest/"
    
    # Common currency codes for validation
    VALID_CURRENCIES = {
        # Existing currencies (preserved)
        'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY',
        'SEK', 'NZD', 'MXN', 'SGD', 'HKD', 'NOK', 'TRY', 'RUB',
        'INR', 'BRL', 'ZAR', 'KRW', 'DKK', 'PLN', 'TWD', 'THB',

        # Additional comprehensive currency list
        'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AWG', 'AZN',
        'BAM', 'BBD', 'BDT', 'BGN', 'BHD', 'BIF', 'BMD', 'BND', 'BOB',
        'BSD', 'BTN', 'BWP', 'BYN', 'BZD', 'CDF', 'CLP', 'COP', 'CRC',
        'CUP', 'CVE', 'CZK', 'DJF', 'DOP', 'DZD', 'EGP', 'ERN', 'ETB',
        'FJD', 'FKP', 'FOK', 'GEL', 'GGP', 'GHS', 'GIP', 'GMD', 'GNF',
        'GTQ', 'GYD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'IMP',
        'IQD', 'IRR', 'ISK', 'JEP', 'JMD', 'JOD', 'KES', 'KGS', 'KHR',
        'KID', 'KMF', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD',
        'LSL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT', 'MOP',
        'MRU', 'MUR', 'MVR', 'MWK', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO',
        'NPR', 'OMR', 'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PYG', 'QAR',
        'RON', 'RSD', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG', 'SHP', 'SLE',
        'SOS', 'SRD', 'SSP', 'STN', 'SYP', 'SZL', 'TJS', 'TMT', 'TND',
        'TOP', 'TTD', 'TVD', 'TZS', 'UAH', 'UGX', 'UYU', 'UZS', 'VES',
        'VND', 'VUV', 'WST', 'XAF', 'XCD', 'XDR', 'XOF', 'XPF', 'YER',
        'ZMW', 'ZWL'
    }
    
    def __init__(self) -> None:
        self.cache_timeout: int = getattr(settings, 'CURRENCY_CACHE_TIMEOUT', 3600)

        # Try to get API key from multiple sources in order of preference:
        # 1. Django settings
        # 2. Environment variable (including from .env file)
        self.api_key: Optional[str] = self._get_api_key()

        if not HAS_DOTENV and not self.api_key:
            logger.info("python-dotenv not installed. Install it to support .env files: pip install python-dotenv")

        logger.info("CurrencyConverter initialized with cache timeout: %d seconds", self.cache_timeout)
        if self.api_key:
            logger.info("API key configured for premium access")
        else:
            logger.info("Using free API tier (no API key configured)")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from Django settings or environment variables.

        Priority order:
        1. Django settings.CURRENCY_API_KEY
        2. Environment variable CURRENCY_API_KEY
        3. Environment variable EXCHANGERATE_API_KEY
        4. None (use free tier)

        Returns:
            Optional[str]: API key if found, None otherwise
        """
        # First try Django settings
        api_key = getattr(settings, 'CURRENCY_API_KEY', None)
        if api_key:
            return api_key

        # Then try environment variables
        api_key = os.getenv('CURRENCY_API_KEY')
        if api_key:
            return api_key

        # Also try common alternative environment variable name
        api_key = os.getenv('EXCHANGERATE_API_KEY')
        if api_key:
            return api_key

        return None

    def validate_currency(self, currency_code: str) -> str:
        """
        Validate if the currency code is supported.
        
        Args:
            currency_code (str): Currency code to validate
            
        Returns:
            str: Validated uppercase currency code

        Raises:
            InvalidCurrencyError: If currency code is invalid
        """
        if not currency_code or not isinstance(currency_code, str):
            raise InvalidCurrencyError("Currency code must be a non-empty string")
        
        currency_code = currency_code.upper().strip()
        if currency_code not in self.VALID_CURRENCIES:
            raise InvalidCurrencyError(f"Unsupported currency code: {currency_code}")
        
        return currency_code
    
    def get_cache_key(self, base_currency: str) -> str:
        """Generate cache key for exchange rates."""
        return f"exchange_rates_{base_currency.lower()}"
    
    def get_exchange_rates(self, base_currency: str) -> Dict:
        """
        Fetch exchange rates for a base currency.
        
        Args:
            base_currency (str): Base currency code
            
        Returns:
            dict: Exchange rates data
            
        Raises:
            APIError: If API request fails
            NetworkError: If network request fails
        """
        base_currency = self.validate_currency(base_currency)
        cache_key = self.get_cache_key(base_currency)
        
        # Try to get from cache first
        try:
            cached_rates = cache.get(cache_key)
            if cached_rates:
                logger.info("Retrieved exchange rates for %s from cache", base_currency)
                return cached_rates
        except Exception as e:
            logger.warning("Cache retrieval failed: %s", str(e))

        # Fetch from API
        logger.info("Fetching exchange rates for %s from API", base_currency)
        try:
            url = f"{self.API_BASE_URL}{base_currency}"
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            try:
                response = requests.get(url, headers=headers, timeout=10)
            except Exception as e:
                # Catch any exception from the requests call
                logger.error("Network error fetching rates for %s: %s", base_currency, str(e))
                raise NetworkError(f"Network error: {str(e)}")

            if response.status_code == 429:
                logger.error("API rate limit exceeded for %s", base_currency)
                raise RateLimitError("API rate limit exceeded")
            elif response.status_code != 200:
                logger.error("API request failed with status %d for %s", response.status_code, base_currency)
                raise APIError(f"API request failed with status {response.status_code}")
            
            try:
                data = response.json()
            except (json.JSONDecodeError, ValueError) as e:
                logger.error("Invalid JSON response for %s: %s", base_currency, str(e))
                raise APIError(f"Invalid JSON response: {str(e)}")

            # Validate response structure
            if 'rates' not in data:
                logger.error("Invalid API response format for %s", base_currency)
                raise APIError("Invalid API response format")

            # Cache the results
            try:
                cache.set(cache_key, data, self.cache_timeout)
                logger.info("Cached exchange rates for %s", base_currency)
            except Exception as e:
                logger.warning("Cache storage failed: %s", str(e))

            return data
            
        except (RateLimitError, APIError, NetworkError):
            # Re-raise our custom exceptions
            raise

    def convert(self, amount: Union[int, float, Decimal], from_currency: str, to_currency: str) -> Decimal:
        """
        Convert an amount from one currency to another.
        
        Args:
            amount (Union[int, float, Decimal]): Amount to convert
            from_currency (str): Source currency code
            to_currency (str): Target currency code
            
        Returns:
            Decimal: Converted amount rounded to 2 decimal places
            
        Raises:
            ValueError: If amount is invalid
            InvalidCurrencyError: If currency codes are invalid
            APIError: If API request fails
            NetworkError: If network request fails
        """
        # Validate inputs
        if not isinstance(amount, (int, float, Decimal)) or amount < 0:
            raise ValueError("Amount must be a non-negative number")
        
        from_currency = self.validate_currency(from_currency)
        to_currency = self.validate_currency(to_currency)
        
        # Convert amount to Decimal for precision
        amount = Decimal(str(amount))
        
        logger.info("Converting %s %s to %s", amount, from_currency, to_currency)

        # If same currency, return original amount
        if from_currency == to_currency:
            result = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            logger.info("Same currency conversion: %s %s", result, from_currency)
            return result

        # Get exchange rates
        rates_data = self.get_exchange_rates(from_currency)
        rates = rates_data['rates']
        
        if to_currency not in rates:
            logger.error("Exchange rate not available for %s", to_currency)
            raise InvalidCurrencyError(f"Exchange rate not available for {to_currency}")
        
        # Perform conversion
        exchange_rate = Decimal(str(rates[to_currency]))
        converted_amount = amount * exchange_rate
        
        # Round to 2 decimal places
        result = converted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        logger.info("Conversion result: %s %s = %s %s (rate: %s)",
                   amount, from_currency, result, to_currency, exchange_rate)

        return result

    def get_supported_currencies(self) -> Set[str]:
        """
        Get list of supported currency codes.
        
        Returns:
            Set[str]: Set of supported currency codes
        """
        return self.VALID_CURRENCIES.copy()
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """
        Get the exchange rate between two currencies.
        
        Args:
            from_currency (str): Source currency code
            to_currency (str): Target currency code
            
        Returns:
            Decimal: Exchange rate

        Raises:
            InvalidCurrencyError: If currency codes are invalid
            APIError: If API request fails
            NetworkError: If network request fails
        """
        from_currency = self.validate_currency(from_currency)
        to_currency = self.validate_currency(to_currency)
        
        if from_currency == to_currency:
            return Decimal('1.00')
        
        rates_data = self.get_exchange_rates(from_currency)
        rates = rates_data['rates']
        
        if to_currency not in rates:
            raise InvalidCurrencyError(f"Exchange rate not available for {to_currency}")
        
        return Decimal(str(rates[to_currency]))
