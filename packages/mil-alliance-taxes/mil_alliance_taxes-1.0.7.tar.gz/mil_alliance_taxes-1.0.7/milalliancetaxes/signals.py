from django.dispatch import receiver
from django.db.models.signals import post_save
from .models.corp_ceo import CorpCeo

from milalliancetaxes.tasks import update_all_taxes

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

@receiver(post_save, sender=CorpCeo)
def on_ceo_created(sender, instance, created, **kwargs):
    logger.info(f"New CEO added: {instance.eve_character.character_name} - Refreshing all data")
    if created:
        update_all_taxes.delay()