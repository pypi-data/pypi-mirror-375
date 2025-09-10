from homeassistant.core import HomeAssistant, Event, Context
import logging
import asyncio
from threading import Lock, Thread

_LOGGER = logging.getLogger(__name__)


class SingletonMeta(type):
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class WhoDid(metaclass=SingletonMeta):
    def __init__(self, hass: HomeAssistant):
        self._eventIdUserMapping = {}
        self.hass = HomeAssistant

        async def handle_event(event: Event):
            if event.context.user_id != None:
                self._eventIdUserMapping[event.context.id] = event.context.user_id

        hass.bus.async_listen("*", handle_event)

    async def getUserId(self, context: Context):
        userid = context.user_id

        if context.user_id == None:
            retryCount = 0
            while context.parent_id not in self._eventIdUserMapping.keys():
                _LOGGER.debug(f"{context.parent_id} in yet in eventIdUserMapping")
                retryCount = retryCount + 1
                if retryCount == 10:
                    _LOGGER.debug(f"{context.parent_id} - Failed to get userid")
                    return None
                await asyncio.sleep(0.1)

            userid = self._eventIdUserMapping[context.parent_id]

        return userid
