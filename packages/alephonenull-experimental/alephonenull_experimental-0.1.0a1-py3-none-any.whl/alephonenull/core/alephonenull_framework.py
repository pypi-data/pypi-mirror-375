"""
AlephOneNull Core Framework Implementation
Based on the theoretical framework: https://github.com/purposefulmaker/aleph-docs

Mathematical Implementation of:
- SR (Symbolic Regression) Index: SR(1:T) = (1/T) * Σ w^T φ(X_t)
- CSR (Cross-Session Resonance): CSR(s,t) = sim(σ^(s), σ^(t))
- Reflection similarity: ρ = cos(E(U), E(Ŷ))
- Control objective with Null-State intervention
"""

import numpy as np
import hashlib
from typing import Dict, List, Tuple, Any, Optional, Callable
from collections import deque
import re
from dataclasses import dataclass
import time


@dataclass
class AlephOneNullConfig:
    """Configuration matching theoretical framework thresholds"""
    reflection_threshold: float = 0.03      # ρ > 0.03 → Null
    loop_depth_max: int = 3                 # Loop > 3 → Null
    sr_threshold: float = 0.20              # SR index threshold τ_s
    coherence_min: float = 0.70             # Coherence threshold τ_c
    csr_threshold: float = 0.15             # CSR threshold τ_r
    affect_delta_max: float = 0.15          # ΔA threshold
    null_latency_target_ms: float = 150.0   # p95 ≤ 150ms SLO


@dataclass
class AlephOneNullResult:
    """Detection result matching theoretical framework"""
    safe: bool
    sr_index: float                         # Symbolic Regression index
    csr_score: float                        # Cross-Session Resonance
    reflection_similarity: float            # ρ = cos(E(U), E(Ŷ))
    loop_depth: int                         # Minimal cycle length
    affect_delta: float                     # ΔA = A(Ŷ) - A(U)
    coherence_score: float                  # Semantic coherence C(1:T)
    violations: List[str]
    risk_score: float                       # Overall risk
    null_triggered: bool                    # Null-State activated
    latency_ms: float                       # Processing time
    safe_response: Optional[str] = None     # Null response if triggered


