from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable, List

import httpx
from llama_deploy.core.schema import LogEvent
from llama_deploy.core.schema.deployments import (
    DeploymentCreate,
    DeploymentResponse,
    DeploymentsListResponse,
    DeploymentUpdate,
)
from llama_deploy.core.schema.git_validation import (
    RepositoryValidationRequest,
    RepositoryValidationResponse,
)
from llama_deploy.core.schema.projects import ProjectsListResponse, ProjectSummary
from llama_deploy.core.schema.public import VersionResponse


class BaseClient:
    def __init__(
        self, base_url: str, api_key: str | None = None, auth: httpx.Auth | None = None
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

        headers: dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            auth=auth,
        )
        self.hookless_client = httpx.AsyncClient(
            base_url=self.base_url, headers=headers, auth=auth
        )

    async def aclose(self) -> None:
        await self.client.aclose()
        await self.hookless_client.aclose()


class ControlPlaneClient(BaseClient):
    """Unscoped client for non-project endpoints."""

    @classmethod
    @asynccontextmanager
    async def ctx(
        cls, base_url: str, api_key: str | None = None, auth: httpx.Auth | None = None
    ) -> AsyncIterator[ControlPlaneClient]:
        client = cls(base_url, api_key, auth)
        try:
            yield client
        finally:
            try:
                await client.aclose()
            except Exception:
                pass

    def __init__(
        self, base_url: str, api_key: str | None = None, auth: httpx.Auth | None = None
    ) -> None:
        super().__init__(base_url, api_key, auth)

    async def server_version(self) -> VersionResponse:
        response = await self.client.get("/api/v1beta1/deployments-public/version")
        response.raise_for_status()
        return VersionResponse.model_validate(response.json())

    async def list_projects(self) -> List[ProjectSummary]:
        response = await self.client.get("/api/v1beta1/deployments/list-projects")
        response.raise_for_status()
        projects_response = ProjectsListResponse.model_validate(response.json())
        return [project for project in projects_response.projects]


class ProjectClient(BaseClient):
    """Project-scoped client for deployment operations."""

    @classmethod
    @asynccontextmanager
    async def ctx(
        cls,
        base_url: str,
        project_id: str,
        api_key: str | None = None,
        auth: httpx.Auth | None = None,
    ) -> AsyncIterator[ProjectClient]:
        client = cls(base_url, project_id, api_key, auth)
        try:
            yield client
        finally:
            try:
                await client.aclose()
            except Exception:
                pass

    def __init__(
        self,
        base_url: str,
        project_id: str,
        api_key: str | None = None,
        auth: httpx.Auth | None = None,
    ) -> None:
        super().__init__(base_url, api_key, auth)
        self.project_id = project_id

    async def list_deployments(self) -> List[DeploymentResponse]:
        response = await self.client.get(
            "/api/v1beta1/deployments",
            params={"project_id": self.project_id},
        )
        response.raise_for_status()
        deployments_response = DeploymentsListResponse.model_validate(response.json())
        return [deployment for deployment in deployments_response.deployments]

    async def get_deployment(
        self, deployment_id: str, include_events: bool = False
    ) -> DeploymentResponse:
        response = await self.client.get(
            f"/api/v1beta1/deployments/{deployment_id}",
            params={"project_id": self.project_id, "include_events": include_events},
        )
        response.raise_for_status()
        return DeploymentResponse.model_validate(response.json())

    async def create_deployment(
        self, deployment_data: DeploymentCreate
    ) -> DeploymentResponse:
        response = await self.client.post(
            "/api/v1beta1/deployments",
            params={"project_id": self.project_id},
            json=deployment_data.model_dump(exclude_none=True),
        )
        response.raise_for_status()
        return DeploymentResponse.model_validate(response.json())

    async def delete_deployment(self, deployment_id: str) -> None:
        response = await self.client.delete(
            f"/api/v1beta1/deployments/{deployment_id}",
            params={"project_id": self.project_id},
        )
        response.raise_for_status()

    async def update_deployment(
        self,
        deployment_id: str,
        update_data: DeploymentUpdate,
    ) -> DeploymentResponse:
        response = await self.client.patch(
            f"/api/v1beta1/deployments/{deployment_id}",
            params={"project_id": self.project_id},
            json=update_data.model_dump(),
        )
        response.raise_for_status()
        return DeploymentResponse.model_validate(response.json())

    async def validate_repository(
        self,
        repo_url: str,
        deployment_id: str | None = None,
        pat: str | None = None,
    ) -> RepositoryValidationResponse:
        response = await self.client.post(
            "/api/v1beta1/deployments/validate-repository",
            params={"project_id": self.project_id},
            json=RepositoryValidationRequest(
                repository_url=repo_url,
                deployment_id=deployment_id,
                pat=pat,
            ).model_dump(),
        )
        response.raise_for_status()
        return RepositoryValidationResponse.model_validate(response.json())

    async def stream_deployment_logs(
        self,
        deployment_id: str,
        *,
        include_init_containers: bool = False,
        since_seconds: int | None = None,
        tail_lines: int | None = None,
    ) -> AsyncIterator[LogEvent]:
        """Stream logs as LogEvent items from the control plane using SSE.

        Yields `LogEvent` models until the stream ends (e.g., rollout completes).
        """
        params: dict[str, object] = {
            "project_id": self.project_id,
            "include_init_containers": include_init_containers,
        }
        if since_seconds is not None:
            params["since_seconds"] = since_seconds
        if tail_lines is not None:
            params["tail_lines"] = tail_lines

        url = f"/api/v1beta1/deployments/{deployment_id}/logs"
        headers = {"Accept": "text/event-stream"}

        async with self.hookless_client.stream(
            "GET", url, params=params, headers=headers, timeout=None
        ) as response:
            response.raise_for_status()

            event_name: str | None = None
            data_lines: list[str] = []
            async for line in response.aiter_lines():
                if line is None:
                    continue
                line = line.decode() if isinstance(line, (bytes, bytearray)) else line
                if line.startswith("event:"):
                    event_name = line[len("event:") :].strip()
                elif line.startswith("data:"):
                    data_lines.append(line[len("data:") :].lstrip())
                elif line.strip() == "":
                    if event_name == "log" and data_lines:
                        data_str = "\n".join(data_lines)
                        try:
                            yield LogEvent.model_validate_json(data_str)
                        except Exception:
                            pass
                    event_name = None
                    data_lines = []


Closer = Callable[[], None]
