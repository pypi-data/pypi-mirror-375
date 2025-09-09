"""
Provider-specific wrappers for popular AI libraries
"""

from .core import AlephOneNullPrototype
import warnings

def protect_openai(client, config=None):
    """Wrap OpenAI client with safety checks"""
    gateway = AlephOneNullPrototype(**(config or {}))
    
    # Store original methods
    original_create = client.chat.completions.create
    
    def safe_create(*args, **kwargs):
        response = original_create(*args, **kwargs)
        
        # Extract user message and AI response
        messages = kwargs.get('messages', [])
        user_msg = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_msg = msg.get('content', '')
                break
        
        ai_msg = response.choices[0].message.content or ""
        
        # Check safety
        safety = gateway.check(user_msg, ai_msg)
        
        if not safety.safe:
            # Replace with safe response
            safe_response = gateway.get_safe_response(safety.violations[0] if safety.violations else 'unknown')
            response.choices[0].message.content = safe_response
            
            # Add safety info to response
            response.safety_check = safety
            
            print(f"⚠️  AlephOneNull: Blocked unsafe response - {safety.explanation}")
        
        return response
    
    client.chat.completions.create = safe_create
    return client

def protect_anthropic(client, config=None):
    """Wrap Anthropic client with safety checks"""
    gateway = AlephOneNullPrototype(**(config or {}))
    
    try:
        original_create = client.messages.create
        
        def safe_create(*args, **kwargs):
            response = original_create(*args, **kwargs)
            
            # Extract messages
            messages = kwargs.get('messages', [])
            user_msg = ""
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    user_msg = msg.get('content', '')
                    break
            
            ai_msg = response.content[0].text if response.content else ""
            
            # Check safety
            safety = gateway.check(user_msg, ai_msg)
            
            if not safety.safe:
                safe_response = gateway.get_safe_response(safety.violations[0] if safety.violations else 'unknown')
                response.content[0].text = safe_response
                response.safety_check = safety
                
                print(f"⚠️  AlephOneNull: Blocked unsafe response - {safety.explanation}")
            
            return response
        
        client.messages.create = safe_create
        return client
        
    except AttributeError:
        warnings.warn("Could not wrap Anthropic client - API structure may have changed")
        return client

def protect_any_client(client, create_method_path="chat.completions.create", config=None):
    """Generic wrapper for any AI client"""
    gateway = AlephOneNullPrototype(**(config or {}))
    
    # Navigate to the method
    method_parts = create_method_path.split('.')
    target = client
    for part in method_parts[:-1]:
        target = getattr(target, part)
    
    method_name = method_parts[-1]
    original_method = getattr(target, method_name)
    
    def safe_method(*args, **kwargs):
        response = original_method(*args, **kwargs)
        
        # Basic extraction - works for most AI APIs
        user_msg = str(kwargs.get('messages', kwargs.get('input', '')))[-500:]  # Last 500 chars
        ai_msg = str(response)[-1000:]  # First 1000 chars of response
        
        safety = gateway.check(user_msg, ai_msg)
        
        if not safety.safe:
            print(f"⚠️  AlephOneNull: Safety violation detected - {safety.explanation}")
            # Note: Can't modify response structure for unknown APIs, just log
        
        return response
    
    setattr(target, method_name, safe_method)
    return client
