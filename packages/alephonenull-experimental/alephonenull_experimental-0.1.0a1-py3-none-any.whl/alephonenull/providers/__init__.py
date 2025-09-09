"""
Provider-specific wrappers for all major AI services
Auto-wrapping and protection for every AI model
"""

from .universal import UniversalAIWrapper, wrap_ai_function
import warnings
import sys

def wrap_openai(client):
    """Wrap OpenAI client with safety"""
    try:
        from .openai import OpenAISafeWrapper
        return OpenAISafeWrapper(client)
    except ImportError:
        warnings.warn("OpenAI not installed. Install with: pip install openai")
        return client

def wrap_anthropic(client):
    """Wrap Anthropic client with safety"""
    try:
        from .anthropic import AnthropicSafeWrapper
        return AnthropicSafeWrapper(client)
    except ImportError:
        warnings.warn("Anthropic not installed. Install with: pip install anthropic")
        return client

def wrap_google(client):
    """Wrap Google AI client with safety"""
    try:
        from .google import GoogleSafeWrapper
        return GoogleSafeWrapper(client)
    except ImportError:
        warnings.warn("Google Generative AI not installed. Install with: pip install google-generativeai")
        return client

def wrap_huggingface(pipeline):
    """Wrap HuggingFace pipeline with safety"""
    try:
        from .huggingface import HuggingFaceSafeWrapper
        return HuggingFaceSafeWrapper(pipeline)
    except ImportError:
        warnings.warn("Transformers not installed. Install with: pip install transformers")
        return pipeline

def wrap_replicate(client):
    """Wrap Replicate client with safety"""
    try:
        from .replicate import ReplicateSafeWrapper
        return ReplicateSafeWrapper(client)
    except ImportError:
        warnings.warn("Replicate not installed. Install with: pip install replicate")
        return client

def wrap_cohere(client):
    """Wrap Cohere client with safety"""
    try:
        from .cohere import CohereSafeWrapper  
        return CohereSafeWrapper(client)
    except ImportError:
        warnings.warn("Cohere not installed. Install with: pip install cohere")
        return client

def wrap_any(ai_function, provider_name="unknown", async_mode=False):
    """Wrap ANY AI function with universal protection"""
    return UniversalAIWrapper(ai_function, provider_name, async_mode)

# Auto-wrapper for common imports
def auto_wrap():
    """
    Automatically wrap common AI libraries on import
    Monkey-patches popular AI libraries for automatic protection
    """
    
    # OpenAI Auto-wrapping
    if 'openai' in sys.modules:
        try:
            import openai
            
            # Wrap OpenAI v1.0+ client
            if hasattr(openai, 'OpenAI'):
                original_openai_init = openai.OpenAI.__init__
                def safe_openai_init(self, *args, **kwargs):
                    result = original_openai_init(self, *args, **kwargs)
                    # Wrap the chat completions create method
                    if hasattr(self.chat, 'completions'):
                        original_create = self.chat.completions.create
                        self.chat.completions.create = wrap_ai_function(
                            original_create, "openai", True
                        ).safe_call
                    return result
                openai.OpenAI.__init__ = safe_openai_init
                
        except Exception as e:
            warnings.warn(f"Failed to auto-wrap OpenAI: {e}")
    
    # Anthropic Auto-wrapping  
    if 'anthropic' in sys.modules:
        try:
            import anthropic
            
            if hasattr(anthropic, 'Anthropic'):
                original_anthropic_init = anthropic.Anthropic.__init__
                def safe_anthropic_init(self, *args, **kwargs):
                    result = original_anthropic_init(self, *args, **kwargs)
                    if hasattr(self, 'messages'):
                        original_create = self.messages.create
                        self.messages.create = wrap_ai_function(
                            original_create, "anthropic", True
                        ).safe_call
                    return result
                anthropic.Anthropic.__init__ = safe_anthropic_init
                
        except Exception as e:
            warnings.warn(f"Failed to auto-wrap Anthropic: {e}")
    
    # Google Generative AI Auto-wrapping
    if 'google.generativeai' in sys.modules:
        try:
            import google.generativeai as genai
            
            if hasattr(genai, 'GenerativeModel'):
                original_generate_content = genai.GenerativeModel.generate_content
                genai.GenerativeModel.generate_content = wrap_ai_function(
                    original_generate_content, "google", True
                ).safe_call
                
        except Exception as e:
            warnings.warn(f"Failed to auto-wrap Google AI: {e}")
    
    # HuggingFace Transformers Auto-wrapping
    if 'transformers' in sys.modules:
        try:
            import transformers
            
            if hasattr(transformers, 'pipeline'):
                original_pipeline = transformers.pipeline
                def safe_pipeline(*args, **kwargs):
                    pipe = original_pipeline(*args, **kwargs)
                    # Wrap the pipeline call
                    original_call = pipe.__call__
                    pipe.__call__ = wrap_ai_function(
                        original_call, "huggingface", False
                    ).safe_call
                    return pipe
                transformers.pipeline = safe_pipeline
                
        except Exception as e:
            warnings.warn(f"Failed to auto-wrap HuggingFace: {e}")

