"""
International compliance service for CineChainLanka
Handles regulatory compliance across different jurisdictions
"""

import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ComplianceService:
    """
    Service for handling international compliance requirements
    """
    
    # Supported jurisdictions
    JURISDICTIONS = {
        'LK': {
            'name': 'Sri Lanka',
            'currency': 'LKR',
            'regulator': 'CBSL',
            'kyc_required': True,
            'aml_required': True,
            'tax_id_required': True,
            'max_investment_annual': 1000000,  # LKR
            'min_investment': 1000,  # LKR
            'compliance_docs': ['passport', 'national_id', 'address_proof', 'bank_statement'],
        },
        'US': {
            'name': 'United States',
            'currency': 'USD',
            'regulator': 'SEC',
            'kyc_required': True,
            'aml_required': True,
            'tax_id_required': True,
            'accredited_investor_required': True,
            'max_investment_annual': 100000,  # USD
            'min_investment': 100,  # USD
            'compliance_docs': ['passport', 'ssn', 'address_proof', 'income_proof', 'accreditation_proof'],
        },
        'UK': {
            'name': 'United Kingdom',
            'currency': 'GBP',
            'regulator': 'FCA',
            'kyc_required': True,
            'aml_required': True,
            'tax_id_required': True,
            'max_investment_annual': 50000,  # GBP
            'min_investment': 50,  # GBP
            'compliance_docs': ['passport', 'ni_number', 'address_proof', 'bank_statement'],
        },
        'SG': {
            'name': 'Singapore',
            'currency': 'SGD',
            'regulator': 'MAS',
            'kyc_required': True,
            'aml_required': True,
            'tax_id_required': True,
            'max_investment_annual': 200000,  # SGD
            'min_investment': 200,  # SGD
            'compliance_docs': ['passport', 'nric', 'address_proof', 'bank_statement'],
        },
        'AU': {
            'name': 'Australia',
            'currency': 'AUD',
            'regulator': 'ASIC',
            'kyc_required': True,
            'aml_required': True,
            'tax_id_required': True,
            'max_investment_annual': 100000,  # AUD
            'min_investment': 100,  # AUD
            'compliance_docs': ['passport', 'tax_file_number', 'address_proof', 'bank_statement'],
        },
    }
    
    @classmethod
    def get_jurisdiction_requirements(cls, jurisdiction_code: str) -> Dict:
        """Get compliance requirements for a specific jurisdiction"""
        return cls.JURISDICTIONS.get(jurisdiction_code.upper(), {})
    
    @classmethod
    def validate_investment_limits(cls, jurisdiction_code: str, amount: float, user_id: int) -> Tuple[bool, str]:
        """Validate investment against jurisdiction limits"""
        requirements = cls.get_jurisdiction_requirements(jurisdiction_code)
        if not requirements:
            return False, f"Unsupported jurisdiction: {jurisdiction_code}"
        
        # Check minimum investment
        if amount < requirements.get('min_investment', 0):
            return False, f"Investment below minimum: {requirements['min_investment']} {requirements['currency']}"
        
        # Check annual investment limit
        annual_investment = cls.get_user_annual_investment(user_id, jurisdiction_code)
        max_annual = requirements.get('max_investment_annual', float('inf'))
        
        if annual_investment + amount > max_annual:
            return False, f"Investment exceeds annual limit: {max_annual} {requirements['currency']}"
        
        return True, "Investment within limits"
    
    @classmethod
    def get_user_annual_investment(cls, user_id: int, jurisdiction_code: str) -> float:
        """Get user's annual investment amount for a jurisdiction"""
        cache_key = f"annual_investment_{user_id}_{jurisdiction_code}"
        cached_amount = cache.get(cache_key)
        
        if cached_amount is not None:
            return cached_amount
        
        # Calculate from database (simplified)
        from funding.models import Transaction
        from datetime import datetime
        
        current_year = datetime.now().year
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31)
        
        transactions = Transaction.objects.filter(
            user_id=user_id,
            jurisdiction=jurisdiction_code,
            created_at__range=[start_date, end_date],
            status='completed'
        )
        
        total_amount = sum(t.amount for t in transactions)
        
        # Cache for 1 hour
        cache.set(cache_key, total_amount, 3600)
        
        return total_amount
    
    @classmethod
    def check_kyc_requirements(cls, user_id: int, jurisdiction_code: str) -> Tuple[bool, List[str]]:
        """Check if user meets KYC requirements for jurisdiction"""
        requirements = cls.get_jurisdiction_requirements(jurisdiction_code)
        if not requirements:
            return False, ["Unsupported jurisdiction"]
        
        missing_docs = []
        required_docs = requirements.get('compliance_docs', [])
        
        # Check if user has required documents
        from kyc.models import KYCDocument
        
        for doc_type in required_docs:
            if not KYCDocument.objects.filter(
                user_id=user_id,
                document_type=doc_type,
                status='approved'
            ).exists():
                missing_docs.append(doc_type)
        
        return len(missing_docs) == 0, missing_docs
    
    @classmethod
    def validate_accredited_investor(cls, user_id: int, jurisdiction_code: str) -> Tuple[bool, str]:
        """Validate accredited investor status for US jurisdiction"""
        if jurisdiction_code.upper() != 'US':
            return True, "Not required for this jurisdiction"
        
        # Check if user is accredited investor
        from users.models import User
        try:
            user = User.objects.get(id=user_id)
            if hasattr(user, 'accredited_investor') and user.accredited_investor:
                return True, "User is accredited investor"
            else:
                return False, "Accredited investor status required for US investments"
        except User.DoesNotExist:
            return False, "User not found"


