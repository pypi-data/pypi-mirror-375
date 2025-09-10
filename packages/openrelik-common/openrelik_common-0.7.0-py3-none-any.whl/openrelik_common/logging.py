import logging
import os
import structlog

OPENRELIK_LOG_TYPE = "OPENRELIK_LOG_TYPE" # structlog,structlog_console,None


class Logger:
    """logger provides functionality to output plain logging, structured JSON
    logging of structured console logging.
    
    The logging output format is defined by setting the environment variable 
    OPENRELIK_LOG_TYPE to `structlog` or `structlog_console`
    Usage:
        ```
            from openrelik_common.logging import Logger

            # Instantiate Logger class
            log = Logger()

            # Setup a logger with 2 binded key-values.
            logger = log.get_logger(name=__name__, key1=value1, key2=value2)

            # Bind additional values to the logger, they will added to any log message.
            log.bind(workflow_id=workflow_id)

            # Output debug log message.
            logger.debug(f"This is a debug message")
        ```
    """

    def __init__(self):
        if os.environ.get(OPENRELIK_LOG_TYPE, "").startswith("structlog"):
            base_processors = [
                # Merge bind context variables
                structlog.contextvars.merge_contextvars,
                # If log level is too low, abort pipeline and throw away log entry.
                # structlog.stdlib.filter_by_level,
                # Add the name of the logger to event dict.
                structlog.stdlib.add_logger_name,
                # Add log level to event dict.
                structlog.stdlib.add_log_level,
                # Perform %-style formatting.
                structlog.stdlib.PositionalArgumentsFormatter(),
                # Add a timestamp in ISO 8601 format.
                structlog.processors.TimeStamper(fmt="iso"),
                # If the "stack_info" key in the event dict is true, remove it and
                # render the current stack trace in the "stack" key.
                structlog.processors.StackInfoRenderer(),
                # If the "exc_info" key in the event dict is either true or a
                # sys.exc_info() tuple, remove "exc_info" and render the exception
                # with traceback into the "exception" key.
                structlog.processors.format_exc_info,
                # If some value is in bytes, decode it to a Unicode str.
                structlog.processors.UnicodeDecoder(),
                # Add callsite parameters.
                structlog.processors.CallsiteParameterAdder(
                    {
                        structlog.processors.CallsiteParameter.FILENAME,
                        structlog.processors.CallsiteParameter.FUNC_NAME,
                        structlog.processors.CallsiteParameter.LINENO,
                    }
                ),
            ]
            if os.environ.get(OPENRELIK_LOG_TYPE, "") == "structlog_console":
                # Render the final event dict for Console output.
                base_processors.append(structlog.dev.ConsoleRenderer())
            else:
                # Render the final event dict as JSON.
                base_processors.append(structlog.processors.JSONRenderer())

            structlog.configure(
                processors=base_processors,
                # `wrapper_class` is the bound logger that you get back from
                # get_logger(). This one imitates the API of `logging.Logger`.
                wrapper_class=structlog.stdlib.BoundLogger,
                # `logger_factory` is used to create wrapped loggers that are used for
                # OUTPUT. This one returns a `logging.Logger`. The final value (a JSON
                # string) from the final processor (`JSONRenderer`) will be passed to
                # the method of the same name as that you've called on the bound logger.
                logger_factory=structlog.stdlib.LoggerFactory(),
                # Effectively freeze configuration after creating the first bound
                # logger.
                # cache_logger_on_first_use=True,
            )

    def get_logger(self, name="", wrap_logger=None, **kwargs):
        """Gets a logger instance.

        Args:
            name (str): The name of the logger.
            wrap_logger (logger): A Python logger instance that can be wrapped in a structlog instance.
            kwargs (**kwargs): Any key/value combinations to bind to the logger.

        Returns:
            logger: A (wrapped) structlog or plain python logger with key-value binded kwargs.
        """
        if wrap_logger:
            # This can be used to wrap e.g. the Celery logger in a structlog
            self.logger = structlog.wrap_logger(wrap_logger)
        elif os.environ.get(OPENRELIK_LOG_TYPE, "").startswith("structlog"):
            # Get a JSON or Console logger
            self.logger = structlog.get_logger(name)
        else:
            # Get a plain Python logger
            self.logger = logging.getLogger(name)

        # Bind any extra arguments as key-value pairs to the logger.
        self.bind(**kwargs)

        return self.logger

    def bind(self, **kwargs):
        """Bind key/values to a Logger instance.

        Args:
            kwargs (**kwargs): Any key/value combinations to bind to the logger.
        """
        if os.environ.get(OPENRELIK_LOG_TYPE, "").startswith("structlog"):
            structlog.contextvars.bind_contextvars(**kwargs)