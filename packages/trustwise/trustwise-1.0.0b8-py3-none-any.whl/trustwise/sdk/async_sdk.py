import logging

from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.config import TrustwiseConfig
from trustwise.sdk.metrics.v3.metrics.async_ import (
    AdherenceMetricAsync,
    AnswerRelevancyMetricAsync,
    CarbonMetricAsync,
    ClarityMetricAsync,
    CompletionMetricAsync,
    ContextRelevancyMetricAsync,
    CostMetricAsync,
    FaithfulnessMetricAsync,
    FormalityMetricAsync,
    HelpfulnessMetricAsync,
    PIIMetricAsync,
    PromptInjectionMetricAsync,
    RefusalMetricAsync,
    SensitivityMetricAsync,
    SimplicityMetricAsync,
    StabilityMetricAsync,
    SummarizationMetricAsync,
    ToneMetricAsync,
    ToxicityMetricAsync,
)

logger = logging.getLogger(__name__)

class MetricsV3Async:
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.faithfulness = FaithfulnessMetricAsync(client)
        self.answer_relevancy = AnswerRelevancyMetricAsync(client)
        self.context_relevancy = ContextRelevancyMetricAsync(client)
        self.summarization = SummarizationMetricAsync(client)
        self.pii = PIIMetricAsync(client)
        self.prompt_injection = PromptInjectionMetricAsync(client)
        self.clarity = ClarityMetricAsync(client)
        self.formality = FormalityMetricAsync(client)
        self.helpfulness = HelpfulnessMetricAsync(client)
        self.simplicity = SimplicityMetricAsync(client)
        self.tone = ToneMetricAsync(client)
        self.toxicity = ToxicityMetricAsync(client)
        self.sensitivity = SensitivityMetricAsync(client)
        self.cost = CostMetricAsync(client)
        self.carbon = CarbonMetricAsync(client)
        self.stability = StabilityMetricAsync(client)
        self.refusal = RefusalMetricAsync(client)
        self.completion = CompletionMetricAsync(client)
        self.adherence = AdherenceMetricAsync(client)

class MetricsAsync:
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.v3 = MetricsV3Async(client)
        self.faithfulness = self.v3.faithfulness
        self.answer_relevancy = self.v3.answer_relevancy
        self.context_relevancy = self.v3.context_relevancy
        self.summarization = self.v3.summarization
        self.pii = self.v3.pii
        self.prompt_injection = self.v3.prompt_injection
        self.clarity = self.v3.clarity
        self.formality = self.v3.formality
        self.helpfulness = self.v3.helpfulness
        self.simplicity = self.v3.simplicity
        self.tone = self.v3.tone
        self.toxicity = self.v3.toxicity
        self.sensitivity = self.v3.sensitivity
        self.cost = self.v3.cost
        self.carbon = self.v3.carbon
        self.stability = self.v3.stability
        self.refusal = self.v3.refusal
        self.completion = self.v3.completion
        self.adherence = self.v3.adherence

    @property
    def version(self) -> str:
        return "v3"

class TrustwiseSDKAsync:
    """
    Async SDK entrypoint for Trustwise. Use this class to access async metrics.
    """
    def __init__(self, config: TrustwiseConfig) -> None:
        """
        Initialize the Trustwise SDK with path-based versioning support.

        Args:
            config: Trustwise configuration instance.
        """
        self.client = TrustwiseAsyncClient(config)
        self.metrics = MetricsAsync(self.client) 