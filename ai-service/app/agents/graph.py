from langgraph.graph import StateGraph, END
from app.agents.state import EvidenceValidationState
from app.agents.nodes import validate_evidence_node

# Inicializa o compilador do Grafo informando o Schema (State)
workflow = StateGraph(EvidenceValidationState)

# Adiciona nosso nó Validador (Poderíamos ter múltiplos: Node A -> Node B)
workflow.add_node("auditor_ia", validate_evidence_node)

# Define o ponto de entrada (Start)
workflow.set_entry_point("auditor_ia")

# Define o fim do fluxo (quando terminar o auditor_ia, vai pro END)
workflow.add_edge("auditor_ia", END)

# Compila para um aplicativo executável
ai_orchestrator = workflow.compile()
