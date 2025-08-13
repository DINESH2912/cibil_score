# jwt_auth.py
import jwt
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Customer

# JWT Configuration
SECRET_KEY = "xKTPNPUjMmS4_Tkex25dx70dWBCUvcCOqXG6Vic-iDlDmySsQm8jUz_IXhJyCALlHy8I3J5WOKtYvOkRNoBUOg"
ALGORITHM = "HS512"

def generate_pan_token(pan_number, expires_in_hours=24):
    """
    Generate JWT token for PAN card validation
    """
    payload = {
        "pan_number": pan_number,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours) if expires_in_hours else None
    }
    
    # Remove exp if no expiry is needed
    if not expires_in_hours:
        payload.pop('exp', None)
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_pan_token(token):
    """
    Decode and validate JWT token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_pan_validation_token(request):
    """
    Generate JWT token for PAN card validation
    """
    try:
        pan_number = request.data.get('pan_number')
        expires_in_hours = request.data.get('expires_in_hours', 24)  # Default 24 hours
        
        if not pan_number:
            return Response(
                {'error': 'PAN number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate PAN format (basic validation)
        if not validate_pan_format(pan_number):
            return Response(
                {'error': 'Invalid PAN format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate token
        token = generate_pan_token(pan_number, expires_in_hours)
        
        return Response({
            'pan_token': token,
            'pan_number': pan_number,
            'expires_in_hours': expires_in_hours if expires_in_hours else 'Never',
            'message': 'PAN validation token generated successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to generate token',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_pan_token(request):
    """
    Validate JWT token and check if PAN card exists in database
    """
    try:
        token = request.data.get('pan_token')
        
        if not token:
            return Response(
                {'error': 'PAN token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Decode token
        payload, error = decode_pan_token(token)
        
        if error:
            return Response(
                {'error': error, 'valid': False},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        pan_number = payload.get('pan_number')
        
        # Check if customer exists in database
        try:
            customer = Customer.objects.get(pan_card_number=pan_number)
            customer_exists = True
            customer_data = {
                'full_name': customer.full_name,
                'email': customer.email,
                'phone': customer.phone_number,
                'pan_card_number': customer.pan_card_number
            }
        except Customer.DoesNotExist:
            customer_exists = False
            customer_data = None
        
        return Response({
            'valid': True,
            'pan_number': pan_number,
            'customer_exists': customer_exists,
            'customer_data': customer_data,
            'token_issued_at': datetime.fromtimestamp(payload.get('iat', 0)).isoformat() if payload.get('iat') else None,
            'token_expires_at': datetime.fromtimestamp(payload.get('exp', 0)).isoformat() if payload.get('exp') else 'Never',
            'message': 'Token is valid'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Token validation failed',
            'details': str(e),
            'valid': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def check_cibil_score_with_token(request):
    """
    Modified CIBIL score check that requires valid JWT token
    """
    try:
        token = request.data.get('pan_token')
        custom_weights = request.data.get('custom_weights', {})
        
        if not token:
            return Response(
                {'error': 'PAN token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Decode and validate token
        payload, error = decode_pan_token(token)
        
        if error:
            return Response(
                {'error': error, 'valid': False},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        pan_number = payload.get('pan_number')
        
        # Now proceed with CIBIL score calculation
        # This essentially calls your existing check_dynamic_cibil_score function
        request.data['pan_card_number'] = pan_number
        
        # Import your existing function
        from .views import check_dynamic_cibil_score
        
        # Call the existing function with modified request
        return check_dynamic_cibil_score(request)
        
    except Exception as e:
        return Response({
            'error': 'CIBIL score calculation failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def validate_pan_format(pan_number):

    import re
    pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return re.match(pan_pattern, pan_number) is not None

# Middleware for JWT authentication (optional)
class JWTPANMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if request requires PAN token validation
        if request.path.startswith('/api/cibil/') and request.method == 'POST':
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                payload, error = decode_pan_token(token)
                
                if not error:
                    request.pan_number = payload.get('pan_number')
                    request.token_valid = True
                else:
                    request.token_valid = False
                    request.token_error = error
            else:
                request.token_valid = False
                request.token_error = "No token provided"

        response = self.get_response(request)
        return response

# Usage example for generating token
def example_generate_token():
    """
    Example of how to generate a token
    """
    pan_number = "MJNNG4830E"
    
    # Generate token with expiry
    token_with_expiry = generate_pan_token(pan_number, expires_in_hours=24)
    print(f"Token with 24h expiry: {token_with_expiry}")
    
    # Generate token without expiry
    token_no_expiry = generate_pan_token(pan_number, expires_in_hours=None)
    print(f"Token without expiry: {token_no_expiry}")
    
    return token_with_expiry, token_no_expiry

# Client-side example for making requests
def example_client_request():
    """
    Example of how to make requests with JWT token
    """
    import requests
    
    # First, generate token
    token_data = {
        "pan_number": "MJNNG4830E",
        "expires_in_hours": 24
    }
    
    response = requests.post(
        "http://your-api-url/api/generate-pan-token/",
        json=token_data
    )
    
    if response.status_code == 200:
        token = response.json()['pan_token']
        
        # Now use token for CIBIL score check
        cibil_data = {
            "pan_token": token,
            "custom_weights": {
                "payment_history": 40,
                "credit_utilization": 30,
                "credit_history_length": 15,
                "credit_mix": 10,
                "new_credit": 5
            }
        }
        
        cibil_response = requests.post(
            "http://your-api-url/api/check-cibil-with-token/",
            json=cibil_data
        )
        
        return cibil_response.json()
    
    return None