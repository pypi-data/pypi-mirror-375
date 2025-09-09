"""Logger especializado para operações de API DATAMETRIA."""

import logging
import json
from typing import Any, Dict, Optional
from contextlib import contextmanager

from ..core.base_logger import BaseLogger, LogCategory, LogLevel, _sanitize_for_log


class APILogger(BaseLogger):
    """Logger especializado para operações de API.
    
    Este logger fornece funcionalidades específicas para logging de requisições
    HTTP, respostas, autenticação e métricas de API.
    
    Attributes:
        slow_request_threshold (float): Threshold para requisições lentas.
        log_request_body (bool): Se deve logar corpo das requisições.
        log_response_body (bool): Se deve logar corpo das respostas.
        max_body_size (int): Tamanho máximo do corpo para log.
        
    Example:
        Uso em APIs:
        
        >>> logger = APILogger("rest_api", slow_request_threshold=2.0)
        >>> logger.log_request(
        ...     "POST",
        ...     "/api/users",
        ...     status_code=201,
        ...     duration=0.5,
        ...     user_id="123"
        ... )
    """
    
    def __init__(self, name: str, **kwargs):
        """Inicializa o logger de API.
        
        Args:
            name (str): Nome do logger.
            **kwargs: Argumentos adicionais incluindo:
                - slow_request_threshold (float): Threshold para requisições lentas
                - log_request_body (bool): Se deve logar corpo das requisições
                - log_response_body (bool): Se deve logar corpo das respostas
                - max_body_size (int): Tamanho máximo do corpo para log
        """
        self.slow_request_threshold = kwargs.pop('slow_request_threshold', 2.0)
        self.log_request_body = kwargs.pop('log_request_body', False)
        self.log_response_body = kwargs.pop('log_response_body', False)
        self.max_body_size = kwargs.pop('max_body_size', 1000)
        super().__init__(name, LogCategory.API, **kwargs)
    
    def _setup_logging_infrastructure(self):
        """Configura handlers específicos para API."""
        # Evitar duplicação de handlers
        if self.logger.handlers:
            return
            
        # Handler de console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # Formatter para API
        formatter = logging.Formatter(
            '%(asctime)s - [API] %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Handler de arquivo para API
        try:
            file_handler = logging.FileHandler('logs/api.log', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except (OSError, IOError):
            # Se não conseguir criar arquivo, continua apenas com console
            pass
        
        self.logger.addHandler(console_handler)
        self.logger.propagate = False
    
    def log_request(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None,
        duration: Optional[float] = None,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        request_body: Any = None,
        response_body: Any = None,
        headers: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        **extra_data
    ):
        """Loga uma requisição de API.
        
        Args:
            method (str): Método HTTP (GET, POST, etc.).
            url (str): URL da requisição.
            status_code (int, optional): Código de status HTTP.
            duration (float, optional): Duração da requisição em segundos.
            request_size (int, optional): Tamanho da requisição em bytes.
            response_size (int, optional): Tamanho da resposta em bytes.
            user_agent (str, optional): User agent do cliente.
            ip_address (str, optional): IP do cliente.
            user_id (str, optional): ID do usuário autenticado.
            endpoint (str, optional): Endpoint da API.
            request_body (Any, optional): Corpo da requisição.
            response_body (Any, optional): Corpo da resposta.
            headers (Dict[str, str], optional): Headers da requisição.
            query_params (Dict[str, Any], optional): Parâmetros de query.
            error (Exception, optional): Exceção se houver erro.
            **extra_data: Dados adicionais.
            
        Example:
            >>> logger.log_request(
            ...     "POST",
            ...     "/api/users",
            ...     status_code=201,
            ...     duration=0.5,
            ...     user_id="123",
            ...     ip_address="192.168.1.100"
            ... )
        """
        success = status_code and 200 <= status_code < 400
        
        # Determinar nível de log
        if not success or error:
            level = LogLevel.ERROR
        elif duration and duration > self.slow_request_threshold:
            level = LogLevel.WARNING
        else:
            level = LogLevel.SUCCESS
        
        # Construir mensagem
        message = f"{method} {url}"
        if status_code:
            message += f" - {status_code}"
        if duration:
            message += f" ({duration:.3f}s)"
        
        # Dados extras para o log
        log_extra = {
            'event_type': 'api_request',
            'http_method': method,
            'url': _sanitize_for_log(url),
            'endpoint': endpoint,
            'status_code': status_code,
            'duration': duration,
            'request_size': request_size,
            'response_size': response_size,
            'user_agent': _sanitize_for_log(user_agent) if user_agent else None,
            'ip_address': ip_address,
            'user_id': user_id,
            'success': success,
            'is_slow_request': duration and duration > self.slow_request_threshold,
            **extra_data
        }
        
        # Adicionar corpo da requisição se habilitado
        if self.log_request_body and request_body:
            log_extra['request_body'] = self._sanitize_body(request_body)
        
        # Adicionar corpo da resposta se habilitado
        if self.log_response_body and response_body:
            log_extra['response_body'] = self._sanitize_body(response_body)
        
        # Adicionar headers sanitizados
        if headers:
            log_extra['headers'] = self._sanitize_headers(headers)
        
        if query_params:
            log_extra['query_params'] = query_params
        
        if error:
            log_extra['error'] = _sanitize_for_log(str(error))
            log_extra['error_type'] = type(error).__name__
        
        self._log(level.value, message, extra=log_extra)
    
    @contextmanager
    def request_context(
        self,
        method: str,
        url: str,
        user_id: Optional[str] = None,
        **extra_context
    ):
        """Context manager para requisições de API.
        
        Args:
            method (str): Método HTTP.
            url (str): URL da requisição.
            user_id (str, optional): ID do usuário.
            **extra_context: Contexto adicional.
            
        Example:
            >>> with logger.request_context("POST", "/api/users", user_id="123"):
            ...     logger.info("Processando criação de usuário")
        """
        context_data = {
            'http_method': method,
            'url': _sanitize_for_log(url),
            'user_id': user_id,
            **extra_context
        }
        
        with self.context(**context_data):
            yield
    
    def log_authentication(
        self,
        auth_type: str,
        user_id: Optional[str] = None,
        success: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
        **extra_data
    ):
        """Loga eventos de autenticação de API.
        
        Args:
            auth_type (str): Tipo de autenticação (bearer, basic, etc.).
            user_id (str, optional): ID do usuário.
            success (bool, optional): Se a autenticação foi bem-sucedida.
                Defaults to True.
            ip_address (str, optional): IP do cliente.
            user_agent (str, optional): User agent do cliente.
            failure_reason (str, optional): Razão da falha se houver.
            **extra_data: Dados adicionais.
            
        Example:
            >>> logger.log_authentication(
            ...     "bearer",
            ...     user_id="123",
            ...     success=True,
            ...     ip_address="192.168.1.100"
            ... )
        """
        level = LogLevel.SUCCESS if success else LogLevel.WARNING
        
        message = f"API Auth {auth_type}: {user_id or 'anonymous'}"
        if not success:
            message += f" - Failed"
            if failure_reason:
                message += f" ({failure_reason})"
        
        log_extra = {
            'event_type': 'api_authentication',
            'auth_type': auth_type,
            'user_id': user_id,
            'success': success,
            'ip_address': ip_address,
            'user_agent': _sanitize_for_log(user_agent) if user_agent else None,
            'failure_reason': failure_reason,
            **extra_data
        }
        
        self._log(level.value, message, extra=log_extra)
    
    def log_rate_limit(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        limit: Optional[int] = None,
        remaining: Optional[int] = None,
        reset_time: Optional[int] = None,
        **extra_data
    ):
        """Loga eventos de rate limiting.
        
        Args:
            user_id (str, optional): ID do usuário.
            ip_address (str, optional): IP do cliente.
            endpoint (str, optional): Endpoint afetado.
            limit (int, optional): Limite de requisições.
            remaining (int, optional): Requisições restantes.
            reset_time (int, optional): Tempo de reset do limite.
            **extra_data: Dados adicionais.
            
        Example:
            >>> logger.log_rate_limit(
            ...     user_id="123",
            ...     endpoint="/api/users",
            ...     limit=100,
            ...     remaining=5
            ... )
        """
        level = LogLevel.WARNING if remaining and remaining < 10 else LogLevel.INFO
        
        message = f"Rate limit: {user_id or ip_address or 'unknown'}"
        if endpoint:
            message += f" on {endpoint}"
        if remaining is not None and limit is not None:
            message += f" ({remaining}/{limit})"
        
        log_extra = {
            'event_type': 'api_rate_limit',
            'user_id': user_id,
            'ip_address': ip_address,
            'endpoint': endpoint,
            'limit': limit,
            'remaining': remaining,
            'reset_time': reset_time,
            **extra_data
        }
        
        self._log(level.value, message, extra=log_extra)
    
    def _sanitize_body(self, body: Any) -> str:
        """Sanitiza corpo da requisição/resposta para log.
        
        Args:
            body (Any): Corpo a ser sanitizado.
            
        Returns:
            str: Corpo sanitizado.
        """
        try:
            if isinstance(body, (dict, list)):
                body_str = json.dumps(body, ensure_ascii=False)
            else:
                body_str = str(body)
            
            # Truncar se muito longo
            if len(body_str) > self.max_body_size:
                body_str = body_str[:self.max_body_size] + "..."
            
            return _sanitize_for_log(body_str)
        except Exception:
            return "[corpo não serializável]"
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitiza headers removendo informações sensíveis.
        
        Args:
            headers (Dict[str, str]): Headers originais.
            
        Returns:
            Dict[str, str]: Headers sanitizados.
        """
        sensitive_headers = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token',
            'x-access-token', 'x-csrf-token'
        }
        
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = _sanitize_for_log(value)
        
        return sanitized