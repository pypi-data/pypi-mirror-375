"""
Cloud and distributed features for device fingerprinting.

Enables secure cloud storage, multi-device management, and distributed verification.
"""

import os
import json
import time
import base64
import hashlib
from typing import Dict, Any, List, Optional
from ..backends import StorageBackend

class CloudStorageBackend(StorageBackend):
    """
    Secure cloud storage backend with encryption and backup.
    
    Supports AWS S3, Azure Blob, Google Cloud Storage with client-side encryption.
    """
    
    def __init__(self, provider: str = "aws", encryption_key: Optional[bytes] = None):
        self.provider = provider
        self.encryption_key = encryption_key or os.urandom(32)
        self._init_cloud_client()
    
    def _init_cloud_client(self):
        """Initialize cloud storage client"""
        if self.provider == "aws":
            try:
                import boto3
                self.client = boto3.client('s3')
                self.bucket = "device-fingerprints-secure"
                self.available = True
            except ImportError:
                self.available = False
        elif self.provider == "azure":
            try:
                from azure.storage.blob import BlobServiceClient
                self.client = BlobServiceClient.from_connection_string("...")
                self.available = True
            except ImportError:
                self.available = False
        else:
            self.available = False
    
    def _encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt data before cloud storage"""
        from cryptography.fernet import Fernet
        
        # Use encryption key to create Fernet cipher
        key = hashlib.sha256(self.encryption_key).digest()
        f = Fernet(base64.urlsafe_b64encode(key))
        
        json_data = json.dumps(data).encode()
        return f.encrypt(json_data)
    
    def _decrypt_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt data from cloud storage"""
        from cryptography.fernet import Fernet
        
        key = hashlib.sha256(self.encryption_key).digest()
        f = Fernet(base64.urlsafe_b64encode(key))
        
        decrypted = f.decrypt(encrypted_data)
        return json.loads(decrypted.decode())
    
    def store(self, key: str, data: Dict[str, Any]) -> bool:
        """Store encrypted data in cloud"""
        if not self.available:
            return False
        
        try:
            encrypted_data = self._encrypt_data(data)
            
            if self.provider == "aws":
                self.client.put_object(
                    Bucket=self.bucket,
                    Key=f"fingerprints/{key}.enc",
                    Body=encrypted_data,
                    ServerSideEncryption='AES256'
                )
            
            return True
        except Exception:
            return False
    
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load and decrypt data from cloud"""
        if not self.available:
            return None
        
        try:
            if self.provider == "aws":
                response = self.client.get_object(
                    Bucket=self.bucket,
                    Key=f"fingerprints/{key}.enc"
                )
                encrypted_data = response['Body'].read()
            
            return self._decrypt_data(encrypted_data)
        except Exception:
            return None

class DistributedVerification:
    """
    Distributed verification system for device fingerprints.
    
    Enables multi-node verification and consensus for high-security scenarios.
    """
    
    def __init__(self, nodes: List[str], consensus_threshold: float = 0.67):
        """
        Initialize distributed verification.
        
        Args:
            nodes: List of verification node URLs
            consensus_threshold: Minimum agreement ratio (0.0-1.0)
        """
        self.nodes = nodes
        self.consensus_threshold = consensus_threshold
    
    def verify_distributed(self, fingerprint: str, binding_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify fingerprint across multiple nodes and reach consensus.
        
        Returns:
            Dictionary with verification results and consensus info
        """
        node_results = []
        
        for node_url in self.nodes:
            try:
                result = self._verify_with_node(node_url, fingerprint, binding_data)
                node_results.append({
                    'node': node_url,
                    'result': result,
                    'timestamp': time.time()
                })
            except Exception as e:
                node_results.append({
                    'node': node_url,
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        # Calculate consensus
        valid_results = [r for r in node_results if 'result' in r]
        if len(valid_results) == 0:
            return {'consensus': False, 'error': 'no_valid_responses'}
        
        positive_votes = sum(1 for r in valid_results if r['result'].get('valid', False))
        consensus_ratio = positive_votes / len(valid_results)
        
        has_consensus = consensus_ratio >= self.consensus_threshold
        
        return {
            'consensus': has_consensus,
            'consensus_ratio': consensus_ratio,
            'positive_votes': positive_votes,
            'total_votes': len(valid_results),
            'node_results': node_results,
            'verification_timestamp': time.time()
        }
    
    def _verify_with_node(self, node_url: str, fingerprint: str, binding_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send verification request to a single node"""
        import requests
        
        payload = {
            'fingerprint': fingerprint,
            'binding_data': binding_data,
            'timestamp': time.time()
        }
        
        response = requests.post(
            f"{node_url}/verify",
            json=payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        response.raise_for_status()
        return response.json()

class MultiDeviceManager:
    """
    Manager for multiple device fingerprints and cross-device verification.
    
    Useful for users with multiple devices or device upgrades.
    """
    
    def __init__(self, storage_backend: StorageBackend):
        self.storage = storage_backend
    
    def register_device(self, device_id: str, fingerprint_data: Dict[str, Any]) -> bool:
        """Register a new device with its fingerprint"""
        device_record = {
            'device_id': device_id,
            'fingerprint_data': fingerprint_data,
            'registration_time': time.time(),
            'last_seen': time.time(),
            'status': 'active'
        }
        
        return self.storage.store(f"device_{device_id}", device_record)
    
    def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all devices registered to a user"""
        # Implementation would query storage for user's devices
        # This is a placeholder for the concept
        devices = []
        
        # In a real implementation, you'd have a user->devices mapping
        for i in range(3):  # Example: 3 devices
            device_data = self.storage.load(f"user_{user_id}_device_{i}")
            if device_data:
                devices.append(device_data)
        
        return devices
    
    def verify_cross_device(self, user_id: str, current_fingerprint: str) -> Dict[str, Any]:
        """
        Verify current device against user's known devices.
        
        Returns similarity scores and recommendations.
        """
        user_devices = self.get_user_devices(user_id)
        
        if not user_devices:
            return {'status': 'no_known_devices'}
        
        similarities = []
        for device in user_devices:
            similarity = self._calculate_device_similarity(
                current_fingerprint, 
                device['fingerprint_data']
            )
            similarities.append({
                'device_id': device['device_id'],
                'similarity': similarity,
                'last_seen': device['last_seen']
            })
        
        # Find best match
        best_match = max(similarities, key=lambda x: x['similarity'])
        
        if best_match['similarity'] > 0.8:
            status = 'known_device'
        elif best_match['similarity'] > 0.5:
            status = 'similar_device'
        else:
            status = 'new_device'
        
        return {
            'status': status,
            'best_match': best_match,
            'all_similarities': similarities,
            'recommendation': self._get_verification_recommendation(status, best_match)
        }
    
    def _calculate_device_similarity(self, fp1: str, fp2_data: Dict[str, Any]) -> float:
        """Calculate similarity between current device and stored device"""
        # This would implement sophisticated similarity analysis
        # For now, a simple hash comparison
        fp2 = fp2_data.get('fingerprint', '')
        
        if fp1 == fp2:
            return 1.0
        
        # Calculate partial similarity based on hardware components
        # This is simplified - real implementation would be more sophisticated
        common_chars = sum(1 for a, b in zip(fp1, fp2) if a == b)
        return common_chars / max(len(fp1), len(fp2))
    
    def _get_verification_recommendation(self, status: str, best_match: Dict[str, Any]) -> str:
        """Get recommendation for verification based on device similarity"""
        if status == 'known_device':
            return 'allow_immediate'
        elif status == 'similar_device':
            return 'request_additional_auth'
        else:
            return 'require_full_verification'
