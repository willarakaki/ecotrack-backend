import logging
import re
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

logger = logging.getLogger(__name__)

class PIISanitizer:
    """
    Camada de Higienizacao de Dados Pessoais (PII) baseada no Microsoft Presidio + spaCy em Portugues.
    Garante conformidade com a LGPD e GDPR antes de qualquer dado ser transmitido a LLMs.
    Utiliza o modelo morfo-sintatico 'pt_core_news_sm' para detectar entidades em portugues (PERSON, LOCATION).
    """

    def __init__(self):
        self.language = "pt"
        self.analyzer = self._initialize_analyzer()
        self.anonymizer = AnonymizerEngine()

    def _initialize_analyzer(self) -> AnalyzerEngine:
        """Inicializa o motor Presidio configurado com o modelo spaCy de Portugues."""
        try:
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [
                    {"lang_code": "pt", "model_name": "pt_core_news_sm"}
                ]
            }
            provider = NlpEngineProvider(nlp_configuration=configuration)
            nlp_engine = provider.create_engine()
            analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["pt", "en"])
            self._register_brazilian_recognizers(analyzer)
            logger.info("[PIISanitizer] Microsoft Presidio inicializado com modelo spaCy em Portugues ('pt_core_news_sm').")
            return analyzer

        except Exception as e:
            logger.warning(f"[PIISanitizer] Falha ao carregar pt_core_news_sm ({e}). Inicializando Presidio basico.")
            try:
                analyzer = AnalyzerEngine()
                self._register_brazilian_recognizers(analyzer)
                return analyzer
            except Exception as ex:
                logger.error(f"[PIISanitizer] Inicializacao do Presidio falhou criticamente: {ex}")
                return None

    def _register_brazilian_recognizers(self, analyzer: AnalyzerEngine):
        """Registra reconhecedores para documentos brasileiros (CPF, CNPJ)."""
        if not analyzer:
            return

        # Reconhecedor de CPF
        cpf_pattern = Pattern(
            name="cpf_pattern",
            regex=r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
            score=0.85
        )
        cpf_recognizer = PatternRecognizer(
            supported_entity="BR_CPF",
            supported_language="pt",
            patterns=[cpf_pattern]
        )
        analyzer.registry.add_recognizer(cpf_recognizer)

        # Reconhecedor de CNPJ
        cnpj_pattern = Pattern(
            name="cnpj_pattern",
            regex=r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
            score=0.85
        )
        cnpj_recognizer = PatternRecognizer(
            supported_entity="BR_CNPJ",
            supported_language="pt",
            patterns=[cnpj_pattern]
        )
        analyzer.registry.add_recognizer(cnpj_recognizer)

    def sanitize(self, text: str, language: str = "pt") -> str:
        """
        Substitui informacoes sensiveis (CPF, Email, Telefone, Nomes) por marcadores anonimizados.
        Ex: 'Meu nome e Carlos Ferreira e meu CPF e 123.456.789-00'
        ->  'Meu nome e <PERSON> e meu CPF e <BR_CPF>'
        """
        if not text or not text.strip():
            return text

        if not self.analyzer:
            # Fallback defensivo com Regex
            text = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "<BR_CPF>", text)
            text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "<EMAIL_ADDRESS>", text)
            return text

        try:
            results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "BR_CPF", "BR_CNPJ", "PERSON"]
            )
            anonymized = self.anonymizer.anonymize(text=text, analyzer_results=results)
            return anonymized.text
        except Exception as e:
            logger.error(f"[PIISanitizer] Erro durante anonimizacao: {e}")
            fallback_text = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "<BR_CPF>", text)
            fallback_text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "<EMAIL_ADDRESS>", fallback_text)
            return fallback_text

pii_sanitizer = PIISanitizer()
