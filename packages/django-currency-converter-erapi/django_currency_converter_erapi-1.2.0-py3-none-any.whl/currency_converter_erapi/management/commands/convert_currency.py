"""
Django management command for converting currencies.

Usage:
    python manage.py convert_currency <amount> <from_currency> <to_currency>
    
Example:
    python manage.py convert_currency 100 USD EUR
"""
from django.core.management.base import BaseCommand, CommandError
from currency_converter_erapi.converter import CurrencyConverter
from currency_converter_erapi.exceptions import (
    CurrencyConverterError,
    InvalidCurrencyError,
    APIError,
    NetworkError,
    RateLimitError
)


class Command(BaseCommand):
    help = 'Convert currency from one type to another'

    def add_arguments(self, parser):
        parser.add_argument(
            'amount',
            type=float,
            help='Amount to convert'
        )
        parser.add_argument(
            'from_currency',
            type=str,
            help='Source currency code (e.g., USD, EUR, GBP)'
        )
        parser.add_argument(
            'to_currency',
            type=str,
            help='Target currency code (e.g., USD, EUR, GBP)'
        )
        parser.add_argument(
            '--rate-only',
            action='store_true',
            help='Show only the exchange rate without converting'
        )
        parser.add_argument(
            '--list-currencies',
            action='store_true',
            help='List all supported currencies'
        )

    def handle(self, *args, **options):
        converter = CurrencyConverter()
        
        # Handle list currencies option
        if options['list_currencies']:
            self.list_supported_currencies(converter)
            return
        
        amount = options['amount']
        from_currency = options['from_currency'].upper()
        to_currency = options['to_currency'].upper()
        rate_only = options['rate_only']
        
        try:
            if rate_only:
                # Show only exchange rate
                rate = converter.get_exchange_rate(from_currency, to_currency)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Exchange rate: 1 {from_currency} = {rate} {to_currency}"
                    )
                )
            else:
                # Perform conversion
                if amount <= 0:
                    raise CommandError("Amount must be greater than 0")
                
                result = converter.convert(amount, from_currency, to_currency)
                
                # Display result
                amount_display = int(amount) if amount == int(amount) else amount
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{amount_display} {from_currency} = {result} {to_currency}"
                    )
                )
                
                # Also show the exchange rate used
                rate = converter.get_exchange_rate(from_currency, to_currency)
                self.stdout.write(
                    self.style.HTTP_INFO(
                        f"Exchange rate: 1 {from_currency} = {rate} {to_currency}"
                    )
                )
                
        except InvalidCurrencyError as e:
            raise CommandError(f"Invalid currency: {e}")
        except RateLimitError:
            raise CommandError(
                "API rate limit exceeded. Please try again later."
            )
        except NetworkError as e:
            raise CommandError(f"Network error: {e}")
        except APIError as e:
            raise CommandError(f"API error: {e}")
        except CurrencyConverterError as e:
            raise CommandError(f"Conversion error: {e}")
        except Exception as e:
            raise CommandError(f"Unexpected error: {e}")

    def list_supported_currencies(self, converter):
        """List all supported currencies."""
        currencies = sorted(converter.get_supported_currencies())
        
        self.stdout.write(
            self.style.SUCCESS("Supported currencies:")
        )
        
        # Display currencies in a nice format (4 columns)
        for i in range(0, len(currencies), 4):
            row = currencies[i:i+4]
            self.stdout.write("  " + "  ".join(f"{curr:<4}" for curr in row))
        
        self.stdout.write(f"\nTotal: {len(currencies)} currencies supported")
