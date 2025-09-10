from qyrusai.configs import Configurations
from typing import Optional, List, Union, Dict, Any
from urllib.parse import urljoin
from qyrusai._rest import AsyncHTTPClient, SyncHTTPClient
from qyrusai._types import (RAGRequest, MCPRequest, ScoreResponse,
                            BatchScoreResponse, EvaluationItem,
                            EvaluationDataset, EvaluationRequestUnion)
import uuid
from datetime import datetime, timezone
import asyncio
import httpx
from concurrent.futures import ThreadPoolExecutor
import requests


# helpers
def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _normalize_eval_input(req):
    # Accept dict or Pydantic model; enforce your RAG/MCP schemas
    if isinstance(req, dict):
        if "tools" in req:
            return MCPRequest(**req).model_dump()
        return RAGRequest(**req).model_dump()
    elif hasattr(req, "model_dump"):
        return req.model_dump()
    raise ValueError("request must be dict or a Pydantic model")


class AsyncLLMEvaluator:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        self.base_url = base_url
        self.gateway_token = gateway_token
        # keep a reference so GC doesn't cancel tasks prematurely
        self._bg_tasks = set()

    def _prepare_headers(self):
        """Prepare common headers for requests."""
        return {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

    def _process_request_data(
            self, request: Union[Dict, RAGRequest, MCPRequest]) -> Dict:
        """Convert request to dictionary format, handling both JSON dict and Pydantic models."""
        if isinstance(request, dict):
            return request
        elif hasattr(request, 'model_dump'):
            return request.model_dump()
        else:
            raise ValueError(
                "Request must be either a dictionary or a Pydantic model")

    async def evaluate(self,
                       context: str,
                       expected_output: str,
                       executed_output: List[str],
                       guardrails: Optional[str] = None) -> float:
        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("judge"))

        data = {
            "context": context,
            "expected_output": expected_output,
            "executed_output": executed_output,
            "guardrails": guardrails
        }

        headers = self._prepare_headers()
        async_client = AsyncHTTPClient()
        response = await async_client.post(url, data, headers)
        return response

    async def evaluate_rag(self, request: Union[Dict, RAGRequest]) -> Dict:
        """Evaluate a RAG (Retrieval-Augmented Generation) system."""
        # Validate and convert input
        if isinstance(request, dict):
            # Validate JSON input against RAGRequest schema
            validated_request = RAGRequest(**request)
            request_data = validated_request.model_dump()
        else:
            request_data = request.model_dump()

        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("score"))

        headers = self._prepare_headers()
        async_client = AsyncHTTPClient()
        response = await async_client.post(url, request_data, headers)
        return response

    async def evaluate_mcp(self, request: Union[Dict, MCPRequest]) -> Dict:
        """Evaluate an MCP (Model Context Protocol) tool-calling system."""
        # Validate and convert input
        if isinstance(request, dict):
            # Validate JSON input against MCPRequest schema
            validated_request = MCPRequest(**request)
            request_data = validated_request.model_dump()
        else:
            request_data = request.model_dump()

        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("score"))

        headers = self._prepare_headers()
        async_client = AsyncHTTPClient()
        response = await async_client.post(url, request_data, headers)
        return response

    async def evaluate_batch(
        self, requests: Union[List[Dict], List[EvaluationRequestUnion],
                              List[Union[Dict, EvaluationRequestUnion]]]
    ) -> Dict:
        """Evaluate a batch of RAG or MCP requests."""
        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("batch/score"))

        headers = self._prepare_headers()

        # Process and validate each request in the batch
        batch_data = []
        for req in requests:
            if isinstance(req, dict):
                # Try to determine if it's RAG or MCP based on presence of 'tools' field
                if 'tools' in req:
                    validated_req = MCPRequest(**req)
                else:
                    validated_req = RAGRequest(**req)
                batch_data.append(validated_req.model_dump())
            else:
                batch_data.append(req.model_dump())

        async_client = AsyncHTTPClient()
        response = await async_client.post(url, batch_data, headers)
        return response

    async def evaluate_dataset(
            self, dataset: Union[Dict, EvaluationDataset]) -> Dict:
        """Evaluate an entire dataset of mixed RAG/MCP evaluations."""
        # Validate and convert dataset
        if isinstance(dataset, dict):
            validated_dataset = EvaluationDataset(**dataset)
        else:
            validated_dataset = dataset

        requests = [item.data for item in validated_dataset.items]
        return await self.evaluate_batch(requests)

    async def get_app_summary(self, app_name: str, **query_params) -> dict:
        """Get application metrics summary."""
        url = urljoin(
            self.base_url,
            Configurations.getLLMEvaluatorContextPath(
                f"apps/{app_name}/summary"))

        headers = {
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

        async_client = AsyncHTTPClient()
        response = await async_client.get(url,
                                          params=query_params,
                                          headers=headers)
        return response

    async def evaluate_online(
        self,
        *,
        app_name: str,
        useremail: str,
        request: Union[Dict, RAGRequest, MCPRequest],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        client_meta: Optional[Dict[str, Any]] = None,
        timeout_s: float = 5.0,
    ) -> str:
        """
        Non-blocking enqueue to Pulse Gateway.
        Uses self.api_key as the Qyrus token and Configurations.getPulseGatewayBaseUrl() for URL.
        Returns a client-generated trace_id immediately.
        """
        if self._bg_tasks is None:
            self._bg_tasks = set()

        # 1) normalize inner RAG/MCP request
        input_payload = _normalize_eval_input(request)

        # 2) build envelope; token comes from self.api_key
        trace_id = str(uuid.uuid4())
        body = {
            "app_name": app_name,
            "qyrus_api_token": self.api_key,  # implicit
            "useremail": useremail,
            "provider": provider,
            "model": model,
            "input": input_payload,
            "emitted_at": _now_iso(),
            "client_meta": {
                **(client_meta or {}), "sdk_trace_id": trace_id,
                "sdk": "qyrusai"
            },
        }

        headers = {
            "Content-Type": "application/json",
            # optional header; the gateway validates from body, but we still send it for parity
            "Custom": self.api_key,
        }

        base = Configurations.getPulseGatewayBaseUrl().rstrip("/")
        url = urljoin(base + "/", "v1/ingest")

        async def _bg_post():
            try:
                # short-lived client; tiny timeouts so user flow never blocks
                async with httpx.AsyncClient(
                        timeout=httpx.Timeout(connect=1.0,
                                              read=timeout_s,
                                              write=timeout_s,
                                              pool=None),
                        http2=True,
                ) as client:
                    await client.post(url, headers=headers, json=body)
            except Exception:
                # best-effort fire-and-forget; swallow
                pass

        t = asyncio.create_task(_bg_post(), name=f"pulse-ingest:{trace_id}")
        self._bg_tasks.add(t)
        t.add_done_callback(self._bg_tasks.discard)
        return trace_id

    async def flush_pulse(self, timeout_s: float = 2.0):
        """Optionally await background sends (e.g., app shutdown)."""
        if not self._bg_tasks:
            return
        await asyncio.wait(self._bg_tasks, timeout=timeout_s)


class SyncLLMEvaluator:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        self.base_url = base_url
        self.gateway_token = gateway_token
        # tiny pool + session for background posts
        self._pulse_pool = ThreadPoolExecutor(max_workers=2,
                                              thread_name_prefix="pulse-bg")
        self._pulse_session = requests.Session()

    def _prepare_headers(self):
        """Prepare common headers for requests."""
        return {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

    def _process_request_data(
            self, request: Union[Dict, RAGRequest, MCPRequest]) -> Dict:
        """Convert request to dictionary format, handling both JSON dict and Pydantic models."""
        if isinstance(request, dict):
            return request
        elif hasattr(request, 'model_dump'):
            return request.model_dump()
        else:
            raise ValueError(
                "Request must be either a dictionary or a Pydantic model")

    def evaluate(self,
                 context: str,
                 expected_output: str,
                 executed_output: List[str],
                 guardrails: Optional[str] = None) -> float:
        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("judge"))

        data = {
            "context": context,
            "expected_output": expected_output,
            "executed_output": executed_output,
            "guardrails": guardrails
        }
        headers = self._prepare_headers()
        sync_client = SyncHTTPClient()
        response = sync_client.post(url, data, headers)
        return response

    def evaluate_rag(self, request: Union[Dict, RAGRequest]) -> Dict:
        """Evaluate a RAG (Retrieval-Augmented Generation) system."""
        # Validate and convert input
        if isinstance(request, dict):
            # Validate JSON input against RAGRequest schema
            validated_request = RAGRequest(**request)
            request_data = validated_request.model_dump()
        else:
            request_data = request.model_dump()

        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("score"))

        headers = self._prepare_headers()
        sync_client = SyncHTTPClient()
        response = sync_client.post(url, request_data, headers)
        return response

    def evaluate_mcp(self, request: Union[Dict, MCPRequest]) -> Dict:
        """Evaluate an MCP (Model Context Protocol) tool-calling system."""
        # Validate and convert input
        if isinstance(request, dict):
            # Validate JSON input against MCPRequest schema
            validated_request = MCPRequest(**request)
            request_data = validated_request.model_dump()
        else:
            request_data = request.model_dump()

        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("score"))

        headers = self._prepare_headers()
        sync_client = SyncHTTPClient()
        response = sync_client.post(url, request_data, headers)
        return response

    def evaluate_batch(
        self, requests: Union[List[Dict], List[EvaluationRequestUnion],
                              List[Union[Dict, EvaluationRequestUnion]]]
    ) -> Dict:
        """Evaluate a batch of RAG or MCP requests."""
        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("batch/score"))

        headers = self._prepare_headers()

        # Process and validate each request in the batch
        batch_data = []
        for req in requests:
            if isinstance(req, dict):
                # Try to determine if it's RAG or MCP based on presence of 'tools' field
                if 'tools' in req:
                    validated_req = MCPRequest(**req)
                else:
                    validated_req = RAGRequest(**req)
                batch_data.append(validated_req.model_dump())
            else:
                batch_data.append(req.model_dump())

        sync_client = SyncHTTPClient()
        response = sync_client.post(url, batch_data, headers)
        return response

    def evaluate_dataset(self, dataset: Union[Dict,
                                              EvaluationDataset]) -> Dict:
        """Evaluate an entire dataset of mixed RAG/MCP evaluations."""
        # Validate and convert dataset
        if isinstance(dataset, dict):
            validated_dataset = EvaluationDataset(**dataset)
        else:
            validated_dataset = dataset

        requests = [item.data for item in validated_dataset.items]
        return self.evaluate_batch(requests)

    def get_app_summary(self, app_name: str, **query_params) -> dict:
        """Get application metrics summary."""
        url = urljoin(
            self.base_url,
            Configurations.getLLMEvaluatorContextPath(
                f"apps/{app_name}/summary"))

        headers = {
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

        sync_client = SyncHTTPClient()
        response = sync_client.get(url, params=query_params, headers=headers)
        return response

    def evaluate_online(
        self,
        *,
        app_name: str,
        useremail: str,
        request: Union[Dict, RAGRequest, MCPRequest],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        client_meta: Optional[Dict[str, Any]] = None,
        timeout_s: float = 5.0,
    ) -> str:
        """
        Non-blocking enqueue to Pulse Gateway (background thread).
        Uses self.api_key as the Qyrus token and Configurations.getPulseGatewayBaseUrl() for URL.
        Returns a client-generated trace_id immediately.
        """
        input_payload = _normalize_eval_input(request)

        trace_id = str(uuid.uuid4())
        body = {
            "app_name": app_name,
            "qyrus_api_token": self.api_key,  # implicit
            "useremail": useremail,
            "provider": provider,
            "model": model,
            "input": input_payload,
            "emitted_at": _now_iso(),
            "client_meta": {
                **(client_meta or {}), "sdk_trace_id": trace_id,
                "sdk": "qyrusai"
            },
        }

        headers = {
            "Content-Type": "application/json",
            "Custom": self.api_key,  # optional; gateway reads body token
        }

        base = Configurations.getPulseGatewayBaseUrl().rstrip("/")
        url = urljoin(base + "/", "v1/ingest")

        def _bg_post():
            try:
                self._pulse_session.post(url,
                                         headers=headers,
                                         json=body,
                                         timeout=timeout_s)
            except Exception:
                pass

        self._pulse_pool.submit(_bg_post)
        return trace_id

    def flush_pulse(self, timeout_s: float = 2.0):
        """Optionally flush outstanding background sends before exit."""
        self._pulse_pool.shutdown(wait=True, timeout=timeout_s)
