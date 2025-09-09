"""Utilitários para sanitização de logs seguindo padrões de segurança DATAMETRIA.

Este módulo fornece funções para sanitizar dados antes de serem logados,
prevenindo ataques de log injection e garantindo que caracteres perigosos
sejam removidos das mensagens de log.

Functions:
    sanitize_for_log: Sanitiza strings para uso seguro em logs.

Example:
    >>> from fidi_common_libraries.ui.utils.log_sanitizer import sanitize_for_log
    >>> safe_value = sanitize_for_log("user\ninput\rwith\x00control")
    >>> logger.info(f"Processing: {safe_value}")
"""

import re
from typing import Any


def sanitize_for_log(value: Any) -> str:
    """Sanitiza entrada para logs removendo caracteres perigosos.
    
    Remove quebras de linha, caracteres de controle e outros caracteres
    que podem ser usados para ataques de log injection ou causar problemas
    na visualização de logs.
    
    Args:
        value (Any): Valor a ser sanitizado. Será convertido para string.
        
    Returns:
        str: Valor sanitizado seguro para logs.
        
    Example:
        Sanitização básica:
        
        >>> sanitize_for_log("normal text")
        'normal text'
        
        Remoção de caracteres perigosos:
        
        >>> sanitize_for_log("text\nwith\rcontrol\x00chars")
        'textwithcontrolchars'
        
        Conversão de tipos:
        
        >>> sanitize_for_log(12345)
        '12345'
        >>> sanitize_for_log(None)
        'None'
    
    Note:
        Esta função é essencial para segurança de logs e deve ser usada
        sempre que valores de entrada do usuário ou dados externos forem
        incluídos em mensagens de log.
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Remove quebras de linha e caracteres de controle (0x00-0x1F, 0x7F-0x9F)
    # Mantém apenas caracteres imprimíveis seguros
    return re.sub(r'[\r\n\x00-\x1f\x7f-\x9f]', '', value)