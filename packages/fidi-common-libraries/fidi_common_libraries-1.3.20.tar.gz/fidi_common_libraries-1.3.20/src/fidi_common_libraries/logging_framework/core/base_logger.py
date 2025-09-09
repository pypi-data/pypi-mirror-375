"""Logger base universal para aplicações enterprise DATAMETRIA.

Este módulo implementa o sistema de logging universal seguindo as diretrizes
DATAMETRIA com suporte a sanitização, contexto automático e especialização
por domínio.
"""

import logging
import threading
import time
import uuid
import re
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union


class LogLevel(Enum):
    """Níveis de log universais DATAMETRIA."""
    TRACE = 5       # Rastreamento muito detalhado
    DEBUG = 10      # Debug padrão
    INFO = 20       # Informações gerais
    SUCCESS = 22    # Operações bem-sucedidas
    WARNING = 30    # Avisos
    ERROR = 40      # Erros
    CRITICAL = 50   # Erros críticos
    AUDIT = 60      # Logs de auditoria
    SECURITY = 70   # Eventos de segurança


class LogCategory(Enum):
    """Categorias de log por domínio DATAMETRIA."""
    AUTOMATION = "automation"
    DATABASE = "database"
    API = "api"
    WEB = "web"
    SECURITY = "security"
    BUSINESS = "business"
    SYSTEM = "system"
    PERFORMANCE = "performance"
    AUDIT = "audit"


def _sanitize_for_log(value: str) -> str:
    """Sanitiza entrada para logs removendo caracteres perigosos.
    
    Args:
        value (str): Valor a ser sanitizado.
        
    Returns:
        str: Valor sanitizado seguro para logs.
    """
    if not isinstance(value, str):
        value = str(value)
    # Remove quebras de linha e caracteres de controle
    return re.sub(r'[\r\n\x00-\x1f\x7f-\x9f]', '', value)


