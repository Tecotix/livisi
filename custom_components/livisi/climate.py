from homeassistant.components.climate import ClimateEntity, ClimateDevice

import logging

from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)

from homeassistant.components.climate import (
    ATTR_CURRENT_HUMIDITY,
    ATTR_CURRENT_TEMPERATURE,
    ATTR_MAX_TEMP,
    ATTR_MIN_TEMP,
    ATTR_TEMPERATURE,
    PLATFORM_SCHEMA,
    # STATE_AUTO,
    # STATE_MANUAL,
    # SUPPORT_AWAY_MODE,
    # SUPPORT_OPERATION_MODE,
    SUPPORT_TARGET_HUMIDITY,
    SUPPORT_TARGET_TEMPERATURE,
    ClimateDevice,
    ClimateEntity,
    abstractmethod,
)

from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    PRECISION_HALVES,
    TEMP_CELSIUS,
)

CONST_OVERLAY_MANUAL = "Manu"
CONST_OVERLAY_AUTOMATIC = "Auto"

# There are two magic temperature values, which indicate:
# Off (valve fully closed)
OFF_TEMPERATURE = 6
# On (valve fully open)
ON_TEMPERATURE = 30.5


OPERATION_LIST = {
    CONST_OVERLAY_MANUAL: HVAC_MODE_OFF,
    CONST_OVERLAY_AUTOMATIC: HVAC_MODE_AUTO,
}

from . import DATA_KEY

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Iterate through all LIVISI! Devices and add thermostats."""
    devices = []

    for device in hass.data[DATA_KEY].thermostats:
        devices.append(LivisiThermostat(device))

    if devices:
        add_entities(devices)


class LivisiThermostat(ClimateEntity):
    def __init__(self, innogy_device):
        # def __init__(self, handler, innogy_device):
        self._innogy_device = innogy_device
        self._support_flags = SUPPORT_TARGET_TEMPERATURE  # | SUPPORT_OPERATION_MODE
        self._min_temp = 6.0
        self._max_temp = 30.0

    @property
    def hvac_mode(self):
        """Return current operation mode."""
        mode = self._innogy_device.capabilities_dict["operationMode"]["value"]
        if mode in [CONST_OVERLAY_AUTOMATIC]:
            return HVAC_MODE_AUTO
        if mode == CONST_OVERLAY_MANUAL:
            return HVAC_MODE_OFF

        return HVAC_MODE_HEAT

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return [HVAC_MODE_OFF, HVAC_MODE_AUTO, HVAC_MODE_HEAT]

    def set_hvac_mode(self, hvac_mode: str):
        """Set new target hvac mode."""

        if hvac_mode == HVAC_MODE_OFF:
            self._innogy_device.client.set_OperationMode_state(
                self._innogy_device.capabilities_dict["operationMode"]["id"],
                CONST_OVERLAY_MANUAL,
            )
        elif hvac_mode == HVAC_MODE_HEAT:
            temp = 1

        elif hvac_mode == HVAC_MODE_AUTO:
            self._innogy_device.client.set_OperationMode_state(
                self._innogy_device.capabilities_dict["operationMode"]["id"],
                CONST_OVERLAY_AUTOMATIC,
            )

        else:
            raise ValueError(f"unsupported HVAC mode {hvac_mode}")

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    # @property
    # def current_operation(self):
    #     """Return current operation ie. heat, cool, idle."""
    #     mode = self._innogy_device.capabilities_dict["OperationMode"]["value"]
    #     return OPERATION_LIST.get(mode)

    @property
    def unique_id(self):
        """Unique ID for this device."""
        return self._innogy_device.id

    @property
    def name(self):
        """Return the name of the device."""
        return self._innogy_device.config_dict["name"]

    @property
    def current_humidity(self):
        """Return the current humidity."""
        return self._innogy_device.capabilities_dict["humidity"]["value"]

    @property
    def current_temperature(self):
        """Return the sensor temperature."""
        return self._innogy_device.capabilities_dict["temperature"]["value"]

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._innogy_device.capabilities_dict["pointTemperature"]["value"]

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return PRECISION_HALVES

    # @property
    # def operation_list(self):
    #     """List of available operation modes."""
    #     return list(OPERATION_LIST.values())

    @property
    def available(self):
        """Return if thermostat is available."""
        return self._innogy_device.device_state_dict["isReachable"]["value"]["value"]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_CURRENT_HUMIDITY: self._innogy_device.capabilities_dict["humidity"][
                "value"
            ],
            "is_reachable": self._innogy_device.device_state_dict["isReachable"][
                "value"
            ],
            # TODO: implement battery low message handling
            # ATTR_STATE_BATTERY_LOW: self._device.battery_low
        }
        return attrs

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        if self._min_temp:
            return self._min_temp
        # get default temp from super class
        return super().min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        if self._max_temp:
            return self._max_temp
        #  Get default temp from super class
        return super().max_temp

    def update(self):
        """Update the state of this climate device."""
        # This is handled by the websocket
        _LOGGER.info("updating device...")
        device_data = self._innogy_device.client.get_full_device_by_id(
            self._innogy_device.id
        )
        myDict = {"temperature": self.target_temperature}
        self.set_temperature(**myDict)
        self.set_operation_mode()
        # _LOGGER.error("Handle Update")
        # TODO Handle update
        # self._innogy_device.client._set_data(device_data)
        # self.update()
        # pass

    @property
    def should_poll(self):
        return True

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        _LOGGER.warn("set temp: " + str(temperature))
        if temperature is None:
            return
        self._innogy_device.client.set_PointTemperature_state(
            self._innogy_device.capabilities_dict["pointTemperature"]["id"],
            float(temperature),
        )

    # pylint: disable=arguments-differ
    def set_operation_mode(self, readable_operation_mode=None):
        """Set new operation mode."""
        _LOGGER.warn("set mode: " + str(readable_operation_mode))

        if readable_operation_mode == None:
            mode = self._innogy_device.capabilities_dict["operationMode"]["value"]
            if mode == "Auto":
                self._innogy_device.client.set_OperationMode_state(
                    self._innogy_device.capabilities_dict["operationMode"]["id"],
                    CONST_OVERLAY_AUTOMATIC,
                )
            else:
                self._innogy_device.client.set_OperationMode_state(
                    self._innogy_device.capabilities_dict["operationMode"]["id"],
                    CONST_OVERLAY_MANUAL,
                )

        else:
            if readable_operation_mode == "Automatic":
                self._innogy_device.client.set_OperationMode_state(
                    self._innogy_device.capabilities_dict["operationMode"]["id"],
                    CONST_OVERLAY_AUTOMATIC,
                )
            else:
                self._innogy_device.client.set_OperationMode_state(
                    self._innogy_device.capabilities_dict["operationMode"]["id"],
                    CONST_OVERLAY_MANUAL,
                )
