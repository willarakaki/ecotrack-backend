import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.copilot import router as copilot_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ecotrack-ai")

app = FastAPI(
    title="EcoTrack AI Microservice",
    description="Servico de Inteligencia Artificial para Rastreamento ESG de Escopo 3 e Copiloto de Sustentabilidade",
    version="1.0.0"
)

# CORS liberado para o Frontend (React / Next / Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra as rotas da API
app.include_router(copilot_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "UP",
        "service": "ecotrack-ai",
        "guardrails": "ACTIVE"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
