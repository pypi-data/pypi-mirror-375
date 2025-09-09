"""Módulo de inicialização e login automatizado para aplicação TOTVS RM.

Este módulo implementa um sistema completo de inicialização e autenticação
automatizada para o sistema TOTVS RM, incluindo seleção de ambiente,
preenchimento de credenciais e validação de login bem-sucedido.

Classes:
    RMStartLogin: Gerenciador principal de inicialização e login automatizado.

Example:
    Uso básico do sistema de login:
    
    >>> from fidi_common_libraries.ui.locators import LocatorService
    >>> locator_service = LocatorService("locators.yaml")
    >>> login_manager = RMStartLogin(locator_service)
    >>> success, rm_app = login_manager.start_and_login("HML", "FIDI-ferias")
    >>> if success:
    ...     print("Login realizado com sucesso")
    ...     main_window = rm_app.get_main_window()

Note:
    Este módulo segue as diretrizes de segurança DATAMETRIA, incluindo
    sanitização de logs, tratamento robusto de exceções e captura de
    screenshots para debug em caso de falha.
"""

import logging
from typing import Tuple, Optional
import time
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError as PywinautoTimeoutError

from ...config.parametros import Parametros
from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIConnectionError, UIElementNotFoundError, UIInteractionError, UITimeoutError
from ..utils.screenshot import capture_screenshot_on_error
from ..utils.log_sanitizer import sanitize_for_log
from ..locators.locator_service import LocatorService
from .application import RMApplication
from .rm_login_env_selector import RMLoginEnvSelector
from .waits import UIWaits

logger = logging.getLogger(__name__)


