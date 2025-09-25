import requests
import os
import hashlib
from urllib.parse import urlparse
from pathlib import Path
import mimetypes
import time
from typing import List, Optional, Tuple


class UbuntuImageFetcher:
    """
    Ubuntu-inspired image fetcher that embodies community values
    """
    
    def __init__(self, base_dir: str = "Fetched_Images"):
        self.base_dir = Path(base_dir)
        self.downloaded_hashes = set()
        self.session = self._create_session()
        self._load_existing_hashes()
    
    def _create_session(self) -> requests.Session:
        """Create a respectful session with appropriate headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Ubuntu-Image-Fetcher/1.0 (Respectful Web Community Tool)',
            'Accept': 'image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        return session
    
    def _load_existing_hashes(self):
        """Load hashes of existing images to prevent duplicates"""
        if not self.base_dir.exists():
            return
        
        for file_path in self.base_dir.rglob('*'):
            if file_path.is_file() and self._is_image_file(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        content_hash = hashlib.md5(f.read()).hexdigest()
                        self.downloaded_hashes.add(content_hash)
                except Exception:
                    continue  # Skip files we can't read
    
    def _is_image_file(self, filepath: Path) -> bool:
        """Check if file is an image based on extension and mime type"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'}
        return filepath.suffix.lower() in image_extensions
    
    def _validate_image_response(self, response: requests.Response, url: str) -> Tuple[bool, str]:
        """
        Validate response before saving - implements security precautions
        """
        # Check Content-Type header
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            return False, f"Content-Type '{content_type}' is not an image type"
        
        # Check Content-Length (prevent extremely large downloads)
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 50 * 1024 * 1024:  # 50MB limit
            return False, "Image too large (>50MB) - skipping for safety"
        
        # Check if content is actually image data (basic validation)
        content_start = response.content[:10]
        image_signatures = [
            b'\xFF\xD8\xFF',  # JPEG
            b'\x89PNG\r\n\x1a\n',  # PNG
            b'GIF87a', b'GIF89a',  # GIF
            b'BM',  # BMP
            b'RIFF',  # WebP (partial)
        ]
        
        if not any(content_start.startswith(sig) for sig in image_signatures):
            return False, "Content doesn't appear to be a valid image"
        
        return True, "Valid image"