"""Views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.utils.html import format_html
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    JsonResponse,
)
from django.utils.timezone import now
from django.urls import reverse

from allianceauth.eveonline.models import EveCharacter
from .models.corp_ceo import CorpCeo
from .models.corporation import Corporation
from .providers import esi

from .app_settings import (
    MILALLIANCETAXES_ALLIANCE_ID,
    MILALLIANCETAXES_TAX_RATE
)

from esi.decorators import token_required

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

@login_required
@permission_required("milalliancetaxes.basic_access")
def redirect_to_current_month(request):
    today = now()
    year_month = today.strftime("%Y_%m")

    return redirect('milalliancetaxes:view_tax', year_month=year_month)


@login_required
@permission_required("milalliancetaxes.basic_access")
@token_required(scopes=CorpCeo.get_esi_scopes())
def add_character(request, token) -> HttpResponse:
    logger.info(f"Creating the CEO {token.character_name}")
    eve_character = get_object_or_404(EveCharacter, character_id=token.character_id)

    corporation = Corporation.objects.filter(corporation_id=eve_character.corporation_id).first()
    if not corporation:
        logger.info(f"Unknown corp ID {eve_character.corporation_id} -> Creating it")
        corporation = Corporation.create_missing_corporation(eve_character.corporation_id)

    with transaction.atomic():
        corpCeo, _ = CorpCeo.objects.update_or_create(
            eve_character=eve_character,
            corporation=corporation
        )
      
    messages.success(
        request,
        format_html(
            "<strong>{}</strong> has been registered. ",
            eve_character,
        ),
    )

    return redirect("milalliancetaxes:redirect_to_current_month")

@login_required
@permission_required("milalliancetaxes.basic_access")
def view_tax(request, year_month):
    from .models.corporation import Corporation

    try:
        year, month = map(int, year_month.split("_"))
    except (ValueError, AttributeError):
        return render(request, "milalliancetaxes/invalid_date.html", status=400)

    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    corporation_ids = list(Corporation.objects.values_list('corporation_id', flat=True))

    corporations_with_tax = []

    for corporation_id in corporation_ids:
        corp = Corporation.objects.get(corporation_id=corporation_id)
        logger.info(f"Retrieving the monthly tax value for the corp {corp.name} under the alliances {MILALLIANCETAXES_ALLIANCE_ID}")
        tax_sum = corp.get_tax_for_month(year, month)
        corporations_with_tax.append((corp, tax_sum))


    prev_url = reverse("milalliancetaxes:view_tax", kwargs={"year_month": f"{prev_year}_{prev_month:02d}"})
    next_url = reverse("milalliancetaxes:view_tax", kwargs={"year_month": f"{next_year}_{next_month:02d}"})

    context = {
        "month": month,
        "year": year,
        "alliance_tax_rate": MILALLIANCETAXES_TAX_RATE,
        "corporations": corporations_with_tax,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "prev_url": prev_url,
        "next_url": next_url,
        }
    return render(request, "milalliancetaxes/tax_overview.html", context)

@login_required
@permission_required("milalliancetaxes.admin_access")
def admin_panel(request):
    corporations = Corporation.objects.all()

    context = {
        "corporations" : corporations
    }
    return render(request, "milalliancetaxes/admin_panel.html", context)

@login_required
@permission_required("milalliancetaxes.admin_access")
def untrack_corporation(request, corporation_id):
    logger.info(f"Corporation {corporation_id} will no longer be tracked")

    try:
        corp = get_object_or_404(Corporation, corporation_id=corporation_id)
    except:
        messages.error(request, f"Corporation with ID {corporation_id} does not exist")
        return redirect('milalliancetaxes:admin_panel')
    
    corp.delete()

    messages.success(
        request,
        format_html(
            "Taxes for this corporation will no longer be tracked."
        ),
    )
    return redirect('milalliancetaxes:admin_panel')
