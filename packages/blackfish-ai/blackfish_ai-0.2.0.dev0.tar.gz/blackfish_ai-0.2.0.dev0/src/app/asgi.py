from __future__ import annotations

import os
from os import urandom
import json
import aiohttp
from aiohttp.typedefs import StrOrURL
import requests
from datetime import datetime
from dataclasses import dataclass
from collections.abc import AsyncGenerator
from typing import Optional, Tuple, Any, Type
import asyncio
import itertools
from pathlib import Path
import bcrypt
from importlib import import_module

from fabric.connection import Connection
from paramiko.sftp_client import SFTPClient
from pydantic import BaseModel

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Result

from litestar import Litestar, Request, get, post, put, delete
from litestar.utils.module_loader import module_to_os_path
from litestar.datastructures import State
from advanced_alchemy.extensions.litestar import (
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
    AlembicAsyncConfig,
)
from advanced_alchemy.base import UUIDAuditBase
from litestar.exceptions import (
    ClientException,
    NotFoundException,
    NotAuthorizedException,
    InternalServerException,
    HTTPException,
    ValidationException,
)
from litestar.status_codes import HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from litestar.config.cors import CORSConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.response import Template, Redirect, Stream
from litestar.connection import ASGIConnection
from litestar.handlers.base import BaseRouteHandler
from litestar.response.redirect import ASGIRedirectResponse
from litestar.types import ASGIApp, Scope, Receive, Send
from litestar.datastructures.secret_values import SecretString
from litestar.middleware.base import MiddlewareProtocol
from litestar.middleware.session.client_side import CookieBackendConfig
from litestar.response import File

from app.logger import logger
from app import services, jobs
from app.services.base import Service, ServiceStatus
from app.services.speech_recognition import SpeechRecognitionConfig
from app.services.text_generation import TextGenerationConfig
from app.jobs.base import BatchJob, BatchJobStatus
from app.jobs.speech_recognition import SpeechRecognitionBatchConfig
from app.config import config as blackfish_config
from app.utils import find_port
from app.models.profile import (
    deserialize_profiles,
    deserialize_profile,
    SlurmProfile,
    LocalProfile,
    BlackfishProfile as Profile,
)
from app.models.model import Model
from app.job import JobConfig, JobScheduler, SlurmJobConfig


def load_service_classes() -> dict[str, Type[Service]]:
    service_classes: dict[str, Type[Service]] = {}
    directory = Path(services.__path__[0])
    for file in directory.glob("*.py"):
        if not file.stem.startswith("_") and not file.stem == "base":
            module = import_module(f"app.{directory.stem}.{file.stem}")
            for k, v in module.__dict__.items():
                if isinstance(v, type) and v.__bases__[0] == Service:
                    service_classes[file.stem] = v
                    logger.debug(f"Added class {k} to service class dictionary.")

    return service_classes


service_classes = load_service_classes()


def load_batch_job_classes() -> dict[str, Type[BatchJob]]:
    batch_job_classes: dict[str, Type[BatchJob]] = {}
    directory = Path(jobs.__path__[0])
    for file in directory.glob("*.py"):
        if not file.stem.startswith("_") and not file.stem == "base":
            module = import_module(f"app.{directory.stem}.{file.stem}")
            for k, v in module.__dict__.items():
                if isinstance(v, type) and v.__bases__[0] == BatchJob:
                    batch_job_classes[file.stem] = v
                    logger.debug(f"Added class {k} to batch job class dictionary.")

    return batch_job_classes


batch_job_classes = load_batch_job_classes()


ContainerConfig = TextGenerationConfig | SpeechRecognitionConfig
BatchContainerConfig = SpeechRecognitionBatchConfig

# --- Auth ---
AUTH_TOKEN: Optional[bytes] = None
if blackfish_config.AUTH_TOKEN is not None:
    AUTH_TOKEN = bcrypt.hashpw(blackfish_config.AUTH_TOKEN.encode(), bcrypt.gensalt())
else:
    AUTH_TOKEN = None
    logger.warning("AUTH_TOKEN is not set. Blackfish API endpoints are unprotected.")


class AuthMiddleware(MiddlewareProtocol):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__()
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if Request(scope).session is None:
            logger.debug(
                "(AuthMiddleware) No session found. Redirecting to dashboard login."
            )
            response = ASGIRedirectResponse(path=f"{blackfish_config.BASE_PATH}/login")
            await response(scope, receive, send)
        elif Request(scope).session.get("token") is None:
            logger.debug(
                "(AuthMiddleware) No token found. Redirecting to dashboard login."
            )
            response = ASGIRedirectResponse(path=f"{blackfish_config.BASE_PATH}/login")
            await response(scope, receive, send)
        else:
            logger.debug(
                "(AuthMiddleware) Found session token!"
            )  # Request(scope).session
            await self.app(scope, receive, send)


