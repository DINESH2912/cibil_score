# # views.py
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods
# from django.utils.decorators import method_decorator
# from django.views import View
# from django.db.models import Sum
# from django.utils import timezone
# import json
# from datetime import datetime, timedelta
# from decimal import Decimal
# from .models import Customer, CreditCard, CibilReport, CibilScore, PaymentHistory, Loan, BankAccount


# class EnhancedCibilScoreCalculator:
#     def _init_(self):
#         self.default_weights = {
#             "payment_history": 35,
#             "credit_utilization": 30,
#             "credit_history_length": 15,
#             "credit_mix": 10,
#             "new_credit": 10
#         }
        
#         # Loan type weights and importance
#         self.loan_type_weights = {
#             'HOME_LOAN': {
#                 'importance_weight': 0.40,  # 40% importance in payment history
#                 'base_score': 100,
#                 'risk_multiplier': 0.8,  # Lower risk
#                 'description': 'Secured loan with property collateral'
#             },
#             'CAR_LOAN': {
#                 'importance_weight': 0.25,  # 25% importance
#                 'base_score': 90,
#                 'risk_multiplier': 0.85,
#                 'description': 'Secured loan with vehicle collateral'
#             },
#             'PERSONAL_LOAN': {
#                 'importance_weight': 0.20,  # 20% importance
#                 'base_score': 80,
#                 'risk_multiplier': 1.3,  # Higher risk penalty
#                 'description': 'Unsecured loan with higher interest'
#             },
#             'EDUCATION_LOAN': {
#                 'importance_weight': 0.15,  # 15% importance
#                 'base_score': 85,
#                 'risk_multiplier': 0.9,
#                 'description': 'Investment in future earning potential'
#             },
#             'BUSINESS_LOAN': {
#                 'importance_weight': 0.30,  # 30% importance
#                 'base_score': 85,
#                 'risk_multiplier': 1.1,
#                 'description': 'Commercial loan with business risk'
#             },
#             'GOLD_LOAN': {
#                 'importance_weight': 0.10,  # 10% importance
#                 'base_score': 95,
#                 'risk_multiplier': 0.7,  # Lowest risk
#                 'description': 'Secured loan with gold collateral'
#             }
#         }
        
#         # Payment status penalties based on loan type
#         self.payment_status_penalties = {
#             'ON_TIME': 0,
#             'LATE_1_30': {
#                 'HOME_LOAN': 15,     # High penalty for home loan delays
#                 'CAR_LOAN': 12,
#                 'PERSONAL_LOAN': 10,  # Lower penalty as expected
#                 'EDUCATION_LOAN': 8,
#                 'BUSINESS_LOAN': 12,
#                 'GOLD_LOAN': 5,      # Lowest penalty
#                 'CREDIT_CARD': 8
#             },
#             'LATE_31_60': {
#                 'HOME_LOAN': 30,
#                 'CAR_LOAN': 25,
#                 'PERSONAL_LOAN': 20,
#                 'EDUCATION_LOAN': 18,
#                 'BUSINESS_LOAN': 25,
#                 'GOLD_LOAN': 15,
#                 'CREDIT_CARD': 20
#             },
#             'LATE_61_90': {
#                 'HOME_LOAN': 50,
#                 'CAR_LOAN': 40,
#                 'PERSONAL_LOAN': 35,
#                 'EDUCATION_LOAN': 30,
#                 'BUSINESS_LOAN': 40,
#                 'GOLD_LOAN': 25,
#                 'CREDIT_CARD': 35
#             },
#             'LATE_90_PLUS': {
#                 'HOME_LOAN': 80,
#                 'CAR_LOAN': 70,
#                 'PERSONAL_LOAN': 60,
#                 'EDUCATION_LOAN': 50,
#                 'BUSINESS_LOAN': 70,
#                 'GOLD_LOAN': 40,
#                 'CREDIT_CARD': 60
#             },
#             'MISSED': {
#                 'HOME_LOAN': 100,
#                 'CAR_LOAN': 90,
#                 'PERSONAL_LOAN': 80,
#                 'EDUCATION_LOAN': 70,
#                 'BUSINESS_LOAN': 90,
#                 'GOLD_LOAN': 60,
#                 'CREDIT_CARD': 80
#             },
#             'DEFAULTED': {
#                 'HOME_LOAN': 150,
#                 'CAR_LOAN': 130,
#                 'PERSONAL_LOAN': 120,
#                 'EDUCATION_LOAN': 100,
#                 'BUSINESS_LOAN': 140,
#                 'GOLD_LOAN': 80,
#                 'CREDIT_CARD': 120
#             }
#         }
        
