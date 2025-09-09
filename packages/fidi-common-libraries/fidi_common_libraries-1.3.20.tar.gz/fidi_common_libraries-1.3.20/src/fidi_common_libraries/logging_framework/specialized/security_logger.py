"""Logger especializado para segurança e auditoria DATAMETRIA."""

import logging
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

from ..core.base_logger import BaseLogger, LogCategory, LogLevel, _sanitize_for_log


class SecurityLogger(BaseLogger):
    """Logger especializado para eventos de segurança e auditoria.
    
    Este logger fornece funcionalidades específicas para logging de eventos
    de segurança, autenticação, autorização e trilha de auditoria.
    
    Attributes:
        enable_audit_trail (bool): Se deve manter trilha de auditoria.
        
    Example:
        Uso em segurança:
        
        >>> logger = SecurityLogger("auth_system", enable_audit_trail=True)
        >>> logger.log_authentication(
        ...     "user123",
        ...     "login",
        ...     success=True,
        ...     ip_address="192.168.1.100"
        ... )
    """
    
    def __init__(self, name: str, **kwargs):
        """Inicializa o logger de segurança.
        
        Args:
            name (str): Nome do logger.
            **kwargs: Argumentos adicionais incluindo:
                - enable_audit_trail (bool): Se deve manter trilha de auditoria
        """
        self.enable_audit_trail = kwargs.pop('enable_audit_trail', True)
        super().__init__(name, LogCategory.SECURITY, **kwargs)
    
    def _setup_logging_infrastructure(self):
        """Configura handlers específicos para segurança."""
        # Evitar duplicação de handlers
        if self.logger.handlers:
            return
            
        # Handler de console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # Formatter para segurança
        formatter = logging.Formatter(
            '%(asctime)s - [SECURITY] %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Handler de arquivo para segurança (crítico)
        try:
            file_handler = logging.FileHandler('logs/security.log', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except (OSError, IOError):
            # Se não conseguir criar arquivo, continua apenas com console
            pass
        
        self.logger.addHandler(console_handler)
        self.logger.propagate = False
    
    def log_authentication(
        self,
        user_id: str,
        action: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        **extra_data
    ):
        """Loga eventos de autenticação.
        
        Args:
            user_id (str): ID do usuário.
            action (str): Ação executada (login, logout, etc.).
            success (bool): Se a autenticação foi bem-sucedida.
            ip_address (str, optional): IP do cliente.
            user_agent (str, optional): User agent do cliente.
            failure_reason (str, optional): Razão da falha se houver.
            additional_data (Dict[str, Any], optional): Dados adicionais.
            **extra_data: Dados extras.
            
        Example:
            >>> logger.log_authentication(
            ...     "user123",
            ...     "login",
            ...     success=True,
            ...     ip_address="192.168.1.100",
            ...     user_agent="Mozilla/5.0..."
            ... )
        """
        level = LogLevel.SECURITY if success else LogLevel.ERROR
        
        message = f"Auth {action}: {_sanitize_for_log(user_id)}"
        if success:
            message += " - Success"
        else:
            message += " - Failed"
            if failure_reason:
                message += f" ({failure_reason})"
        
        log_extra = {
            'event_type': 'authentication',
            'user_id': _sanitize_for_log(user_id),
            'action': action,
            'success': success,
            'ip_address': ip_address,
            'user_agent': _sanitize_for_log(user_agent) if user_agent else None,
            'failure_reason': failure_reason,
            **extra_data
        }
        
        if additional_data:
            # Sanitizar dados adicionais
            sanitized_additional = {
                k: _sanitize_for_log(str(v)) for k, v in additional_data.items()
            }
            log_extra.update(sanitized_additional)
        
        self._log(level.value, message, extra=log_extra)
    
    def log_authorization(
        self,
        user_id: str,
        resource: str,
        action: str,
        granted: bool,
        permissions: Optional[List[str]] = None,
        denial_reason: Optional[str] = None,
        **extra_data
    ):
        """Loga eventos de autorização.
        
        Args:
            user_id (str): ID do usuário.
            resource (str): Recurso acessado.
            action (str): Ação tentada.
            granted (bool): Se o acesso foi concedido.
            permissions (List[str], optional): Permissões do usuário.
            denial_reason (str, optional): Razão da negação se houver.
            **extra_data: Dados extras.
            
        Example:
            >>> logger.log_authorization(
            ...     "user123",
            ...     "/admin/users",
            ...     "read",
            ...     granted=True,
            ...     permissions=["admin", "user_read"]
            ... )
        """
        level = LogLevel.SECURITY if granted else LogLevel.WARNING
        
        message = f"Auth {action} on {resource}: {_sanitize_for_log(user_id)}"
        if granted:
            message += " - Granted"
        else:
            message += " - Denied"
            if denial_reason:
                message += f" ({denial_reason})"
        
        log_extra = {
            'event_type': 'authorization',
            'user_id': _sanitize_for_log(user_id),
            'resource': _sanitize_for_log(resource),
            'action': action,
            'granted': granted,
            'permissions': permissions,
            'denial_reason': denial_reason,
            **extra_data
        }
        
        self._log(level.value, message, extra=log_extra)
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        affected_resources: Optional[List[str]] = None,
        mitigation_actions: Optional[List[str]] = None,
        **extra_data
    ):
        """Loga eventos de segurança gerais.
        
        Args:
            event_type (str): Tipo do evento (intrusion_attempt, etc.).
            severity (str): Severidade (low, medium, high, critical).
            description (str): Descrição do evento.
            user_id (str, optional): ID do usuário envolvido.
            ip_address (str, optional): IP envolvido.
            affected_resources (List[str], optional): Recursos afetados.
            mitigation_actions (List[str], optional): Ações de mitigação.
            **extra_data: Dados extras.
            
        Example:
            >>> logger.log_security_event(
            ...     "brute_force_attempt",
            ...     "high",
            ...     "Múltiplas tentativas de login falharam",
            ...     ip_address="192.168.1.100",
            ...     mitigation_actions=["block_ip", "alert_admin"]
            ... )
        """
        level_map = {
            'low': LogLevel.INFO,
            'medium': LogLevel.WARNING,
            'high': LogLevel.ERROR,
            'critical': LogLevel.CRITICAL
        }
        
        level = level_map.get(severity.lower(), LogLevel.WARNING)
        
        message = f"Security Event [{severity.upper()}]: {event_type}"
        message += f" - {_sanitize_for_log(description)}"
        
        log_extra = {
            'event_type': 'security_event',
            'security_event_type': event_type,
            'severity': severity,
            'description': _sanitize_for_log(description),
            'user_id': _sanitize_for_log(user_id) if user_id else None,
            'ip_address': ip_address,
            'affected_resources': affected_resources,
            'mitigation_actions': mitigation_actions,
            **extra_data
        }
        
        self._log(level.value, message, extra=log_extra)
    
    def log_data_access(
        self,
        user_id: str,
        data_type: str,
        action: str,
        success: bool = True,
        record_count: Optional[int] = None,
        sensitive_data: bool = False,
        **extra_data
    ):
        """Loga acessos a dados para auditoria.
        
        Args:
            user_id (str): ID do usuário.
            data_type (str): Tipo de dados acessados.
            action (str): Ação executada (read, write, delete, etc.).
            success (bool, optional): Se o acesso foi bem-sucedido.
                Defaults to True.
            record_count (int, optional): Número de registros afetados.
            sensitive_data (bool, optional): Se são dados sensíveis.
                Defaults to False.
            **extra_data: Dados extras.
            
        Example:
            >>> logger.log_data_access(
            ...     "user123",
            ...     "customer_data",
            ...     "read",
            ...     success=True,
            ...     record_count=50,
            ...     sensitive_data=True
            ... )
        """
        level = LogLevel.AUDIT if success else LogLevel.ERROR
        
        message = f"Data {action}: {data_type} by {_sanitize_for_log(user_id)}"
        if record_count is not None:
            message += f" ({record_count} records)"
        if sensitive_data:
            message += " [SENSITIVE]"
        
        log_extra = {
            'event_type': 'data_access',
            'user_id': _sanitize_for_log(user_id),
            'data_type': data_type,
            'action': action,
            'success': success,
            'record_count': record_count,
            'sensitive_data': sensitive_data,
            **extra_data
        }
        
        self._log(level.value, message, extra=log_extra)
    
    @contextmanager
    def audit_context(
        self,
        operation: str,
        user_id: str,
        **audit_data
    ):
        """Context manager para operações auditáveis.
        
        Args:
            operation (str): Nome da operação.
            user_id (str): ID do usuário.
            **audit_data: Dados de auditoria.
            
        Example:
            >>> with logger.audit_context("user_creation", "admin123"):
            ...     logger.info("Criando novo usuário")
            ...     # Operação é automaticamente auditada
        """
        context_data = {
            'audit_operation': operation,
            'audit_user_id': _sanitize_for_log(user_id),
            **audit_data
        }
        
        with self.context(**context_data):
            if self.enable_audit_trail:
                self.audit(f"Iniciando operação auditável: {operation}")
            
            try:
                yield
                
                if self.enable_audit_trail:
                    self.audit(f"Operação auditável concluída: {operation}")
                    
            except Exception as e:
                if self.enable_audit_trail:
                    self.audit(f"Operação auditável falhou: {operation} - {_sanitize_for_log(str(e))}")
                raise
    
    def log_compliance_event(
        self,
        regulation: str,
        event_type: str,
        description: str,
        user_id: Optional[str] = None,
        data_subject: Optional[str] = None,
        **extra_data
    ):
        """Loga eventos relacionados a compliance.
        
        Args:
            regulation (str): Regulamentação (LGPD, GDPR, etc.).
            event_type (str): Tipo do evento (data_request, etc.).
            description (str): Descrição do evento.
            user_id (str, optional): ID do usuário.
            data_subject (str, optional): Titular dos dados.
            **extra_data: Dados extras.
            
        Example:
            >>> logger.log_compliance_event(
            ...     "LGPD",
            ...     "data_deletion_request",
            ...     "Usuário solicitou exclusão de dados",
            ...     user_id="user123",
            ...     data_subject="customer456"
            ... )
        """
        message = f"Compliance [{regulation}] {event_type}: {_sanitize_for_log(description)}"
        
        log_extra = {
            'event_type': 'compliance_event',
            'regulation': regulation,
            'compliance_event_type': event_type,
            'description': _sanitize_for_log(description),
            'user_id': _sanitize_for_log(user_id) if user_id else None,
            'data_subject': _sanitize_for_log(data_subject) if data_subject else None,
            **extra_data
        }
        
        self._log(LogLevel.AUDIT.value, message, extra=log_extra)