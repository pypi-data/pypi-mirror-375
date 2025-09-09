#!/usr/bin/env python3
"""
Runtime Installer - Silent installation of GGUF runtime
Optimized for CPU-only inference with minimal resource usage
"""

import os
import subprocess
import sys
import platform
import logging
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from functools import wraps

# Custom Exceptions
class RuntimeInstallError(Exception):
    """Base exception for runtime installation errors"""
    pass

class DependencyInstallError(RuntimeInstallError):
    """Exception for dependency installation errors"""
    pass

class VerificationError(RuntimeInstallError):
    """Exception for installation verification errors"""
    pass

# Configuration
@dataclass
class InstallConfig:
    timeout: int = 300
    max_retries: int = 3
    pip_timeout: int = 60
    user_agent: str = "RuntimeInstaller/1.0"

def retry_on_failure(max_retries: int = 3, delay: float = 2.0):
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

class RuntimeInstaller:
    def __init__(self, install_dir: str = "./runtime", config: Optional[InstallConfig] = None):
        self.install_dir = Path(install_dir)
        self.install_dir.mkdir(exist_ok=True)
        self.config = config or InstallConfig()
        self.logger = self._setup_logger()
        self.system = platform.system().lower()
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('RuntimeInstaller')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _validate_environment(self) -> bool:
        """Validate the current environment"""
        try:
            # Check Python version
            if sys.version_info < (3, 8):
                self.logger.error("Python 3.8 or higher is required")
                return False
            
            # Check pip availability
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True, timeout=self.config.pip_timeout)
            if result.returncode != 0:
                self.logger.error("pip is not available")
                return False
            
            self.logger.info(f"Environment validation successful - Python {sys.version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            return False
    
    def _run_pip_command(self, cmd: List[str], timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """Run pip command with proper error handling"""
        timeout = timeout or self.config.pip_timeout
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                check=False
            )
            return result
        except subprocess.TimeoutExpired as e:
            self.logger.error(f"Command timed out after {timeout}s: {' '.join(cmd)}")
            raise RuntimeInstallError(f"Command timeout: {e}") from e
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            raise RuntimeInstallError(f"Command execution error: {e}") from e
    
    @retry_on_failure(max_retries=3, delay=2.0)
    def install_llama_cpp(self) -> bool:
        """Install llama-cpp-python with CPU-only support"""
        try:
            self.logger.info("Installing llama-cpp-python (CPU-only)...")
            
            # Uninstall existing version if any
            uninstall_cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "llama-cpp-python"]
            self._run_pip_command(uninstall_cmd)
            
            # Install with CPU-only flags
            install_cmd = [
                sys.executable, "-m", "pip", "install", 
                "llama-cpp-python", 
                "--no-cache-dir",
                "--disable-pip-version-check",
                "--quiet"
            ]
            
            # Add CPU-only compilation flags
            env = os.environ.copy()
            env["CMAKE_ARGS"] = "-DLLAMA_CUBLAS=OFF -DLLAMA_CUDA=OFF -DLLAMA_METAL=OFF"
            env["FORCE_CMAKE"] = "1"
            
            result = subprocess.run(install_cmd, env=env, capture_output=True, text=True, 
                                  timeout=self.config.timeout)
            
            if result.returncode == 0:
                self.logger.info("llama-cpp-python installed successfully")
                return True
            else:
                error_msg = f"Installation failed: {result.stderr}"
                self.logger.error(error_msg)
                raise DependencyInstallError(error_msg)
                
        except Exception as e:
            self.logger.error(f"Failed to install llama-cpp-python: {e}")
            raise DependencyInstallError(f"llama-cpp-python installation failed: {e}") from e
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def install_dependencies(self) -> bool:
        """Install required dependencies"""
        dependencies = [
            "requests",
            "psutil", 
            "fastapi",
            "uvicorn[standard]",
            "pydantic"
        ]
        
        try:
            self.logger.info("Installing dependencies...")
            
            for dep in dependencies:
                self.logger.info(f"Installing {dep}...")
                cmd = [sys.executable, "-m", "pip", "install", dep, "--no-cache-dir", "--quiet"]
                result = self._run_pip_command(cmd)
                
                if result.returncode != 0:
                    error_msg = f"Failed to install {dep}: {result.stderr}"
                    self.logger.error(error_msg)
                    raise DependencyInstallError(error_msg)
                    
            self.logger.info("All dependencies installed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install dependencies: {e}")
            raise DependencyInstallError(f"Dependencies installation failed: {e}") from e
    
    def verify_installation(self) -> bool:
        """Verify that all components are properly installed"""
        try:
            self.logger.info("Verifying installation...")
            
            # Test llama-cpp-python import
            try:
                import llama_cpp
                self.logger.info("llama-cpp-python import successful")
            except ImportError as e:
                raise VerificationError(f"llama-cpp-python import failed: {e}")
            
            # Test other dependencies
            required_modules = ["requests", "psutil", "fastapi", "uvicorn"]
            for module in required_modules:
                try:
                    __import__(module)
                    self.logger.info(f"{module} import successful")
                except ImportError as e:
                    raise VerificationError(f"{module} import failed: {e}")
            
            self.logger.info("All dependencies verified successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Import verification failed: {e}")
            raise VerificationError(f"Installation verification failed: {e}") from e
    
    def get_installation_info(self) -> Dict[str, Any]:
        """Get information about the current installation"""
        info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "install_dir": str(self.install_dir),
            "dependencies": {}
        }
        
        # Check installed packages
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                info["pip_packages"] = result.stdout
        except Exception:
            info["pip_packages"] = "Unable to retrieve"
        
        return info
    
    def install_all(self) -> bool:
        """Install all required components"""
        try:
            self.logger.info("Starting silent installation...")
            
            # Validate environment first
            if not self._validate_environment():
                raise RuntimeInstallError("Environment validation failed")
            
            # Check if already installed
            try:
                if self.verify_installation():
                    self.logger.info("All dependencies already installed and verified")
                    return True
            except VerificationError:
                self.logger.info("Installation verification failed, proceeding with installation...")
            
            # Install dependencies
            if not self.install_dependencies():
                raise RuntimeInstallError("Dependencies installation failed")
                
            # Install llama-cpp-python
            if not self.install_llama_cpp():
                raise RuntimeInstallError("llama-cpp-python installation failed")
                
            # Final verification
            if not self.verify_installation():
                raise RuntimeInstallError("Final installation verification failed")
                
            self.logger.info("Installation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            raise RuntimeInstallError(f"Installation process failed: {e}") from e

if __name__ == "__main__":
    installer = RuntimeInstaller()
    try:
        success = installer.install_all()
        sys.exit(0 if success else 1)
    except RuntimeInstallError as e:
        print(f"Installation failed: {e}")
        sys.exit(1)