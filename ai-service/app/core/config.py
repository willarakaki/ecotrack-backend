from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP: str = "ai-validation-group"
    KAFKA_TOPIC_EVIDENCE: str = "ia-evidence-requests-topic"
    KAFKA_TOPIC_RESULTS: str = "ia-evidence-results-topic"

    # API Keys
    GEMINI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