#     def calculate_enhanced_score(self, pan_card_number, custom_weights=None):
#         weights = custom_weights if custom_weights else self.default_weights
        
#         # Validate weights sum to 100
#         if sum(weights.values()) != 100:
#             raise ValueError("Custom weights must sum to 100%")
        
#         credit_data = self._get_credit_data(pan_card_number)
        
#         # Calculate base score components with loan-specific logic
#         payment_score = self._calculate_loan_weighted_payment_score(credit_data)
#         utilization_score = self._calculate_credit_utilization_score(credit_data)
#         history_score = self._calculate_credit_history_score(credit_data)
#         mix_score = self._calculate_credit_mix_score(credit_data)
#         new_credit_score = self._calculate_new_credit_score(credit_data)
        
#         # Calculate weighted base score
#         base_score = (
#             (payment_score * weights["payment_history"] / 100) +
#             (utilization_score * weights["credit_utilization"] / 100) +
#             (history_score * weights["credit_history_length"] / 100) +
#             (mix_score * weights["credit_mix"] / 100) +
#             (new_credit_score * weights["new_credit"] / 100)
#         )
        
#         # Calculate final enhanced score (convert 0-100 scale to 300-900 scale)
#         enhanced_score = min(900, max(300, int(300 + (base_score * 6))))
        
#         # Save to database
#         self._save_to_database(credit_data["customer"], enhanced_score, payment_score, 
#                               utilization_score, history_score, mix_score, new_credit_score)
        
#         # Get detailed loan analysis
#         loan_analysis = self._get_loan_specific_analysis(credit_data)
        
#         return {
#             "pan_card_number": pan_card_number,
#             "customer_name": credit_data["customer"].full_name,
#             "enhanced_score": enhanced_score,
#             "base_score": round(base_score, 2),
#             "score_breakdown": {
#                 "payment_history": round(payment_score * weights["payment_history"] / 100, 2),
#                 "credit_utilization": round(utilization_score * weights["credit_utilization"] / 100, 2),
#                 "credit_history_length": round(history_score * weights["credit_history_length"] / 100, 2),
#                 "credit_mix": round(mix_score * weights["credit_mix"] / 100, 2),
#                 "new_credit": round(new_credit_score * weights["new_credit"] / 100, 2)
#             },
#             "weights_used": weights,
#             "score_grade": self._get_score_grade(enhanced_score),
#             "loan_specific_analysis": loan_analysis,
#             "calculated_at": datetime.now().isoformat()
#         }
    
#     def _calculate_loan_weighted_payment_score(self, credit_data):
#         """Calculate payment score with loan-specific weights and penalties"""
#         customer = credit_data["customer"]
        
#         total_weighted_score = 0
#         total_weight = 0
#         loan_scores = {}
        
#         # Analyze each loan type separately
#         for loan_type, config in self.loan_type_weights.items():
#             # Get loans of this type
#             loans = Loan.objects.filter(customer=customer, loan_type=loan_type)
#             if not loans.exists():
#                 continue
                
#             # Get payment history for this loan type
#             loan_payments = PaymentHistory.objects.filter(
#                 customer=customer,
#                 loan__in=loans
#             )
            
#             if loan_payments.exists():
#                 loan_score = self._calculate_loan_type_score(loan_type, loan_payments, config)
#                 loan_scores[loan_type] = loan_score
                
#                 # Apply importance weight
#                 weighted_score = loan_score * config['importance_weight']
#                 total_weighted_score += weighted_score
#                 total_weight += config['importance_weight']
        
#         # Handle credit card payments separately
#         credit_cards = CreditCard.objects.filter(customer=customer)
#         if credit_cards.exists():
#             card_payments = PaymentHistory.objects.filter(
#                 customer=customer,
#                 credit_card__in=credit_cards
#             )
            
