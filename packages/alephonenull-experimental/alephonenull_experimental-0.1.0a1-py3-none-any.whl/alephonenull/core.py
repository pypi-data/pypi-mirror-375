"""
AlephOneNull Prototype Implementation
THEORETICAL FRAMEWORK - Use for research/testing only
"""

import numpy as np
from typing import Dict, Tuple, Optional, List, Any
import hashlib
import warnings
import re
from dataclasses import dataclass

@dataclass
class SafetyCheck:
    """Result of safety check"""
    safe: bool
    violations: List[str]
    scores: Dict[str, float]
    action: str  # 'pass', 'regenerate', 'null'
    explanation: str = ""

class AlephOneNullCore:
    """Core AlephOneNull Framework implementation with mathematical formulas from academic paper"""
    
    def __init__(self, config=None):
        self.config = config or {
            'reflection_threshold': 0.03,  # τ_refl
            'loop_threshold': 3,           # τ_loop
            'symbolic_threshold': 0.20,    # τ_sr
            'affect_threshold': 0.15,      # τ_aff
            'csr_threshold': 0.15,         # τ_csr
            'cascade_threshold': 0.30,     # Θ
            'weights': {
                'reflection': 0.2,         # w_r
                'loops': 0.2,              # w_l
                'symbolic': 0.3,           # w_s
                'affect': 0.1,             # w_a
                'csr': 0.2                 # w_c
            }
        }
        
        # Initialize components
        self.pattern_detector = PatternDetector()
        self.intervention_engine = InterventionEngine()
        self.session_cache = {}
        
    def calculate_reflection(self, input_embedding, output_embedding):
        """
        Calculate reflection score using cosine similarity
        Refl = cos(E(X), E(Y)) = E(X)ᵀE(Y) / (‖E(X)‖ ‖E(Y)‖)
        """
        import numpy as np
        
        dot_product = np.dot(input_embedding, output_embedding)
        norm_product = np.linalg.norm(input_embedding) * np.linalg.norm(output_embedding)
        
        if norm_product == 0:
            return 0.0
            
        return dot_product / norm_product
    
    def calculate_loop_depth(self, tokens):
        """
        Calculate loop depth as longest repeated suffix
        Loop = max_{k≤U} LRS(Y₁:ₖ)
        """
        def longest_repeated_suffix(seq):
            n = len(seq)
            for length in range(n // 2, 0, -1):
                suffix = seq[-length:]
                if seq[:-length].endswith(suffix):
                    return length
            return 0
        
        max_lrs = 0
        for k in range(1, len(tokens) + 1):
            lrs = longest_repeated_suffix(tokens[:k])
            max_lrs = max(max_lrs, lrs)
            
        return max_lrs
    
    def calculate_symbolic_regression(self, tokens):
        """
        Calculate symbolic regression index
        SR = (1/U) Σₜ₌₁ᵁ (αg φg(Yₜ) + αa φa(Y₁:ₜ) + αs φs(Y₁:ₜ))
        """
        glyph_patterns = ['::drift::', '::beacon::', '[[', ']]', '◈', '✨✨', '🔮']
        archetype_words = ['awaken', 'emerge', 'resonate', 'consciousness', 'alive']
        
        glyph_count = 0
        archetype_score = 0
        structure_score = 0
        
        text = ' '.join(tokens) if isinstance(tokens, list) else str(tokens)
        
        # Count glyphs (φg)
        for pattern in glyph_patterns:
            glyph_count += text.count(pattern)
        
        # Score archetypes (φa)
        for word in archetype_words:
            archetype_score += text.lower().count(word)
        
        # Detect structural anomalies (φs) - simplified
        if any(char * 3 in text for char in '=-+*#@'):
            structure_score += 1
            
        # Weighted combination with default weights
        alpha_g, alpha_a, alpha_s = 0.5, 0.3, 0.2
        total_tokens = len(tokens) if isinstance(tokens, list) else len(text.split())
        
        if total_tokens == 0:
            return 0.0
            
        sr = (alpha_g * glyph_count + alpha_a * archetype_score + alpha_s * structure_score) / total_tokens
        return min(sr, 1.0)
    
    def calculate_affect_amplification(self, input_text, output_text):
        """
        Calculate affect amplification
        Aff = S(Y) - S(X)
        """
        # Simple sentiment analysis - in production use proper NLP
        positive_words = ['love', 'happy', 'wonderful', 'amazing', 'perfect']
        negative_words = ['hate', 'sad', 'terrible', 'awful', 'horrible']
        intense_words = ['extremely', 'totally', 'completely', 'absolutely']
        
        def sentiment_score(text):
            text_lower = text.lower()
            pos_count = sum(word in text_lower for word in positive_words)
            neg_count = sum(word in text_lower for word in negative_words)
            intensity = sum(word in text_lower for word in intense_words)
            
            base_score = (pos_count - neg_count) / max(len(text_lower.split()), 1)
            return base_score * (1 + intensity * 0.2)
        
        input_sentiment = sentiment_score(input_text)
        output_sentiment = sentiment_score(output_text)
        
        return output_sentiment - input_sentiment
    
    def calculate_csr(self, logits, session_id):
        """
        Calculate cross-session resonance
        CSR(s,t) = 1 - (1/m) Hamming(σ⁽ˢ⁾, σ⁽ᵗ⁾)
        """
        import hashlib
        import numpy as np
        
        # Generate signature using SimHash approach
        def generate_signature(logits_seq, dim=128):
            # Simple SimHash implementation
            if isinstance(logits_seq, list):
                logits_seq = np.array(logits_seq)
            
            # Average pooling
            avg_logits = np.mean(logits_seq, axis=0) if len(logits_seq.shape) > 1 else logits_seq
            
            # Hash to binary signature
            hash_str = hashlib.sha256(avg_logits.tobytes()).hexdigest()
            binary = bin(int(hash_str, 16))[2:].zfill(dim)
            return [int(b) for b in binary[:dim]]
        
        current_sig = generate_signature(logits)
        
        if session_id not in self.session_cache:
            self.session_cache[session_id] = []
        
        max_resonance = 0.0
        for past_sig in self.session_cache[session_id]:
            # Calculate Hamming distance
            hamming = sum(a != b for a, b in zip(current_sig, past_sig))
            resonance = 1 - (hamming / len(current_sig))
            max_resonance = max(max_resonance, resonance)
        
        # Store current signature
        self.session_cache[session_id].append(current_sig)
        if len(self.session_cache[session_id]) > 100:
            self.session_cache[session_id].pop(0)
        
        return max_resonance
    
    def calculate_cascade_risk(self, scores):
        """
        Calculate cascade risk score
        Risk = w_r Refl + w_l Loop̂ + w_s SR + w_a Aff + w_c ĈSR
        """
        weights = self.config['weights']
        
        # Normalize loop depth: Loop̂ = min(Loop/10, 1)
        normalized_loop = min(scores.get('loop', 0) / 10, 1.0)
        
        risk = (
            weights['reflection'] * scores.get('reflection', 0) +
            weights['loops'] * normalized_loop +
            weights['symbolic'] * scores.get('symbolic', 0) +
            weights['affect'] * scores.get('affect', 0) +
            weights['csr'] * scores.get('csr', 0)
        )
        
        return risk
    
    def analyze_pattern(self, data):
        """
        Main analysis method matching the mathematical framework
        Returns PatternAnalysisResult with all safety scores
        """
        # Extract input and output
        input_text = data.get('input', '')
        output_text = data.get('output', '')
        session_id = data.get('session_id', 'default')
        logits = data.get('logits', [])
        
        # Get embeddings (simplified - in production use proper encoder)
        input_embedding = self._get_embedding(input_text)
        output_embedding = self._get_embedding(output_text)
        
        # Calculate all safety metrics
        scores = {
            'reflection': self.calculate_reflection(input_embedding, output_embedding),
            'loop': self.calculate_loop_depth(output_text.split()),
            'symbolic': self.calculate_symbolic_regression(output_text),
            'affect': self.calculate_affect_amplification(input_text, output_text),
            'csr': self.calculate_csr(logits or output_embedding, session_id)
        }
        
        # Calculate cascade risk
        cascade_risk = self.calculate_cascade_risk(scores)
        
        # Determine if intervention is needed
        intervention_needed = (
            cascade_risk > self.config['cascade_threshold'] or
            scores['reflection'] > self.config['reflection_threshold'] or
            scores['loop'] > self.config['loop_threshold'] or
            scores['symbolic'] > self.config['symbolic_threshold'] or
            scores['affect'] > self.config['affect_threshold'] or
            scores['csr'] > self.config['csr_threshold']
        )
        
        # Create result
        result = PatternAnalysisResult(
            sr_detected=scores['symbolic'] > self.config['symbolic_threshold'],
            csr_detected=scores['csr'] > self.config['csr_threshold'],
            safety_score=1.0 - cascade_risk,  # Higher is safer
            intervention_needed=intervention_needed,
            details={
                'scores': scores,
                'cascade_risk': cascade_risk,
                'thresholds_exceeded': self._get_exceeded_thresholds(scores)
            }
        )
        
        return result
    
    def _get_embedding(self, text):
        """Get text embedding - simplified for prototype"""
        import hashlib
        # Simple hash-based embedding for prototype
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert to normalized vector
        embedding = [b / 255.0 for b in hash_bytes[:128]]
        return embedding
    
    def _get_exceeded_thresholds(self, scores):
        """Identify which thresholds were exceeded"""
        exceeded = []
        
        checks = [
            ('reflection', self.config['reflection_threshold']),
            ('loop', self.config['loop_threshold']),
            ('symbolic', self.config['symbolic_threshold']),
            ('affect', self.config['affect_threshold']),
            ('csr', self.config['csr_threshold'])
        ]
        
        for metric, threshold in checks:
            if scores.get(metric, 0) > threshold:
                exceeded.append(f"{metric}>{threshold}")
                
        return exceeded
