from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_WINDOW,
    BinarySensorEntity,
)

from . import DATA_KEY


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Iterate through all LIVISI! Devices and add window shutters."""
    devices = []

    for device in hass.data[DATA_KEY].window_sensors:
        devices.append(LivisiWindowSensor(device, device.type))

    if devices:
        add_entities(devices)


class LivisiWindowSensor(BinarySensorEntity):
    """Representation of a LIVISI! Cube Binary Sensor device."""

    def __init__(self, innogy_device, sensor_type):
        """Initialize of the Innogy Sensor."""
        self._innogy_device = innogy_device
        self._sensor_type = sensor_type
        self._state = None
        self._state_attributes = None

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._innogy_device.id + str(self._sensor_type)

    @property
    def name(self):
        """Return the name of the sensor."""

        location_name = ""
        try:
            location_name = self._innogy_device.location_dict["name"]
        except:
            location_name = ""

        if location_name:
            return (
                location_name
                + "_"
                + self._innogy_device.config_dict["name"]
                + "_"
                + self._sensor_type
            )

        return self._innogy_device.config_dict["name"] + "_" + self._sensor_type

    @property
    def state(self):
        """Return the state of the sensor."""
        try:
            if self._innogy_device.capabilities_dict["isOpen"]:
                state = self._innogy_device.capabilities_dict["isOpen"]["value"]
                return state
        except:
            return False

    @property
    def should_poll(self):
        return False

    def update(self):
        """Update method called when should_poll is true."""
        if self._innogy_device.capabilities_dict["isOpen"]:
            self._state = self._innogy_device.capabilities_dict["isOpen"]["value"]
        # self.update()
        # pass

    # def is_on(self):
    #     """Return true if the binary sensor is on/open."""
    #     return self._device.is_open

    # @property
    # def device_state_attributes(self):
    #     """Return the state attributes."""
    #     return self._state_attributes
