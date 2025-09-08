from logging import FileHandler, StreamHandler
from logging.handlers import (HTTPHandler, QueueHandler, RotatingFileHandler,
                              SMTPHandler, SocketHandler,
                              TimedRotatingFileHandler)
from typing import Any, Callable, Mapping, ParamSpec, Tuple, TypeVar, overload

from .classproperty import classproperty

T = TypeVar('T')
P = ParamSpec('P')

class LogMeta(type):
    @overload
    def __init__(self, name:str, bases:Tuple, params:dict):...
    @overload
    def __call__(self, *args, **kwargs) -> LogMeta:...
    @overload
    def debug(self, msg: object, *args: object, exc_info: Any = None, stack_info: bool = False, stacklevel: int = 1, **kwargs: object) -> None:...
    @overload
    def info(self, msg: object, *args: object, exc_info: Any = None, stack_info: bool = False, stacklevel: int = 1, **kwargs: object) -> None:...
    @overload
    def warning(self, msg: object, *args: object, exc_info: Any = None, stack_info: bool = False, stacklevel: int = 1, **kwargs: object) -> None:...
    @overload
    def error(self, msg: object, *args: object, exc_info: Any = None, stack_info: bool = False, stacklevel: int = 1, **kwargs: object) -> None:...
    @overload
    def critical(self, msg: object, *args: object, exc_info: Any = None, stack_info: bool = False, stacklevel: int = 1, **kwargs: object) -> None:...

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
    """
    Class for configuring a logger without creating an instance.\n
    To use, inherit the LoggerBase class:\n
    ```
    class MainLog(LoggerBase):...
    ```
    After this you can call the class anywhere:\n
    ```
    MainLog.debug('Test message')
    ```

    To configure, define the `Config` class inside (see `DefaultConfig` in `LogMeta`)\n
        ```
        class MainLog(LoggerBase):
            class Config:
                level = DEBUG
                handlers = [
                    StreamHandler(stdout),
                    FileHandler('test.log')
                ]
                fmt = Formatter(
                    style='{',
                    datefmt='%Y:%m:%d %H:%M:%S',
                    fmt='{LoggerName} - {asctime} - {levelname} - {message}'
                )
        ```

    To use the logger name, use the variable `LoggerName`
    """

    @classproperty
    @overload
    def level(cls) -> LogLevels:...

    @classproperty
    @overload
    def handler(cls) -> Handlers:...

    @classmethod
    @overload
    def error_handler(cls, func:Callable[P, T]) -> Callable[P, T]:...

    @classmethod
    @overload
    def inject(cls, obj:type) -> None:
        """
        The function replaces and wraps the __getattribute__ method.
        ```
        class MainLog(Loggerbase):...

        class MyClass:...

        MainLog.inject(MyClass)
        ```
        When the __getattribute__ method is called, the result obtained, if it is a function, 
        is wrapped in a decorator with a try/except block:\n
        ```
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as ex:
                cls.error(ex)
                raise ex
        ```
        """

    @classmethod
    @overload
    def wrap(cls, obj:type):
        """
        Method to inject as a decorator. Calls the `inject` method on the class being decorated.\n
        ```
        class MainLog(LoggerBase):...

        @MainLog.wrap
        class MyClass:...
        ```
        """


