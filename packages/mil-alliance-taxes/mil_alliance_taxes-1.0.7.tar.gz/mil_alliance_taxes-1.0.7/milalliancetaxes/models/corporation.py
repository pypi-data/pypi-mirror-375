from decimal import Decimal
from django.db import models
from django.db.models import Sum

from datetime import datetime, timedelta

from ..providers import esi

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

from ..app_settings import (
    MILALLIANCETAXES_ALLIANCE_ID
)

class Corporation(models.Model):
    corporation_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    is_updated = models.BooleanField(default=False)
    tax_rate = models.DecimalField(max_digits=20, decimal_places=2)

    def get_tax_for_month(self, year: int, month: int) -> Decimal:
        from .tax_ledger import TaxLedger

        entries_for_month = TaxLedger.objects.filter(
            corporation_id=self.corporation_id,
            date__year=year,
            date__month=month,
            alliance_id__in=MILALLIANCETAXES_ALLIANCE_ID
        )

        logger.info(f"{len(entries_for_month)} entries retrieved from the ledger for the corporation {self.corporation_id} - month {month} - year {year}")

        return entries_for_month.aggregate(total_amount=Sum('taxed_amount'))['total_amount'] or Decimal('0.00')
    
    @staticmethod
    def create_missing_corporation(corporation_id: int):
        corporation_data = esi.client.Corporation.get_corporations_corporation_id(
            corporation_id=corporation_id
        ).results()

        corporation, _ = Corporation.objects.update_or_create(
            corporation_id=corporation_id,
            tax_rate=round(corporation_data["tax_rate"]*100, 2),
            defaults={
                "name": corporation_data["name"],
                "is_updated": False
            }
        )

        return corporation
    
    def get_member_from_alliance_date_range(self):
        alliance_history = esi.client.Corporation.get_corporations_corporation_id_alliancehistory(
            corporation_id=self.corporation_id
        ).results()

        sorted_records = sorted(alliance_history, key=lambda r: r['start_date'])

        membership_range = {'start': None, 'end': None}
        
        for i, record in enumerate(sorted_records):
            alliance_id = record.get('alliance_id')
            record_date = record['start_date']

            if alliance_id in MILALLIANCETAXES_ALLIANCE_ID:
                # Reset and start the range -- Overwrites any precedent entry as we only keep the most recent membership
                membership_range = {'start': record_date, 'end': None}
            elif membership_range['start'] is not None:
                # If in the MILALLIANCETAXES_ALLIANCE_ID and it changes or becomes None
                membership_range['end'] = record_date

        #If start is defined but there is no end, it means the corporation is still in the alliance
        if membership_range and membership_range['end'] is None:
            membership_range['end'] = datetime.now(tz=record_date.tzinfo) + timedelta(days=1)               

        logger.info(f"The Corporation {self.corporation_id} was a member of the alliance from {membership_range['start']} to {membership_range['end']}")

        return membership_range