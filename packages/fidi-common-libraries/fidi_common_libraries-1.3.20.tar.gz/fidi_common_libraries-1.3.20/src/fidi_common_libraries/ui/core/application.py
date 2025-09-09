"""
Gerenciamento avançado de conexão e ciclo de vida de aplicações TOTVS RM.

Este módulo implementa um sistema robusto para gerenciamento de aplicações
externas, especificamente otimizado para o sistema TOTVS RM. Oferece
funcionalidades completas de conexão, inicialização, monitoramento e
fechamento de aplicações com tratamento de erros abrangente e segurança.

Example:
    Uso básico da classe RMApplication:
    
    >>> app_manager = RMApplication(backend="uia")
    >>> app = app_manager.connect_or_start()
    >>> main_window = app_manager.get_main_window()
    >>> # ... usar a aplicação ...
    >>> app_manager.close_application()

Note:
    Este módulo segue as diretrizes de segurança DATAMETRIA, incluindo
    sanitização de logs e validação de parâmetros de entrada.
"""

import logging
import os
import time
from typing import Optional, Union
import psutil

from pywinauto import Application, Desktop
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIConnectionError
from ..utils.screenshot import capture_screenshot_on_error
from ..utils.log_sanitizer import sanitize_for_log

logger = logging.getLogger(__name__)


