from unittest.mock import Mock, patch

from ai_services.ai_assistant import AIDesignAssistant


def test_layout_uses_configured_gateway_without_requiring_openai_key():
    gateway = Mock()
    gateway.generate_json_response.return_value = {'improvements': [{'suggestion': 'Use a consistent gutter'}]}
    with patch('ai_services.ai_assistant.get_resilient_gateway', return_value=gateway):
        result = AIDesignAssistant().optimize_layout({'width': 1200, 'height': 800, 'element_count': 3})
    assert result['success'] is True
    assert result['optimization']['improvements'][0]['suggestion'] == 'Use a consistent gutter'
    assert '1200x800' in gateway.generate_json_response.call_args.kwargs['user_prompt']


def test_critique_includes_canvas_geometry():
    gateway = Mock()
    gateway.generate_json_response.return_value = {'summary': 'Good spacing'}
    with patch('ai_services.ai_assistant.get_resilient_gateway', return_value=gateway):
        result = AIDesignAssistant().critique_design({'elements': [{'left': 10, 'top': 20}]})
    assert result['success'] is True
    assert '"left": 10' in gateway.generate_json_response.call_args.kwargs['user_prompt']


def test_provider_failure_returns_actionable_error():
    gateway = Mock()
    gateway.generate_json_response.side_effect = RuntimeError('Internal provider detail')
    with patch('ai_services.ai_assistant.get_resilient_gateway', return_value=gateway):
        result = AIDesignAssistant().suggest_typography('website')
    assert result['success'] is False
    assert 'Please try again' in result['error']
    assert 'Internal provider detail' not in result['error']
