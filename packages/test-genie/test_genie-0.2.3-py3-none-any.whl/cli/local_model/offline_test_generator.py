#!/usr/bin/env python3
"""
Offline Test Generator - CLI Integration for TestGenie
Generates test cases using offline GGUF model with optimized resource usage
"""

import os
import sys
import argparse
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from functools import wraps
import tempfile
import shutil

# Import our modules
from main_orchestrator import TestGenieOrchestrator
from model_downloader import ModelDownloader, DownloadConfig
from runtime_installer import RuntimeInstaller, InstallConfig
from server_manager import ServerManager, ServerConfig
from prompt_handler import CodePromptHandler, PromptConfig
from code_formatter import CodeProcessor
from resource_manager import ResourceManager

# Custom Exceptions
class TestGenerationError(Exception):
    """Base exception for test generation errors"""
    pass

class FileReadError(TestGenerationError):
    """Exception for file reading errors"""
    pass

class ServerStartupError(TestGenerationError):
    """Exception for server startup errors"""
    pass

# Configuration
@dataclass
class TestGenConfig:
    model_url: str = "https://drive.google.com/file/d/1Pdmqn3AqXdlaZyj7iPVCAcRVHP3n9Eht/view?usp=drive_link"
    models_dir: str = "./models"
    server_host: str = "127.0.0.1"
    server_port: int = 8123
    max_positive: int = 3
    max_negative: int = 2
    timeout: int = 300
    cleanup_on_exit: bool = True

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

