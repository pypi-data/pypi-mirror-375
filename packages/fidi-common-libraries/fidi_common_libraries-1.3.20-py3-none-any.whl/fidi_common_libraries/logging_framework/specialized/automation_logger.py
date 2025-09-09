"""Logger especializado para automação UI DATAMETRIA."""

import logging
import time
from typing import Any, Dict, Optional
from contextlib import contextmanager
from datetime import datetime

from ..core.base_logger import BaseLogger, LogCategory, LogLevel, _sanitize_for_log


class AutomationLogger(BaseLogger):
    """Logger especializado para automação UI com pywinauto.
    
    Este logger fornece funcionalidades específicas para automação de UI,
    incluindo contexto de elementos, operações pywinauto e captura de screenshots.
    
    Attributes:
        enable_screenshots (bool): Se deve capturar screenshots em erros.
        enable_ui_context (bool): Se deve capturar contexto de UI.
        
    Example:
        Uso em automação UI:
        
        >>> logger = AutomationLogger("ui_automation")
        >>> with logger.ui_context(window_title="Calculator", action="click"):
        ...     logger.pywinauto_operation(
        ...         "click",
        ...         {"class_name": "Button", "title": "1"},
        ...         success=True,
        ...         duration=0.1
        ...     )
    """
    
    def __init__(self, name: str, **kwargs):
        """Inicializa o logger de automação.
        
        Args:
            name (str): Nome do logger.
            **kwargs: Argumentos adicionais incluindo:
                - enable_screenshots (bool): Capturar screenshots em erros
                - enable_ui_context (bool): Capturar contexto de UI
        """
        self.enable_screenshots = kwargs.pop('enable_screenshots', True)
        self.enable_ui_context = kwargs.pop('enable_ui_context', True)
        super().__init__(name, LogCategory.AUTOMATION, **kwargs)
    
    def _setup_logging_infrastructure(self):
        """Configura handlers específicos para automação."""
        # Evitar duplicação de handlers
        if self.logger.handlers:
            return
            
        # Handler de console com formatação específica
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # Formatter para automação
        formatter = logging.Formatter(
            '%(asctime)s - [AUTOMATION] %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Handler de arquivo para automação
        try:
            file_handler = logging.FileHandler('logs/automation.log', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except (OSError, IOError):
            # Se não conseguir criar arquivo, continua apenas com console
            pass
        
        self.logger.addHandler(console_handler)
        self.logger.propagate = False
    
    @contextmanager
    def ui_context(
        self, 
        window_title: Optional[str] = None,
        action: Optional[str] = None,
        element: Optional[str] = None,
        **extra_context
    ):
        """Context manager para capturar contexto de UI.
        
        Args:
            window_title (str, optional): Título da janela.
            action (str, optional): Ação sendo executada.
            element (str, optional): Elemento alvo.
            **extra_context: Contexto adicional.
            
        Example:
            >>> with logger.ui_context(window_title="Calculator", action="click"):
            ...     logger.info("Clicando no botão")
        """
        context_data = {
            'window_title': window_title,
            'action': action,
            'element': element,
            'ui_timestamp': datetime.now().isoformat(),
            **extra_context
        }
        
        # Filtrar valores None
        context_data = {k: v for k, v in context_data.items() if v is not None}
        
        with self.context(**context_data):
            if self.enable_ui_context:
                self.trace(f"Iniciando contexto UI: {context_data}")
            yield
    
    def pywinauto_operation(
        self,
        operation: str,
        element_info: Dict[str, Any],
        success: bool = True,
        duration: Optional[float] = None,
        error: Optional[Exception] = None,
        **extra_data
    ):
        """Loga operações específicas do pywinauto.
        
        Args:
            operation (str): Nome da operação (click, type_keys, etc.).
            element_info (Dict[str, Any]): Informações do elemento.
            success (bool, optional): Se a operação foi bem-sucedida.
                Defaults to True.
            duration (float, optional): Duração da operação em segundos.
            error (Exception, optional): Exceção se houver erro.
            **extra_data: Dados adicionais da operação.
            
        Example:
            >>> logger.pywinauto_operation(
            ...     "click",
            ...     {"class_name": "Button", "title": "OK"},
            ...     success=True,
            ...     duration=0.15
            ... )
        """
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        
        # Construir mensagem
        msg_parts = [f"PyWinAuto.{operation}"]
        
        if element_info:
            element_desc = ", ".join([
                f"{k}={v}" for k, v in element_info.items() 
                if v is not None
            ])
            msg_parts.append(f"Element({element_desc})")
        
        if duration is not None:
            msg_parts.append(f"Duration: {duration:.3f}s")
        
        if not success and error:
            safe_error = _sanitize_for_log(str(error))
            msg_parts.append(f"Error: {safe_error}")
        
        msg = " | ".join(msg_parts)
        
        # Dados extras para o log
        log_extra = {
            'event_type': 'pywinauto_operation',
            'operation': operation,
            'element_info': element_info,
            'success': success,
            'duration': duration,
            **extra_data
        }
        
        if error:
            log_extra['error'] = _sanitize_for_log(str(error))
            log_extra['error_type'] = type(error).__name__
        
        self.logger.log(level.value, msg, extra=log_extra)
        
        # Capturar screenshot em caso de erro
        if not success and self.enable_screenshots:
            self._capture_error_screenshot(operation, element_info)
    
    def element_interaction(
        self,
        action: str,
        element_criteria: Dict[str, Any],
        success: bool = True,
        retry_count: int = 0,
        **extra_data
    ):
        """Loga interações com elementos de UI.
        
        Args:
            action (str): Ação executada (find, click, type, etc.).
            element_criteria (Dict[str, Any]): Critérios de busca do elemento.
            success (bool, optional): Se a interação foi bem-sucedida.
                Defaults to True.
            retry_count (int, optional): Número de tentativas realizadas.
                Defaults to 0.
            **extra_data: Dados adicionais.
            
        Example:
            >>> logger.element_interaction(
            ...     "find_element",
            ...     {"auto_id": "btnSave", "title": "Salvar"},
            ...     success=True,
            ...     retry_count=2
            ... )
        """
        level = LogLevel.SUCCESS if success else LogLevel.WARNING
        
        criteria_str = ", ".join([
            f"{k}={v}" for k, v in element_criteria.items()
        ])
        
        msg = f"Element {action}: {criteria_str}"
        if retry_count > 0:
            msg += f" (after {retry_count} retries)"
        
        log_extra = {
            'event_type': 'element_interaction',
            'action': action,
            'element_criteria': element_criteria,
            'success': success,
            'retry_count': retry_count,
            **extra_data
        }
        
        self.logger.log(level.value, msg, extra=log_extra)
    
    def window_operation(
        self,
        operation: str,
        window_info: Dict[str, Any],
        success: bool = True,
        **extra_data
    ):
        """Loga operações com janelas.
        
        Args:
            operation (str): Operação executada (connect, activate, close, etc.).
            window_info (Dict[str, Any]): Informações da janela.
            success (bool, optional): Se a operação foi bem-sucedida.
                Defaults to True.
            **extra_data: Dados adicionais.
            
        Example:
            >>> logger.window_operation(
            ...     "connect",
            ...     {"title": "Calculator", "process_id": 1234},
            ...     success=True
            ... )
        """
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        
        window_desc = ", ".join([
            f"{k}={v}" for k, v in window_info.items()
            if v is not None
        ])
        
        msg = f"Window {operation}: {window_desc}"
        
        log_extra = {
            'event_type': 'window_operation',
            'operation': operation,
            'window_info': window_info,
            'success': success,
            **extra_data
        }
        
        self.logger.log(level.value, msg, extra=log_extra)
    
    def log_ui_operation(
        self,
        operation: str,
        element_info: Dict[str, Any],
        success: bool = True,
        duration: Optional[float] = None,
        error: Optional[Exception] = None
    ):
        """Loga operações específicas de UI (alias para pywinauto_operation).
        
        Args:
            operation (str): Nome da operação (click, type_text, etc.)
            element_info (Dict[str, Any]): Informações do elemento
            success (bool): Se a operação foi bem-sucedida
            duration (float, optional): Duração da operação em segundos
            error (Exception, optional): Exceção se houver erro
        """
        self.pywinauto_operation(
            operation=operation,
            element_info=element_info,
            success=success,
            duration=duration,
            error=error
        )
    
    def _capture_error_screenshot(self, operation: str, element_info: Dict[str, Any]):
        """Captura screenshot em caso de erro.
        
        Args:
            operation (str): Operação que falhou.
            element_info (Dict[str, Any]): Informações do elemento.
        """
        try:
            from ...ui.utils.screenshot import capture_screenshot_on_error
            screenshot_name = f"automation_error_{operation}_{int(time.time())}"
            capture_screenshot_on_error(screenshot_name)
            self.debug(f"Screenshot capturado: {screenshot_name}")
        except Exception as e:
            safe_error = _sanitize_for_log(str(e))
            self.warning(f"Falha ao capturar screenshot: {safe_error}")