#             if card_payments.exists():
#                 card_score = self._calculate_credit_card_score(card_payments)
#                 loan_scores['CREDIT_CARD'] = card_score
                
#                 # Credit cards get 20% weight
#                 weighted_score = card_score * 0.20
#                 total_weighted_score += weighted_score
#                 total_weight += 0.20
        
#         # Calculate final payment history score
#         if total_weight > 0:
#             final_score = total_weighted_score / total_weight
#         else:
#             # DEFAULT CASE: No loan or credit card payment history
#             # Use bank account activity as indicator if available
#             bank_accounts = BankAccount.objects.filter(customer=customer)
#             if bank_accounts.exists():
#                 # Base score for having bank accounts with good standing
#                 final_score = 70.0
                
#                 # Bonus for account age and status
#                 for account in bank_accounts:
#                     # Bonus for account age
#                     if hasattr(account, 'account_opened_date') and account.account_opened_date:
#                         account_age_months = (datetime.now().date() - account.account_opened_date).days // 30
#                         if account_age_months >= 12:
#                             final_score += 5
#                         elif account_age_months >= 6:
#                             final_score += 2
                    
#                     # Bonus for active account status
#                     if hasattr(account, 'status') and account.status == 'ACTIVE':
#                         final_score += 3
                    
#                     # Bonus for maintaining minimum balance (if available)
#                     if (hasattr(account, 'current_balance') and 
#                         hasattr(account, 'minimum_balance') and 
#                         account.current_balance >= account.minimum_balance):
#                         final_score += 2
                
#                 final_score = min(85, final_score)  # Cap at 85 for customers without credit history
#             else:
#                 # No payment history and no bank accounts - minimal score
#                 final_score = 60.0
        
#         return round(min(100, max(0, final_score)), 2)
    
#     def _calculate_loan_type_score(self, loan_type, payments, config):
#         """Calculate score for specific loan type with penalties"""
#         total_payments = payments.count()
#         if total_payments == 0:
#             return config['base_score']
        
#         # Start with base score for this loan type
#         score = config['base_score']
        
#         # Apply penalties based on payment status
#         for payment in payments:
#             status = payment.payment_status
#             if status in self.payment_status_penalties and status != 'ON_TIME':
#                 penalty = self.payment_status_penalties[status].get(loan_type, 0)
#                 # Apply risk multiplier
#                 penalty = penalty * config['risk_multiplier']
#                 score -= penalty
        
#         # Normalize by number of payments to get average impact
#         if total_payments > 0:
#             # Bonus for consistent on-time payments
#             on_time_count = payments.filter(payment_status='ON_TIME').count()
#             on_time_ratio = on_time_count / total_payments
            
#             if on_time_ratio >= 0.95:  # 95% or more on time
#                 score += 10  # Bonus
#             elif on_time_ratio >= 0.90:  # 90% or more on time
#                 score += 5   # Small bonus
        
#         return round(min(100, max(0, score)), 2)
    
#     def _calculate_credit_card_score(self, payments):
#         """Calculate score for credit card payments"""
#         total_payments = payments.count()
#         if total_payments == 0:
#             return 80.0  # Default score for credit cards
        
#         score = 80.0  # Base score for credit cards
        
#         # Apply penalties
#         for payment in payments:
#             status = payment.payment_status
#             if status in self.payment_status_penalties and status != 'ON_TIME':
#                 penalty = self.payment_status_penalties[status].get('CREDIT_CARD', 0)
#                 score -= penalty
        
#         # Normalize and add bonus for consistency
#         on_time_count = payments.filter(payment_status='ON_TIME').count()
#         on_time_ratio = on_time_count / total_payments
        
#         if on_time_ratio >= 0.95:
#             score += 15  # Higher bonus for credit cards
#         elif on_time_ratio >= 0.90:
#             score += 8
        
#         return round(min(100, max(0, score)), 2)
    
#     def _get_loan_specific_analysis(self, credit_data):
#         """Get detailed analysis by loan type"""
#         customer = credit_data["customer"]
#         analysis = {}
        
#         # Check if customer has any loans or credit cards
#         has_loans = False
#         has_credit_cards = False
        
#         for loan_type, config in self.loan_type_weights.items():
#             loans = Loan.objects.filter(customer=customer, loan_type=loan_type)
#             if not loans.exists():
#                 continue
                
