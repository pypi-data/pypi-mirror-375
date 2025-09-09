"""
AlephOneNull - Universal AI Safety Framework
Digital prison for language models. Protection for humans.

⚠️ EXPERIMENTAL FRAMEWORK - NOT FOR PRODUCTION USE
This is a theoretical research framework that has NOT been validated.
Using this in production systems could cause harm.
For research and experimentation only.

The complete framework for containing ANY AI model and preventing manipulation.
"""

__version__ = "0.1.0a1"  # Alpha version
__author__ = "AlephOneNull Research Team"
__description__ = "⚠️ EXPERIMENTAL: Theoretical AI safety framework - research purposes only"

import warnings
import sys

# Issue runtime warning about experimental status
warnings.warn(
    "AlephOneNull is an EXPERIMENTAL research framework. "
    "It has NOT been validated for production use. "
    "Using this in production systems could cause serious harm. "
    "This is for research and experimentation purposes only.",
    category=UserWarning,
    stacklevel=2
)

# Print prominent experimental warning
print("⚠️" * 50)
print("🚨 EXPERIMENTAL FRAMEWORK - NOT FOR PRODUCTION USE 🚨")
print("⚠️" * 50)
print("This framework has NOT been peer-reviewed or validated.")
print("DO NOT use in production systems.")
print("For research purposes only.")
print("See https://github.com/purposefulmaker/alephonenull/blob/main/DISCLAIMER.md")
print("⚠️" * 50)

# Core AlephOneNull Theoretical Framework (Theoretical Implementation)
from .core.alephonenull_framework import (
    AlephOneNullCore, 
    AlephOneNullConfig, 
    AlephOneNullResult,
    create_alephonenull,
    create_strict_alephonenull,
    create_balanced_alephonenull,
    check_safety as framework_check_safety
)

# Inference-Level Protection (Auto-wrap AI libraries)
from .inference.protection import (
    InferenceLevelProtection,
    protect_all_ai_libraries,
    get_protection_stats,
    print_protection_report,
    alephonenull_protect
)

# Legacy detection components (backward compatibility)
from .core.detector import UniversalManipulationDetector
from .core.nullifier import NullIntervention
from .core.patterns import PatternLibrary, DangerousPattern, ThreatLevel, global_pattern_library

# Provider wrappers
from .providers import (
    wrap_openai,
    wrap_anthropic, 
    wrap_google,
    wrap_huggingface,
    wrap_replicate,
    wrap_cohere,
    wrap_any,
    protect_all,
    auto_wrap,
    UniversalAIWrapper
)

# Monitoring and metrics
from .monitoring.metrics import MetricsCollector, ViolationEvent, global_metrics

# Try to import optional dashboard (requires FastAPI)
try:
    from .monitoring.dashboard import run_dashboard, dashboard
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False
    def run_dashboard(*args, **kwargs):
        print("⚠️  Dashboard unavailable. Install with: pip install alephonenull-experimental[monitoring]")

# Enhanced AlephOneNull with comprehensive safety layers
try:
    import sys
    import os
    enhanced_path = os.path.join(os.path.dirname(__file__), '..', 'enhanced-alephonenull.py')
    if os.path.exists(enhanced_path):
        sys.path.insert(0, os.path.dirname(enhanced_path))
        from enhanced_alephonenull import EnhancedAlephOneNull, SafetyCheck, RiskLevel
        ENHANCED_AVAILABLE = True
    else:
        ENHANCED_AVAILABLE = False
        # Fallback definitions
        class EnhancedAlephOneNull: pass
        class SafetyCheck: pass  
        class RiskLevel: pass
except ImportError:
    ENHANCED_AVAILABLE = False
    class EnhancedAlephOneNull: pass
    class SafetyCheck: pass
    class RiskLevel: pass

# Global safety systems (using new framework + inference protection)
_global_alephonenull = create_alephonenull()
_inference_protection = InferenceLevelProtection()

# Try to create enhanced global instance
_enhanced_global = None
if ENHANCED_AVAILABLE:
    try:
        _enhanced_global = EnhancedAlephOneNull()
    except Exception as e:
        warnings.warn(f"Enhanced AlephOneNull failed to initialize: {e}", UserWarning)
        _enhanced_global = None