class AMLService:
    """
    Anti-Money Laundering service
    """
    
    @classmethod
    def check_sanctions_list(cls, user_data: Dict) -> Tuple[bool, str]:
        """Check user against sanctions lists"""
        try:
            # This would integrate with actual sanctions checking services
            # For now, we'll simulate the check
            
            # Check OFAC (US) sanctions
            ofac_result = cls._check_ofac_sanctions(user_data)
            if not ofac_result[0]:
                return False, f"OFAC sanctions match: {ofac_result[1]}"
            
            # Check EU sanctions
            eu_result = cls._check_eu_sanctions(user_data)
            if not eu_result[0]:
                return False, f"EU sanctions match: {eu_result[1]}"
            
            # Check UN sanctions
            un_result = cls._check_un_sanctions(user_data)
            if not un_result[0]:
                return False, f"UN sanctions match: {un_result[1]}"
            
            return True, "No sanctions matches found"
            
        except Exception as e:
            logger.error(f"AML sanctions check error: {e}")
            return False, f"AML check failed: {str(e)}"
    
    @classmethod
    def _check_ofac_sanctions(cls, user_data: Dict) -> Tuple[bool, str]:
        """Check OFAC sanctions list"""
        # Simulated OFAC check
        # In production, this would call actual OFAC API
        return True, "OFAC check passed"
    
    @classmethod
    def _check_eu_sanctions(cls, user_data: Dict) -> Tuple[bool, str]:
        """Check EU sanctions list"""
        # Simulated EU sanctions check
        return True, "EU sanctions check passed"
    
    @classmethod
    def _check_un_sanctions(cls, user_data: Dict) -> Tuple[bool, str]:
        """Check UN sanctions list"""
        # Simulated UN sanctions check
        return True, "UN sanctions check passed"
    
    @classmethod
    def risk_assessment(cls, user_data: Dict, transaction_data: Dict) -> Dict:
        """Perform AML risk assessment"""
        risk_score = 0
        risk_factors = []
        
        # Check transaction amount
        amount = transaction_data.get('amount', 0)
        if amount > 10000:  # High value transaction
            risk_score += 30
            risk_factors.append("High value transaction")
        
        # Check user location
        country = user_data.get('country', '').upper()
        high_risk_countries = ['AF', 'IR', 'KP', 'SY']  # Example high-risk countries
        if country in high_risk_countries:
            risk_score += 50
            risk_factors.append("High-risk jurisdiction")
        
        # Check transaction pattern
        if transaction_data.get('is_first_transaction', False):
            risk_score += 10
            risk_factors.append("First-time transaction")
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'requires_review': risk_score >= 40
        }


