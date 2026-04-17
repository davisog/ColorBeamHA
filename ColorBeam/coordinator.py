"""Coordinator for the ColorBeam integration."""

import asyncio
from datetime import timedelta
import logging
from typing import Any


from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN
from .pycolorbeam import ColorBeamBaseInstance,ColorBeamLightInstance,ColorBeamRGBLightInstance

UPDATE_INTERVAL = 20
_LOGGER = logging.getLogger(__name__)

class ColorBeamUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Update coordinator for ColorBeam data."""

    RGB: list
    BI:list
    version:str
    LoadNames:dict

    def __init__(self,hass: HomeAssistant,name:str,client:ColorBeamBaseInstance
                 )->None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
         )
        self.client = client

    @property
    def RGBlights(self)->list:
        return self.RGB
    
    @property
    def BIlights(self)->list:
        return self.BI

    def LoadNames(self)->dict:
        return self.LoadNames

    async def _async_update_data(self) -> dict:
        """Update ColorBeam data."""

        if not hasattr(self,"RGB") or not hasattr(self,"BI") or not hasattr(self,"LoadNames"):
            async with asyncio.timeout(10):
                try:
                    self.BI , self.RGB = await self.client.updateall()
                    self.version = await self.client.getversion()
                    self.LoadNames = await self.client.getLoadStore()
                except Exception as e:
                    _LOGGER.error(e)
        
class ColorBeamBiUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Update coordinator for ColorBeam Bi data."""

    data : dict[str,Any]

    def __init__(self,hass: HomeAssistant,name:str,client:ColorBeamLightInstance
                 )->None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
         )
        self.client = client

    @property
    def brightness(self):
        return self.data["brightness"]
    
    @property
    def temp(self):
        return self.data["temp"]
    
    @property
    def is_On(self):
        return self.data["is_on"]

    async def _async_update_data(self) -> dict:
        """Update ColorBeam data."""

        if not hasattr(self.data):
            async with asyncio.timeout(10):
                try:
                    self.data = await self.client.update()
                except Exception as e:
                    _LOGGER.error(e)

class ColorBeamRGBUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Update coordinator for ColorBeam RGB data."""

    data: dict[str,Any]

    def __init__(self,hass: HomeAssistant,name:str,client:ColorBeamRGBLightInstance
                 )->None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_intveral=timedelta(seconds=UPDATE_INTERVAL),
         )
        self.client = client

    @property
    def brightness(self):
        return self.data["brightness"]
    
    @property
    def RGB(self):
        return self.data["RGB"]
    
    @property
    def is_On(self):
        return self.data["is_on"]

    async def _async_update_data(self) -> dict:
        """Update ColorBeam data."""

        if not hasattr(self.data):
            async with asyncio.timeout(10):
                try:
                    self.data = await self.client.update()
                except Exception as e:
                    _LOGGER.error(e)