"""Logger genérico para casos não especializados."""

import logging
from .base_logger import BaseLogger, LogCategory


class GenericLogger(BaseLogger):
    """Logger genérico para domínios não especializados.
    
    Este logger fornece funcionalidade básica de logging quando não há
    um logger especializado disponível para a categoria.
    
    Example:
        Uso do logger genérico:
        
        >>> logger = GenericLogger("generic_app", LogCategory.SYSTEM)
        >>> logger.info("Operação do sistema")
    """
    
    def _setup_logging_infrastructure(self):
        """Configura infraestrutura básica de logging.
        
        Configura um handler de console simples com formatação básica.
        """
        # Evitar duplicação de handlers
        if self.logger.handlers:
            return
            
        # Handler de console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # Formatter básico
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Adicionar handler
        self.logger.addHandler(console_handler)
        self.logger.propagate = False