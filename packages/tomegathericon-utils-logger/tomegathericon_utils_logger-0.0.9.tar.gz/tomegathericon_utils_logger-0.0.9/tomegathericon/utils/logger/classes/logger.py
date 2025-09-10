"""
Logging Framework for Application Monitoring and Diagnostics

This module provides a robust, thread-safe logging framework built on top of
Python's standard logging library. It implements a singleton logger to ensure
consistent logging behavior throughout the application.

The logger supports multiple output destinations (console and rotating files),
configurable log levels, and custom formatting. It automatically manages log
file rotation based on size limits and maintains a specified number of backup
files.

Key Features:
-------------
* Singleton design pattern ensures exactly one logger instance
* Thread-safe implementation for concurrent environments
* Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
* Rotating file handler with customizable size limits and backup counts
* Console output with the same formatting as file output
* Property-based configuration with validation
* Automatic log directory creation
* Default configuration for quick setup

Usage Example:
-------------
::

    # Get the singleton logger instance
    logger = Logger()

    # Configure the logger if needed
    logger.level = "DEBUG"
    logger.file_name = "app/logs/custom.log"
    logger.max_bytes = 5_000_000
    logger.backup_count = 5

    # Log messages at different levels
    logger.debug("Detailed information for debugging")
    logger.info("Confirmation that things are working as expected")
    logger.warning("An indication that something unexpected happened")
    logger.error("A more serious problem that prevented an operation")
    logger.critical("A serious error indicating that the program
    may be unable to continue")
"""
import logging
import os
import pathlib
import sys
import threading
from logging import Logger as _Logger
from logging import StreamHandler, getLogger
from logging.handlers import RotatingFileHandler
from typing import Any, Final

from pyfiglet import figlet_format
from tomegathericon.utils.logFormatter import LogFormatter

from ..exceptions import InvalidValueProvidedError, LoggerNotAvailableError, PropertyNotFoundError
from ._logger_properties import _LoggerProperties
from .level_filter import LevelFilter


