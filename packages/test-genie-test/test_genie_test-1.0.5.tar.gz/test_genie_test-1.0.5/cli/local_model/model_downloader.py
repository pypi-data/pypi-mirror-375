#!/usr/bin/env python3
"""
Model Downloader - Downloads GGUF models from storage
Optimized for CPU-only inference with minimal resource usage
"""

import os
import re
import time
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from functools import wraps
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

# Custom Exceptions
class ModelDownloadError(Exception):
    """Base exception for model download errors"""
    pass

class GoogleDriveDownloadError(ModelDownloadError):
    """Exception for Google Drive specific errors"""
    pass

class InvalidURLError(ModelDownloadError):
    """Exception for invalid URLs"""
    pass

# Configuration
@dataclass
class DownloadConfig:
    chunk_size: int = 8192
    timeout: int = 300
    max_retries: int = 3
    progress_interval: int = 1024 * 1024  # Log every MB
    user_agent: str = "ModelDownloader/1.0"

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class ModelDownloader:
    def __init__(self, models_dir: str = "/models", config: Optional[DownloadConfig] = None):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.config = config or DownloadConfig()
        self.logger = self._setup_logger()
        self.session = self._create_session()
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('ModelDownloader')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'User-Agent': self.config.user_agent
        })
        
        return session
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _extract_filename_from_url(self, url: str) -> str:
        """Extract filename from URL with better handling"""
        parsed = urlparse(url)
        filename = Path(parsed.path).name
        
        if not filename or filename == '/':
            return "model.gguf"
        
        # Remove query parameters from filename
        if '?' in filename:
            filename = filename.split('?')[0]
        
        return filename
    
    def _verify_file_integrity(self, file_path: Path, expected_size: Optional[int] = None) -> bool:
        """Verify file integrity"""
        if not file_path.exists():
            return False
        
        actual_size = file_path.stat().st_size
        
        if expected_size and actual_size != expected_size:
            self.logger.error(f"File size mismatch: expected {expected_size}, got {actual_size}")
            return False
        
        if actual_size == 0:
            self.logger.error("Downloaded file is empty")
            return False
        
        return True
    
    def download_model(self, model_url: str, filename: Optional[str] = None) -> str:
        """Download GGUF model with progress tracking and resume capability"""
        # Validate URL
        if not self._validate_url(model_url):
            raise InvalidURLError(f"Invalid URL format: {model_url}")
        
        # Determine filename
        if not filename:
            if "drive.google.com" in model_url:
                filename = "model.gguf"  # Default filename for Google Drive
            else:
                filename = self._extract_filename_from_url(model_url)
            
        model_path = self.models_dir / filename
        
        # Check if already exists and verify integrity
        if model_path.exists():
            if self._verify_file_integrity(model_path):
                self.logger.info(f"Model {filename} already exists and is valid")
                return str(model_path)
            else:
                self.logger.warning(f"Model {filename} exists but is corrupted, re-downloading...")
                model_path.unlink()
            
        self.logger.info(f"Downloading {filename} from {model_url}")
        
        try:
            # Handle Google Drive URLs
            if "drive.google.com" in model_url:
                model_url = self._convert_google_drive_url(model_url)
                # Use special Google Drive handler
                if self._handle_google_drive_download(model_url, model_path):
                    return str(model_path)
                else:
                    raise GoogleDriveDownloadError("Google Drive download failed")
            else:
                # Regular download for non-Google Drive URLs
                self._download_regular_file(model_url, model_path)
                return str(model_path)
            
        except Exception as e:
            self.logger.error(f"Failed to download {filename}: {e}")
            if model_path.exists():
                model_path.unlink()  # Clean up partial download
            raise ModelDownloadError(f"Download failed: {e}") from e
    
    def _download_regular_file(self, url: str, model_path: Path) -> None:
        """Download regular file (non-Google Drive)"""
        headers = {}
        if model_path.exists():
            headers['Range'] = f'bytes={model_path.stat().st_size}-'
            
        response = self.session.get(url, headers=headers, stream=True, timeout=self.config.timeout)
        response.raise_for_status()
        
        mode = 'ab' if headers else 'wb'
        total_size = int(response.headers.get('content-length', 0))
        
        with open(model_path, mode) as f:
            downloaded = model_path.stat().st_size if headers else 0
            start_time = time.time()
            last_log_time = 0
            
            for chunk in response.iter_content(chunk_size=self.config.chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Log progress every MB or every 5 seconds
                    current_time = time.time()
                    if (downloaded % self.config.progress_interval == 0 or 
                        current_time - last_log_time >= 5):
                        
                        progress = (downloaded / total_size * 100) if total_size > 0 else 0
                        speed = downloaded / (current_time - start_time) / 1024 / 1024  # MB/s
                        
                        self.logger.info(
                            f"Downloaded {downloaded:,}/{total_size:,} bytes "
                            f"({progress:.1f}%) - {speed:.1f} MB/s"
                        )
                        last_log_time = current_time
                        
        self.logger.info(f"Successfully downloaded {model_path.name}")
    
    def verify_model(self, model_path: str, expected_hash: Optional[str] = None) -> bool:
        """Verify model integrity"""
        if not expected_hash:
            return True
            
        self.logger.info("Verifying model integrity...")
        sha256_hash = hashlib.sha256()
        
        with open(model_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
                
        actual_hash = sha256_hash.hexdigest()
        is_valid = actual_hash == expected_hash
        
        if is_valid:
            self.logger.info("Model verification successful")
        else:
            self.logger.error(f"Model verification failed. Expected: {expected_hash}, Got: {actual_hash}")
            
        return is_valid
    
    def _convert_google_drive_url(self, url: str) -> str:
        """Convert Google Drive sharing URL to direct download URL"""
        try:
            # Extract file ID from Google Drive URL
            if "/file/d/" in url:
                file_id = url.split("/file/d/")[1].split("/")[0]
            else:
                raise ValueError("Invalid Google Drive URL format")
            
            # Convert to direct download URL
            direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            self.logger.info(f"Converted Google Drive URL to direct download URL")
            return direct_url
            
        except Exception as e:
            self.logger.error(f"Failed to convert Google Drive URL: {e}")
            raise InvalidURLError(f"Invalid Google Drive URL: {e}") from e
    
    @retry_on_failure(max_retries=3, delay=2.0)
    def _handle_google_drive_download(self, url: str, model_path: Path) -> bool:
        """Handle Google Drive download with confirmation page"""
        try:
            # First request to get the confirmation page
            response = self.session.get(url, stream=True, timeout=self.config.timeout)
            response.raise_for_status()
            
            # Check if we got the confirmation page
            if "Virus scan warning" in response.text or "download anyway" in response.text.lower():
                self.logger.info("Google Drive confirmation page detected, handling...")
                
                # Extract form parameters from the confirmation page
                # Extract the form action URL
                action_match = re.search(r'action="([^"]*)"', response.text)
                if not action_match:
                    self.logger.error("Could not find form action in response")
                    return False
                
                action_url = action_match.group(1)
                self.logger.info(f"Found form action URL: {action_url}")
                
                # Extract form parameters
                id_match = re.search(r'name="id"\s+value="([^"]*)"', response.text)
                export_match = re.search(r'name="export"\s+value="([^"]*)"', response.text)
                confirm_match = re.search(r'name="confirm"\s+value="([^"]*)"', response.text)
                uuid_match = re.search(r'name="uuid"\s+value="([^"]*)"', response.text)
                
                if not all([id_match, export_match, confirm_match, uuid_match]):
                    self.logger.error("Could not extract all form parameters")
                    return False
                
                # Prepare the confirmation request
                confirm_data = {
                    'id': id_match.group(1),
                    'export': export_match.group(1),
                    'confirm': confirm_match.group(1),
                    'uuid': uuid_match.group(1)
                }
                
                self.logger.info("Making confirmation request...")
                
                # Make the confirmation request (GET request with parameters)
                confirm_response = self.session.get(action_url, params=confirm_data, stream=True, timeout=self.config.timeout)
                confirm_response.raise_for_status()
                
                # Now download the actual file
                return self._download_file_stream(confirm_response, model_path)
            else:
                # Direct download without confirmation
                return self._download_file_stream(response, model_path)
                
        except Exception as e:
            self.logger.error(f"Failed to handle Google Drive download: {e}")
            raise GoogleDriveDownloadError(f"Google Drive download failed: {e}") from e
    
    def _download_file_stream(self, response: requests.Response, model_path: Path) -> bool:
        """Download file from response stream with better progress reporting"""
        try:
            total_size = int(response.headers.get('content-length', 0))
            start_time = time.time()
            last_log_time = 0
            
            with open(model_path, 'wb') as f:
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=self.config.chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Log progress every MB or every 5 seconds
                        current_time = time.time()
                        if (downloaded % self.config.progress_interval == 0 or 
                            current_time - last_log_time >= 5):
                            
                            progress = (downloaded / total_size * 100) if total_size > 0 else 0
                            speed = downloaded / (current_time - start_time) / 1024 / 1024  # MB/s
                            
                            self.logger.info(
                                f"Downloaded {downloaded:,}/{total_size:,} bytes "
                                f"({progress:.1f}%) - {speed:.1f} MB/s"
                            )
                            last_log_time = current_time
            
            self.logger.info(f"Successfully downloaded {model_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download file stream: {e}")
            return False

if __name__ == "__main__":
    downloader = ModelDownloader()
    # Example usage
    # model_path = downloader.download_model("<LINK_TO_FILES>/model.gguf")
    # downloader.verify_model(model_path)