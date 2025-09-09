"""Factory para criação de loggers especializados DATAMETRIA."""

from typing import Type, Dict, Any, Optional, Union
from .base_logger import BaseLogger, LogCategory, LogLevel


class LoggerFactory:
    """Factory para criação de loggers especializados DATAMETRIA.
    
    Esta classe gerencia a criação e cache de loggers especializados,
    garantindo que cada combinação categoria/nome tenha uma única instância.
    
    Example:
        Uso da factory:
        
        >>> factory = LoggerFactory()
        >>> logger = factory.get_logger("my_app", LogCategory.AUTOMATION)
        >>> # Mesma instância será retornada em chamadas subsequentes
        >>> same_logger = factory.get_logger("my_app", LogCategory.AUTOMATION)
        >>> assert logger is same_logger
    """
    
    _logger_classes: Dict[LogCategory, Type[BaseLogger]] = {}
    _instances: Dict[str, BaseLogger] = {}
    
    @classmethod
    def register_logger_class(cls, category: LogCategory, logger_class: Type[BaseLogger]):
        """Registra uma classe de logger para uma categoria.
        
        Args:
            category (LogCategory): Categoria do domínio.
            logger_class (Type[BaseLogger]): Classe do logger especializado.
            
        Example:
            >>> class MyAutomationLogger(BaseLogger):
            ...     def _setup_logging_infrastructure(self):
            ...         pass
            >>> 
            >>> LoggerFactory.register_logger_class(
            ...     LogCategory.AUTOMATION, 
            ...     MyAutomationLogger
            ... )
        """
        cls._logger_classes[category] = logger_class
    
    @classmethod
    def get_logger(
        cls,
        name: str,
        category: LogCategory,
        level: Union[LogLevel, int, str] = LogLevel.INFO,
        **kwargs
    ) -> BaseLogger:
        """Obtém ou cria um logger especializado.
        
        Args:
            name (str): Nome do logger.
            category (LogCategory): Categoria do domínio.
            level (Union[LogLevel, int, str], optional): Nível de log.
                Defaults to LogLevel.INFO.
            **kwargs: Argumentos adicionais para o logger.
            
        Returns:
            BaseLogger: Instância do logger especializado.
            
        Example:
            >>> logger = LoggerFactory.get_logger(
            ...     "ui_automation", 
            ...     LogCategory.AUTOMATION,
            ...     level=LogLevel.DEBUG
            ... )
        """
        logger_key = f"{category.value}_{name}"
        
        if logger_key not in cls._instances:
            logger_class = cls._logger_classes.get(category)
            
            if not logger_class:
                logger_class = cls._import_logger_class(category)
                cls._logger_classes[category] = logger_class
            
            cls._instances[logger_key] = logger_class(
                name=name,
                category=category,
                level=level,
                **kwargs
            )
        
        return cls._instances[logger_key]
    
    @classmethod
    def _import_logger_class(cls, category: LogCategory) -> Type[BaseLogger]:
        """Importa dinamicamente a classe de logger para uma categoria.
        
        Args:
            category (LogCategory): Categoria do domínio.
            
        Returns:
            Type[BaseLogger]: Classe do logger especializado.
            
        Raises:
            ImportError: Se não conseguir importar a classe.
        """
        try:
            if category == LogCategory.AUTOMATION:
                from ..specialized.automation_logger import AutomationLogger
                return AutomationLogger
            elif category == LogCategory.DATABASE:
                from ..specialized.database_logger import DatabaseLogger
                return DatabaseLogger
            elif category == LogCategory.API:
                from ..specialized.api_logger import APILogger
                return APILogger
            elif category == LogCategory.WEB:
                from ..specialized.web_logger import WebLogger
                return WebLogger
            elif category == LogCategory.SECURITY:
                from ..specialized.security_logger import SecurityLogger
                return SecurityLogger
            else:
                # Fallback para logger genérico
                from .generic_logger import GenericLogger
                return GenericLogger
        except ImportError:
            # Fallback para logger genérico se especializado não existir
            from .generic_logger import GenericLogger
            return GenericLogger


# Funções de conveniência para criação de loggers
def get_automation_logger(name: str, **kwargs) -> BaseLogger:
    """Obtém logger de automação.
    
    Args:
        name (str): Nome do logger.
        **kwargs: Argumentos adicionais.
        
    Returns:
        BaseLogger: Logger de automação.
        
    Example:
        >>> logger = get_automation_logger("ui_test")
        >>> logger.info("Iniciando automação")
    """
    return LoggerFactory.get_logger(name, LogCategory.AUTOMATION, **kwargs)


def get_database_logger(name: str, **kwargs) -> BaseLogger:
    """Obtém logger de banco de dados.
    
    Args:
        name (str): Nome do logger.
        **kwargs: Argumentos adicionais.
        
    Returns:
        BaseLogger: Logger de banco de dados.
        
    Example:
        >>> logger = get_database_logger("main_db")
        >>> logger.info("Conectando ao banco")
    """
    return LoggerFactory.get_logger(name, LogCategory.DATABASE, **kwargs)


def get_api_logger(name: str, **kwargs) -> BaseLogger:
    """Obtém logger de API.
    
    Args:
        name (str): Nome do logger.
        **kwargs: Argumentos adicionais.
        
    Returns:
        BaseLogger: Logger de API.
        
    Example:
        >>> logger = get_api_logger("rest_api")
        >>> logger.info("Processando requisição")
    """
    return LoggerFactory.get_logger(name, LogCategory.API, **kwargs)


def get_web_logger(name: str, **kwargs) -> BaseLogger:
    """Obtém logger web.
    
    Args:
        name (str): Nome do logger.
        **kwargs: Argumentos adicionais.
        
    Returns:
        BaseLogger: Logger web.
        
    Example:
        >>> logger = get_web_logger("webapp")
        >>> logger.info("Usuário logado")
    """
    return LoggerFactory.get_logger(name, LogCategory.WEB, **kwargs)


def get_security_logger(name: str, **kwargs) -> BaseLogger:
    """Obtém logger de segurança.
    
    Args:
        name (str): Nome do logger.
        **kwargs: Argumentos adicionais.
        
    Returns:
        BaseLogger: Logger de segurança.
        
    Example:
        >>> logger = get_security_logger("auth_system")
        >>> logger.security("Tentativa de login suspeita")
    """
    return LoggerFactory.get_logger(name, LogCategory.SECURITY, **kwargs)