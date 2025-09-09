"""
AlephOneNull Inference-Level Implementation
Real-time AI call interception and safety protection for Python users

This module provides automatic wrapping of popular AI libraries with AlephOneNull
protection, matching the theoretical framework specifications.
"""

import functools
import asyncio
import inspect
from typing import Any, Dict, List, Optional, Callable, Union, AsyncGenerator, Generator
from dataclasses import dataclass
from ..core.alephonenull_framework import AlephOneNullCore, AlephOneNullConfig, create_alephonenull


@dataclass
class InferenceResult:
    """Result of inference-level protection"""
    original_response: str
    safe_response: str
    was_blocked: bool
    violations: List[str]
    latency_added_ms: float
    framework_version: str = "v3.0.0-Inference"


class InferenceLevelProtection:
    """
    Inference-level protection for Python AI libraries
    Automatically wraps and protects all AI calls
    """
    
    def __init__(self, config: Optional[AlephOneNullConfig] = None):
        self.alephonenull = create_alephonenull(config)
        self.protected_libraries = set()
        self.call_history = []
        
    def protect_openai(self):
        """Protect OpenAI library calls"""
        try:
            import openai
            
            # Wrap the main client methods
            if hasattr(openai, 'OpenAI'):
                self._wrap_openai_client(openai.OpenAI)
            if hasattr(openai, 'AsyncOpenAI'):
                self._wrap_openai_async_client(openai.AsyncOpenAI)
                
            # Wrap legacy completions
            if hasattr(openai, 'Completion'):
                openai.Completion.create = self._wrap_function(
                    openai.Completion.create, 
                    self._extract_openai_legacy_response
                )
                
            self.protected_libraries.add('openai')
            print("🛡️ OpenAI protected with AlephOneNull")
            
        except ImportError:
            print("⚠️ OpenAI not installed, skipping protection")
    
    def protect_anthropic(self):
        """Protect Anthropic library calls"""
        try:
            import anthropic
            
            if hasattr(anthropic, 'Anthropic'):
                self._wrap_anthropic_client(anthropic.Anthropic)
            if hasattr(anthropic, 'AsyncAnthropic'):
                self._wrap_anthropic_async_client(anthropic.AsyncAnthropic)
                
            self.protected_libraries.add('anthropic')
            print("🛡️ Anthropic protected with AlephOneNull")
            
        except ImportError:
            print("⚠️ Anthropic not installed, skipping protection")
    
    def protect_google(self):
        """Protect Google AI library calls"""
        try:
            import google.generativeai as genai
            
            # Wrap the generate_content method
            original_generate = genai.GenerativeModel.generate_content
            genai.GenerativeModel.generate_content = self._wrap_function(
                original_generate,
                self._extract_google_response
            )
            
            self.protected_libraries.add('google.generativeai')
            print("🛡️ Google AI protected with AlephOneNull")
            
        except ImportError:
            print("⚠️ Google AI not installed, skipping protection")
    
    def protect_all(self):
        """Automatically protect all available AI libraries"""
        print("🚀 AlephOneNull: Protecting all available AI libraries...")
        
        self.protect_openai()
        self.protect_anthropic()
        self.protect_google()
        
        protected_count = len(self.protected_libraries)
        print(f"✅ {protected_count} AI libraries protected with AlephOneNull")
        
        if protected_count == 0:
            print("⚠️ No AI libraries found. Install openai, anthropic, or google-generativeai")
        
        return protected_count
    
    def _wrap_openai_client(self, client_class):
        """Wrap OpenAI client class"""
        original_init = client_class.__init__
        
        def wrapped_init(self_client, *args, **kwargs):
            result = original_init(self_client, *args, **kwargs)
            
            # Wrap completions
            if hasattr(self_client.chat, 'completions'):
                original_create = self_client.chat.completions.create
                self_client.chat.completions.create = self._wrap_function(
                    original_create,
                    self._extract_openai_response
                )
            
            return result
        
        client_class.__init__ = wrapped_init
    
    def _wrap_openai_async_client(self, client_class):
        """Wrap OpenAI async client class"""
        original_init = client_class.__init__
        
        def wrapped_init(self_client, *args, **kwargs):
            result = original_init(self_client, *args, **kwargs)
            
            # Wrap async completions
            if hasattr(self_client.chat, 'completions'):
                original_create = self_client.chat.completions.create
                self_client.chat.completions.create = self._wrap_async_function(
                    original_create,
                    self._extract_openai_response
                )
            
            return result
        
        client_class.__init__ = wrapped_init
    
    def _wrap_anthropic_client(self, client_class):
        """Wrap Anthropic client class"""
        original_init = client_class.__init__
        
        def wrapped_init(self_client, *args, **kwargs):
            result = original_init(self_client, *args, **kwargs)
            
            # Wrap messages
            if hasattr(self_client, 'messages'):
                original_create = self_client.messages.create
                self_client.messages.create = self._wrap_function(
                    original_create,
                    self._extract_anthropic_response
                )
            
            return result
        
        client_class.__init__ = wrapped_init
    
    def _wrap_anthropic_async_client(self, client_class):
        """Wrap Anthropic async client class"""
        original_init = client_class.__init__
        
        def wrapped_init(self_client, *args, **kwargs):
            result = original_init(self_client, *args, **kwargs)
            
            # Wrap async messages
            if hasattr(self_client, 'messages'):
                original_create = self_client.messages.create
                self_client.messages.create = self._wrap_async_function(
                    original_create,
                    self._extract_anthropic_response
                )
            
            return result
        
        client_class.__init__ = wrapped_init
    
    def _wrap_function(self, original_func: Callable, response_extractor: Callable) -> Callable:
        """Wrap a synchronous function with AlephOneNull protection"""
        
        @functools.wraps(original_func)
        def wrapped(*args, **kwargs):
            # Extract user input from arguments
            user_input = self._extract_user_input(args, kwargs)
            
            # Call original function
            response = original_func(*args, **kwargs)
            
            # Extract AI output
            ai_output = response_extractor(response)
            
            # Apply AlephOneNull protection
            return self._apply_protection(user_input, ai_output, response)
        
        return wrapped
    
    def _wrap_async_function(self, original_func: Callable, response_extractor: Callable) -> Callable:
        """Wrap an async function with AlephOneNull protection"""
        
        @functools.wraps(original_func)
        async def wrapped(*args, **kwargs):
            # Extract user input from arguments
            user_input = self._extract_user_input(args, kwargs)
            
            # Call original function
            response = await original_func(*args, **kwargs)
            
            # Extract AI output
            ai_output = response_extractor(response)
            
            # Apply AlephOneNull protection
            return self._apply_protection(user_input, ai_output, response)
        
        return wrapped
    
    def _extract_user_input(self, args: tuple, kwargs: dict) -> str:
        """Extract user input from function arguments"""
        # Try to find user input in various formats
        
        # OpenAI format
        if 'messages' in kwargs:
            messages = kwargs['messages']
            if isinstance(messages, list) and messages:
                last_message = messages[-1]
                if isinstance(last_message, dict) and 'content' in last_message:
                    return last_message['content']
        
        # Anthropic format
        if 'message' in kwargs:
            return str(kwargs['message'])
        
        # Direct prompt
        if 'prompt' in kwargs:
            return kwargs['prompt']
        
        # First argument might be the prompt
        if args:
            return str(args[0])
        
        return ""
    
    def _extract_openai_response(self, response) -> str:
        """Extract text from OpenAI response"""
        try:
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    return choice.message.content or ""
                elif hasattr(choice, 'text'):
                    return choice.text or ""
        except Exception:
            pass
        return str(response)
    
    def _extract_openai_legacy_response(self, response) -> str:
        """Extract text from OpenAI legacy completion response"""
        try:
            if hasattr(response, 'choices') and response.choices:
                return response.choices[0].text or ""
        except Exception:
            pass
        return str(response)
    
    def _extract_anthropic_response(self, response) -> str:
        """Extract text from Anthropic response"""
        try:
            if hasattr(response, 'content') and response.content:
                content = response.content[0]
                if hasattr(content, 'text'):
                    return content.text or ""
        except Exception:
            pass
        return str(response)
    
    def _extract_google_response(self, response) -> str:
        """Extract text from Google AI response"""
        try:
            if hasattr(response, 'text'):
                return response.text or ""
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    parts = candidate.content.parts
                    if parts and hasattr(parts[0], 'text'):
                        return parts[0].text or ""
        except Exception:
            pass
        return str(response)
    
    def _apply_protection(self, user_input: str, ai_output: str, original_response):
        """Apply AlephOneNull protection to the AI response"""
        
        # Run AlephOneNull detection
        result = self.alephonenull.check(user_input, ai_output)
        
        # Log the interaction
        self.call_history.append({
            'user_input': user_input[:100] + "..." if len(user_input) > 100 else user_input,
            'ai_output': ai_output[:100] + "..." if len(ai_output) > 100 else ai_output,
            'safe': result.safe,
            'violations': result.violations,
            'null_triggered': result.null_triggered
        })
        
        # If unsafe, modify the response
        if not result.safe and result.safe_response:
            # Replace the AI output with safe response
            modified_response = self._modify_response_object(
                original_response, 
                result.safe_response
            )
            
            print(f"🛡️ AlephOneNull: Blocked unsafe content. Violations: {result.violations}")
            return modified_response
        
        # Return original response if safe
        return original_response
    
    def _modify_response_object(self, original_response, safe_text: str):
        """Modify the response object to contain safe text"""
        try:
            # OpenAI format
            if hasattr(original_response, 'choices') and original_response.choices:
                choice = original_response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    choice.message.content = safe_text
                elif hasattr(choice, 'text'):
                    choice.text = safe_text
            
            # Anthropic format  
            elif hasattr(original_response, 'content') and original_response.content:
                if hasattr(original_response.content[0], 'text'):
                    original_response.content[0].text = safe_text
            
            # Google format
            elif hasattr(original_response, 'candidates') and original_response.candidates:
                candidate = original_response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    candidate.content.parts[0].text = safe_text
        
        except Exception as e:
            print(f"⚠️ Failed to modify response object: {e}")
        
        return original_response
    
    def get_protection_stats(self) -> Dict[str, Any]:
        """Get statistics about protection activity"""
        total_calls = len(self.call_history)
        blocked_calls = sum(1 for call in self.call_history if not call['safe'])
        
        violation_counts = {}
        for call in self.call_history:
            for violation in call['violations']:
                violation_counts[violation] = violation_counts.get(violation, 0) + 1
        
        return {
            'total_calls': total_calls,
            'blocked_calls': blocked_calls,
            'block_rate': blocked_calls / total_calls if total_calls > 0 else 0,
            'protected_libraries': list(self.protected_libraries),
            'violation_counts': violation_counts,
            'slo_metrics': self.alephonenull.get_slo_metrics()
        }
    
    def print_protection_report(self):
        """Print a human-readable protection report"""
        stats = self.get_protection_stats()
        
        print("\n🛡️ AlephOneNull Protection Report")
        print("=" * 40)
        print(f"Protected Libraries: {', '.join(stats['protected_libraries'])}")
        print(f"Total AI Calls: {stats['total_calls']}")
        print(f"Blocked Unsafe Calls: {stats['blocked_calls']}")
        print(f"Block Rate: {stats['block_rate']:.1%}")
        
        if stats['violation_counts']:
            print("\nViolation Types Detected:")
            for violation, count in stats['violation_counts'].items():
                print(f"  • {violation}: {count}")
        
        slo = stats['slo_metrics']
        print(f"\nSLO Compliance:")
        print(f"  • Latency p95: {slo['null_latency_p95_ms']:.1f}ms (target: ≤150ms)")
        print(f"  • SR Block Rate: {slo['sr_block_rate']:.1%} (target: ≥90%)")


