from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class KycConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kyc'
    verbose_name = _('KYC & Verification')
