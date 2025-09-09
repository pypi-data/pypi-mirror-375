"""Utilitários para sanitização de nomes de arquivo seguindo padrões DATAMETRIA.

Este módulo fornece funções para sanitizar nomes de arquivo removendo
caracteres inválidos e garantindo compatibilidade com diferentes sistemas
operacionais.

Functions:
    sanitize_filename: Sanitiza strings para uso seguro como nomes de arquivo.

Example:
    >>> from fidi_common_libraries.ui.utils.filename_sanitizer import sanitize_filename
    >>> safe_name = sanitize_filename("TOTVS RM: Sistema/Principal")
    >>> print(safe_name)
    'TOTVS_RM__Sistema_Principal'
"""

from typing import Union


def sanitize_filename(filename: Union[str, None], max_length: int = 50) -> str:
    """Sanitiza nome de arquivo removendo caracteres inválidos do sistema.
    
    Remove caracteres que não são permitidos em nomes de arquivo no
    Windows e outros sistemas operacionais, garantindo compatibilidade
    multiplataforma.
    
    Args:
        filename (Union[str, None]): Nome original do arquivo a ser sanitizado.
            Se None ou vazio, retorna nome padrão.
        max_length (int, optional): Comprimento máximo do nome resultante.
            Defaults to 50 para evitar problemas com paths longos.
            
    Returns:
        str: Nome sanitizado seguro para uso como nome de arquivo.
            Retorna 'unnamed_file' se o resultado for vazio ou None.
            
    Example:
        Sanitização básica:
        
        >>> sanitize_filename("arquivo.txt")
        'arquivo.txt'
        
        Remoção de caracteres inválidos:
        
        >>> sanitize_filename("TOTVS RM: Sistema/Principal")
        'TOTVS_RM__Sistema_Principal'
        
        Com limite de tamanho:
        
        >>> sanitize_filename("Nome muito longo para arquivo", max_length=10)
        'Nome_muito'
        
        Tratamento de valores None/vazios:
        
        >>> sanitize_filename(None)
        'unnamed_file'
        >>> sanitize_filename("")
        'unnamed_file'
        
    Note:
        - Remove caracteres: < > : " / \ | ? *
        - Substitui espaços por underscores
        - Trunca no comprimento máximo especificado
        - Garante que sempre retorna um nome válido
        - Compatível com Windows, Linux e macOS
    """
    if not filename:
        return "unnamed_file"
    
    # Converter para string se necessário
    if not isinstance(filename, str):
        filename = str(filename)
    
    # Caracteres inválidos em nomes de arquivo (Windows + Unix)
    invalid_chars = r'<>:"/\|?*'
    
    # Substituir caracteres inválidos por underscore
    sanitized = "".join(c if c not in invalid_chars else "_" for c in filename)
    
    # Substituir espaços por underscores
    sanitized = sanitized.replace(" ", "_")
    
    # Truncar no comprimento máximo
    sanitized = sanitized[:max_length]
    
    # Garantir que não está vazio após sanitização
    return sanitized or "unnamed_file"