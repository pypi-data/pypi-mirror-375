"""Logger especializado para operações de banco de dados DATAMETRIA."""

import logging
import time
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

from ..core.base_logger import BaseLogger, LogCategory, LogLevel, _sanitize_for_log


class DatabaseLogger(BaseLogger):
    """Logger especializado para operações de banco de dados.
    
    Este logger fornece funcionalidades específicas para logging de operações
    de banco de dados, incluindo queries, procedures e transações.
    
    Attributes:
        slow_query_threshold (float): Threshold para queries lentas em segundos.
        
    Example:
        Uso em operações de banco:
        
        >>> logger = DatabaseLogger("main_db", slow_query_threshold=1.0)
        >>> logger.log_query(
        ...     "SELECT * FROM users WHERE active = ?",
        ...     "SELECT",
        ...     duration=0.05,
        ...     rows_affected=150,
        ...     success=True
        ... )
    """
    
    def __init__(self, name: str, **kwargs):
        """Inicializa o logger de banco de dados.
        
        Args:
            name (str): Nome do logger.
            **kwargs: Argumentos adicionais incluindo:
                - slow_query_threshold (float): Threshold para queries lentas
        """
        self.slow_query_threshold = kwargs.pop('slow_query_threshold', 1.0)
        super().__init__(name, LogCategory.DATABASE, **kwargs)
    
    def _setup_logging_infrastructure(self):
        """Configura handlers específicos para banco de dados."""
        # Evitar duplicação de handlers
        if self.logger.handlers:
            return
            
        # Handler de console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # Formatter para banco de dados
        formatter = logging.Formatter(
            '%(asctime)s - [DATABASE] %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Handler de arquivo para banco
        try:
            file_handler = logging.FileHandler('logs/database.log', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except (OSError, IOError):
            # Se não conseguir criar arquivo, continua apenas com console
            pass
        
        self.logger.addHandler(console_handler)
        self.logger.propagate = False
    
    def log_query(
        self,
        query: str,
        query_type: str,
        duration: float,
        rows_affected: Optional[int] = None,
        table: Optional[str] = None,
        database: Optional[str] = None,
        parameters: Optional[List[Any]] = None,
        success: bool = True,
        error: Optional[Exception] = None,
        **extra_data
    ):
        """Loga uma query de banco de dados.
        
        Args:
            query (str): Query SQL executada.
            query_type (str): Tipo da query (SELECT, INSERT, UPDATE, etc.).
            duration (float): Duração da execução em segundos.
            rows_affected (int, optional): Número de linhas afetadas.
            table (str, optional): Tabela principal da query.
            database (str, optional): Nome do banco de dados.
            parameters (List[Any], optional): Parâmetros da query.
            success (bool, optional): Se a query foi bem-sucedida.
                Defaults to True.
            error (Exception, optional): Exceção se houver erro.
            **extra_data: Dados adicionais.
            
        Example:
            >>> logger.log_query(
            ...     "SELECT * FROM users WHERE id = ?",
            ...     "SELECT",
            ...     duration=0.025,
            ...     rows_affected=1,
            ...     table="users",
            ...     parameters=[123]
            ... )
        """
        # Sanitizar query para log
        sanitized_query = self._sanitize_query(query, parameters)
        
        # Determinar nível de log
        if not success:
            level = LogLevel.ERROR
            message = f"Query falhou: {query_type}"
        elif duration > self.slow_query_threshold:
            level = LogLevel.WARNING
            message = f"Query lenta: {query_type}"
        else:
            level = LogLevel.SUCCESS
            message = f"Query executada: {query_type}"
        
        # Adicionar informações à mensagem
        if table:
            message += f" em {table}"
        if duration:
            message += f" ({duration:.3f}s)"
        if rows_affected is not None:
            message += f" - {rows_affected} linhas"
        
        # Dados extras para o log
        log_extra = {
            'event_type': 'database_query',
            'query_type': query_type,
            'query': sanitized_query,
            'duration': duration,
            'rows_affected': rows_affected,
            'table': table,
            'database': database,
            'success': success,
            'is_slow_query': duration > self.slow_query_threshold,
            **extra_data
        }
        
        if error:
            log_extra['error'] = _sanitize_for_log(str(error))
            log_extra['error_type'] = type(error).__name__
        
        self.logger.log(level.value, message, extra=log_extra)
    
    def log_procedure(
        self,
        procedure_name: str,
        parameters: Optional[List[Any]] = None,
        duration: Optional[float] = None,
        result_type: str = "void",
        result_value: Any = None,
        success: bool = True,
        error: Optional[Exception] = None,
        **extra_data
    ):
        """Loga execução de procedure.
        
        Args:
            procedure_name (str): Nome da procedure.
            parameters (List[Any], optional): Parâmetros da procedure.
            duration (float, optional): Duração da execução.
            result_type (str, optional): Tipo do resultado.
                Defaults to "void".
            result_value (Any, optional): Valor retornado.
            success (bool, optional): Se a execução foi bem-sucedida.
                Defaults to True.
            error (Exception, optional): Exceção se houver erro.
            **extra_data: Dados adicionais.
            
        Example:
            >>> logger.log_procedure(
            ...     "sp_get_user_data",
            ...     parameters=[123],
            ...     duration=0.15,
            ...     result_type="single_row",
            ...     success=True
            ... )
        """
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        
        message = f"Procedure {procedure_name}"
        if duration:
            message += f" ({duration:.3f}s)"
        if result_type != "void":
            message += f" -> {result_type}"
        
        # Sanitizar parâmetros
        safe_params = None
        if parameters:
            safe_params = [_sanitize_for_log(str(p)) for p in parameters]
        
        log_extra = {
            'event_type': 'database_procedure',
            'procedure_name': procedure_name,
            'parameters': safe_params,
            'duration': duration,
            'result_type': result_type,
            'success': success,
            **extra_data
        }
        
        if error:
            log_extra['error'] = _sanitize_for_log(str(error))
            log_extra['error_type'] = type(error).__name__
        
        if result_value is not None and result_type != "void":
            log_extra['result_preview'] = _sanitize_for_log(str(result_value)[:100])
        
        self.logger.log(level.value, message, extra=log_extra)
    
    @contextmanager
    def transaction_context(self, transaction_name: Optional[str] = None):
        """Context manager para transações de banco.
        
        Args:
            transaction_name (str, optional): Nome da transação.
            
        Example:
            >>> with logger.transaction_context("user_update"):
            ...     logger.log_query("UPDATE users SET ...", "UPDATE", 0.1)
            ...     logger.log_query("INSERT INTO audit ...", "INSERT", 0.05)
        """
        transaction_id = f"txn_{int(time.time())}"
        start_time = time.time()
        
        context_data = {
            'transaction_id': transaction_id,
            'transaction_name': transaction_name or "unnamed"
        }
        
        with self.context(**context_data):
            self.info(f"Iniciando transação: {transaction_name or transaction_id}")
            
            try:
                yield transaction_id
                
                duration = time.time() - start_time
                self.success(f"Transação concluída: {transaction_name or transaction_id}", extra={
                    'event_type': 'transaction_success',
                    'transaction_id': transaction_id,
                    'duration': duration
                })
                
            except Exception as e:
                duration = time.time() - start_time
                self.error(f"Transação falhou: {transaction_name or transaction_id}", extra={
                    'event_type': 'transaction_error',
                    'transaction_id': transaction_id,
                    'duration': duration,
                    'error': _sanitize_for_log(str(e)),
                    'error_type': type(e).__name__
                })
                raise
    
    def log_connection(
        self,
        action: str,
        database: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        success: bool = True,
        duration: Optional[float] = None,
        error: Optional[Exception] = None,
        **extra_data
    ):
        """Loga operações de conexão com banco.
        
        Args:
            action (str): Ação executada (connect, disconnect, reconnect).
            database (str): Nome do banco de dados.
            host (str, optional): Host do banco.
            port (int, optional): Porta do banco.
            success (bool, optional): Se a operação foi bem-sucedida.
                Defaults to True.
            duration (float, optional): Duração da operação.
            error (Exception, optional): Exceção se houver erro.
            **extra_data: Dados adicionais.
            
        Example:
            >>> logger.log_connection(
            ...     "connect",
            ...     "production_db",
            ...     host="db.example.com",
            ...     port=5432,
            ...     success=True,
            ...     duration=0.5
            ... )
        """
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        
        message = f"Database {action}: {database}"
        if host:
            message += f" at {host}"
            if port:
                message += f":{port}"
        if duration:
            message += f" ({duration:.3f}s)"
        
        log_extra = {
            'event_type': 'database_connection',
            'action': action,
            'database': database,
            'host': host,
            'port': port,
            'success': success,
            'duration': duration,
            **extra_data
        }
        
        if error:
            log_extra['error'] = _sanitize_for_log(str(error))
            log_extra['error_type'] = type(error).__name__
        
        self.logger.log(level.value, message, extra=log_extra)
    
    def _sanitize_query(self, query: str, parameters: Optional[List[Any]] = None) -> str:
        """Sanitiza query para log removendo dados sensíveis.
        
        Args:
            query (str): Query original.
            parameters (List[Any], optional): Parâmetros da query.
            
        Returns:
            str: Query sanitizada.
        """
        # Sanitizar a query básica
        sanitized = _sanitize_for_log(query)
        
        # Truncar se muito longa
        if len(sanitized) > 500:
            sanitized = sanitized[:497] + "..."
        
        # Adicionar informação sobre parâmetros sem expor valores
        if parameters:
            param_count = len(parameters)
            sanitized += f" [com {param_count} parâmetros]"
        
        return sanitized
    
    def log_database_operation(
        self,
        operation: str,
        database: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        success: bool = True,
        duration: Optional[float] = None,
        error: Optional[Exception] = None
    ):
        """Loga operações de banco de dados (alias para log_connection).
        
        Args:
            operation (str): Tipo de operação (connect, disconnect, etc.)
            database (str, optional): Nome do banco
            host (str, optional): Host do banco
            port (int, optional): Porta do banco
            success (bool): Se a operação foi bem-sucedida
            duration (float, optional): Duração da operação
            error (Exception, optional): Exceção se houver erro
        """
        self.log_connection(
            action=operation,
            database=database or "unknown",
            host=host,
            port=port,
            success=success,
            duration=duration,
            error=error
        )