class RMApplication:
    """Gerenciador completo de conexão e ciclo de vida da aplicação TOTVS RM.
    
    Esta classe fornece um sistema robusto para gerenciamento de aplicações
    TOTVS RM, incluindo conexão, inicialização, monitoramento e fechamento
    com tratamento de erros abrangente e segurança.
    
    Attributes:
        config: Configuração de UI obtida do sistema.
        backend (str): Backend do pywinauto ('uia' ou 'win32').
        app (Application): Instância da aplicação conectada.
        
    Example:
        Uso básico:
        
        >>> app_manager = RMApplication(backend="uia")
        >>> app = app_manager.connect_or_start()
        >>> main_window = app_manager.get_main_window()
        >>> app_manager.close_application()
        
    Note:
        Utiliza sanitização de logs e validação de parâmetros para segurança.
    """
    
    def __init__(self, backend: str = "uia"):
        """Inicializa o gerenciador de aplicação RM.
        
        Args:
            backend (str, optional): Backend do pywinauto ('uia' ou 'win32').
                Defaults to "uia" para compatibilidade com tecnologias modernas.
                
        Raises:
            ValueError: Se backend não for 'uia' ou 'win32'.
            
        Example:
            >>> app_manager = RMApplication(backend="uia")
            >>> app_manager = RMApplication(backend="win32")
        """
        # Validação do parâmetro backend
        valid_backends = {'uia', 'win32'}
        if backend not in valid_backends:
            raise ValueError(f"Backend deve ser um de {valid_backends}, recebido: {backend}")
        
        self.config = get_ui_config()
        self.backend = backend
        self._app: Optional[Application] = None
        self._process_id: Optional[int] = None
        self._is_connected: bool = False
        self._started_by_us: bool = False

    @property
    def app(self) -> Application:
        """Propriedade que retorna a instância da aplicação, garantindo conexão.
        
        Returns:
            Application: Instância da aplicação pywinauto conectada.
            
        Raises:
            UIConnectionError: Se falhar ao obter a instância após tentativa de conexão.
            
        Example:
            >>> app_manager = RMApplication()
            >>> application = app_manager.app  # Conecta automaticamente se necessário
        """
        if not self.is_connected():
            logger.warning("Aplicação não estava conectada. Tentando reconexão automática.")
            self.connect()
        if self._app is None:
            raise UIConnectionError("Falha crítica ao obter a instância da aplicação após tentativa de conexão.")
        return self._app
    
    def start_application(
        self, 
        executable_path: Optional[str] = None,
        wait_time: int = 10
    ) -> Application:
        """Inicia uma nova instância da aplicação TOTVS RM.
        
        Args:
            executable_path (str, optional): Caminho para o executável do RM.
                Defaults to None (usa variável de ambiente RM_EXECUTABLE_PATH).
            wait_time (int, optional): Tempo de espera em segundos após iniciar.
                Defaults to 10.
                
        Returns:
            Application: Instância da aplicação iniciada.
            
        Raises:
            UIConnectionError: Se falhar ao iniciar a aplicação.
            
        Example:
            >>> app_manager = RMApplication()
            >>> app = app_manager.start_application("/path/to/RM.exe", wait_time=15)
        """
        if not executable_path:
            executable_path = os.getenv('RM_EXECUTABLE_PATH', r"C:\totvs\CorporeRM\RM.Net\RM.exe")
        
        try:
            safe_backend = sanitize_for_log(self.backend)
            safe_path = sanitize_for_log(executable_path)
            logger.info(f"Iniciando aplicação RM com backend '{safe_backend}': {safe_path}")
            if not os.path.exists(executable_path):
                raise UIConnectionError(f"Executável não encontrado: {safe_path}")
            
            # Usa o backend definido na inicialização da classe
            self._app = Application(backend=self.backend).start(executable_path)
            self._started_by_us = True
            
            logger.info(f"Aplicação iniciada, aguardando {wait_time} segundos para estabilização...")
            time.sleep(wait_time)
            
            # Conecta à aplicação que acabamos de iniciar para obter o PID e validar
            self._process_id = self._app.process
            self._is_connected = True
            
            logger.info(f"Aplicação RM iniciada e conectada com PID: {self._process_id}")
            return self._app
                
        except Exception as e:
            error_msg = f"Erro ao iniciar aplicação RM: {str(e)}"
            logger.error(error_msg, exc_info=True)
            capture_screenshot_on_error("start_application_failed")
            raise UIConnectionError(error_msg, str(e))

    def connect(
        self, 
        auto_id: Optional[str] = None,
        process_id: Optional[int] = None,
        try_start_if_not_found: bool = True
    ) -> Application:
        """Estabelece conexão com uma aplicação RM existente.
        
        Args:
            auto_id (str, optional): ID automático da janela principal.
                Defaults to None (usa configuração ui_config.default_main_window_auto_id).
            process_id (int, optional): ID do processo para conectar.
                Defaults to None.
            try_start_if_not_found (bool, optional): Se deve tentar iniciar
                a aplicação se não encontrada. Defaults to True.
                
        Returns:
            Application: Instância da aplicação conectada.
            
        Raises:
            UIConnectionError: Se falhar ao conectar após todas as tentativas.
            
        Example:
            >>> app_manager = RMApplication()
            >>> app = app_manager.connect()  # Usa configuração padrão
            >>> app = app_manager.connect(auto_id="CustomForm")
            >>> app = app_manager.connect(process_id=1234)
        """
        # Usa configuração padrão se auto_id não fornecido
        if auto_id is None:
            auto_id = getattr(self.config, 'default_main_window_auto_id', 'MainForm')
            
        for attempt in range(1, self.config.max_connection_attempts + 1):
            try:
                logger.info(f"Tentativa {attempt}/{self.config.max_connection_attempts} de conexão...")
                
                app_spec = Application(backend=self.backend)
                
                if process_id:
                    self._app = app_spec.connect(process=process_id)
                else:
                    # Tenta conectar usando o auto_id, que é o mais robusto
                    window_spec = Desktop(backend=self.backend).window(auto_id=auto_id)
                    if window_spec.exists(timeout=self.config.wait_between_retries):
                        self._app = app_spec.connect(process=window_spec.process_id())
                    else:
                        safe_auto_id = sanitize_for_log(auto_id)
                        raise ElementNotFoundError(f"Janela com auto_id='{safe_auto_id}' não encontrada.")

                self._process_id = self._app.process
                self._is_connected = True
                logger.info(f"Conexão estabelecida com sucesso ao PID: {self._process_id}")
                return self._app
                
            except Exception as e:
                safe_error = sanitize_for_log(str(e))
                logger.warning(f"Tentativa {attempt} falhou: {safe_error}")
                if attempt == self.config.max_connection_attempts:
                    if try_start_if_not_found and not self._started_by_us:
                        logger.info("Tentando iniciar a aplicação como último recurso...")
                        return self.start_application()
                    
                    error_msg = f"Falha ao conectar após {self.config.max_connection_attempts} tentativas"
                    capture_screenshot_on_error("connection_failed")
                    raise UIConnectionError(error_msg, str(e))
        
        raise UIConnectionError("Falha ao conectar após todas as tentativas.")

    def get_main_window(self, auto_id: Optional[str] = None, title_fallback: Optional[str] = None):
        """Localiza e retorna a janela principal da aplicação RM.
        
        Args:
            auto_id (str, optional): ID automático da janela principal.
                Defaults to None (usa configuração ui_config.default_main_window_auto_id).
            title_fallback (str, optional): Padrão regex para título como fallback.
                Defaults to None (usa configuração ui_config.default_title_fallback).
                
        Returns:
            WindowSpecification: Janela principal encontrada.
            
        Raises:
            UIConnectionError: Se não conseguir encontrar a janela principal.
            
        Example:
            >>> app_manager = RMApplication()
            >>> main_window = app_manager.get_main_window()  # Usa configuração padrão
            >>> totvs_window = app_manager.get_main_window(title_fallback=".*RM.*")
        """
        # Usa configurações padrão se não fornecidas
        if auto_id is None:
            auto_id = getattr(self.config, 'default_main_window_auto_id', 'MainForm')
        if title_fallback is None:
            title_fallback = getattr(self.config, 'default_title_fallback', '.*TOTVS.*')
            
        try:
            # Prioridade 1: Buscar por auto_id, o método mais confiável
            return self.app.window(auto_id=auto_id)
        except ElementNotFoundError:
            # Prioridade 2: Fallback para título genérico, caso o auto_id falhe
            safe_auto_id = sanitize_for_log(auto_id)
            safe_title = sanitize_for_log(title_fallback)
            logger.warning(f"Janela com auto_id='{safe_auto_id}' não encontrada. Tentando fallback com título '{safe_title}'.")
            try:
                return self.app.window(title_re=title_fallback)
            except ElementNotFoundError as e:
                safe_error = sanitize_for_log(str(e))
                raise UIConnectionError(f"Não foi possível encontrar a janela principal: {safe_error}")

    def close_application(self, force: bool = False) -> None:
        """Fecha a aplicação RM de forma controlada ou forçada.
        
        Args:
            force (bool, optional): Se deve forçar o fechamento.
                Defaults to False.
                
        Example:
            >>> app_manager = RMApplication()
            >>> app_manager.close_application()  # Fechamento suave
            >>> app_manager.close_application(force=True)  # Forçar fechamento
        """
        if not self.is_connected() or not self._app:
            logger.info("Nenhuma aplicação conectada para fechar.")
            return
        
        try:
            if self._started_by_us or force:
                logger.info("Fechando aplicação RM...")
                # O método kill() do pywinauto é robusto para fechar
                self._app.kill(soft=not force)
                logger.info("Aplicação RM fechada.")
            else:
                logger.info("Aplicação não foi iniciada por este processo, apenas desconectando.")
                
        except Exception as e:
            logger.warning(f"Erro ao fechar aplicação: {e}")
        finally:
            self.disconnect()

    def disconnect(self) -> None:
        """Desconecta da aplicação e limpa o estado interno.
        
        Example:
            >>> app_manager = RMApplication()
            >>> app_manager.disconnect()  # Limpa conexão sem fechar app
        """
        if self._app:
            logger.info("Desconectando da aplicação.")
            self._app = None
            self._is_connected = False
            self._process_id = None
            self._started_by_us = False

    def is_connected(self) -> bool:
        """Verifica se há conexão ativa e se o processo ainda existe.
        
        Returns:
            bool: True se conectado e processo existe, False caso contrário.
            
        Example:
            >>> app_manager = RMApplication()
            >>> if app_manager.is_connected():
            ...     print("Aplicação conectada")
        """
        if not self._is_connected or not self._app or not self._process_id:
            return False
        
        # Usa psutil para uma verificação rápida e eficiente da existência do processo
        try:
            if not psutil.pid_exists(self._process_id):
                logger.warning(f"Conexão perdida: Processo com PID {self._process_id} não existe mais.")
                self.disconnect()
                return False
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            logger.warning(f"Não foi possível verificar processo PID {self._process_id}")
            self.disconnect()
            return False
            
        return True
    
    def connect_or_start(
        self,
        auto_id: Optional[str] = None,
        executable_path: Optional[str] = None,
        wait_time: int = 10
    ) -> Application:
        """Conecta a uma aplicação existente ou inicia uma nova se necessário.
        
        Args:
            auto_id (str, optional): ID automático da janela principal.
                Defaults to None (usa configuração ui_config.default_main_window_auto_id).
            executable_path (str, optional): Caminho para o executável do RM.
                Defaults to None.
            wait_time (int, optional): Tempo de espera após iniciar.
                Defaults to 10.
                
        Returns:
            Application: Instância da aplicação conectada ou iniciada.
            
        Raises:
            UIConnectionError: Se falhar ao conectar ou iniciar.
            
        Example:
            >>> app_manager = RMApplication()
            >>> app = app_manager.connect_or_start()  # Usa configuração padrão
        """
        try:
            return self.connect(auto_id=auto_id, try_start_if_not_found=False)
        except UIConnectionError:
            logger.info("Não foi possível conectar a aplicação existente, iniciando nova instância...")
            return self.start_application(executable_path=executable_path, wait_time=wait_time)
    
    def get_totvs_window(self):
        """Obtém a janela TOTVS usando padrões comuns.
        
        Returns:
            WindowSpecification: Janela TOTVS encontrada.
            
        Raises:
            UIConnectionError: Se não conseguir encontrar a janela TOTVS.
            
        Example:
            >>> app_manager = RMApplication()
            >>> totvs_window = app_manager.get_totvs_window()
        """
        return self.get_main_window(title_fallback=".*TOTVS.*")
    
    def wait_for_application_ready(self, timeout: int = 60) -> bool:
        """Aguarda a aplicação ficar pronta para uso.
        
        Args:
            timeout (int, optional): Timeout em segundos. Defaults to 60.
            
        Returns:
            bool: True se a aplicação ficou pronta, False se timeout.
            
        Example:
            >>> app_manager = RMApplication()
            >>> if app_manager.wait_for_application_ready(timeout=30):
            ...     print("Aplicação pronta para uso")
        """
        try:
            main_window = self.get_main_window()
            main_window.wait('ready', timeout=timeout)
            return True
        except Exception as e:
            safe_error = sanitize_for_log(str(e))
            logger.warning(f"Timeout aguardando aplicação ficar pronta: {safe_error}")
            return False
