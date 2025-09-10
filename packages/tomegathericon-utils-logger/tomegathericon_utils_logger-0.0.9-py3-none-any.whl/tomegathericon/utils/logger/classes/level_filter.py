import logging


class LevelFilter(logging.Filter):
    """
    Filters log records based on a specified minimum logging level.

    This filter allows only those log records whose severity level is
    equal to or greater than the specified level. It is useful for
    customizing log handling by providing control over what levels of
    log messages are processed or ignored.

    :ivar __level: Minimum logging level allowed by the filter.
    :type __level: int
    """
    __DEFAULT_LEVEL = logging.INFO

    def __init__(self, level: int = __DEFAULT_LEVEL) -> None:
        """Initializes the filter with the specified minimum logging level.

        The filter will allow any log record with a level equal to or greater
        than this level to pass through.

        :param level: The minimum log level to capture.
        :type level: int
        """
        self.__level = level
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        """Determines if a log record should be passed to the handler.

        This method checks the severity level of the given log record
        against the filter's own level.

        :param record: The log record to be filtered.
        :type record: logging.LogRecord
        :return: ``True`` if the log record's level is at or above the filter's
                 level, and ``False`` otherwise.
        :rtype: bool
        """
        return record.levelno >= self.__level
