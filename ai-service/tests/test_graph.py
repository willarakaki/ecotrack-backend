from unittest.mock import patch
from app.orchestrator.graph import ai_orchestrator
from app.agents.gatekeeper_node import GatekeeperOutput
from app.agents.nodes import ValidationOutput

@patch("app.agents.gatekeeper_node.structured_gatekeeper")
@patch("app.agents.nodes.structured_llm")
def test_ai_orchestrator_garbage_rejection(mock_llm, mock_gatekeeper):
    """
    Testa se o Gatekeeper barra evidencias obvias de lixo,
    impedindo que o no pesado (Gemini) seja invocado.
    """
    mock_gatekeeper.invoke.return_value = GatekeeperOutput(
        is_valid_format=False,
        reason="Imagem totalmente escura."
    )
    
    initial_state = {
        "action_id": "act_123",
        "action_type": "RECICLAGEM_PLASTICO",
        "evidence_url": "https://dummy.com/foto_preta.jpg"
    }

    final_state = ai_orchestrator.invoke(initial_state)

    assert final_state["verdict"] == "REJECTED"
    assert "Triagem Inicial falhou" in final_state["reasoning"]
    assert final_state["co2_saved"] == 0.0
    
    mock_llm.invoke.assert_not_called()
    mock_gatekeeper.invoke.assert_called_once()

@patch("app.agents.gatekeeper_node.structured_gatekeeper")
@patch("app.agents.nodes.structured_llm")
def test_ai_orchestrator_valid_evidence_approval(mock_llm, mock_gatekeeper):
    """
    Testa o 'Happy Path': A imagem passa pelo Gatekeeper (Ollama)
    e e devidamente avaliada e aprovada pelo Gemini.
    """
    mock_gatekeeper.invoke.return_value = GatekeeperOutput(
        is_valid_format=True,
        reason=""
    )
    
    mock_llm.invoke.return_value = ValidationOutput(
        verdict="APPROVED",
        reasoning="A foto mostra claramente os plasticos na lixeira correta.",
        co2_saved=2.5
    )
    
    initial_state = {
        "action_id": "act_456",
        "action_type": "RECICLAGEM_PLASTICO",
        "evidence_url": "https://dummy.com/reciclagem.jpg"
    }

    final_state = ai_orchestrator.invoke(initial_state)

    assert final_state["verdict"] == "APPROVED"
    assert final_state["co2_saved"] == 2.5
    
    mock_gatekeeper.invoke.assert_called_once()
    mock_llm.invoke.assert_called_once()

@patch("app.agents.gatekeeper_node.structured_gatekeeper")
@patch("app.agents.nodes.structured_llm")
def test_ai_orchestrator_metro_ticket_vlm_audit(mock_llm, mock_gatekeeper):
    """
    Testa a auditoria visual especializada em tickets de metro via VLM.
    Valida se a modalidade e a distancia estimada sao extraidas.
    """
    mock_gatekeeper.invoke.return_value = GatekeeperOutput(
        is_valid_format=True,
        reason=""
    )
    
    mock_llm.invoke.return_value = ValidationOutput(
        verdict="APPROVED",
        reasoning="Bilhete de metro autenticado com estacao e data validas.",
        co2_saved=1.44,
        detected_modality="METRO",
        estimated_distance_km=12.0
    )
    
    initial_state = {
        "action_id": "act_789",
        "action_type": "TRANSPORTE_PUBLICO",
        "evidence_url": "https://s3.amazonaws.com/ecotrack/tickets/metro_ticket.jpg"
    }

    final_state = ai_orchestrator.invoke(initial_state)

    assert final_state["verdict"] == "APPROVED"
    assert final_state["co2_saved"] == 1.44
    assert final_state["detected_modality"] == "METRO"
    assert final_state["estimated_distance_km"] == 12.0
