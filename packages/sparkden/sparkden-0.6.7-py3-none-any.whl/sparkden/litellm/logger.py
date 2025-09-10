import json

from litellm.integrations.custom_logger import CustomLogger
from litestar.types.protocols import Logger


class LitellmLogger(CustomLogger):
    def __init__(self, logger: Logger, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        self.logger.debug(
            f"Litellm success event: {
                json.dumps(
                    {
                        'response_obj': response_obj.model_dump(),
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat(),
                    },
                    indent=2,
                )
            }"
        )

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        self.logger.debug(
            f"Litellm failure event: {
                json.dumps(
                    {
                        'response_obj': response_obj.model_dump(),
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat(),
                    },
                    indent=2,
                )
            }"
        )
