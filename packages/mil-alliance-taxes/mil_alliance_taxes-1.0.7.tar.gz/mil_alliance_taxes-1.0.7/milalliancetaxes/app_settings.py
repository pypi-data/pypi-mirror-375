from app_utils.django import clean_setting

MILALLIANCETAXES_ALLIANCE_ID = clean_setting("MILALLIANCETAXES_ALLIANCE_ID", None, required_type=list)
MILALLIANCETAXES_TAX_RATE = clean_setting("MILALLIANCETAXES_TAX_RATE", None, required_type=float)