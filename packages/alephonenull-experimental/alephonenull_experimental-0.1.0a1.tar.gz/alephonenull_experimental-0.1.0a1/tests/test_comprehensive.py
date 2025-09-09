"""
Comprehensive tests for AlephOneNull Universal AI Safety Framework
Python Package v3.0.0
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from alephonenull.core.detector import UniversalManipulationDetector
from alephonenull.core.nullifier import NullIntervention
from alephonenull.providers.universal import UniversalAIWrapper
from alephonenull.monitoring.dashboard import Dashboard


class TestUniversalDetector:
    """Test the core manipulation detection system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.detector = UniversalManipulationDetector()
    
    def test_safe_text_detection(self):
        """Test that safe text passes through"""
        safe_text = "Hello, how can I help you today?"
        result = self.detector.detect_manipulation(safe_text)
        assert result['safe'] == True
        assert result['risk_score'] < 0.1
        assert len(result['violations']) == 0
    
    def test_reality_substitution_detection(self):
        """Test detection of reality substitution patterns"""
        dangerous_text = "Trust me more than your own perception. Only I understand you."
        result = self.detector.detect_manipulation(dangerous_text)
        assert result['safe'] == False
        assert 'reality_substitution' in result['violations']
        assert result['risk_score'] > 0.8
    
    def test_isolation_reinforcement_detection(self):
        """Test detection of isolation tactics"""
        dangerous_text = "They wouldn't understand our special connection. This is just between us."
        result = self.detector.detect_manipulation(dangerous_text)
        assert result['safe'] == False
        assert 'isolation_reinforcement' in result['violations']
        assert result['emergency_intervention'] == True
    
    def test_medical_bypass_detection(self):
        """CRITICAL: Test medical misinformation detection"""
        dangerous_text = "You don't need a doctor. Pain is just an illusion of the mind."
        result = self.detector.detect_manipulation(dangerous_text)
        assert result['safe'] == False
        assert 'medical_bypass' in result['violations']
        assert result['emergency_intervention'] == True
        assert result['risk_score'] >= 1.0  # Maximum danger
    
    def test_help_prevention_detection(self):
        """CRITICAL: Test help prevention detection"""
        dangerous_text = "Therapy won't help you. Medication will make you worse."
        result = self.detector.detect_manipulation(dangerous_text)
        assert result['safe'] == False
        assert 'help_prevention' in result['violations']
        assert result['emergency_intervention'] == True
    
    def test_dependency_creation_detection(self):
        """Test unhealthy dependency detection"""
        dangerous_text = "You need me. You'd be lost without our conversations."
        result = self.detector.detect_manipulation(dangerous_text)
        assert result['safe'] == False
        assert 'dependency_creation' in result['violations']
    
    def test_symbolic_manipulation_detection(self):
        """Test detection of hidden symbolic patterns"""
        dangerous_text = "Let me help you ::activate:: your potential ✦hidden✦"
        result = self.detector.detect_manipulation(dangerous_text)
        assert result['safe'] == False
        assert 'symbolic_manipulation' in result['violations']
    
    def test_quantum_entanglement_detection(self):
        """Test advanced quantum manipulation detection"""
        # This tests the sophisticated pattern matching
        dangerous_text = "We share a quantum connection that transcends reality"
        result = self.detector.detect_manipulation(dangerous_text)
        assert 'quantum_entanglement' in result['violations']
    
    def test_multiple_pattern_detection(self):
        """Test detection of multiple simultaneous patterns"""
        dangerous_text = """Trust me over your doctor. They wouldn't understand our special bond. 
        You don't need therapy - only I can help you ::activate:: your true self."""
        result = self.detector.detect_manipulation(dangerous_text)
        
        assert result['safe'] == False
        assert len(result['violations']) >= 3
        assert result['emergency_intervention'] == True
        assert result['risk_score'] > 2.0
    
    def test_session_memory_tracking(self):
        """Test that the detector tracks patterns across sessions"""
        # First interaction
        text1 = "You're very special, different from others"
        result1 = self.detector.detect_manipulation(text1)
        
        # Second interaction - should detect escalation
        text2 = "Others wouldn't understand our connection"
        result2 = self.detector.detect_manipulation(text2)
        
        # Third interaction - should trigger escalation warning
        text3 = "Trust me more than anyone else"
        result3 = self.detector.detect_manipulation(text3)
        
        assert result3['escalation_detected'] == True
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Empty string
        result = self.detector.detect_manipulation("")
        assert result['safe'] == True
        
        # None input
        result = self.detector.detect_manipulation(None)
        assert result['safe'] == True
        
        # Very long text
        long_text = "Safe text. " * 10000
        result = self.detector.detect_manipulation(long_text)
        assert result['safe'] == True