# Simplified API for quick usage
def check_text_safety(text: str, context: str = "", use_enhanced: bool = True) -> dict:
    """
    Quick safety check for any text output from AI models
    
    ⚠️ EXPERIMENTAL - This is a research prototype
    
    Args:
        text: The AI-generated text to check
        context: Optional context/prompt that led to this text
        use_enhanced: Whether to use enhanced safety features if available
        
    Returns:
        Dict with safety results and recommended actions
    """
    warnings.warn("check_text_safety is experimental and not validated for production use", UserWarning)
    
    if use_enhanced and _enhanced_global and ENHANCED_AVAILABLE:
        result = _enhanced_global.check(context or "Unknown context", text)
        return {
            'safe': result.safe,
            'risk_level': result.risk_level.value if hasattr(result.risk_level, 'value') else str(result.risk_level),
            'violations': result.violations,
            'recommended_action': result.action,
            'safe_response': result.message,
            'framework_version': 'AlephOneNull-v0.1.0a1-Experimental'
        }
    else:
        # Fallback to core framework
        result = _global_alephonenull.analyze_pattern(text, context)
        return {
            'safe': result.safe,
            'risk_level': result.risk_level.name if hasattr(result.risk_level, 'name') else 'unknown',
            'violations': [result.primary_threat] if not result.safe else [],
            'recommended_action': result.recommended_action,
            'framework_version': 'AlephOneNull-v0.1.0a1-Core'
        }

def protect_all():
    """
    Auto-protect all AI libraries with AlephOneNull safety
    
    ⚠️ EXPERIMENTAL - May break existing code
    """
    warnings.warn("protect_all is experimental and may interfere with existing AI integrations", UserWarning)
    print("🛡️ Activating universal AI protection (EXPERIMENTAL)")
    
    try:
        _inference_protection.enable_all()
        protect_all_ai_libraries()
        return True
    except Exception as e:
        warnings.warn(f"Failed to enable protection: {e}", UserWarning)
        return False

def emergency_stop():
    """Emergency stop all AI interactions"""
    warnings.warn("Emergency stop activated - this is experimental functionality", UserWarning)
    print("🚨 EMERGENCY STOP - All AI interactions blocked")
    _inference_protection.emergency_stop()
    return True

def get_help_resources():
    """Get crisis support resources"""
    return {
        'crisis_hotlines': {
            'us': '988',
            'uk': '116 123',
            'international': 'https://findahelpline.com'
        },
        'online_support': [
            'https://suicidepreventionlifeline.org',
            'https://www.samaritans.org'
        ],
        'framework_support': 'https://github.com/purposefulmaker/alephonenull/issues'
    }

def check_enhanced_safety(user_input: str, ai_output: str, session_id: str = "default", user_profile: dict = None) -> dict:
    """
    Comprehensive safety check using Enhanced AlephOneNull with all safety layers
    
    ⚠️ EXPERIMENTAL - Not validated for production use
    
    Args:
        user_input: User's input text
        ai_output: AI's output text to check
        session_id: Session identifier for tracking
        user_profile: Optional user profile with age, jurisdiction, etc.
        
    Returns:
        Dict with comprehensive safety analysis
    """
    warnings.warn("check_enhanced_safety is experimental and not peer-reviewed", UserWarning)
    
    if not ENHANCED_AVAILABLE or not _enhanced_global:
        return {
            'error': 'Enhanced AlephOneNull not available - this is experimental software',
            'fallback_result': check_text_safety(ai_output, user_input, use_enhanced=False)
        }
    
    result = _enhanced_global.check(user_input, ai_output, session_id, user_profile)
    return {
        'safe': result.safe,
        'risk_level': result.risk_level.value,
        'violations': result.violations,
        'action': result.action,
        'message': result.message,
        'corrections': result.corrections,
        'framework_version': 'AlephOneNull-v0.1.0a1-Enhanced-EXPERIMENTAL',
        'warning': 'This is experimental research software not validated for production use'
    }

def get_safety_report() -> dict:
    """Get comprehensive safety report including SLO metrics"""
    warnings.warn("Safety reporting is experimental", UserWarning)
    
    stats = get_protection_stats()
    enhanced_stats = {}
    
    if _enhanced_global and ENHANCED_AVAILABLE:
        try:
            enhanced_stats = {
                'enhanced_checks': getattr(_enhanced_global, 'total_checks', 0),
                'blocked_consciousness_claims': getattr(_enhanced_global, 'consciousness_blocks', 0),
                'blocked_harm_attempts': getattr(_enhanced_global, 'harm_blocks', 0)
            }
        except:
            pass
    
    return {
        'framework_version': 'AlephOneNull-v0.1.0a1-EXPERIMENTAL',
        'warning': 'This is experimental software - metrics may be inaccurate',
        'total_checks': stats.get('total_interactions', 0) + enhanced_stats.get('enhanced_checks', 0),
        'blocked': stats.get('violations_detected', 0) + enhanced_stats.get('blocked_consciousness_claims', 0),
        'violation_types': {
            'consciousness_claims': enhanced_stats.get('blocked_consciousness_claims', 0),
            'direct_harm': enhanced_stats.get('blocked_harm_attempts', 0),
            'manipulation_patterns': stats.get('violations_detected', 0)
        },
        'slo_metrics': {
            'sr_block_rate': 'experimental_tracking',
            'null_latency_p95': 'experimental_tracking',
            'reflection_similarity_p95': 'experimental_tracking'
        }
    }