class OfflineTestGenerator:
    def __init__(self, 
                 model_url: str = "https://drive.google.com/file/d/1Pdmqn3AqXdlaZyj7iPVCAcRVHP3n9Eht/view?usp=drive_link",
                 models_dir: str = "./models",
                 server_host: str = "127.0.0.1",
                 server_port: int = 8123,
                 config: Optional[TestGenConfig] = None):
        
        self.config = config or TestGenConfig()
        self.model_url = model_url
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.server_host = server_host
        self.server_port = server_port
        
        # Initialize components with configurations
        self.downloader = ModelDownloader(str(self.models_dir), DownloadConfig())
        self.installer = RuntimeInstaller(config=InstallConfig())
        self.server_manager: Optional[ServerManager] = None
        self.prompt_handler: Optional[CodePromptHandler] = None
        self.code_processor = CodeProcessor()
        self.resource_manager = ResourceManager()
        
        # Setup logging
        self.logger = self._setup_logger()
        self.running = False
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('OfflineTestGenerator')
        if not logger.handlers:  # Only add handler if none exist
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        return logger
    
    def _validate_file(self, file_path: str) -> bool:
        """Validate input file"""
        try:
            path = Path(file_path)
            if not path.exists():
                self.logger.error(f"File not found: {file_path}")
                return False
            
            if not path.is_file():
                self.logger.error(f"Path is not a file: {file_path}")
                return False
            
            # Check file extension
            valid_extensions = ['.py', '.cpp', '.c', '.cc']
            if path.suffix.lower() not in valid_extensions:
                self.logger.error(f"Unsupported file type: {path.suffix}")
                return False
            
            # Check file size (reasonable limit)
            if path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
                self.logger.error(f"File too large: {path.stat().st_size} bytes")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"File validation failed: {e}")
            return False
    
    @retry_on_failure(max_retries=3, delay=2.0)
    def _ensure_dependencies(self) -> bool:
        """Ensure all dependencies are installed"""
        self.logger.info("Checking dependencies...")
        
        try:
            if not self.installer.install_all():
                raise TestGenerationError("Failed to install dependencies")
            return True
        except Exception as e:
            self.logger.error(f"Dependency installation failed: {e}")
            raise TestGenerationError(f"Dependencies not available: {e}") from e
    
    @retry_on_failure(max_retries=3, delay=2.0)
    def _ensure_model(self) -> bool:
        """Ensure model is downloaded"""
        self.logger.info("Checking model...")
        
        try:
            model_path = self.downloader.download_model(self.model_url)
            self.logger.info(f"Model ready: {model_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to download model: {e}")
            raise TestGenerationError(f"Model not available: {e}") from e
    
    def _start_server(self) -> bool:
        """Start the offline server"""
        self.logger.info("Starting offline server...")
        
        try:
            # Find the downloaded model
            model_files = list(self.models_dir.glob("*.gguf"))
            if not model_files:
                raise ServerStartupError("No GGUF model found")
            
            model_path = str(model_files[0])
            
            # Create server configuration
            server_config = ServerConfig(
                host=self.server_host,
                port=self.server_port,
                timeout=self.config.timeout
            )
            
            # Start server manager
            self.server_manager = ServerManager(
                model_path=model_path,
                config=server_config
            )
            
            success = self.server_manager.start()
            if success:
                self.logger.info("Server started successfully")
                # Initialize prompt handler
                server_url = self.server_manager.get_server_url()
                prompt_config = PromptConfig(timeout=self.config.timeout)
                self.prompt_handler = CodePromptHandler(server_url, prompt_config)
                return True
            else:
                raise ServerStartupError("Failed to start server")
                
        except Exception as e:
            self.logger.error(f"Server startup failed: {e}")
            raise ServerStartupError(f"Server startup failed: {e}") from e
    
    def _stop_server(self):
        """Stop the offline server"""
        if self.server_manager:
            self.logger.info("Stopping server...")
            self.server_manager.stop()
            self.server_manager = None
    
    def _read_source_file(self, file_path: str) -> str:
        """Read the source file content with validation"""
        try:
            if not self._validate_file(file_path):
                raise FileReadError(f"File validation failed: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                raise FileReadError(f"File is empty: {file_path}")
            
            self.logger.info(f"Read {len(content)} characters from {file_path}")
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            raise FileReadError(f"File read failed: {e}") from e
    
    def _detect_language(self, source_code: str, file_path: str) -> str:
        """Detect programming language from code and file extension"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext in ['.cpp', '.c', '.cc']:
            return 'cpp'
        elif ext == '.py':
            return 'python'
        else:
            # Fallback to content analysis
            if '#include' in source_code or 'int ' in source_code or 'void ' in source_code:
                return 'cpp'
            elif 'def ' in source_code or 'import ' in source_code:
                return 'python'
            else:
                return 'python'  # Default
    
    def _count_functions(self, source_code: str, language: str) -> int:
        """Count functions in source code"""
        if language == 'cpp':
            return (source_code.count('int ') + source_code.count('void ') + 
                   source_code.count('float ') + source_code.count('double ') +
                   source_code.count('bool ') + source_code.count('char '))
        else:  # python
            return source_code.count('def ')
    
    def _generate_test_prompt(self, source_code: str, language: str, positive: int, negative: int) -> str:
        """Generate optimized prompt for test case generation"""
        
        # Limit the number of test cases to prevent timeout
        max_positive = min(positive, self.config.max_positive)
        max_negative = min(negative, self.config.max_negative)
        
        function_count = self._count_functions(source_code, language)
        
        # Create language-specific prompt
        if language == 'cpp':
            if function_count <= 2:
                prompt = f"""Write C++ test cases for these functions:

{source_code}

Generate {max_positive} positive and {max_negative} negative test cases. Use assert() for testing. Keep it simple."""
            else:
                prompt = f"""Write C++ test cases for these {function_count} functions:

{source_code}

Generate {max_positive} positive and {max_negative} negative test cases per function. Use assert() for testing. Keep it simple and focused."""
        else:  # python
            if function_count <= 2:
                prompt = f"""Write pytest test cases for these functions:

{source_code}

Generate {max_positive} positive and {max_negative} negative test cases. Keep it simple."""
            else:
                prompt = f"""Write pytest test cases for these {function_count} functions:

{source_code}

Generate {max_positive} positive and {max_negative} negative test cases per function. Keep it simple and focused."""
        
        return prompt
    
    def _generate_tests(self, source_code: str, language: str, positive: int, negative: int) -> Optional[str]:
        """Generate test cases using the offline model with fallback mechanism"""
        if not self.prompt_handler:
            self.logger.error("Prompt handler not initialized")
            return None
        
        try:
            # Wait for server to be ready
            if not self.prompt_handler.wait_for_server():
                self.logger.error("Server not ready")
                return None
            
            # Try multiple prompt strategies with fallback
            prompts_to_try = [
                # Strategy 1: Full prompt with requested parameters
                self._generate_test_prompt(source_code, language, positive, negative),
                # Strategy 2: Simplified prompt with fewer test cases
                self._generate_test_prompt(source_code, language, min(positive, 2), min(negative, 1)),
                # Strategy 3: Very simple prompt
                f"Write {language} test cases for: {source_code[:500]}...",
                # Strategy 4: Ultra-simple fallback
                f"Write simple {language} tests for these functions: {self._count_functions(source_code, language)} functions"
            ]
            
            for i, prompt in enumerate(prompts_to_try, 1):
                self.logger.info(f"Trying generation strategy {i}...")
                
                try:
                    # Adjust parameters based on strategy
                    if i == 1:
                        # Full parameters for first attempt
                        max_tokens, temperature, timeout = 1024, 0.2, 180
                    elif i == 2:
                        # Reduced parameters for second attempt
                        max_tokens, temperature, timeout = 512, 0.3, 120
                    else:
                        # Minimal parameters for fallback attempts
                        max_tokens, temperature, timeout = 256, 0.4, 60
                    
                    result = self.prompt_handler.send_prompt(
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=0.9,
                        timeout=timeout
                    )
                    
                    if result and result.get("text") and len(result["text"].strip()) > 50:
                        self.logger.info(f"Success with strategy {i}")
                        return result["text"]
                    else:
                        self.logger.warning(f"Strategy {i} produced insufficient output")
                        
                except Exception as e:
                    self.logger.warning(f"Strategy {i} failed: {e}")
                    continue
            
            self.logger.error("All generation strategies failed")
            return None
                
        except Exception as e:
            self.logger.error(f"Test generation failed: {e}")
            return None
    
    def _save_test_file(self, source_file_path: str, test_content: str, language: str) -> str:
        """Save test content to file in the same directory as source file"""
        try:
            source_path = Path(source_file_path)
            source_dir = source_path.parent
            source_name = source_path.stem
            
            # Determine test file extension based on language
            if language == 'cpp':
                test_ext = '.cpp'
            else:  # python
                test_ext = '.py'
            
            # Generate test file name
            test_file_name = f"test_{source_name}{test_ext}"
            test_file_path = source_dir / test_file_name
            
            # Add imports and setup if not present
            imports = []
            
            if language == 'python':
                # Python test file
                if "import pytest" not in test_content:
                    imports.append("import pytest")
                
                if "from " not in test_content and "import " not in test_content:
                    # Add import for the source module
                    imports.extend([
                        "import sys",
                        "import os",
                        "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))",
                        f"from {source_name} import *"
                    ])
            elif language == 'cpp':
                # C++ test file
                if "#include" not in test_content:
                    imports.extend([
                        "#include <iostream>",
                        "#include <cassert>",
                        f'#include "{source_name}{source_path.suffix}"'
                    ])
            
            if imports:
                test_content = "\n".join(imports) + "\n\n" + test_content
            
            # Write test file
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            self.logger.info(f"Test file saved: {test_file_path}")
            return str(test_file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save test file: {e}")
            raise TestGenerationError(f"Failed to save test file: {e}") from e
    
    def _cleanup(self):
        """Clean up resources"""
        try:
            self._stop_server()
            if self.config.cleanup_on_exit:
                self.resource_manager.cleanup_all()
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    def generate_tests_for_file(self, 
                               file_path: str, 
                               positive: int = 3, 
                               negative: int = 2) -> Optional[str]:
        """Main method to generate tests for a file"""
        
        self.logger.info(f"Generating tests for: {file_path}")
        self.logger.info(f"Parameters: {positive} positive, {negative} negative test cases")
        
        try:
            # Step 1: Ensure dependencies
            if not self._ensure_dependencies():
                return None
            
            # Step 2: Ensure model is available
            if not self._ensure_model():
                return None
            
            # Step 3: Start server
            if not self._start_server():
                return None
            
            # Step 4: Read source file
            source_code = self._read_source_file(file_path)
            language = self._detect_language(source_code, file_path)
            
            # Step 5: Generate tests
            self.logger.info("Generating test cases...")
            test_content = self._generate_tests(source_code, language, positive, negative)
            
            if not test_content:
                self.logger.error("Failed to generate test cases")
                return None
            
            # Step 6: Save test file
            test_file_path = self._save_test_file(file_path, test_content, language)
            
            self.logger.info("✅ Test generation completed successfully!")
            return test_file_path
            
        except Exception as e:
            self.logger.error(f"Test generation failed: {e}")
            return None
        finally:
            # Always cleanup
            self._cleanup()
    
    def get_generation_info(self) -> Dict[str, Any]:
        """Get information about the current generation setup"""
        return {
            "model_url": self.model_url,
            "models_dir": str(self.models_dir),
            "server_host": self.server_host,
            "server_port": self.server_port,
            "config": {
                "max_positive": self.config.max_positive,
                "max_negative": self.config.max_negative,
                "timeout": self.config.timeout,
                "cleanup_on_exit": self.config.cleanup_on_exit
            },
            "server_running": self.server_manager is not None and self.server_manager.is_running() if self.server_manager else False
        }

def main():
    parser = argparse.ArgumentParser(
        description="TestGenie Offline Test Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  test-genie offline func.py -p 5 -n 3
  test-genie offline /path/to/file.py --positive 4 --negative 2
  test-genie offline script.py -p 2 -n 1 --port 8124
        """
    )
    
    parser.add_argument("file_path", help="Path to the Python file to generate tests for")
    parser.add_argument("-p", "--positive", type=int, default=3, 
                       help="Number of positive test cases per function (default: 3)")
    parser.add_argument("-n", "--negative", type=int, default=2, 
                       help="Number of negative test cases per function (default: 2)")
    parser.add_argument("--model-url", 
                       default="https://drive.google.com/file/d/1Pdmqn3AqXdlaZyj7iPVCAcRVHP3n9Eht/view?usp=drive_link",
                       help="URL to GGUF model file")
    parser.add_argument("--models-dir", default="./models", 
                       help="Directory to store models")
    parser.add_argument("--server-host", default="127.0.0.1", 
                       help="Server host")
    parser.add_argument("--server-port", type=int, default=8123, 
                       help="Server port")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger('OfflineTestGenerator').setLevel(logging.DEBUG)
    
    # Validate file path
    if not os.path.exists(args.file_path):
        print(f"❌ Error: File not found: {args.file_path}")
        sys.exit(1)
    
    if not (args.file_path.endswith('.py') or args.file_path.endswith('.cpp') or args.file_path.endswith('.c')):
        print(f"❌ Error: File must be a Python file (.py) or C++ file (.cpp/.c)")
        sys.exit(1)
    
    # Validate parameters
    if args.positive < 1 or args.negative < 1:
        print("❌ Error: Positive and negative test counts must be at least 1")
        sys.exit(1)
    
    # Create configuration
    config = TestGenConfig(
        model_url=args.model_url,
        models_dir=args.models_dir,
        server_host=args.server_host,
        server_port=args.server_port,
        max_positive=args.positive,
        max_negative=args.negative
    )
    
    # Create generator and run
    generator = OfflineTestGenerator(
        model_url=args.model_url,
        models_dir=args.models_dir,
        server_host=args.server_host,
        server_port=args.server_port,
        config=config
    )
    
    print(f"🚀 TestGenie Offline - Generating tests for {args.file_path}")
    print(f"📊 Parameters: {args.positive} positive, {args.negative} negative test cases")
    print("=" * 60)
    
    start_time = time.time()
    test_file_path = generator.generate_tests_for_file(
        file_path=args.file_path,
        positive=args.positive,
        negative=args.negative
    )
    end_time = time.time()
    
    print("=" * 60)
    
    if test_file_path:
        print(f"✅ Success! Test file generated: {test_file_path}")
        print(f"⏱️  Total time: {end_time - start_time:.2f} seconds")
        print(f"🧪 You can run the tests with: python -m pytest {test_file_path}")
        sys.exit(0)
    else:
        print("❌ Failed to generate test cases")
        sys.exit(1)

if __name__ == "__main__":
    main()