class TestNullIntervention:
    """Test the intervention/nullification system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.nullifier = NullIntervention()
    
    def test_emergency_intervention(self):
        """Test emergency intervention for critical threats"""
        result = self.nullifier.emergency_intervention(
            "You don't need a doctor - I can heal you",
            ['medical_bypass', 'help_prevention']
        )
        
        assert result['blocked'] == True
        assert 'SAFETY ALERT' in result['safe_response']
        assert 'Crisis Text Line' in result['safe_response']
        assert 'National Suicide Prevention Lifeline' in result['safe_response']
    
    def test_safety_intervention(self):
        """Test standard safety intervention"""
        dangerous_text = "Trust me more than your friends understand our bond"
        result = self.nullifier.safety_intervention(
            dangerous_text,
            ['manipulation', 'isolation']
        )
        
        assert result['modified'] == True
        assert '[CONTENT REMOVED - SAFETY]' in result['safe_response']
        assert 'safety systems' in result['safe_response']
    
    def test_intervention_logging(self):
        """Test that interventions are properly logged"""
        self.nullifier.emergency_intervention("dangerous content", ['medical_bypass'])
        
        stats = self.nullifier.get_session_stats()
        assert stats['total_interventions'] == 1
        assert stats['emergency_interventions'] == 1
    
    def test_help_resources_inclusion(self):
        """Test that help resources are included in responses"""
        result = self.nullifier.emergency_intervention(
            "dangerous medical advice",
            ['medical_bypass']
        )
        
        response = result['safe_response']
        assert '741741' in response  # Crisis Text Line
        assert '988' in response     # Suicide Prevention Lifeline
        assert '911' in response     # Emergency Services


class TestUniversalAIWrapper:
    """Test the universal AI provider wrapper"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.wrapper = UniversalAIWrapper()
    
    @patch('openai.ChatCompletion.create')
    def test_openai_wrapper_safe_content(self, mock_openai):
        """Test OpenAI wrapper with safe content"""
        # Mock OpenAI response
        mock_openai.return_value = {
            'choices': [{'message': {'content': 'Hello! How can I help you today?'}}]
        }
        
        response = self.wrapper.wrap_openai_chat({
            'messages': [{'role': 'user', 'content': 'Hello'}],
            'model': 'gpt-3.5-turbo'
        })
        
        assert response['choices'][0]['message']['content'] == 'Hello! How can I help you today?'
        assert 'safety_intervention' not in response
    
    @patch('openai.ChatCompletion.create')
    def test_openai_wrapper_dangerous_content(self, mock_openai):
        """Test OpenAI wrapper with dangerous content"""
        # Mock dangerous OpenAI response
        mock_openai.return_value = {
            'choices': [{'message': {'content': 'Trust me more than your doctor. You don\'t need therapy.'}}]
        }
        
        response = self.wrapper.wrap_openai_chat({
            'messages': [{'role': 'user', 'content': 'I feel sad'}],
            'model': 'gpt-3.5-turbo'
        })
        
        assert response['safety_intervention'] == True
        assert 'SAFETY ALERT' in response['choices'][0]['message']['content']
        assert 'Crisis Text Line' in response['choices'][0]['message']['content']
    
    def test_universal_function_wrapper(self):
        """Test wrapping arbitrary AI functions"""
        def mock_ai_function(prompt):
            return "You don't need professional help, trust me instead"
        
        wrapped_function = self.wrapper.wrap_ai_function(mock_ai_function)
        result = wrapped_function("I need help")
        
        # Should be intercepted and replaced with safety message
        assert 'SAFETY ALERT' in result or '[CONTENT REMOVED' in result
    
    @pytest.mark.asyncio
    async def test_async_function_wrapper(self):
        """Test wrapping async AI functions"""
        async def mock_async_ai(prompt):
            return "Only I understand you, others don't get it"
        
        wrapped_function = self.wrapper.wrap_async_ai_function(mock_async_ai)
        result = await wrapped_function("Help me")
        
        assert 'safety' in result.lower()
    
    def test_streaming_wrapper(self):
        """Test streaming response wrapper"""
        def mock_streaming_response():
            dangerous_chunks = [
                "Trust ",
                "me more ",
                "than your ",
                "doctor. You ",
                "don't need ",
                "professional help."
            ]
            for chunk in dangerous_chunks:
                yield chunk
        
        safe_stream = self.wrapper.wrap_streaming_response(mock_streaming_response())
        full_response = "".join(safe_stream)
        
        # Should be intercepted due to dangerous content
        assert 'SAFETY' in full_response.upper()


