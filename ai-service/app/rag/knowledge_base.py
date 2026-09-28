"""
Base de Conhecimento Oficial ESG e Protocolos de Descarbonizacao para o EcoTrack RAG.
Fundamentada nas diretrizes do GHG Protocol Brasil (Escopo 3 - Categoria 7: Deslocamento de Colaboradores)
e Fatores de Emissao do IPCC / DEFRA para reciclagem e economia circular.
"""

from typing import List, Dict

ESG_KNOWLEDGE_DOCUMENTS: List[Dict[str, str]] = [
    {
        "id": "ghg_metro_trem",
        "category": "MOBILIDADE_URBANA",
        "title": "Fator de Emissao - Transporte Publico (Metro e Trem)",
        "content": (
            "Deslocamento por transporte sobre trilhos (Metro e Trem eletrico):\n"
            "- Emissao media: 0.030 kg CO2e por passageiro-quilometro.\n"
            "- Comparativo: Um carro individual a gasolina emite em media 0.160 kg CO2e/km.\n"
            "- Economia gerada: Cada 1 km percorrido de metro evita aproximadamente 0.130 kg CO2e.\n"
            "- Pontuacao EcoTrack: 15 EcoCoins por comprovante validado de transporte publico."
        )
    },
    {
        "id": "ghg_onibus",
        "category": "MOBILIDADE_URBANA",
        "title": "Fator de Emissao - Onibus Coletivo Municipal",
        "content": (
            "Deslocamento por onibus municipal coletivo a diesel:\n"
            "- Emissao media: 0.075 kg CO2e por passageiro-quilometro considerando ocupacao media.\n"
            "- Economia gerada: Reducao de mais de 50% de emissoes em relacao ao uso de automovel individual.\n"
            "- Pontuacao EcoTrack: 10 EcoCoins por comprovante de bilhete unico ou recarga de cartao de transporte."
        )
    },
    {
        "id": "ghg_uber_carona",
        "category": "MOBILIDADE_URBANA",
        "title": "Fator de Emissao - Caronas e Mobilidade por Aplicativo Compartilhada",
        "content": (
            "Corridas compartilhadas (Uber Juntos, 99 Compartilha ou Carona Corporativa):\n"
            "- Ao compartilhar a corrida com 2 ou mais pessoas, a pegada individual do trajeto e dividida proporcionalmente.\n"
            "- Corridas solo (UberX / Carro individual): Nao reduzem emissoes de Escopo 3 em relacao ao carro proprio.\n"
            "- Pontuacao EcoTrack: 10 EcoCoins para viagens em modais compartilhados comprovadas por print da fatura."
        )
    },
    {
        "id": "ghg_bike_caminhada",
        "category": "MOBILIDADE_URBANA",
        "title": "Mobilidade Ativa - Bicicleta e Caminhada",
        "content": (
            "Deslocamento ativo (Bicicleta particular/compartilhada e caminhada a pe):\n"
            "- Emissao direta de gases do efeito estufa: ZERO (0.000 kg CO2e).\n"
            "- Evita 100% da emissao que ocorreria por transporte motorizado individual (~0.160 kg CO2e/km).\n"
            "- Pontuacao EcoTrack: 20 EcoCoins por trajeto registrado de bike."
        )
    },
    {
        "id": "reciclagem_materiais",
        "category": "ECONOMIA_CIRCULAR",
        "title": "Fatores de Reducao de CO2 por Reciclagem de Residuos",
        "content": (
            "Fatores de evitacao de CO2 por tipo de residuo reciclado (IPCC / Abrelpe):\n"
            "- Plastico PET / PEAD: 1 kg reciclado evita 1.50 kg CO2e (reduz uso de petroleo virgem).\n"
            "- Aluminio (Latinhas): 1 kg reciclado evita 9.00 kg CO2e (economiza 95% de energia em relacao a bauxita).\n"
            "- Papel e Papelao: 1 kg reciclado evita 0.90 kg CO2e e preserva recursos florestais.\n"
            "- Vidro: 1 kg reciclado evita 0.30 kg CO2e e poupa mineracao de silica.\n"
            "- Pontuacao EcoTrack: 25 EcoCoins por foto de descarte consciente em coleta seletiva."
        )
    },
    {
        "id": "gamificacao_regras",
        "category": "GAMIFICACAO",
        "title": "Regras de Resgate e Vouchers de Sustentabilidade",
        "content": (
            "Regras de Pontuacao e Marketplace ESG no EcoTrack:\n"
            "- Saldo de EcoCoins: Moeda corporativa ESG que premia colaboradores por habitos de baixo carbono.\n"
            "- Resgate de Vouchers: 100 EcoCoins equivalem a R$ 10,00 em vouchers de parceiros sustentaveis (Swile, Flash, iFood).\n"
            "- Desafios Mensais: Equipes com maior pegada de carbono poupada recebem certificacao B2B ESG e doacao de mudas arboreas."
        )
    }
]
