import hmac
import hashlib
import json
from app.core.config import settings

def generate_baseline_hmac(baseline_data: dict) -> str:
    """
    Genera un HMAC-SHA256 sobre una representación canónica de la línea base.
    """
    # Convertir a JSON canónico (llaves ordenadas, sin espacios extra)
    canonical_data = json.dumps(baseline_data, sort_keys=True, separators=(',', ':')).encode('utf-8')
    
    # Usar la clave secreta externa a la BD
    secret_key = settings.HMAC_SECRET_KEY.encode('utf-8')
    
    # Calcular HMAC
    signature = hmac.new(secret_key, canonical_data, hashlib.sha256).hexdigest()
    return signature

def verify_baseline_hmac(baseline_data: dict, expected_hmac: str) -> bool:
    """
    Verifica que la línea base no haya sido alterada.
    """
    calculated_hmac = generate_baseline_hmac(baseline_data)
    return hmac.compare_digest(calculated_hmac, expected_hmac)