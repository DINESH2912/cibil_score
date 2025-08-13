from typing import Optional
from .models import Bank

def validate_bank_secret(request) -> Optional[Bank]:
    api_key = request.headers.get('x-api-key')
    if not api_key:
        return None
    try:
        return Bank.objects.get(api_secret_key=api_key, is_active=True)
    except Bank.DoesNotExist:
        return None
