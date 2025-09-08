from celery import shared_task, group
from .models.corp_ceo import CorpCeo
from .models.corporation import Corporation
from .models.tax_ledger import TaxLedger
from .app_settings import (
    MILALLIANCETAXES_ALLIANCE_ID,
    MILALLIANCETAXES_TAX_RATE
)

from esi.models import Token

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

TASK_DEFAULT_KWARGS = {"time_limit": 3600, "max_retries": 3}

@shared_task(**{**TASK_DEFAULT_KWARGS, **{"bind": True}})
def update_all_taxes(self):
    Corporation.objects.update(is_updated=False)

    scopes = CorpCeo.get_esi_scopes()

    ceo_characters = [ceo.eve_character for ceo in CorpCeo.objects.all()]

    tokens_for_corporation = {}
    for character in ceo_characters:
        try:
            token = Token.get_token(
                character_id=character.character_id,
                scopes=scopes
            )
        except:
            logger.info(f"No token available for {character.character_name}")

        if token and token.valid_access_token():
            tokens_for_corporation[character.corporation_id] = token

    corp_taxes_update_tasks = list()
    for corporation_id, token in tokens_for_corporation.items():
        task_signature = update_one_corp_taxes.si(corporation_id, token.id)
        corp_taxes_update_tasks.append(task_signature)

    group(corp_taxes_update_tasks).delay()

    return

@shared_task(**{**TASK_DEFAULT_KWARGS, **{"bind": True}})
def update_one_corp_taxes(self, corporation_id: int, token_id: int):
    token = Token.objects.get(id=token_id)
    logger.info(f"Valid token for corp {corporation_id} is from the character {token.character_name}")

    corporation = Corporation.objects.filter(corporation_id=corporation_id).first()

    corporation_ledger = CorpCeo.retrieve_corp_ledger(token=token)
    corporation_member_range = corporation.get_member_from_alliance_date_range()

    TaxLedger.import_from_corp_ledger(
        corporation_ledger= corporation_ledger,
        corporation_id=corporation_id,
        alliance_tax_rate=MILALLIANCETAXES_TAX_RATE,
        earliest_accepted_date=corporation_member_range['start'],
        latest_accepted_date=corporation_member_range['end'],
    )
    
    Corporation.objects.filter(corporation_id=corporation_id).update(is_updated=True)
    logger.info(f"Ledger for the corporation {corporation_id} has been updated")

@shared_task(**{**TASK_DEFAULT_KWARGS, **{"bind": True}})
def update_alliance_membership(self):
    from .providers import esi

    alliance_members = []

    for alliance_id in MILALLIANCETAXES_ALLIANCE_ID:
        alliance_members.extend(esi.client.Alliance.get_alliances_alliance_id_corporations(
                alliance_id=alliance_id
            ).results()
        )
    
    for corporation_id in alliance_members:
        already_exists = Corporation.objects.filter(corporation_id=corporation_id).exists()
        if not already_exists:
            logger.info(f"Unknown corp ID {corporation_id} -> Creating it")
            Corporation.create_missing_corporation(corporation_id)
        else:
            logger.info(f"The corp ID {corporation_id} is already known")

    return