class BaseLogger(ABC):
    """Logger base universal para todos os domínios DATAMETRIA.
    
    Esta classe implementa o sistema de logging enterprise seguindo as
    diretrizes DATAMETRIA com sanitização automática, contexto rico e
    especialização por domínio.
    
    Attributes:
        name (str): Nome do logger.
        category (LogCategory): Categoria do domínio.
        enable_correlation (bool): Se deve usar correlation IDs.
        enable_metrics (bool): Se deve coletar métricas.
        
    Example:
        Implementação de logger especializado:
        
        >>> class MyLogger(BaseLogger):
        ...     def _setup_logging_infrastructure(self):
        ...         # Configurar handlers específicos
        ...         pass
        >>> 
        >>> logger = MyLogger("my_app", LogCategory.AUTOMATION)
        >>> with logger.operation("test_operation"):
        ...     logger.info("Operação executada")
    """
    
    def __init__(
        self,
        name: str,
        category: LogCategory,
        level: Union[LogLevel, int, str] = LogLevel.INFO,
        enable_correlation: bool = True,
        enable_metrics: bool = True,
        enable_performance_tracking: bool = True,
        custom_context: Optional[Dict[str, Any]] = None
    ):
        """Inicializa o logger base.
        
        Args:
            name (str): Nome do logger.
            category (LogCategory): Categoria do domínio.
            level (Union[LogLevel, int, str], optional): Nível de log.
                Defaults to LogLevel.INFO.
            enable_correlation (bool, optional): Se deve usar correlation IDs.
                Defaults to True.
            enable_metrics (bool, optional): Se deve coletar métricas.
                Defaults to True.
            enable_performance_tracking (bool, optional): Se deve rastrear performance.
                Defaults to True.
            custom_context (Dict[str, Any], optional): Contexto customizado.
                Defaults to None.
        """
        self.name = name
        self.category = category
        self.enable_correlation = enable_correlation
        self.enable_metrics = enable_metrics
        self.enable_performance_tracking = enable_performance_tracking
        
        # Configurar logger interno
        self.logger = logging.getLogger(f"{category.value}.{name}")
        self.logger.setLevel(self._convert_level(level))
        
        # Contexto thread-local
        self._context = threading.local()
        self._custom_context = custom_context or {}
        
        # Configurar infraestrutura
        self._setup_logging_infrastructure()
        
        self.info(f"{category.value.title()}Logger '{name}' inicializado")
    
    @abstractmethod
    def _setup_logging_infrastructure(self):
        """Configura handlers e formatters específicos do domínio.
        
        Este método deve ser implementado por cada logger especializado
        para configurar seus handlers, formatters e filtros específicos.
        """
        pass
    
    def _convert_level(self, level: Union[LogLevel, int, str]) -> int:
        """Converte nível de log para valor inteiro.
        
        Args:
            level (Union[LogLevel, int, str]): Nível a ser convertido.
            
        Returns:
            int: Valor inteiro do nível.
        """
        if isinstance(level, LogLevel):
            return level.value
        elif isinstance(level, str):
            return getattr(logging, level.upper(), logging.INFO)
        return level
    
    @contextmanager
    def context(self, **context_data):
        """Context manager para adicionar contexto temporário.
        
        Args:
            **context_data: Dados de contexto a serem adicionados.
            
        Example:
            >>> with logger.context(user_id="123", session="abc"):
            ...     logger.info("Operação com contexto")
        """
        old_context = getattr(self._context, 'current_context', {})
        self._context.current_context = {**old_context, **context_data}
        
        try:
            yield
        finally:
            self._context.current_context = old_context
    
    @contextmanager
    def operation(self, operation_name: str, **operation_data):
        """Context manager para operações com tracking automático.
        
        Args:
            operation_name (str): Nome da operação.
            **operation_data: Dados adicionais da operação.
            
        Yields:
            str: ID único da operação.
            
        Example:
            >>> with logger.operation("user_login", user_id="123") as op_id:
            ...     logger.info("Processando login")
            ...     # Operação é automaticamente logada com sucesso/erro
        """
        operation_id = str(uuid.uuid4())
        start_time = time.time()
        
        context_data = {
            'operation_id': operation_id,
            'operation_name': operation_name,
            **operation_data
        }
        
        with self.context(**context_data):
            self.info(f"Iniciando operação: {operation_name}", extra={
                'event_type': 'operation_start',
                'operation_id': operation_id
            })
            
            try:
                yield operation_id
                
                duration = time.time() - start_time
                self.success(f"Operação concluída: {operation_name}", extra={
                    'event_type': 'operation_success',
                    'operation_id': operation_id,
                    'duration': duration
                })
                
            except Exception as e:
                duration = time.time() - start_time
                self.error(f"Operação falhou: {operation_name}", extra={
                    'event_type': 'operation_error',
                    'operation_id': operation_id,
                    'duration': duration,
                    'error': _sanitize_for_log(str(e)),
                    'error_type': type(e).__name__
                })
                raise
    
    def _get_enriched_extra(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enriquece dados extras com contexto automático.
        
        Args:
            extra (Dict[str, Any], optional): Dados extras fornecidos.
                Defaults to None.
                
        Returns:
            Dict[str, Any]: Dados enriquecidos com contexto.
        """
        enriched = {
            'category': self.category.value,
            'logger_name': self.name,
            'timestamp': datetime.now().isoformat(),
            **self._custom_context
        }
        
        # Adicionar contexto thread-local se disponível
        current_context = getattr(self._context, 'current_context', {})
        enriched.update(current_context)
        
        # Adicionar correlation ID se habilitado
        if self.enable_correlation and 'correlation_id' not in enriched:
            enriched['correlation_id'] = str(uuid.uuid4())
        
        # Adicionar dados extras fornecidos
        if extra:
            enriched.update(extra)
        
        return enriched
    
    def _log(self, level: int, msg: str, *args, **kwargs):
        """Método interno de log com sanitização e enriquecimento.
        
        Args:
            level (int): Nível do log.
            msg (str): Mensagem do log.
            *args: Argumentos posicionais.
            **kwargs: Argumentos nomeados.
        """
        # Sanitizar mensagem
        safe_msg = _sanitize_for_log(str(msg))
        
        # Enriquecer dados extras
        extra = kwargs.pop('extra', {})
        enriched_extra = self._get_enriched_extra(extra)
        
        # Log com dados enriquecidos
        self.logger.log(level, safe_msg, *args, extra=enriched_extra, **kwargs)
    
    # Métodos de logging públicos
    def trace(self, msg: str, *args, **kwargs):
        """Log de rastreamento detalhado."""
        self._log(LogLevel.TRACE.value, msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        """Log de debug."""
        self._log(LogLevel.DEBUG.value, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Log de informação."""
        self._log(LogLevel.INFO.value, msg, *args, **kwargs)
    
    def success(self, msg: str, *args, **kwargs):
        """Log de operação bem-sucedida."""
        self._log(LogLevel.SUCCESS.value, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log de aviso."""
        self._log(LogLevel.WARNING.value, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log de erro."""
        self._log(LogLevel.ERROR.value, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log de erro crítico."""
        self._log(LogLevel.CRITICAL.value, msg, *args, **kwargs)
    
    def audit(self, msg: str, *args, **kwargs):
        """Log de auditoria."""
        self._log(LogLevel.AUDIT.value, msg, *args, **kwargs)
    
    def security(self, msg: str, *args, **kwargs):
        """Log de segurança."""
        self._log(LogLevel.SECURITY.value, msg, *args, **kwargs)