class Logger:
    """
    A thread-safe, Singleton-based Logger class.

    This class provides configurable logging capabilities with support for multiple log
    properties such as log level, log file rotation, and custom handlers. It ensures
    there is only a single instance of the Logger in operation, using a thread-safe
    Singleton design pattern. The Logger is designed to be initialized with default
    or user-specified properties and supports modifications for certain mutable attributes.

    :ivar level_filter: The current level filter applied to the logger.
    :type level_filter: LevelFilter
    :ivar log_level: The current logging level as a string.
    :type log_level: str
    """

    _INSTANCES: dict[Any, 'Logger'] = {}
    _LOCK: threading.Lock = threading.Lock()
    __INITIALIZED: bool = False

    __LOG_LEVELS: Final[frozenset[str]] = frozenset({
        "NOTSET",
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    })

    __PROP_NAME: Final[str] = "LOGGER_NAME"
    __PROP_LEVEL: Final[str] = "LOGGER_LOG_LEVEL"
    __PROP_FILE_NAME: Final[str] = "LOGGER_FILE_NAME"
    __PROP_BACKUP_COUNT: Final[str] = "LOGGER_BACKUP_COUNT"
    __PROP_MAX_BYTES: Final[str] = "LOGGER_MAX_BYTES"
    __PROP_PROPAGATE: Final[str] = "LOGGER_PROPAGATE"
    __PROP_ENABLE_FILE_LOGGING: Final[str] = "LOGGER_ENABLE_FILE_LOGGING"
    __PROP_ENABLE_STDOUT_LOGGING: Final[str] = "LOGGER_ENABLE_STDOUT_LOGGING"
    __PROP_HANDLERS_METADATA: Final[str] = "LOGGER_HANDLERS_METADATA"
    __PROP_ASCII_FONT: Final[str] = "LOGGER_ASCII_FONT"

    __DEFAULT_LOGGER_PROPS: Final[dict[str, Any]] = {
        __PROP_NAME: "logger",
        __PROP_LEVEL: "INFO",
        __PROP_FILE_NAME: None,
        __PROP_BACKUP_COUNT: None,
        __PROP_MAX_BYTES: None,
        __PROP_PROPAGATE: False,
        __PROP_ENABLE_FILE_LOGGING: False,
        __PROP_ENABLE_STDOUT_LOGGING: True,
        __PROP_ASCII_FONT: "starwars",
        __PROP_HANDLERS_METADATA: []
    }

    __IMMUTABLE_LOGGER_PROPS: Final[frozenset[str]] = frozenset({
        __PROP_NAME,
        __PROP_FILE_NAME,
        __PROP_BACKUP_COUNT,
        __PROP_MAX_BYTES
    })

    def __new__(cls, *args: str, **kwargs: str) -> 'Logger':
        """
        Ensures a class follows the Singleton design pattern such that only one instance
        of the class can be created. This implementation uses a thread-safe lock to
        safeguard instance creation in multi-threaded environments.

        :param cls: The class for which the singleton instance is to be created.
        :type cls: type
        :param args: Positional arguments to be passed to the class constructor.
        :type args: str
        :param kwargs: Keyword arguments to be passed to the class constructor.
        :type kwargs: str
        :return: The singleton instance of the specified class.
        :rtype: object
        """
        with cls._LOCK:
            if cls not in cls._INSTANCES:
                instance = super().__new__(cls)
                cls._INSTANCES[cls] = instance
        return cls._INSTANCES[cls]

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Sets the given attribute of the object, applying specific constraints and validations
        based on its key and value. This method enforces rules for setting attributes, ensuring
        restricted attributes, mutable properties, and environment variable values are handled
        appropriately.

        :param key: The attribute name intended for assignment.
        :type key: str
        :param value: The value to be assigned to the specified attribute.
        :type value: Any
        :return: None
        :rtype: None

        :raises InvalidValueProvidedError: Raised when attempting to set an attribute
           that is not allowed based on predefined rules.
        """
        if key.startswith("_Logger_") or key in ("level_filter", "formatter"):
            super().__setattr__(key, value)
            return None
        if f"LOGGER_{key.upper()}" not in self.__DEFAULT_LOGGER_PROPS:
            raise InvalidValueProvidedError(
                f"Property {key} cannot be set, possible values: "
                f"{", ".join(sorted(self.__DEFAULT_LOGGER_PROPS.keys())).
                lower().replace("logger_", "")}")
        if (f"LOGGER_{key.upper()}" in self.__IMMUTABLE_LOGGER_PROPS and getattr(self, key)
            is not None):
            self.error(f"Property {key} is immutable "
                            f"and cannot be overridden.")
            return None
        else:
            if os.environ.get(f"LOGGER_{key.upper()}") and hasattr(self, key):
                self.debug(f"Property {key} is already set via "
                                             f"environment variable. Overriding it to {value}.")
                return super().__setattr__(key, value)
        return super().__setattr__(key, value)

    def __init__(self, props: dict[str, Any] | None = None) -> None:
        """
        Initializes the logger instance with given properties or environment-derived
        ones. The logger is configured with a formatter, specific log level filter,
        and other settings. If the properties are provided during initialization,
        they will override the defaults from the environment.

        :param props: Optional dictionary of logger properties to configure the logger.
        :type props: Optional[dict[str, Any]]
        :raises Exception: If an error occurs during initialization.
        """
        try:
            if self.__INITIALIZED:
                self.debug("Logger instance is already initialized. Cannot Reinitialize.")
                return
            self.__INITIALIZED = True
            self.__properties: dict[str, Any] = self.__get_properties_from_env()
            self.__formatter: LogFormatter = LogFormatter()
            self.__filter: LevelFilter = LevelFilter(getattr(logging, (self.__properties[self.__PROP_LEVEL]).upper()))
            self.__logger: _Logger = self.__create_logger()
            if props:
                __props: _LoggerProperties = _LoggerProperties(**props.copy())
                for key, value in __props.__dict__.items():
                    setattr(self, key, value)
        except Exception as e:
            logging.critical(f" Error occurred while initializing the Logger "
                             f"with provided properties. Exiting.\n"
                             f"Error: {e}")
            raise e

    def info(self, message: str) -> None:
        """Logs a message with the ``INFO`` level.

        :param message: The message string to log.
        :type message: str
        :return: None
        :rtype: None
        :raises PropertyNotFoundError: If the logger has not been initialized.
        """
        if self.__logger is None:
            raise LoggerNotAvailableError("Logger has not been initialized")
        self.__logger.info(message)

    def debug(self, message: str) -> None:
        """Logs a message with the ``DEBUG`` level.

        :param message: The message string to log.
        :type message: str
        :return: None
        :rtype: None
        :raises PropertyNotFoundError: If the logger has not been initialized.
        """
        if self.__logger is None:
            raise LoggerNotAvailableError("Logger has not been initialized")
        self.__logger.debug(message)

    def warning(self, message: str) -> None:
        """Logs a message with the ``WARNING`` level.

        :param message: The message string to log.
        :type message: str
        :return: None
        :rtype: None
        :raises PropertyNotFoundError: If the logger has not been initialized.
        """
        if self.__logger is None:
            raise LoggerNotAvailableError("Logger has not been initialized")
        self.__logger.warning(message)

    def error(self, message: str) -> None:
        """Logs a message with the ``ERROR`` level.

        :param message: The message string to log.
        :type message: str
        :return: None
        :rtype: None
        :raises PropertyNotFoundError: If the logger has not been initialized.
        """
        if self.__logger is None:
            raise LoggerNotAvailableError("Logger has not been initialized")
        self.__logger.error(message)

    def critical(self, message: str) -> None:
        """Logs a message with the ``CRITICAL`` level.

        :param message: The message string to log.
        :type message: str
        :return: None
        :rtype: None
        :raises PropertyNotFoundError: If the logger has not been initialized.
        """
        if self.__logger is None:
            raise LoggerNotAvailableError("Logger has not been initialized")
        self.__logger.critical(message)

    @property
    def level_filter(self) -> LevelFilter:
        """
        Gets the current logging level filter applied to the logger.

        The `level_filter` property retrieves a copy of the `LevelFilter` object
        associated with the logger. This allows for viewing the currently applied
        filter without directly exposing the original `LevelFilter` object, therefore
        preserving immutability and encapsulation.

        :return: A copy of the `LevelFilter` object currently associated with the logger.
        :rtype: LevelFilter
        """
        return self.__filter

    @level_filter.setter
    def level_filter(self, level_filter: LevelFilter) -> None:
        """
        Sets the logging level filter for the logger to customize the log output based on the provided filter settings.

        :param level_filter: A filter object determining which logging levels will pass.
        :type level_filter: LevelFilter
        :return: None
        :rtype: None

        :raises InvalidValueProvidedError: If the provided level_filter is not an instance of LevelFilter.
        :raises LoggerNotAvailableError: If the logger instance is not available.

        """
        try:
            if not isinstance(level_filter, LevelFilter):
                raise InvalidValueProvidedError("level_filter must be an instance of LevelFilter")
            self.__filter = level_filter
            self.__set_filter(self.__filter)
        except InvalidValueProvidedError as e:
            self.__logger.error(e)
            raise e
        except LoggerNotAvailableError as e:
            logging.error(e)
            raise e

    @property
    def log_level(self) -> str:
        """Get the current logging level.

        :returns: The current log level as a string.
        :rtype: str
        :raises PropertyNotFoundError: If the level property is not found in
                                        the internal properties dictionary.
        """
        if self.__PROP_LEVEL not in self.__properties:
            raise PropertyNotFoundError(f"Property {self.__PROP_LEVEL} not found")
        log_level: str = self.__properties[self.__PROP_LEVEL]
        return log_level

    @log_level.setter
    def log_level(self, value: str) -> None:
        """
        Sets the logging level to a specified value. The logging level must be one of the
        predefined valid levels; otherwise, an InvalidValueProvidedError will be raised.
        This method also updates the internal property dictionary with the new level and
        redefines the logging configuration to reflect this new level.

        :param value: The desired logging level. Must be one of the valid predefined levels.
        :type value: str
        :return: None
        :rtype: None
        :raises InvalidValueProvidedError: When the specified logging level is invalid.
        :raises LoggerNotAvailableError: When the logger is not available to handle the
            error logging properly.
        """
        try:
            if value.upper() not in self.__LOG_LEVELS:
                raise InvalidValueProvidedError(
                    f"Invalid log level: {value}. Must be one of {", ".join(sorted(self.__LOG_LEVELS)).lower()}"
                )
            self.__properties[self.__PROP_LEVEL] = value.upper()
            self.__set_level(value)
        except InvalidValueProvidedError as e:
            self.__logger.error(e)
            raise e
        except LoggerNotAvailableError as e:
            logging.error(e)
            raise e

    @property
    def file_name(self) -> str:
        """Get the log file name.

        :returns: The current log file path.
        :rtype: str
        :raises PropertyNotFoundError: If the file_name property is not found.
        """
        if self.__PROP_FILE_NAME not in self.__properties:
            raise PropertyNotFoundError(f"Property {self.__PROP_FILE_NAME} not found")
        file_name: str = self.__properties[self.__PROP_FILE_NAME]
        return file_name

    @file_name.setter
    def file_name(self, value: str) -> None:
        """
        Sets the file name property unless it is already set. If an attempt is made
        to override an already set file name, an `InvalidValueProvidedError` is raised.

        :param value:
            The file name to be set. The value should be a non-empty string.
        :type value: str
        :return: None
        :rtype: None
        """
        self.__properties[self.__PROP_FILE_NAME] = value

    @property
    def backup_count(self) -> int:
        """Get the number of backup log files to keep.

        :returns: The current backup count.
        :rtype: int
        :raises PropertyNotFoundError: If the backup_count property is not found.
        """
        if self.__PROP_BACKUP_COUNT not in self.__properties:
            raise PropertyNotFoundError(f"Property {self.__PROP_BACKUP_COUNT} not found")
        backup_count: int = self.__properties[self.__PROP_BACKUP_COUNT]
        return backup_count

    @backup_count.setter
    def backup_count(self, value: int) -> None:
        """Set the number of backup log files to keep with validation.

        :param value: The number of backup files.
        :type value: int
        :return: None
        :rtype: None
        :raises InvalidValueProvidedError: If the value is not a non-negative
                                           integer.
        """
        if not isinstance(value, int) or value < 0:
            raise InvalidValueProvidedError("Backup count must be a positive integer")
        self.__properties[self.__PROP_BACKUP_COUNT] = value

    @property
    def max_bytes(self) -> int:
        """Get the maximum size of each log file in bytes.

        :returns: The current maximum size in bytes.
        :rtype: int
        :raises PropertyNotFoundError: If the max_bytes property is not found.
        """
        if self.__PROP_MAX_BYTES not in self.__properties:
            raise PropertyNotFoundError(f"Property {self.__PROP_MAX_BYTES} not found")
        max_bytes: int = self.__properties[self.__PROP_MAX_BYTES]
        return max_bytes

    @max_bytes.setter
    def max_bytes(self, value: int) -> None:
        """Set the maximum size of each log file in bytes with validation.

        :param value: The maximum size in bytes.
        :type value: int
        :return: None
        :rtype: None
        :raises InvalidValueProvidedError: If the value is not a positive integer.
        """
        if not isinstance(value, int) or value <= 0:
            raise InvalidValueProvidedError("Max bytes must be a positive integer")
        self.__properties[self.__PROP_MAX_BYTES] = value

    @property
    def name(self) -> str:
        """Get the logger name.

        :returns: The current logger name.
        :rtype: str
        :raises PropertyNotFoundError: If the name property is not found.
        """
        if self.__PROP_NAME not in self.__properties:
            raise PropertyNotFoundError(f"Property {self.__PROP_NAME} not found")
        name: str = self.__properties[self.__PROP_NAME]
        return name

    @property
    def propagate(self) -> bool:
        """Get the propagate flag for the logger.

        :returns: True if the logger propagates to parent loggers, False otherwise.
        :rtype: bool
        :raises PropertyNotFoundError: If the propagate property is not found.
        """
        if self.__PROP_PROPAGATE not in self.__properties:
            raise PropertyNotFoundError(f"Property {self.__PROP_PROPAGATE} not found")
        propagate: bool = self.__properties[self.__PROP_PROPAGATE]
        return propagate

    @propagate.setter
    def propagate(self, value: bool) -> None:
        """Set the propagate flag for the logger with validation.

        :param value: True to propagate to parent loggers, False otherwise.
        :type value: bool
        :return: None
        :rtype: None
        :raises InvalidValueProvidedError: If the value is not a boolean.
        """
        if not isinstance(value, bool):
            raise InvalidValueProvidedError("Propagate must be a boolean value")
        self.__properties[self.__PROP_PROPAGATE] = value

    @property
    def formatter(self) -> LogFormatter:
        """Get the log formatter.

        :returns: The current log formatter.
        :rtype: LogFormatter
        """
        return self.__formatter

    @formatter.setter
    def formatter(self, formatter: LogFormatter) -> None:
        """
        Sets the log formatter for the logger and updates all existing handlers
        with the new formatter.

        :param formatter: The new log formatter to set. Must be an instance of LogFormatter.
        :type formatter: LogFormatter
        :return: None
        :rtype: None
        :raises InvalidValueProvidedError: Raised if the provided formatter is not an instance
            of LogFormatter.
        """
        if not isinstance(formatter, LogFormatter):
            raise InvalidValueProvidedError("Formatter must be an instance of LogFormatter")
        self.__formatter = formatter.__copy__()
        for handler in self.__logger.handlers:
            handler.setFormatter(formatter)

    @property
    def enable_file_logging(self) -> bool:
        """Get the enable_file_logging flag.

        :returns: True if file logging is enabled, False otherwise.
        :rtype: bool
        """
        if self.__PROP_ENABLE_FILE_LOGGING not in self.__properties:
            raise PropertyNotFoundError(f"Property {self.__PROP_ENABLE_FILE_LOGGING} not found")
        enable_file_logging: bool = self.__properties[self.__PROP_ENABLE_FILE_LOGGING]
        return enable_file_logging

    @enable_file_logging.setter
    def enable_file_logging(self, value: bool) -> None:
        """
        Sets the enable_file_logging property, allowing or disallowing logging to a file.
        When enabled, file logging is configured by setting appropriate handlers. If
        the file logging is already enabled, existing file handlers are removed before
        re-applying the property. Ensures that required file logging properties are set
        before enabling file logging.

        :param value: The new value for the enable_file_logging property.
        :type value: bool
        :return: None
        :rtype: None
        :raises InvalidValueProvidedError: Raised when the provided value is not a boolean.
        :raises PropertyNotFoundError: Raised when required file logging properties
            (file_name, backup_count, or max_bytes) are not set but enabling file logging
            is attempted.
        """
        if self.enable_file_logging and value:
            self.warning("File logging is already enabled")
            return
        if not isinstance(value, bool):
            raise InvalidValueProvidedError("Enable_file_logging must be a boolean value")
        self.__properties[self.__PROP_ENABLE_FILE_LOGGING] = value
        if value and (
            self.file_name is None or
            self.backup_count is None or
            self.max_bytes is None
        ):
            raise PropertyNotFoundError("file_name, backup_count, "
                                        "or max_bytes must be set "
                                        "for enabling file logging")
        if value:
            self.__logger.addHandler(self.__create_file_handler(self.__formatter))
        if not value:
            self.__remove_logger_handler_using_name(logger=self.__logger,
                                                    name="rotating_file")

    @property
    def enable_stdout_logging(self) -> bool:
        """Get the enable_stdout_logging flag.

        :returns: True if stdout logging is enabled, False otherwise.
        :rtype: bool
        """
        if self.__PROP_ENABLE_STDOUT_LOGGING not in self.__properties:
            raise PropertyNotFoundError(f"Property {self.__PROP_ENABLE_STDOUT_LOGGING} not found")
        enable_stdout_logging: bool = self.__properties[self.__PROP_ENABLE_STDOUT_LOGGING]
        return enable_stdout_logging

    @enable_stdout_logging.setter
    def enable_stdout_logging(self, value: bool) -> None:
        """
        Setter method for the `enable_stdout_logging` property.

        This method sets the value for the `enable_stdout_logging` property,
        validating that the provided value is a boolean. Depending on the provided
        value, it configures or removes a handler for logging to the standard output.

        :param value: A boolean value indicating whether to enable or disable stdout
                      logging.
        :type value: bool
        :return: None
        :rtype: None
        :raises InvalidValueProvidedError: If the provided value is not a boolean.
        """
        if not isinstance(value, bool):
            raise InvalidValueProvidedError("Enable_stdout_logging must be a boolean value")
        if self.enable_stdout_logging and value:
            self.warning("STDOUT logging is already enabled")
            return
        self.__properties[self.__PROP_ENABLE_STDOUT_LOGGING] = value
        if value:
            self.__logger.addHandler(self.__create_stdout_handler(self.__formatter))
        if not value:
            self.__remove_logger_handler_using_name(logger=self.__logger,
                                                    name="stdout")

    def __set_filter(self, value: LevelFilter) -> None:
        """
        Sets the filter for the logger's handlers to the provided `value`. Clears any
        existing filters and applies the new one if a logger instance is available.

        :param value: A new filter of type `LevelFilter` to be applied to all the
            logger's handlers.
        :type value: LevelFilter
        :return: None
        :rtype: None
        :raises LoggerNotAvailableError: If the logger is not available.
        """
        if not self.__logger:
            logging.error("Logger is not available")
            raise LoggerNotAvailableError("Logger is not available")
        for handler in self.__logger.handlers[:]:
            handler.filters.clear()
            handler.addFilter(self.__filter)

    def __set_level(self, value: str) -> None:
        """
        Sets the logging level for the logger and its associated handlers. Clears
        all existing filters and applies a custom filter to each handler.

        :param value: Logging level to be set. Accepted values are case insensitive
                      and should correspond to valid logging levels (e.g., "DEBUG",
                      "INFO", "WARNING", etc.).
        :type value: str
        :return: None
        :rtype: None
        :raises LoggerNotAvailableError: If the logger is not available.
        """
        if not self.__logger:
            logging.error("Logger is not available")
            raise LoggerNotAvailableError("Logger is not available")
        self.__logger.setLevel(value.upper())
        if self.__logger.handlers:
            for handler in self.__logger.handlers:
                handler.setLevel(value.upper())
                handler.filters.clear()
                handler.addFilter(self.__filter)

    def __create_logger(self) -> _Logger:
        """
        Creates and configures a logger instance with default properties.

        This method initializes a logger with a specified name, log level, and logger
        handlers. It utilizes the application's predefined properties for consistent
        configuration. The logger is equipped with additional filters and debug-level
        logging information.

        :return: Configured logger instance
        :rtype: _Logger
        """
        root_logger: _Logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addFilter(self.__filter)
        logging.debug("Initializing Logger with Default Properties\n")
        logging.debug(f"\n{figlet_format(self.__properties[self.__PROP_NAME],
                                              font=self.__properties[self.__PROP_ASCII_FONT])}\n")
        log_level = self.__properties[self.__PROP_LEVEL]
        self.__logger = getLogger(self.__properties[self.__PROP_NAME])
        logging.debug(f"Logger Name set to: {self.__properties[self.__PROP_NAME]}\n")
        self.__logger.propagate = self.__properties[self.__PROP_PROPAGATE]
        self.__set_level(log_level)
        logging.debug(f"Logger Level set to: {log_level.upper()}\n")
        self.__add_handlers()
        logging.debug("Logger Initialized with Default Properties\n")
        self.debug("Switched to Logger Instance")
        return self.__logger

    def __create_file_handler(self, fmt: LogFormatter) -> RotatingFileHandler:
        """
        Creates and returns a `RotatingFileHandler` configured with the provided
        formatter and specific handler properties. Ensures the directory for the log
        file exists before initializing the handler. This method either reuses an
        existing file handler that matches its name or creates a new one.

        :param fmt: Log formatter to apply to the log records handled by the file handler.
        :type fmt: LogFormatter
        :return: A configured `RotatingFileHandler` object.
        :rtype: RotatingFileHandler
        """
        pathlib.Path(self.file_name).parent.mkdir(parents=True, exist_ok=True)
        file_handler: RotatingFileHandler = next((handler for handler
                                              in self.__properties[self.__PROP_HANDLERS_METADATA]
                                              if handler.name == "rotating_file"),
                                                RotatingFileHandler(filename=self.file_name,
                                               backupCount=int(self.backup_count),
                                               maxBytes=int(self.max_bytes),
                                               ))
        file_handler.name = "rotating_file"
        file_handler.setFormatter(fmt.__copy__())
        file_handler.addFilter(self.__filter)
        file_handler.setLevel(self.log_level.upper())
        self.__properties[self.__PROP_HANDLERS_METADATA].append(file_handler)
        return file_handler

    def __create_stdout_handler(self, fmt: LogFormatter) -> StreamHandler[Any]:
        """Creates and configures a ``StreamHandler`` for standard output.

        This private method sets up a handler that sends log messages to
        ``sys.stdout``.

        :param fmt: The formatter to be used for the handler.
        :type fmt: LogFormatter
        :returns: A configured ``StreamHandler`` instance.
        :rtype: StreamHandler
        """
        stdout_handler: StreamHandler[Any] = next((handler for handler
                                          in self.__properties[self.__PROP_HANDLERS_METADATA]
                                          if handler.name == "stdout"),
                                          StreamHandler(stream=sys.stdout))
        stdout_handler.name = "stdout"
        stdout_handler.setFormatter(fmt.__copy__())
        stdout_handler.setLevel(self.log_level.upper())
        stdout_handler.addFilter(self.__filter)
        self.__properties[self.__PROP_HANDLERS_METADATA].append(stdout_handler)
        return stdout_handler

    def __add_handlers(self) -> None:
        """
        Adds logging handlers based on specified properties. This method configures
        handlers to enable file and/or stdout logging if these options are set
        in the respective properties.

        :return: None
        :rtype: None
        """
        if self.__properties[self.__PROP_ENABLE_FILE_LOGGING]:
            self.__logger.addHandler(self.__create_file_handler(self.__formatter))
        if self.__properties[self.__PROP_ENABLE_STDOUT_LOGGING]:
            self.__logger.addHandler(self.__create_stdout_handler(self.__formatter))

    def __remove_logger_handler_using_name(self, **kwargs: Any) -> None:
        """
        Removes a logger handler by its name from the specified logger.

        This method identifies a logger handler with the provided name and removes it
        from the given logger. If no appropriate handler is found, no action is taken.
        A debug message will be logged if the handler is successfully removed.

        :param kwargs: Dictionary containing the following keys:
                       - ``name`` (str): The name of the handler to remove.
                       - ``logger`` (_Logger): The logger from which the handler
                         will be removed.
        :type kwargs: Any
        :raises InvalidValueProvidedError: If the ``name`` or ``logger`` is not
                                            provided or is invalid.
        :return: None
        :rtype: None
        """
        args: dict[str, Any] = kwargs.copy()
        __name: str = args.get("name", "")
        __logger: _Logger | None = args.get("logger", None)
        if __name is None or __logger is None:
            raise InvalidValueProvidedError("Name and logger must be provided")
        for handler in __logger.handlers:
            if handler.name == __name:
                __logger.removeHandler(handler)
                self.debug(f"Removed Handler {__name} from {__logger.name}")
                break
        for prop_handler in self.__properties[self.__PROP_HANDLERS_METADATA][:]:
            if prop_handler is not None and prop_handler.name == __name:
                self.__properties[self.__PROP_HANDLERS_METADATA].remove(prop_handler)

    def __get_properties_from_env(self) -> dict[str, Any]:
        """
        Retrieves properties for the logger from the environment variables. If a property is not found
        in the environment variables, it will default to the predefined value in
        `__DEFAULT_LOGGER_PROPS`. The retrieved properties are returned as a dictionary, with any
        Boolean strings ("True"/"False") or values replaced with the appropriate Python Boolean types.

        :return: A dictionary containing properties for the logger with their respective values,
            fetched from the environment variables or defaulted to their predefined values.
        :rtype: dict[str, Any]
        """
        __properties: dict[str, Any] = {}
        for key, value in self.__DEFAULT_LOGGER_PROPS.copy().items():
            if os.environ.get(key):
                __properties[key] = os.environ.get(key)
                if __properties[key] in ["True", "true", True]:
                    __properties[key] = True
                if __properties[key] in ["False", "false", False]:
                    __properties[key] = False
            else:
                __properties[key] = value
        return __properties
