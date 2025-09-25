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
    
    def _generate_filename(self, url: str, content_type: str) -> str:
        """Generate appropriate filename from URL or content type"""
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # If no filename from URL, generate one
        if not filename or '.' not in filename:
            # Get extension from content-type
            extension = mimetypes.guess_extension(content_type.split(';')[0])
            if not extension:
                extension = '.jpg'  # Default fallback
            
            # Create filename from domain and timestamp
            domain = parsed_url.netloc.replace('www.', '')
            timestamp = int(time.time())
            filename = f"{domain}_{timestamp}{extension}"
        
        # Sanitize filename for filesystem compatibility
        filename = "".join(c for c in filename if c.isalnum() or c in '.-_')
        return filename
    
    def _check_duplicate(self, content: bytes) -> bool:
        """Check if image is duplicate based on content hash"""
        content_hash = hashlib.md5(content).hexdigest()
        if content_hash in self.downloaded_hashes:
            return True
        self.downloaded_hashes.add(content_hash)
        return False
    
    def fetch_image(self, url: str) -> bool:
        """
        Fetch single image with Ubuntu principles: respect, community, sharing
        """
        try:
            print(f"Connecting to: {url}")
            
            # Respectful request with timeout
            response = self.session.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Validate the response
            is_valid, message = self._validate_image_response(response, url)
            if not is_valid:
                print(f"✗ Validation failed: {message}")
                return False
            
            # Get the full content
            content = response.content
            
            # Check for duplicates
            if self._check_duplicate(content):
                print(f"✗ Duplicate image detected - skipping to respect storage")
                return False
            
            # Create directory with community spirit
            os.makedirs(self.base_dir, exist_ok=True)
            
            # Generate filename
            content_type = response.headers.get('content-type', 'image/jpeg')
            filename = self._generate_filename(url, content_type)
            filepath = self.base_dir / filename
            
            # Ensure unique filename
            counter = 1
            original_filepath = filepath
            while filepath.exists():
                name, ext = original_filepath.stem, original_filepath.suffix
                filepath = self.base_dir / f"{name}_{counter}{ext}"
                counter += 1
            
            # Save with Ubuntu sharing spirit
            with open(filepath, 'wb') as f:
                f.write(content)
            
            print(f"✓ Successfully fetched: {filename}")
            print(f"✓ Image saved to {filepath}")
            return True
            
        except requests.exceptions.Timeout:
            print(f"✗ Connection timeout - respecting server limits")
            return False
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection error - network community unavailable")
            return False
        except requests.exceptions.HTTPError as e:
            print(f"✗ HTTP error {e.response.status_code}: Server respectfully declined")
            return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Request error: {e}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False