from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import csv

from django.db import models
from allianceauth.eveonline.models import EveCharacter
from esi.models import Token

from ..providers import esi
from ..dataclasses.wallet_ledger import WalletLedger
from .corporation import Corporation

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

class CorpCeo(models.Model):
    id = models.AutoField(primary_key=True)
    eve_character = models.OneToOneField(
        EveCharacter, related_name="milalliancetaxes_corpceo", on_delete=models.CASCADE
    )
    corporation = models.ForeignKey(Corporation, on_delete=models.CASCADE)

    @classmethod
    def get_esi_scopes(cls) -> list:
        return [
            "esi-wallet.read_corporation_wallets.v1",
        ]

    def __str__(self) -> str:
        return f"{self.eve_character.character_name} (PK:{self.pk})"

    def __repr__(self) -> str:
        return f"Character(pk={self.pk}, eve_character='{self.eve_character}')"

    @classmethod
    def retrieve_character_from_token(cls, token: Token):
        return cls.objects.filter(eve_character__character_id = token.character_id).first()
    
    @classmethod
    def get_corporation_id(cls, token: Token):
        character = cls.objects.filter(eve_character__character_id = token.character_id).first()
        return character.eve_character.corporation_id

    def retrieve_corp_ledger(token: Token):
        character = CorpCeo.retrieve_character_from_token(token)

        corporation_data = esi.client.Corporation.get_corporations_corporation_id(
            corporation_id=character.corporation.corporation_id
        ).results()
        character.corporation.tax_rate = round(corporation_data["tax_rate"]*100, 2)

        logger.info(f"Tax rate for the corporation {character.corporation.corporation_id} is {character.corporation.tax_rate}%")

        character.corporation.save(update_fields=["tax_rate"])

        logger.info(f"Retrieving the corporation wallet journal for the CEO {character}")

        unfiltered_transactions = esi.client.Wallet.get_corporations_corporation_id_wallets_division_journal(
                corporation_id=character.eve_character.corporation_id,
                division=1,
                token=token.valid_access_token()
        ).results()

        logger.info(f"Filtering the ledge to keep only ESS and Bounty")
        corporation_ledger = []
        for transaction in unfiltered_transactions:
            if transaction["ref_type"] == "ess_escrow_transfer" or transaction["ref_type"] == "bounty_prizes":
                corporation_ledger.append(
                    WalletLedger(
                        id=transaction["id"],
                        date=transaction["date"],
                        amount=Decimal(str(transaction["amount"])),
                        ref_type=transaction["ref_type"],
                        generated_by=transaction["second_party_id"]
                    )
                )
        
        logger.info(f"There are {len(corporation_ledger)} entries for ESS and Bounty")
        return corporation_ledger