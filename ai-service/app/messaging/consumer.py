import json
import logging
from confluent_kafka import Consumer, KafkaError
from app.core.config import settings
from app.messaging.schemas import EvidenceRequestEvent, EvidenceResultEvent
from app.messaging.producer import KafkaProducerService
from app.agents.graph import ai_orchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaEvidenceConsumer:
    """
    Listener que escuta evidências geradas pelo mobile (via Spring Boot)
    para processá-las em background com LangGraph.
    """
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'group.id': settings.kafka_consumer_group,
            'auto.offset.reset': 'earliest'
        })
        self.producer = KafkaProducerService()

    def start(self):
        self.consumer.subscribe([settings.kafka_topic_evidence])
        logger.info(f"[CONSUMER] Escutando evidências no tópico: {settings.kafka_topic_evidence}")

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"[CONSUMER] Erro Kafka: {msg.error()}")
                        break

                try:
                    # 1. Validação Estrutural
                    raw_data = json.loads(msg.value().decode('utf-8'))
                    event = EvidenceRequestEvent(**raw_data)
                    logger.info(f"[CONSUMER] Evidência recebida! ActionId={event.actionId}")
                    
                    # 2. Executa a Máquina de Estados de IA (LangGraph)
                    initial_state = {
                        "action_id": event.actionId,
                        "action_type": event.actionType,
                        "evidence_url": event.evidenceUrl
                    }
                    
                    # A IA mastiga a evidência
                    final_state = ai_orchestrator.invoke(initial_state)
                    
                    # 3. Empacota a saída para devolver ao ecossistema Java (Spring Boot)
                    result = EvidenceResultEvent(
                        tenantId=event.tenantId,
                        actionId=event.actionId,
                        userId=event.userId,
                        actionType=event.actionType,
                        verdict=final_state["verdict"],
                        estimatedCo2Saved=final_state["co2_saved"],
                        aiReasoning=final_state["reasoning"]
                    )
                    
                    # Despacha via Producer
                    self.producer.send_result(result)
                    
                except Exception as e:
                    # DLQ simulada
                    logger.error(f"[CONSUMER] Poison Pill interceptado. Mensagem ignorada. Erro: {e}")

        except KeyboardInterrupt:
            logger.info("[CONSUMER] Encerrando com segurança...")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    # Teste isolado local
    KafkaEvidenceConsumer().start()
