"""
Social Features Service for CineChainLanka
Handles community building, social interactions, and engagement features
"""

import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class SocialFeaturesService:
    """
    Service for social features and community building
    """
    
    @classmethod
    def create_community(cls, community_data: Dict) -> Dict:
        """Create a new community"""
        try:
            from users.models import User
            from campaigns.models import Community
            
            # Create community
            community = Community.objects.create(
                name=community_data.get('name'),
                description=community_data.get('description'),
                category=community_data.get('category'),
                creator_id=community_data.get('creator_id'),
                is_public=community_data.get('is_public', True),
                rules=community_data.get('rules', []),
                tags=community_data.get('tags', [])
            )
            
            # Add creator as admin
            community.members.add(community_data.get('creator_id'))
            community.admins.add(community_data.get('creator_id'))
            
            return {
                'success': True,
                'community_id': community.id,
                'community': {
                    'id': community.id,
                    'name': community.name,
                    'description': community.description,
                    'category': community.category,
                    'member_count': 1,
                    'created_at': community.created_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Community creation error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def join_community(cls, user_id: int, community_id: int) -> Dict:
        """Join a community"""
        try:
            from campaigns.models import Community
            
            community = Community.objects.get(id=community_id)
            
            # Check if user is already a member
            if community.members.filter(id=user_id).exists():
                return {'success': False, 'error': 'Already a member of this community'}
            
            # Add user to community
            community.members.add(user_id)
            
            # Send notification to community admins
            cls._notify_community_admins(community, user_id, 'join')
            
            return {
                'success': True,
                'message': 'Successfully joined community',
                'community_id': community_id,
                'member_count': community.members.count()
            }
            
        except Exception as e:
            logger.error(f"Community join error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def leave_community(cls, user_id: int, community_id: int) -> Dict:
        """Leave a community"""
        try:
            from campaigns.models import Community
            
            community = Community.objects.get(id=community_id)
            
            # Remove user from community
            community.members.remove(user_id)
            
            # Remove from admins if they were an admin
            if community.admins.filter(id=user_id).exists():
                community.admins.remove(user_id)
            
            return {
                'success': True,
                'message': 'Successfully left community',
                'community_id': community_id,
                'member_count': community.members.count()
            }
            
        except Exception as e:
            logger.error(f"Community leave error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def create_post(cls, post_data: Dict) -> Dict:
        """Create a social media post"""
        try:
            from campaigns.models import SocialPost
            
            post = SocialPost.objects.create(
                author_id=post_data.get('author_id'),
                content=post_data.get('content'),
                post_type=post_data.get('post_type', 'text'),
                media_urls=post_data.get('media_urls', []),
                campaign_id=post_data.get('campaign_id'),
                community_id=post_data.get('community_id'),
                is_public=post_data.get('is_public', True),
                tags=post_data.get('tags', [])
            )
            
            # Notify followers
            cls._notify_followers(post.author_id, post.id, 'post')
            
            return {
                'success': True,
                'post_id': post.id,
                'post': {
                    'id': post.id,
                    'content': post.content,
                    'author_id': post.author_id,
                    'created_at': post.created_at.isoformat(),
                    'likes_count': 0,
                    'comments_count': 0,
                    'shares_count': 0
                }
            }
            
        except Exception as e:
            logger.error(f"Post creation error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def like_post(cls, user_id: int, post_id: int) -> Dict:
        """Like a post"""
        try:
            from campaigns.models import SocialPost, PostLike
            
            post = SocialPost.objects.get(id=post_id)
            
            # Check if already liked
            if PostLike.objects.filter(user_id=user_id, post_id=post_id).exists():
                return {'success': False, 'error': 'Post already liked'}
            
            # Create like
            PostLike.objects.create(user_id=user_id, post_id=post_id)
            
            # Update post like count
            likes_count = PostLike.objects.filter(post_id=post_id).count()
            
            # Notify post author
            if post.author_id != user_id:
                cls._notify_user(post.author_id, f'Someone liked your post', 'like', post_id)
            
            return {
                'success': True,
                'likes_count': likes_count,
                'message': 'Post liked successfully'
            }
            
        except Exception as e:
            logger.error(f"Post like error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def comment_on_post(cls, user_id: int, post_id: int, comment_data: Dict) -> Dict:
        """Comment on a post"""
        try:
            from campaigns.models import SocialPost, PostComment
            
            post = SocialPost.objects.get(id=post_id)
            
            # Create comment
            comment = PostComment.objects.create(
                user_id=user_id,
                post_id=post_id,
                content=comment_data.get('content'),
                parent_comment_id=comment_data.get('parent_comment_id')
            )
            
            # Update post comment count
            comments_count = PostComment.objects.filter(post_id=post_id).count()
            
            # Notify post author
            if post.author_id != user_id:
                cls._notify_user(post.author_id, f'New comment on your post', 'comment', post_id)
            
            return {
                'success': True,
                'comment_id': comment.id,
                'comments_count': comments_count,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author_id': comment.user_id,
                    'created_at': comment.created_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Post comment error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def follow_user(cls, follower_id: int, following_id: int) -> Dict:
        """Follow a user"""
        try:
            from users.models import User, UserFollow
            
            if follower_id == following_id:
                return {'success': False, 'error': 'Cannot follow yourself'}
            
            # Check if already following
            if UserFollow.objects.filter(follower_id=follower_id, following_id=following_id).exists():
                return {'success': False, 'error': 'Already following this user'}
            
            # Create follow relationship
            UserFollow.objects.create(follower_id=follower_id, following_id=following_id)
            
            # Update follower counts
            follower_count = UserFollow.objects.filter(following_id=following_id).count()
            following_count = UserFollow.objects.filter(follower_id=follower_id).count()
            
            # Notify the user being followed
            cls._notify_user(following_id, f'You have a new follower', 'follow', follower_id)
            
            return {
                'success': True,
                'message': 'Successfully followed user',
                'follower_count': follower_count,
                'following_count': following_count
            }
            
        except Exception as e:
            logger.error(f"User follow error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def unfollow_user(cls, follower_id: int, following_id: int) -> Dict:
        """Unfollow a user"""
        try:
            from users.models import UserFollow
            
            # Remove follow relationship
            UserFollow.objects.filter(follower_id=follower_id, following_id=following_id).delete()
            
            # Update follower counts
            follower_count = UserFollow.objects.filter(following_id=following_id).count()
            following_count = UserFollow.objects.filter(follower_id=follower_id).count()
            
            return {
                'success': True,
                'message': 'Successfully unfollowed user',
                'follower_count': follower_count,
                'following_count': following_count
            }
            
        except Exception as e:
            logger.error(f"User unfollow error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_user_feed(cls, user_id: int, limit: int = 20, offset: int = 0) -> Dict:
        """Get user's social media feed"""
        try:
            from campaigns.models import SocialPost
            from users.models import UserFollow
            
            # Get users that the current user follows
            following_ids = UserFollow.objects.filter(follower_id=user_id).values_list('following_id', flat=True)
            
            # Get posts from followed users and public posts
            posts = SocialPost.objects.filter(
                Q(author_id__in=following_ids) | Q(is_public=True)
            ).order_by('-created_at')[offset:offset + limit]
            
            # Format posts
            feed_posts = []
            for post in posts:
                feed_posts.append({
                    'id': post.id,
                    'content': post.content,
                    'author': {
                        'id': post.author_id,
                        'username': post.author.username if hasattr(post, 'author') else 'Unknown'
                    },
                    'post_type': post.post_type,
                    'media_urls': post.media_urls,
                    'created_at': post.created_at.isoformat(),
                    'likes_count': post.likes_count,
                    'comments_count': post.comments_count,
                    'shares_count': post.shares_count,
                    'is_liked': cls._is_post_liked_by_user(post.id, user_id)
                })
            
            return {
                'success': True,
                'posts': feed_posts,
                'has_more': len(feed_posts) == limit
            }
            
        except Exception as e:
            logger.error(f"Feed generation error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_trending_topics(cls, limit: int = 10) -> List[Dict]:
        """Get trending topics and hashtags"""
        try:
            from campaigns.models import SocialPost
            
            # Get posts from last 7 days
            week_ago = datetime.now() - timedelta(days=7)
            recent_posts = SocialPost.objects.filter(created_at__gte=week_ago)
            
            # Extract hashtags and count frequency
            hashtag_counts = {}
            for post in recent_posts:
                tags = post.tags or []
                for tag in tags:
                    if tag.startswith('#'):
                        hashtag = tag.lower()
                        hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
            
            # Sort by frequency and return top hashtags
            trending_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            return [
                {
                    'hashtag': hashtag,
                    'count': count,
                    'trend_score': min(count / 10, 1.0)  # Normalize trend score
                }
                for hashtag, count in trending_hashtags
            ]
            
        except Exception as e:
            logger.error(f"Trending topics error: {e}")
            return []
    
    @classmethod
    def get_user_engagement_stats(cls, user_id: int) -> Dict:
        """Get user's engagement statistics"""
        try:
            from campaigns.models import SocialPost, PostLike, PostComment
            from users.models import UserFollow
            
            # Get user's posts
            user_posts = SocialPost.objects.filter(author_id=user_id)
            
            # Calculate engagement metrics
            total_posts = user_posts.count()
            total_likes = PostLike.objects.filter(post__author_id=user_id).count()
            total_comments = PostComment.objects.filter(post__author_id=user_id).count()
            total_shares = sum(post.shares_count for post in user_posts)
            
            # Calculate engagement rate
            total_engagement = total_likes + total_comments + total_shares
            engagement_rate = (total_engagement / total_posts) if total_posts > 0 else 0
            
            # Get follower/following counts
            followers_count = UserFollow.objects.filter(following_id=user_id).count()
            following_count = UserFollow.objects.filter(follower_id=user_id).count()
            
            return {
                'user_id': user_id,
                'posts_count': total_posts,
                'likes_received': total_likes,
                'comments_received': total_comments,
                'shares_received': total_shares,
                'total_engagement': total_engagement,
                'engagement_rate': round(engagement_rate, 2),
                'followers_count': followers_count,
                'following_count': following_count
            }
            
        except Exception as e:
            logger.error(f"Engagement stats error: {e}")
            return {'error': str(e)}
    
    @classmethod
    def _is_post_liked_by_user(cls, post_id: int, user_id: int) -> bool:
        """Check if user has liked a post"""
        try:
            from campaigns.models import PostLike
            return PostLike.objects.filter(post_id=post_id, user_id=user_id).exists()
        except Exception:
            return False
    
    @classmethod
    def _notify_followers(cls, user_id: int, post_id: int, notification_type: str) -> None:
        """Notify user's followers about new activity"""
        try:
            from users.models import UserFollow
            
            followers = UserFollow.objects.filter(following_id=user_id).values_list('follower_id', flat=True)
            
            for follower_id in followers:
                cls._notify_user(follower_id, f'New {notification_type} from someone you follow', notification_type, post_id)
                
        except Exception as e:
            logger.error(f"Follower notification error: {e}")
    
    @classmethod
    def _notify_user(cls, user_id: int, message: str, notification_type: str, reference_id: int) -> None:
        """Send notification to user"""
        try:
            from users.models import Notification
            
            Notification.objects.create(
                user_id=user_id,
                message=message,
                notification_type=notification_type,
                reference_id=reference_id,
                is_read=False
            )
            
        except Exception as e:
            logger.error(f"User notification error: {e}")
    
    @classmethod
    def _notify_community_admins(cls, community, user_id: int, action: str) -> None:
        """Notify community admins about new activity"""
        try:
            admin_ids = community.admins.values_list('id', flat=True)
            
            for admin_id in admin_ids:
                if admin_id != user_id:  # Don't notify the user who performed the action
                    cls._notify_user(admin_id, f'New {action} in community {community.name}', action, community.id)
                    
        except Exception as e:
            logger.error(f"Community admin notification error: {e}")


class InfluencerCollaborationService:
    """
    Service for influencer collaboration and partnerships
    """
    
    @classmethod
    def create_collaboration_request(cls, request_data: Dict) -> Dict:
        """Create a collaboration request with an influencer"""
        try:
            from campaigns.models import InfluencerCollaboration
            
            collaboration = InfluencerCollaboration.objects.create(
                campaign_id=request_data.get('campaign_id'),
                influencer_id=request_data.get('influencer_id'),
                requester_id=request_data.get('requester_id'),
                collaboration_type=request_data.get('collaboration_type'),
                proposed_terms=request_data.get('proposed_terms'),
                budget=request_data.get('budget'),
                status='pending'
            )
            
            # Notify influencer
            cls._notify_influencer(collaboration.influencer_id, collaboration.id)
            
            return {
                'success': True,
                'collaboration_id': collaboration.id,
                'message': 'Collaboration request sent successfully'
            }
            
        except Exception as e:
            logger.error(f"Collaboration request error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def respond_to_collaboration(cls, collaboration_id: int, response_data: Dict) -> Dict:
        """Respond to a collaboration request"""
        try:
            from campaigns.models import InfluencerCollaboration
            
            collaboration = InfluencerCollaboration.objects.get(id=collaboration_id)
            
            # Update collaboration status
            collaboration.status = response_data.get('status')
            if response_data.get('status') == 'accepted':
                collaboration.accepted_terms = response_data.get('accepted_terms')
                collaboration.agreed_budget = response_data.get('agreed_budget')
            collaboration.save()
            
            # Notify requester
            cls._notify_user(collaboration.requester_id, 
                           f'Collaboration request {response_data.get("status")}', 
                           'collaboration', collaboration_id)
            
            return {
                'success': True,
                'message': f'Collaboration request {response_data.get("status")}',
                'collaboration_id': collaboration_id
            }
            
        except Exception as e:
            logger.error(f"Collaboration response error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_influencer_recommendations(cls, campaign_id: int, limit: int = 10) -> List[Dict]:
        """Get influencer recommendations for a campaign"""
        try:
            from campaigns.models import Campaign
            from users.models import User
            
            campaign = Campaign.objects.get(id=campaign_id)
            campaign_category = campaign.category
            
            # Find influencers in the same category with good engagement
            influencers = User.objects.filter(
                user_type='influencer',
                categories__contains=[campaign_category],
                is_verified=True
            ).annotate(
                avg_engagement=Avg('social_engagement_rate')
            ).order_by('-avg_engagement')[:limit]
            
            recommendations = []
            for influencer in influencers:
                recommendations.append({
                    'influencer_id': influencer.id,
                    'username': influencer.username,
                    'followers_count': influencer.followers_count,
                    'engagement_rate': influencer.avg_engagement,
                    'categories': influencer.categories,
                    'collaboration_rate': influencer.collaboration_rate,
                    'match_score': cls._calculate_influencer_match_score(influencer, campaign)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Influencer recommendations error: {e}")
            return []
    
    @classmethod
    def _calculate_influencer_match_score(cls, influencer, campaign) -> float:
        """Calculate how well an influencer matches a campaign"""
        try:
            score = 0.0
            
            # Category match
            if campaign.category in influencer.categories:
                score += 0.4
            
            # Follower count match
            if campaign.funding_goal < 10000:
                if 1000 <= influencer.followers_count <= 10000:
                    score += 0.3
            elif campaign.funding_goal < 50000:
                if 10000 <= influencer.followers_count <= 100000:
                    score += 0.3
            else:
                if influencer.followers_count > 100000:
                    score += 0.3
            
            # Engagement rate
            if influencer.avg_engagement > 0.05:
                score += 0.3
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Influencer match score error: {e}")
            return 0.0
    
    @classmethod
    def _notify_influencer(cls, influencer_id: int, collaboration_id: int) -> None:
        """Notify influencer about collaboration request"""
        try:
            cls._notify_user(influencer_id, 'New collaboration request', 'collaboration', collaboration_id)
        except Exception as e:
            logger.error(f"Influencer notification error: {e}")
    
    @classmethod
    def _notify_user(cls, user_id: int, message: str, notification_type: str, reference_id: int) -> None:
        """Send notification to user"""
        try:
            from users.models import Notification
            
            Notification.objects.create(
                user_id=user_id,
                message=message,
                notification_type=notification_type,
                reference_id=reference_id,
                is_read=False
            )
            
        except Exception as e:
            logger.error(f"User notification error: {e}")

