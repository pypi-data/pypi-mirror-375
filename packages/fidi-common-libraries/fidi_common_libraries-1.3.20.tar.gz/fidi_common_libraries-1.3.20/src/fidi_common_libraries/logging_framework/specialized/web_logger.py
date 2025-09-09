"""Logger especializado para aplicações web DATAMETRIA."""

import logging
from typing import Any, Dict, Optional
from contextlib import contextmanager

from ..core.base_logger import BaseLogger, LogCategory, LogLevel, _sanitize_for_log


class WebLogger(BaseLogger):
    """Logger especializado para aplicações web.
    
    Este logger fornece funcionalidades específicas para logging de aplicações
    web, incluindo requisições HTTP, sessões de usuário e eventos de frontend.
    
    Example:
        Uso em aplicações web:
        
        >>> logger = WebLogger("webapp")
        >>> logger.log_page_view(
        ...     "/dashboard",
        ...     user_id="123",
        ...     session_id="abc",
        ...     load_time=1.5
        ... )
    """
    
    def __init__(self, name: str, **kwargs):
        """Inicializa o logger web.
        
        Args:
            name (str): Nome do logger.
            **kwargs: Argumentos adicionais.
        """
        super().__init__(name, LogCategory.WEB, **kwargs)
    
    def _setup_logging_infrastructure(self):
        """Configura handlers específicos para web."""
        # Evitar duplicação de handlers
        if self.logger.handlers:
            return
            
        # Handler de console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # Formatter para web
        formatter = logging.Formatter(
            '%(asctime)s - [WEB] %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Handler de arquivo para web
        try:
            file_handler = logging.FileHandler('logs/web.log', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except (OSError, IOError):
            # Se não conseguir criar arquivo, continua apenas com console
            pass
        
        self.logger.addHandler(console_handler)
        self.logger.propagate = False
    
    def log_page_view(
        self,
        page: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        load_time: Optional[float] = None,
        referrer: Optional[str] = None,
        **extra_data
    ):
        """Loga visualização de página.
        
        Args:
            page (str): Página visualizada.
            user_id (str, optional): ID do usuário.
            session_id (str, optional): ID da sessão.
            ip_address (str, optional): IP do cliente.
            user_agent (str, optional): User agent.
            load_time (float, optional): Tempo de carregamento.
            referrer (str, optional): Página de origem.
            **extra_data: Dados extras.
            
        Example:
            >>> logger.log_page_view(
            ...     "/dashboard",
            ...     user_id="123",
            ...     session_id="abc",
            ...     load_time=1.5
            ... )
        """
        message = f"Page view: {_sanitize_for_log(page)}"
        if user_id:
            message += f" by {_sanitize_for_log(user_id)}"
        if load_time:
            message += f" ({load_time:.2f}s)"
        
        log_extra = {
            'event_type': 'page_view',
            'page': _sanitize_for_log(page),
            'user_id': _sanitize_for_log(user_id) if user_id else None,
            'session_id': session_id,
            'ip_address': ip_address,
            'user_agent': _sanitize_for_log(user_agent) if user_agent else None,
            'load_time': load_time,
            'referrer': _sanitize_for_log(referrer) if referrer else None,
            **extra_data
        }
        
        self._log(LogLevel.INFO.value, message, extra=log_extra)
    
    def log_user_action(
        self,
        action: str,
        user_id: str,
        target: Optional[str] = None,
        success: bool = True,
        **extra_data
    ):
        """Loga ação do usuário.
        
        Args:
            action (str): Ação executada.
            user_id (str): ID do usuário.
            target (str, optional): Alvo da ação.
            success (bool, optional): Se foi bem-sucedida.
                Defaults to True.
            **extra_data: Dados extras.
            
        Example:
            >>> logger.log_user_action(
            ...     "button_click",
            ...     "user123",
            ...     target="save_button",
            ...     success=True
            ... )
        """
        level = LogLevel.SUCCESS if success else LogLevel.WARNING
        
        message = f"User action: {action} by {_sanitize_for_log(user_id)}"
        if target:
            message += f" on {_sanitize_for_log(target)}"
        
        log_extra = {
            'event_type': 'user_action',
            'action': action,
            'user_id': _sanitize_for_log(user_id),
            'target': _sanitize_for_log(target) if target else None,
            'success': success,
            **extra_data
        }
        
        self._log(level.value, message, extra=log_extra)
    
    @contextmanager
    def session_context(self, session_id: str, user_id: Optional[str] = None):
        """Context manager para sessões web.
        
        Args:
            session_id (str): ID da sessão.
            user_id (str, optional): ID do usuário.
            
        Example:
            >>> with logger.session_context("abc123", "user456"):
            ...     logger.info("Processando requisição")
        """
        context_data = {
            'session_id': session_id,
            'user_id': _sanitize_for_log(user_id) if user_id else None
        }
        
        with self.context(**context_data):
            yield