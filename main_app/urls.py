from django.urls import path
from .views import calculate_cibil_score,auth_token

urlpatterns = [
    path('calculate-cibil-score/', calculate_cibil_score, name='calculate_cibil_score'),
    path('auth_token/',auth_token,name='auth-token')

]
