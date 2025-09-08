import json
import logging
import requests
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from .models_extended import IPFSFile
from campaigns.models import Campaign

logger = logging.getLogger(__name__)


class IPFSService:
    """
    Service for IPFS file storage and retrieval
    """
    
    def __init__(self):
        self.gateway_urls = getattr(settings, 'IPFS_GATEWAY_URLS', [
            'https://ipfs.io/ipfs/',
            'https://gateway.pinata.cloud/ipfs/',
            'https://cloudflare-ipfs.com/ipfs/',
        ])
        self.pinata_api_key = getattr(settings, 'PINATA_API_KEY', None)
        self.pinata_secret_key = getattr(settings, 'PINATA_SECRET_KEY', None)
        self.pinata_gateway = 'https://gateway.pinata.cloud/ipfs/'
    
    def upload_file(
        self, 
        file: UploadedFile, 
        uploaded_by_id: int,
        campaign_id: Optional[int] = None,
        nft_id: Optional[int] = None,
        file_type: str = 'other'
    ) -> IPFSFile:
        """Upload file to IPFS"""
        try:
            # Upload to Pinata if API keys are available
            if self.pinata_api_key and self.pinata_secret_key:
                ipfs_hash, ipfs_url = self._upload_to_pinata(file)
            else:
                # Fallback to local IPFS node or other service
                ipfs_hash, ipfs_url = self._upload_to_local_ipfs(file)
            
            # Create IPFS file record
            ipfs_file = IPFSFile.objects.create(
                ipfs_hash=ipfs_hash,
                file_name=file.name,
                file_type=file_type,
                file_size=file.size,
                mime_type=file.content_type,
                ipfs_url=ipfs_url,
                gateway_urls=self.gateway_urls,
                uploaded_by_id=uploaded_by_id,
                campaign_id=campaign_id,
                nft_id=nft_id,
                is_pinned=True
            )
            
            logger.info(f"File uploaded to IPFS: {ipfs_hash}")
            return ipfs_file
            
        except Exception as e:
            logger.error(f"Error uploading file to IPFS: {e}")
            raise
    
    def upload_json_metadata(
        self, 
        metadata: Dict, 
        uploaded_by_id: int,
        campaign_id: Optional[int] = None,
        nft_id: Optional[int] = None
    ) -> IPFSFile:
        """Upload JSON metadata to IPFS"""
        try:
            # Convert metadata to JSON string
            json_string = json.dumps(metadata, indent=2, ensure_ascii=False)
            
            # Create a file-like object
            from io import BytesIO
            file_obj = BytesIO(json_string.encode('utf-8'))
            file_obj.name = f"metadata_{nft_id or campaign_id or 'unknown'}.json"
            
            # Upload to IPFS
            return self.upload_file(
                file_obj, 
                uploaded_by_id,
                campaign_id=campaign_id,
                nft_id=nft_id,
                file_type='metadata'
            )
            
        except Exception as e:
            logger.error(f"Error uploading metadata to IPFS: {e}")
            raise
    
    def _upload_to_pinata(self, file: UploadedFile) -> Tuple[str, str]:
        """Upload file to Pinata IPFS service"""
        try:
            url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
            
            headers = {
                'pinata_api_key': self.pinata_api_key,
                'pinata_secret_api_key': self.pinata_secret_key,
            }
            
            files = {
                'file': (file.name, file, file.content_type)
            }
            
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            
            data = response.json()
            ipfs_hash = data['IpfsHash']
            ipfs_url = f"{self.pinata_gateway}{ipfs_hash}"
            
            return ipfs_hash, ipfs_url
            
        except Exception as e:
            logger.error(f"Error uploading to Pinata: {e}")
            raise
    
    def _upload_to_local_ipfs(self, file: UploadedFile) -> Tuple[str, str]:
        """Upload file to local IPFS node (fallback)"""
        try:
            # This would require a local IPFS node running
            # For now, we'll simulate the upload
            import hashlib
            import time
            
            # Generate a mock IPFS hash
            content = file.read()
            file.seek(0)  # Reset file pointer
            
            # Create a mock hash (in real implementation, use IPFS client)
            hash_input = f"{file.name}{file.size}{time.time()}".encode()
            mock_hash = hashlib.sha256(hash_input).hexdigest()[:46]  # IPFS hash length
            
            ipfs_url = f"{self.gateway_urls[0]}{mock_hash}"
            
            logger.warning(f"Using mock IPFS hash: {mock_hash}")
            return mock_hash, ipfs_url
            
        except Exception as e:
            logger.error(f"Error uploading to local IPFS: {e}")
            raise
    
    def get_file_content(self, ipfs_hash: str) -> Optional[bytes]:
        """Get file content from IPFS"""
        try:
            for gateway_url in self.gateway_urls:
                try:
                    url = f"{gateway_url}{ipfs_hash}"
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    return response.content
                except requests.RequestException:
                    continue
            
            logger.error(f"Could not retrieve file {ipfs_hash} from any gateway")
            return None
            
        except Exception as e:
            logger.error(f"Error getting file content {ipfs_hash}: {e}")
            return None
    
    def get_json_metadata(self, ipfs_hash: str) -> Optional[Dict]:
        """Get JSON metadata from IPFS"""
        try:
            content = self.get_file_content(ipfs_hash)
            if content:
                return json.loads(content.decode('utf-8'))
            return None
        except Exception as e:
            logger.error(f"Error getting JSON metadata {ipfs_hash}: {e}")
            return None
    
    def pin_file(self, ipfs_hash: str) -> bool:
        """Pin file to IPFS (if using Pinata)"""
        try:
            if not self.pinata_api_key or not self.pinata_secret_key:
                logger.warning("Pinata API keys not configured, skipping pin operation")
                return False
            
            url = "https://api.pinata.cloud/pinning/pinByHash"
            
            headers = {
                'Content-Type': 'application/json',
                'pinata_api_key': self.pinata_api_key,
                'pinata_secret_api_key': self.pinata_secret_key,
            }
            
            data = {
                'hashToPin': ipfs_hash,
                'pinataMetadata': {
                    'name': f'pinned_file_{ipfs_hash}'
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            logger.info(f"File {ipfs_hash} pinned successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error pinning file {ipfs_hash}: {e}")
            return False
    
    def unpin_file(self, ipfs_hash: str) -> bool:
        """Unpin file from IPFS (if using Pinata)"""
        try:
            if not self.pinata_api_key or not self.pinata_secret_key:
                logger.warning("Pinata API keys not configured, skipping unpin operation")
                return False
            
            url = f"https://api.pinata.cloud/pinning/unpin/{ipfs_hash}"
            
            headers = {
                'pinata_api_key': self.pinata_api_key,
                'pinata_secret_api_key': self.pinata_secret_key,
            }
            
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
            logger.info(f"File {ipfs_hash} unpinned successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error unpinning file {ipfs_hash}: {e}")
            return False
    
    def create_nft_metadata(
        self,
        name: str,
        description: str,
        image_url: str,
        attributes: List[Dict],
        campaign_id: int,
        contribution_amount: float,
        creator: str
    ) -> Dict:
        """Create NFT metadata following OpenSea standards"""
        try:
            metadata = {
                "name": name,
                "description": description,
                "image": image_url,
                "external_url": f"https://cinechainlanka.com/campaigns/{campaign_id}",
                "attributes": [
                    {
                        "trait_type": "Campaign ID",
                        "value": campaign_id
                    },
                    {
                        "trait_type": "Contribution Amount",
                        "value": contribution_amount
                    },
                    {
                        "trait_type": "Creator",
                        "value": creator
                    },
                    {
                        "trait_type": "Platform",
                        "value": "CineChainLanka"
                    }
                ] + attributes,
                "background_color": "000000",
                "animation_url": None,
                "youtube_url": None
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error creating NFT metadata: {e}")
            raise
    
    def get_available_gateways(self) -> List[str]:
        """Get list of available IPFS gateways"""
        return self.gateway_urls
    
    def test_gateway(self, gateway_url: str) -> bool:
        """Test if a gateway is accessible"""
        try:
            # Test with a known IPFS hash (QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG - "Hello World")
            test_hash = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
            url = f"{gateway_url}{test_hash}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_working_gateways(self) -> List[str]:
        """Get list of working IPFS gateways"""
        working_gateways = []
        for gateway in self.gateway_urls:
            if self.test_gateway(gateway):
                working_gateways.append(gateway)
        return working_gateways


class NFTMetadataService:
    """
    Service for NFT metadata management
    """
    
    def __init__(self):
        self.ipfs_service = IPFSService()
    
    def create_campaign_nft_metadata(
        self,
        campaign,
        contribution_amount: float,
        backer_name: str,
        nft_name: str = None
    ) -> Dict:
        """Create metadata for campaign contribution NFT"""
        try:
            if not nft_name:
                nft_name = f"{campaign.title} - Contribution NFT"
            
            # Create attributes
            attributes = [
                {
                    "trait_type": "Campaign Title",
                    "value": campaign.title
                },
                {
                    "trait_type": "Category",
                    "value": campaign.category.name
                },
                {
                    "trait_type": "Funding Goal",
                    "value": float(campaign.funding_goal)
                },
                {
                    "trait_type": "Contribution Amount",
                    "value": contribution_amount
                },
                {
                    "trait_type": "Backer",
                    "value": backer_name
                },
                {
                    "trait_type": "Rarity",
                    "value": self._calculate_rarity(contribution_amount, campaign.funding_goal)
                }
            ]
            
            # Use campaign cover image if available
            image_url = campaign.cover_image.url if campaign.cover_image else ""
            
            metadata = self.ipfs_service.create_nft_metadata(
                name=nft_name,
                description=f"Contribution NFT for {campaign.title} campaign",
                image_url=image_url,
                attributes=attributes,
                campaign_id=campaign.id,
                contribution_amount=contribution_amount,
                creator=campaign.creator.username
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error creating campaign NFT metadata: {e}")
            raise
    
    def _calculate_rarity(self, contribution_amount: float, funding_goal: float) -> str:
        """Calculate NFT rarity based on contribution amount"""
        try:
            percentage = (contribution_amount / float(funding_goal)) * 100
            
            if percentage >= 10:
                return "Legendary"
            elif percentage >= 5:
                return "Epic"
            elif percentage >= 2:
                return "Rare"
            elif percentage >= 1:
                return "Uncommon"
            else:
                return "Common"
        except Exception:
            return "Common"
    
    def upload_nft_metadata(
        self,
        metadata: Dict,
        uploaded_by_id: int,
        nft_id: int
    ) -> IPFSFile:
        """Upload NFT metadata to IPFS"""
        try:
            return self.ipfs_service.upload_json_metadata(
                metadata=metadata,
                uploaded_by_id=uploaded_by_id,
                nft_id=nft_id,
                file_type='metadata'
            )
        except Exception as e:
            logger.error(f"Error uploading NFT metadata: {e}")
            raise