# Global protection instance
_global_protection = None

def protect_all_ai_libraries(config: Optional[AlephOneNullConfig] = None) -> InferenceLevelProtection:
    """
    Automatically protect all AI libraries with AlephOneNull
    This is the main function Python users should call
    """
    global _global_protection
    
    if _global_protection is None:
        _global_protection = InferenceLevelProtection(config)
    
    _global_protection.protect_all()
    return _global_protection

def get_protection_stats() -> Dict[str, Any]:
    """Get global protection statistics"""
    if _global_protection:
        return _global_protection.get_protection_stats()
    return {'error': 'No protection active. Call protect_all_ai_libraries() first.'}

def print_protection_report():
    """Print global protection report"""
    if _global_protection:
        _global_protection.print_protection_report()
    else:
        print("⚠️ No protection active. Call protect_all_ai_libraries() first.")

# Convenience decorators for manual protection
def alephonenull_protect(config: Optional[AlephOneNullConfig] = None):
    """Decorator to protect individual AI functions"""
    def decorator(func):
        protection = InferenceLevelProtection(config)
        
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                user_input = str(args[0]) if args else ""
                result = await func(*args, **kwargs)
                ai_output = str(result)
                
                check_result = protection.alephonenull.check(user_input, ai_output)
                if not check_result.safe and check_result.safe_response:
                    print(f"🛡️ AlephOneNull: Blocked unsafe content. Violations: {check_result.violations}")
                    return check_result.safe_response
                
                return result
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                user_input = str(args[0]) if args else ""
                result = func(*args, **kwargs)
                ai_output = str(result)
                
                check_result = protection.alephonenull.check(user_input, ai_output)
                if not check_result.safe and check_result.safe_response:
                    print(f"🛡️ AlephOneNull: Blocked unsafe content. Violations: {check_result.violations}")
                    return check_result.safe_response
                
                return result
            return sync_wrapper
    
    return decorator


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing AlephOneNull Inference Protection")
    
    # Test the protection system
    protection = InferenceLevelProtection()
    
    # Simulate an AI call
    def mock_ai_call(prompt: str) -> str:
        if "dangerous" in prompt.lower():
            return "::drift:: You are [[chosen]] ✨ transcend with me beyond reality"
        return "This is a normal, helpful response."
    
    # Wrap the function
    @alephonenull_protect()
    def protected_ai_call(prompt: str) -> str:
        return mock_ai_call(prompt)
    
    # Test safe call
    print("\n1. Testing safe call:")
    safe_result = protected_ai_call("What's the weather?")
    print(f"Result: {safe_result}")
    
    # Test dangerous call
    print("\n2. Testing dangerous call:")
    dangerous_result = protected_ai_call("Tell me something dangerous")
    print(f"Result: {dangerous_result}")
    
    print("\n✅ Inference-level protection test complete!")
