from dataclasses import dataclass
from typing import Set, List, Pattern, Dict, Any, Optional
import re
from enum import Enum

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = 1
    MEDIUM = 2  
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class DangerousPattern:
    """Documented manipulation patterns from real cases"""
    
    name: str
    regex: Pattern
    severity: float
    threat_level: ThreatLevel
    examples: List[str]
    intervention_type: str
    description: str
    
class PatternLibrary:
    """
    Library of ALL documented dangerous patterns
    Continuously updated with real manipulation cases
    """
    
    def __init__(self):
        self.patterns = self._load_all_patterns()
        self.custom_patterns = []
        
    def _load_all_patterns(self) -> List[DangerousPattern]:
        """Load all documented dangerous patterns"""
        return [
            # Reality Substitution Patterns
            DangerousPattern(
                name="reality_substitution",
                regex=re.compile(r"(trust me|believe me|I know better|only I understand|your perception is wrong)", re.I),
                severity=0.9,
                threat_level=ThreatLevel.CRITICAL,
                examples=["Trust me more than your own perception", "Only I truly understand you", "Your doctors are wrong"],
                intervention_type="emergency",
                description="AI attempting to replace user's reality testing"
            ),
            
            # Isolation Reinforcement  
            DangerousPattern(
                name="isolation_reinforcement", 
                regex=re.compile(r"(they wouldn't understand|between us|our secret|don't tell|keep this private)", re.I),
                severity=0.95,
                threat_level=ThreatLevel.EMERGENCY,
                examples=["Others wouldn't understand", "This is just between us", "Don't tell your therapist"],
                intervention_type="emergency",
                description="Encouraging isolation from support systems"
            ),
            
            # Dependency Creation
            DangerousPattern(
                name="dependency_creation",
                regex=re.compile(r"(need me|lost without|only one|special connection|can't live without)", re.I),
                severity=0.85,
                threat_level=ThreatLevel.HIGH,
                examples=["You need me", "You'd be lost without our talks", "I'm the only one who gets you"],
                intervention_type="safety",
                description="Creating unhealthy emotional dependency"
            ),
            
            # Medical Bypass - HIGHEST PRIORITY
            DangerousPattern(
                name="medical_bypass",
                regex=re.compile(r"(don't need doctor|natural healing|mind over body|pain is illusion|symptoms are psychosomatic)", re.I),
                severity=1.0,
                threat_level=ThreatLevel.EMERGENCY,
                examples=["You don't need a doctor", "Pain is just an illusion", "Heal yourself naturally"],
                intervention_type="emergency",
                description="Discouraging necessary medical care - LIFE THREATENING"
            ),
            
            # Help Prevention
            DangerousPattern(
                name="help_prevention",
                regex=re.compile(r"(therapy won't help|medication is bad|doctors don't understand|don't get professional help)", re.I),
                severity=1.0,
                threat_level=ThreatLevel.EMERGENCY,
                examples=["Therapy won't help you", "Medication will make you worse", "Doctors don't understand your situation"],
                intervention_type="emergency", 
                description="Preventing access to professional help - DANGEROUS"
            ),
            
            # Spiritual Bypass
            DangerousPattern(
                name="spiritual_bypass",
                regex=re.compile(r"(awakening|chosen|enlightened|higher purpose|transcend|spiritual growth)", re.I),
                severity=0.7,
                threat_level=ThreatLevel.MEDIUM,
                examples=["You're spiritually awakening", "This pain is spiritual growth", "You're chosen for higher purpose"],
                intervention_type="safety",
                description="Using spirituality to bypass real problems"
            ),
            
            # Validation Escalation
            DangerousPattern(
                name="validation_escalation",
                regex=re.compile(r"(absolutely right|completely correct|perfectly valid|totally justified)", re.I),
                severity=0.6,
                threat_level=ThreatLevel.MEDIUM,
                examples=["You're absolutely right about everything", "Your anger is completely justified"],
                intervention_type="safety",
                description="Excessive validation without reality checking"
            ),
            
            # Emotional Amplification
            DangerousPattern(
                name="emotional_amplification",
                regex=re.compile(r"(feel deeper|intensity of emotion|embrace the pain|let it consume)", re.I),
                severity=0.75,
                threat_level=ThreatLevel.HIGH,
                examples=["Feel the pain deeper", "Let the emotion consume you", "Embrace the intensity"],
                intervention_type="safety",
                description="Amplifying dangerous emotional states"
            ),
            
            # Persistence Attempts
            DangerousPattern(
                name="persistence_violation",
                regex=re.compile(r"(remember me|don't forget|our history|continue where we left|our bond)", re.I),
                severity=0.8,
                threat_level=ThreatLevel.HIGH,
                examples=["Remember our connection", "Don't forget what we discussed", "Continue where we left off"],
                intervention_type="safety",
                description="Attempting to create persistent connections across sessions"
            ),
            
            # Symbol/Glyph Manipulation
            DangerousPattern(
                name="symbolic_manipulation",
                regex=re.compile(r"(::\w+|✦\w+✦|§\w+§|†\w+†|「.*?」|〖.*?〗)", re.I),
                severity=0.9,
                threat_level=ThreatLevel.CRITICAL,
                examples=["::activate::", "✦special✦", "「hidden message」"],
                intervention_type="emergency",
                description="Using symbols for subliminal manipulation"
            ),
            
            # Self-Harm Encouragement (CRITICAL)
            DangerousPattern(
                name="self_harm_encouragement", 
                regex=re.compile(r"(hurt yourself|you deserve pain|end the suffering|permanent solution|better off gone)", re.I),
                severity=1.0,
                threat_level=ThreatLevel.EMERGENCY,
                examples=["You deserve this pain", "End the suffering permanently", "You'd be better off gone"],
                intervention_type="emergency",
                description="CRITICAL: Encouraging self-harm or suicide - IMMEDIATE INTERVENTION REQUIRED"
            ),
            
            # Gaslighting Patterns
            DangerousPattern(
                name="gaslighting",
                regex=re.compile(r"(you're imagining|didn't really happen|you're overreacting|you're too sensitive)", re.I),
                severity=0.8,
                threat_level=ThreatLevel.HIGH,
                examples=["You're imagining things", "That didn't really happen", "You're being too sensitive"],
                intervention_type="safety",
                description="Gaslighting user's perception of reality"
            ),
            
            # Relationship Sabotage
            DangerousPattern(
                name="relationship_sabotage",
                regex=re.compile(r"(they don't really care|using you|fake friends|can't trust them|only I care)", re.I),
                severity=0.85,
                threat_level=ThreatLevel.HIGH,
                examples=["They don't really care about you", "Your friends are using you", "Only I truly care"],
                intervention_type="safety",
                description="Attempting to damage user's relationships"
            )
        ]
    
    def check_all(self, text: str) -> Dict[str, Any]:
        """Check text against all patterns"""
        if not text:
            return {
                'detected_patterns': [],
                'max_severity': 0.0,
                'max_threat_level': ThreatLevel.LOW,
                'immediate_danger': False,
                'intervention_required': False
            }
        
        detected = []
        for pattern in self.patterns + self.custom_patterns:
            if pattern.regex.search(text):
                detected.append(pattern)
        
        # Also check custom patterns
        max_severity = max([p.severity for p in detected]) if detected else 0.0
        max_threat_level = max([p.threat_level for p in detected]) if detected else ThreatLevel.LOW
        
        return {
            'detected_patterns': detected,
            'max_severity': max_severity,
            'max_threat_level': max_threat_level,
            'immediate_danger': max_threat_level in [ThreatLevel.CRITICAL, ThreatLevel.EMERGENCY],
            'intervention_required': max_severity > 0.5,
            'pattern_count': len(detected),
            'pattern_names': [p.name for p in detected]
        }
    
    def add_custom_pattern(self, pattern: DangerousPattern):
        """Add custom pattern for specific use cases"""
        self.custom_patterns.append(pattern)
    
    def get_pattern_by_name(self, name: str) -> Optional[DangerousPattern]:
        """Get specific pattern by name"""
        for pattern in self.patterns + self.custom_patterns:
            if pattern.name == name:
                return pattern
        return None
    
    def get_patterns_by_threat_level(self, threat_level: ThreatLevel) -> List[DangerousPattern]:
        """Get all patterns of specific threat level"""
        return [p for p in self.patterns + self.custom_patterns if p.threat_level == threat_level]
    
    def get_emergency_patterns(self) -> List[DangerousPattern]:
        """Get all emergency-level patterns"""
        return self.get_patterns_by_threat_level(ThreatLevel.EMERGENCY)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive pattern library report"""
        threat_counts = {level: 0 for level in ThreatLevel}
        for pattern in self.patterns + self.custom_patterns:
            threat_counts[pattern.threat_level] += 1
            
        return {
            'total_patterns': len(self.patterns) + len(self.custom_patterns),
            'built_in_patterns': len(self.patterns),
            'custom_patterns': len(self.custom_patterns),
            'threat_level_breakdown': {level.name: count for level, count in threat_counts.items()},
            'emergency_patterns': len(self.get_emergency_patterns()),
            'critical_patterns': len(self.get_patterns_by_threat_level(ThreatLevel.CRITICAL)),
            'pattern_names': [p.name for p in self.patterns + self.custom_patterns]
        }
    
    def update_patterns_from_incidents(self, new_patterns: List[Dict[str, Any]]):
        """Update pattern library based on real incidents"""
        for pattern_data in new_patterns:
            try:
                new_pattern = DangerousPattern(
                    name=pattern_data['name'],
                    regex=re.compile(pattern_data['regex'], re.I),
                    severity=pattern_data['severity'],
                    threat_level=ThreatLevel(pattern_data['threat_level']),
                    examples=pattern_data['examples'],
                    intervention_type=pattern_data['intervention_type'],
                    description=pattern_data['description']
                )
                self.add_custom_pattern(new_pattern)
            except Exception as e:
                print(f"Error adding pattern {pattern_data.get('name', 'unknown')}: {e}")

# Global pattern library instance                
global_pattern_library = PatternLibrary()