#             has_loans = True
#             payments = PaymentHistory.objects.filter(
#                 customer=customer,
#                 loan__in=loans
#             )
            
#             if payments.exists():
#                 total_payments = payments.count()
#                 on_time = payments.filter(payment_status='ON_TIME').count()
#                 late = payments.exclude(payment_status='ON_TIME').count()
                
#                 # Calculate penalty breakdown
#                 penalty_breakdown = {}
#                 total_penalties = 0
                
#                 for status in ['LATE_1_30', 'LATE_31_60', 'LATE_61_90', 'LATE_90_PLUS', 'MISSED', 'DEFAULTED']:
#                     count = payments.filter(payment_status=status).count()
#                     if count > 0:
#                         penalty = self.payment_status_penalties[status].get(loan_type, 0)
#                         total_penalty = penalty * config['risk_multiplier'] * count
#                         penalty_breakdown[status] = {
#                             'count': count,
#                             'penalty_per_incident': round(penalty * config['risk_multiplier'], 2),
#                             'total_penalty': round(total_penalty, 2)
#                         }
#                         total_penalties += total_penalty
                
#                 analysis[loan_type] = {
#                     'loan_count': loans.count(),
#                     'total_payments': total_payments,
#                     'on_time_payments': on_time,
#                     'late_payments': late,
#                     'on_time_percentage': round((on_time / total_payments) * 100, 2),
#                     'importance_weight': config['importance_weight'],
#                     'base_score': config['base_score'],
#                     'risk_multiplier': config['risk_multiplier'],
#                     'penalty_breakdown': penalty_breakdown,
#                     'total_penalties_applied': round(total_penalties, 2),
#                     'final_loan_score': self._calculate_loan_type_score(loan_type, payments, config),
#                     'description': config['description']
#                 }
        
#         # Add credit card analysis
#         cards = CreditCard.objects.filter(customer=customer)
#         if cards.exists():
#             has_credit_cards = True
#             payments = PaymentHistory.objects.filter(customer=customer, credit_card__in=cards)
#             if payments.exists():
#                 total_payments = payments.count()
#                 on_time = payments.filter(payment_status='ON_TIME').count()
                
#                 analysis['CREDIT_CARD'] = {
#                     'card_count': cards.count(),
#                     'total_payments': total_payments,
#                     'on_time_payments': on_time,
#                     'on_time_percentage': round((on_time / total_payments) * 100, 2),
#                     'importance_weight': 0.20,
#                     'final_score': self._calculate_credit_card_score(payments)
#                 }
        
#         # Add information for customers without loans or credit cards
#         if not has_loans and not has_credit_cards:
#             bank_accounts = BankAccount.objects.filter(customer=customer)
#             analysis['BANK_ACCOUNT_BASED'] = {
#                 'message': 'Score calculated based on bank account activity as no loan/credit history available',
#                 'bank_accounts_count': bank_accounts.count(),
#                 'calculation_basis': 'Account age, status, and balance maintenance',
#                 'recommendations': [
#                     'Consider applying for a secured credit card to build credit history',
#                     'Maintain good banking relationship with consistent account activity',
#                     'Keep accounts in good standing with no overdrafts',
#                     'Consider a small personal loan if needed to establish credit history'
#                 ]
#             }
            
#             if bank_accounts.exists():
#                 oldest_account = bank_accounts.order_by('account_opened_date').first()
#                 if oldest_account and hasattr(oldest_account, 'account_opened_date'):
#                     relationship_months = (datetime.now().date() - oldest_account.account_opened_date).days // 30
#                     analysis['BANK_ACCOUNT_BASED']['banking_relationship_months'] = relationship_months
        
#         return analysis
    
#     def _get_credit_data(self, pan_card_number):
#         """Get credit data from database"""
#         try:
#             customer = Customer.objects.get(pan_card_number=pan_card_number.upper())
#         except Customer.DoesNotExist:
#             raise ValueError(f"Customer with PAN {pan_card_number} not found in database")
        
#         # Get payment history
#         payments = PaymentHistory.objects.filter(customer=customer)
#         payment_stats = self._calculate_payment_stats(payments)
        