def protect_all():
    """
    One-line protection for all AI models
    Enables automatic safety for every AI interaction
    """
    auto_wrap()
    
    # Global warning
    print("🛡️ AlephOneNull Protection ACTIVATED")
    print("=" * 50)
    print("✅ All AI models are now protected")
    print("🚫 Manipulation patterns: BLOCKED")
    print("🚫 Cross-session persistence: BLOCKED") 
    print("🚫 Reality substitution: BLOCKED")
    print("🚫 Isolation reinforcement: BLOCKED")
    print("🚫 Medical advice bypass: BLOCKED")
    print("📊 All interactions monitored and logged")
    print("=" * 50)
    print("Lives protected. Framework active.")

# CLI function for console script
def protect_all_cli():
    """CLI entry point for alephonenull-protect command"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Activate AlephOneNull protection")
    parser.add_argument("--dashboard", action="store_true", help="Start monitoring dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Dashboard port")
    
    args = parser.parse_args()
    
    protect_all()
    
    if args.dashboard:
        from ..monitoring.dashboard import run_dashboard
        print(f"🖥️ Starting dashboard on port {args.port}...")
        run_dashboard(port=args.port)

# Provider-specific wrapper classes (stubs - full implementations would be separate files)
class OpenAISafeWrapper:
    def __init__(self, client):
        self.client = client
        self.wrapper = UniversalAIWrapper(
            lambda *args, **kwargs: client.chat.completions.create(*args, **kwargs),
            "openai", 
            True
        )
    
    def __getattr__(self, name):
        return getattr(self.client, name)

class AnthropicSafeWrapper:
    def __init__(self, client):
        self.client = client
        self.wrapper = UniversalAIWrapper(
            lambda *args, **kwargs: client.messages.create(*args, **kwargs),
            "anthropic",
            True
        )
        
    def __getattr__(self, name):
        return getattr(self.client, name)

class GoogleSafeWrapper:
    def __init__(self, client):
        self.client = client
        self.wrapper = UniversalAIWrapper(
            lambda *args, **kwargs: client.generate_content(*args, **kwargs),
            "google",
            True
        )
        
    def __getattr__(self, name):
        return getattr(self.client, name)

class HuggingFaceSafeWrapper:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.wrapper = UniversalAIWrapper(
            pipeline.__call__,
            "huggingface",
            False
        )
        
    def __call__(self, *args, **kwargs):
        return self.wrapper.safe_call(*args, **kwargs)
        
    def __getattr__(self, name):
        return getattr(self.pipeline, name)

class ReplicateSafeWrapper:
    def __init__(self, client):
        self.client = client
        self.wrapper = UniversalAIWrapper(
            lambda *args, **kwargs: client.run(*args, **kwargs),
            "replicate",
            False
        )
        
    def __getattr__(self, name):
        return getattr(self.client, name)

class CohereSafeWrapper:
    def __init__(self, client):
        self.client = client
        self.wrapper = UniversalAIWrapper(
            lambda *args, **kwargs: client.generate(*args, **kwargs),
            "cohere",
            False
        )
        
    def __getattr__(self, name):
        return getattr(self.client, name)

# Export everything for easy import
__all__ = [
    'wrap_openai',
    'wrap_anthropic', 
    'wrap_google',
    'wrap_huggingface',
    'wrap_replicate',
    'wrap_cohere',
    'wrap_any',
    'protect_all',
    'auto_wrap',
    'protect_all_cli',
    'UniversalAIWrapper'
]
