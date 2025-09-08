from pathlib import Path

from . import __version__

from esi.clients import EsiClientProvider

esi = EsiClientProvider(
    app_info_text=f"milalliancetaxes v{__version__}"
)