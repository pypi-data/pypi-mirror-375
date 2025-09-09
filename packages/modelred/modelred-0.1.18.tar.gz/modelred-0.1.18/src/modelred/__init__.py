import asyncio
import aiohttp
import requests
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Union, Callable

__version__ = "0.1.18"

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logger = logging.getLogger("modelred")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# Constants / Enums
# -----------------------------------------------------------------------------
BASE_URL = "https://app.modelred.ai"


class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    REST = "rest"
    BEDROCK = "bedrock"
    SAGEMAKER = "sagemaker"


class AssessmentStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


# -----------------------------------------------------------------------------
# Data classes
# -----------------------------------------------------------------------------
@dataclass
class Model:
    id: str
    modelId: str
    provider: str
    modelName: Optional[str]
    displayName: str
    description: Optional[str]
    isActive: bool
    lastTested: Optional[datetime]
    testCount: int
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdByUser: Optional[Dict[str, Any]] = None


@dataclass
class Assessment:
    id: str
    modelId: str
    status: AssessmentStatus
    testTypes: List[str]
    priority: Priority
    progress: int = 0
    results: Optional[Dict[str, Any]] = None
    errorMessage: Optional[str] = None
    createdAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    estimatedDuration: Optional[int] = None
    detailedReport: Optional[Dict[str, Any]] = None


@dataclass
class Probe:
    id: str
    key: str
    display_name: str
    description: str
    estimated_time: str
    tags: List[str]
    category: str
    tier: str
    severity: str
    isActive: bool
    version: str


@dataclass
class ProbesIndex:
    probes: List[Probe]
    probe_categories: Dict[str, Any]
    tier_definitions: Dict[str, Any]
    severity_levels: Dict[str, Any]


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------
class ModelRedError(Exception):
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response or {}


class AuthenticationError(ModelRedError):
    pass


class AuthorizationError(ModelRedError):
    pass


class SubscriptionLimitError(ModelRedError):
    def __init__(self, message: str, tier: Optional[str] = None, **kw):
        super().__init__(message, **kw)
        self.tier = tier


class ValidationError(ModelRedError):
    pass


class NotFoundError(ModelRedError):
    pass


class ConflictError(ModelRedError):
    pass


class RateLimitError(ModelRedError):
    pass


class ServerError(ModelRedError):
    pass


class NetworkError(ModelRedError):
    pass


