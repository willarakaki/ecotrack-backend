from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Kafka Configuration
    kafka_bootstrap_servers: str = Field(default="localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    kafka_consumer_group: str = Field(default="ai-validation-group", alias="KAFKA_CONSUMER_GROUP")
    kafka_topic_evidence: str = Field(default="ia-evidence-requests-topic", alias="KAFKA_TOPIC_EVIDENCE")
    kafka_topic_results: str = Field(default="ia-evidence-results-topic", alias="KAFKA_TOPIC_RESULTS")

    # API Keys & LLM Routing
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    
    # LangSmith Observability
    langchain_tracing_v2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: str | None = Field(default=None, alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="ecotrack-ai", alias="LANGCHAIN_PROJECT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
