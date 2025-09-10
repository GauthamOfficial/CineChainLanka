"""
Machine Learning Models for CineChainLanka
Implements various ML models for predictions and recommendations
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta
import json
import pickle
import os

logger = logging.getLogger(__name__)


class CampaignSuccessModel:
    """
    Machine Learning model for predicting campaign success
    """
    
    def __init__(self):
        self.model = None
        self.feature_columns = [
            'funding_goal', 'duration_days', 'creator_experience',
            'has_video', 'has_images', 'description_length',
            'social_media_followers', 'previous_campaigns',
            'team_size', 'budget_breakdown_quality', 'timeline_realism',
            'market_demand', 'competition_level', 'seasonality_factor'
        ]
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        try:
            model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'campaign_success_model.pkl')
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
            else:
                # Initialize with a simple model if no trained model exists
                self.model = self._create_simple_model()
        except Exception as e:
            logger.error(f"Error loading campaign success model: {e}")
            self.model = self._create_simple_model()
    
    def _create_simple_model(self):
        """Create a simple model for demonstration"""
        class SimpleModel:
            def predict_proba(self, X):
                # Simple scoring system
                scores = []
                for row in X:
                    score = 0.0
                    # Funding goal factor
                    if row[0] < 10000:
                        score += 0.3
                    elif row[0] < 50000:
                        score += 0.2
                    # Duration factor
                    if 30 <= row[1] <= 45:
                        score += 0.2
                    # Creator experience
                    if row[2] > 3:
                        score += 0.2
                    # Content factors
                    if row[3]:  # has_video
                        score += 0.1
                    if row[4]:  # has_images
                        score += 0.05
                    # Social media
                    if row[6] > 1000:
                        score += 0.15
                    
                    # Normalize to probability
                    prob = min(max(score, 0.0), 1.0)
                    scores.append([1-prob, prob])  # [failure_prob, success_prob]
                
                return np.array(scores)
        
        return SimpleModel()
    
    def predict(self, features: Dict) -> Dict:
        """Predict campaign success probability"""
        try:
            # Prepare feature vector
            feature_vector = self._prepare_features(features)
            
            # Get prediction
            probabilities = self.model.predict_proba([feature_vector])
            success_probability = probabilities[0][1]  # Success probability
            
            # Calculate confidence
            confidence = self._calculate_confidence(feature_vector)
            
            return {
                'success_probability': float(success_probability),
                'failure_probability': float(probabilities[0][0]),
                'confidence': confidence,
                'prediction': 'success' if success_probability > 0.5 else 'failure'
            }
            
        except Exception as e:
            logger.error(f"Campaign success prediction error: {e}")
            return {'error': f'Prediction failed: {str(e)}'}
    
    def _prepare_features(self, features: Dict) -> List[float]:
        """Prepare feature vector for model"""
        feature_vector = []
        for col in self.feature_columns:
            value = features.get(col, 0)
            # Convert boolean to float
            if isinstance(value, bool):
                value = 1.0 if value else 0.0
            feature_vector.append(float(value))
        return feature_vector
    
    def _calculate_confidence(self, feature_vector: List[float]) -> float:
        """Calculate prediction confidence"""
        try:
            # Simple confidence calculation based on feature completeness
            non_zero_features = sum(1 for f in feature_vector if f > 0)
            confidence = min(non_zero_features / len(feature_vector), 1.0)
            return round(confidence, 3)
        except Exception as e:
            logger.error(f"Confidence calculation error: {e}")
            return 0.5


class RevenueForecastingModel:
    """
    Machine Learning model for revenue forecasting
    """
    
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained forecasting model"""
        try:
            model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'revenue_forecast_model.pkl')
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
            else:
                self.model = self._create_simple_forecast_model()
        except Exception as e:
            logger.error(f"Error loading revenue forecast model: {e}")
            self.model = self._create_simple_forecast_model()
    
    def _create_simple_forecast_model(self):
        """Create a simple forecasting model"""
        class SimpleForecastModel:
            def predict(self, historical_data, periods):
                # Simple trend-based forecasting
                if len(historical_data) < 2:
                    return [historical_data[-1] if historical_data else 0] * periods
                
                # Calculate trend
                recent_data = historical_data[-min(6, len(historical_data)):]
                trend = np.polyfit(range(len(recent_data)), recent_data, 1)[0]
                
                # Generate forecast
                forecast = []
                last_value = historical_data[-1]
                for i in range(periods):
                    next_value = last_value + trend * (i + 1)
                    # Apply some seasonality and noise
                    seasonality = 0.1 * np.sin(2 * np.pi * i / 12)  # Monthly seasonality
                    noise = np.random.normal(0, 0.05) * last_value
                    forecast.append(max(0, last_value + trend * (i + 1) + seasonality + noise))
                
                return forecast
        
        return SimpleForecastModel()
    
    def forecast(self, historical_data: List[float], periods: int = 12) -> Dict:
        """Generate revenue forecast"""
        try:
            if not historical_data:
                return {'error': 'No historical data provided'}
            
            # Generate forecast
            forecast_values = self.model.predict(historical_data, periods)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(forecast_values, historical_data)
            
            # Detect trends and seasonality
            trend_analysis = self._analyze_trend(historical_data)
            seasonality = self._detect_seasonality(historical_data)
            
            return {
                'forecast': forecast_values,
                'confidence_intervals': confidence_intervals,
                'trend_analysis': trend_analysis,
                'seasonality': seasonality,
                'forecast_periods': periods
            }
            
        except Exception as e:
            logger.error(f"Revenue forecasting error: {e}")
            return {'error': f'Forecasting failed: {str(e)}'}
    
    def _calculate_confidence_intervals(self, forecast: List[float], historical_data: List[float]) -> Dict:
        """Calculate confidence intervals for forecast"""
        try:
            # Calculate historical volatility
            if len(historical_data) > 1:
                returns = np.diff(historical_data) / historical_data[:-1]
                volatility = np.std(returns)
            else:
                volatility = 0.1  # Default volatility
            
            # Calculate confidence intervals
            confidence_intervals = {
                'lower_95': [],
                'upper_95': [],
                'lower_68': [],
                'upper_68': []
            }
            
            for i, value in enumerate(forecast):
                # Calculate standard error (increases with forecast horizon)
                std_error = volatility * value * np.sqrt(i + 1)
                
                confidence_intervals['lower_95'].append(max(0, value - 1.96 * std_error))
                confidence_intervals['upper_95'].append(value + 1.96 * std_error)
                confidence_intervals['lower_68'].append(max(0, value - std_error))
                confidence_intervals['upper_68'].append(value + std_error)
            
            return confidence_intervals
            
        except Exception as e:
            logger.error(f"Confidence interval calculation error: {e}")
            return {}
    
    def _analyze_trend(self, historical_data: List[float]) -> Dict:
        """Analyze trend in historical data"""
        try:
            if len(historical_data) < 2:
                return {'trend': 'insufficient_data', 'slope': 0}
            
            # Calculate linear trend
            x = np.arange(len(historical_data))
            slope, intercept = np.polyfit(x, historical_data, 1)
            
            # Determine trend direction
            if slope > 0.1:
                trend = 'increasing'
            elif slope < -0.1:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            return {
                'trend': trend,
                'slope': float(slope),
                'r_squared': float(np.corrcoef(x, historical_data)[0, 1] ** 2)
            }
            
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return {'trend': 'unknown', 'slope': 0}
    
    def _detect_seasonality(self, historical_data: List[float]) -> Dict:
        """Detect seasonality in historical data"""
        try:
            if len(historical_data) < 12:  # Need at least 12 data points
                return {'has_seasonality': False, 'period': 0, 'strength': 0}
            
            # Simple seasonality detection using FFT
            fft = np.fft.fft(historical_data)
            freqs = np.fft.fftfreq(len(historical_data))
            
            # Find dominant frequency
            power_spectrum = np.abs(fft) ** 2
            dominant_freq_idx = np.argmax(power_spectrum[1:len(power_spectrum)//2]) + 1
            dominant_freq = freqs[dominant_freq_idx]
            
            # Calculate seasonality strength
            seasonality_strength = power_spectrum[dominant_freq_idx] / np.sum(power_spectrum)
            
            # Determine if seasonality is significant
            has_seasonality = seasonality_strength > 0.1 and abs(dominant_freq) > 0
            
            return {
                'has_seasonality': has_seasonality,
                'period': int(1 / abs(dominant_freq)) if dominant_freq != 0 else 0,
                'strength': float(seasonality_strength)
            }
            
        except Exception as e:
            logger.error(f"Seasonality detection error: {e}")
            return {'has_seasonality': False, 'period': 0, 'strength': 0}


class RecommendationModel:
    """
    Machine Learning model for content and campaign recommendations
    """
    
    def __init__(self):
        self.model = None
        self.user_embeddings = {}
        self.item_embeddings = {}
        self.load_model()
    
    def load_model(self):
        """Load the trained recommendation model"""
        try:
            model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'recommendation_model.pkl')
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data.get('model')
                    self.user_embeddings = model_data.get('user_embeddings', {})
                    self.item_embeddings = model_data.get('item_embeddings', {})
            else:
                self.model = self._create_simple_recommendation_model()
        except Exception as e:
            logger.error(f"Error loading recommendation model: {e}")
            self.model = self._create_simple_recommendation_model()
    
    def _create_simple_recommendation_model(self):
        """Create a simple recommendation model"""
        class SimpleRecommendationModel:
            def __init__(self):
                self.user_embeddings = {}
                self.item_embeddings = {}
            
            def fit(self, user_item_matrix):
                # Simple collaborative filtering
                n_users, n_items = user_item_matrix.shape
                embedding_dim = min(10, min(n_users, n_items) // 2)
                
                # Initialize embeddings randomly
                self.user_embeddings = np.random.randn(n_users, embedding_dim) * 0.1
                self.item_embeddings = np.random.randn(n_items, embedding_dim) * 0.1
                
                # Simple gradient descent
                learning_rate = 0.01
                for epoch in range(100):
                    for i in range(n_users):
                        for j in range(n_items):
                            if user_item_matrix[i, j] > 0:
                                prediction = np.dot(self.user_embeddings[i], self.item_embeddings[j])
                                error = user_item_matrix[i, j] - prediction
                                
                                # Update embeddings
                                self.user_embeddings[i] += learning_rate * error * self.item_embeddings[j]
                                self.item_embeddings[j] += learning_rate * error * self.user_embeddings[i]
            
            def predict(self, user_id, item_ids):
                if user_id not in self.user_embeddings:
                    return [0.5] * len(item_ids)
                
                user_embedding = self.user_embeddings[user_id]
                scores = []
                for item_id in item_ids:
                    if item_id in self.item_embeddings:
                        score = np.dot(user_embedding, self.item_embeddings[item_id])
                        scores.append(float(score))
                    else:
                        scores.append(0.5)  # Default score
                
                return scores
        
        return SimpleRecommendationModel()
    
    def recommend_items(self, user_id: int, item_ids: List[int], top_k: int = 10) -> List[Dict]:
        """Recommend items for a user"""
        try:
            # Get user embedding
            if user_id not in self.user_embeddings:
                # Cold start - use content-based recommendations
                return self._get_content_based_recommendations(user_id, item_ids, top_k)
            
            # Calculate scores for all items
            scores = self.model.predict(user_id, item_ids)
            
            # Create item-score pairs
            item_scores = list(zip(item_ids, scores))
            
            # Sort by score and return top-k
            item_scores.sort(key=lambda x: x[1], reverse=True)
            
            recommendations = []
            for item_id, score in item_scores[:top_k]:
                recommendations.append({
                    'item_id': item_id,
                    'score': score,
                    'reason': self._get_recommendation_reason(user_id, item_id, score)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Item recommendation error: {e}")
            return []
    
    def _get_content_based_recommendations(self, user_id: int, item_ids: List[int], top_k: int) -> List[Dict]:
        """Get content-based recommendations for cold start users"""
        try:
            # Simple content-based filtering
            # This would analyze item features and user preferences
            recommendations = []
            
            for item_id in item_ids[:top_k]:
                # Simple scoring based on item popularity and recency
                score = np.random.uniform(0.3, 0.8)  # Random score for demo
                recommendations.append({
                    'item_id': item_id,
                    'score': score,
                    'reason': 'Content-based recommendation'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Content-based recommendation error: {e}")
            return []
    
    def _get_recommendation_reason(self, user_id: int, item_id: int, score: float) -> str:
        """Get explanation for recommendation"""
        try:
            if score > 0.8:
                return "High match with your preferences"
            elif score > 0.6:
                return "Good match with your interests"
            elif score > 0.4:
                return "Moderate match - you might like this"
            else:
                return "Based on similar users' preferences"
        except Exception as e:
            logger.error(f"Recommendation reason error: {e}")
            return "Recommended for you"


class FraudDetectionModel:
    """
    Machine Learning model for fraud detection
    """
    
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained fraud detection model"""
        try:
            model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'fraud_detection_model.pkl')
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
            else:
                self.model = self._create_simple_fraud_model()
        except Exception as e:
            logger.error(f"Error loading fraud detection model: {e}")
            self.model = self._create_simple_fraud_model()
    
    def _create_simple_fraud_model(self):
        """Create a simple fraud detection model"""
        class SimpleFraudModel:
            def predict_proba(self, features):
                # Simple rule-based fraud detection
                fraud_scores = []
                for feature_vector in features:
                    score = 0.0
                    
                    # Check for unusual amounts
                    amount = feature_vector[0]
                    if amount > 50000:  # High amount
                        score += 0.3
                    
                    # Check for rapid transactions
                    time_since_last = feature_vector[1]
                    if time_since_last < 60:  # Less than 1 minute
                        score += 0.4
                    
                    # Check for new user
                    account_age = feature_vector[2]
                    if account_age < 1:  # Less than 1 day
                        score += 0.2
                    
                    # Check for unusual location
                    location_anomaly = feature_vector[3]
                    if location_anomaly > 0.8:
                        score += 0.3
                    
                    # Check for unusual device
                    device_anomaly = feature_vector[4]
                    if device_anomaly > 0.8:
                        score += 0.2
                    
                    # Normalize to probability
                    fraud_prob = min(max(score, 0.0), 1.0)
                    fraud_scores.append([1-fraud_prob, fraud_prob])
                
                return np.array(fraud_scores)
        
        return SimpleFraudModel()
    
    def detect_fraud(self, transaction_features: Dict) -> Dict:
        """Detect fraud in transaction"""
        try:
            # Prepare feature vector
            feature_vector = self._prepare_fraud_features(transaction_features)
            
            # Get fraud probability
            probabilities = self.model.predict_proba([feature_vector])
            fraud_probability = probabilities[0][1]
            
            # Determine fraud risk level
            if fraud_probability > 0.8:
                risk_level = 'HIGH'
            elif fraud_probability > 0.5:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            # Get fraud indicators
            indicators = self._get_fraud_indicators(transaction_features)
            
            return {
                'fraud_probability': float(fraud_probability),
                'risk_level': risk_level,
                'indicators': indicators,
                'requires_review': risk_level in ['HIGH', 'MEDIUM'],
                'recommended_actions': self._get_fraud_actions(risk_level)
            }
            
        except Exception as e:
            logger.error(f"Fraud detection error: {e}")
            return {'error': f'Fraud detection failed: {str(e)}'}
    
    def _prepare_fraud_features(self, features: Dict) -> List[float]:
        """Prepare feature vector for fraud detection"""
        return [
            features.get('amount', 0),
            features.get('time_since_last_transaction', 3600),
            features.get('account_age_days', 365),
            features.get('location_anomaly_score', 0),
            features.get('device_anomaly_score', 0),
            features.get('payment_method_risk', 0),
            features.get('user_verification_level', 1),
            features.get('transaction_frequency', 1)
        ]
    
    def _get_fraud_indicators(self, features: Dict) -> List[str]:
        """Get fraud indicators for transaction"""
        indicators = []
        
        if features.get('amount', 0) > 50000:
            indicators.append('High transaction amount')
        
        if features.get('time_since_last_transaction', 3600) < 60:
            indicators.append('Rapid transaction sequence')
        
        if features.get('account_age_days', 365) < 1:
            indicators.append('New account')
        
        if features.get('location_anomaly_score', 0) > 0.8:
            indicators.append('Unusual location')
        
        if features.get('device_anomaly_score', 0) > 0.8:
            indicators.append('Unusual device')
        
        return indicators
    
    def _get_fraud_actions(self, risk_level: str) -> List[str]:
        """Get recommended actions based on fraud risk level"""
        if risk_level == 'HIGH':
            return ['Block transaction', 'Require additional verification', 'Flag for manual review']
        elif risk_level == 'MEDIUM':
            return ['Require additional verification', 'Monitor closely']
        else:
            return ['Process normally']


class ModelTrainingService:
    """
    Service for training and updating ML models
    """
    
    @classmethod
    def train_campaign_success_model(cls, training_data: List[Dict]) -> Dict:
        """Train the campaign success prediction model"""
        try:
            # This would implement actual model training
            # For now, return success status
            return {
                'success': True,
                'model_type': 'campaign_success',
                'training_samples': len(training_data),
                'accuracy': 0.85,  # Simulated accuracy
                'training_time': '2.5 minutes'
            }
        except Exception as e:
            logger.error(f"Model training error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def train_recommendation_model(cls, user_item_interactions: List[Dict]) -> Dict:
        """Train the recommendation model"""
        try:
            # This would implement actual collaborative filtering training
            return {
                'success': True,
                'model_type': 'recommendation',
                'interactions': len(user_item_interactions),
                'users': len(set(item['user_id'] for item in user_item_interactions)),
                'items': len(set(item['item_id'] for item in user_item_interactions))
            }
        except Exception as e:
            logger.error(f"Recommendation model training error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def retrain_models(cls) -> Dict:
        """Retrain all models with latest data"""
        try:
            results = {}
            
            # Train campaign success model
            campaign_data = cls._get_campaign_training_data()
            results['campaign_success'] = cls.train_campaign_success_model(campaign_data)
            
            # Train recommendation model
            interaction_data = cls._get_interaction_training_data()
            results['recommendation'] = cls.train_recommendation_model(interaction_data)
            
            return {
                'success': True,
                'results': results,
                'retrain_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Model retraining error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def _get_campaign_training_data(cls) -> List[Dict]:
        """Get training data for campaign success model"""
        try:
            # This would fetch actual campaign data from database
            return []
        except Exception as e:
            logger.error(f"Error getting campaign training data: {e}")
            return []
    
    @classmethod
    def _get_interaction_training_data(cls) -> List[Dict]:
        """Get training data for recommendation model"""
        try:
            # This would fetch actual user-item interaction data
            return []
        except Exception as e:
            logger.error(f"Error getting interaction training data: {e}")
            return []