class RMStartLogin:
    """Gerenciador completo de inicialização e login automatizado para TOTVS RM.
    
    Esta classe implementa um sistema robusto de inicialização da aplicação
    TOTVS RM e execução de login automatizado, incluindo seleção de ambiente,
    preenchimento de credenciais e validação de sucesso.
    
    Attributes:
        locator_service (LocatorService): Serviço de localização de elementos UI.
        config (UIConfig): Configuração de UI obtida do sistema.
        waits (UIWaits): Utilitário para operações de espera.
        rm_app (RMApplication): Instância do gerenciador de aplicação RM.
        
    Example:
        Uso básico:
        
        >>> locator_service = LocatorService("locators.yaml")
        >>> login_manager = RMStartLogin(locator_service)
        >>> success, app = login_manager.start_and_login("HML", "FIDI-ferias")
        >>> if success:
        ...     main_window = app.get_main_window()
        
        Uso com backend específico:
        
        >>> login_manager = RMStartLogin(locator_service, backend="win32")
        >>> success, app = login_manager.start_and_login("PROD", "FIDI-comum")
        
    Note:
        - Utiliza sanitização de logs para segurança
        - Captura screenshots automaticamente em caso de falha
        - Suporta ambientes HML e PROD
        - Integra com sistema de parâmetros para credenciais
    """
    
    def __init__(self, locator_service: LocatorService, backend: str = "uia") -> None:
        """Inicializa o gerenciador de login RM com configurações personalizáveis.
        
        Args:
            locator_service (LocatorService): Serviço de localização de elementos UI.
                Deve estar configurado com arquivo de locators válido.
            backend (str, optional): Backend do pywinauto a ser utilizado.
                Opções: 'uia' (recomendado) ou 'win32'. Defaults to "uia".
                
        Raises:
            ValueError: Se locator_service for None ou backend inválido.
            
        Example:
            Inicialização básica:
            
            >>> locator_service = LocatorService("locators.yaml")
            >>> login_manager = RMStartLogin(locator_service)
            
            Com backend específico:
            
            >>> login_manager = RMStartLogin(locator_service, backend="win32")
            
        Note:
            O backend 'uia' é recomendado para aplicações modernas.
            O locator_service deve estar configurado antes da inicialização.
        """
        if locator_service is None:
            raise ValueError("Parâmetro 'locator_service' não pode ser None")
        
        # Validar backend
        valid_backends = {'uia', 'win32'}
        if backend not in valid_backends:
            raise ValueError(f"Backend deve ser um de {valid_backends}, recebido: {backend}")
            
        self.locator_service = locator_service
        self.config = get_ui_config()
        self.waits = UIWaits()
        self.rm_app = RMApplication(backend=backend)
    
    def start_and_login(self, ambiente: str, produto: str) -> Tuple[bool, Optional[RMApplication]]:
        """Executa processo completo de inicialização e login no TOTVS RM.
        
        Este método coordena todo o processo de login, desde a inicialização
        da aplicação até a validação de login bem-sucedido.
        
        Args:
            ambiente (str): Ambiente de execução ('HML' ou 'PROD').
            produto (str): Nome do produto para busca de credenciais.
                Usado para obter parâmetros APP_USER e APP_PASSWORD.
                
        Returns:
            Tuple[bool, Optional[RMApplication]]: Tupla contendo:
                - bool: True se login bem-sucedido, False caso contrário
                - RMApplication: Instância da aplicação se sucesso, None se falha
                
        Raises:
            ValueError: Se ambiente não for 'HML' ou 'PROD', ou produto vazio.
            UIConnectionError: Se falhar ao iniciar a aplicação.
            UIElementNotFoundError: Se elementos de login não forem encontrados.
            UIInteractionError: Se falhar ao interagir com elementos.
            UITimeoutError: Se operações excederem timeout.
            
        Example:
            Login em homologação:
            
            >>> success, app = login_manager.start_and_login("HML", "FIDI-ferias")
            >>> if success:
            ...     print("Login realizado com sucesso")
            ...     main_window = app.get_main_window()
            
            Login em produção:
            
            >>> success, app = login_manager.start_and_login("PROD", "FIDI-comum")
            
        Note:
            - Captura screenshots automaticamente em caso de falha
            - Utiliza sistema de parâmetros para obter credenciais
            - Aguarda aplicação ficar completamente pronta após login
            - Logs detalhados para troubleshooting
        """
        if not ambiente or ambiente.upper() not in ['HML', 'PROD']:
            raise ValueError("Ambiente deve ser 'HML' ou 'PROD'")
        if not produto:
            raise ValueError("Produto não pode ser vazio")
        
        try:
            safe_ambiente = sanitize_for_log(ambiente)
            safe_produto = sanitize_for_log(produto)
            logger.info(f"Iniciando login RM - Ambiente: {safe_ambiente}, Produto: {safe_produto}")
            self._start_application()
            login_window = self._get_login_window()
            user, password = self._get_credentials(ambiente, produto)
            self._fill_login_fields(login_window, user, password)
            self._select_environment(login_window, ambiente, produto)
            self._click_login_button(login_window)
            self._wait_for_login_complete()
            logger.info("Login RM realizado com sucesso")
            return True, self.rm_app
        except Exception as e:
            safe_error = sanitize_for_log(str(e))
            error_msg = f"Erro durante login RM: {safe_error}"
            logger.error(error_msg, exc_info=True)
            capture_screenshot_on_error("rm_start_login_failed")
            return False, None

    def _start_application(self) -> None:
        """Inicia a aplicação TOTVS RM com tempo de espera estendido.
        
        Raises:
            UIConnectionError: Se falhar ao iniciar a aplicação.
            
        Note:
            Usa tempo de espera de 15 segundos para estabilização da aplicação.
        """
        try:
            logger.info("Iniciando aplicação RM...")
            self.rm_app.start_application(wait_time=15)
            logger.info("Aplicação RM iniciada com sucesso")
        except Exception as e:
            safe_error = sanitize_for_log(str(e))
            raise UIConnectionError(f"Falha ao iniciar aplicação RM: {safe_error}", str(e))
    
    def _get_login_window(self):
        """Localiza e retorna a janela de login usando auto_id confiável.
        
        Returns:
            WindowSpecification: Janela de login pronta para interação.
            
        Raises:
            UIElementNotFoundError: Se janela de login não for encontrada ou
                não ficar pronta no tempo esperado (45 segundos).
                
        Note:
            Usa auto_id 'RMSFormLoginUX' que é o identificador mais estável
            para a janela de login do TOTVS RM.
        """
        try:
            logger.info("Procurando pela janela de login (auto_id='RMSFormLoginUX')...")
            app_instance = self.rm_app.app
            login_window = app_instance.window(auto_id="RMSFormLoginUX")
            login_window.wait('ready', timeout=45)
            logger.info("Janela de login encontrada e pronta.")
            return login_window
        except (ElementNotFoundError, PywinautoTimeoutError) as e:
            safe_error = sanitize_for_log(str(e))
            error_msg = f"Falha crítica ao obter a janela de login (auto_id='RMSFormLoginUX'): {safe_error}"
            logger.error(error_msg)
            capture_screenshot_on_error("get_login_window_failed")
            raise UIElementNotFoundError(error_msg, str(e))

    def _get_credentials(self, ambiente: str, produto: str) -> Tuple[str, str]:
        """Obtém credenciais do sistema de parâmetros.
        
        Args:
            ambiente (str): Ambiente para busca de parâmetros.
            produto (str): Produto para busca de parâmetros.
            
        Returns:
            Tuple[str, str]: Tupla contendo (usuário, senha).
            
        Raises:
            ValueError: Se credenciais não forem encontradas ou estiverem vazias.
            
        Note:
            Busca parâmetros APP_USER e APP_PASSWORD no sistema de configuração.
        """
        try:
            parametros = Parametros(ambiente=ambiente, produto=produto)
            user = parametros.get_parametro("APP_USER")
            password = parametros.get_parametro("APP_PASSWORD")
            if not user or not password:
                raise ValueError("Credenciais 'APP_USER' ou 'APP_PASSWORD' não encontradas")
            return user, password
        except Exception as e:
            safe_error = sanitize_for_log(str(e))
            raise ValueError(f"Erro ao obter credenciais: {safe_error}")

    def _fill_login_fields(self, login_window, user: str, password: str) -> None:
        """Preenche os campos de usuário e senha com esperas robustas.
        
        Args:
            login_window: Janela de login onde estão os campos.
            user (str): Nome de usuário para preenchimento.
            password (str): Senha para preenchimento.
            
        Raises:
            UIElementNotFoundError: Se campos não forem encontrados ou não
                ficarem prontos no tempo esperado.
            UIInteractionError: Se falhar ao preencher os campos.
            
        Note:
            - Usa auto_ids 'cUser' e 'cPassword' para localizar campos
            - Desenha outline nos campos para debug visual
            - Aguarda campos ficarem visíveis e habilitados
        """
        try:
            logger.debug("Aguardando campo de usuário (auto_id='cUser')...")
            user_field = login_window.child_window(auto_id="cUser", control_type="Edit")
            user_field.wait('visible enabled', timeout=20)
            user_field.draw_outline()
            user_field.set_edit_text(user)
            logger.debug("Campo usuário preenchido")
            
            logger.debug("Aguardando campo de senha (auto_id='cPassword')...")
            password_field = login_window.child_window(auto_id="cPassword", control_type="Edit")
            password_field.wait('visible enabled', timeout=10)
            password_field.draw_outline()
            password_field.set_edit_text(password)
            logger.debug("Campo senha preenchido")
            
        except (ElementNotFoundError, PywinautoTimeoutError) as e:
            safe_error = sanitize_for_log(str(e))
            error_msg = f"Campos de login não encontrados ou não ficaram prontos a tempo: {safe_error}"
            logger.error(error_msg)
            raise UIElementNotFoundError(error_msg, str(e))
        except Exception as e:
            safe_error = sanitize_for_log(str(e))
            raise UIInteractionError(f"Erro ao preencher campos de login: {safe_error}", str(e))

    def _select_environment(self, login_window, ambiente: str, produto: str) -> None:
        """Seleciona o ambiente apropriado na tela de login.
        
        Args:
            login_window: Janela de login onde está o seletor de ambiente.
            ambiente (str): Ambiente a ser selecionado ('HML' ou 'PROD').
            produto (str): Produto para identificação do ambiente correto.
            
        Raises:
            UIInteractionError: Se falhar na seleção do ambiente.
            
        Note:
            Utiliza RMLoginEnvSelector para lógica específica de seleção.
        """
        try:
            env_selector = RMLoginEnvSelector(login_window, self.locator_service)
            success, selected_alias = env_selector.select_environment(ambiente, produto)
            if not success:
                raise UIInteractionError("Falha na seleção do ambiente")
            safe_alias = sanitize_for_log(selected_alias)
            logger.info(f"Ambiente selecionado: {safe_alias}")
        except Exception as e:
            safe_error = sanitize_for_log(str(e))
            raise UIInteractionError(f"Erro na seleção do ambiente: {safe_error}", str(e))

    def _click_login_button(self, login_window) -> None:
        """Clica no botão Entrar e aguarda processamento.
        
        Args:
            login_window: Janela de login onde está o botão Entrar.
            
        Raises:
            UIElementNotFoundError: Se botão Entrar não for encontrado.
            UIInteractionError: Se falhar ao clicar no botão.
            
        Note:
            Aguarda tempo configurável para a MainForm carregar após o clique.
        """
        try:
            login_button = login_window.child_window(title="Entrar", control_type="Button")
            login_button.wait('ready', timeout=10)
            login_button.click()
            wait_time = getattr(self.config, 'wait_before_next_window', 15.0)
            logger.info(f"Botão Entrar clicado. Aguardando {wait_time}s para a MainForm carregar...")
            time.sleep(wait_time)
        except (ElementNotFoundError, PywinautoTimeoutError) as e:
            safe_error = sanitize_for_log(str(e))
            raise UIElementNotFoundError(f"Botão Entrar não encontrado: {safe_error}", str(e))
        except Exception as e:
            safe_error = sanitize_for_log(str(e))
            raise UIInteractionError(f"Erro ao clicar no botão Entrar: {safe_error}", str(e))

    def _wait_for_login_complete(self) -> None:
        """Aguarda a aplicação ficar pronta após o login, procurando pela MainForm.
        
        Raises:
            UITimeoutError: Se a MainForm não aparecer no tempo esperado (60 segundos).
            
        Note:
            Valida que o login foi bem-sucedido verificando se a janela principal
            (MainForm) está visível e habilitada.
        """
        try:
            logger.info("Aguardando login ser completado e MainForm aparecer...")
            main_window = self.rm_app.get_main_window(auto_id="MainForm")
            main_window.wait('visible enabled', timeout=60)
            logger.info("Login completado - MainForm está pronta.")
        except (ElementNotFoundError, PywinautoTimeoutError) as e:
            safe_error = sanitize_for_log(str(e))
            raise UITimeoutError(f"Timeout: A janela principal (MainForm) não apareceu após o login. Erro: {safe_error}", str(e))

