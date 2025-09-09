"""Framework de Logging Universal DATAMETRIA.

Sistema de logging enterprise-grade que cobre todos os domínios de aplicação:
automação UI, APIs, banco de dados, aplicações web, segurança e auditoria.

Example:
    Uso básico do framework:
    
    >>> from fidi_common_libraries.logging_framework import get_automation_logger
    >>> logger = get_automation_logger("ui_automation")
    >>> 
    >>> with logger.operation("login_process"):
    ...     logger.info("Iniciando processo de login")
    ...     # ... lógica de automação ...
    ...     logger.success("Login realizado com sucesso")
"""

from .core.logger_factory import (
    LoggerFactory,
    get_automation_logger,
    get_database_logger,
    get_api_logger,
    get_web_logger,
    get_security_logger
)
from .core.base_logger import LogLevel, LogCategory

__version__ = "1.3.20"
__all__ = [
    "LoggerFactory",
    "get_automation_logger",
    "get_database_logger", 
    "get_api_logger",
    "get_web_logger",
    "get_security_logger",
    "LogLevel",
    "LogCategory"
]