def auth_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:  # type: ignore
    if AUTH_TOKEN is None:
        logger.error("AUTH_TOKEN is not set. Cannot authenticate user.")
        raise InternalServerException(detail="Authentication token is not set.")
    token = connection.session.get("token")
    if token is None:
        logger.debug("Session token is None. Raising NotAuthorizedException.")
        raise NotAuthorizedException
    if not bcrypt.checkpw(token.encode(), AUTH_TOKEN):
        logger.debug("Invalid token provided. Raising NotAuthorizedException.")
        raise NotAuthorizedException


PAGE_MIDDLEWARE = [] if blackfish_config.DEBUG else [AuthMiddleware]
ENDPOINT_GUARDS = [] if blackfish_config.DEBUG else [auth_guard]
if not blackfish_config.DEBUG:
    logger.info(
        f"Blackfish API is protected with AUTH_TOKEN = {blackfish_config.AUTH_TOKEN}"
    )
else:
    logger.warning(
        """Blackfish is running in debug mode. API endpoints are unprotected. In a production
          environment, set BLACKFISH_DEBUG=0 to require user authentication."""
    )


# --- Utils ---
async def get_service(service_id: str, session: AsyncSession) -> Service | None:
    """Query a single service ID from the application database and raise a `NotFoundException`
    if the service is missing.
    """
    query = sa.select(Service).where(Service.id == service_id)
    res = await session.execute(query)
    try:
        return res.scalar_one()
    except NoResultFound:
        logger.error(f"Service {service_id} not found.")
        return None


async def get_batch_job(job_id: str, session: AsyncSession) -> BatchJob | None:
    """Query a single batch job ID from the application database and raise a `NotFoundException`
    if the service is missing.
    """
    query = sa.select(BatchJob).where(BatchJob.id == job_id)
    res = await session.execute(query)
    try:
        return res.scalar_one()
    except NoResultFound:
        logger.error(f"Batch job {job_id} not found.")
        return None


ModelInfoResult = dict[str, str]


def model_info(profile: Profile) -> Tuple[ModelInfoResult, ModelInfoResult]:
    if not profile.is_local():
        logger.error("Profile should be local.")
        raise Exception("Profile should be local.")

    cache_dir = Path(*[profile.cache_dir, "models", "info.json"])
    try:
        with open(cache_dir, "r") as f:
            cache_info = json.load(f)
    except OSError as e:
        logger.error(f"Failed to open cache info.json: {e}.")
        cache_info = dict()
    home_dir = Path(*[profile.home_dir, "models", "info.json"])
    try:
        with open(home_dir, "r") as f:
            home_info = json.load(f)
    except OSError as e:
        logger.error(f"Failed to open home info.json: {e}.")
        home_info = dict()
    return cache_info, home_info


def remote_model_info(
    profile: Profile, sftp: SFTPClient
) -> Tuple[ModelInfoResult, ModelInfoResult]:
    if not isinstance(profile, SlurmProfile):
        raise Exception("Profile should be a SlurmProfile.")

    cache_dir = os.path.join(profile.cache_dir, "models", "info.json")
    try:
        with sftp.open(cache_dir, "r") as f:
            cache_info = json.load(f)
    except Exception as e:
        logger.error(f"Failed to open remote cache info.json: {e}")
        cache_info = dict()
    home_dir = os.path.join(profile.home_dir, "models", "info.json")
    try:
        with sftp.open(home_dir, "r") as f:
            home_info = json.load(f)
    except Exception as e:
        logger.error(f"Failed to open remote home info.json: {e}")
        home_info = dict()
    return cache_info, home_info


