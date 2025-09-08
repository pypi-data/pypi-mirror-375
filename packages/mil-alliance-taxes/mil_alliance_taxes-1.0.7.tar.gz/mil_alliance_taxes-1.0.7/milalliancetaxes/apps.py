from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from . import __version__

class MilalliancetaxesConfig(AppConfig):
    name = "milalliancetaxes"
    label = "milalliancetaxes"
    verbose_name = f"MIL Alliance Taxes v{__version__}"

    def ready(self):
        import milalliancetaxes.signals

        if not getattr(settings, 'MILALLIANCETAXES_ALLIANCE_ID', None):
            raise ImproperlyConfigured("MILALLIANCETAXES_ALLIANCE_ID setting is required and cannot be empty.")
        
        if not getattr(settings, 'MILALLIANCETAXES_TAX_RATE', None):
            raise ImproperlyConfigured("MILALLIANCETAXES_TAX_RATE setting is required and cannot be empty.")