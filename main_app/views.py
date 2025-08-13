import json
import jwt
from datetime import datetime, timedelta
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", "supersecret")  # for signing JWTs
TOKEN_EXPIRY_MINUTES = 30


@csrf_exempt
def auth_token(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    # Step 1: Parse JSON body
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    pan_number = data.get('pan_card_number')
    if not pan_number:
        return JsonResponse({'error': 'PAN card number required in body'}, status=400)

    # Step 2: Create JWT payload
    payload = {
        "pan_card_number": pan_number,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    }

    # Step 3: Generate token
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # Step 4: Return token
    return JsonResponse({
        "success": True,
        "token": token,
        "expires_in_minutes": TOKEN_EXPIRY_MINUTES
    })
# ---------------- CIBIL CHECK ENDPOINT ----------------
@csrf_exempt
def calculate_cibil_score(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    # Step 1: Check Bearer token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Bearer token required'}, status=401)

    token = auth_header.split(' ')[1]
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        bank_name = decoded.get("bank_name")
    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Invalid token'}, status=401)

    # Step 2: Parse request JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    pan_number = data.get('panNumber')
    print(pan_number)
    
    if not pan_number:
        return JsonResponse({'error': 'PAN card number required'}, status=400)

    # Weights for score calculation
    weights = {
        "payment_history": 35,
        "credit_utilization": 30,
        "credit_history_length": 15,
        "credit_mix": 10,
        "new_credit": 10
    }

    # Step 3: Call bank microservices with token
    base_url = getattr(settings, 'BANK_MICROSERVICE_BASE_URL', 'http://172.17.254.222:5000/api')

    try:
        auth_response = requests.post(f"{base_url}/auth-token/", timeout=30)
        token = auth_response.json().get("token")
        headers = {
    "Authorization": f"Bearer {token}"
}

        customers = requests.get(f"{base_url}/fetch-customers/",headers=headers,timeout=30).json()
        loans = requests.get(f"{base_url}/fetch-loans",headers=headers,timeout=30).json()
        transactions = requests.get(f"{base_url}/fetch-transactions/",headers=headers,timeout=30).json()
        
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Error calling bank microservices: {str(e)}'}, status=502)
    
    # Step 4: Find customer by PAN
    customer = next((c for c in customers if c.get('panNumber', '').upper() == pan_number.upper()), None)
    if not customer:
        return JsonResponse({'error': 'Customer not found'}, status=404)

    customer_id = customer.get('id')
    customer_loans = [loan for loan in loans if loan.get('customerId') == customer_id]
    account_number = customer.get('accountNumber') or customer.get('generatedAccountNumber')
    customer_transactions = [txn for txn in transactions if account_number and account_number in str(txn.get('accountId', ''))]

    # Step 5: Calculate CIBIL score
    payment_score = calculate_payment_history(customer_loans, customer_transactions)
    utilization_score = calculate_credit_utilization(customer_loans)
    history_score = calculate_credit_history(customer, customer_loans, customer_transactions)
    mix_score = calculate_credit_mix(customer_loans)
    new_credit_score = calculate_new_credit(customer_loans)

    base_score = (
        (payment_score * weights["payment_history"] / 100) +
        (utilization_score * weights["credit_utilization"] / 100) +
        (history_score * weights["credit_history_length"] / 100) +
        (mix_score * weights["credit_mix"] / 100) +
        (new_credit_score * weights["new_credit"] / 100)
    )
    cibil_score = min(900, max(300, int(300 + (base_score * 6))))

    return JsonResponse({
        "success": True,
        "bank": bank_name,
        "pan_card_number": pan_number,
        "customer_name": f"{customer.get('firstName', '')} {customer.get('lastName', '')}".strip(),
        "cibil_score": cibil_score,
        "component_scores": {
            "payment_history": payment_score,
            "credit_utilization": utilization_score,
            "credit_history_length": history_score,
            "credit_mix": mix_score,
            "new_credit": new_credit_score
        },
        "calculated_at": datetime.now().isoformat()
    })


# ---------------- HELPER FUNCTIONS ----------------
def calculate_payment_history(loans, transactions):
    if not loans:
        return 70.0 if transactions else 60.0
    approved_loans = sum(1 for loan in loans if loan.get('status', '').lower() == 'approved')
    return min(100, (approved_loans / len(loans)) * 100) if loans else 60.0


def calculate_credit_utilization(loans):
    if not loans:
        return 75.0
    total_amount = sum(float(loan.get('amount', 0) or 0) for loan in loans if loan.get('status', '').lower() == 'approved')
    if total_amount == 0:
        return 75.0
    utilization = total_amount * 0.7
    ratio = (utilization / total_amount) * 100
    return 85.0 if ratio <= 30 else (65.0 if ratio <= 50 else 45.0)


def calculate_credit_history(customer, loans, transactions):
    dates = []
    for loan in loans:
        created_at = loan.get('createdAt')
        if created_at:
            try:
                dates.append(datetime.fromisoformat(str(created_at).replace('Z', '+00:00')).date())
            except Exception:
                pass
    created_at = customer.get('createdAt')
    if created_at:
        try:
            dates.append(datetime.fromisoformat(str(created_at).replace('Z', '+00:00')).date())
        except Exception:
            pass
    if not dates:
        return 35.0
    months_old = (datetime.now().date() - min(dates)).days // 30
    if months_old >= 60:
        return 70.0
    elif months_old >= 36:
        return 55.0
    elif months_old >= 12:
        return 40.0
    return 35.0


def calculate_credit_mix(loans):
    if not loans:
        return 50.0
    loan_types = {loan.get('loanType', '').lower() for loan in loans if loan.get('loanType')}
    return min(100, 40 + len(loan_types) * 15)


def calculate_new_credit(loans):
    if not loans:
        return 85.0
    six_months_ago = datetime.now() - timedelta(days=180)
    recent_loans = 0
    for loan in loans:
        created_at = loan.get('createdAt')
        if created_at:
            try:
                if datetime.fromisoformat(str(created_at).replace('Z', '+00:00')) >= six_months_ago:
                    recent_loans += 1
            except Exception:
                pass
    return 85.0 if recent_loans == 0 else (80.0 if recent_loans == 1 else 60.0)
