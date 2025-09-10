"""
Advanced Security Service for CineChainLanka
Handles multi-factor authentication, fraud detection, and security monitoring
"""

import logging
import secrets
import hashlib
import hmac
import base64
import qrcode
import io
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import pyotp
import requests
import json

logger = logging.getLogger(__name__)
User = get_user_model()


class MultiFactorAuthenticationService:
    """
    Service for multi-factor authentication
    """
    
    @classmethod
    def setup_totp(cls, user_id: int) -> Dict:
        """Setup TOTP (Time-based One-Time Password) for user"""
        try:
            user = User.objects.get(id=user_id)
            
            # Generate secret key
            secret = pyotp.random_base32()
            
            # Create TOTP object
            totp = pyotp.TOTP(secret)
            
            # Generate provisioning URI
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name="CineChainLanka"
            )
            
            # Generate QR code
            qr_code = cls._generate_qr_code(provisioning_uri)
            
            # Store secret temporarily (will be confirmed later)
            cache.set(f'mfa_setup_{user_id}', secret, 600)  # 10 minutes
            
            return {
                'success': True,
                'secret': secret,
                'provisioning_uri': provisioning_uri,
                'qr_code': qr_code,
                'backup_codes': cls._generate_backup_codes(user_id)
            }
            
        except Exception as e:
            logger.error(f"TOTP setup error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def verify_totp_setup(cls, user_id: int, token: str) -> Dict:
        """Verify TOTP setup with user's token"""
        try:
            # Get secret from cache
            secret = cache.get(f'mfa_setup_{user_id}')
            if not secret:
                return {'success': False, 'error': 'Setup session expired'}
            
            # Verify token
            totp = pyotp.TOTP(secret)
            if totp.verify(token, valid_window=1):
                # Save secret to user profile
                user = User.objects.get(id=user_id)
                user.mfa_secret = secret
                user.mfa_enabled = True
                user.save()
                
                # Clear temporary secret
                cache.delete(f'mfa_setup_{user_id}')
                
                return {
                    'success': True,
                    'message': 'TOTP setup completed successfully'
                }
            else:
                return {'success': False, 'error': 'Invalid token'}
                
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def verify_totp_token(cls, user_id: int, token: str) -> Dict:
        """Verify TOTP token for authentication"""
        try:
            user = User.objects.get(id=user_id)
            
            if not user.mfa_enabled or not user.mfa_secret:
                return {'success': False, 'error': 'MFA not enabled for user'}
            
            # Verify token
            totp = pyotp.TOTP(user.mfa_secret)
            if totp.verify(token, valid_window=1):
                # Log successful MFA
                cls._log_mfa_event(user_id, 'success', 'totp')
                return {'success': True, 'message': 'Token verified successfully'}
            else:
                # Log failed MFA attempt
                cls._log_mfa_event(user_id, 'failure', 'totp')
                return {'success': False, 'error': 'Invalid token'}
                
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def setup_sms_mfa(cls, user_id: int, phone_number: str) -> Dict:
        """Setup SMS-based MFA"""
        try:
            user = User.objects.get(id=user_id)
            
            # Generate verification code
            verification_code = cls._generate_sms_code()
            
            # Store code temporarily
            cache.set(f'sms_verification_{user_id}', verification_code, 300)  # 5 minutes
            
            # Send SMS (in production, integrate with SMS service)
            sms_sent = cls._send_sms(phone_number, f'Your CineChainLanka verification code: {verification_code}')
            
            if sms_sent:
                return {
                    'success': True,
                    'message': 'Verification code sent to your phone',
                    'phone_number': phone_number[-4:].rjust(len(phone_number), '*')  # Masked phone
                }
            else:
                return {'success': False, 'error': 'Failed to send SMS'}
                
        except Exception as e:
            logger.error(f"SMS MFA setup error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def verify_sms_code(cls, user_id: int, code: str) -> Dict:
        """Verify SMS verification code"""
        try:
            # Get stored code
            stored_code = cache.get(f'sms_verification_{user_id}')
            if not stored_code:
                return {'success': False, 'error': 'Verification code expired'}
            
            if code == stored_code:
                # Enable SMS MFA for user
                user = User.objects.get(id=user_id)
                user.sms_mfa_enabled = True
                user.save()
                
                # Clear verification code
                cache.delete(f'sms_verification_{user_id}')
                
                # Log successful MFA
                cls._log_mfa_event(user_id, 'success', 'sms')
                
                return {'success': True, 'message': 'SMS MFA enabled successfully'}
            else:
                # Log failed attempt
                cls._log_mfa_event(user_id, 'failure', 'sms')
                return {'success': False, 'error': 'Invalid verification code'}
                
        except Exception as e:
            logger.error(f"SMS verification error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def send_sms_code(cls, user_id: int) -> Dict:
        """Send SMS code for authentication"""
        try:
            user = User.objects.get(id=user_id)
            
            if not user.sms_mfa_enabled:
                return {'success': False, 'error': 'SMS MFA not enabled'}
            
            # Generate code
            verification_code = cls._generate_sms_code()
            
            # Store code temporarily
            cache.set(f'sms_auth_{user_id}', verification_code, 300)  # 5 minutes
            
            # Send SMS
            sms_sent = cls._send_sms(user.phone_number, f'Your CineChainLanka login code: {verification_code}')
            
            if sms_sent:
                return {'success': True, 'message': 'SMS code sent'}
            else:
                return {'success': False, 'error': 'Failed to send SMS'}
                
        except Exception as e:
            logger.error(f"SMS code sending error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def verify_sms_auth(cls, user_id: int, code: str) -> Dict:
        """Verify SMS authentication code"""
        try:
            # Get stored code
            stored_code = cache.get(f'sms_auth_{user_id}')
            if not stored_code:
                return {'success': False, 'error': 'Authentication code expired'}
            
            if code == stored_code:
                # Clear code
                cache.delete(f'sms_auth_{user_id}')
                
                # Log successful MFA
                cls._log_mfa_event(user_id, 'success', 'sms')
                
                return {'success': True, 'message': 'SMS authentication successful'}
            else:
                # Log failed attempt
                cls._log_mfa_event(user_id, 'failure', 'sms')
                return {'success': False, 'error': 'Invalid authentication code'}
                
        except Exception as e:
            logger.error(f"SMS authentication error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def _generate_qr_code(cls, data: str) -> str:
        """Generate QR code for TOTP setup"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"QR code generation error: {e}")
            return ""
    
    @classmethod
    def _generate_backup_codes(cls, user_id: int) -> List[str]:
        """Generate backup codes for MFA"""
        try:
            codes = []
            for _ in range(10):
                code = secrets.token_hex(4).upper()
                codes.append(code)
            
            # Store codes securely
            cache.set(f'backup_codes_{user_id}', codes, 86400)  # 24 hours
            
            return codes
            
        except Exception as e:
            logger.error(f"Backup codes generation error: {e}")
            return []
    
    @classmethod
    def _generate_sms_code(cls) -> str:
        """Generate 6-digit SMS code"""
        return f"{secrets.randbelow(1000000):06d}"
    
    @classmethod
    def _send_sms(cls, phone_number: str, message: str) -> bool:
        """Send SMS message (integrate with SMS service)"""
        try:
            # In production, integrate with SMS service like Twilio, AWS SNS, etc.
            # For now, just log the message
            logger.info(f"SMS to {phone_number}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            return False
    
    @classmethod
    def _log_mfa_event(cls, user_id: int, status: str, method: str) -> None:
        """Log MFA event for security monitoring"""
        try:
            from users.models import SecurityEvent
            
            SecurityEvent.objects.create(
                user_id=user_id,
                event_type='mfa',
                status=status,
                method=method,
                ip_address='127.0.0.1',  # Would get from request
                user_agent='Unknown'  # Would get from request
            )
            
        except Exception as e:
            logger.error(f"MFA event logging error: {e}")


class AdvancedFraudDetectionService:
    """
    Service for advanced fraud detection and prevention
    """
    
    @classmethod
    def analyze_transaction_risk(cls, transaction_data: Dict) -> Dict:
        """Analyze transaction for fraud risk"""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # Amount-based risk
            amount = transaction_data.get('amount', 0)
            if amount > 10000:
                risk_score += 0.2
                risk_factors.append('High transaction amount')
            
            # Velocity-based risk
            velocity_risk = cls._check_transaction_velocity(transaction_data)
            if velocity_risk > 0.5:
                risk_score += velocity_risk
                risk_factors.append('Unusual transaction velocity')
            
            # Location-based risk
            location_risk = cls._check_location_risk(transaction_data)
            if location_risk > 0.3:
                risk_score += location_risk
                risk_factors.append('Suspicious location pattern')
            
            # Device-based risk
            device_risk = cls._check_device_risk(transaction_data)
            if device_risk > 0.3:
                risk_score += device_risk
                risk_factors.append('Unusual device pattern')
            
            # Behavioral risk
            behavioral_risk = cls._check_behavioral_risk(transaction_data)
            if behavioral_risk > 0.4:
                risk_score += behavioral_risk
                risk_factors.append('Unusual behavioral pattern')
            
            # Determine risk level
            if risk_score >= 0.8:
                risk_level = 'CRITICAL'
            elif risk_score >= 0.6:
                risk_level = 'HIGH'
            elif risk_score >= 0.4:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            return {
                'risk_score': round(risk_score, 3),
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'requires_review': risk_level in ['HIGH', 'CRITICAL'],
                'recommended_actions': cls._get_risk_actions(risk_level)
            }
            
        except Exception as e:
            logger.error(f"Transaction risk analysis error: {e}")
            return {'error': str(e)}
    
    @classmethod
    def _check_transaction_velocity(cls, transaction_data: Dict) -> float:
        """Check for unusual transaction velocity"""
        try:
            user_id = transaction_data.get('user_id')
            amount = transaction_data.get('amount', 0)
            
            # Check transactions in last hour
            from funding.models import Transaction
            from datetime import datetime, timedelta
            
            hour_ago = datetime.now() - timedelta(hours=1)
            recent_transactions = Transaction.objects.filter(
                user_id=user_id,
                created_at__gte=hour_ago
            )
            
            recent_amount = sum(t.amount for t in recent_transactions)
            total_recent_amount = recent_amount + amount
            
            # Risk increases with high velocity
            if total_recent_amount > 50000:
                return 0.8
            elif total_recent_amount > 20000:
                return 0.5
            elif total_recent_amount > 10000:
                return 0.2
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Velocity check error: {e}")
            return 0.0
    
    @classmethod
    def _check_location_risk(cls, transaction_data: Dict) -> float:
        """Check for location-based risk"""
        try:
            # This would integrate with geolocation services
            # For now, return a simple risk score
            ip_address = transaction_data.get('ip_address', '')
            user_country = transaction_data.get('user_country', '')
            transaction_country = transaction_data.get('transaction_country', '')
            
            # Check for country mismatch
            if user_country and transaction_country and user_country != transaction_country:
                return 0.6
            
            # Check for high-risk countries
            high_risk_countries = ['AF', 'IR', 'KP', 'SY']
            if transaction_country in high_risk_countries:
                return 0.8
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Location risk check error: {e}")
            return 0.0
    
    @classmethod
    def _check_device_risk(cls, transaction_data: Dict) -> float:
        """Check for device-based risk"""
        try:
            user_id = transaction_data.get('user_id')
            device_fingerprint = transaction_data.get('device_fingerprint', '')
            
            # Check if device is new for user
            from users.models import UserDevice
            
            if not UserDevice.objects.filter(user_id=user_id, fingerprint=device_fingerprint).exists():
                return 0.4
            
            # Check for unusual device characteristics
            user_agent = transaction_data.get('user_agent', '')
            if 'bot' in user_agent.lower() or 'crawler' in user_agent.lower():
                return 0.7
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Device risk check error: {e}")
            return 0.0
    
    @classmethod
    def _check_behavioral_risk(cls, transaction_data: Dict) -> float:
        """Check for behavioral risk patterns"""
        try:
            user_id = transaction_data.get('user_id')
            amount = transaction_data.get('amount', 0)
            
            # Check user's typical transaction patterns
            from funding.models import Transaction
            from datetime import datetime, timedelta
            
            # Get user's transaction history
            user_transactions = Transaction.objects.filter(user_id=user_id)
            
            if user_transactions.count() < 5:
                return 0.2  # New user risk
            
            # Check for unusual amount
            avg_amount = sum(t.amount for t in user_transactions) / user_transactions.count()
            if amount > avg_amount * 5:
                return 0.6
            
            # Check for unusual time
            current_hour = datetime.now().hour
            typical_hours = [t.created_at.hour for t in user_transactions]
            if current_hour not in typical_hours:
                return 0.3
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Behavioral risk check error: {e}")
            return 0.0
    
    @classmethod
    def _get_risk_actions(cls, risk_level: str) -> List[str]:
        """Get recommended actions based on risk level"""
        if risk_level == 'CRITICAL':
            return ['Block transaction', 'Require manual review', 'Contact user']
        elif risk_level == 'HIGH':
            return ['Require additional verification', 'Flag for review']
        elif risk_level == 'MEDIUM':
            return ['Monitor closely', 'Require MFA']
        else:
            return ['Process normally']


class SecurityMonitoringService:
    """
    Service for security monitoring and incident response
    """
    
    @classmethod
    def monitor_security_events(cls) -> Dict:
        """Monitor security events and generate alerts"""
        try:
            from users.models import SecurityEvent
            from datetime import datetime, timedelta
            
            # Get recent security events
            hour_ago = datetime.now() - timedelta(hours=1)
            recent_events = SecurityEvent.objects.filter(created_at__gte=hour_ago)
            
            # Analyze event patterns
            alerts = []
            
            # Check for multiple failed login attempts
            failed_logins = recent_events.filter(
                event_type='login',
                status='failure'
            ).values('user_id').annotate(count=Count('id')).filter(count__gte=5)
            
            for event in failed_logins:
                alerts.append({
                    'type': 'multiple_failed_logins',
                    'user_id': event['user_id'],
                    'count': event['count'],
                    'severity': 'HIGH',
                    'message': f'User {event["user_id"]} has {event["count"]} failed login attempts'
                })
            
            # Check for unusual MFA failures
            mfa_failures = recent_events.filter(
                event_type='mfa',
                status='failure'
            ).values('user_id').annotate(count=Count('id')).filter(count__gte=3)
            
            for event in mfa_failures:
                alerts.append({
                    'type': 'multiple_mfa_failures',
                    'user_id': event['user_id'],
                    'count': event['count'],
                    'severity': 'MEDIUM',
                    'message': f'User {event["user_id"]} has {event["count"]} MFA failures'
                })
            
            # Check for suspicious IP addresses
            suspicious_ips = recent_events.filter(
                event_type='login',
                status='failure'
            ).values('ip_address').annotate(count=Count('id')).filter(count__gte=10)
            
            for event in suspicious_ips:
                alerts.append({
                    'type': 'suspicious_ip',
                    'ip_address': event['ip_address'],
                    'count': event['count'],
                    'severity': 'HIGH',
                    'message': f'IP {event["ip_address"]} has {event["count"]} failed login attempts'
                })
            
            return {
                'success': True,
                'alerts': alerts,
                'total_events': recent_events.count(),
                'monitoring_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Security monitoring error: {e}")
            return {'error': str(e)}
    
    @classmethod
    def generate_security_report(cls, start_date: datetime, end_date: datetime) -> Dict:
        """Generate comprehensive security report"""
        try:
            from users.models import SecurityEvent
            from django.db.models import Count, Q
            
            # Get events in date range
            events = SecurityEvent.objects.filter(
                created_at__range=[start_date, end_date]
            )
            
            # Event type breakdown
            event_types = events.values('event_type').annotate(count=Count('id'))
            
            # Status breakdown
            status_breakdown = events.values('status').annotate(count=Count('id'))
            
            # Top IP addresses
            top_ips = events.values('ip_address').annotate(count=Count('id')).order_by('-count')[:10]
            
            # Failed login attempts by user
            failed_logins = events.filter(
                event_type='login',
                status='failure'
            ).values('user_id').annotate(count=Count('id')).order_by('-count')[:10]
            
            # Security incidents
            incidents = cls._identify_security_incidents(events)
            
            return {
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_events': events.count(),
                    'event_types': list(event_types),
                    'status_breakdown': list(status_breakdown),
                    'top_ips': list(top_ips),
                    'failed_logins': list(failed_logins),
                    'security_incidents': len(incidents)
                },
                'incidents': incidents,
                'recommendations': cls._generate_security_recommendations(events)
            }
            
        except Exception as e:
            logger.error(f"Security report generation error: {e}")
            return {'error': str(e)}
    
    @classmethod
    def _identify_security_incidents(cls, events) -> List[Dict]:
        """Identify potential security incidents"""
        incidents = []
        
        # Group events by user and time window
        user_events = {}
        for event in events:
            user_id = event.user_id
            if user_id not in user_events:
                user_events[user_id] = []
            user_events[user_id].append(event)
        
        # Analyze each user's events
        for user_id, user_event_list in user_events.items():
            # Check for brute force attacks
            failed_logins = [e for e in user_event_list if e.event_type == 'login' and e.status == 'failure']
            if len(failed_logins) >= 5:
                incidents.append({
                    'type': 'brute_force_attack',
                    'user_id': user_id,
                    'severity': 'HIGH',
                    'description': f'Multiple failed login attempts for user {user_id}',
                    'count': len(failed_logins)
                })
            
            # Check for account takeover attempts
            mfa_failures = [e for e in user_event_list if e.event_type == 'mfa' and e.status == 'failure']
            if len(mfa_failures) >= 3:
                incidents.append({
                    'type': 'account_takeover_attempt',
                    'user_id': user_id,
                    'severity': 'HIGH',
                    'description': f'Multiple MFA failures for user {user_id}',
                    'count': len(mfa_failures)
                })
        
        return incidents
    
    @classmethod
    def _generate_security_recommendations(cls, events) -> List[str]:
        """Generate security recommendations based on events"""
        recommendations = []
        
        # Count failed logins
        failed_logins = events.filter(event_type='login', status='failure').count()
        if failed_logins > 100:
            recommendations.append("Consider implementing rate limiting for login attempts")
        
        # Check for MFA adoption
        mfa_events = events.filter(event_type='mfa').count()
        login_events = events.filter(event_type='login').count()
        if login_events > 0 and mfa_events / login_events < 0.5:
            recommendations.append("Encourage users to enable multi-factor authentication")
        
        # Check for unusual IP patterns
        unique_ips = events.values('ip_address').distinct().count()
        if unique_ips > 1000:
            recommendations.append("Monitor for unusual IP address patterns")
        
        return recommendations

