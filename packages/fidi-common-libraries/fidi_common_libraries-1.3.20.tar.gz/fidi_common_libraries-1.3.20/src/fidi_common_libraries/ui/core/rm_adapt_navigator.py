import logging
import time
from typing import Optional, Dict, Any, List, Tuple
from pywinauto.base_wrapper import BaseWrapper
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError as PywinautoTimeoutError
from pywinauto.application import WindowSpecification

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIElementNotFoundError, UIInteractionError, UITimeoutError
from ..utils.screenshot import capture_screenshot_on_error
from ..utils.log_sanitizer import sanitize_for_log

logger = logging.getLogger(__name__)


class RMAdaptNavigator:
    """Navegador adaptativo para aplicação TOTVS RM.
    
    Classe especializada para navegação robusta em interfaces do TOTVS RM,
    suportando diferentes tipos de wrapper (UIAWrapper, WindowSpecification,
    HybridWrapper) e navegação hierárquica através de múltiplos steps.
    
    Attributes:
        parent_element (BaseWrapper): Elemento pai para navegação.
        config: Configurações de UI obtidas do sistema.
    
    Example:
        Navegação simples:
        
        >>> navigator = RMAdaptNavigator(parent_element)
        >>> button = navigator.navigate_to_element(
        ...     title="Salvar",
        ...     control_type="Button",
        ...     click_element=True
        ... )
        
        Navegação hierárquica:
        
        >>> steps = [
        ...     {"title": "Menu", "control_type": "MenuItem", "click_element": True},
        ...     {"title": "Submenu", "control_type": "MenuItem", "click_element": False}
        ... ]
        >>> success, element_id = navigator.navigate_to_path(steps)
    
    Note:
        Esta classe implementa retry automático e logging sanitizado
        conforme padrões de segurança DATAMETRIA.
    """

    def __init__(self, parent_element: Any) -> None:
        """Inicializa o navegador adaptativo.
        
        Args:
            parent_element (Any): Elemento pai para navegação. Deve ser um
                wrapper válido (BaseWrapper, WindowSpecification ou HybridWrapper).
        
        Raises:
            ValueError: Se parent_element for None.
            TypeError: Se parent_element não for um wrapper válido.
        
        Example:
            >>> navigator = RMAdaptNavigator(main_window)
        """
        if parent_element is None:
            raise ValueError("Parâmetro 'parent_element' não pode ser None")

        if isinstance(parent_element, WindowSpecification):
            parent_element = parent_element.wrapper_object()

        if not self._is_valid_wrapper(parent_element):
            raise TypeError(f"Elemento pai inválido: {type(parent_element)}")

        self.parent_element = parent_element
        self.config = get_ui_config()

    def _is_valid_wrapper(self, element: Any) -> bool:
        """Verifica se o elemento é um wrapper válido.
        
        Args:
            element (Any): Elemento a ser validado.
        
        Returns:
            bool: True se for um wrapper válido, False caso contrário.
        """
        return (
            isinstance(element, BaseWrapper) or
            hasattr(element, '_wrapper') and hasattr(element, '_app') or
            "HybridWrapper" in type(element).__name__
        )

    def navigate_to_element(
        self,
        title: Optional[str] = None,
        auto_id: Optional[str] = None,
        control_type: Optional[str] = None,
        click_element: bool = False,
        wait_timeout: float = 30.0,
        debug: bool = False,
        outline_color: str = "green",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs: Any
    ) -> Optional[BaseWrapper]:
        """Localiza e retorna um elemento filho com base nos critérios informados.
        
        Executa busca robusta de elemento usando child_window() como método
        primário e fallback para busca manual através de children().
        
        Args:
            title (Optional[str], optional): Título do elemento. Defaults to None.
            auto_id (Optional[str], optional): ID de automação. Defaults to None.
            control_type (Optional[str], optional): Tipo de controle. Defaults to None.
            click_element (bool, optional): Se deve clicar no elemento encontrado.
                Defaults to False.
            wait_timeout (float, optional): Timeout para aguardar elemento.
                Defaults to 30.0.
            debug (bool, optional): Se deve exibir logs detalhados.
                Defaults to False.
            outline_color (str, optional): Cor do contorno para destacar elemento.
                Defaults to "green".
            max_retries (int, optional): Número máximo de tentativas.
                Defaults to 3.
            retry_delay (float, optional): Delay entre tentativas em segundos.
                Defaults to 1.0.
            **kwargs: Argumentos adicionais para busca.
        
        Returns:
            Optional[BaseWrapper]: Elemento encontrado e pronto para uso, ou None se não encontrado.
        
        Raises:
            ValueError: Se nenhum critério for fornecido.
            UIElementNotFoundError: Se elemento não for encontrado.
            UITimeoutError: Se elemento não ficar disponível no timeout.
            UIInteractionError: Se houver erro durante interação.
        
        Example:
            Busca simples:
            
            >>> element = navigator.navigate_to_element(
            ...     title="Salvar",
            ...     control_type="Button"
            ... )
            
            Busca com clique automático:
            
            >>> element = navigator.navigate_to_element(
            ...     title="OK",
            ...     control_type="Button",
            ...     click_element=True,
            ...     debug=True
            ... )
        
        Note:
            Pelo menos um critério (title, auto_id, control_type) deve ser fornecido.
            O método implementa retry automático e logging sanitizado.
        """

        if not any([title, auto_id, control_type]):
            raise ValueError("Pelo menos um critério (title, auto_id, control_type) deve ser fornecido")

        # Verificação mais robusta do estado do elemento pai
        try:
            if not self.parent_element.is_visible() or not self.parent_element.is_enabled():
                raise UIElementNotFoundError("O elemento pai da navegação não está visível ou habilitado.")
        except Exception as e:
            logger.warning(f"Não foi possível verificar estado do elemento pai: {e}")

        action = "Clicando em" if click_element else "Encontrando"
        criteria_log = f"title='{title}', auto_id='{auto_id}', control_type='{control_type}'"
        
        # Log do parent atual para debug hierárquico
        try:
            parent_info = f"'{self.parent_element.window_text()}'" if self.parent_element.window_text() else type(self.parent_element).__name__
        except:
            parent_info = type(self.parent_element).__name__
        
        logger.info(f"{action} elemento: {sanitize_for_log(criteria_log)} em parent={sanitize_for_log(parent_info)} (timeout: {wait_timeout}s)")

        # Retry logic
        for attempt in range(max_retries):
            try:
                found = self._find_element(title, auto_id, control_type, debug)
                
                if not found:
                    if attempt < max_retries - 1:
                        logger.warning(f"Tentativa {attempt + 1} falhou, tentando novamente em {retry_delay}s")
                        time.sleep(retry_delay)
                        continue
                    raise ElementNotFoundError(f"Nenhum elemento correspondeu aos critérios após {max_retries} tentativas")

                # Espera até visível/habilitado com timeout adequado
                if not self._wait_element_ready(found, wait_timeout):
                    raise UITimeoutError(f"Elemento não ficou disponível dentro do timeout de {wait_timeout}s")

                # Executa ação se solicitado
                if click_element:
                    self._perform_action(found, control_type, outline_color, criteria_log)
                else:
                    if debug:
                        found.draw_outline(colour=outline_color)
                    logger.debug(f"Elemento encontrado com sucesso: {sanitize_for_log(criteria_log)}")

                return found

            except (ElementNotFoundError, PywinautoTimeoutError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Tentativa {attempt + 1} falhou: {sanitize_for_log(str(e))}")
                    time.sleep(retry_delay)
                    continue
                
                error_msg = f"Elemento não encontrado após {max_retries} tentativas ({sanitize_for_log(criteria_log)}): {sanitize_for_log(str(e))}"
                logger.error(error_msg)
                capture_screenshot_on_error("rm_adapt_navigator_element_not_found")
                raise UIElementNotFoundError(error_msg, str(e)) from e
            except Exception as e:
                error_msg = f"Erro inesperado durante navegação adaptativa ({sanitize_for_log(criteria_log)}): {sanitize_for_log(str(e))}"
                logger.error(error_msg, exc_info=True)
                capture_screenshot_on_error("rm_adapt_navigator_failed")
                raise UIInteractionError(error_msg, str(e)) from e
        
        return None

    def _find_element(self, title: Optional[str], auto_id: Optional[str], control_type: Optional[str], debug: bool) -> Optional[BaseWrapper]:
        """Encontra elemento usando child_window() ou busca manual.
        
        Args:
            title (Optional[str]): Título do elemento.
            auto_id (Optional[str]): ID de automação do elemento.
            control_type (Optional[str]): Tipo de controle do elemento.
            debug (bool): Se deve exibir logs de debug.
        
        Returns:
            Optional[BaseWrapper]: Elemento encontrado ou None.
        """
        search_kwargs = {
            k: v for k, v in {
                "title": title,
                "auto_id": auto_id,
                "control_type": control_type,
            }.items() if v is not None
        }

        found = None
        
        # Tenta child_window() primeiro
        if hasattr(self.parent_element, "child_window"):
            try:
                element_spec = self.parent_element.child_window(**search_kwargs)
                # Verifica se é WindowSpecification antes de chamar wrapper_object()
                if hasattr(element_spec, 'wrapper_object'):
                    found = element_spec.wrapper_object()
                else:
                    found = element_spec
                if debug and found:
                    logger.debug(f"✅ Elemento encontrado via child_window(): {sanitize_for_log(str(found))}")
            except Exception as e:
                logger.debug(f"child_window() falhou, tentando busca manual: {sanitize_for_log(str(e))}")

        # Fallback para busca manual
        if not found:
            children = self.parent_element.children()
            logger.debug(f"DEBUG: Procurando entre {len(children)} filhos para {sanitize_for_log(str(search_kwargs))}")
            
            for child in children:
                try:
                    c_type = child.friendly_class_name()
                    c_title = child.window_text()
                    
                    # ✅ CORREÇÃO CRÍTICA: Chamar automation_id() como método
                    c_auto_id = None
                    try:
                        if hasattr(child, 'automation_id'):
                            c_auto_id = child.automation_id()
                    except Exception as e:
                        logger.debug(f"Erro ao obter automation_id: {sanitize_for_log(str(e))}")
                    
                    if debug:
                        logger.info(f"    Filho encontrado: type='{sanitize_for_log(c_type)}', title='{sanitize_for_log(c_title)}', auto_id='{sanitize_for_log(str(c_auto_id))}'")
                    
                    # Verificação completa incluindo auto_id
                    title_match = not title or c_title == title
                    type_match = not control_type or c_type == control_type
                    auto_id_match = not auto_id or c_auto_id == auto_id
                    
                    if title_match and type_match and auto_id_match:
                        found = child
                        if debug:
                            logger.info(f"  ✅ MATCH encontrado: type='{sanitize_for_log(c_type)}', title='{sanitize_for_log(c_title)}', auto_id='{sanitize_for_log(str(c_auto_id))}'")
                        break
                        
                except Exception as e:
                    logger.debug(f"Erro ao processar filho: {sanitize_for_log(str(e))}")
                    continue

        return found

    def _wait_element_ready(self, element: BaseWrapper, timeout: float) -> bool:
        """Espera elemento ficar visível e habilitado.
        
        Args:
            element (BaseWrapper): Elemento a aguardar.
            timeout (float): Timeout em segundos.
        
        Returns:
            bool: True se elemento ficou pronto, False caso contrário.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if element.is_visible() and element.is_enabled():
                    return True
            except Exception as e:
                logger.debug(f"Erro na verificação de estado: {sanitize_for_log(str(e))}")
            time.sleep(0.5)
        
        logger.warning(f"Elemento não ficou pronto dentro do timeout de {timeout}s")
        return False

    def _perform_action(self, element: BaseWrapper, control_type: Optional[str], outline_color: str, criteria_log: str) -> None:
        """Executa ação no elemento (clique ou seleção).
        
        Args:
            element (BaseWrapper): Elemento para executar ação.
            control_type (Optional[str]): Tipo de controle do elemento.
            outline_color (str): Cor do contorno para destacar elemento.
            criteria_log (str): Critérios de busca para log.
        
        Raises:
            Exception: Se falhar ao executar a ação.
        """
        try:
            element.draw_outline(colour=outline_color)
            time.sleep(getattr(self.config, "wait_before_click", 0.1))
            
            if control_type == "TabItem":
                getattr(element, 'select', lambda: element.click_input())()
                logger.info(f"✅ Ação de seleção executada com sucesso: {sanitize_for_log(criteria_log)}")
            else:
                element.click_input(double=False)
                logger.info(f"✅ Ação de clique executada com sucesso: {sanitize_for_log(criteria_log)}")
        except Exception as e:
            logger.error(f"❌ Erro ao executar ação: {sanitize_for_log(str(e))}")
            raise

    def navigate_to_path(
        self,
        steps: List[Dict[str, Any]],
        outline_color: str = "green",
        debug: bool = False
    ) -> Tuple[bool, str]:
        """Executa navegação sequencial hierárquica.
        
        Navega através de múltiplos elementos de forma hierárquica,
        onde cada step usa o elemento encontrado no step anterior
        como parent para o próximo.
        
        Args:
            steps (List[Dict[str, Any]]): Lista de passos de navegação.
                Cada step deve conter 'title', 'control_type', 'auto_id'
                e opcionalmente 'click_element' e 'wait_timeout'.
            outline_color (str, optional): Cor do contorno para destacar elementos.
                Defaults to "green".
            debug (bool, optional): Se deve exibir logs detalhados.
                Defaults to False.
        
        Returns:
            Tuple[bool, str]: (sucesso, identificador_do_último_elemento)
        
        Raises:
            ValueError: Se lista de steps estiver vazia ou step inválido.
        
        Example:
            >>> steps = [
            ...     {"title": "Arquivo", "control_type": "MenuItem", "click_element": True},
            ...     {"title": "Salvar", "control_type": "Button", "click_element": False}
            ... ]
            >>> success, last_id = navigator.navigate_to_path(steps)
        """
        if not steps:
            raise ValueError("Lista de steps não pode estar vazia")

        logger.info(f"🚀 Iniciando navegação hierárquica com {len(steps)} passos")
        last_identifier = "UNKNOWN"
        current_parent = self.parent_element

        for i, step in enumerate(steps, 1):
            if not isinstance(step, dict) or not step:
                raise ValueError(f"Critérios inválidos no passo {i}: {step}")

            title = step.get("title")
            auto_id = step.get("auto_id")
            control_type = step.get("control_type")
            click_element = step.get("click_element", False)
            last_identifier = title or auto_id or control_type or f"Step_{i}"

            if debug:
                try:
                    parent_info = current_parent.window_text() or type(current_parent).__name__
                    parent_handle = getattr(current_parent, 'handle', 'N/A')
                except:
                    parent_info = type(current_parent).__name__
                    parent_handle = 'N/A'
                logger.info(f"\n🔍 Step {i}: Buscando em parent='{sanitize_for_log(parent_info)}' (handle={parent_handle})")
                logger.info(f"    Critérios: control_type='{sanitize_for_log(str(control_type))}' title='{sanitize_for_log(str(title))}' auto_id='{sanitize_for_log(str(auto_id))}'")

            try:
                # ✅ CORREÇÃO CRÍTICA: Busca direta sem criar novo navigator
                found = None
                children = current_parent.children()
                
                if debug:
                    logger.info(f"  📋 Total de filhos: {len(children)}")
                
                for child in children:
                    try:
                        c_type = child.friendly_class_name()
                        c_title = child.window_text()
                        
                        # Obter auto_id corretamente
                        c_auto_id = None
                        try:
                            if hasattr(child, 'automation_id'):
                                c_auto_id = child.automation_id()
                        except:
                            pass
                        
                        if debug:
                            logger.info(f"    📄 Filho: type='{sanitize_for_log(c_type)}', title='{sanitize_for_log(c_title)}', auto_id='{sanitize_for_log(str(c_auto_id))}'")
                        
                        # Verificação de match
                        title_match = not title or c_title == title
                        type_match = not control_type or c_type == control_type
                        auto_id_match = not auto_id or c_auto_id == auto_id
                        
                        if title_match and type_match and auto_id_match:
                            found = child
                            if debug:
                                logger.info(f"  ✅ MATCH encontrado: {sanitize_for_log(c_type)} - '{sanitize_for_log(c_title)}' - auto_id:'{sanitize_for_log(str(c_auto_id))}'")
                            break
                            
                    except Exception as e:
                        logger.debug(f"Erro ao processar filho: {e}")
                        continue
                
                if not found:
                    error_msg = f"Elemento não encontrado no step {i}: {sanitize_for_log(str(step))}"
                    logger.error(error_msg)
                    capture_screenshot_on_error("rm_adapt_navigator_path_failed")
                    return False, last_identifier
                
                # Verificar se elemento está pronto
                timeout = step.get("wait_timeout", 10.0)
                start_time = time.time()
                while time.time() - start_time < timeout:
                    try:
                        if found.is_visible() and found.is_enabled():
                            break
                    except:
                        pass
                    time.sleep(0.5)
                else:
                    if debug:
                        logger.warning(f"  ⏰ Elemento não ficou pronto no timeout de {timeout}s")
                
                # Executar ação se necessário
                if click_element:
                    try:
                        found.draw_outline(colour=outline_color)
                        time.sleep(getattr(self.config, "wait_before_click", 0.1))
                        
                        if control_type == "TabItem":
                            if hasattr(found, 'select'):
                                found.select()
                            else:
                                found.click_input()
                            if debug:
                                logger.info(f"  🖱️ Seleção executada no step {i}")
                        else:
                            found.click_input(double=False)
                            if debug:
                                logger.info(f"  🖱️ Clique executado no step {i}")
                    except Exception as e:
                        error_msg = f"Erro ao executar ação no step {i}: {sanitize_for_log(str(e))}"
                        logger.error(error_msg)
                        return False, last_identifier
                else:
                    if debug:
                        found.draw_outline(colour=outline_color)
                
                # ✅ ATUALIZAR current_parent para navegação hierárquica
                current_parent = found
                
                try:
                    last_identifier = found.window_text() or last_identifier
                except Exception:
                    pass
                
                if debug:
                    try:
                        next_parent_info = current_parent.window_text() or type(current_parent).__name__
                        logger.info(f"  ✅ Step {i} concluído. Próximo parent: '{sanitize_for_log(next_parent_info)}'")
                    except:
                        logger.info(f"  ✅ Step {i} concluído")
                    
            except Exception as e:
                logger.error(f"❌ Navegação hierárquica falhou no passo {i} ({sanitize_for_log(last_identifier)}): {sanitize_for_log(str(e))}")
                capture_screenshot_on_error("rm_adapt_navigator_path_failed")
                return False, last_identifier

        logger.info(f"🎉 Navegação hierárquica concluída com sucesso. Último elemento: {sanitize_for_log(last_identifier)}")
        return True, last_identifier

    def navigate_to_path_debug(self, steps: List[Dict[str, Any]], outline_color: str = "green") -> Optional[BaseWrapper]:
        """Versão debug da navegação hierárquica com logs detalhados.
        
        Executa navegação passo a passo com logging detalhado para debug,
        mantendo a lógica robusta de navegação hierárquica.
        
        Args:
            steps (List[Dict[str, Any]]): Lista de passos de navegação.
            outline_color (str, optional): Cor do contorno para destacar elementos.
                Defaults to "green".
        
        Returns:
            Optional[BaseWrapper]: Elemento final encontrado ou None se falhou.
        
        Example:
            >>> steps = [{"title": "Arquivo", "control_type": "MenuItem"}]
            >>> element = navigator.navigate_to_path_debug(steps)
        """
        if not steps:
            logger.error("Lista de steps vazia")
            return None

        current_element = self.parent_element
        logger.info(f"🔍 Iniciando navegação debug hierárquica com {len(steps)} steps")

        for idx, step in enumerate(steps, 1):
            try:
                step_title = step.get('title', '')
                step_control_type = step.get('control_type', '')
                step_auto_id = step.get('auto_id', '')
                
                try:
                    parent_info = current_element.window_text() or type(current_element).__name__
                except:
                    parent_info = type(current_element).__name__
                
                logger.info(f"\n🔍 Step {idx}: buscando em '{sanitize_for_log(parent_info)}'")
                logger.info(f"    Critérios: control_type='{sanitize_for_log(step_control_type)}' title='{sanitize_for_log(step_title)}' auto_id='{sanitize_for_log(step_auto_id)}'")
                
                children = current_element.children()
                logger.info(f"  📋 Total de filhos: {len(children)}")
                
                found = None
                for child in children:
                    try:
                        c_type = child.friendly_class_name()
                        c_title = child.window_text()
                        
                        # Obter auto_id corretamente
                        c_auto_id = None
                        try:
                            if hasattr(child, 'automation_id'):
                                c_auto_id = child.automation_id()
                        except:
                            pass
                        
                        logger.info(f"    📄 Filho: type='{sanitize_for_log(c_type)}', title='{sanitize_for_log(c_title)}', auto_id='{sanitize_for_log(str(c_auto_id))}'")
                        
                        # Lógica de busca melhorada
                        title_match = not step_title or step_title in [c_title, '', None]
                        type_match = c_type == step_control_type
                        auto_id_match = not step_auto_id or c_auto_id == step_auto_id
                        
                        if type_match and title_match and auto_id_match:
                            found = child
                            logger.info(f"  ✅ MATCH encontrado: {sanitize_for_log(c_type)} - '{sanitize_for_log(c_title)}' - auto_id:'{sanitize_for_log(str(c_auto_id))}'")
                            break
                            
                    except Exception as e:
                        logger.debug(f"Erro ao processar filho: {e}")
                        continue
                
                if not found:
                    logger.error(f"  ❌ NÃO encontrado no step {idx}")
                    return None
                
                if step.get('click_element'):
                    logger.info("  🖱️ Clicando neste elemento")
                    try:
                        if step_control_type == "TabItem":
                            if hasattr(found, 'select'):
                                found.select()
                            else:
                                found.click_input()
                        else:
                            found.click_input()
                        logger.info("  ✅ Clique executado com sucesso")
                    except Exception as e:
                        logger.error(f"  ❌ Erro ao clicar: {sanitize_for_log(str(e))}")
                        return None
                
                # ✅ CRÍTICO: Atualizar current_element para navegação hierárquica
                current_element = found
                
            except Exception as e:
                logger.error(f"❌ Erro no step {idx}: {sanitize_for_log(str(e))}")
                return None

        # Desenhar contorno no elemento final
        try:
            current_element.draw_outline(colour=outline_color, thickness=3)
            logger.info(f"🎯 Elemento final encontrado e destacado: {sanitize_for_log(str(current_element))}")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao desenhar contorno: {sanitize_for_log(str(e))}")

        return current_element

    def map_hierarchy(self, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """Mapeia a hierarquia de elementos para debug.
        
        Útil para entender a estrutura de elementos antes de criar os steps
        de navegação. Retorna um dicionário com informações hierárquicas.
        
        Args:
            max_depth (int, optional): Profundidade máxima de mapeamento.
                Defaults to 3.
            current_depth (int, optional): Profundidade atual (uso interno).
                Defaults to 0.
        
        Returns:
            Dict[str, Any]: Dicionário com estrutura hierárquica dos elementos.
                Contém 'type', 'title', 'auto_id' e 'children'.
        
        Example:
            >>> hierarchy = navigator.map_hierarchy(max_depth=2)
            >>> print(hierarchy['type'])
            'Pane'
        """
        if current_depth >= max_depth:
            return {"max_depth_reached": True}
        
        try:
            element_info = {
                "type": self.parent_element.friendly_class_name(),
                "title": self.parent_element.window_text(),
                "auto_id": None,
                "children": []
            }
            
            # Obter auto_id
            try:
                if hasattr(self.parent_element, 'automation_id'):
                    element_info["auto_id"] = self.parent_element.automation_id()
            except:
                pass
            
            # Mapear filhos
            children = self.parent_element.children()
            for child in children[:10]:  # Limitar a 10 filhos para evitar spam
                try:
                    child_navigator = RMAdaptNavigator(child)
                    child_info = child_navigator.map_hierarchy(max_depth, current_depth + 1)
                    element_info["children"].append(child_info)
                except Exception as e:
                    element_info["children"].append({"error": sanitize_for_log(str(e))})
            
            return element_info
            
        except Exception as e:
            return {"error": sanitize_for_log(str(e))}

    def navigate_to_elements(self, *elements: Tuple[Dict[str, Any], bool]) -> Tuple[bool, str]:
        """Método de compatibilidade com versão anterior.
        
        Mantido para compatibilidade com código legado que usa a interface
        antiga de navegação por elementos.
        
        Args:
            *elements: Tuplas de (critérios, click_element) para navegação.
        
        Returns:
            Tuple[bool, str]: (sucesso, identificador_do_último_elemento)
        
        Note:
            Este método está deprecated. Use navigate_to_path() para novos desenvolvimentos.
        """
        steps = []
        for element_tuple in elements:
            if isinstance(element_tuple, tuple) and len(element_tuple) >= 2:
                criteria, click_element = element_tuple[0], element_tuple[1]
                if isinstance(criteria, dict):
                    step = criteria.copy()
                    step['click_element'] = click_element
                    steps.append(step)
        return self.navigate_to_path(steps)


def RMAdaptativeNavigator(parent: BaseWrapper, **kwargs: Any) -> Optional[BaseWrapper]:
    """Função obsoleta mantida para compatibilidade.
    
    Esta função está deprecated e será removida em versões futuras.
    Use a classe RMAdaptNavigator diretamente para novos desenvolvimentos.
    
    Args:
        parent (BaseWrapper): Elemento pai para navegação.
        **kwargs: Argumentos para navegação (title, control_type, etc.).
    
    Returns:
        Optional[BaseWrapper]: Elemento encontrado ou None se não encontrado.
    
    Raises:
        ValueError: Se elemento não for encontrado ou erro na navegação.
        DeprecationWarning: Aviso de função obsoleta.
    
    Example:
        >>> # Deprecated - não use em código novo
        >>> element = RMAdaptativeNavigator(parent, title="Salvar")
        >>> 
        >>> # Use isto em vez disso:
        >>> navigator = RMAdaptNavigator(parent)
        >>> element = navigator.navigate_to_element(title="Salvar")
    
    Note:
        Esta função será removida na versão 2.0.0.
    """
    import warnings
    warnings.warn(
        "A função RMAdaptativeNavigator está obsoleta. Use a classe RMAdaptNavigator diretamente.",
        DeprecationWarning,
        stacklevel=2
    )
    try:
        navigator = RMAdaptNavigator(parent)
        result = navigator.navigate_to_element(**kwargs)
        if result is None:
            raise ValueError("Elemento não encontrado")
        return result
    except (UIElementNotFoundError, UIInteractionError, UITimeoutError, ValueError) as e:
        raise ValueError(str(e)) from e