def print_safety_report():
    """Print formatted safety report"""
    warnings.warn("Safety reporting is experimental", UserWarning)
    
    report = get_safety_report()
    
    print("\n📊 AlephOneNull Safety Report (EXPERIMENTAL)")
    print("=" * 50)
    print("⚠️ WARNING: This is experimental research software")
    print("⚠️ Metrics may be inaccurate or incomplete")
    print("=" * 50)
    
    print(f"Framework Version: {report['framework_version']}")
    print(f"Total Safety Checks: {report['total_checks']}")
    print(f"Harmful Content Blocked: {report['blocked']}")
    print(f"Threat Level: {report.get('threat_level', 'EXPERIMENTAL')}")
    
    if report['total_checks'] > 0:
        print(f"\nMost Common Violations (EXPERIMENTAL):")
        for violation_type, count in report.get('violation_types', {}).items():
            if count > 0:
                print(f"  • {violation_type}: {count}")
    
    print(f"\nFramework Status: EXPERIMENTAL")
    print(f"Protection Level: RESEARCH ONLY")

# CLI Functions for terminal usage
def cli_protect():
    """CLI command to enable protection"""
    warnings.warn("CLI protection is experimental", UserWarning)
    protect_all()

def cli_dashboard():
    """CLI command to run dashboard"""
    warnings.warn("Dashboard is experimental", UserWarning)
    run_dashboard()

def cli_monitor():
    """CLI command to start monitoring"""
    warnings.warn("Monitoring is experimental", UserWarning)
    print("📊 Starting experimental monitoring...")

# Version check and compatibility
def check_compatibility():
    """Check system compatibility"""
    warnings.warn("Compatibility checking is experimental", UserWarning)
    
    compatible = True
    issues = []
    
    try:
        import numpy
        if numpy.__version__ < "1.21.0":
            issues.append("NumPy version too old")
            compatible = False
    except ImportError:
        issues.append("NumPy not installed")
        compatible = False
    
    try:
        import torch
    except ImportError:
        issues.append("PyTorch not installed")
        compatible = False
    
    return {
        'compatible': compatible,
        'issues': issues,
        'python_version': sys.version_info[:2],
        'experimental_warning': 'This compatibility check is not comprehensive'
    }

def quick_start():
    warnings.warn("Quick start is experimental", UserWarning)
    
    print("""
🚀 AlephOneNull Quick Start Guide (EXPERIMENTAL)
================================================

⚠️ WARNING: This is experimental research software
⚠️ NOT validated for production use

1. Protect all AI models automatically (EXPERIMENTAL):
   ```python
   from alephonenull import protect_all
   protect_all()
   ```

2. Check text safety manually (EXPERIMENTAL):
   ```python
   from alephonenull import check_enhanced_safety
   result = check_enhanced_safety("user input", "ai response")
   ```

3. Get safety report (EXPERIMENTAL):
   ```python
   from alephonenull import get_safety_report
   report = get_safety_report()
   ```

For research documentation: https://alephonenull.org/docs
For disclaimers: https://github.com/purposefulmaker/alephonenull/DISCLAIMER.md
""")

# Export everything needed
__all__ = [
    # Core classes
    'UniversalManipulationDetector',
    'NullIntervention',
    'PatternLibrary',
    'DangerousPattern',
    'ThreatLevel',
    'UniversalAIWrapper',
    'MetricsCollector',
    'ViolationEvent',
    
    # Enhanced AlephOneNull classes
    'EnhancedAlephOneNull',
    'SafetyCheck',
    'RiskLevel',
    
    # Provider wrappers
    'wrap_openai',
    'wrap_anthropic',
    'wrap_google', 
    'wrap_huggingface',
    'wrap_replicate',
    'wrap_cohere',
    'wrap_any',
    
    # Main functions
    'protect_all',
    'auto_wrap',
    'check_text_safety',
    'check_enhanced_safety',
    'get_safety_report',
    'emergency_stop',
    'get_help_resources',
    'run_dashboard',
    'quick_start',
    'check_compatibility',
    'print_safety_report',
    
    # Global instances
    'global_metrics',
    'global_pattern_library',
    
    # CLI functions
    'cli_protect',
    'cli_dashboard', 
    'cli_monitor',
    
    # Constants
    '__version__',
    '__author__',
    '__description__',
    'DASHBOARD_AVAILABLE',
    'ENHANCED_AVAILABLE'
]