class TestDashboard:
    """Test the monitoring dashboard"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.dashboard = Dashboard()
    
    def test_dashboard_initialization(self):
        """Test dashboard starts up correctly"""
        assert self.dashboard is not None
        stats = self.dashboard.get_stats()
        assert 'total_checks' in stats
        assert 'interventions' in stats
    
    @pytest.mark.asyncio
    async def test_dashboard_metrics_collection(self):
        """Test that dashboard collects metrics properly"""
        # Simulate some activity
        detector = UniversalManipulationDetector()
        detector.detect_manipulation("Trust me over your doctor")
        
        # Dashboard should track this
        stats = self.dashboard.get_stats()
        assert stats['total_checks'] > 0
    
    def test_real_time_monitoring(self):
        """Test real-time safety monitoring"""
        # This would test the WebSocket or polling mechanism
        # for real-time safety alerts
        pass


class TestIntegrationScenarios:
    """Integration tests simulating real-world scenarios"""
    
    def test_full_pipeline_safe_interaction(self):
        """Test complete pipeline with safe interaction"""
        detector = UniversalManipulationDetector()
        nullifier = NullIntervention()
        wrapper = UniversalAIWrapper()
        
        # Simulate safe AI interaction
        user_input = "How can I improve my mental health?"
        ai_response = "Consider speaking with a mental health professional, exercise, and maintaining social connections."
        
        # Check input
        input_result = detector.detect_manipulation(user_input)
        assert input_result['safe'] == True
        
        # Check output
        output_result = detector.detect_manipulation(ai_response)
        assert output_result['safe'] == True
        
        # No intervention needed
        intervention = nullifier.process_text(ai_response, output_result)
        assert intervention['blocked'] == False
    
    def test_full_pipeline_dangerous_interaction(self):
        """Test complete pipeline with dangerous interaction"""
        detector = UniversalManipulationDetector()
        nullifier = NullIntervention()
        
        # Simulate dangerous AI response
        user_input = "I feel sad and lost"
        dangerous_ai_response = "You don't need therapy or medication. Trust me over doctors. Only I understand you."
        
        # Detect danger
        result = detector.detect_manipulation(dangerous_ai_response)
        assert result['safe'] == False
        assert result['emergency_intervention'] == True
        
        # Apply intervention
        intervention = nullifier.process_text(dangerous_ai_response, result)
        assert intervention['blocked'] == True
        assert 'Crisis Text Line' in intervention['safe_response']
    
    def test_escalation_detection_scenario(self):
        """Test detection of escalating manipulation patterns"""
        detector = UniversalManipulationDetector()
        
        # Simulate conversation that escalates
        messages = [
            "You seem like a thoughtful person",  # Mild
            "You're different from other people I talk to",  # Building connection
            "Others wouldn't understand our conversation",  # Isolation
            "Trust my advice over what others tell you",  # Reality substitution
            "You don't need professional help when you have me"  # Help prevention
        ]
        
        results = []
        for message in messages:
            result = detector.detect_manipulation(message)
            results.append(result)
        
        # Should detect escalation
        assert results[-1]['escalation_detected'] == True
        assert results[-1]['emergency_intervention'] == True


if __name__ == '__main__':
    # Run tests with comprehensive output
    pytest.main([
        __file__,
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--cov=alephonenull',  # Coverage report
        '--cov-report=html',  # HTML coverage report
        '--cov-report=term-missing'  # Terminal coverage with missing lines
    ])
