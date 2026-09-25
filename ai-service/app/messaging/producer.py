import logging
from confluent_kafka import Producer
from app.core.config import settings
from app.messaging.schemas import EvidenceResultEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaProducerService:
    """
    Serviço responsável por despachar a decisão da IA de volta 
    ao barramento do Kafka para que o Spring Boot atualize o banco.
    """
    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': settings.kafka_bootstrap_servers
        })

    def send_result(self, event: EvidenceResultEvent):
        try:
            # Pydantic cuidará de serializar para JSON
            payload = event.model_dump_json()
            
            # Envia utilizando o actionId como chave para garantir ordenação nas partições
            self.producer.produce(
                topic=settings.kafka_topic_results,
                key=event.actionId,
                value=payload
            )
            self.producer.flush()
            logger.info(f"[PRODUCER] Veredito enviado: Topic={settings.kafka_topic_results} | Action={event.actionId} | Verdict={event.verdict}")
        
        except Exception as e:
            logger.error(f"[PRODUCER] Erro crítico ao produzir mensagem para o Kafka: {e}")
