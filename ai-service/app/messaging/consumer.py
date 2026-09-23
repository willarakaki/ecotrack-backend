import json
import logging
from confluent_kafka import Consumer, KafkaError
from app.core.config import settings
from app.messaging.schemas import EvidenceRequestEvent, EvidenceResultEvent
from app.messaging.producer import KafkaProducerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaEvidenceConsumer:
    """
    Listener que escuta evidências geradas pelo mobile (via Spring Boot)
    para processá-las em background com LangGraph.
    """
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': settings.KAFKA_CONSUMER_GROUP,
            'auto.offset.reset': 'earliest'
        })
        self.producer = KafkaProducerService()

    def start(self):
        self.consumer.subscribe([settings.KAFKA_TOPIC_EVIDENCE])
        logger.info(f"[CONSUMER] Escutando evidências no tópico: {settings.KAFKA_TOPIC_EVIDENCE}")

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
                    # Desserializa evento (Trava Pydantic)
                    raw_data = json.loads(msg.value().decode('utf-8'))
                    event = EvidenceRequestEvent(**raw_data)
                    logger.info(f"[CONSUMER] Evidência recebida! ActionId={event.actionId}, Tipo={event.actionType}")
                    
                    # --------------------------------------------------------
                    # TODO (Sprint 3): Integrar chamada real do LangGraph aqui!
                    # --------------------------------------------------------
                    
                    # Mock de devolução temporária para o Java
                    result = EvidenceResultEvent(
                        tenantId=event.tenantId,
                        actionId=event.actionId,
                        userId=event.userId,
                        actionType=event.actionType,
                        verdict="APPROVED", # Mock
                        estimatedCo2Saved=15.0, # Mock de calculo de IA
                        aiReasoning="[MOCK] O LangGraph aprovou a foto enviada."
                    )
                    
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
