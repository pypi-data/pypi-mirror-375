from pydantic import BaseModel, ConfigDict


class _LoggerProperties(BaseModel):
    """
    Represents configurable properties for a logging system.

    This class provides attributes for configuring various aspects of a logging
    system such as log level, file settings, and logging outputs. It's designed
    to enforce strict rules on its attributes, and no extra or undefined attributes
    can be added.

    :ivar log_level: The logging level to be used (e.g., DEBUG, INFO, WARNING).
    :type log_level: str | None
    :ivar file_name: The name of the file where logs should be saved.
    :type file_name: str | None
    :ivar max_bytes: The maximum size in bytes for a log file before it gets
        rotated.
    :type max_bytes: int | None
    :ivar backup_count: The number of backup log files to keep after rotation.
    :type backup_count: int | None
    :ivar propagate: Specifies whether the logger should propagate log messages
        to parent loggers.
    :type propagate: bool | None
    :ivar enable_file_logging: Indicates if logging to a file should be enabled.
    :type enable_file_logging: bool | None
    :ivar enable_stdout_logging: Indicates if logging to the standard output
        should be enabled.
    :type enable_stdout_logging: bool | None
    :ivar ascii_font: The font style (represented as a string) for ASCII art in
        logged messages.
    :type ascii_font: str | None
    """
    model_config = ConfigDict(extra="forbid")  # noqa: F841

    log_level: str | None = None
    file_name: str | None = None
    max_bytes: int | None = None
    backup_count: int | None = None
    propagate: bool | None = None
    enable_file_logging: bool | None = None
    enable_stdout_logging: bool | None = None
    ascii_font: str | None = None  # noqa: F841