class TaxComplianceService:
    """
    Tax compliance service for different jurisdictions
    """
    
    @classmethod
    def calculate_tax_obligations(cls, user_id: int, jurisdiction_code: str, 
                                transaction_amount: float) -> Dict:
        """Calculate tax obligations for a transaction"""
        requirements = ComplianceService.get_jurisdiction_requirements(jurisdiction_code)
        if not requirements:
            return {'error': 'Unsupported jurisdiction'}
        
        # Get user's tax information
        from users.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return {'error': 'User not found'}
        
        # Calculate applicable taxes
        taxes = {}
        
        if jurisdiction_code.upper() == 'LK':
            # Sri Lanka tax calculation
            taxes = cls._calculate_sri_lanka_taxes(transaction_amount, user)
        elif jurisdiction_code.upper() == 'US':
            # US tax calculation
            taxes = cls._calculate_us_taxes(transaction_amount, user)
        elif jurisdiction_code.upper() == 'UK':
            # UK tax calculation
            taxes = cls._calculate_uk_taxes(transaction_amount, user)
        else:
            # Generic tax calculation
            taxes = cls._calculate_generic_taxes(transaction_amount, user, jurisdiction_code)
        
        return {
            'jurisdiction': jurisdiction_code,
            'transaction_amount': transaction_amount,
            'taxes': taxes,
            'total_tax': sum(taxes.values()),
            'net_amount': transaction_amount - sum(taxes.values())
        }
    
    @classmethod
    def _calculate_sri_lanka_taxes(cls, amount: float, user: 'User') -> Dict:
        """Calculate Sri Lanka taxes"""
        taxes = {}
        
        # VAT (if applicable)
        if amount > 100000:  # LKR
            taxes['vat'] = amount * 0.15  # 15% VAT
        
        # Income tax (simplified)
        if hasattr(user, 'annual_income') and user.annual_income:
            if user.annual_income > 1200000:  # LKR
                taxes['income_tax'] = amount * 0.14  # 14% income tax
        
        return taxes
    
    @classmethod
    def _calculate_us_taxes(cls, amount: float, user: 'User') -> Dict:
        """Calculate US taxes"""
        taxes = {}
        
        # Capital gains tax (simplified)
        if amount > 1000:  # USD
            taxes['capital_gains_tax'] = amount * 0.20  # 20% capital gains
        
        # State tax (varies by state)
        taxes['state_tax'] = amount * 0.05  # 5% state tax (simplified)
        
        return taxes
    
    @classmethod
    def _calculate_uk_taxes(cls, amount: float, user: 'User') -> Dict:
        """Calculate UK taxes"""
        taxes = {}
        
        # Capital gains tax
        if amount > 12300:  # GBP (annual allowance)
            taxes['capital_gains_tax'] = amount * 0.20  # 20% CGT
        
        return taxes
    
    @classmethod
    def _calculate_generic_taxes(cls, amount: float, user: 'User', jurisdiction: str) -> Dict:
        """Calculate generic taxes for other jurisdictions"""
        taxes = {}
        
        # Generic transaction tax
        taxes['transaction_tax'] = amount * 0.05  # 5% transaction tax
        
        return taxes


class RegulatoryReportingService:
    """
    Service for regulatory reporting requirements
    """
    
    @classmethod
    def generate_aml_report(cls, start_date: datetime, end_date: datetime) -> Dict:
        """Generate AML compliance report"""
        from funding.models import Transaction
        
        transactions = Transaction.objects.filter(
            created_at__range=[start_date, end_date],
            status='completed'
        )
        
        # Calculate report metrics
        total_transactions = transactions.count()
        total_volume = sum(t.amount for t in transactions)
        high_value_transactions = transactions.filter(amount__gt=10000).count()
        
        # Risk assessment summary
        high_risk_transactions = 0
        for transaction in transactions:
            user_data = {
                'country': getattr(transaction.user, 'country', ''),
                'first_name': getattr(transaction.user, 'first_name', ''),
                'last_name': getattr(transaction.user, 'last_name', ''),
            }
            transaction_data = {
                'amount': transaction.amount,
                'is_first_transaction': not Transaction.objects.filter(
                    user=transaction.user,
                    created_at__lt=transaction.created_at
                ).exists()
            }
            
            risk_assessment = AMLService.risk_assessment(user_data, transaction_data)
            if risk_assessment['risk_level'] == 'HIGH':
                high_risk_transactions += 1
        
        return {
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_transactions': total_transactions,
                'total_volume': total_volume,
                'high_value_transactions': high_value_transactions,
                'high_risk_transactions': high_risk_transactions,
                'average_transaction_value': total_volume / total_transactions if total_transactions > 0 else 0
            },
            'compliance_status': 'COMPLIANT' if high_risk_transactions < total_transactions * 0.1 else 'REVIEW_REQUIRED'
        }
    
    @classmethod
    def generate_tax_report(cls, jurisdiction: str, year: int) -> Dict:
        """Generate tax reporting data for a jurisdiction"""
        from funding.models import Transaction
        from datetime import datetime
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        transactions = Transaction.objects.filter(
            jurisdiction=jurisdiction,
            created_at__range=[start_date, end_date],
            status='completed'
        )
        
        # Calculate tax obligations
        total_tax_obligation = 0
        user_tax_data = {}
        
        for transaction in transactions:
            tax_obligation = TaxComplianceService.calculate_tax_obligations(
                transaction.user_id, jurisdiction, transaction.amount
            )
            
            if 'total_tax' in tax_obligation:
                total_tax_obligation += tax_obligation['total_tax']
                
                user_id = transaction.user_id
                if user_id not in user_tax_data:
                    user_tax_data[user_id] = {
                        'total_amount': 0,
                        'total_tax': 0,
                        'transaction_count': 0
                    }
                
                user_tax_data[user_id]['total_amount'] += transaction.amount
                user_tax_data[user_id]['total_tax'] += tax_obligation['total_tax']
                user_tax_data[user_id]['transaction_count'] += 1
        
        return {
            'jurisdiction': jurisdiction,
            'year': year,
            'total_transactions': transactions.count(),
            'total_volume': sum(t.amount for t in transactions),
            'total_tax_obligation': total_tax_obligation,
            'user_tax_summary': user_tax_data
        }

