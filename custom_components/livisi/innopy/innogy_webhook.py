import logging

import json
import asyncio
import websockets
from pprint import pformat, pprint

from .innopy_client import InnopyClient

from .innogy_event import InnogyEvent

# from .innogy_client import InnogyClient
# from .innopy_constants import *


_LOGGER = logging.getLogger(__name__)


class InnogyWebhook(object):
    def __init__(self):
        _LOGGER.info("init webhook")

    def subscribe_events(self, hass, client):
        _LOGGER.info("starting innogy event handler")
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(self._innogy_event_handler(client))
        self.subscribe_events
        # self._innogy_event_handler()

    @asyncio.coroutine
    def _innogy_event_handler(self, client):
        #        websocket = yield from websockets.connect(API_URL_EVENTS.replace("{token}",self.token["access_token"]),sslopt={"cert_reqs": ssl.CERT_NONE})
        while True:
            try:
                _LOGGER.warning("connecting websocket")
                websocket = yield from websockets.connect(
                    API_URL_EVENTS.replace("{token}", client.token["access_token"])
                )
                _LOGGER.warning("websocket connected")

                _LOGGER.warning("waiting for event ...")
                response = yield from websocket.recv()
                result = json.loads(response)

                try:
                    self._handle_event(result, websocket)
                    _LOGGER.info("... event handled")
                except Exception as e:
                    import traceback

                _LOGGER.error(traceback.format_exc(e))
            except Exception as e:
                _LOGGER.warning(str(e))
            finally:
                yield from websocket.close()
                # self.initialize()

    def _handle_event(self, evt, websocket):
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
            device = InnogyClient.get_device_by_capability_id(cap_id)
            _LOGGER.info(device.config_dict["name"])
            for prop_name in event.properties_dict.keys():
                device.capabilities_dict[prop_name]["value"] = event.properties_dict[
                    prop_name
                ]["value"]

            if "lastchanged" in event.properties_dict[prop_name]:
                device.capabilities_dict[prop_name][
                    "lastchanged"
                ] = event.properties_dict[prop_name]["lastchanged"]
                _LOGGER.info(
                    "updated "
                    + str(prop_name)
                    + " to "
                    + str(device.capabilities_dict[prop_name]["value"])
                )

                # {'Properties': [{'name': 'Reason', 'value': 'SessionExpired'}],
                #'desc': '/desc/event/Disconnect',
                #'timestamp': '2018-05-01T22:10:35.2825559Z',
                #'type': '/event/Disconnect'} :
            _LOGGER.info("... event handled completely")
        except:
            _LOGGER.error("could not process event: " + pformat(evt))
