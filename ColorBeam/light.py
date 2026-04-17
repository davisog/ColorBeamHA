from __future__ import annotations

import logging
import asyncio
from typing import cast,Any
import voluptuous as vol
import uuid
from .pycolorbeam import ColorBeamBaseInstance,ColorBeamLightInstance,ColorBeamRGBLightInstance

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ColorMode,ATTR_COLOR_TEMP_KELVIN,ATTR_BRIGHTNESS,ATTR_TRANSITION, ATTR_RGB_COLOR,ATTR_RGBW_COLOR,ATTR_RGBWW_COLOR,
                                            LightEntity,LightEntityFeature,filter_supported_color_modes)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant,callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from .coordinator import ColorBeamUpdateCoordinator,ColorBeamBiUpdateCoordinator,ColorBeamRGBUpdateCoordinator
from .const import DOMAIN
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ColorBeam Light platform."""
    coordinator : ColorBeamUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    deviceLoadNames = coordinator.LoadNames

    known_devices_BI: set[int] = set()
    known_devices_RGB: set[int] = set()

    def check_device()->None:
        current_devices_RGB = coordinator.RGBlights
        current_devices_BI = coordinator.BIlights
        new_devices_RGB = current_devices_RGB-known_devices_RGB
        new_devices_BI = current_devices_BI-known_devices_BI

        for RGB in coordinator.RGBlights:
            if RGB in new_devices_RGB:
                light = {
                    "ip" : entry.data["host"],
                    "port" :entry.data["port"],
                    "name" : deviceLoadNames[str(RGB)]['name'],
                    "id" : RGB,
                    "uuid" : f"CB_{RGB}_light",
                    "version":coordinator.version
                }
                # Add devices
                add_entities([CbRGBLight(light)],update_before_add=True)
                known_devices_RGB.add(RGB)

        for BI in coordinator.BIlights:
            if BI in new_devices_BI:
                light = {
                    "ip" : entry.data["host"],
                    "port" :entry.data["port"],
                    "name" : deviceLoadNames[str(BI)]['name'],
                    "id" : BI,
                    "uuid" : f"CB_{BI}_light",
                    "version": coordinator.version
                }
                # Add devices
                add_entities([CbBiLight(light)],update_before_add=True)
                known_devices_BI.add(BI)
    
    check_device()
    entry.async_on_unload(
        coordinator.async_add_listener(check_device)
    )




class CbBiLight(LightEntity):
    """Representation of an ColorBeam Light."""
    _attr_color_mode = ColorMode.COLOR_TEMP
    _attr_supported_color_modes = {ColorMode.COLOR_TEMP}
    _attr_supported_features = LightEntityFeature.TRANSITION
    _attr_min_color_temp_kelvin = 2000
    _attr_max_color_temp_kelvin = 7000

    def __init__(self, light) -> None:
        """Initialize a ColorBeamLight."""
        self._light = ColorBeamLightInstance(light["ip"],light["port"],light["id"])
        self._name = light["name"]
        self._state = None
        self._attr_brightness = None
        self._previous_brightness = 255
        self._attr_color_temp_kelvin = None
        self._attr_unique_id = light["uuid"]
        self._version = light['version']

    @property
    def device_info(self)-> DeviceInfo:
        """return device Info"""
        return DeviceInfo(
            identifiers={(DOMAIN,f"CB_{self._attr_unique_id}_light")},
            name=self._name,
            manufacturer="color Beam",
            sw_version= self._version,
        )

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self) -> int:
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._attr_brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state
    @property
    def color_temp_kelvin(self) -> int | None:
        """Return Color Temp"""
        return self._attr_color_temp_kelvin


    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs.get(ATTR_BRIGHTNESS)
        elif self._previous_brightness == 0:
            self._attr_brightness = 255/2
        else:
            self._attr_brightness = self._previous_brightness
        if ATTR_COLOR_TEMP_KELVIN in kwargs:
            tempurature = kwargs.get(ATTR_COLOR_TEMP_KELVIN)
        else:
            tempurature = self._attr_color_temp_kelvin
        await self._light.setTemp(tempurature)
        await self._light.turn_on(self._attr_brightness)
        await self.async_update()
        self._previous_brightness = self._attr_brightness

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self._light.turn_off()
        await self.async_update()

        
    async def async_update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        await self._light.update()
        self._attr_color_temp_kelvin = self._light.Temp
        self._state = self._light.is_on
        self._attr_brightness = self._light.Getbrightness

class CbRGBLight(LightEntity):
    """Representation of an ColorBeam Light."""
    _attr_supported_features = LightEntityFeature.TRANSITION

    def __init__(self, light) -> None:
        """Initialize a ColorBeamLight."""
        self._light = ColorBeamRGBLightInstance(light["ip"],light["port"],light["id"])
        self._name = light["name"]
        self._state = None
        self._attr_brightness = None
        self._previous_brightness = 255
        self._attr_rgb_color = None
        self._attr_colorMode = None
        self._attr_supported_color_modes = None
        self._attr_unique_id = light["uuid"]
        self._version = light['version']

    @property
    def device_info(self)-> DeviceInfo:
        """return device Info"""
        return DeviceInfo(
            identifiers={(DOMAIN,f"CB_{self._attr_unique_id}_light")},
            name=self._name,
            manufacturer="color Beam",
            sw_version= self._version,
        )

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self) -> int:
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._attr_brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state
    @property
    def rgb_color(self) -> tuple | None:
        """Return Color """
        return self._attr_rgb_color
    @property
    def rgbw_color(self) -> tuple | None:
        """Return Color """
        return self._attr_rgb_color
    @property
    def rgbww_color(self) -> tuple | None:
        """Return Color """
        return self._attr_rgb_color
    @property
    def color_mode(self) -> ColorMode:
        """return color mode"""
        if len(self._attr_rgb_color) == 5:
            return ColorMode.RGBWW
        elif len(self._attr_rgb_color) == 4:
            return ColorMode.RGBW
        else:
            return ColorMode.RGB
    @property
    def supported_color_modes(self):
        color_mode = self.color_mode
        if color_mode== ColorMode.RGBWW:
            return {ColorMode.RGBWW}
        elif color_mode == ColorMode.RGBW:
            return {ColorMode.RGBW}
        else:
            return {ColorMode.RGB}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs.get(ATTR_BRIGHTNESS)
        elif self._previous_brightness == 0:
            brightness = 255/2
        else:
            brightness = self._previous_brightness
        if ATTR_RGBWW_COLOR in kwargs:
            rgb_color = kwargs.pop(ATTR_RGBWW_COLOR)
        elif ATTR_RGBW_COLOR in kwargs:
            rgb_color = kwargs.pop(ATTR_RGBW_COLOR)
        elif ATTR_RGB_COLOR in kwargs:
            rgb_color = kwargs.pop(ATTR_RGB_COLOR)
        else:
            rgb_color = self._attr_rgb_color
        await self._light.setRGB(rgb_color)
        await self._light.turn_on(brightness)
        await self.async_update()
        self._previous_brightness = self._attr_brightness

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self._light.turn_off()
        await self.async_update()

    async def async_update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        await self._light.update()
        self._attr_rgb_color = self._light.getRGB
        self._attr_colorMode = self.color_mode
        self._attr_supported_color_modes = self.supported_color_modes
        _LOGGER.debug(self._attr_rgb_color)
        self._state = self._light.is_on
        self._attr_brightness = self._light.Getbrightness
        