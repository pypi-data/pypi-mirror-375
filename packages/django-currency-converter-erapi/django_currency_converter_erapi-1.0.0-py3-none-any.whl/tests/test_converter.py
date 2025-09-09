"""
Tests for the currency converter functionality
"""
import pytest
from decimal import Decimal
from unittest.mock import patch, Mock
from django.test import TestCase
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO

from currency_converter_erapi.converter import CurrencyConverter
from currency_converter_erapi.exceptions import (
    InvalidCurrencyError,
    APIError,
    RateLimitError,
    NetworkError,
)


class CurrencyConverterTestCase(TestCase):
    """Test cases for CurrencyConverter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.converter = CurrencyConverter()
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests"""
        cache.clear()
    
    def test_validate_currency_valid_codes(self):
        """Test validation of valid currency codes"""
        valid_currencies = ['USD', 'EUR', 'GBP', 'JPY']
        for currency in valid_currencies:
            result = self.converter.validate_currency(currency)
            self.assertEqual(result, currency.upper())
    
    def test_validate_currency_case_insensitive(self):
        """Test currency validation is case insensitive"""
        result = self.converter.validate_currency('usd')
        self.assertEqual(result, 'USD')
        
        result = self.converter.validate_currency('Eur')
        self.assertEqual(result, 'EUR')
    
    def test_validate_currency_with_whitespace(self):
        """Test currency validation handles whitespace"""
        result = self.converter.validate_currency('  USD  ')
        self.assertEqual(result, 'USD')
    
    def test_validate_currency_invalid_codes(self):
        """Test validation of invalid currency codes"""
        invalid_currencies = ['XXX', 'INVALID', '123', '']
        for currency in invalid_currencies:
            with self.assertRaises(InvalidCurrencyError):
                self.converter.validate_currency(currency)
    
    def test_validate_currency_none_input(self):
        """Test validation with None input"""
        with self.assertRaises(InvalidCurrencyError):
            self.converter.validate_currency(None)
    
    def test_validate_currency_non_string_input(self):
        """Test validation with non-string input"""
        with self.assertRaises(InvalidCurrencyError):
            self.converter.validate_currency(123)
    
    def test_get_cache_key(self):
        """Test cache key generation"""
        key = self.converter.get_cache_key('USD')
        self.assertEqual(key, 'exchange_rates_usd')
        
        key = self.converter.get_cache_key('EUR')
        self.assertEqual(key, 'exchange_rates_eur')
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_get_exchange_rates_success(self, mock_get):
        """Test successful API call for exchange rates"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'base': 'USD',
            'rates': {
                'EUR': 0.85,
                'GBP': 0.75,
                'JPY': 110.0
            }
        }
        mock_get.return_value = mock_response
        
        rates = self.converter.get_exchange_rates('USD')
        
        self.assertEqual(rates['base'], 'USD')
        self.assertIn('EUR', rates['rates'])
        self.assertEqual(rates['rates']['EUR'], 0.85)
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_get_exchange_rates_caching(self, mock_get):
        """Test that exchange rates are cached properly"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'base': 'USD',
            'rates': {'EUR': 0.85}
        }
        mock_get.return_value = mock_response
        
        # First call should hit the API
        rates1 = self.converter.get_exchange_rates('USD')
        self.assertEqual(mock_get.call_count, 1)
        
        # Second call should use cache
        rates2 = self.converter.get_exchange_rates('USD')
        self.assertEqual(mock_get.call_count, 1)  # No additional API call
        
        self.assertEqual(rates1, rates2)
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_get_exchange_rates_rate_limit_error(self, mock_get):
        """Test handling of rate limit errors"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with self.assertRaises(RateLimitError):
            self.converter.get_exchange_rates('USD')
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_get_exchange_rates_api_error(self, mock_get):
        """Test handling of API errors"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with self.assertRaises(APIError):
            self.converter.get_exchange_rates('USD')
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_get_exchange_rates_network_error(self, mock_get):
        """Test handling of network errors"""
        mock_get.side_effect = Exception("Network error")
        
        with self.assertRaises(NetworkError):
            self.converter.get_exchange_rates('USD')
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_get_exchange_rates_invalid_json(self, mock_get):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with self.assertRaises(APIError):
            self.converter.get_exchange_rates('USD')
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_convert_same_currency(self, mock_get):
        """Test conversion between same currencies"""
        result = self.converter.convert(100, 'USD', 'USD')
        self.assertEqual(result, Decimal('100.00'))
        
        # Should not make API call for same currency
        mock_get.assert_not_called()
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_convert_different_currencies(self, mock_get):
        """Test conversion between different currencies"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'base': 'USD',
            'rates': {'EUR': 0.85}
        }
        mock_get.return_value = mock_response
        
        result = self.converter.convert(100, 'USD', 'EUR')
        self.assertEqual(result, Decimal('85.00'))
    
    def test_convert_invalid_amount(self):
        """Test conversion with invalid amounts"""
        with self.assertRaises(ValueError):
            self.converter.convert(-10, 'USD', 'EUR')
        
        with self.assertRaises(ValueError):
            self.converter.convert('invalid', 'USD', 'EUR')
    
    def test_convert_invalid_currencies(self):
        """Test conversion with invalid currency codes"""
        with self.assertRaises(InvalidCurrencyError):
            self.converter.convert(100, 'INVALID', 'EUR')
        
        with self.assertRaises(InvalidCurrencyError):
            self.converter.convert(100, 'USD', 'INVALID')
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_convert_precision(self, mock_get):
        """Test conversion precision and rounding"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'base': 'USD',
            'rates': {'EUR': 0.856789}
        }
        mock_get.return_value = mock_response
        
        result = self.converter.convert(100, 'USD', 'EUR')
        self.assertEqual(result, Decimal('85.68'))  # Rounded to 2 decimal places
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_get_exchange_rate(self, mock_get):
        """Test getting exchange rate between currencies"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'base': 'USD',
            'rates': {'EUR': 0.85}
        }
        mock_get.return_value = mock_response
        
        rate = self.converter.get_exchange_rate('USD', 'EUR')
        self.assertEqual(rate, Decimal('0.85'))
    
    def test_get_exchange_rate_same_currency(self):
        """Test getting exchange rate for same currency"""
        rate = self.converter.get_exchange_rate('USD', 'USD')
        self.assertEqual(rate, Decimal('1.00'))
    
    def test_get_supported_currencies(self):
        """Test getting supported currencies"""
        currencies = self.converter.get_supported_currencies()
        self.assertIsInstance(currencies, set)
        self.assertIn('USD', currencies)
        self.assertIn('EUR', currencies)
        self.assertIn('GBP', currencies)
        self.assertTrue(len(currencies) >= 20)


class ManagementCommandTestCase(TestCase):
    """Test cases for management commands"""
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_convert_currency_command(self, mock_get):
        """Test convert_currency management command"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'base': 'USD',
            'rates': {'EUR': 0.85}
        }
        mock_get.return_value = mock_response
        
        out = StringIO()
        call_command('convert_currency', '100', 'USD', 'EUR', stdout=out)
        
        output = out.getvalue()
        self.assertIn('100 USD = 85.00 EUR', output)
        self.assertIn('Exchange rate: 1 USD = 0.85 EUR', output)
    
    @patch('currency_converter_erapi.converter.requests.get')
    def test_convert_currency_command_rate_only(self, mock_get):
        """Test convert_currency command with rate-only option"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'base': 'USD',
            'rates': {'EUR': 0.85}
        }
        mock_get.return_value = mock_response
        
        out = StringIO()
        call_command('convert_currency', '100', 'USD', 'EUR', '--rate-only', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Exchange rate: 1 USD = 0.85 EUR', output)
        self.assertNotIn('100 USD = 85.00 EUR', output)
    
    def test_convert_currency_command_list_currencies(self):
        """Test convert_currency command with list-currencies option"""
        out = StringIO()
        call_command('convert_currency', '0', 'USD', 'EUR', '--list-currencies', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Supported currencies:', output)
        self.assertIn('USD', output)
        self.assertIn('EUR', output)
    
    def test_convert_currency_command_invalid_amount(self):
        """Test convert_currency command with invalid amount"""
        with self.assertRaises(CommandError):
            call_command('convert_currency', '-100', 'USD', 'EUR')
    
    def test_convert_currency_command_invalid_currency(self):
        """Test convert_currency command with invalid currency"""
        with self.assertRaises(CommandError):
            call_command('convert_currency', '100', 'INVALID', 'EUR')