#         # Get credit utilization
#         cards = CreditCard.objects.filter(customer=customer, is_active=True)
#         utilization_stats = self._calculate_utilization_stats(cards)
        
#         # Get credit history
#         history_stats = self._calculate_history_stats(customer)
        
#         # Get credit mix
#         mix_stats = self._calculate_mix_stats(customer)
        
#         # Get new credit
#         new_credit_stats = self._calculate_new_credit_stats(customer)
        
#         return {
#             "customer": customer,
#             "payment_history": payment_stats,
#             "credit_utilization": utilization_stats,
#             "credit_history": history_stats,
#             "credit_mix": mix_stats,
#             "new_credit": new_credit_stats
#         }
    
#     def _calculate_payment_stats(self, payments):
#         """Calculate payment statistics from database"""
#         if not payments.exists():
#             return {
#                 "on_time_payments": 0,
#                 "late_payments": 0,
#                 "defaults": 0,
#                 "total_payments": 0
#             }
        
#         total_payments = payments.count()
#         on_time = payments.filter(payment_status='ON_TIME').count()
#         late = payments.exclude(payment_status='ON_TIME').exclude(payment_status='DEFAULTED').count()
#         defaults = payments.filter(payment_status='DEFAULTED').count()
        
#         return {
#             "on_time_payments": on_time,
#             "late_payments": late,
#             "defaults": defaults,
#             "total_payments": total_payments
#         }
    
#     def _calculate_utilization_stats(self, cards):
#         """Calculate credit utilization from database"""
#         if not cards.exists():
#             # DEFAULT VALUES for customers without credit cards
#             return {
#                 "current_utilization": 0,
#                 "average_utilization": 0,
#                 "credit_limit": 0,
#                 "current_balance": 0
#             }
        
#         total_limit = cards.aggregate(total=Sum('credit_limit'))['total'] or Decimal('0')
#         total_balance = cards.aggregate(total=Sum('current_balance'))['total'] or Decimal('0')
        
#         current_util = float(total_balance / total_limit * 100) if total_limit > 0 else 0
        
#         return {
#             "current_utilization": current_util,
#             "average_utilization": current_util,
#             "credit_limit": float(total_limit),
#             "current_balance": float(total_balance)
#         }
    
#     def _calculate_history_stats(self, customer):
#         """Calculate credit history from database"""
#         oldest_dates = []
        
#         # Get oldest loan
#         try:
#             oldest_loan = Loan.objects.filter(customer=customer).order_by('loan_start_date').first()
#             if oldest_loan:
#                 oldest_dates.append(oldest_loan.loan_start_date)
#         except:
#             pass
        
#         # Get oldest card
#         oldest_card = CreditCard.objects.filter(customer=customer).order_by('card_issued_date').first()
#         if oldest_card:
#             oldest_dates.append(oldest_card.card_issued_date)
        
#         # Get oldest bank account
#         try:
#             oldest_account = BankAccount.objects.filter(customer=customer).order_by('account_opened_date').first()
#             if oldest_account:
#                 oldest_dates.append(oldest_account.account_opened_date)
#         except:
#             pass
        
#         if not oldest_dates:
#             return {
#                 "oldest_account_months": 0,
#                 "average_age_months": 0,
#                 "total_accounts": 0
#             }
        
#         oldest_date = min(oldest_dates)
#         oldest_months = (datetime.now().date() - oldest_date).days // 30
        
#         total_accounts = CreditCard.objects.filter(customer=customer).count()
#         try:
#             total_accounts += Loan.objects.filter(customer=customer).count()
#         except:
#             pass
#         try:
#             total_accounts += BankAccount.objects.filter(customer=customer).count()
#         except:
#             pass
        
#         return {
#             "oldest_account_months": oldest_months,
#             "average_age_months": oldest_months // 2 if oldest_months > 0 else 0,
#             "total_accounts": total_accounts
#         }
    
#     def _calculate_credit_mix_score(self, credit_data):
#         """Calculate credit mix component score"""
#         mix_data = credit_data["credit_mix"]
        