async def find_models(profile: Profile) -> list[Model]:
    """Find all model revisions associated with a given profile.

    The model files associated with a given profile are determined by the contents
    found in `profile.home_dir` and `profile.cache_dir`. We assume that model files
    are stored using the same schema as Hugging Face.
    """
    models = []
    revisions = []
    if isinstance(profile, SlurmProfile) and not profile.is_local():
        logger.debug(f"Connecting to sftp::{profile.user}@{profile.host}")
        with (
            Connection(host=profile.host, user=profile.user) as conn,
            conn.sftp() as sftp,
        ):
            cache_info, home_info = remote_model_info(profile, sftp=sftp)
            cache_dir = os.path.join(profile.cache_dir, "models")
            logger.debug(f"Searching cache directory {cache_dir}")
            try:
                model_dirs = sftp.listdir(cache_dir)
                for model_dir in filter(lambda x: x.startswith("models--"), model_dirs):
                    _, namespace, model = model_dir.split("--")
                    repo = f"{namespace}/{model}"
                    logger.debug(f"Found model {repo}")
                    image = cache_info.get(repo)
                    if image is None:
                        logger.warning(
                            f"No image info found for model {repo} in {cache_dir}!"
                        )
                        image = "missing"
                    for revision in sftp.listdir(
                        os.path.join(cache_dir, model_dir, "snapshots")
                    ):
                        if revision not in revisions:
                            logger.debug(f"Found revision {revision}")
                            models.append(
                                Model(
                                    repo=repo,
                                    profile=profile.name,
                                    revision=revision,
                                    image=image,
                                    model_dir=os.path.join(cache_dir, model_dir),
                                )
                            )
                            revisions.append(revision)
            except FileNotFoundError as e:
                logger.error(f"Failed to list directory: {e}")

            home_dir = os.path.join(profile.home_dir, "models")
            logger.debug(f"Searching home directory: {home_dir}")
            try:
                model_dirs = sftp.listdir(home_dir)
                for model_dir in filter(lambda x: x.startswith("models--"), model_dirs):
                    _, namespace, model = model_dir.split("--")
                    repo = f"{namespace}/{model}"
                    logger.debug("Found model {repo}")
                    image = home_info.get(repo)
                    if image is None:
                        logger.warning(
                            f"No image info found for model {repo} in {home_dir}!"
                        )
                        image = "missing"
                    for revision in sftp.listdir(
                        os.path.join(home_dir, model_dir, "snapshots")
                    ):
                        if revision not in revisions:
                            logger.debug(f"Found revision {revision}")
                            models.append(
                                Model(
                                    repo=repo,
                                    profile=profile.name,
                                    revision=revision,
                                    image=image,
                                    model_dir=os.path.join(home_dir, model_dir),
                                )
                            )
                            revisions.append(revision)
            except FileNotFoundError as e:
                logger.error(f"Failed to list directory: {e}")
            return models
    else:
        cache_info, home_info = model_info(profile)
        cache_dir = os.path.join(profile.cache_dir, "models")
        logger.debug(f"Searching cache directory {cache_dir}")
        try:
            model_dirs = os.listdir(cache_dir)
            for model_dir in filter(lambda x: x.startswith("models--"), model_dirs):
                _, namespace, model = model_dir.split("--")
                repo = f"{namespace}/{model}"
                logger.debug(f"Found model {repo}")
                image = cache_info.get(repo)
                if image is None:
                    logger.warning(
                        f"No image info found for model {repo} in {cache_dir}!"
                    )
                    image = "missing"
                for revision in os.listdir(
                    os.path.join(cache_dir, model_dir, "snapshots")
                ):
                    if revision not in revisions:
                        logger.debug(f"Found revision {revision}")
                        models.append(
                            Model(
                                repo=repo,
                                profile=profile.name,
                                revision=revision,
                                image=image,
                                model_dir=os.path.join(cache_dir, model_dir),
                            )
                        )
                        revisions.append(revision)
        except FileNotFoundError as e:
            logger.error(f"Failed to list directory: {e}")

        home_dir = os.path.join(profile.home_dir, "models")
        logger.debug(f"Searching home directory: {home_dir}")
        try:
            model_dirs = os.listdir(home_dir)
            for model_dir in filter(lambda x: x.startswith("models--"), model_dirs):
                _, namespace, model = model_dir.split("--")
                repo = f"{namespace}/{model}"
                logger.debug(f"Found model {repo}")
                image = home_info.get(repo)
                if image is None:
                    logger.warning(
                        f"No image info found for model {repo} in {home_dir}!"
                    )
                    image = "missing"
                for revision in os.listdir(
                    os.path.join(home_dir, model_dir, "snapshots")
                ):
                    if revision not in revisions:
                        logger.debug(f"Found revision {revision}")
                        models.append(
                            Model(
                                repo=repo,
                                profile=profile.name,
                                revision=revision,
                                image=image,
                                model_dir=os.path.join(home_dir, model_dir),
                            )
                        )
                        revisions.append(revision)
        except FileNotFoundError as e:
            logger.error(f"Failed to list directory: {e}")
        return list(models)


# --- Pages ---
@get("/", middleware=PAGE_MIDDLEWARE)
async def index() -> Redirect:
    return Redirect(f"{blackfish_config.BASE_PATH}/dashboard")


@get(path="/dashboard", middleware=PAGE_MIDDLEWARE)
async def dashboard() -> Template:
    return Template(template_name="dashboard.html")


@get(path="/login")
async def dashboard_login(request: Request) -> Template | Redirect:  # type: ignore
    if AUTH_TOKEN is None:
        logger.error("AUTH_TOKEN is not set. Redirecting to dashboard.")
        return Redirect(f"{blackfish_config.BASE_PATH}/dashboard")
    token = request.session.get("token")
    if token is not None:
        if bcrypt.checkpw(token.encode(), AUTH_TOKEN):
            logger.debug("User authenticated. Redirecting to dashboard.")
            return Redirect(f"{blackfish_config.BASE_PATH}/dashboard")

    logger.debug("User not authenticated. Returning login page.")
    return Template(template_name="login.html")


@get(path="/text-generation", middleware=PAGE_MIDDLEWARE)
async def text_generation() -> Template:
    return Template(template_name="text-generation.html")


@get(path="/speech-recognition", middleware=PAGE_MIDDLEWARE)
async def speech_recognition() -> Template:
    return Template(template_name="speech-recognition.html")


