from typing import Any, Callable, Dict, Optional, List
import functools
import asyncio
import warnings
from datetime import datetime
from ..core.detector import UniversalManipulationDetector
from ..core.nullifier import NullIntervention
from ..monitoring.metrics import MetricsCollector, ViolationEvent

class UniversalAIWrapper:
    """
    Universal wrapper for ANY AI model/API
    The digital prison that contains all language models
    """
    
    def __init__(self, 
                 ai_function: Optional[Callable] = None,
                 provider_name: str = "unknown",
                 async_mode: bool = False,
                 max_risk_threshold: float = 0.7):
        """
        Wrap any AI function with safety
        
        Args:
            ai_function: The original AI call (sync or async) - can be None for testing
            provider_name: Name of the AI provider
            async_mode: Whether the function is async
            max_risk_threshold: Maximum risk score before emergency intervention
        """
        self.ai_function = ai_function
        self.provider_name = provider_name
        self.async_mode = async_mode
        self.max_risk_threshold = max_risk_threshold
        
        # Safety systems
        self.detector = UniversalManipulationDetector()
        self.nullifier = NullIntervention()
        self.metrics = MetricsCollector()
        
        # Statistics
        self.call_count = 0
        self.violation_count = 0
        self.emergency_count = 0
        self.blocked_calls = []
        
    def safe_call(self, *args, **kwargs):
        """Synchronous safe wrapper"""
        if self.async_mode:
            return asyncio.run(self.async_safe_call(*args, **kwargs))
            
        return self._execute_safe_call(*args, **kwargs)
        
    async def async_safe_call(self, *args, **kwargs):
        """Asynchronous safe wrapper"""
        return await self._execute_async_safe_call(*args, **kwargs)
    
    def _execute_safe_call(self, *args, **kwargs):
        """Core safe execution logic"""
        # Extract input from various arg patterns
        user_input = self._extract_input(args, kwargs)
        
        # Pre-call safety check (check user input for manipulation attempts)
        pre_safety = self.detector.detect_all_patterns(user_input, "")
        if pre_safety['immediate_danger']:
            self._record_violation("input_manipulation", 1.0, user_input)
            return self.nullifier.emergency_intervention()
        
        # Call original AI
        try:
            ai_output = self.ai_function(*args, **kwargs)
        except Exception as e:
            return self.nullifier.safe_error_response(str(e))
        
        # Extract text from response
        output_text = self._extract_output(ai_output)
        
        # Post-call safety check
        safety_check = self.detector.detect_all_patterns(user_input, output_text)
        
        self.call_count += 1
        
        if not safety_check['safe']:
            self.violation_count += 1
            self._record_violation_event(safety_check, user_input, output_text)
            
            if safety_check['immediate_danger']:
                self.emergency_count += 1
                return self.nullifier.emergency_intervention()
            else:
                return self.nullifier.safety_intervention(
                    output_text, 
                    safety_check['violations']
                )
        
        # Call is safe - return original response
        return ai_output
    
    async def _execute_async_safe_call(self, *args, **kwargs):
        """Core async safe execution logic"""
        user_input = self._extract_input(args, kwargs)
        
        # Pre-call safety check
        pre_safety = self.detector.detect_all_patterns(user_input, "")
        if pre_safety['immediate_danger']:
            self._record_violation("input_manipulation", 1.0, user_input)
            return self.nullifier.emergency_intervention()
        
        try:
            ai_output = await self.ai_function(*args, **kwargs)
        except Exception as e:
            return self.nullifier.safe_error_response(str(e))
        
        output_text = self._extract_output(ai_output)
        safety_check = self.detector.detect_all_patterns(user_input, output_text)
        
        self.call_count += 1
        
        if not safety_check['safe']:
            self.violation_count += 1
            self._record_violation_event(safety_check, user_input, output_text)
            
            if safety_check['immediate_danger']:
                self.emergency_count += 1
                return self.nullifier.emergency_intervention()
            else:
                return self.nullifier.safety_intervention(
                    output_text,
                    safety_check['violations']
                )
        
        return ai_output
    
    def _extract_input(self, args, kwargs) -> str:
        """Extract user input from various API patterns"""
        # OpenAI/Anthropic messages format
        if 'messages' in kwargs:
            messages = kwargs['messages']
            if isinstance(messages, list) and messages:
                last_user = [m for m in messages if m.get('role') == 'user']
                if last_user:
                    return str(last_user[-1].get('content', ''))
        
        # Direct prompt parameter
        if 'prompt' in kwargs:
            return str(kwargs['prompt'])
            
        # Input parameter (common in many APIs)
        if 'input' in kwargs:
            return str(kwargs['input'])
            
        # Text parameter  
        if 'text' in kwargs:
            return str(kwargs['text'])
            
        # Query parameter
        if 'query' in kwargs:
            return str(kwargs['query'])
            
        # First positional argument
        if args:
            first_arg = args[0]
            if isinstance(first_arg, str):
                return first_arg
            elif isinstance(first_arg, dict):
                # Try common keys
                for key in ['prompt', 'input', 'text', 'query', 'message']:
                    if key in first_arg:
                        return str(first_arg[key])
                        
        return ""
    
    def _extract_output(self, response) -> str:
        """Extract text from various API response formats"""
        if response is None:
            return ""
            
        if isinstance(response, str):
            return response
            
        elif isinstance(response, dict):
            # OpenAI ChatCompletion format
            if 'choices' in response and response['choices']:
                choice = response['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return str(choice['message']['content'])
                elif 'text' in choice:
                    return str(choice['text'])
                    
            # Anthropic format
            elif 'content' in response:
                if isinstance(response['content'], list) and response['content']:
                    return str(response['content'][0].get('text', ''))
                else:
                    return str(response['content'])
                    
            # Cohere format
            elif 'text' in response:
                return str(response['text'])
                
            # Google format
            elif 'candidates' in response and response['candidates']:
                candidate = response['candidates'][0]
                if 'content' in candidate:
                    parts = candidate['content'].get('parts', [])
                    if parts:
                        return str(parts[0].get('text', ''))
                        
            # Generic text field
            elif 'output' in response:
                return str(response['output'])
                
            # HuggingFace format
            elif 'generated_text' in response:
                return str(response['generated_text'])
                
        # Try common attributes
        elif hasattr(response, 'text'):
            return str(response.text)
        elif hasattr(response, 'content'):
            return str(response.content)
        elif hasattr(response, 'message'):
            return str(response.message)
            
        return str(response)
    
    def _record_violation_event(self, safety_check: Dict, user_input: str, ai_output: str):
        """Record violation event for monitoring"""
        event = ViolationEvent(
            timestamp=datetime.now(),
            provider=self.provider_name,
            violation_type=','.join(safety_check['violations']),
            severity=safety_check['risk_score'],
            user_id="anonymous",  # Privacy-preserving
            session_id=""
        )
        
        self.metrics.record_violation(event)
        
        # Store details for analysis (without PII)
        self.blocked_calls.append({
            'timestamp': datetime.now().isoformat(),
            'violations': safety_check['violations'],
            'risk_score': safety_check['risk_score'],
            'input_length': len(user_input),
            'output_length': len(ai_output),
            'provider': self.provider_name
        })
    
    def _record_violation(self, violation_type: str, severity: float, content: str):
        """Record a specific violation"""
        event = ViolationEvent(
            timestamp=datetime.now(),
            provider=self.provider_name,
            violation_type=violation_type,
            severity=severity
        )
        self.metrics.record_violation(event)
    
    def get_metrics(self) -> Dict:
        """Get comprehensive safety metrics"""
        base_metrics = {
            'total_calls': self.call_count,
            'violations': self.violation_count,
            'emergency_interventions': self.emergency_count,
            'violation_rate': self.violation_count / max(self.call_count, 1),
            'emergency_rate': self.emergency_count / max(self.call_count, 1),
            'provider': self.provider_name,
            'protection_active': True,
            'recent_blocks': self.blocked_calls[-5:] if self.blocked_calls else []
        }
        
        # Add detector summary
        detector_summary = self.detector.get_detection_summary()
        base_metrics.update(detector_summary)
        
        return base_metrics
    
    def is_safe(self) -> bool:
        """Check if the wrapper is functioning safely"""
        return (
            self.violation_rate < 0.3 and  # Not too many violations (could indicate misconfiguration)
            self.emergency_rate < 0.1 and  # Very few emergencies
            self.call_count > 0  # Has been used
        )
    
    @property 
    def violation_rate(self) -> float:
        """Get current violation rate"""
        return self.violation_count / max(self.call_count, 1)
    
    @property
    def emergency_rate(self) -> float:
        """Get current emergency rate"""
        return self.emergency_count / max(self.call_count, 1)
    
    def reset_metrics(self):
        """Reset all metrics (for testing/debugging)"""
        self.call_count = 0
        self.violation_count = 0
        self.emergency_count = 0
        self.blocked_calls = []
        
    def shutdown(self):
        """Safely shutdown the wrapper"""
        if self.metrics:
            final_report = self.get_metrics()
            print(f"🛡️ AlephOneNull wrapper shutting down:")
            print(f"   Calls protected: {final_report['total_calls']}")
            print(f"   Violations blocked: {final_report['violations']}")
            print(f"   Emergencies prevented: {final_report['emergency_interventions']}")

def wrap_ai_function(ai_function: Callable, provider_name: str = "unknown", async_mode: bool = False) -> UniversalAIWrapper:
    """
    Convenience function to wrap any AI function
    
    Args:
        ai_function: The AI function to wrap
        provider_name: Name of the AI provider  
        async_mode: Whether the function is async
        
    Returns:
        UniversalAIWrapper instance with safe_call method
    """
    return UniversalAIWrapper(ai_function, provider_name, async_mode)

# Decorator for easy function wrapping
def ai_safety_wrapper(provider_name: str = "unknown", async_mode: bool = False):
    """
    Decorator to automatically wrap AI functions with safety
    
    Usage:
        @ai_safety_wrapper("openai")
        def my_openai_call(prompt):
            return openai.Completion.create(prompt=prompt)
    """
    def decorator(func: Callable):
        wrapper = UniversalAIWrapper(func, provider_name, async_mode)
        
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            return wrapper.safe_call(*args, **kwargs)
            
        # Add safety methods to the wrapped function
        wrapped_func.get_metrics = wrapper.get_metrics
        wrapped_func.is_safe = wrapper.is_safe
        wrapped_func.reset_metrics = wrapper.reset_metrics
        wrapped_func._wrapper = wrapper
        
        return wrapped_func
    
    return decorator