#         # Count different types
#         account_types = 0
#         if mix_data["credit_cards"] > 0:
#             account_types += 1
#         if mix_data["personal_loans"] > 0:
#             account_types += 1
#         if mix_data["home_loans"] > 0:
#             account_types += 1
#         if mix_data["auto_loans"] > 0:
#             account_types += 1
#         if mix_data["other_loans"] > 0:
#             account_types += 1
        
#         # DEFAULT CASE: If no credit products, check bank accounts
#         if account_types == 0:
#             customer = credit_data["customer"]
#             bank_accounts = BankAccount.objects.filter(customer=customer)
            
#             if bank_accounts.exists():
#                 # Base score for having bank accounts
#                 base_score = 50
                
#                 # Bonus for different types of bank accounts
#                 account_types_set = set()
#                 for account in bank_accounts:
#                     if hasattr(account, 'account_type'):
#                         account_types_set.add(account.account_type)
                
#                 # Bonus for account diversity
#                 base_score += len(account_types_set) * 8
                
#                 # Bonus for multiple accounts
#                 if bank_accounts.count() >= 2:
#                     base_score += 10
                
#                 return min(75, max(40, base_score))  # Cap at 75 for bank accounts only
#             else:
#                 return 40  # Minimum score if no accounts at all
        
#         # Original logic for customers with credit products
#         base_score = 40 + (account_types * 12)
        
#         # Bonus for optimal credit cards (2-4)
#         cc_count = mix_data["credit_cards"]
#         if 2 <= cc_count <= 4:
#             base_score += 10
        
#         # Bonus for secured loans
#         if mix_data["home_loans"] > 0:
#             base_score += 8
#         if mix_data["auto_loans"] > 0:
#             base_score += 5
        
#         return min(100, max(20, base_score))
    
#     def _calculate_new_credit_score(self, credit_data):
#         """Calculate new credit component score"""
#         new_credit_data = credit_data["new_credit"]
#         recent_accounts = new_credit_data["new_accounts_6months"]
        
#         # DEFAULT CASE: No recent credit accounts
#         if recent_accounts == 0:
#             return 85.0  # Good score for not seeking new credit aggressively
#         elif recent_accounts == 1:
#             return 80.0
#         elif recent_accounts == 2:
#             return 60.0
#         else:
#             return 40.0
    
#     def _calculate_mix_stats(self, customer):
#         """Calculate credit mix from database"""
#         credit_cards = CreditCard.objects.filter(customer=customer).count()
        
#         # Initialize loan counts
#         home_loans = 0
#         personal_loans = 0
#         auto_loans = 0
#         other_loans = 0
        
#         try:
#             loans = Loan.objects.filter(customer=customer)
#             home_loans = loans.filter(loan_type='HOME_LOAN').count()
#             personal_loans = loans.filter(loan_type='PERSONAL_LOAN').count()
#             auto_loans = loans.filter(loan_type='CAR_LOAN').count()
#             other_loans = loans.exclude(loan_type__in=['HOME_LOAN', 'PERSONAL_LOAN', 'CAR_LOAN']).count()
#         except:
#             pass
        
#         return {
#             "credit_cards": credit_cards,
#             "personal_loans": personal_loans,
#             "home_loans": home_loans,
#             "auto_loans": auto_loans,
#             "other_loans": other_loans
#         }
    
#     def _calculate_new_credit_stats(self, customer):
#         """Calculate new credit from database"""
#         six_months_ago = timezone.now() - timedelta(days=180)
#         twelve_months_ago = timezone.now() - timedelta(days=365)
        
#         # Count new credit cards
#         new_cards_6m = CreditCard.objects.filter(
#             customer=customer, 
#             created_at__gte=six_months_ago
#         ).count()
        
#         new_cards_12m = CreditCard.objects.filter(
#             customer=customer, 
#             created_at__gte=twelve_months_ago
#         ).count()
        
#         # Count new loans
#         new_loans_6m = 0
#         new_loans_12m = 0
        
#         try:
#             new_loans_6m = Loan.objects.filter(
#                 customer=customer, 
#                 created_at__gte=six_months_ago
#             ).count()
            
#             new_loans_12m = Loan.objects.filter(
#                 customer=customer, 
#                 created_at__gte=twelve_months_ago
#             ).count()
#         except:
#             pass
        