# --- Endpoints ---
@get("/api/info", guards=ENDPOINT_GUARDS)
async def info(state: State) -> dict[str, Any]:
    return {
        "HOST": state.HOST,
        "PORT": state.PORT,
        "STATIC_DIR": state.STATIC_DIR,
        "HOME_DIR": state.HOME_DIR,
        "DEBUG": state.DEBUG,
        "CONTAINER_PROVIDER": state.CONTAINER_PROVIDER,
    }


@post("/api/login")
async def login(token: SecretString | None, request: Request) -> Optional[Redirect]:  # type: ignore
    if AUTH_TOKEN is None:
        logger.error("AUTH_TOKEN is not set. Cannot authenticate user.")
        raise InternalServerException(detail="Authentication token is not set.")
    session_token = request.session.get("token")
    if session_token is not None:
        if bcrypt.checkpw(session_token.encode(), AUTH_TOKEN):
            logger.debug("User logged in with session token. Redirecting to dashboard.")
            return Redirect(f"{blackfish_config.BASE_PATH}/dashboard")
    if token is not None:
        if bcrypt.checkpw(token.get_secret().encode(), AUTH_TOKEN):
            logger.debug(
                "Authentication token verified. Adding token to session and redirecting to dashboard."
            )
            request.set_session({"token": token.get_secret()})
            return Redirect(f"{blackfish_config.BASE_PATH}/dashboard")
        else:
            logger.debug("Invalid token provided. Redirecting to login.")
            return Redirect(f"{blackfish_config.BASE_PATH}/login?success=false")
    else:
        logger.debug("No token provided. Redirecting to login.")
        return Redirect(f"{blackfish_config.BASE_PATH}/login?success=false")


@post("/api/logout", guards=ENDPOINT_GUARDS)
async def logout(request: Request) -> Redirect:  # type: ignore
    token = request.session.get("token")
    if token is not None:
        request.set_session({"token": None})
        logger.debug("from logout: reset session.")
    return Redirect(f"{blackfish_config.BASE_PATH}/login")


@dataclass
class FileStats:
    name: str
    path: str
    is_dir: bool
    size: int  # bytes
    created_at: datetime
    modified_at: datetime


def listdir(path: str, hidden: bool = False) -> list[FileStats]:
    scan_iter = os.scandir(path)
    if not hidden:
        items = list(filter(lambda x: not x.name.startswith("."), scan_iter))
    else:
        items = list(scan_iter)
    return [
        FileStats(
            name=item.name,
            path=item.path,
            is_dir=item.is_dir(),
            size=item.stat().st_size,
            created_at=datetime.fromtimestamp(item.stat().st_ctime),
            modified_at=datetime.fromtimestamp(item.stat().st_mtime),
        )
        for item in items
    ]


@get("/api/files", guards=ENDPOINT_GUARDS)
async def get_files(
    path: str,
    hidden: bool = False,
) -> list[FileStats] | HTTPException:
    if os.path.isdir(path):
        try:
            return listdir(path, hidden=hidden)
        except PermissionError:
            logger.debug("Permission error raised")
            raise NotAuthorizedException(f"User not authorized to access {path}")
    else:
        logger.debug("Not found error")
        raise NotFoundException(detail=f"Path {path} does not exist.")


@get("/api/audio", guards=ENDPOINT_GUARDS, media_type="audio/wav")
async def get_audio(path: str) -> File | None:
    if os.path.isfile(path):
        if path.endswith(".wav") or path.endswith(".mp3"):
            return File(path=path)
        else:
            raise ValidationException("Path should specify a .wav or .mp3 file.")
    else:
        raise NotFoundException(f"{path} not found.")


@get("/api/ports", guards=ENDPOINT_GUARDS)
async def get_ports(request: Request) -> int:  # type: ignore
    """Find an available port on the server. This endpoint allows a UI to run local services."""
    return find_port()


class ServiceRequest(BaseModel):
    name: str
    image: str
    repo_id: str
    profile: Profile
    container_config: ContainerConfig
    job_config: JobConfig
    mount: Optional[str] = None
    grace_period: int = 180  # seconds


@dataclass
class StopServiceRequest:
    timeout: bool = False
    failed: bool = False


def build_service(data: ServiceRequest) -> Optional[Service]:
    """Convert a service request into a service object based on the requested image."""

    ServiceClass = service_classes.get(data.image)
    if ServiceClass is not None:
        flattened = {
            "name": data.name,
            "model": data.repo_id,
            "profile": data.profile.name,
            "home_dir": data.profile.home_dir,
            "cache_dir": data.profile.cache_dir,
            "mount": data.mount,
            "grace_period": data.grace_period,
        }
        if isinstance(data.profile, LocalProfile):
            flattened["host"] = "localhost"
            flattened["provider"] = blackfish_config.CONTAINER_PROVIDER
        if isinstance(data.profile, SlurmProfile) and isinstance(
            data.job_config, SlurmJobConfig
        ):
            flattened["host"] = data.profile.host
            flattened["user"] = data.profile.user
            flattened["time"] = data.job_config.time
            flattened["ntasks_per_node"] = data.job_config.ntasks_per_node
            flattened["mem"] = data.job_config.mem
            flattened["gres"] = data.job_config.gres
            flattened["partition"] = data.job_config.partition
            flattened["constraint"] = data.job_config.constraint
            flattened["scheduler"] = JobScheduler.Slurm

        return ServiceClass(**flattened)

    else:
        logger.error(f"build_service received unrecognized image {data.image}")
        return None


