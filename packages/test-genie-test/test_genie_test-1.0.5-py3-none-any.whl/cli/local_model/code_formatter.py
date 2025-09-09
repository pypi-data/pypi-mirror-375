#!/usr/bin/env python3
"""
Code Formatter and Validator - Formats and validates generated code
Optimized for CPU-only processing with minimal resource usage
"""

import re
import ast
import logging
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from functools import wraps

# Custom Exceptions
class CodeProcessingError(Exception):
    """Base exception for code processing errors"""
    pass

class FormattingError(CodeProcessingError):
    """Exception for code formatting errors"""
    pass

class ValidationError(CodeProcessingError):
    """Exception for code validation errors"""
    pass

# Configuration
@dataclass
class FormattingConfig:
    python_line_length: int = 88
    cpp_style: str = "Google"
    timeout: int = 10
    enable_black: bool = True
    enable_clang_format: bool = True
    strict_validation: bool = False

def retry_on_failure(max_retries: int = 2, delay: float = 1.0):
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
                    import time
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class CodeFormatter:
    def __init__(self, config: Optional[FormattingConfig] = None):
        self.config = config or FormattingConfig()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('CodeFormatter')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _validate_input(self, code: str) -> bool:
        """Validate input code"""
        if not isinstance(code, str):
            self.logger.error("Code must be a string")
            return False
        
        if len(code) > 1024 * 1024:  # 1MB limit
            self.logger.error("Code too large")
            return False
        
        return True
    
    def clean_generated_code(self, code: str) -> str:
        """Clean and format generated code"""
        if not self._validate_input(code):
            return ""
        
        if not code:
            return ""
        
        # Remove markdown code blocks
        code = re.sub(r'```(?:python|py|cpp|c\+\+|javascript|js|java|c|go|rust)?\n?', '', code)
        code = re.sub(r'```\n?', '', code)
        
        # Remove common prefixes/suffixes
        code = re.sub(r'^(Here\'s|Here is|Here\'s the|The following|Generated code:?)\s*', '', code, flags=re.IGNORECASE)
        code = re.sub(r'\n*(This code|The code|Note:|Explanation:).*$', '', code, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up whitespace
        code = code.strip()
        
        # Ensure proper line endings
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            # Skip empty lines at the beginning
            if not cleaned_lines and not line:
                continue
            cleaned_lines.append(line)
        
        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    @retry_on_failure(max_retries=2, delay=1.0)
    def format_python_code(self, code: str) -> Tuple[str, bool]:
        """Format Python code using black (if available) or basic formatting"""
        try:
            if not self.config.enable_black:
                return self._basic_python_format(code), False
            
            # Try using black formatter
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run([
                    'black', '--line-length', str(self.config.python_line_length), '--quiet', temp_file
                ], capture_output=True, text=True, timeout=self.config.timeout)
                
                if result.returncode == 0:
                    with open(temp_file, 'r') as f:
                        formatted_code = f.read()
                    os.unlink(temp_file)
                    return formatted_code, True
                else:
                    os.unlink(temp_file)
                    return self._basic_python_format(code), False
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                os.unlink(temp_file)
                return self._basic_python_format(code), False
                
        except Exception as e:
            self.logger.warning(f"Black formatting failed: {e}")
            return self._basic_python_format(code), False
    
    def _basic_python_format(self, code: str) -> str:
        """Basic Python code formatting"""
        try:
            # Parse and unparse to fix basic formatting
            tree = ast.parse(code)
            formatted = ast.unparse(tree)
            return formatted
        except SyntaxError:
            # If parsing fails, return cleaned code
            return self.clean_generated_code(code)
    
    @retry_on_failure(max_retries=2, delay=1.0)
    def format_cpp_code(self, code: str) -> Tuple[str, bool]:
        """Format C++ code using clang-format (if available) or basic formatting"""
        try:
            if not self.config.enable_clang_format:
                return self._basic_cpp_format(code), False
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run([
                    'clang-format', f'-style={self.config.cpp_style}', temp_file
                ], capture_output=True, text=True, timeout=self.config.timeout)
                
                if result.returncode == 0:
                    formatted_code = result.stdout
                    os.unlink(temp_file)
                    return formatted_code, True
                else:
                    os.unlink(temp_file)
                    return self._basic_cpp_format(code), False
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                os.unlink(temp_file)
                return self._basic_cpp_format(code), False
                
        except Exception as e:
            self.logger.warning(f"Clang-format failed: {e}")
            return self._basic_cpp_format(code), False
    
    def _basic_cpp_format(self, code: str) -> str:
        """Basic C++ code formatting"""
        # Clean up common formatting issues
        code = re.sub(r'\n\s*\n\s*\n+', '\n\n', code)  # Multiple blank lines
        code = re.sub(r'{\s*\n', '{\n', code)  # Opening braces
        code = re.sub(r'\n\s*}', '\n}', code)  # Closing braces
        code = re.sub(r';\s*\n', ';\n', code)  # Semicolons
        
        return self.clean_generated_code(code)

class CodeValidator:
    def __init__(self, config: Optional[FormattingConfig] = None):
        self.config = config or FormattingConfig()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('CodeValidator')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _validate_input(self, code: str) -> bool:
        """Validate input code"""
        if not isinstance(code, str):
            self.logger.error("Code must be a string")
            return False
        
        return True
    
    def validate_python_code(self, code: str) -> Dict[str, Any]:
        """Validate Python code syntax and basic structure"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "metrics": {
                "lines": 0,
                "functions": 0,
                "classes": 0,
                "imports": 0
            }
        }
        
        try:
            if not self._validate_input(code):
                result["errors"].append("Invalid input")
                return result
            
            # Parse the code
            tree = ast.parse(code)
            
            # Basic validation
            if not code.strip():
                result["errors"].append("Code is empty")
                return result
            
            # Calculate metrics
            result["metrics"]["lines"] = len(code.split('\n'))
            result["metrics"]["functions"] = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            result["metrics"]["classes"] = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            result["metrics"]["imports"] = len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
            
            # Check for common issues
            self._check_python_issues(tree, result)
            
            result["valid"] = len(result["errors"]) == 0
            
        except SyntaxError as e:
            result["errors"].append(f"Syntax error: {e}")
        except Exception as e:
            result["errors"].append(f"Validation error: {e}")
        
        return result
    
    def _check_python_issues(self, tree: ast.AST, result: Dict[str, Any]):
        """Check for common Python code issues"""
        for node in ast.walk(tree):
            # Check for print statements (suggest logging)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print':
                result["warnings"].append("Consider using logging instead of print statements")
            
            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                result["warnings"].append("Bare except clause - consider specifying exception type")
            
            # Check for unused imports (basic check)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        result["suggestions"].append(f"Consider using 'import {alias.name}' instead of 'import {alias.name} as {alias.asname}'")
            
            # Check for long lines
            if hasattr(node, 'lineno') and hasattr(node, 'col_offset'):
                # This is a simplified check - in practice you'd need the source lines
                pass
    
    def validate_cpp_code(self, code: str) -> Dict[str, Any]:
        """Validate C++ code syntax (basic validation)"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "metrics": {
                "lines": 0,
                "functions": 0,
                "classes": 0,
                "includes": 0
            }
        }
        
        try:
            if not self._validate_input(code):
                result["errors"].append("Invalid input")
                return result
            
            if not code.strip():
                result["errors"].append("Code is empty")
                return result
            
            # Calculate metrics
            result["metrics"]["lines"] = len(code.split('\n'))
            result["metrics"]["functions"] = len(re.findall(r'\b(int|void|float|double|bool|char)\s+\w+\s*\(', code))
            result["metrics"]["classes"] = len(re.findall(r'\bclass\s+\w+', code))
            result["metrics"]["includes"] = len(re.findall(r'#include\s*[<"]', code))
            
            # Basic C++ validation
            self._check_cpp_issues(code, result)
            
            result["valid"] = len(result["errors"]) == 0
            
        except Exception as e:
            result["errors"].append(f"Validation error: {e}")
        
        return result
    
    def _check_cpp_issues(self, code: str, result: Dict[str, Any]):
        """Check for common C++ code issues"""
        # Check for proper includes
        if '#include' not in code and ('std::' in code or 'cout' in code or 'cin' in code):
            result["warnings"].append("Missing standard library includes")
        
        # Check for main function
        if 'int main(' not in code and 'void main(' not in code:
            result["suggestions"].append("Consider adding a main function for executable code")
        
        # Check for proper namespace usage
        if 'using namespace std;' in code:
            result["warnings"].append("Consider avoiding 'using namespace std' in header files")
        
        # Check for memory management
        if 'new ' in code and 'delete ' not in code:
            result["warnings"].append("Memory allocated with 'new' should be freed with 'delete'")
        
        # Check for proper header guards (basic check)
        if '#ifndef' not in code and '#pragma once' not in code and code.count('#include') > 1:
            result["suggestions"].append("Consider adding header guards to prevent multiple inclusion")

