"""represenation of a ColorBeam BI Light"""

from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import ColorBeamUpdateCoordinator
#import ColorBeam.pycolorbeam as pycolorbeam

PLATFORMS = [Platform.LIGHT]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the ColorBeam integration."""

    coordinator = ColorBeamUpdateCoordinator(
        hass,
        entry.title,
        pycolorbeam.ColorBeamBaseInstance(
            entry.data['host'],entry.data['port']
        )
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN,{})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Clean up resources and entities associated with the integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok