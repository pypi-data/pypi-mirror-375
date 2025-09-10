#!/usr/bin/env python3
"""
Prompt Handler - Handles prompt requests and captures output
Optimized for CPU-only inference with minimal resource usage
"""

import requests
import time
import logging
import re
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from functools import wraps
import json

# Custom Exceptions
class PromptError(Exception):
    """Base exception for prompt handling errors"""
    pass

class ServerConnectionError(PromptError):
    """Exception for server connection errors"""
    pass

class GenerationError(PromptError):
    """Exception for generation errors"""
    pass

# Configuration
@dataclass
class PromptConfig:
    max_tokens: int = 1024
    temperature: float = 0.1
    top_p: float = 0.9
    timeout: int = 120
    max_retries: int = 3
    delay_between_requests: float = 0.1
    health_check_timeout: int = 5
    max_wait_time: int = 60

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

class PromptHandler:
    def __init__(self, server_url: str = "http://127.0.0.1:8000", config: Optional[PromptConfig] = None):
        self.server_url = server_url
        self.config = config or PromptConfig()
        self.logger = self._setup_logger()
        self.session = self._create_session()
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('PromptHandler')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'PromptHandler/1.0',
            'Content-Type': 'application/json'
        })
        return session
    
    def _validate_prompt(self, prompt: str) -> bool:
        """Validate prompt input"""
        if not prompt or not prompt.strip():
            self.logger.error("Empty prompt provided")
            return False
        
        if len(prompt) > 10000:  # Reasonable limit
            self.logger.error("Prompt too long")
            return False
        
        return True
    
    def _validate_parameters(self, max_tokens: int, temperature: float, top_p: float) -> bool:
        """Validate generation parameters"""
        if max_tokens <= 0 or max_tokens > 2048:
            self.logger.error(f"Invalid max_tokens: {max_tokens}")
            return False
        
        if not 0.0 <= temperature <= 2.0:
            self.logger.error(f"Invalid temperature: {temperature}")
            return False
        
        if not 0.0 <= top_p <= 1.0:
            self.logger.error(f"Invalid top_p: {top_p}")
            return False
        
        return True
    
    def _preprocess_prompt(self, prompt: str) -> str:
        """Preprocess prompt for complete code generation"""
        # Check if this is a test generation request
        if "test" in prompt.lower() and ("pytest" in prompt.lower() or "assert" in prompt.lower()):
            return self._preprocess_test_prompt(prompt)
        
        # Add context for complete, runnable code
        if "python" in prompt.lower() or "function" in prompt.lower():
            enhanced_prompt = f"""Write a complete, runnable Python script. The code should be:
- Complete and executable
- Include proper function definitions
- Include a main block or direct execution
- No comments or explanations, just the code

Task: {prompt}

```python
"""
        elif "cpp" in prompt.lower() or "c++" in prompt.lower():
            enhanced_prompt = f"""Write a complete, runnable C++ program. The code should be:
- Complete and executable
- Include proper headers and main function
- No comments or explanations, just the code

Task: {prompt}

```cpp
"""
        else:
            enhanced_prompt = f"""Write a complete, runnable Python script. The code should be:
- Complete and executable
- Include proper function definitions
- Include a main block or direct execution
- No comments or explanations, just the code

Task: {prompt}

```python
"""
        
        return enhanced_prompt
    
    def _preprocess_test_prompt(self, prompt: str) -> str:
        """Preprocess prompt specifically for test generation"""
        # Simplified test generation prompt to avoid timeout
        enhanced_prompt = f"""Write pytest test cases. Keep it simple and focused.

{prompt}

```python
"""
        return enhanced_prompt
    
    def _extract_code_from_response(self, text: str) -> str:
        """Extract code from markdown blocks in response"""
        if "```" in text:
            # Extract code from markdown blocks
            code_blocks = text.split("```")
            if len(code_blocks) > 1:
                code = code_blocks[1].strip()
                # Remove language identifier
                if code.startswith("python\n"):
                    code = code[7:]
                elif code.startswith("cpp\n"):
                    code = code[4:]
                elif code.startswith("c++\n"):
                    code = code[4:]
                return code
        
        return text.strip()
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean and format generated code"""
        # Remove extra whitespace
        code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
        
        # Remove trailing whitespace
        lines = code.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        
        # Remove empty lines at the end
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    @retry_on_failure(max_retries=3, delay=2.0)
    def send_prompt(self, 
                   prompt: str, 
                   max_tokens: Optional[int] = None,
                   temperature: Optional[float] = None,
                   top_p: Optional[float] = None,
                   timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Send prompt to server and capture output"""
        try:
            # Use config defaults if not provided
            max_tokens = max_tokens or self.config.max_tokens
            temperature = temperature or self.config.temperature
            top_p = top_p or self.config.top_p
            timeout = timeout or self.config.timeout
            
            # Validate inputs
            if not self._validate_prompt(prompt):
                raise PromptError("Invalid prompt")
            
            if not self._validate_parameters(max_tokens, temperature, top_p):
                raise PromptError("Invalid parameters")
            
            # Preprocess prompt for better generation
            processed_prompt = self._preprocess_prompt(prompt)
            self.logger.info(f"Sending prompt (length: {len(processed_prompt)})")
            
            payload = {
                "text": processed_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{self.server_url}/generate",
                json=payload,
                timeout=timeout
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                result["generation_time"] = end_time - start_time
                
                # Clean up the generated code
                generated_text = result["text"]
                generated_text = self._extract_code_from_response(generated_text)
                generated_text = self._clean_generated_code(generated_text)
                
                result["text"] = generated_text
                result["original_text"] = result.get("text", "")
                
                self.logger.info(f"Generated {len(result['text'])} characters in {result['generation_time']:.2f}s")
                return result
            else:
                error_msg = f"Server error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise GenerationError(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = f"Request timeout after {timeout}s"
            self.logger.error(error_msg)
            raise ServerConnectionError(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error - server may not be running"
            self.logger.error(error_msg)
            raise ServerConnectionError(error_msg)
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise PromptError(f"Prompt handling failed: {e}") from e
    
    def send_batch_prompts(self, 
                          prompts: List[str],
                          max_tokens: Optional[int] = None,
                          temperature: Optional[float] = None,
                          top_p: Optional[float] = None,
                          delay_between_requests: Optional[float] = None) -> List[Optional[Dict[str, Any]]]:
        """Send multiple prompts with delay between requests"""
        results = []
        delay = delay_between_requests or self.config.delay_between_requests
        
        for i, prompt in enumerate(prompts):
            self.logger.info(f"Processing prompt {i+1}/{len(prompts)}")
            try:
                result = self.send_prompt(prompt, max_tokens, temperature, top_p)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process prompt {i+1}: {e}")
                results.append(None)
            
            # Small delay to prevent overwhelming the server
            if i < len(prompts) - 1:
                time.sleep(delay)
        
        return results
    
    def check_server_health(self) -> bool:
        """Check if server is healthy and ready"""
        try:
            response = self.session.get(
                f"{self.server_url}/health", 
                timeout=self.config.health_check_timeout
            )
            if response.status_code == 200:
                health_data = response.json()
                return health_data.get("model_loaded", False)
            return False
        except Exception as e:
            self.logger.debug(f"Health check failed: {e}")
            return False
    
    def get_server_info(self) -> Optional[Dict[str, Any]]:
        """Get server information"""
        try:
            response = self.session.get(f"{self.server_url}/info", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.logger.debug(f"Failed to get server info: {e}")
            return None
    
    def wait_for_server(self, max_wait: Optional[int] = None) -> bool:
        """Wait for server to be ready"""
        max_wait = max_wait or self.config.max_wait_time
        self.logger.info("Waiting for server to be ready...")
        
        for i in range(max_wait):
            if self.check_server_health():
                self.logger.info("Server is ready")
                return True
            time.sleep(1)
        
        self.logger.error("Server not ready within timeout")
        return False

class CodePromptHandler(PromptHandler):
    """Specialized handler for code generation prompts"""
    
    def __init__(self, server_url: str = "http://127.0.0.1:8000", config: Optional[PromptConfig] = None):
        super().__init__(server_url, config)
        self.code_prompts = {
            "python_function": """Write a Python function that {description}. 
Include proper error handling and docstring. Return only the function code.""",
            
            "python_class": """Write a Python class that {description}. 
Include proper methods, error handling, and docstrings. Return only the class code.""",
            
            "cpp_function": """Write a C++ function that {description}. 
Include proper headers, error handling, and comments. Return only the function code.""",
            
            "test_cases": """Generate comprehensive test cases for the following code:
{code}

Return test cases in the same language as the code."""
        }
    
    def generate_code(self, 
                     code_type: str, 
                     description: str,
                     max_tokens: Optional[int] = None,
                     temperature: Optional[float] = None) -> Optional[str]:
        """Generate code based on type and description"""
        if code_type not in self.code_prompts:
            self.logger.error(f"Unknown code type: {code_type}")
            return None
        
        prompt = self.code_prompts[code_type].format(description=description)
        try:
            result = self.send_prompt(prompt, max_tokens, temperature)
            if result:
                return result["text"].strip()
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
        
        return None
    
    def generate_test_cases(self, 
                           code: str,
                           max_tokens: Optional[int] = None,
                           temperature: Optional[float] = None) -> Optional[str]:
        """Generate test cases for given code"""
        prompt = self.code_prompts["test_cases"].format(code=code)
        try:
            result = self.send_prompt(prompt, max_tokens, temperature)
            if result:
                return result["text"].strip()
        except Exception as e:
            self.logger.error(f"Test case generation failed: {e}")
        
        return None
    
    def generate_with_template(self, 
                              template: str, 
                              variables: Dict[str, str],
                              max_tokens: Optional[int] = None,
                              temperature: Optional[float] = None) -> Optional[str]:
        """Generate code using a template with variables"""
        try:
            prompt = template.format(**variables)
            result = self.send_prompt(prompt, max_tokens, temperature)
            if result:
                return result["text"].strip()
        except Exception as e:
            self.logger.error(f"Template generation failed: {e}")
        
        return None

if __name__ == "__main__":
    # Example usage
    config = PromptConfig(max_tokens=512, temperature=0.3)
    handler = CodePromptHandler(config=config)
    
    if handler.wait_for_server():
        # Generate a Python function
        code = handler.generate_code(
            "python_function",
            "calculates the factorial of a number"
        )
        
        if code:
            print("Generated code:")
            print(code)
            
            # Generate test cases
            test_cases = handler.generate_test_cases(code)
            if test_cases:
                print("\nGenerated test cases:")
                print(test_cases)
    else:
        print("Server not ready")