class CodeProcessor:
    """Main class that combines formatting and validation"""
    
    def __init__(self, config: Optional[FormattingConfig] = None):
        self.config = config or FormattingConfig()
        self.formatter = CodeFormatter(self.config)
        self.validator = CodeValidator(self.config)
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('CodeProcessor')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language from code content"""
        # Simple language detection based on keywords
        if '#include' in code or 'int main(' in code or 'std::' in code:
            return 'cpp'
        elif 'def ' in code or 'import ' in code or 'print(' in code:
            return 'python'
        else:
            return 'python'  # Default
    
    def process_code(self, code: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Process code: clean, format, and validate"""
        result = {
            "original_code": code,
            "cleaned_code": "",
            "formatted_code": "",
            "validation": {},
            "success": False,
            "language": language or self._detect_language(code),
            "processing_time": 0
        }
        
        import time
        start_time = time.time()
        
        try:
            # Clean the code
            cleaned = self.formatter.clean_generated_code(code)
            result["cleaned_code"] = cleaned
            
            # Format the code
            if result["language"].lower() == "python":
                formatted, format_success = self.formatter.format_python_code(cleaned)
                validation = self.validator.validate_python_code(formatted)
            elif result["language"].lower() in ["cpp", "c++", "c"]:
                formatted, format_success = self.formatter.format_cpp_code(cleaned)
                validation = self.validator.validate_cpp_code(formatted)
            else:
                formatted = cleaned
                format_success = False
                validation = {"valid": True, "errors": [], "warnings": [], "suggestions": [], "metrics": {}}
            
            result["formatted_code"] = formatted
            result["validation"] = validation
            result["format_success"] = format_success
            result["success"] = validation.get("valid", False)
            
            self.logger.info(f"Code processing completed. Valid: {result['success']}")
            
        except Exception as e:
            self.logger.error(f"Code processing failed: {e}")
            result["error"] = str(e)
            result["success"] = False
        
        result["processing_time"] = time.time() - start_time
        return result
    
    def get_processing_info(self) -> Dict[str, Any]:
        """Get information about the code processor"""
        return {
            "config": {
                "python_line_length": self.config.python_line_length,
                "cpp_style": self.config.cpp_style,
                "timeout": self.config.timeout,
                "enable_black": self.config.enable_black,
                "enable_clang_format": self.config.enable_clang_format,
                "strict_validation": self.config.strict_validation
            },
            "available_tools": {
                "black": self._check_tool_available("black"),
                "clang-format": self._check_tool_available("clang-format")
            }
        }
    
    def _check_tool_available(self, tool_name: str) -> bool:
        """Check if a formatting tool is available"""
        try:
            subprocess.run([tool_name, '--version'], capture_output=True, timeout=5)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

if __name__ == "__main__":
    # Example usage
    config = FormattingConfig(enable_black=False, enable_clang_format=False)
    processor = CodeProcessor(config)
    
    sample_python = """
    def factorial(n):
        if n < 0:
            return None
        if n == 0:
            return 1
        return n * factorial(n-1)
    """
    
    result = processor.process_code(sample_python, "python")
    print("Processing result:")
    print(f"Success: {result['success']}")
    print(f"Language: {result['language']}")
    print(f"Processing time: {result['processing_time']:.3f}s")
    print(f"Formatted code:\n{result['formatted_code']}")
    if result['validation']['warnings']:
        print(f"Warnings: {result['validation']['warnings']}")
    
    print(f"\nProcessor info: {processor.get_processing_info()}")