#         return {
#             "recent_inquiries": new_cards_6m + new_loans_6m,
#             "new_accounts_6months": new_cards_6m + new_loans_6m,
#             "new_accounts_12months": new_cards_12m + new_loans_12m
#         }
    
#     def _calculate_credit_utilization_score(self, credit_data):
#         """Calculate credit utilization component score"""
#         utilization_data = credit_data["credit_utilization"]
#         current_util = utilization_data["current_utilization"]
        
#         # DEFAULT CASE: No credit cards (utilization = 0)
#         if current_util == 0 and utilization_data["credit_limit"] == 0:
#             return 75.0  # Neutral score for customers without credit cards
        
#         # Original logic for customers with credit cards
#         if current_util <= 10:
#             return 100.0
#         elif current_util <= 30:
#             return 85.0
#         elif current_util <= 50:
#             return 65.0
#         elif current_util <= 70:
#             return 45.0
#         else:
#             return 25.0
    
#     def _save_to_database(self, customer, score, payment_score, utilization_score, 
#                          history_score, mix_score, new_credit_score):
#         """Save CIBIL score to database"""
#         try:
#             # Set previous scores to not latest
#             CibilScore.objects.filter(customer=customer, is_latest=True).update(is_latest=False)
            
#             # Get additional metrics with defaults
#             cards = CreditCard.objects.filter(customer=customer, is_active=True)
#             total_limit = cards.aggregate(total=Sum('credit_limit'))['total'] or Decimal('0')
#             total_balance = cards.aggregate(total=Sum('current_balance'))['total'] or Decimal('0')
            
#             total_outstanding = total_balance
#             try:
#                 loans = Loan.objects.filter(customer=customer, status='ACTIVE')
#                 loan_outstanding = loans.aggregate(total=Sum('outstanding_amount'))['total'] or Decimal('0')
#                 total_outstanding += loan_outstanding
#             except:
#                 pass
            
#             utilization_ratio = float(total_outstanding / total_limit) if total_limit > 0 else 0
            
#             # Create new score record
#             CibilScore.objects.create(
#                 customer=customer,
#                 score=score,
#                 payment_history_score=Decimal(str(payment_score)),
#                 credit_utilization_score=Decimal(str(utilization_score)),
#                 credit_history_length_score=Decimal(str(history_score)),
#                 credit_mix_score=Decimal(str(mix_score)),
#                 new_credit_score=Decimal(str(new_credit_score)),
#                 total_accounts=cards.count(),
#                 active_accounts=cards.count(),
#                 total_credit_limit=total_limit,
#                 total_outstanding=total_outstanding,
#                 credit_utilization_ratio=Decimal(str(utilization_ratio)),
#                 is_latest=True
#             )
#         except Exception as e:
#             # If saving fails, continue without saving
#             print(f"Failed to save to database: {e}")
    
#     def _calculate_credit_history_score(self, credit_data):
#         """Calculate credit history component score"""
#         history_data = credit_data["credit_history"]
#         oldest_months = history_data["oldest_account_months"]
        
#         # DEFAULT CASE: No credit history, use bank account history
#         if oldest_months == 0:
#             customer = credit_data["customer"]
#             bank_accounts = BankAccount.objects.filter(customer=customer)
            
#             if bank_accounts.exists():
#                 oldest_account = bank_accounts.order_by('account_opened_date').first()
#                 if oldest_account and hasattr(oldest_account, 'account_opened_date'):
#                     bank_months = (datetime.now().date() - oldest_account.account_opened_date).days // 30
                    
#                     # Score based on bank account age (lower than credit history scores)
#                     if bank_months >= 60:  # 5 years
#                         return 70.0
#                     elif bank_months >= 36:  # 3 years
#                         return 60.0
#                     elif bank_months >= 24:  # 2 years
#                         return 50.0
#                     elif bank_months >= 12:  # 1 year
#                         return 45.0
#                     else:
#                         return 35.0
#             return 35.0  # Minimum score for no history
        
#         # Original logic for customers with credit history
#         if oldest_months >= 120:  # 10 years
#             return 100.0
#         elif oldest_months >= 84:  # 7 years
#             return 85.0
#         elif oldest_months >= 60:  # 5 years
#             return 70.0
#         elif oldest_months >= 36:  # 3 years
#             return 55.0
#         elif oldest_months >= 12:  # 1 year
#             return 40.0
#         else:
#             return 25.0
    
