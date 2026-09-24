from langgraph.graph import StateGraph, END
from app.agents.state import EvidenceValidationState
from app.agents.nodes import validate_evidence_node
from app.agents.gatekeeper_node import gatekeeper_node

def route_after_gatekeeper(state: EvidenceValidationState) -> str:
    """
    Roteador Condicional.
    Se o gatekeeper cravou um verdict (ex: REJECTED por ser lixo), encerra o grafo.
    Caso contrário, envia para a auditoria profunda da LLM (Gemini).
    """
    if state.get("verdict"):
        return "end"
    return "auditor_ia"

# Inicializa o compilador do Grafo informando o Schema (State)
workflow = StateGraph(EvidenceValidationState)

# Adiciona os nós
workflow.add_node("gatekeeper", gatekeeper_node)
workflow.add_node("auditor_ia", validate_evidence_node)

# Define o ponto de entrada (Start)
workflow.set_entry_point("gatekeeper")

# Aresta Condicional: Saindo do gatekeeper, ou vai pro fim, ou vai pro auditor_ia
workflow.add_conditional_edges(
    "gatekeeper",
    route_after_gatekeeper,
    {
        "end": END,
        "auditor_ia": "auditor_ia"
    }
)

# O auditor_ia sempre vai pro fim quando termina
workflow.add_edge("auditor_ia", END)

# Compila para um aplicativo executável
ai_orchestrator = workflow.compile()

