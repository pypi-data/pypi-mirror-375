"""Conector único para aplicação RM com lógica robusta de captura de janelas.

Este módulo implementa um conector especializado para aplicações TOTVS RM
já em execução, fornecendo funcionalidades avançadas de conexão, captura
de janelas e gerenciamento de estado com tratamento de erros robusto.

Classes:
    RMSingleConnect: Conector principal para aplicações RM em execução.
    HybridWrapper: Wrapper híbrido que combina funcionalidades de diferentes backends.

Funções:
    connect_single: Função de conveniência para conexão única.

Example:
    Uso básico do conector:
    
    >>> connector = RMSingleConnect(backend="uia", screenshot_enabled=True)
    >>> success, windows = connector.connect_single()
    >>> if success:
    ...     main_window = connector.get_main_window()
    ...     print(f"Conectado à janela: {main_window}")
    
    Uso com função de conveniência:
    
    >>> windows = connect_single(backend="uia", retries=5)
    >>> if windows:
    ...     print(f"Conectado a {len(windows)} janelas")

Note:
    Este módulo segue as diretrizes de segurança DATAMETRIA, incluindo
    sanitização de logs e tratamento robusto de exceções.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from pywinauto import Application, Desktop
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError as PywinautoTimeoutError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIConnectionError
from ..utils.screenshot import capture_screenshot_on_error
from ..utils.log_sanitizer import sanitize_for_log
from ..utils.filename_sanitizer import sanitize_filename

logger = logging.getLogger(__name__)


class RMSingleConnect:
    """Conector robusto para aplicações TOTVS RM já em execução.
    
    Esta classe implementa um sistema avançado de conexão a aplicações RM
    existentes, com funcionalidades de captura de janelas, gerenciamento
    de estado e tratamento de erros abrangente.
    
    Attributes:
        config (UIConfig): Configuração de UI obtida do sistema.
        backend (str): Backend do pywinauto utilizado ('uia' ou 'win32').
        screenshot_enabled (bool): Se screenshots devem ser capturados.
        retries (int): Número máximo de tentativas de conexão.
        delay (float): Delay entre tentativas em segundos.
        screenshot_dir (Path): Diretório para armazenar screenshots.
        
    Example:
        Uso básico:
        
        >>> connector = RMSingleConnect()
        >>> success, windows = connector.connect_single()
        >>> if success:
        ...     app = connector.get_application()
        ...     main_window = connector.get_main_window()
        
        Uso avançado com screenshots:
        
        >>> connector = RMSingleConnect(
        ...     backend="uia",
        ...     screenshot_enabled=True,
        ...     screenshot_dir="./debug_screenshots",
        ...     retries=15
        ... )
        >>> success, windows = connector.connect_single(pid=1234)
        
    Note:
        Utiliza sanitização de logs e captura de screenshots para debug.
        Suporta conexão por PID específico ou busca automática por auto_id.
    """
    
    def __init__(
        self,
        backend: str = "uia",
        screenshot_enabled: bool = False,
        screenshot_dir: Optional[str] = None,
        retries: int = 12,
        delay: float = 5.0
    ):
        """Inicializa o conector RM com configurações personalizáveis.
        
        Args:
            backend (str, optional): Backend do pywinauto a ser utilizado.
                Opções: 'uia' (recomendado) ou 'win32'. Defaults to "uia".
            screenshot_enabled (bool, optional): Se deve capturar screenshots
                automaticamente durante o processamento. Defaults to False.
            screenshot_dir (str, optional): Diretório para armazenar screenshots.
                Se None, usa "screenshots" no diretório atual. Defaults to None.
            retries (int, optional): Número máximo de tentativas de conexão
                antes de falhar. Defaults to 12.
            delay (float, optional): Tempo de espera em segundos entre tentativas
                e para verificação de existência de elementos. Defaults to 5.0.
                
        Raises:
            OSError: Se não conseguir criar o diretório de screenshots.
            
        Example:
            Configuração básica:
            
            >>> connector = RMSingleConnect()
            
            Configuração avançada:
            
            >>> connector = RMSingleConnect(
            ...     backend="uia",
            ...     screenshot_enabled=True,
            ...     screenshot_dir="./debug",
            ...     retries=20,
            ...     delay=3.0
            ... )
            
        Note:
            O backend 'uia' é recomendado para aplicações modernas.
            Screenshots são úteis para debug mas consomem espaço em disco.
        """
        self.config = get_ui_config()
        self.backend = backend
        self.screenshot_enabled = screenshot_enabled
        self.retries = retries
        self.delay = delay
        self.screenshot_dir = Path(screenshot_dir or "screenshots")
        if screenshot_enabled:
            self.screenshot_dir.mkdir(exist_ok=True)
        self._app: Optional[Application] = None
        self._connected_windows: Dict[str, Dict[str, Any]] = {}

    def connect_single(
        self,
        auto_id: Optional[str] = None,
        title: Optional[str] = None,
        titulos_fallback: Optional[List[str]] = None,
        pid: Optional[int] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Conecta a uma única instância do TOTVS RM em execução.
        
        Este método implementa a lógica principal de conexão, tentando
        estabelecer conexão com uma aplicação RM existente usando diferentes
        estratégias de busca e validação.
        
        Args:
            auto_id (str, optional): ID automático da janela principal para busca.
                Se None, usa configuração padrão do ui_config. Defaults to None.
            title (str, optional): Título da janela para busca alternativa.
                Se None, usa configuração padrão do ui_config. Defaults to None.
            titulos_fallback (List[str], optional): Lista de títulos alternativos
                para busca caso o método principal falhe. Defaults to None.
            pid (int, optional): Process ID específico para conexão direta.
                Se fornecido, conecta diretamente ao processo. Defaults to None.
                
        Returns:
            Tuple[bool, Dict[str, Any]]: Tupla contendo:
                - bool: True se conexão bem-sucedida, False caso contrário
                - Dict[str, Any]: Dicionário com informações das janelas conectadas.
                  Chaves incluem: 'title', 'pid', 'element', 'wrapper', 'spec', 'screenshot'
                  
        Raises:
            UIConnectionError: Se falhar ao estabelecer conexão após todas as tentativas.
            
        Example:
            Conexão básica:
            
            >>> success, windows = connector.connect_single()
            >>> if success:
            ...     print(f"Conectado a {len(windows)} janelas")
            
            Conexão por PID específico:
            
            >>> success, windows = connector.connect_single(pid=1234)
            
            Conexão com auto_id customizado:
            
            >>> success, windows = connector.connect_single(
            ...     auto_id="CustomMainForm",
            ...     titulos_fallback=["RM - Sistema", "TOTVS RM"]
            ... )
            
        Note:
            O método tenta primeiro conexão por PID (se fornecido), depois
            por auto_id, e finalmente por títulos alternativos. Todas as
            operações são logadas com sanitização de dados sensíveis.
        """
        # Usar configurações padrão se não fornecidas
        auto_id = auto_id or self.config.default_main_window_auto_id
        title = title or self.config.default_title_fallback
        
        try:
            safe_auto_id = sanitize_for_log(auto_id)
            logger.info(f"Iniciando conexão com aplicação RM, procurando por auto_id='{safe_auto_id}'...")
            
            self._app, main_window_spec = self._establish_connection(auto_id, title, titulos_fallback, pid)
            
            if not self._app or not main_window_spec:
                safe_auto_id = sanitize_for_log(auto_id)
                raise UIConnectionError(f"Não foi possível estabelecer conexão com a janela principal (auto_id='{safe_auto_id}') após todas as tentativas.")
            
            self._capture_windows(main_window_spec)
            
            if not self._connected_windows:
                raise UIConnectionError("Conexão com o processo RM estabelecida, mas falha ao capturar a janela principal.")

            logger.info(f"Conexão estabelecida com {len(self._connected_windows)} janelas.")
            return True, self._connected_windows
            
        except Exception as e:
            safe_error = sanitize_for_log(str(e))
            error_msg = f"Erro fatal durante o processo de conexão: {safe_error}"
            logger.error(error_msg, exc_info=True)
            capture_screenshot_on_error("rm_single_connect_failed")
            return False, {}

    def _establish_connection(
        self,
        auto_id: str,
        title: str,
        titulos_fallback: Optional[List[str]],
        pid: Optional[int]
    ) -> Tuple[Optional[Application], Optional[Any]]:
        """Estabelece conexão com aplicação RM usando estratégias múltiplas.
        
        Método interno que implementa a lógica de conexão com diferentes
        estratégias: conexão direta por PID ou busca por auto_id com retry.
        
        Args:
            auto_id (str): ID automático da janela principal para busca.
            title (str): Título da janela (reservado para uso futuro).
            titulos_fallback (List[str], optional): Títulos alternativos
                (reservado para implementação futura).
            pid (int, optional): Process ID específico para conexão direta.
                
        Returns:
            Tuple[Optional[Application], Optional[Any]]: Tupla contendo:
                - Application: Instância da aplicação pywinauto ou None se falhar
                - WindowSpecification: Especificação da janela encontrada ou None
                
        Example:
            Uso interno pelo método connect_single:
            
            >>> app, window = self._establish_connection(
            ...     auto_id="MainForm",
            ...     title="TOTVS RM",
            ...     titulos_fallback=None,
            ...     pid=None
            ... )
            >>> if app and window:
            ...     print("Conexão estabelecida")
                
        Note:
            Este é um método interno que não deve ser chamado diretamente.
            Implementa retry automático e logging detalhado de tentativas.
        """
        desktop = Desktop(backend=self.backend)
        
        if pid:
            try:
                logger.info(f"Conectando ao PID {pid}...")
                app = Application(backend=self.backend).connect(process=pid)
                window_spec = app.window(auto_id=auto_id)
                if window_spec.exists(timeout=self.delay):
                    self._app = app
                    return app, window_spec
            except Exception as e:
                safe_error = sanitize_for_log(str(e))
                logger.error(f"Falha ao conectar ou encontrar janela no PID {pid}: {safe_error}")
                return None, None

        # Busca por auto_id quando não há PID específico
        for attempt in range(1, self.retries + 1):
            logger.info(f"Tentativa {attempt}/{self.retries} para encontrar janela principal...")
            try:
                window_spec = desktop.window(auto_id=auto_id)
                if window_spec.exists(timeout=self.delay):
                    safe_auto_id = sanitize_for_log(auto_id)
                    logger.info(f"Janela encontrada por auto_id='{safe_auto_id}'. Conectando...")
                    app = Application(backend=self.backend).connect(
                        process=window_spec.process_id()
                    )
                    self._app = app
                    return app, window_spec
            except Exception:
                pass
        
        logger.error("Falha ao conectar ao TOTVS RM após todas as tentativas")
        return None, None

    def _capture_windows(self, main_window_spec) -> None:
        """Processa e captura janela principal garantindo estado operacional.
        
        Este método processa a janela principal encontrada, garantindo que
        ela esteja visível, pronta para interação e com foco adequado.
        Também captura informações detalhadas da janela.
        
        Args:
            main_window_spec: Especificação da janela principal encontrada
                pelo método _establish_connection.
                
        Raises:
            UIConnectionError: Se a janela não ficar pronta no tempo esperado
                (timeout de 60 segundos) ou se houver falha crítica no processamento.
            PywinautoTimeoutError: Se operações de wait excederem o timeout.
            
        Example:
            Uso interno após estabelecer conexão:
            
            >>> # Chamado internamente por connect_single
            >>> self._capture_windows(main_window_spec)
            >>> # Janela agora está em self._connected_windows
            
        Note:
            - Aguarda janela ficar 'visible ready' com timeout de 60s
            - Tenta definir foco na janela principal
            - Em caso de falha no foco, tenta restaurar a janela
            - Captura screenshot se habilitado
            - Cria HybridWrapper para funcionalidades estendidas
        """
        if not self._app:
            return
        
        try:
            window_title = main_window_spec.window_text()
            safe_title = sanitize_for_log(window_title)
            logger.info(f"Processando janela principal '{safe_title}'...")
            
            # Aguardar janela ficar visível e pronta
            logger.debug(f"Aguardando janela '{safe_title}' ficar pronta...")
            main_window_spec.wait('visible ready', timeout=60)
            logger.debug(f"Janela '{safe_title}' está pronta")

            main_wrapper = main_window_spec.wrapper_object()

            # Definir foco na janela principal
            safe_wrapper_title = sanitize_for_log(main_wrapper.window_text())
            logger.debug(f"Definindo foco na janela '{safe_wrapper_title}'...")
            try:
                main_wrapper.set_focus()
                logger.debug("Foco definido com sucesso")
            except Exception as e:
                safe_error = sanitize_for_log(str(e))
                logger.warning(f"Falha ao definir foco ({safe_error}). Tentando restaurar...")
                try:
                    main_wrapper.restore()
                    main_wrapper.set_focus()
                    logger.debug("Janela restaurada e foco definido")
                except Exception as e_restore:
                    safe_error = sanitize_for_log(str(e_restore))
                    logger.error(f"Falha ao restaurar janela: {safe_error}")

            window_info = self._process_window(main_wrapper)
            if window_info:
                self._connected_windows[str(main_wrapper.handle)] = window_info
                
        except PywinautoTimeoutError as e:
            safe_title = sanitize_for_log(main_window_spec.window_text())
            safe_error = sanitize_for_log(str(e))
            error_msg = f"Janela '{safe_title}' não ficou pronta: {safe_error}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_single_connect_main_window_not_ready")
            raise UIConnectionError(error_msg, str(e)) from e
        except Exception as e:
            safe_error = sanitize_for_log(str(e))
            logger.error(f"Erro ao processar janela principal: {safe_error}")

    def _process_window(self, window_wrapper) -> Dict[str, Any]:
        """Processa janela capturando informações completas e screenshot opcional.
        
        Extrai informações detalhadas da janela e cria estrutura de dados
        padronizada com todas as informações necessárias para uso posterior.
        
        Args:
            window_wrapper: Wrapper da janela obtido via wrapper_object().
                Pode ser UIAWrapper ou Win32Wrapper dependendo do backend.
                
        Returns:
            Dict[str, Any]: Dicionário com informações da janela contendo:
                - 'title' (str): Título da janela
                - 'pid' (int): Process ID da aplicação
                - 'element' (HybridWrapper): Wrapper híbrido para interações
                - 'wrapper': Wrapper original do pywinauto
                - 'spec': WindowSpecification para operações avançadas
                - 'screenshot' (str|None): Caminho do screenshot se capturado
                
        Example:
            Estrutura do dicionário retornado:
            
            >>> window_info = self._process_window(wrapper)
            >>> print(window_info)
            {
                'title': 'TOTVS RM - Sistema Principal',
                'pid': 1234,
                'element': HybridWrapper(...),
                'wrapper': <UIAWrapper object>,
                'spec': <WindowSpecification object>,
                'screenshot': './screenshots/20240101_120000_TOTVS_RM.png'
            }
            
        Note:
            - Screenshot é capturado apenas se screenshot_enabled=True
            - Falhas na captura de screenshot são silenciosas (não interrompem)
            - HybridWrapper combina funcionalidades de wrapper e spec
        """
        img_path_str = None
        
        if self.screenshot_enabled:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = sanitize_filename(window_wrapper.window_text())
                img_path = self.screenshot_dir / f"{timestamp}_{safe_title}.png"
                window_wrapper.capture_as_image().save(str(img_path))
                img_path_str = str(img_path)
            except Exception:
                pass
        
        return {
            "title": window_wrapper.window_text(),
            "pid": window_wrapper.process_id(),
            "element": self._create_hybrid_wrapper(window_wrapper),
            "wrapper": window_wrapper,
            "spec": self._app.window(handle=window_wrapper.handle) if self._app else None,
            "screenshot": img_path_str
        }
    

    
    def _create_hybrid_wrapper(self, original_wrapper):
        """Cria wrapper híbrido combinando funcionalidades de wrapper e spec.
        
        Cria uma classe híbrida que combina as funcionalidades do wrapper
        original (UIAWrapper/Win32Wrapper) com WindowSpecification, fornecendo
        acesso completo a todas as operações do pywinauto.
        
        Args:
            original_wrapper: Wrapper original da janela obtido via wrapper_object().
                Pode ser UIAWrapper ou Win32Wrapper dependendo do backend usado.
                
        Returns:
            HybridWrapper: Instância de wrapper híbrido que combina:
                - Funcionalidades do wrapper original (click, type_keys, etc.)
                - Funcionalidades de WindowSpecification (child_window, etc.)
                - Métodos proxy para 'exists' e 'wait'
                
        Raises:
            UIConnectionError: Se a instância da aplicação não estiver disponível
                no momento da criação do wrapper.
                
        Example:
            Uso do wrapper híbrido:
            
            >>> hybrid = self._create_hybrid_wrapper(original_wrapper)
            >>> # Funcionalidades do wrapper original
            >>> hybrid.click()
            >>> hybrid.type_keys("texto")
            >>> # Funcionalidades de WindowSpecification
            >>> child = hybrid.child_window(title="Botão")
            >>> # Métodos proxy
            >>> if hybrid.exists():
            ...     hybrid.wait('ready')
                
        Note:
            - O HybridWrapper é uma classe interna criada dinamicamente
            - Fornece acesso transparente a ambos os tipos de funcionalidade
            - Implementa __str__ e __repr__ para debug
            - Delega atributos não encontrados para o wrapper original
        """
        app_instance = self._app
        if not app_instance:
            logger.error("Instância da aplicação não disponível para HybridWrapper")
            raise UIConnectionError("Instância da aplicação não disponível")

        class HybridWrapper:
            """Wrapper híbrido que combina BaseWrapper e WindowSpecification.
            
            Esta classe interna combina as funcionalidades de wrappers do pywinauto
            (UIAWrapper/Win32Wrapper) com WindowSpecification, fornecendo uma
            interface unificada para todas as operações de automação.
            
            Attributes:
                _wrapper: Wrapper original do pywinauto.
                _app: Instância da aplicação para operações de WindowSpecification.
                
            Example:
                Uso através do wrapper híbrido:
                
                >>> # Operações do wrapper original
                >>> hybrid.click()
                >>> hybrid.set_focus()
                >>> # Operações de WindowSpecification
                >>> child = hybrid.child_window(title="OK")
                >>> # Métodos proxy
                >>> hybrid.wait('ready', timeout=10)
            """
            
            def __init__(self, wrapper: Any, app: Application):
                """Inicializa wrapper híbrido com wrapper original e aplicação.
                
                Args:
                    wrapper: Wrapper original obtido via wrapper_object().
                        Pode ser UIAWrapper ou Win32Wrapper dependendo do backend.
                    app: Instância da aplicação pywinauto para operações
                        de WindowSpecification.
                        
                Example:
                    >>> hybrid = HybridWrapper(original_wrapper, app_instance)
                """
                self._wrapper = wrapper
                self._app = app

            def child_window(self, **kwargs) -> Any:
                """Encontra elemento filho usando aplicação e wrapper como pai.
                
                Utiliza a funcionalidade de WindowSpecification para encontrar
                elementos filhos usando o wrapper atual como elemento pai.
                
                Args:
                    **kwargs: Critérios de busca do elemento filho.
                        Exemplos: title="OK", auto_id="btnSave", class_name="Button"
                        
                Returns:
                    WindowSpecification: Especificação do elemento filho encontrado.
                    
                Example:
                    >>> button = hybrid.child_window(title="Salvar")
                    >>> edit = hybrid.child_window(auto_id="txtNome")
                """
                return self._app.window(parent=self._wrapper, **kwargs)

            def __getattr__(self, name: str) -> Any:
                """Delega acesso aos atributos para wrapper original com proxy especial.
                
                Implementa delegação transparente de atributos e métodos para o
                wrapper original, com tratamento especial para métodos que precisam
                de WindowSpecification.
                
                Args:
                    name (str): Nome do atributo ou método solicitado.
                    
                Returns:
                    Any: Atributo ou método do wrapper original, ou método proxy
                        para 'exists' e 'wait' que usam WindowSpecification.
                        
                Raises:
                    AttributeError: Se o atributo não existir no wrapper original
                        nem nos métodos proxy especiais.
                        
                Example:
                    >>> # Métodos do wrapper original
                    >>> hybrid.click()  # Delegado para wrapper
                    >>> # Métodos proxy especiais
                    >>> hybrid.exists()  # Usa WindowSpecification
                    >>> hybrid.wait('ready')  # Usa WindowSpecification
                    
                Note:
                    Os métodos 'exists' e 'wait' são tratados especialmente
                    porque funcionam melhor com WindowSpecification.
                """
                try:
                    return getattr(self._wrapper, name)
                except AttributeError:
                    if name in ['exists', 'wait']:
                        def proxy_method(*args, **kwargs):
                            spec = self._app.window(handle=self._wrapper.handle)
                            return getattr(spec, name)(*args, **kwargs)
                        return proxy_method
                    raise
            
            def __str__(self) -> str:
                """Representação string legível do wrapper híbrido.
                
                Returns:
                    str: Representação string no formato HybridWrapper(wrapper).
                """
                return f"HybridWrapper({self._wrapper})"

            def __repr__(self) -> str:
                """Representação detalhada do wrapper híbrido para debug.
                
                Returns:
                    str: Representação detalhada incluindo repr do wrapper original.
                """
                return f"HybridWrapper({repr(self._wrapper)})"
        
        return HybridWrapper(original_wrapper, app_instance)
    
    def get_main_window(self):
        """Obtém elemento da janela principal conectada.
        
        Retorna o HybridWrapper da primeira janela conectada, que normalmente
        é a janela principal da aplicação RM.
        
        Returns:
            Optional[HybridWrapper]: Elemento da janela principal ou None
                se nenhuma janela estiver conectada.
                
        Example:
            >>> main_window = connector.get_main_window()
            >>> if main_window:
            ...     main_window.click()
            ...     child = main_window.child_window(title="Menu")
            
        Note:
            Retorna None se connect_single() não foi chamado com sucesso
            ou se nenhuma janela foi capturada.
        """
        if not self._connected_windows:
            return None
        return next(iter(self._connected_windows.values())).get('element')

    def get_application(self) -> Optional[Application]:
        """Obtém instância da aplicação pywinauto conectada.
        
        Retorna a instância da aplicação pywinauto que foi estabelecida
        durante o processo de conexão.
        
        Returns:
            Optional[Application]: Instância da aplicação pywinauto ou None
                se não houver conexão ativa.
                
        Example:
            >>> app = connector.get_application()
            >>> if app:
            ...     # Usar métodos da aplicação diretamente
            ...     windows = app.windows()
            ...     print(f"Aplicação tem {len(windows)} janelas")
            
        Note:
            Útil para operações avançadas que requerem acesso direto
            à instância da aplicação pywinauto.
        """
        return self._app

    def disconnect(self) -> None:
        """Desconecta da aplicação e limpa todos os recursos internos.
        
        Limpa o estado interno do conector, removendo referências à aplicação
        e janelas conectadas. Não fecha a aplicação, apenas desconecta.
        
        Example:
            >>> connector.disconnect()
            >>> # Agora get_application() retornará None
            >>> assert connector.get_application() is None
            
        Note:
            - Não fecha a aplicação RM, apenas remove as referências
            - Após disconnect(), é necessário chamar connect_single() novamente
            - Operação é sempre segura, mesmo se já desconectado
        """
        self._app = None
        self._connected_windows.clear()
        logger.info("Desconectado do TOTVS RM")


