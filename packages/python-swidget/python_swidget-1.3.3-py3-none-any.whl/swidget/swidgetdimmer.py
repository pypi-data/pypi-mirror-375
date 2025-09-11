"""Module for SwidgetDimmer."""
import logging

from swidget.exceptions import SwidgetException
from swidget.swidgetdevice import DeviceType, SwidgetDevice

_LOGGER = logging.getLogger(__name__)


class SwidgetDimmer(SwidgetDevice):
    """Representation of a Swidget Dimmer device."""

    def __init__(
        self,
        host,
        token_name: str,
        secret_key: str,
        use_https: bool,
        use_websockets: bool,
    ) -> None:
        super().__init__(
            host=host,
            token_name=token_name,
            secret_key=secret_key,
            use_https=use_https,
            use_websockets=use_websockets,
        )
        self.device_type = DeviceType.Dimmer

    @property  # type: ignore
    def brightness(self) -> int:
        """Return current brightness on dimmers.

        Will return a range between 0 - 100.
        """
        _LOGGER.debug("SwidgetDimmer.brightness called")
        if not self.is_dimmable:
            raise SwidgetException("Device is not dimmable.")
        try:
            return self.assemblies["host"].components["0"].functions["level"]["now"]
        except KeyError:
            return self.assemblies["host"].components["0"].functions["level"]["default"]

    async def set_brightness(self, brightness) -> None:
        """Set the brightness of the device."""
        _LOGGER.debug(
            "SwidgetDimmer.set_brightness() called with brightness: {brightness}"
        )
        self.assemblies["host"].components["0"].functions["level"]["now"] = brightness
        await self.send_command(
            assembly="host",
            component="0",
            function="level",
            command={"now": brightness},
        )

    async def set_default_brightness(self, brightness) -> None:
        """Set the brightness of the device when it is turned on."""
        _LOGGER.debug(
            "SwidgetDimmer.set_default_brightness() called with brightness: {brightness}"
        )
        await self.send_command(
            assembly="host",
            component="0",
            function="level",
            command={"default": brightness},
        )

    @property  # type: ignore
    def is_dimmable(self) -> bool:
        """Whether the switch supports brightness changes."""
        _LOGGER.debug("SwidgetDimmer.is_dimmable() called")
        return True
