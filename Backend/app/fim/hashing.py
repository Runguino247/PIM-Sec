import hashlib

def calculate_sha256(file_path: str, chunk_size: int = 8192) -> str:
    """
    Calcula el hash SHA-256 de un archivo leyéndolo por bloques
    para no sobrecargar la memoria (RNF-04).
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        raise IOError(f"Error leyendo el archivo {file_path}: {str(e)}")