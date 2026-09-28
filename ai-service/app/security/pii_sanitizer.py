import logging
import re
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine

logger = logging.getLogger(__name__)

class PIISanitizer:
    """
    Camada de Higienizacao de Dados Pessoais (PII) baseada no Microsoft Presidio.
    Garante conformidade com a LGPD e GDPR antes de qualquer dado ser transmitido a LLMs.
    """

    def __init__(self):
        try:
            self.analyzer = AnalyzerEngine()
            self._register_brazilian_recognizers()
        except Exception as e:
            logger.warning(f"[PIISanitizer] Inicializacao avancada do Presidio falhou, usando modo defensivo: {e}")
            self.analyzer = None

        self.anonymizer = AnonymizerEngine()

    def _register_brazilian_recognizers(self):
        """Registra reconhecedores de padroes para documentos brasileiros (CPF, CNPJ)."""
        # Reconhecedor de CPF (com ou sem pontuacao)
        cpf_pattern = Pattern(
            name="cpf_pattern",
            regex=r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
            score=0.85
        )
        cpf_recognizer = PatternRecognizer(
            supported_entity="BR_CPF",
            patterns=[cpf_pattern]
        )
        self.analyzer.registry.add_recognizer(cpf_recognizer)

        # Reconhecedor de CNPJ
        cnpj_pattern = Pattern(
            name="cnpj_pattern",
            regex=r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
            score=0.85
        )
        cnpj_recognizer = PatternRecognizer(
            supported_entity="BR_CNPJ",
            patterns=[cnpj_pattern]
        )
        self.analyzer.registry.add_recognizer(cnpj_recognizer)

    def sanitize(self, text: str, language: str = "en") -> str:
        """
        Substitui informacoes sensiveis (CPF, Email, Telefone, etc) por marcadores anonimizados.
        Ex: 'Meu CPF e 123.456.789-00' -> 'Meu CPF e <BR_CPF>'
        """
        if not text or not text.strip():
            return text

        if not self.analyzer:
            # Fallback defensivo com Regex para CPF e Email se Presidio nao carregar
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
            logger.error(f"[PIISanitizer] Erro durante anonimizacao com Presidio: {e}")
            # Fallback defensivo regex
            fallback_text = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "<BR_CPF>", text)
            fallback_text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "<EMAIL_ADDRESS>", fallback_text)
            return fallback_text

pii_sanitizer = PIISanitizer()
