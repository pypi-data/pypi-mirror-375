#!/usr/bin/env python3
"""
Server Manager - Manages background GGUF inference server
Optimized for CPU-only inference with minimal resource usage
"""

import os
import time
import signal
import subprocess
import threading
import logging
import psutil
import gc
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from functools import wraps
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from llama_cpp import Llama

# Custom Exceptions
class ServerError(Exception):
    """Base exception for server errors"""
    pass

class ModelLoadError(ServerError):
    """Exception for model loading errors"""
    pass

class ServerStartError(ServerError):
    """Exception for server startup errors"""
    pass

# Configuration
@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    n_ctx: int = 4096
    n_threads: int = 0  # 0 = auto-detect
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    timeout: int = 30
    health_check_interval: int = 1
    max_retries: int = 30

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

class GGUFServer:
    def __init__(self, model_path: str, config: Optional[ServerConfig] = None):
        self.model_path = model_path
        self.config = config or ServerConfig()
        self.llm: Optional[Llama] = None
        self.app = FastAPI(title="GGUF Inference Server", version="1.0.0")
        self.server_process: Optional[subprocess.Popen] = None
        self.logger = self._setup_logger()
        self._setup_middleware()
        self._setup_routes()
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('GGUFServer')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        @self.app.post("/generate")
        async def generate(prompt: Dict[str, Any]):
            try:
                if not self.llm:
                    raise HTTPException(status_code=503, detail="Model not loaded")
                
                text = prompt.get("text", "")
                max_tokens = prompt.get("max_tokens", self.config.max_tokens)
                temperature = prompt.get("temperature", self.config.temperature)
                top_p = prompt.get("top_p", self.config.top_p)
                
                # Validate parameters
                if not text.strip():
                    raise HTTPException(status_code=400, detail="Empty prompt")
                
                if max_tokens <= 0 or max_tokens > 2048:
                    raise HTTPException(status_code=400, detail="Invalid max_tokens")
                
                # Generate response
                response = self.llm(
                    text,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    echo=False,
                    stop=["</s>", "```", "---", "\n\n\n\n"]
                )
                
                return JSONResponse(content={
                    "text": response["choices"][0]["text"],
                    "usage": response.get("usage", {}),
                    "model": os.path.basename(self.model_path)
                })
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Generation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return JSONResponse(content={
                "status": "healthy" if self.llm else "loading",
                "model_loaded": self.llm is not None,
                "model_path": self.model_path,
                "uptime": time.time() - getattr(self, '_start_time', time.time())
            })
        
        @self.app.get("/info")
        async def info():
            """Server information endpoint"""
            return JSONResponse(content={
                "model_path": self.model_path,
                "config": {
                    "n_ctx": self.config.n_ctx,
                    "n_threads": self.config.n_threads,
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p
                },
                "system": {
                    "cpu_count": os.cpu_count(),
                    "memory": psutil.virtual_memory()._asdict()
                }
            })
    
    def _validate_model_path(self) -> bool:
        """Validate model path exists and is accessible"""
        try:
            model_path = Path(self.model_path)
            if not model_path.exists():
                self.logger.error(f"Model file does not exist: {self.model_path}")
                return False
            
            if not model_path.is_file():
                self.logger.error(f"Model path is not a file: {self.model_path}")
                return False
            
            # Check file size (should be > 0)
            if model_path.stat().st_size == 0:
                self.logger.error(f"Model file is empty: {self.model_path}")
                return False
            
            self.logger.info(f"Model validation successful: {self.model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Model validation failed: {e}")
            return False
    
    @retry_on_failure(max_retries=3, delay=2.0)
    def load_model(self):
        """Load GGUF model with CPU optimization"""
        try:
            if not self._validate_model_path():
                raise ModelLoadError("Model validation failed")
            
            self.logger.info(f"Loading model: {self.model_path}")
            
            # Determine optimal thread count
            n_threads = self.config.n_threads or os.cpu_count()
            
            # CPU-optimized parameters
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=self.config.n_ctx,
                n_threads=n_threads,
                n_gpu_layers=0,  # CPU-only
                verbose=False,
                use_mmap=True,  # Memory mapping for efficiency
                use_mlock=False,  # Don't lock memory
                low_vram=False,  # Not applicable for CPU
                f16_kv=True,  # Use 16-bit for key-value cache
                logits_all=False,  # Only compute logits for last token
                embedding=False,  # Disable embeddings
                offload_kqv=False,  # Keep everything in memory
                last_n_tokens_size=512,  # Larger cache for better context
                batch_size=512,  # Batch size for processing
                n_batch=512,  # Number of tokens to process in parallel
                seed=-1,  # Random seed
                n_parts=1,  # Number of model parts
                rope_freq_base=10000.0,
                rope_freq_scale=1.0,
                mul_mat_q=True,  # Use quantized matrix multiplication
                ftype=None,  # Auto-detect quantization type
                typical_p=1.0,
                repeat_penalty=1.05,  # Lower penalty for better code generation
                repeat_last_n=512,  # Larger context for repetition
                penalize_nl=False,  # Allow newlines in code
                stop=None,  # No stop tokens during model loading
                stream=False
            )
            
            self.logger.info("Model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise ModelLoadError(f"Model loading failed: {e}") from e
    
    def _wait_for_server_ready(self) -> bool:
        """Wait for server to be ready"""
        max_retries = self.config.max_retries
        health_check_interval = self.config.health_check_interval
        
        for i in range(max_retries):
            try:
                response = requests.get(
                    f"http://{self.config.host}:{self.config.port}/health", 
                    timeout=1
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("model_loaded", False):
                        self.logger.info(f"Server started successfully on {self.config.host}:{self.config.port}")
                        return True
            except Exception:
                pass
            
            if i < max_retries - 1:  # Don't sleep on last attempt
                time.sleep(health_check_interval)
        
        self.logger.error("Server failed to start within timeout")
        return False
    
    def start_server(self):
        """Start the FastAPI server in background"""
        try:
            self.logger.info("Starting GGUF inference server...")
            self._start_time = time.time()
            
            # Load model first
            self.load_model()
            
            # Start server in background thread
            def run_server():
                try:
                    uvicorn.run(
                        self.app,
                        host=self.config.host,
                        port=self.config.port,
                        log_level="warning",  # Reduce logging
                        access_log=False,  # Disable access logs
                        loop="asyncio"
                    )
                except Exception as e:
                    self.logger.error(f"Server thread error: {e}")
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # Wait for server to be ready
            return self._wait_for_server_ready()
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise ServerStartError(f"Server startup failed: {e}") from e
    
    def stop_server(self):
        """Stop the server and cleanup resources"""
        try:
            self.logger.info("Stopping server...")
            
            # Clear model from memory
            if self.llm:
                del self.llm
                self.llm = None
            
            # Force garbage collection
            gc.collect()
            
            self.logger.info("Server stopped and resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error stopping server: {e}")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "model_path": self.model_path,
            "host": self.config.host,
            "port": self.config.port,
            "model_loaded": self.llm is not None,
            "uptime": time.time() - getattr(self, '_start_time', time.time())
        }

class ServerManager:
    def __init__(self, model_path: str, config: Optional[ServerConfig] = None):
        self.server: Optional[GGUFServer] = None
        self.model_path = model_path
        self.config = config or ServerConfig()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('ServerManager')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def start(self) -> bool:
        """Start the background server"""
        try:
            self.server = GGUFServer(self.model_path, self.config)
            return self.server.start_server()
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop the background server"""
        if self.server:
            self.server.stop_server()
            self.server = None
    
    def is_running(self) -> bool:
        """Check if server is running"""
        try:
            response = requests.get(
                f"http://{self.config.host}:{self.config.port}/health", 
                timeout=1
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_server_url(self) -> str:
        """Get server URL"""
        return f"http://{self.config.host}:{self.config.port}"
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        if self.server:
            return self.server.get_server_info()
        return {"status": "not_running"}

if __name__ == "__main__":
    # Example usage
    config = ServerConfig(port=8001)
    manager = ServerManager("/models/model.gguf", config)
    if manager.start():
        print("Server started successfully")
        print(f"Server info: {manager.get_server_info()}")
        time.sleep(10)  # Keep running for demo
        manager.stop()
    else:
        print("Failed to start server")