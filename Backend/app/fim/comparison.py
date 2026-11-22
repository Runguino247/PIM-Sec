from typing import Optional

def evaluate_integrity(
    expected_sha256: Optional[str], 
    actual_sha256: Optional[str],
    expected_identity: Optional[str] = None,
    actual_identity: Optional[str] = None
) -> str:
    """
    Compara los hashes y retorna el resultado según el catálogo de la Sección 12.1.
    """
    # 1. Archivo nuevo (no estaba en la línea base)
    if expected_sha256 is None and actual_sha256 is not None:
        return "NEW"
    
    # 2. Archivo eliminado (estaba en línea base pero no se encontró)
    if expected_sha256 is not None and actual_sha256 is None:
        return "DELETED"

    # 3. Error de lectura (el scanner maneja esto antes de llamar aquí)
    if expected_sha256 is None and actual_sha256 is None:
        return "ERROR"

    # 4. Ambos hashes existen: comparar contenido
    if expected_sha256 == actual_sha256:
        return "INTACT"
    
    # 5. Hashes diferentes: ¿es MODIFIED o REPLACED?
    # Regla estricta del documento: Un hash diferente NO es prueba de sustitución.
    # Solo se usa REPLACED si hay evidencia adicional (identidad del archivo cambió).
    if expected_identity and actual_identity and expected_identity != actual_identity:
        return "REPLACED"
    
    return "MODIFIED"