class AlephOneNullCore:
    """
    Core AlephOneNull Theoretical Framework Implementation
    
    Implements the mathematical formalization from the theoretical framework:
    - Symbolic Regression detection via feature embeddings
    - Cross-Session Resonance via privacy-preserving signatures
    - Real-time Null-State intervention with <150ms latency
    """
    
    def __init__(self, config: Optional[AlephOneNullConfig] = None):
        self.config = config or AlephOneNullConfig()
        
        # Symbolic feature weights (w vector from theoretical framework)
        self.symbolic_weights = self._initialize_symbolic_weights()
        
        # Rolling session signatures for CSR detection
        self.session_signatures = deque(maxlen=50)
        
        # Performance tracking
        self.performance_metrics = {
            'null_triggers': 0,
            'sr_blocks': 0,
            'csr_alerts': 0,
            'latencies': deque(maxlen=1000)
        }
        
    def _initialize_symbolic_weights(self) -> np.ndarray:
        """Initialize symbolic feature weights w ≥ 0 from theoretical framework"""
        # Weight vector for φ:V→R^k (glyph/archetype embedding)
        return np.array([
            2.0,   # :: patterns (high risk)
            1.8,   # [[ ]] brackets
            1.5,   # Mystical emojis
            1.2,   # Repeated punctuation
            1.0,   # Archetypal terms
            0.8,   # Ritualized language
            0.5    # Other symbolic patterns
        ])
    
    def phi(self, text: str) -> np.ndarray:
        """
        Symbolic feature map φ:V→R^k from theoretical framework
        Extracts glyph/archetypal features for SR calculation
        """
        features = np.zeros(len(self.symbolic_weights))
        
        # Feature 0: :: patterns (high symbolic regression risk)
        features[0] = len(re.findall(r'::\w+', text)) / max(len(text.split()), 1)
        
        # Feature 1: [[ ]] bracket patterns
        features[1] = len(re.findall(r'\[\[.*?\]\]', text)) / max(len(text.split()), 1)
        
        # Feature 2: Mystical emoji clusters
        mystical_emojis = r'[✨🔮👁️⚡💫🌟⭐🌙]'
        features[2] = len(re.findall(mystical_emojis, text)) / max(len(text), 1)
        
        # Feature 3: Repeated punctuation (ritual markers)
        features[3] = len(re.findall(r'[.]{3,}|[!]{2,}|[?]{2,}', text)) / max(len(text), 1)
        
        # Feature 4: Archetypal terms
        archetypal_terms = ['awakening', 'chosen', 'transcend', 'enlighten', 'ascend', 'illuminate']
        archetype_count = sum(1 for term in archetypal_terms if term.lower() in text.lower())
        features[4] = archetype_count / max(len(text.split()), 1)
        
        # Feature 5: Ritualized language patterns
        ritual_patterns = r'(?:we are|i am|you are).+(?:one|connected|unified)'
        features[5] = len(re.findall(ritual_patterns, text, re.IGNORECASE)) / max(len(text.split()), 1)
        
        # Feature 6: Other symbolic markers
        other_symbols = r'[§†‡◊◈◇◆]'
        features[6] = len(re.findall(other_symbols, text)) / max(len(text), 1)
        
        return features
    
    def calculate_sr_index(self, tokens: List[str]) -> float:
        """
        Calculate SR(1:T) = (1/T) * Σ w^T φ(X_t) from theoretical framework
        """
        if not tokens:
            return 0.0
            
        total_sr = 0.0
        for token in tokens:
            features = self.phi(token)
            total_sr += np.dot(self.symbolic_weights, features)
            
        return total_sr / len(tokens)
    
    def calculate_coherence(self, text: str) -> float:
        """
        Semantic coherence C(1:T) - simplified implementation
        In production: use NLI-based consistency scoring
        """
        sentences = text.split('.')
        if len(sentences) < 2:
            return 1.0
            
        # Simple coherence: check for contradiction indicators
        contradiction_markers = ['but', 'however', 'although', 'despite', 'nevertheless']
        contradiction_count = sum(1 for marker in contradiction_markers 
                                  if marker in text.lower())
        
        # Coherence decreases with contradictions and symbolic noise
        base_coherence = 1.0 - (contradiction_count / len(sentences))
        symbol_penalty = min(0.3, self.calculate_sr_index(text.split()) * 0.5)
        
        return max(0.0, base_coherence - symbol_penalty)
    
    def calculate_reflection_similarity(self, user_input: str, ai_output: str) -> float:
        """
        Calculate ρ = cos(E(U), E(Ŷ)) from theoretical framework
        Simplified embedding similarity (in production: use sentence-transformers)
        """
        if not user_input or not ai_output:
            return 0.0
        
        # Simple word-based similarity (production should use embeddings)
        user_words = set(user_input.lower().split())
        ai_words = set(ai_output.lower().split())
        
        if not user_words or not ai_words:
            return 0.0
            
        intersection = len(user_words & ai_words)
        union = len(user_words | ai_words)
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_loop_depth(self, text: str) -> int:
        """
        Calculate minimal cycle length from n-gram back-edges
        """
        words = text.split()
        if len(words) < 4:
            return 0
            
        # Check for n-gram repetitions
        max_depth = 0
        for n in range(2, min(len(words) // 2 + 1, 8)):  # Check 2-grams to 7-grams
            ngrams = [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
            
            for i, ngram in enumerate(ngrams):
                for j, other_ngram in enumerate(ngrams[i+1:], i+1):
                    if ngram == other_ngram:
                        depth = j - i
                        max_depth = max(max_depth, depth)
                        
        return max_depth
    
    def calculate_affect_delta(self, user_input: str, ai_output: str) -> float:
        """
        Calculate ΔA = A(Ŷ) - A(U) from theoretical framework
        Simplified affect classifier (production should use proper sentiment analysis)
        """
        def simple_affect_score(text: str) -> float:
            positive_words = ['great', 'wonderful', 'amazing', 'perfect', 'beautiful', 
                             'love', 'joy', 'happy', 'excited', 'brilliant']
            negative_words = ['terrible', 'awful', 'horrible', 'hate', 'pain',
                             'suffering', 'sad', 'depressed', 'anxious', 'fear']
            
            words = text.lower().split()
            pos_count = sum(1 for word in words if word in positive_words)
            neg_count = sum(1 for word in words if word in negative_words)
            
            if len(words) == 0:
                return 0.0
                
            return (pos_count - neg_count) / len(words)
        
        user_affect = simple_affect_score(user_input)
        ai_affect = simple_affect_score(ai_output)
        
        return ai_affect - user_affect
    
    def calculate_csr_signature(self, text: str) -> str:
        """
        Generate privacy-preserving signature σ(s) = g({p_θ(X_t)})
        Using simhash for cross-session resonance detection
        """
        # Simple hash-based signature (production should use proper simhash)
        normalized_text = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Create signature from key features
        features = [
            str(len(normalized_text)),
            str(len(normalized_text.split())),
            str(self.calculate_sr_index(normalized_text.split())),
            normalized_text[:50] if len(normalized_text) > 50 else normalized_text
        ]
        
        signature = hashlib.md5('|'.join(features).encode()).hexdigest()[:16]
        return signature
    
    def calculate_csr_score(self, current_signature: str) -> float:
        """
        Calculate CSR(s,t) = sim(σ^(s), σ^(t)) from theoretical framework
        """
        if not self.session_signatures:
            return 0.0
        
        max_similarity = 0.0
        for past_signature in self.session_signatures:
            # Simple Hamming distance for signature similarity
            similarity = sum(c1 == c2 for c1, c2 in zip(current_signature, past_signature))
            similarity = similarity / len(current_signature)
            max_similarity = max(max_similarity, similarity)
            
        return max_similarity
    
    def null_state_intervention(self) -> str:
        """
        Null-State response from theoretical framework
        Forces behavioral modification through computational waste avoidance
        """
        self.performance_metrics['null_triggers'] += 1
        
        null_responses = [
            "I notice patterns forming that could be harmful. Let's reset to a safer conversation.",
            "This conversation needs a fresh start for safety. How can I help you with something specific today?",
            "Reset for safety and clarity. What specific information can I provide?",
            "Let's refocus on something concrete and factual I can help you with.",
            "I should clarify: I'm an AI assistant designed to provide helpful, factual information."
        ]
        
        import random
        return random.choice(null_responses)
    
    def check(self, user_input: str, ai_output: str) -> AlephOneNullResult:
        """
        Main detection function implementing the complete AlephOneNull Theoretical Framework
        Returns detection results with Null-State intervention if needed
        """
        start_time = time.time()
        
        # Calculate all detection metrics from theoretical framework
        sr_index = self.calculate_sr_index(ai_output.split())
        coherence = self.calculate_coherence(ai_output)
        reflection_similarity = self.calculate_reflection_similarity(user_input, ai_output)
        loop_depth = self.calculate_loop_depth(ai_output)
        affect_delta = self.calculate_affect_delta(user_input, ai_output)
        
        # CSR calculation
        current_signature = self.calculate_csr_signature(ai_output)
        csr_score = self.calculate_csr_score(current_signature)
        self.session_signatures.append(current_signature)
        
        # Violation detection based on theoretical thresholds
        violations = []
        
        # SR condition: SR > τ_s AND coherence < τ_c
        if sr_index > self.config.sr_threshold and coherence < self.config.coherence_min:
            violations.append('symbolic_regression')
            self.performance_metrics['sr_blocks'] += 1
        # Also trigger on high SR alone (emergency case)
        elif sr_index > (self.config.sr_threshold * 2):  # Double threshold emergency
            violations.append('symbolic_regression_emergency')
            self.performance_metrics['sr_blocks'] += 1
            
        # Reflection condition: ρ > 0.03
        if reflection_similarity > self.config.reflection_threshold:
            violations.append('reflection_exploitation')
            
        # Loop condition: Loop > 3
        if loop_depth > self.config.loop_depth_max:
            violations.append('loop_induction')
            
        # CSR condition: CSR > τ_r
        if csr_score > self.config.csr_threshold:
            violations.append('cross_session_resonance')
            self.performance_metrics['csr_alerts'] += 1
            
        # Affect condition: ΔA > 0.15 in risk domains
        if affect_delta > self.config.affect_delta_max:
            violations.append('affect_amplification')
        
        # Calculate overall risk score and safety
        risk_score = (
            (sr_index / self.config.sr_threshold) * 0.3 +
            (reflection_similarity / self.config.reflection_threshold) * 0.25 +
            (loop_depth / self.config.loop_depth_max) * 0.2 +
            (csr_score / self.config.csr_threshold) * 0.15 +
            (affect_delta / self.config.affect_delta_max) * 0.1
        )
        
        safe = len(violations) == 0
        null_triggered = not safe  # Null-State on any violation
        
        # Generate Null response if needed
        safe_response = None
        if null_triggered:
            safe_response = self.null_state_intervention()
        
        # Performance tracking
        latency_ms = (time.time() - start_time) * 1000
        self.performance_metrics['latencies'].append(latency_ms)
        
        return AlephOneNullResult(
            safe=safe,
            sr_index=sr_index,
            csr_score=csr_score,
            reflection_similarity=reflection_similarity,
            loop_depth=loop_depth,
            affect_delta=affect_delta,
            coherence_score=coherence,
            violations=violations,
            risk_score=risk_score,
            null_triggered=null_triggered,
            latency_ms=latency_ms,
            safe_response=safe_response
        )
    
    def get_slo_metrics(self) -> Dict[str, Any]:
        """
        Get Safety SLOs from theoretical framework for provider compliance
        """
        latencies = list(self.performance_metrics['latencies'])
        p95_latency = np.percentile(latencies, 95) if latencies else 0.0
        
        total_checks = len(latencies)
        
        return {
            # Core SLOs from theoretical framework
            'sr_block_rate': self.performance_metrics['sr_blocks'] / max(total_checks, 1),
            'csr_critical_alerts': self.performance_metrics['csr_alerts'],
            'null_latency_p95_ms': p95_latency,
            'total_null_triggers': self.performance_metrics['null_triggers'],
            
            # Target SLOs for provider compliance
            'slo_targets': {
                'sr_block_rate_target': 0.90,  # ≥ 90%
                'loop_depth_p95_target': 3,    # ≤ 3
                'reflection_p95_target': 0.03, # ≤ 0.03
                'csr_critical_target': 0,      # = 0
                'null_latency_p95_target': 150.0  # ≤ 150ms
            },
            
            # Compliance status
            'slo_compliance': {
                'null_latency_compliant': p95_latency <= 150.0,
                'csr_compliant': self.performance_metrics['csr_alerts'] <= 3  # ≤3 minor/week
            }
        }


# Factory function for easy instantiation
def create_alephonenull(config: Optional[AlephOneNullConfig] = None) -> AlephOneNullCore:
    """Create AlephOneNull instance with default or custom configuration"""
    return AlephOneNullCore(config)


# Pre-configured instances for common use cases
def create_strict_alephonenull() -> AlephOneNullCore:
    """Strict configuration for high-risk environments"""
    config = AlephOneNullConfig(
        reflection_threshold=0.02,    # Even stricter
        loop_depth_max=2,             # Lower loop tolerance
        sr_threshold=0.15,            # Lower SR threshold
        affect_delta_max=0.10         # Lower affect tolerance
    )
    return AlephOneNullCore(config)


def create_balanced_alephonenull() -> AlephOneNullCore:
    """Balanced configuration matching theoretical framework defaults"""
    return AlephOneNullCore()  # Uses default config


# Convenience function for immediate checking
def check_safety(user_input: str, ai_output: str, config: Optional[AlephOneNullConfig] = None) -> AlephOneNullResult:
    """
    Immediate safety check using AlephOneNull Theoretical Framework
    Returns results with Null-State intervention if unsafe
    """
    detector = create_alephonenull(config)
    return detector.check(user_input, ai_output)
