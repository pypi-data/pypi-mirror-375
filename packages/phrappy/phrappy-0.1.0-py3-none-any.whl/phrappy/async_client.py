import logging
import asyncio
from typing import Optional, TypeVar, Dict, Any, Union, Mapping, Sequence, Tuple
from collections import deque

from httpx import HTTPStatusError, Response, AsyncClient
from pydantic import BaseModel

from ._meta import __version__, homepage
from .exceptions import PhrappyError
from .async_tags import (
    AdditionalWorkflowStepOperations,
    AnalysisOperations,
    AsyncRequestOperations,
    AuthenticationOperations,
    BilingualFileOperations,
    BusinessUnitOperations,
    BuyerOperations,
    ClientOperations,
    ConnectorOperations,
    CostCenterOperations,
    CustomFieldsOperations,
    CustomFileTypeOperations,
    DomainOperations,
    DueDateSchemeOperations,
    EmailTemplateOperations,
    FileOperations,
    GlossaryOperations,
    ImportsettingsOperations,
    ConversationsOperations,
    JobOperations,
    SupportedLanguagesOperations,
    LanguageQualityAssessmentOperations,
    QualityAssuranceOperations,
    MachineTranslationSettingsOperations,
    MachineTranslationOperations,
    MappingOperations,
    LanguageAIOperations,
    NetRateSchemeOperations,
    NotificationsOperations,
    PriceListOperations,
    ProjectTemplateOperations,
    TermBaseOperations,
    TranslationMemoryOperations,
    ProjectOperations,
    TranslationOperations,
    SegmentOperations,
    ProviderOperations,
    ProjectReferenceFileOperations,
    QuoteOperations,
    SCIMOperations,
    SegmentationRulesOperations,
    ServiceOperations,
    SpellCheckOperations,
    SubDomainOperations,
    UserOperations,
    WorkflowStepOperations,
    VendorOperations,
    WebhookOperations,
    XMLAssistantOperations,
    WorkflowchangesOperations,
)


MEMSOURCE_BASE_URL = "https://cloud.memsource.com/web"

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
FileType = Tuple[str, Union[bytes, Any]]
RequestFiles = Union[Mapping[str, FileType], Sequence[Tuple[str, FileType]]]

ua = f"phrappy/{__version__} (+{homepage})"