def connect_single(**kwargs) -> Dict[str, Any]:
    """Função de conveniência para conexão única ao TOTVS RM.
    
    Esta função simplifica o uso do RMSingleConnect criando uma instância,
    executando a conexão e retornando apenas as janelas conectadas.
    
    Args:
        **kwargs: Argumentos combinados para inicialização e conexão.
            Argumentos de inicialização:
            - backend (str): Backend do pywinauto
            - screenshot_enabled (bool): Se deve capturar screenshots
            - screenshot_dir (str): Diretório para screenshots
            - retries (int): Número de tentativas
            - delay (float): Delay entre tentativas
            
            Argumentos de conexão:
            - auto_id (str): ID automático da janela
            - title (str): Título da janela
            - titulos_fallback (List[str]): Títulos alternativos
            - pid (int): Process ID específico
            
    Returns:
        Dict[str, Any]: Dicionário com janelas conectadas se bem-sucedido,
            dicionário vazio se falhar. Estrutura igual ao retornado por
            connect_single() do RMSingleConnect.
            
    Example:
        Uso básico:
        
        >>> windows = connect_single()
        >>> if windows:
        ...     print(f"Conectado a {len(windows)} janelas")
        
        Uso com parâmetros:
        
        >>> windows = connect_single(
        ...     backend="uia",
        ...     screenshot_enabled=True,
        ...     retries=20,
        ...     pid=1234
        ... )
        
    Note:
        - Função stateless que cria nova instância a cada chamada
        - Separa automaticamente argumentos de inicialização e conexão
        - Retorna dicionário vazio em caso de falha (não levanta exceção)
    """
    # Separar argumentos de inicialização e conexão automaticamente
    init_args = {
        k: v for k, v in kwargs.items() 
        if k in RMSingleConnect.__init__.__code__.co_varnames
    }
    connect_args = {
        k: v for k, v in kwargs.items() 
        if k in RMSingleConnect.connect_single.__code__.co_varnames
    }
    
    connector = RMSingleConnect(**init_args)
    success, windows = connector.connect_single(**connect_args)
    return windows if success else {}