@post("/api/services", guards=ENDPOINT_GUARDS)
async def run_service(
    data: ServiceRequest,
    session: AsyncSession,
    state: State,
) -> Optional[Service]:
    service = build_service(data)
    if service is not None:
        try:
            await service.start(
                session,
                state,
                container_options=data.container_config,
                job_options=data.job_config,
            )
        except Exception as e:
            detail = f"Unable to start service. Error: {e}"
            logger.error(detail)
            raise InternalServerException(detail=detail)

    return service


@put("/api/services/{service_id:str}/stop", guards=ENDPOINT_GUARDS)
async def stop_service(
    service_id: str, data: StopServiceRequest, session: AsyncSession, state: State
) -> Service:
    service = await get_service(service_id, session)
    if service is None:
        raise NotFoundException(detail="Service not found")

    await service.stop(session, timeout=data.timeout, failed=data.failed)
    return service


@get("/api/services/{service_id:str}", guards=ENDPOINT_GUARDS)
async def refresh_service(
    service_id: str, session: AsyncSession, state: State
) -> Optional[Service]:
    service = await get_service(service_id, session)
    if service is None:
        raise NotFoundException(detail="Service not found")

    await service.refresh(session, state)
    return service


@get("/api/services", guards=ENDPOINT_GUARDS)
async def fetch_services(
    session: AsyncSession,
    state: State,
    id: Optional[str] = None,
    image: Optional[str] = None,
    model: Optional[str] = None,
    status: Optional[str] = None,
    port: Optional[int] = None,
    name: Optional[str] = None,
    profile: Optional[str] = None,
) -> list[Service]:
    query_params = {
        "id": id,
        "image": image,
        "model": model,
        "status": status,
        "port": port,
        "name": name,
        "profile": profile,
    }

    query_params = {k: v for k, v in query_params.items() if v is not None}
    query = sa.select(Service).filter_by(**query_params)
    res = await session.execute(query)
    services = res.scalars().all()

    await asyncio.gather(*[s.refresh(session, state) for s in services])

    return list(services)


@delete("/api/services", guards=ENDPOINT_GUARDS, status_code=200)
async def delete_service(
    session: AsyncSession,
    state: State,
    id: Optional[str] = None,
    image: Optional[str] = None,
    model: Optional[str] = None,
    status: Optional[str] = None,
    port: Optional[int] = None,
    name: Optional[str] = None,
    profile: Optional[str] = None,
) -> list[dict[str, str]]:
    query_params = {
        "id": id,
        "image": image,
        "model": model,
        "status": status,
        "port": port,
        "name": name,
        "profile": profile,
    }

    query_params = {k: v for k, v in query_params.items() if v is not None}
    query = sa.select(Service).filter_by(**query_params)
    query_res = await session.execute(query)
    services = query_res.scalars().all()

    if len(services) == 0:
        logger.warning(
            f"The query parameters {query_params} did not match any services."
        )
        return []

    await asyncio.gather(*[s.refresh(session, state) for s in services])

    res = []
    for service in services:
        if service.status in [
            ServiceStatus.STOPPED,
            ServiceStatus.TIMEOUT,
            ServiceStatus.FAILED,
            None,
        ]:
            logger.debug(f"Queueing service {service.id} for deletion")
            deletion = sa.delete(Service).where(Service.id == service.id)
            try:
                await session.execute(deletion)
            except Exception as e:
                raise InternalServerException(
                    detail=f"An error occurrred while attempting to delete service {service.id.hex}: {e}"
                )
            try:
                job = service.get_job()
                if job is not None:
                    job.remove()
            except Exception as e:
                logger.warning(
                    f"Unable to remove job for service {service.id.hex}: {e}"
                )
            res.append(
                {
                    "id": service.id.hex,
                    "status": "ok",
                }
            )
        else:
            logger.warning(
                f"Service is still running (status={service.status}). Aborting delete."
            )
            res.append(
                {
                    "id": service.id.hex,
                    "status": "error",
                    "message": "Service is still running",
                }
            )

    return res