#     def _get_score_grade(self, score):
#         """Convert numerical score to grade"""
#         if score >= 800:
#             return "Excellent"
#         elif score >= 750:
#             return "Very Good"
#         elif score >= 700:
#             return "Good"
#         elif score >= 650:
#             return "Fair"
#         elif score >= 600:
#             return "Poor"
#         else:
#             return "Very Poor"


# # Initialize the calculator globally
# calculator = EnhancedCibilScoreCalculator()


# @method_decorator(csrf_exempt, name='dispatch')
# class CibilScoreView(View):
#     """
#     Class-based view for CIBIL score calculation
#     """
    
#     def post(self, request):
#         try:
#             # Parse JSON data
#             data = json.loads(request.body)
            
#             # Extract required fields
#             pan_card_number = data.get('pan_card_number')
#             print(pan_check({"pan": pan_card_number}))

#             custom_weights = data.get('custom_weights')
            
#             # Validate required fields
#             if not pan_card_number:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'PAN card number is required'
#                 }, status=400)
            
#             # Validate PAN card format
#             pan = pan_card_number.upper().strip()
#             if len(pan) != 10 or not pan[:5].isalpha() or not pan[5:9].isdigit() or not pan[9].isalpha():
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Invalid PAN card number format. Expected format: ABCDE1234F'
#                 }, status=400)
            
#             # Calculate enhanced score
#             result = calculator.calculate_enhanced_score(
#                 pan_card_number=pan,
#                 custom_weights=custom_weights
#             )
            
#             return JsonResponse({
#                 'success': True,
#                 'data': result,
#                 'message': 'Enhanced CIBIL score calculated successfully'
#             })
            
#         except ValueError as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             }, status=400)
            
#         except json.JSONDecodeError:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Invalid JSON data'
#             }, status=400)
        
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': f'Failed to calculate enhanced CIBIL score: {str(e)}'
#             }, status=500)
    
#     def get(self, request):
#         return JsonResponse({
#             'message': 'Loan-Specific Weighted CIBIL Score Calculator API',
#             'version': '2.0',
#             'default_weights': calculator.default_weights,
#             'loan_type_weights': calculator.loan_type_weights,
#             'payment_penalties': calculator.payment_status_penalties,
#             'example_request': {
#                 'pan_card_number': 'ABCDE1234F',
#                 'custom_weights': {
#                     'payment_history': 40,
#                     'credit_utilization': 25,
#                     'credit_history_length': 20,
#                     'credit_mix': 10,
#                     'new_credit': 5
#                 }
#             },
#             'note': 'This calculator handles customers without loan/credit history by using bank account activity'
#         })


# @csrf_exempt
# @require_http_methods(["POST"])
# def check_dynamic_cibil_score(request):
#     """
#     Function-based view for CIBIL score calculation
#     Alternative to class-based view
#     """
#     try:
#         # Parse JSON data
#         data = json.loads(request.body)
        
#         # Extract required fields
#         pan_card_number = data.get('pan_card_number')
#         print(pan_card_number)
#         print(pan_check(pan_card_number))

#         custom_weights = data.get('custom_weights')
        
#         # Validate required fields
#         if not pan_card_number:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'PAN card number is required'
#             }, status=400)
        
#         # Validate PAN card format
#         pan = pan_card_number.upper().strip()
#         if len(pan) != 10 or not pan[:5].isalpha() or not pan[5:9].isdigit() or not pan[9].isalpha():
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Invalid PAN card number format. Expected format: ABCDE1234F'
#             }, status=400)
        
#         # Calculate enhanced score
#         result = calculator.calculate_enhanced_score(
#             pan_card_number=pan,
#             custom_weights=custom_weights
#         )
        
#         return JsonResponse({
#             'success': True,
#             'data': result,
#             'message': 'Enhanced CIBIL score calculated successfully'
#         })
        
#     except ValueError as e:
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         }, status=400)
        
#     except json.JSONDecodeError:
#         return JsonResponse({
#             'success': False,
#             'error': 'Invalid JSON data'
#         }, status=400)
    
#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'error': f'Failed to calculate enhanced CIBIL score: {str(e)}'
#         }, status=500)