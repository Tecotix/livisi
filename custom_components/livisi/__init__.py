"""Support for the (unofficial) livisi API."""
from datetime import timedelta
import logging
import threading
import time

# from PyTado.interface import Tado
from requests import RequestException
import requests.exceptions

import asyncio
import websockets

from pprint import pformat, pprint
import json
from .innopy.innopy_constants import *
from .innopy.innogy_event import InnogyEvent
from .innopy.innogy_webhook import InnogyWebhook

# from .innopy.innopy.innopy_client import InnopyClient

from homeassistant.components.climate.const import PRESET_AWAY, PRESET_HOME
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import Throttle
from homeassistant.helpers.discovery import (
    load_platform,
    async_load_platform,
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

from .const import (
    CONF_FALLBACK,
    DATA,
    DOMAIN,
    INSIDE_TEMPERATURE_MEASUREMENT,
    SIGNAL_TADO_UPDATE_RECEIVED,
    TEMP_OFFSET,
    UPDATE_LISTENER,
    UPDATE_TRACK,
)


from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "livisi"
DATA_KEY = "livisi"

CONST_OVERLAY_MANUAL = "Manu"
CONST_OVERLAY_AUTOMATIC = "Auto"

PLATFORMS = ["climate", "binary_sensor"]

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=4)
SCAN_INTERVAL = timedelta(seconds=5)

CONFIG_SCHEMA = cv.deprecated(DOMAIN)


# def setup(hass, config):
#     _LOGGER.info("Setup...")
#     return True


# async def async_setup_entry(hass, config_entry):
#     _LOGGER.info("async Setup entry...")
#     return True


# async def async_setup(hass, config):
#     _LOGGER.info("async Setup entry...")
#     if DOMAIN not in config:
#         return True

#     if hass.config_entries.async_entries(DOMAIN):
#         # We can only have one dongle. If there is already one in the config,
#         # there is no need to import the yaml based config.
#         return True


# def setup_platform(hass, config, add_devices, discovery_info=None):
# def setup_platform(hass, config, add_devices, discovery_info=None):
def setup(hass, config):
    # async def async_setup(hass, config):

    #     innopy = hass.data[DATA_KEY]
    #     hass.async_create_task(innopy.subscribe_events())

    # async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # def setup(hass, config):

    # username = config[DOMAIN][CONF_USERNAME]
    # password = config[DOMAIN][CONF_PASSWORD]

    import json

    from .innopy.innopy_client import InnopyClient

    try:

        global token
        # json_token = '{"access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjQ2RDUwNkFBQkYxNzJDNDA0N0ExQjM3Qzc5RjJFRDQzRDU3QjFDMjIiLCJ4NXQiOiJSdFVHcXI4WExFQkhvYk44ZWZMdFE5VjdIQ0kiLCJ0eXAiOiJKV1QifQ.eyJjbGllbnRfaWQiOiIzNTkwMzU4NiIsInN1YiI6ImRyYWdvbmZseTE5NzgiLCJkZXZpY2UiOiI5MTQxMDEwMTE3MTQiLCJjbGllbnRfcGVybWlzc2lvbnMiOiIzRkRGRiIsInRlbmFudCI6IlJXRSIsInVzZXJfcGVybWlzc2lvbnMiOiJGRkZGRkZGRkZGRkZGRkZGIiwic2Vzc2lvbiI6IjgzNDVlODgyMjZkZDQ0NTZhNTQzNTFhYjU3YWYyMDU4IiwibmJmIjoxNjIwNjQyMzk3LCJleHAiOjE2MjA4MTUxOTcsImlzcyI6IlNtYXJ0SG9tZUFQSSIsImF1ZCI6ImFsbCJ9.iIMiAvHirUBekkfLSL06de3iYOIO3Xo4p5_o49dwD9rhxqCYB0Fxo23qo1uQ69VoxrqKL99iDIuR2nFFgu21BXy5dNp1chxR10a7WqUXdykn-snMJwwITBYQWFI9g59vZ6SGSTsd87e5Z50eGuf50c_GD80c6hZ9Wg85l709k-Weinl-ihn_7KP4XtkfY1ytn_oZ7Z7_gfe8dTFBuEz9WrVbbP4eUiE9fLsuXv0KBv0fCnnQSqvYf2nA5_coR16ecaJzOxSod_7Rq-eK9rMa2c96W_JoyhZJ4N0AsZQzcReFClQE4cy2BL7w2YgRYUbzmWHOjiALfdrPyJXmctGRjA'
        json_token = '{"access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjQ2RDUwNkFBQkYxNzJDNDA0N0ExQjM3Qzc5RjJFRDQzRDU3QjFDMjIiLCJ4NXQiOiJSdFVHcXI4WExFQkhvYk44ZWZMdFE5VjdIQ0kiLCJ0eXAiOiJKV1QifQ.eyJjbGllbnRfaWQiOiI1NDAzMTExNSIsInN1YiI6ImRyYWdvbmZseTE5NzgiLCJkZXZpY2UiOiI5MTQxMDEwMTE3MTQiLCJjbGllbnRfcGVybWlzc2lvbnMiOiI4RkIiLCJ0ZW5hbnQiOiJSV0UiLCJ1c2VyX3Blcm1pc3Npb25zIjoiRkZGRkZGRkZGRkZGRkZGRiIsInNlc3Npb24iOiJkZjA1ODE2NWUzZGY0YTY2OGYzNzc5YmM4MGIwNDVhZiIsIm5iZiI6MTYyNjg1Mzk3MSwiZXhwIjoxNjI3MDI2NzcxLCJpc3MiOiJTbWFydEhvbWVBUEkiLCJhdWQiOiJhbGwifQ.aiMKXYX3jTLCgHeMxP0pthfHESI9AvMuFXgS0oSJCaFn35U-77oKyTrQFuq22_kgMmxTW969YhQlZ9JDAtX8YV6miXPWWz0oNnb53HPkKS4CVtV9U6MiJked3sjsvj4eUKgPJsIFNVb6NM1i9_OvSCSNvRGqn3WI8kVMr-dV66nU20y3aF3KF6oNDY5ENmZBcmBCSHJvFTfedjdCRsOJFUXFh54KJHuMPCn46bpIDKSiAZDqYsihD9KsAnAiryeUc50Zj2wpGPUBM8lXN3J0fqZlL1DitWE6H_CUbxffMgOpEVAcFjUleI6gpKfBdFib7IWV4sPfBPltqhWMqY8jPA","token_type": "Bearer","expires_in": 172800,"refresh_token": "8c3f2aeee57942a5ae6bcb25dac8df41"}'
        token = json.loads(json_token)
        global innopy
        innopy = InnopyClient(token, hass)

    except Exception as e:
        _LOGGER.error("Innopy could not be initalized: " + str(e))
        return False

    _LOGGER.warning("getting climate devices")

    # climate_devices = []

    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}

    hass.data[DATA_KEY] = innopy

    load_platform(hass, "climate", DOMAIN, {}, config)
    load_platform(hass, "binary_sensor", DOMAIN, {}, config)

    # Create a Thread with a function without any arguments
    th = threading.Thread(target=subscribe_events)
    # Start the thread
    th.start()

    # hass.async_create_task(subscribe_events())
    # subscribe_events()

    _LOGGER.warning("init complete")

    # asyncio.run_coroutine_threadsafe(async_setup_entry1(hass), hass.loop)
    # asyncio.run_coroutine_threadsafe(innopy.subscribe_events(), hass.loop)

    # async_load_platform(hass, "binary_sensor", DOMAIN, {}, config)
    # async_load_platform(hass, "climate", DOMAIN, {}, config)

    # asyncio.run_coroutine_threadsafe(async_setup_entry1(hass), hass.loop)

    # asyncio.ensure_future(innopy.subscribe_events())

    # yield from hass.async_create_task(innopy.subscribe_events())

    # hass.async_create_task(innopy.subscribe_events())

    # hass.async_add_executor_job(innopy.subscribe_events())

    # asyncio.run_coroutine_threadsafe(async_setup1(config, hass), hass.loop).result()

    # asyncio.ensure_future(async_setup1(config, hass))

    # asyncio.create_task(async_setup1(config, hass))

    # asyncio.run(innopy.subscribe_events())

    # asyncio.run_coroutine_threadsafe(innopy.subscribe_events(), hass.loop).result()
    # asyncio.run_coroutine_threadsafe(async_say_hello(hass, target), hass.loop).result()

    # Return boolean to indicate that initialization was successful.
    return True