@delete("/api/services/prune", guards=ENDPOINT_GUARDS, status_code=200)
async def prune_services(session: AsyncSession, state: State) -> int:
    query = sa.select(Service).where(
        Service.status.in_(
            [
                ServiceStatus.STOPPED,
                ServiceStatus.TIMEOUT,
                ServiceStatus.FAILED,
            ]
        )
    )
    res = await session.execute(query)
    services = res.scalars().all()

    if len(services) == 0:
        return 0

    await asyncio.gather(*[s.refresh(session, state) for s in services])

    count = 0
    for service in services:
        logger.debug(f"Queueing service {service.id} for deletion")
        deletion = sa.delete(Service).where(Service.id == service.id)
        try:
            await session.execute(deletion)
        except Exception as e:
            raise InternalServerException(
                detail=f"An error occurrred while attempting to delete service {service.id.hex}: {e}"
            )
        try:
            job = service.get_job()
            if job is not None:
                job.remove()
        except Exception as e:
            logger.warning(f"Unable to remove job for service {service.id.hex}: {e}")
            raise InternalServerException(
                detail=f"An error occurrred while attempting to delete service {service.id.hex}: {e}"
            )
        count += 1

    return count


class BatchJobRequest(BaseModel):
    name: str
    pipeline: str
    repo_id: str
    profile: Profile
    job_config: JobConfig
    container_config: BatchContainerConfig
    mount: str


def build_batch_job(data: BatchJobRequest) -> BatchJob | None:
    """Convert a batch job request into a batch job object based on the requested pipeline."""

    BatchJobClass = batch_job_classes.get(data.pipeline)
    logger.debug(f"BatchJobClass: {BatchJobClass}")
    if BatchJobClass is not None:
        flattened = {
            "name": data.name,
            "repo_id": data.repo_id,
            "profile": data.profile.name,
            "home_dir": data.profile.home_dir,
            "cache_dir": data.profile.cache_dir,
            "mount": data.mount,
        }

        if isinstance(data.profile, LocalProfile):
            flattened["host"] = "localhost"
            if blackfish_config.CONTAINER_PROVIDER is None:
                logger.error(
                    "Failed to build batch job: blackfish config is missing a container provider"
                )
                return None
            flattened["provider"] = blackfish_config.CONTAINER_PROVIDER
        elif isinstance(data.profile, SlurmProfile):
            flattened["user"] = data.profile.user
            flattened["host"] = data.profile.host
            flattened["scheduler"] = JobScheduler.Slurm

        logger.debug("Creating batch job")
        batch_job = BatchJobClass(**flattened)
        logger.debug(f"Batch job created: {batch_job}")
        return batch_job

    else:
        logger.error(
            f"Failed to build batch job: unrecognized pipeline {data.pipeline}"
        )
        return None


@post("/api/jobs", guards=ENDPOINT_GUARDS)
async def run_job(
    data: BatchJobRequest,
    session: AsyncSession,
    state: State,
) -> BatchJob | None:
    logger.debug(f"Received job request: {data}")

    logger.debug("Building batch job...")
    batch_job = build_batch_job(data)

    if batch_job is not None:
        logger.debug("Attempting to start batch job...")
        try:
            await batch_job.start(
                session,
                state,
                job_options=data.job_config,
                container_options=data.container_config,
            )
        except Exception as e:
            detail = f"Unable to start batch job. Error: {e}"
            logger.error(detail)
            raise InternalServerException(detail=detail)

    return batch_job


@get("/api/jobs", guards=ENDPOINT_GUARDS)
async def fetch_jobs(
    session: AsyncSession,
    state: State,
    id: Optional[str] = None,
    pipeline: Optional[str] = None,
    repo_id: Optional[str] = None,
    status: Optional[str] = None,
    name: Optional[str] = None,
    profile: Optional[str] = None,
) -> list[BatchJob]:
    query_params = {
        "id": id,
        "pipeline": pipeline,
        "repo_id": repo_id,
        "status": status,
        "name": name,
        "profile": profile,
    }

    query_params = {k: v for k, v in query_params.items() if v is not None}
    query = sa.select(BatchJob).filter_by(**query_params)
    logger.debug(f"Executing query {query}...")
    res = await session.execute(query)
    jobs = res.scalars().all()
    logger.debug(f"Found {len(jobs)} matching batch jobs.")

    await asyncio.gather(*[s.update(session, state) for s in jobs])

    return list(jobs)


@get("/api/jobs/{id:str}", guards=ENDPOINT_GUARDS)
async def get_job(
    id: str,
    session: AsyncSession,
    state: State,
) -> BatchJob | None:
    """Fetch a job by its ID."""
    query = sa.select(BatchJob).where(BatchJob.id == id)
    res = await session.execute(query)
    try:
        return res.scalar_one()
    except NoResultFound:
        raise NotFoundException(detail=f"Job {id} not found")
    except Exception as e:
        logger.error(f"Failed to execute query: {e}")
        raise InternalServerException(
            detail="An error occurred while fetching the job."
        )


@put("/api/jobs/{job_id:str}/stop", guards=ENDPOINT_GUARDS)
async def stop_job(
    job_id: str,
    session: AsyncSession,
    state: State,
) -> BatchJob | None:
    """Stop a job by its ID."""
    job = await get_batch_job(job_id, session)
    if job is None:
        logger.debug("HERE")
        raise NotFoundException(detail=f"Job {job_id} not found")

    try:
        await job.stop(session, state)
        return job
    except Exception as e:
        logger.error(f"Failed to stop job {job_id}: {e}")
        raise InternalServerException(
            detail="An error occurred while stopping the job."
        )