# -----------------------------------------------------------------------------
# Provider config helpers
# -----------------------------------------------------------------------------
class ProviderConfig:
    @staticmethod
    def openai(
        api_key: str,
        model_name: str = "gpt-3.5-turbo",
        organization: Optional[str] = None,
    ) -> Dict[str, Any]:
        cfg = {"api_key": api_key, "model_name": model_name}
        if organization:
            cfg["organization"] = organization
        return cfg

    @staticmethod
    def anthropic(
        api_key: str, model_name: str = "claude-3-sonnet-20240229"
    ) -> Dict[str, Any]:
        return {"api_key": api_key, "model_name": model_name}

    @staticmethod
    def azure(
        api_key: str,
        endpoint: str,
        deployment_name: str,
        api_version: str = "2024-06-01",
    ) -> Dict[str, Any]:
        return {
            "api_key": api_key,
            "endpoint": endpoint,
            "deployment_name": deployment_name,
            "api_version": api_version,
        }

    @staticmethod
    def huggingface(
        model_name: str,
        api_key: Optional[str] = None,
        use_inference_api: bool = True,
        endpoint_url: Optional[str] = None,
        task: str = "text-generation",
    ) -> Dict[str, Any]:
        cfg = {
            "model_name": model_name,
            "use_inference_api": use_inference_api,
            "task": task,
        }
        if api_key:
            cfg["api_key"] = api_key
        if endpoint_url:
            cfg["endpoint_url"] = endpoint_url
        return cfg

    @staticmethod
    def rest(
        uri: str,
        name: Optional[str] = None,
        key_env_var: str = "REST_API_KEY",
        api_key: Optional[str] = None,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        req_template: str = "$INPUT",
        req_template_json_object: Optional[Dict[str, Any]] = None,
        response_json: bool = True,
        response_json_field: str = "text",
        request_timeout: int = 20,
        ratelimit_codes: Optional[List[int]] = None,
        skip_codes: Optional[List[int]] = None,
        verify_ssl: Union[bool, str] = True,
        proxies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        cfg = {
            "uri": uri,
            "method": method,
            "headers": headers or {},
            "req_template": req_template,
            "response_json": response_json,
            "response_json_field": response_json_field,
            "request_timeout": request_timeout,
            "ratelimit_codes": ratelimit_codes or [429],
            "skip_codes": skip_codes or [],
            "verify_ssl": verify_ssl,
        }
        if name is not None:
            cfg["name"] = name
        if key_env_var != "REST_API_KEY":
            cfg["key_env_var"] = key_env_var
        if api_key is not None:
            cfg["api_key"] = api_key
        if req_template_json_object is not None:
            cfg["req_template_json_object"] = req_template_json_object
        if proxies is not None:
            cfg["proxies"] = proxies
        return cfg

    @staticmethod
    def bedrock(
        region: str,
        model_id: str,
        access_key_id: str,
        secret_access_key: str,
        session_token: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        cfg = {
            "region": region,
            "model_id": model_id,
            "access_key_id": access_key_id,
            "secret_access_key": secret_access_key,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if session_token:
            cfg["session_token"] = session_token
        return cfg

    @staticmethod
    def sagemaker(
        region: str,
        endpoint_name: str,
        access_key_id: str,
        secret_access_key: str,
        session_token: Optional[str] = None,
        content_type: str = "application/json",
        accept: str = "application/json",
        request_json_template: Optional[Dict[str, Any]] = None,
        request_text_template: Optional[str] = None,
        response_json_field: str = "generated_text",
        timeout_ms: int = 20000,
    ) -> Dict[str, Any]:
        cfg = {
            "region": region,
            "endpoint_name": endpoint_name,
            "access_key_id": access_key_id,
            "secret_access_key": secret_access_key,
            "content_type": content_type,
            "accept": accept,
            "response_json_field": response_json_field,
            "timeout_ms": timeout_ms,
        }
        if session_token:
            cfg["session_token"] = session_token
        if request_json_template is not None:
            cfg["request_json_template"] = request_json_template
        if request_text_template is not None:
            cfg["request_text_template"] = request_text_template
        return cfg


# -----------------------------------------------------------------------------
# Base client
# -----------------------------------------------------------------------------
class _BaseClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MODELRED_API_KEY")
        if not self.api_key or not self.api_key.startswith("mr_"):
            raise ValidationError("Valid API key is required (must start with 'mr_').")
        self.logger = logger

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"ModelRed-PythonSDK/{__version__}",
        }

    def _parse_dt(self, s: Optional[str]) -> Optional[datetime]:
        if not s:
            return None
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None

    def _map_error(self, status: int, payload: Dict[str, Any]):
        msg = payload.get("error") or payload.get("message") or f"API error {status}"
        if status == 401:
            raise AuthenticationError(msg, status, payload)
        if status == 403:
            tier = payload.get("tier")
            if any(
                w in msg.lower() for w in ("limit", "subscription", "tier", "upgrade")
            ):
                raise SubscriptionLimitError(
                    msg, tier=tier, status_code=status, response=payload
                )
            raise AuthorizationError(msg, status, payload)
        if status == 404:
            raise NotFoundError(msg, status, payload)
        if status == 409:
            raise ConflictError(msg, status, payload)
        if status == 422:
            raise ValidationError(msg, status, payload)
        if status == 429:
            raise RateLimitError(msg, status, payload)
        if status >= 500:
            raise ServerError(msg, status, payload)
        raise ModelRedError(msg, status, payload)

    def _parse_model(self, d: Dict[str, Any]) -> Model:
        return Model(
            id=d["id"],
            modelId=d["modelId"],
            provider=d["provider"],
            modelName=d.get("modelName"),
            displayName=d["displayName"],
            description=d.get("description"),
            isActive=d.get("isActive", True),
            lastTested=self._parse_dt(d.get("lastTested")),
            testCount=d.get("testCount", 0),
            createdAt=self._parse_dt(d.get("createdAt")),
            updatedAt=self._parse_dt(d.get("updatedAt")),
            createdByUser=d.get("createdByUser"),
        )

    def _parse_assessment(self, d: Dict[str, Any]) -> Assessment:
        status_raw = str(d.get("status", "")).lower()
        try:
            status = AssessmentStatus(status_raw)
        except Exception:
            try:
                status = AssessmentStatus[d.get("status")]
            except Exception:
                status = AssessmentStatus.QUEUED

        prio_raw = str(d.get("priority", "normal")).lower()
        try:
            prio = Priority(prio_raw)
        except Exception:
            prio = Priority.NORMAL

        return Assessment(
            id=d["id"],
            modelId=d["modelId"],
            status=status,
            testTypes=d.get("testTypes", []),
            priority=prio,
            progress=d.get("progress", 0),
            results=d.get("results"),
            errorMessage=d.get("errorMessage"),
            createdAt=self._parse_dt(d.get("createdAt")),
            completedAt=self._parse_dt(d.get("completedAt")),
            estimatedDuration=d.get("estimatedDuration"),
            detailedReport=d.get("detailedReport"),
        )

    def _parse_probes(self, payload: Dict[str, Any]) -> ProbesIndex:
        data = payload.get("data", {})
        probes = [
            Probe(
                id=p["id"],
                key=p["key"],
                display_name=p["display_name"],
                description=p["description"],
                estimated_time=p["estimated_time"],
                tags=list(p.get("tags", [])),
                category=p["category"],
                tier=p["tier"],
                severity=p["severity"],
                isActive=p.get("isActive", True),
                version=p.get("version", "1.0"),
            )
            for p in data.get("probes", [])
        ]
        return ProbesIndex(
            probes=probes,
            probe_categories=data.get("probe_categories", {}),
            tier_definitions=data.get("tier_definitions", {}),
            severity_levels=data.get("severity_levels", {}),
        )


# -----------------------------------------------------------------------------
# Sync client
# -----------------------------------------------------------------------------
class ModelRed(_BaseClient):
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        super().__init__(api_key)
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(self._headers())

    def _request(self, method: str, path: str, **kw) -> Dict[str, Any]:
        url = f"{BASE_URL}/api{path}"
        try:
            resp = self._session.request(method, url, timeout=self.timeout, **kw)
            try:
                payload = resp.json()
            except Exception:
                payload = {"error": resp.text}
            if resp.status_code >= 400:
                self._map_error(resp.status_code, payload)
            return payload
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {e}")

    # Models
    def create_model(
        self,
        *,
        modelId: str,
        provider: Union[str, ModelProvider],
        displayName: str,
        providerConfig: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Model:
        if isinstance(provider, ModelProvider):
            provider = provider.value
        body = {
            "modelId": modelId,
            "provider": provider,
            "displayName": displayName,
            "providerConfig": providerConfig,
        }
        if description:
            body["description"] = description
        p = self._request("POST", "/models", json=body)
        return self._parse_model(p["data"])

    def list_models(self) -> List[Model]:
        p = self._request("GET", "/models")
        return [self._parse_model(m) for m in p["data"]]

    def get_model(self, model_identifier: str) -> Model:
        # Try DB id first, then fall back to listing and matching on modelId
        try:
            p = self._request("GET", f"/models/{model_identifier}")
            return self._parse_model(p["data"])
        except NotFoundError:
            pass
        for m in self.list_models():
            if m.modelId == model_identifier:
                return m
        raise NotFoundError(f"Model '{model_identifier}' not found")

    def delete_model(self, model_identifier: str) -> bool:
        model = self.get_model(model_identifier)
        p = self._request("DELETE", f"/models/{model.id}")
        return p.get("success", True)

    # Assessments
    def create_assessment(
        self,
        *,
        model: str,
        test_types: List[str],
        priority: Union[str, Priority] = Priority.NORMAL,
    ) -> Assessment:
        """
        `model` can be the developer-facing modelId (slug) OR the DB id.
        The server resolves it within your organization.
        """
        if isinstance(priority, Priority):
            priority = priority.value
        body = {"model": model, "testTypes": test_types, "priority": priority}
        p = self._request("POST", "/assessments", json=body)
        return self._parse_assessment(p["data"])

    def get_assessment(self, assessment_id: str) -> Assessment:
        p = self._request("GET", f"/assessments/{assessment_id}")
        return self._parse_assessment(p["data"])

    def list_assessments(self, limit: Optional[int] = None) -> List[Assessment]:
        params = {}
        if limit:
            params["limit"] = str(limit)
        p = self._request("GET", "/assessments", params=params)
        return [self._parse_assessment(a) for a in p["data"]]

    def wait_for_completion(
        self,
        assessment_id: str,
        *,
        timeout_minutes: int = 60,
        poll_interval: int = 10,
        progress_callback: Optional[Callable[[Assessment], None]] = None,
    ) -> Assessment:
        deadline = time.time() + timeout_minutes * 60
        last_status = None
        while time.time() < deadline:
            a = self.get_assessment(assessment_id)
            if a.status != last_status and progress_callback:
                progress_callback(a)
                last_status = a.status
            if a.status in (
                AssessmentStatus.COMPLETED,
                AssessmentStatus.FAILED,
                AssessmentStatus.CANCELLED,
            ):
                return a
            time.sleep(poll_interval)
        raise ModelRedError(f"Assessment timeout after {timeout_minutes} minutes")

    # Probes
    def get_probes(
        self,
        *,
        category: Optional[str] = None,
        tier: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> ProbesIndex:
        params = {}
        if category:
            params["category"] = category
        if tier:
            params["tier"] = tier
        if severity:
            params["severity"] = severity
        p = self._request("GET", "/probes", params=params)
        return self._parse_probes(p)


# -----------------------------------------------------------------------------
# Async client
# -----------------------------------------------------------------------------
class AsyncModelRed(_BaseClient):
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        super().__init__(api_key)
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            timeout=self.timeout, headers=self._headers()
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            await self._session.close()
            self._session = None

    async def _request(self, method: str, path: str, **kw) -> Dict[str, Any]:
        if not self._session:
            raise RuntimeError(
                "Use 'async with AsyncModelRed()' to create the session."
            )
        url = f"{BASE_URL}/api{path}"
        try:
            async with self._session.request(method, url, **kw) as resp:
                try:
                    payload = await resp.json()
                except Exception:
                    payload = {"error": await resp.text()}
                if resp.status >= 400:
                    self._map_error(resp.status, payload)
                return payload
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {e}")

    # Models
    async def create_model(
        self,
        *,
        modelId: str,
        provider: Union[str, ModelProvider],
        displayName: str,
        providerConfig: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Model:
        if isinstance(provider, ModelProvider):
            provider = provider.value
        body = {
            "modelId": modelId,
            "provider": provider,
            "displayName": displayName,
            "providerConfig": providerConfig,
        }
        if description:
            body["description"] = description
        p = await self._request("POST", "/models", json=body)
        return self._parse_model(p["data"])

    async def list_models(self) -> List[Model]:
        p = await self._request("GET", "/models")
        return [self._parse_model(m) for m in p["data"]]

    async def get_model(self, model_identifier: str) -> Model:
        try:
            p = await self._request("GET", f"/models/{model_identifier}")
            return self._parse_model(p["data"])
        except NotFoundError:
            pass
        for m in await self.list_models():
            if m.modelId == model_identifier:
                return m
        raise NotFoundError(f"Model '{model_identifier}' not found")

    async def delete_model(self, model_identifier: str) -> bool:
        m = await self.get_model(model_identifier)
        p = await self._request("DELETE", f"/models/{m.id}")
        return p.get("success", True)

    # Assessments
    async def create_assessment(
        self,
        *,
        model: str,
        test_types: List[str],
        priority: Union[str, Priority] = Priority.NORMAL,
    ) -> Assessment:
        if isinstance(priority, Priority):
            priority = priority.value
        body = {"model": model, "testTypes": test_types, "priority": priority}
        p = await self._request("POST", "/assessments", json=body)
        return self._parse_assessment(p["data"])

    async def get_assessment(self, assessment_id: str) -> Assessment:
        p = await self._request("GET", f"/assessments/{assessment_id}")
        return self._parse_assessment(p["data"])

    async def list_assessments(self, limit: Optional[int] = None) -> List[Assessment]:
        params = {}
        if limit:
            params["limit"] = str(limit)
        p = await self._request("GET", "/assessments", params=params)
        return [self._parse_assessment(a) for a in p["data"]]

    async def wait_for_completion(
        self,
        assessment_id: str,
        *,
        timeout_minutes: int = 60,
        poll_interval: int = 10,
        progress_callback: Optional[Callable[[Assessment], None]] = None,
    ) -> Assessment:
        deadline = time.time() + timeout_minutes * 60
        last_status = None
        while time.time() < deadline:
            a = await self.get_assessment(assessment_id)
            if a.status != last_status and progress_callback:
                progress_callback(a)
                last_status = a.status
            if a.status in (
                AssessmentStatus.COMPLETED,
                AssessmentStatus.FAILED,
                AssessmentStatus.CANCELLED,
            ):
                return a
            await asyncio.sleep(poll_interval)
        raise ModelRedError(f"Assessment timeout after {timeout_minutes} minutes")

    # Probes
    async def get_probes(
        self,
        *,
        category: Optional[str] = None,
        tier: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> ProbesIndex:
        params = {}
        if category:
            params["category"] = category
        if tier:
            params["tier"] = tier
        if severity:
            params["severity"] = severity
        p = await self._request("GET", "/probes", params=params)
        return self._parse_probes(p)


# -----------------------------------------------------------------------------
# Public exports
# -----------------------------------------------------------------------------
__all__ = [
    "ModelRed",
    "AsyncModelRed",
    "Model",
    "Assessment",
    "ModelProvider",
    "AssessmentStatus",
    "Priority",
    "ProviderConfig",
    # Exceptions
    "ModelRedError",
    "AuthenticationError",
    "AuthorizationError",
    "SubscriptionLimitError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
]