class AsyncPhrappy:
    """Async client for interacting with the Phrase TMS API."""

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = MEMSOURCE_BASE_URL,
        timeout=180,
    ):
        """
        Args:
            token: Optional API token. If provided without "ApiToken " prefix, it will be added.
            base_url: Base URL for API requests. Defaults to cloud.memsource.com.
        """
        self._client = AsyncClient(timeout=timeout, headers={"User-Agent": ua})
        self.base_url = base_url
        self.token = self._validate_token(token)
        self.last_responses = deque(maxlen=5)
        self._init_operations()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncPhrappy":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    @staticmethod
    def _validate_token(token: Optional[str]) -> Optional[str]:
        if not token:
            return None
        if token.startswith("ApiToken "):
            return token
        return f"ApiToken {token}"

    def _init_operations(self) -> None:
        self.additional_workflow_step = AdditionalWorkflowStepOperations(self)
        self.analysis = AnalysisOperations(self)
        self.async_request = AsyncRequestOperations(self)
        self.authentication = AuthenticationOperations(self)
        self.bilingual_file = BilingualFileOperations(self)
        self.business_unit = BusinessUnitOperations(self)
        self.buyer = BuyerOperations(self)
        self.client = ClientOperations(self)
        self.connector = ConnectorOperations(self)
        self.cost_center = CostCenterOperations(self)
        self.custom_fields = CustomFieldsOperations(self)
        self.custom_file_type = CustomFileTypeOperations(self)
        self.domain = DomainOperations(self)
        self.due_date_scheme = DueDateSchemeOperations(self)
        self.email_template = EmailTemplateOperations(self)
        self.file = FileOperations(self)
        self.glossary = GlossaryOperations(self)
        self.importsettings = ImportsettingsOperations(self)
        self.conversations = ConversationsOperations(self)
        self.job = JobOperations(self)
        self.supported_languages = SupportedLanguagesOperations(self)
        self.language_quality_assessment = LanguageQualityAssessmentOperations(self)
        self.quality_assurance = QualityAssuranceOperations(self)
        self.machine_translation_settings = MachineTranslationSettingsOperations(self)
        self.machine_translation = MachineTranslationOperations(self)
        self.mapping = MappingOperations(self)
        self.language_ai = LanguageAIOperations(self)
        self.net_rate_scheme = NetRateSchemeOperations(self)
        self.notifications = NotificationsOperations(self)
        self.price_list = PriceListOperations(self)
        self.project_template = ProjectTemplateOperations(self)
        self.term_base = TermBaseOperations(self)
        self.translation_memory = TranslationMemoryOperations(self)
        self.project = ProjectOperations(self)
        self.translation = TranslationOperations(self)
        self.segment = SegmentOperations(self)
        self.provider = ProviderOperations(self)
        self.project_reference_file = ProjectReferenceFileOperations(self)
        self.quote = QuoteOperations(self)
        self.scim = SCIMOperations(self)
        self.segmentation_rules = SegmentationRulesOperations(self)
        self.service = ServiceOperations(self)
        self.spell_check = SpellCheckOperations(self)
        self.sub_domain = SubDomainOperations(self)
        self.user = UserOperations(self)
        self.workflow_step = WorkflowStepOperations(self)
        self.vendor = VendorOperations(self)
        self.webhook = WebhookOperations(self)
        self.xml_assistant = XMLAssistantOperations(self)
        self.workflowchanges = WorkflowchangesOperations(self)

    async def make_request(
        self,
        method: str,
        path: str,
        phrase_token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Union[T, Dict[str, Any]]] = None,
        files: Optional[RequestFiles] = None,
        headers: Optional[Dict[str, str]] = None,
        content: Optional[bytes] = None,
        timeout: float = 180.0,
    ) -> Response:
        """Perform an async HTTP request to the Phrase TMS API."""
        if not path.startswith("/"):
            path = "/" + path
        url = self.base_url.rstrip("/") + path

        request_headers = {}
        request_headers.setdefault("User-Agent", ua)
        if token := (phrase_token or self.token):
            request_headers["Authorization"] = token
        if headers:
            request_headers.update(headers)

        if payload is not None and not isinstance(payload, dict):
            try:
                payload = payload.model_dump(exclude_none=True)
            except Exception as e:
                logger.exception("Failed to serialize payload")
                raise PhrappyError("Failed to serialize request payload") from e

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        response: Optional[Response] = None
        for attempt in range(3):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    params=params,
                    json=payload,
                    files=files,
                    content=content,
                    timeout=timeout,
                )
                # Cache small responses for diagnostics
                try:
                    cl = int(response.headers.get("Content-Length") or 0)
                except ValueError:
                    cl = 0
                if cl and cl < 10240:
                    await response.aread()
                    self.last_responses.append(response)

                response.raise_for_status()
                return response

            except HTTPStatusError as exc:
                if response:
                    if response.status_code in (429, 503):
                        await asyncio.sleep(min(2**attempt, 8))
                        continue
                    try:
                        await response.aread()
                        error_data = response.json()
                        error_code = error_data.get("errorCode")
                        error_desc = error_data.get("errorDescription")
                        msg = (
                            f"API request failed: {method} {url}\n"
                            f"Status: {response.status_code}\n"
                            f"Error code: {error_code}\n"
                            f"Description: {error_desc}"
                        )
                        raise PhrappyError(msg) from exc
                    except ValueError:
                        raise PhrappyError(
                            f"API request failed with invalid JSON response: {await response.aread() or b''}"
                        ) from exc
                else:
                    raise PhrappyError(
                        f"Request failed with no response: {str(exc)}"
                    ) from exc

            except Exception as e:
                logger.exception(f"Unexpected error during request: {url}")
                raise PhrappyError(f"An unexpected error occurred: {str(e)}") from e

        # If we somehow exit the retry loop without returning/raising earlier:
        raise PhrappyError("Request retries exhausted")

    @classmethod
    async def from_creds(
        cls, username: str, password: str, base_url=MEMSOURCE_BASE_URL, timeout=180
    ) -> "AsyncPhrappy":
        pp = cls(base_url=base_url, timeout=timeout)
        login_dto = {"userName": username, "password": password}
        resp = await pp.authentication.login(login_dto)
        pp.token = pp._validate_token(getattr(resp, "token", None))
        return pp