# def setup(hass, config):
#     temp = 1
#     asyncio.run_coroutine_threadsafe(async_setup_entry1(), hass.loop)
#     return True


def subscribe_events():
    _LOGGER.info("starting innogy event handler")
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(_innogy_event_handler())
    # _innogy_event_handler()
    # self._innogy_event_handler()


@asyncio.coroutine
def _innogy_event_handler():
    #        websocket = yield from websockets.connect(API_URL_EVENTS.replace("{token}",self.token["access_token"]),sslopt={"cert_reqs": ssl.CERT_NONE})
    while True:
        try:
            _LOGGER.warning("connecting websocket")
            websocket = yield from websockets.connect(
                API_URL_EVENTS.replace("{token}", token["access_token"])
            )
            _LOGGER.warning("websocket connected")

            _LOGGER.warning("waiting for event ...")
            response = yield from websocket.recv()
            _LOGGER.warn(response)
            result = json.loads(response)

            try:
                _handle_event(result, websocket)
                _LOGGER.info("... event handled")
            except Exception as e:
                import traceback

                _LOGGER.error(traceback.format_exc(e))
        except Exception as e:
            _LOGGER.warning(str(e))
        finally:
            yield from websocket.close()
            # self.initialize()


# @asyncio.coroutine
def _handle_event(evt, websocket):
    try:
        _LOGGER.warning("new event ...")
        _LOGGER.warning(pformat(evt))
        event = InnogyEvent(evt)

        if event.type == "/event/Disconnect":
            _LOGGER.info("DISCONNECT EVENT!")
            _LOGGER.debug(pformat(evt))
            _LOGGER.info("closing websocket ...")
            websocket.close()
            return

        _LOGGER.info("getting change value")
        cap_id = event.source.replace("/capability/", "")
        device = innopy.get_device_by_capability_id(cap_id)
        _LOGGER.info(device.config_dict["name"])
        for prop_name in event.properties_dict.keys():
            device.capabilities_dict[prop_name]["value"] = event.properties_dict[
                prop_name
            ]["value"]

        if "lastchanged" in event.properties_dict[prop_name]:
            device.capabilities_dict[prop_name]["lastchanged"] = event.properties_dict[
                prop_name
            ]["lastchanged"]
            _LOGGER.info(
                "updated "
                + str(prop_name)
                + " to "
                + str(device.capabilities_dict[prop_name]["value"])
            )

        # device._set_data(device)
        # device.update()
        # {'Properties': [{'name': 'Reason', 'value': 'SessionExpired'}],
        #'desc': '/desc/event/Disconnect',
        #'timestamp': '2018-05-01T22:10:35.2825559Z',
        #'type': '/event/Disconnect'} :
        # if self.type == "RST":

        _LOGGER.info("... event handled completely")
    except:
        _LOGGER.error("could not process event: " + pformat(evt))