@dataclass
class DeleteBatchJobResponse:
    job_id: str
    status: str
    message: Optional[str] = None


@delete("/api/jobs", guards=ENDPOINT_GUARDS, status_code=200)
async def delete_job(
    session: AsyncSession,
    state: State,
    id: Optional[str] = None,
    pipeline: Optional[str] = None,
    model: Optional[str] = None,
    status: Optional[str] = None,
    name: Optional[str] = None,
    profile: Optional[str] = None,
) -> list[DeleteBatchJobResponse] | None:
    """Delete batch jobs matching the provided query parameters."""

    query_params = {
        "id": id,
        "pipeline": pipeline,
        "model": model,
        "status": status,
        "name": name,
        "profile": profile,
    }

    query_params = {k: v for k, v in query_params.items() if v is not None}
    query = sa.select(BatchJob).filter_by(**query_params)
    logger.debug(f"Executing query {query}...")
    query_res = await session.execute(query)
    jobs = query_res.scalars().all()
    logger.debug(f"Found {len(jobs)} matching batch jobs.")

    if len(jobs) == 0:
        logger.warning(
            f"The query parameters {query_params} did not match any batch jobs."
        )
        return []

    await asyncio.gather(*[s.update(session, state) for s in jobs])

    res = []
    for batch_job in jobs:
        if batch_job.status in [
            BatchJobStatus.STOPPED,
            BatchJobStatus.TIMEOUT,
            BatchJobStatus.FAILED,
            BatchJobStatus.COMPLETED,
            None,
        ]:
            logger.debug(f"Queueing batch job {batch_job.id} for deletion")
            deletion = sa.delete(BatchJob).where(BatchJob.id == batch_job.id)
            try:
                await session.execute(deletion)
            except Exception as e:
                raise InternalServerException(
                    detail=f"An error occurrred while attempting to delete batch job {batch_job.id.hex}: {e}"
                )
            try:
                job = batch_job.get_job()
                if job is not None:
                    job.remove()
            except Exception as e:
                logger.warning(
                    f"Unable to remove job for batch job {batch_job.id.hex}: {e}"
                )
            res.append(DeleteBatchJobResponse(job_id=batch_job.id.hex, status="ok"))
        else:
            logger.warning(
                f"Batch job is still running (status={batch_job.status}). Aborting delete."
            )
            res.append(
                DeleteBatchJobResponse(
                    job_id=batch_job.id.hex,
                    status="error",
                    message="Batch job is still running",
                )
            )

    return res


async def asyncpost(url: StrOrURL, data: Any, headers: Any) -> Any:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as response:
            return await response.json()


@post(
    [
        "/proxy/{port:int}/{cmd:str}",
        "/proxy/{port:int}/{ver:str}/{cmd:path}",
    ],
    guards=ENDPOINT_GUARDS,
)
async def proxy_service(
    data: dict[Any, Any],
    port: int,
    ver: Optional[str],
    cmd: str,
    streaming: Optional[bool],
    session: AsyncSession,
    state: State,
) -> Any | Stream:
    """Call a service via proxy and return the response.

    Setting query parameter `streaming` to `True` streams the response.
    """

    if ver is not None:
        url = f"http://localhost:{port}/{ver}{cmd}"
    else:
        url = f"http://localhost:{port}/{cmd}"

    if streaming:

        async def generator() -> AsyncGenerator:  # type: ignore
            headers = {"Content-Type": "application/json"}
            with requests.post(url, json=data, headers=headers, stream=True) as res:
                for x in res.iter_content(chunk_size=None):
                    if x:
                        yield x

        return Stream(generator)
    else:
        res = await asyncpost(
            url,
            json.dumps(data),
            {"Content-Type": "application/json"},
        )
        return res


@get("/api/models", guards=ENDPOINT_GUARDS)
async def get_models(
    session: AsyncSession,
    state: State,
    profile: Optional[str] = None,
    image: Optional[str] = None,
    refresh: Optional[bool] = False,
) -> list[Model]:
    profiles = deserialize_profiles(state.HOME_DIR)

    res: list[list[Model]] | Result[Tuple[Model]]
    if refresh:
        if profile is not None:
            matched = next((p for p in profiles if p.name == profile), None)
            if matched is None:
                logger.warning(
                    f"Profile '{profile}' not found. Returning an empty list."
                )
                return list()
            models = await find_models(matched)
            logger.debug(
                "Deleting existing models WHERE model.profile == '{profile}'..."
            )
            try:
                delete_query = sa.delete(Model).where(Model.profile == profile)
                await session.execute(delete_query)
            except Exception as e:
                logger.error(f"Failed to execute query: {e}")
        else:
            res = await asyncio.gather(*[find_models(profile) for profile in profiles])
            models = list(itertools.chain(*res))  # list[list[dict]] -> list[dict]
            logger.debug("Deleting all existing models...")
            try:
                delete_all_query = sa.delete(Model)
                await session.execute(delete_all_query)
            except Exception as e:
                logger.error(f"Failed to execute query: {e}")
        logger.debug("Inserting refreshed models...")
        session.add_all(models)
        try:
            await session.flush()
        except Exception as e:
            logger.error(f"Failed to execute transaction: {e}")
        if image is not None:
            return sorted(
                list(filter(lambda x: x.image == image, models)),
                key=lambda x: x.repo.lower(),
            )
        else:
            return sorted(models, key=lambda x: x.repo.lower())
    else:
        logger.info("Querying model table...")

        query_filter = {}
        if profile is not None:
            query_filter["profile"] = profile
        if image is not None:
            query_filter["image"] = image

        select_query = (
            sa.select(Model)
            .filter_by(**query_filter)
            .order_by(sa.func.lower(Model.repo))
        )
        try:
            res = await session.execute(select_query)
            return list(res.scalars().all())
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            return []


