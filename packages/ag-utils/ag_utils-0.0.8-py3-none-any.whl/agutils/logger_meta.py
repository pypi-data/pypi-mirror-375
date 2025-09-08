from __future__ import annotations

from datetime import datetime
from functools import wraps
from inspect import iscoroutinefunction
from logging import (CRITICAL, DEBUG, ERROR, INFO, WARN, WARNING, FileHandler,
                     Formatter, Handler, Logger, LoggerAdapter, LogRecord,
                     StreamHandler)
from logging.handlers import (HTTPHandler, QueueHandler, RotatingFileHandler,
                              SMTPHandler, SocketHandler,
                              TimedRotatingFileHandler)
from sys import stdout
from typing import Iterable, List, Literal, Tuple
from uuid import uuid4

from .classproperty import classproperty
from .colored_message import ColoredConsoleMessage as CCM


class ColoredLogger(Logger):
    COLORS = dict(
        DEBUG = CCM.BLUE,
        INFO = CCM.RESET,
        WARN = CCM.YELLOW,
        WARNING = CCM.YELLOW,
        ERROR = CCM.RED,
        CRITICAL = CCM.RED
    )

    def callHandlers(self, record:LogRecord) -> None:
        color = self.COLORS.get(record.levelname, CCM.RESET)
        CCM.set(color)
        super().callHandlers(record)
        CCM.reset()


class LogMeta(type):


    class DefaultConfig:
        cls = ColoredLogger
        level = INFO
        handlers = [StreamHandler(stdout)]
        fmt = Formatter(
            style='{',
            datefmt='%Y-%m-%d %H:%M:%S',
            fmt='{asctime} - {levelname} - {LoggerName} - {message}'
        )

    def __init__(self, name:str, bases:Tuple, params:dict):
        self._logger = self.__config_logger(name, params)
        self._logger_a = LoggerAdapter(self._logger, {"LoggerName": name})
        super(LogMeta, self).__init__(name, bases, params)

    def __call__(self, *args, **kwargs) -> LogMeta:
        raise ValueError('Cannot create instance')

    def __config_logger(self, name, params:dict) -> Logger:
        config = params.get('Config', self.DefaultConfig)

        cls = getattr(config, 'cls', self.DefaultConfig.cls)
        if not isinstance(cls, type) and cls != Logger and Logger not in cls.__bases__:
            cls = self.DefaultConfig.cls

        level = getattr(config, 'level', self.DefaultConfig.level)
        if level not in [DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL]:
            level = self.DefaultConfig.level

        fmt = getattr(config, 'fmt', self.DefaultConfig.fmt)
        if not isinstance(fmt, Formatter):
            fmt = self.DefaultConfig.fmt

        handlers = getattr(config, 'handlers', self.DefaultConfig.handlers)
        if not isinstance(handlers, Iterable):
            handlers = self.DefaultConfig.handlers


        logger = cls(name=f'{name}.{uuid4().hex}.meta', level=level)
        for h in handlers:
            if not isinstance(h, Handler):
                continue
            h.setLevel(level)
            h.setFormatter(fmt)
            logger.addHandler(h)
        return logger

    def debug(self, message:object, *args, **kwargs):
        stacklevel = kwargs.get('stacklevel', 2)
        kwargs.update(stacklevel=stacklevel)
        self._logger_a.debug(message, *args, **kwargs)

    def info(self, message:object, *args, **kwargs):
        stacklevel = kwargs.get('stacklevel', 2)
        kwargs.update(stacklevel=stacklevel)
        self._logger_a.info(message, *args, **kwargs)

    def warning(self, message:object, *args, **kwargs):
        stacklevel = kwargs.get('stacklevel', 2)
        kwargs.update(stacklevel=stacklevel)
        self._logger_a.warning(message, *args, **kwargs)

    def error(self, message:object, *args, **kwargs):
        stacklevel = kwargs.get('stacklevel', 2)
        kwargs.update(stacklevel=stacklevel)
        self._logger_a.error(message, *args, **kwargs)

    def critical(self, message:object, *args, **kwargs):
        stacklevel = kwargs.get('stacklevel', 2)
        kwargs.update(stacklevel=stacklevel)
        self._logger_a.critical(message, *args, **kwargs)

class LogLevels:
    DEBUG = DEBUG
    INFO = INFO
    WARN = WARN
    WARNING = WARNING
    ERROR = ERROR
    CRITICAL = CRITICAL

class Handlers:
    StreamHandler = StreamHandler
    FileHandler = FileHandler
    RotatingFileHandler = RotatingFileHandler
    TimedRotatingFileHandler = TimedRotatingFileHandler
    SocketHandler = SocketHandler
    HTTPHandler = HTTPHandler
    QueueHandler = QueueHandler
    SMTPHandlers = SMTPHandler


class LoggerBase(metaclass=LogMeta):

    @classproperty
    def level(cls) -> LogLevels:
        return LogLevels

    @classproperty
    def handler(cls) -> Handlers:
        return Handlers

    @classmethod
    def error_handler(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                cls.error(ex, stacklevel=2)
                raise ex
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as ex:
                cls.error(ex, stacklevel=2)
                raise ex
        return async_wrapper if iscoroutinefunction(func) else wrapper

    @classmethod
    def __getattribute(cls, func):
        @wraps(func)
        def wrapper(self, name:str):
            result = func(self, name)
            if callable(result):
                result = cls.error_handler(result)
            return result
        return wrapper

    @classmethod
    def inject(cls, obj:type):
        if not isinstance(obj, type):
            cls.warning(f'Cannot inject to {obj}. Value must be `type`')
            return
        try:
            obj.__getattribute__ = cls.__getattribute(obj.__getattribute__)
        except Exception as ex:
            cls.warning(f'Cannot inject to {obj}. {ex}')

    @classmethod
    def wrap(cls, obj:type):
        if isinstance(obj, type):
            cls.inject(obj)
            return obj
        if callable(obj):
            return cls.error_handler(obj)
        return obj

    class Config:
        level = INFO
        handlers = [StreamHandler(stdout)]
        fmt = Formatter(
            style='{',
            datefmt='%Y-%m-%d %H:%M:%S',
            fmt='{asctime} - {levelname} - {LoggerName} - {message}'
        )


class AgUtilsLog(LoggerBase):
    class Config:
        fmt = Formatter(
            style='{',
            datefmt='%Y-%m-%d %H:%M:%S',
            fmt='[{LoggerName}::{levelname}] {message}'
        )