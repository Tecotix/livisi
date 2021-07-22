# import .innopy_device_types
from pprint import pprint, pformat
import logging
import colorlog

_LOGGER = logging.getLogger(__name__)


def create_devices(innogy_client, device):
    devices = []

    i = InnogyDevice(innogy_client, device)

    return i


class InnogyDevice:
    def __init__(self, innogy_client, device):
        self.client = innogy_client
        self._set_data(device)
        _LOGGER.info("creating device: " + device["id"])

    def _set_data(self, device):

        try:
            self.config_dict = {
                item: device["config"][item] for item in device["config"]
            }
        except:
            _LOGGER.info("Test")
        # self.config = {item: device["config"][item] for item in device["config"]}

        # self.desc = device["desc"]
        self.id = device["id"]

        self.manufacturer = device["manufacturer"]
        self.product = device["product"]
        self.serialnumber = device["serialNumber"]
        self.type = device["type"]
        self.version = device["version"]

        # TODO: Handle tags?
        state_dict = {}
        if "device_state" in device:

            for state in device["device_state"]:
                if "lastChanged" in state:
                    state_dict.update(
                        {
                            state: {
                                "value": device["device_state"][state],
                                "lastchanged": device["device_state"][state],
                            }
                        }
                    )
                else:
                    state_dict.update({state: {"value": device["device_state"][state]}})

        self.device_state_dict = state_dict

        capabilities_dict = {}
        if "resolved_capabilities" in device:
            for cap in device["resolved_capabilities"]:
                if "state" in device["resolved_capabilities"][cap]:
                    for s in device["resolved_capabilities"][cap]["state"]:
                        cap_name = s
                        cap_value = device["resolved_capabilities"][cap]["state"][s][
                            "value"
                        ]
                        cap_lastchanged = device["resolved_capabilities"][cap]["state"][
                            s
                        ]["lastChanged"]
                        capabilities_dict.update(
                            {
                                cap_name: {
                                    "id": cap,
                                    "value": cap_value,
                                    "lastChanged": cap_lastchanged,
                                }
                            }
                        )

        self.capabilities_dict = capabilities_dict

        locations_dict = {}
        if "resolved_location" in device:
            if "location" in device:
                loc_id = device["location"].replace("/location/", "")
                if "resolved_location" in device:
                    loc_name = device["resolved_location"]["name"]
                    loc_type = device["resolved_location"]["type"]
                    locations_dict.update(
                        {loc_name: {"name": loc_name, "id": loc_id, "type": loc_type}}
                    )
        self.location_dict = locations_dict

    def update(self):
        _LOGGER.info("updating device...")
        device_data = self.client.get_full_device_by_id(self.id)
        self._set_data(device_data)