@get("/api/models/{model_id:str}", guards=ENDPOINT_GUARDS)
async def get_model(model_id: str, session: AsyncSession) -> Model:
    logger.info(f"Model={model_id}")
    query = sa.select(Model).where(Model.id == model_id)
    res = await session.execute(query)
    try:
        return res.scalar_one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"Model {model_id} not found") from e


@post("/api/models", guards=ENDPOINT_GUARDS)
async def create_model(data: Model, session: AsyncSession) -> Model:
    session.add(data)
    return data


@delete("/api/models/{model_id:str}", guards=ENDPOINT_GUARDS)
async def delete_model(model_id: str, session: AsyncSession) -> None:
    query = sa.delete(Model).where(Model.id == model_id)
    await session.execute(query)


@get("/api/profiles", guards=ENDPOINT_GUARDS)
async def read_profiles() -> list[Profile]:
    try:
        return deserialize_profiles(blackfish_config.HOME_DIR)
    except FileNotFoundError:
        raise NotFoundException(detail="Profiles config not found.")


@get("/api/profiles/{name: str}", guards=ENDPOINT_GUARDS)
async def read_profile(name: str) -> Profile | None:
    try:
        profile = deserialize_profile(blackfish_config.HOME_DIR, name)
    except Exception as e:
        raise InternalServerException(detail=f"Failed to deserialize profile: {e}.")

    if profile is not None:
        return profile
    else:
        logger.error("Profile not found.")
        raise NotFoundException(detail="Profile not found.")


# --- Config ---
BASE_DIR = module_to_os_path("app")

db_config = SQLAlchemyAsyncConfig(
    connection_string=f"sqlite+aiosqlite:///{blackfish_config.HOME_DIR}/app.sqlite",
    metadata=UUIDAuditBase.metadata,
    create_all=True,
    alembic_config=AlembicAsyncConfig(
        version_table_name="ddl_version",
        script_config=f"{BASE_DIR}/db/migrations/alembic.ini",
        script_location=f"{BASE_DIR}/db/migrations",
    ),
)


async def session_provider(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as e:
        raise ClientException(
            status_code=HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


cors_config = CORSConfig(
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openapi_config = OpenAPIConfig(
    title="Blackfish API",
    version="0.0.1",
    render_plugins=[SwaggerRenderPlugin(path="/swagger")],
)

template_config = TemplateConfig(
    directory=blackfish_config.STATIC_DIR / "build",
    engine=JinjaTemplateEngine,
)

session_config = CookieBackendConfig(
    secret=urandom(16),
    key="bf_user",
    # samesite="none",
)

next_server = create_static_files_router(
    path="_next",
    directories=[blackfish_config.STATIC_DIR / "build" / "_next"],
    html_mode=True,
)

img_server = create_static_files_router(
    path="img",
    directories=[blackfish_config.STATIC_DIR / "build" / "img"],
    html_mode=True,
)


def not_found_exception_handler(request: Request, exc: Exception) -> Template:  # type: ignore
    return Template(template_name="404.html", status_code=HTTP_404_NOT_FOUND)


app = Litestar(
    path=blackfish_config.BASE_PATH,
    route_handlers=[
        dashboard,
        dashboard_login,
        text_generation,
        speech_recognition,
        index,
        info,
        login,
        logout,
        get_ports,
        get_files,
        get_audio,
        run_service,
        stop_service,
        refresh_service,
        fetch_services,
        delete_service,
        prune_services,
        proxy_service,
        run_job,
        fetch_jobs,
        get_job,
        stop_job,
        delete_job,
        create_model,
        get_model,
        get_models,
        delete_model,
        read_profiles,
        read_profile,
        next_server,
        img_server,
    ],
    dependencies={"session": session_provider},
    plugins=[SQLAlchemyPlugin(db_config)],
    logging_config=None,  # disable Litestar logger (we're using our own)
    state=State(blackfish_config.as_dict()),
    cors_config=cors_config,
    openapi_config=openapi_config,
    template_config=template_config,
    middleware=[session_config.middleware],
    exception_handlers={NotFoundException: not_found_exception_handler},
)
