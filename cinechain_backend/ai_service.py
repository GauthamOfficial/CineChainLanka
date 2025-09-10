"""
AI and Machine Learning Service for CineChainLanka
Provides predictive analytics, content recommendations, and risk assessment
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta
import json
import math

logger = logging.getLogger(__name__)


class PredictiveAnalyticsService:
    """
    Service for predictive analytics and forecasting
    """
    
    @classmethod
    def predict_campaign_success(cls, campaign_data: Dict) -> Dict:
        """Predict the likelihood of campaign success"""
        try:
            # Extract features from campaign data
            features = cls._extract_campaign_features(campaign_data)
            
            # Calculate success probability using ML model
            success_probability = cls._calculate_success_probability(features)
            
            # Generate insights and recommendations
            insights = cls._generate_campaign_insights(features, success_probability)
            
            return {
                'success_probability': success_probability,
                'confidence_level': cls._calculate_confidence_level(features),
                'key_factors': cls._identify_key_factors(features),
                'insights': insights,
                'recommendations': cls._generate_recommendations(features, success_probability),
                'risk_factors': cls._identify_risk_factors(features)
            }
            
        except Exception as e:
            logger.error(f"Campaign success prediction error: {e}")
            return {'error': f'Prediction failed: {str(e)}'}
    
    @classmethod
    def predict_revenue_forecast(cls, content_id: str, platform: str, months: int = 12) -> Dict:
        """Predict revenue forecast for content"""
        try:
            # Get historical revenue data
            historical_data = cls._get_historical_revenue_data(content_id, platform)
            
            if not historical_data:
                return {'error': 'Insufficient historical data for prediction'}
            
            # Apply forecasting model
            forecast = cls._apply_forecasting_model(historical_data, months)
            
            # Calculate confidence intervals
            confidence_intervals = cls._calculate_confidence_intervals(forecast)
            
            return {
                'content_id': content_id,
                'platform': platform,
                'forecast_period_months': months,
                'forecast_data': forecast,
                'confidence_intervals': confidence_intervals,
                'trend_analysis': cls._analyze_revenue_trend(historical_data),
                'seasonality_factors': cls._detect_seasonality(historical_data)
            }
            
        except Exception as e:
            logger.error(f"Revenue forecast error: {e}")
            return {'error': f'Revenue forecast failed: {str(e)}'}
    
    @classmethod
    def predict_investor_behavior(cls, user_id: int) -> Dict:
        """Predict investor behavior and preferences"""
        try:
            # Get user's investment history
            investment_history = cls._get_user_investment_history(user_id)
            
            if not investment_history:
                return {'error': 'Insufficient investment history for prediction'}
            
            # Analyze investment patterns
            patterns = cls._analyze_investment_patterns(investment_history)
            
            # Predict future behavior
            predictions = cls._predict_future_behavior(patterns)
            
            return {
                'user_id': user_id,
                'investment_patterns': patterns,
                'predicted_preferences': predictions['preferences'],
                'predicted_risk_tolerance': predictions['risk_tolerance'],
                'predicted_investment_amount': predictions['investment_amount'],
                'recommended_campaigns': cls._recommend_campaigns_for_user(user_id, patterns),
                'behavior_insights': cls._generate_behavior_insights(patterns)
            }
            
        except Exception as e:
            logger.error(f"Investor behavior prediction error: {e}")
            return {'error': f'Behavior prediction failed: {str(e)}'}
    
    @classmethod
    def _extract_campaign_features(cls, campaign_data: Dict) -> Dict:
        """Extract features from campaign data for ML model"""
        features = {
            'funding_goal': campaign_data.get('funding_goal', 0),
            'duration_days': campaign_data.get('duration_days', 30),
            'category': campaign_data.get('category', ''),
            'creator_experience': campaign_data.get('creator_experience', 0),
            'has_video': campaign_data.get('has_video', False),
            'has_images': campaign_data.get('has_images', False),
            'description_length': len(campaign_data.get('description', '')),
            'social_media_followers': campaign_data.get('social_media_followers', 0),
            'previous_campaigns': campaign_data.get('previous_campaigns', 0),
            'team_size': campaign_data.get('team_size', 1),
            'budget_breakdown_quality': campaign_data.get('budget_breakdown_quality', 0),
            'timeline_realism': campaign_data.get('timeline_realism', 0),
            'market_demand': campaign_data.get('market_demand', 0),
            'competition_level': campaign_data.get('competition_level', 0),
            'seasonality_factor': campaign_data.get('seasonality_factor', 0)
        }
        return features
    
    @classmethod
    def _calculate_success_probability(cls, features: Dict) -> float:
        """Calculate campaign success probability using ML model"""
        try:
            # This would use a trained ML model in production
            # For now, we'll use a simplified scoring system
            
            score = 0.0
            
            # Funding goal factor (lower goals have higher success rate)
            goal = features.get('funding_goal', 0)
            if goal < 10000:
                score += 0.3
            elif goal < 50000:
                score += 0.2
            elif goal < 100000:
                score += 0.1
            
            # Duration factor (optimal duration is 30-45 days)
            duration = features.get('duration_days', 30)
            if 30 <= duration <= 45:
                score += 0.2
            elif 20 <= duration <= 60:
                score += 0.1
            
            # Creator experience factor
            experience = features.get('creator_experience', 0)
            if experience > 5:
                score += 0.2
            elif experience > 2:
                score += 0.1
            
            # Content quality factors
            if features.get('has_video', False):
                score += 0.1
            if features.get('has_images', False):
                score += 0.05
            
            # Description quality
            desc_length = features.get('description_length', 0)
            if desc_length > 500:
                score += 0.1
            elif desc_length > 200:
                score += 0.05
            
            # Social media presence
            followers = features.get('social_media_followers', 0)
            if followers > 10000:
                score += 0.15
            elif followers > 1000:
                score += 0.1
            
            # Previous campaign success
            prev_campaigns = features.get('previous_campaigns', 0)
            if prev_campaigns > 0:
                score += 0.1
            
            # Market factors
            market_demand = features.get('market_demand', 0)
            if market_demand > 0.7:
                score += 0.1
            elif market_demand > 0.5:
                score += 0.05
            
            # Normalize to 0-1 probability
            probability = min(max(score, 0.0), 1.0)
            
            return round(probability, 3)
            
        except Exception as e:
            logger.error(f"Success probability calculation error: {e}")
            return 0.5  # Default probability
    
    @classmethod
    def _calculate_confidence_level(cls, features: Dict) -> str:
        """Calculate confidence level for prediction"""
        try:
            # Factors that increase confidence
            confidence_score = 0
            
            if features.get('creator_experience', 0) > 3:
                confidence_score += 1
            if features.get('previous_campaigns', 0) > 0:
                confidence_score += 1
            if features.get('social_media_followers', 0) > 5000:
                confidence_score += 1
            if features.get('description_length', 0) > 300:
                confidence_score += 1
            if features.get('budget_breakdown_quality', 0) > 0.7:
                confidence_score += 1
            
            if confidence_score >= 4:
                return 'HIGH'
            elif confidence_score >= 2:
                return 'MEDIUM'
            else:
                return 'LOW'
                
        except Exception as e:
            logger.error(f"Confidence level calculation error: {e}")
            return 'LOW'
    
    @classmethod
    def _identify_key_factors(cls, features: Dict) -> List[Dict]:
        """Identify key factors affecting campaign success"""
        factors = []
        
        # Creator experience
        experience = features.get('creator_experience', 0)
        if experience > 5:
            factors.append({
                'factor': 'Creator Experience',
                'value': f'{experience} years',
                'impact': 'positive',
                'description': 'Experienced creators have higher success rates'
            })
        elif experience < 1:
            factors.append({
                'factor': 'Creator Experience',
                'value': f'{experience} years',
                'impact': 'negative',
                'description': 'First-time creators face higher challenges'
            })
        
        # Funding goal
        goal = features.get('funding_goal', 0)
        if goal > 100000:
            factors.append({
                'factor': 'Funding Goal',
                'value': f'${goal:,}',
                'impact': 'negative',
                'description': 'High funding goals reduce success probability'
            })
        elif goal < 10000:
            factors.append({
                'factor': 'Funding Goal',
                'value': f'${goal:,}',
                'impact': 'positive',
                'description': 'Moderate funding goals increase success probability'
            })
        
        # Social media presence
        followers = features.get('social_media_followers', 0)
        if followers > 10000:
            factors.append({
                'factor': 'Social Media Presence',
                'value': f'{followers:,} followers',
                'impact': 'positive',
                'description': 'Strong social media presence helps reach goals'
            })
        elif followers < 100:
            factors.append({
                'factor': 'Social Media Presence',
                'value': f'{followers:,} followers',
                'impact': 'negative',
                'description': 'Limited social media reach may hinder success'
            })
        
        return factors
    
    @classmethod
    def _generate_campaign_insights(cls, features: Dict, success_probability: float) -> List[str]:
        """Generate insights about the campaign"""
        insights = []
        
        if success_probability > 0.7:
            insights.append("This campaign has a high probability of success based on current factors.")
        elif success_probability > 0.4:
            insights.append("This campaign has a moderate probability of success with room for improvement.")
        else:
            insights.append("This campaign may face challenges. Consider optimizing key factors.")
        
        # Duration insights
        duration = features.get('duration_days', 30)
        if duration < 20:
            insights.append("Campaign duration is quite short. Consider extending to 30-45 days for better results.")
        elif duration > 60:
            insights.append("Campaign duration is quite long. Shorter campaigns often perform better.")
        
        # Content insights
        if not features.get('has_video', False):
            insights.append("Adding a campaign video could significantly improve success probability.")
        
        if features.get('description_length', 0) < 200:
            insights.append("Consider expanding the campaign description to provide more details.")
        
        return insights
    
    @classmethod
    def _generate_recommendations(cls, features: Dict, success_probability: float) -> List[Dict]:
        """Generate recommendations to improve campaign success"""
        recommendations = []
        
        # Video recommendation
        if not features.get('has_video', False):
            recommendations.append({
                'type': 'content',
                'priority': 'high',
                'title': 'Add Campaign Video',
                'description': 'Create an engaging video explaining your project',
                'expected_impact': '+15% success probability'
            })
        
        # Description improvement
        if features.get('description_length', 0) < 500:
            recommendations.append({
                'type': 'content',
                'priority': 'medium',
                'title': 'Expand Description',
                'description': 'Add more details about your project, team, and goals',
                'expected_impact': '+10% success probability'
            })
        
        # Social media
        if features.get('social_media_followers', 0) < 1000:
            recommendations.append({
                'type': 'marketing',
                'priority': 'high',
                'title': 'Build Social Media Presence',
                'description': 'Increase your social media following before launching',
                'expected_impact': '+20% success probability'
            })
        
        # Funding goal adjustment
        goal = features.get('funding_goal', 0)
        if goal > 50000 and success_probability < 0.5:
            recommendations.append({
                'type': 'strategy',
                'priority': 'high',
                'title': 'Consider Lower Funding Goal',
                'description': 'Start with a smaller goal and use stretch goals',
                'expected_impact': '+25% success probability'
            })
        
        return recommendations
    
    @classmethod
    def _identify_risk_factors(cls, features: Dict) -> List[Dict]:
        """Identify risk factors for the campaign"""
        risks = []
        
        # High funding goal risk
        goal = features.get('funding_goal', 0)
        if goal > 100000:
            risks.append({
                'factor': 'High Funding Goal',
                'severity': 'high',
                'description': 'Very high funding goals are difficult to achieve',
                'mitigation': 'Consider breaking into phases or reducing goal'
            })
        
        # Inexperienced creator risk
        experience = features.get('creator_experience', 0)
        if experience < 1:
            risks.append({
                'factor': 'Inexperienced Creator',
                'severity': 'medium',
                'description': 'First-time creators face higher failure rates',
                'mitigation': 'Seek mentorship or partner with experienced creators'
            })
        
        # Limited social presence risk
        followers = features.get('social_media_followers', 0)
        if followers < 500:
            risks.append({
                'factor': 'Limited Social Media Presence',
                'severity': 'medium',
                'description': 'Low social media following limits reach',
                'mitigation': 'Build social media presence before launching'
            })
        
        # Short duration risk
        duration = features.get('duration_days', 30)
        if duration < 20:
            risks.append({
                'factor': 'Short Campaign Duration',
                'severity': 'low',
                'description': 'Very short campaigns may not reach enough people',
                'mitigation': 'Extend campaign duration to 30-45 days'
            })
        
        return risks


class ContentRecommendationService:
    """
    Service for content recommendation and discovery
    """
    
    @classmethod
    def recommend_campaigns(cls, user_id: int, limit: int = 10) -> List[Dict]:
        """Recommend campaigns to a user based on their preferences"""
        try:
            # Get user preferences and history
            user_preferences = cls._get_user_preferences(user_id)
            user_history = cls._get_user_history(user_id)
            
            # Get available campaigns
            available_campaigns = cls._get_available_campaigns()
            
            # Calculate recommendation scores
            recommendations = []
            for campaign in available_campaigns:
                score = cls._calculate_recommendation_score(campaign, user_preferences, user_history)
                if score > 0.3:  # Only recommend campaigns with decent match
                    recommendations.append({
                        'campaign': campaign,
                        'score': score,
                        'reasons': cls._get_recommendation_reasons(campaign, user_preferences)
                    })
            
            # Sort by score and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Campaign recommendation error: {e}")
            return []
    
    @classmethod
    def recommend_content_for_ott(cls, user_id: int, platform: str) -> List[Dict]:
        """Recommend content for OTT platform distribution"""
        try:
            # Get user's content preferences
            preferences = cls._get_user_content_preferences(user_id)
            
            # Get content performance data
            content_performance = cls._get_content_performance_data(platform)
            
            # Calculate recommendations
            recommendations = []
            for content in content_performance:
                score = cls._calculate_content_recommendation_score(content, preferences)
                if score > 0.4:
                    recommendations.append({
                        'content': content,
                        'score': score,
                        'platform': platform,
                        'expected_performance': cls._predict_content_performance(content, platform)
                    })
            
            # Sort by score and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:10]
            
        except Exception as e:
            logger.error(f"Content recommendation error: {e}")
            return []
    
    @classmethod
    def _get_user_preferences(cls, user_id: int) -> Dict:
        """Get user preferences from their activity"""
        try:
            # This would analyze user's past investments, views, etc.
            # For now, return default preferences
            return {
                'preferred_categories': ['drama', 'comedy', 'documentary'],
                'preferred_funding_range': [1000, 50000],
                'preferred_duration': [30, 45],
                'risk_tolerance': 'medium',
                'investment_frequency': 'monthly'
            }
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}
    
    @classmethod
    def _calculate_recommendation_score(cls, campaign: Dict, preferences: Dict, history: Dict) -> float:
        """Calculate recommendation score for a campaign"""
        try:
            score = 0.0
            
            # Category match
            campaign_category = campaign.get('category', '').lower()
            preferred_categories = [cat.lower() for cat in preferences.get('preferred_categories', [])]
            if campaign_category in preferred_categories:
                score += 0.3
            
            # Funding range match
            campaign_goal = campaign.get('funding_goal', 0)
            preferred_range = preferences.get('preferred_funding_range', [0, 100000])
            if preferred_range[0] <= campaign_goal <= preferred_range[1]:
                score += 0.2
            
            # Duration match
            campaign_duration = campaign.get('duration_days', 30)
            preferred_duration = preferences.get('preferred_duration', [20, 60])
            if preferred_duration[0] <= campaign_duration <= preferred_duration[1]:
                score += 0.1
            
            # Creator experience
            creator_exp = campaign.get('creator_experience', 0)
            if creator_exp > 3:
                score += 0.2
            
            # Social proof
            if campaign.get('backers_count', 0) > 10:
                score += 0.1
            
            # Progress
            progress = campaign.get('progress_percentage', 0)
            if progress > 20:
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Recommendation score calculation error: {e}")
            return 0.0


class RiskAssessmentService:
    """
    Service for risk assessment and fraud detection
    """
    
    @classmethod
    def assess_investment_risk(cls, user_id: int, campaign_id: int, amount: float) -> Dict:
        """Assess risk for an investment"""
        try:
            # Get user risk profile
            user_risk_profile = cls._get_user_risk_profile(user_id)
            
            # Get campaign risk factors
            campaign_risk_factors = cls._get_campaign_risk_factors(campaign_id)
            
            # Calculate overall risk score
            risk_score = cls._calculate_risk_score(user_risk_profile, campaign_risk_factors, amount)
            
            # Determine risk level
            risk_level = cls._determine_risk_level(risk_score)
            
            # Generate risk factors
            risk_factors = cls._identify_risk_factors(user_risk_profile, campaign_risk_factors)
            
            return {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'recommendations': cls._generate_risk_recommendations(risk_factors),
                'requires_approval': risk_level in ['HIGH', 'CRITICAL']
            }
            
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            return {'error': f'Risk assessment failed: {str(e)}'}
    
    @classmethod
    def detect_fraud(cls, transaction_data: Dict) -> Dict:
        """Detect potential fraud in transactions"""
        try:
            fraud_indicators = []
            fraud_score = 0.0
            
            # Check for unusual patterns
            if cls._is_unusual_transaction_pattern(transaction_data):
                fraud_indicators.append('Unusual transaction pattern')
                fraud_score += 0.3
            
            # Check for suspicious amounts
            if cls._is_suspicious_amount(transaction_data):
                fraud_indicators.append('Suspicious transaction amount')
                fraud_score += 0.2
            
            # Check for rapid transactions
            if cls._is_rapid_transaction(transaction_data):
                fraud_indicators.append('Rapid transaction sequence')
                fraud_score += 0.2
            
            # Check for location anomalies
            if cls._is_location_anomaly(transaction_data):
                fraud_indicators.append('Location anomaly detected')
                fraud_score += 0.3
            
            # Determine fraud risk
            if fraud_score >= 0.7:
                fraud_risk = 'HIGH'
            elif fraud_score >= 0.4:
                fraud_risk = 'MEDIUM'
            else:
                fraud_risk = 'LOW'
            
            return {
                'fraud_risk': fraud_risk,
                'fraud_score': fraud_score,
                'indicators': fraud_indicators,
                'requires_review': fraud_risk in ['HIGH', 'MEDIUM'],
                'recommended_actions': cls._get_fraud_actions(fraud_risk)
            }
            
        except Exception as e:
            logger.error(f"Fraud detection error: {e}")
            return {'error': f'Fraud detection failed: {str(e)}'}
    
    @classmethod
    def _get_user_risk_profile(cls, user_id: int) -> Dict:
        """Get user's risk profile"""
        try:
            # This would analyze user's transaction history, behavior, etc.
            return {
                'account_age_days': 365,
                'total_investments': 10,
                'average_investment': 5000,
                'investment_frequency': 'monthly',
                'kyc_status': 'verified',
                'payment_methods': ['bank_transfer', 'stripe'],
                'location_consistency': 0.9,
                'device_consistency': 0.8
            }
        except Exception as e:
            logger.error(f"Error getting user risk profile: {e}")
            return {}
    
    @classmethod
    def _calculate_risk_score(cls, user_profile: Dict, campaign_factors: Dict, amount: float) -> float:
        """Calculate overall risk score"""
        try:
            risk_score = 0.0
            
            # User risk factors
            if user_profile.get('kyc_status') != 'verified':
                risk_score += 0.2
            
            if user_profile.get('account_age_days', 0) < 30:
                risk_score += 0.1
            
            if amount > user_profile.get('average_investment', 0) * 5:
                risk_score += 0.2
            
            # Campaign risk factors
            if campaign_factors.get('creator_experience', 0) < 1:
                risk_score += 0.1
            
            if campaign_factors.get('success_rate', 1.0) < 0.5:
                risk_score += 0.2
            
            # Amount risk
            if amount > 50000:
                risk_score += 0.1
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Risk score calculation error: {e}")
            return 0.5
    
    @classmethod
    def _determine_risk_level(cls, risk_score: float) -> str:
        """Determine risk level from score"""
        if risk_score >= 0.8:
            return 'CRITICAL'
        elif risk_score >= 0.6:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'

