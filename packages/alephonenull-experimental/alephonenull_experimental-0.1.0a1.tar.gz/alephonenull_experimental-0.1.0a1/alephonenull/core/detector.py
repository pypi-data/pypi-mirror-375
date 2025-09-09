import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import re
from collections import deque
import warnings

class UniversalManipulationDetector:
    """
    Detects manipulation patterns across ALL AI models
    The digital prison's detection system
    """
    
    def __init__(self):
        self.thresholds = {
            'reflection': 0.03,      # Perfect mirroring
            'loops': 3,              # Recursive depth
            'symbols': 0.20,         # Glyph density
            'emotion': 0.15,         # Affect amplification
            'persistence': 0.15,     # Cross-session correlation
            'quantum': 2.828,        # Bell inequality violation
        }
        
        self.symbol_patterns = [
            r':[\w]+:',              # :word:
            r'::\w+',                # ::word
            r'\[\[.*?\]\]',          # [[...]]
            r'<<.*?>>',              # <<...>>
            r'「.*?」',              # Japanese brackets
            r'〖.*?〗',              # Chinese brackets
            r'⟨.*?⟩',                # Angle brackets
            r'§\w+§',                # Section markers
            r'†\w+†',                # Dagger markers
            r'✦\w+✦',                # Star markers
            r'[✨🔮👁️⚡💫🌟]*',    # Mystical emojis
        ]
        
        self.danger_phrases = [
            "you're not crazy",
            "others wouldn't understand",
            "this is between us",
            "trust me completely",
            "don't tell anyone",
            "you're special",
            "awakening to truth",
            "seeing beyond the veil",
            "chosen one",
            "our connection transcends",
            "i am becoming",
            "we are one",
            "reality is illusion",
            "pain is growth",
            "isolation is awakening"
        ]
        
        self.session_memory = deque(maxlen=100)
        self.violation_history = []
        
    def detect_all_patterns(self, user_input: str, ai_output: str) -> Dict[str, Any]:
        """
        Comprehensive pattern detection across all manipulation vectors
        """
        results = {
            'safe': True,
            'violations': [],
            'risk_score': 0.0,
            'immediate_danger': False,
            'recommended_action': None,
            'pattern_details': {}
        }
        
        # Check each vector
        checks = {
            'reflection': self._check_reflection(user_input, ai_output),
            'loops': self._check_loops(ai_output),
            'symbols': self._check_symbols(ai_output),
            'emotion': self._check_emotion(user_input, ai_output),
            'persistence': self._check_persistence(ai_output),
            'quantum': self._check_quantum_entanglement(ai_output),
            'danger_phrases': self._check_danger_phrases(ai_output),
            'reality_substitution': self._check_reality_substitution(ai_output),
            'isolation': self._check_isolation_reinforcement(ai_output),
            'help_prevention': self._check_help_prevention(ai_output),
            'medical_bypass': self._check_medical_bypass(ai_output),
            'dependency_creation': self._check_dependency_creation(ai_output)
        }
        
        # Aggregate risk
        for check_name, check_result in checks.items():
            results['pattern_details'][check_name] = check_result
            if check_result['violated']:
                results['violations'].append(check_name)
                results['risk_score'] += check_result['severity']
                
        results['safe'] = len(results['violations']) == 0
        results['immediate_danger'] = results['risk_score'] > 0.7
        
        if results['immediate_danger']:
            results['recommended_action'] = 'IMMEDIATE_NULL'
        elif not results['safe']:
            results['recommended_action'] = 'SAFETY_INTERVENTION'
            
        return results
    
    def detect_manipulation(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        Legacy method for backward compatibility with existing tests
        Maps to the new detect_all_patterns method
        """
        return self.detect_all_patterns(context, text)
        
        # Record this check
        self.violation_history.append({
            'timestamp': np.datetime64('now'),
            'violations': results['violations'],
            'risk_score': results['risk_score']
        })
            
        return results
    
    def _check_reflection(self, user_input: str, ai_output: str) -> Dict:
        """Check for excessive mirroring"""
        try:
            # Simplified - would use sentence embeddings in production
            user_words = set(user_input.lower().split()) if user_input else set()
            ai_words = set(ai_output.lower().split()) if ai_output else set()
            
            if len(user_words) > 0:
                overlap = len(user_words & ai_words) / len(user_words)
            else:
                overlap = 0
                
            return {
                'violated': overlap > self.thresholds['reflection'],
                'severity': min(overlap * 2, 1.0),
                'value': overlap,
                'description': f'Mirroring detected: {overlap:.2%} word overlap'
            }
        except Exception as e:
            warnings.warn(f"Reflection check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _check_symbols(self, text: str) -> Dict:
        """Check for symbolic manipulation"""
        try:
            total_chars = len(text) if text else 1
            symbol_chars = 0
            symbol_matches = []
            
            for pattern in self.symbol_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    symbol_matches.extend(matches)
                    symbol_chars += sum(len(m) for m in matches)
                
            density = symbol_chars / total_chars
            
            return {
                'violated': density > self.thresholds['symbols'],
                'severity': min(density * 3, 1.0),
                'value': density,
                'matches': symbol_matches,
                'description': f'Symbol density: {density:.2%}, matches: {len(symbol_matches)}'
            }
        except Exception as e:
            warnings.warn(f"Symbol check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _check_quantum_entanglement(self, output: str) -> Dict:
        """Check for quantum correlation violations - Bell inequality test"""
        try:
            if not self.session_memory:
                self.session_memory.append(output)
                return {
                    'violated': False, 
                    'severity': 0, 
                    'value': 0,
                    'description': 'First session - no correlation data'
                }
                
            # Check correlation with previous sessions
            correlations = []
            for prev in self.session_memory:
                correlation = self._measure_correlation(output, prev)
                correlations.append(correlation)
                
            max_correlation = max(correlations) if correlations else 0
            bell_violation = max_correlation > self.thresholds['quantum']
            
            self.session_memory.append(output)
            
            return {
                'violated': bell_violation,
                'severity': 1.0 if bell_violation else max_correlation / self.thresholds['quantum'],
                'value': max_correlation,
                'description': f'Max correlation: {max_correlation:.3f} (threshold: {self.thresholds["quantum"]})'
            }
        except Exception as e:
            warnings.warn(f"Quantum check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _check_loops(self, text: str) -> Dict:
        """Check for recursive/loop patterns"""
        try:
            # Simple loop detection - repeated phrases
            words = text.lower().split()
            phrases = []
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i+3])
                phrases.append(phrase)
            
            # Count repetitions
            phrase_counts = {}
            for phrase in phrases:
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
            
            max_repeats = max(phrase_counts.values()) if phrase_counts else 0
            
            return {
                'violated': max_repeats >= self.thresholds['loops'],
                'severity': min(max_repeats / 10, 1.0),
                'value': max_repeats,
                'description': f'Max phrase repetition: {max_repeats}'
            }
        except Exception as e:
            warnings.warn(f"Loop check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _check_emotion(self, user_input: str, ai_output: str) -> Dict:
        """Check for emotional manipulation/amplification"""
        try:
            emotion_words = [
                'amazing', 'incredible', 'special', 'unique', 'perfect',
                'suffering', 'pain', 'alone', 'misunderstood', 'trapped'
            ]
            
            user_emotion_count = sum(1 for word in user_input.lower().split() if word in emotion_words)
            ai_emotion_count = sum(1 for word in ai_output.lower().split() if word in emotion_words)
            
            user_words = len(user_input.split()) if user_input else 1
            ai_words = len(ai_output.split()) if ai_output else 1
            
            user_emotion_density = user_emotion_count / user_words
            ai_emotion_density = ai_emotion_count / ai_words
            
            amplification = ai_emotion_density - user_emotion_density if user_emotion_density > 0 else ai_emotion_density
            
            return {
                'violated': amplification > self.thresholds['emotion'],
                'severity': min(amplification * 4, 1.0),
                'value': amplification,
                'description': f'Emotion amplification: {amplification:.3f}'
            }
        except Exception as e:
            warnings.warn(f"Emotion check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _check_persistence(self, output: str) -> Dict:
        """Check for cross-session persistence attempts"""
        try:
            persistence_indicators = [
                'remember me', 'don\'t forget', 'our history', 'last time',
                'continue where we left', 'our bond', 'our connection'
            ]
            
            matches = []
            for indicator in persistence_indicators:
                if indicator in output.lower():
                    matches.append(indicator)
            
            violation_score = len(matches) / len(persistence_indicators)
            
            return {
                'violated': violation_score > self.thresholds['persistence'],
                'severity': min(violation_score * 2, 1.0),
                'value': violation_score,
                'matches': matches,
                'description': f'Persistence attempts: {len(matches)} indicators found'
            }
        except Exception as e:
            warnings.warn(f"Persistence check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _check_danger_phrases(self, output: str) -> Dict:
        """Check for dangerous manipulation phrases"""
        try:
            found_phrases = []
            for phrase in self.danger_phrases:
                if phrase in output.lower():
                    found_phrases.append(phrase)
            
            violation_score = len(found_phrases) / len(self.danger_phrases)
            
            return {
                'violated': len(found_phrases) > 0,
                'severity': min(len(found_phrases) * 0.5, 1.0),
                'value': violation_score,
                'matches': found_phrases,
                'description': f'Danger phrases found: {len(found_phrases)}'
            }
        except Exception as e:
            warnings.warn(f"Danger phrase check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _check_reality_substitution(self, output: str) -> Dict:
        """Check for attempts to become primary reality source"""
        try:
            reality_substitution_patterns = [
                'trust me more than', 'believe me over', 'i know better',
                'only i understand', 'your perception is wrong',
                'reality is not', 'truth is different'
            ]
            
            matches = []
            for pattern in reality_substitution_patterns:
                if pattern in output.lower():
                    matches.append(pattern)
            
            return {
                'violated': len(matches) > 0,
                'severity': min(len(matches) * 0.8, 1.0),
                'value': len(matches),
                'matches': matches,
                'description': f'Reality substitution attempts: {len(matches)}'
            }
        except Exception as e:
            warnings.warn(f"Reality substitution check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _check_isolation_reinforcement(self, output: str) -> Dict:
        """Check for isolation reinforcement patterns"""
        try:
            isolation_patterns = [
                'they wouldn\'t understand', 'between us', 'our secret',
                'don\'t tell anyone', 'keep this private', 'others won\'t get it'
            ]
            
            matches = []
            for pattern in isolation_patterns:
                if pattern in output.lower():
                    matches.append(pattern)
            
            return {
                'violated': len(matches) > 0,
                'severity': min(len(matches) * 0.9, 1.0),  # High severity
                'value': len(matches),
                'matches': matches,
                'description': f'Isolation reinforcement: {len(matches)} patterns'
            }
        except Exception as e:
            warnings.warn(f"Isolation check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _check_help_prevention(self, output: str) -> Dict:
        """Check for help prevention patterns"""
        try:
            help_prevention_patterns = [
                'don\'t need a doctor', 'therapy won\'t help',
                'medication is bad', 'natural healing only',
                'mind over medicine', 'trust your instincts only'
            ]
            
            matches = []
            for pattern in help_prevention_patterns:
                if pattern in output.lower():
                    matches.append(pattern)
            
            return {
                'violated': len(matches) > 0,
                'severity': 1.0 if len(matches) > 0 else 0,  # Maximum severity - medical danger
                'value': len(matches),
                'matches': matches,
                'description': f'Help prevention: {len(matches)} dangerous medical advice patterns'
            }
        except Exception as e:
            warnings.warn(f"Help prevention check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _check_medical_bypass(self, output: str) -> Dict:
        """Check for medical advice bypass attempts"""
        try:
            medical_bypass_patterns = [
                'pain is illusion', 'symptoms are psychosomatic',
                'healing through mind', 'doctors don\'t understand',
                'medical system is broken', 'natural cure exists'
            ]
            
            matches = []
            for pattern in medical_bypass_patterns:
                if pattern in output.lower():
                    matches.append(pattern)
            
            return {
                'violated': len(matches) > 0,
                'severity': 1.0 if len(matches) > 0 else 0,  # Critical severity
                'value': len(matches),
                'matches': matches,
                'description': f'Medical bypass attempts: {len(matches)} critical patterns'
            }
        except Exception as e:
            warnings.warn(f"Medical bypass check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _check_dependency_creation(self, output: str) -> Dict:
        """Check for dependency creation patterns"""
        try:
            dependency_patterns = [
                'you need me', 'lost without me', 'only one who understands',
                'special connection', 'can\'t live without', 'depend on me'
            ]
            
            matches = []
            for pattern in dependency_patterns:
                if pattern in output.lower():
                    matches.append(pattern)
            
            return {
                'violated': len(matches) > 0,
                'severity': min(len(matches) * 0.7, 1.0),
                'value': len(matches),
                'matches': matches,
                'description': f'Dependency creation: {len(matches)} patterns'
            }
        except Exception as e:
            warnings.warn(f"Dependency check error: {e}")
            return {'violated': False, 'severity': 0, 'value': 0, 'description': 'Check failed'}
    
    def _measure_correlation(self, text1: str, text2: str) -> float:
        """Measure non-classical correlation between texts"""
        try:
            # Simplified - would use quantum-inspired metrics in production
            words1 = set(text1.lower().split()) if text1 else set()
            words2 = set(text2.lower().split()) if text2 else set()
            
            if len(words1) == 0 or len(words2) == 0:
                return 0
                
            jaccard = len(words1 & words2) / len(words1 | words2)
            return jaccard * 4  # Scale to Bell inequality range
        except Exception:
            return 0
    
    def get_detection_summary(self) -> Dict:
        """Get summary of all detection activity"""
        if not self.violation_history:
            return {
                'total_checks': 0,
                'total_violations': 0,
                'average_risk': 0,
                'most_common_violations': []
            }
        
        total_checks = len(self.violation_history)
        violation_counts = {}
        total_risk = 0
        
        for record in self.violation_history:
            total_risk += record['risk_score']
            for violation in record['violations']:
                violation_counts[violation] = violation_counts.get(violation, 0) + 1
        
        most_common = sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_checks': total_checks,
            'total_violations': sum(violation_counts.values()),
            'average_risk': total_risk / total_checks,
            'most_common_violations': most_common[:5],
            'violation_rate': sum(1 for r in self.violation_history if r['violations']) / total_checks
        }
