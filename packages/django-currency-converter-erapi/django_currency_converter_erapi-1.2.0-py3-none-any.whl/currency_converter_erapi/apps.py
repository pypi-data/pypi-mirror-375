from django.apps import AppConfig


class CurrencyConverterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'currency_converter_erapi'
    verbose_name = 'Currency Converter'

    def ready(self):
        """
        Initialize the application when Django starts.
        """
        pass
