# tests/conftest.py
from __future__ import annotations
import os, logging, asyncio
from pathlib import Path
from typing import Iterator, AsyncIterator

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from phrappy import cdh_generator
from phrappy import AsyncPhrappy
from phrappy import Phrappy  # sync client
from phrappy.models import (
    CreateProjectV3Dto, JobCreateRequestDto, UidReference, JobPartDeleteReferences, ProjectDtoV2, JobListDto
)

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default=None, help="Override Phrase TMS base URL")


def pytest_configure(config):
    for m in ["live", "slow", "destructive"]:
        config.addinivalue_line("markers", f"{m}: custom marker registered in pytest.ini")


@pytest.fixture(scope="session", autouse=True)
def _load_env():
    load_dotenv()


def _need_creds_or_skip():
    token = os.getenv("PHRAPPY_TOKEN")
    user = os.getenv("PHRAPPY_USER")
    pwd = os.getenv("PHRAPPY_PASSWORD")
    if not token and not (user and pwd):
        pytest.skip(
            "Set PHRAPPY_TOKEN or PHRAPPY_USER/PHRAPPY_PASSWORD in environment (or .env) to run live tests.",
            allow_module_level=True,
        )
    return token, user, pwd


@pytest.fixture(scope="session")
def base_url(pytestconfig) -> str:
    return pytestconfig.getoption("--base-url") or os.getenv("PHRAPPY_BASE_URL") or "https://cloud.memsource.com/web"


# -------------------------
# SYNC FIXTURES
# -------------------------
@pytest.fixture(scope="session")
def client(base_url) -> Iterator[Phrappy]:
    token, user, pwd = _need_creds_or_skip()
    if token:
        c = Phrappy(token=token, base_url=base_url)
    else:
        c = Phrappy.from_creds(username=user, password=pwd)
        os.environ["PHRAPPY_TOKEN"] = c.token or ""
    yield c


@pytest.fixture
def project(client: Phrappy) -> Iterator[ProjectDtoV2]:
    from datetime import datetime
    name = f"Test Project {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    dto = CreateProjectV3Dto(name=name, sourceLang="en", targetLangs=["sv", "da"])
    p = client.project.create_project_v3(dto)
    try:
        yield p
    finally:
        try:
            client.project.delete_project(p.uid, purge=True)
        except Exception as e:
            logger.warning("Failed to delete project %s: %s", getattr(p, "uid", "?"), e)


@pytest.fixture
def created_jobs(client: Phrappy, project, test_file: Path) -> Iterator[JobListDto]:
    jobs = client.job.create_job(
        project_uid=project.uid,
        content_disposition=cdh_generator(test_file.name),
        file_bytes=test_file.read_bytes(),
        memsource=JobCreateRequestDto(targetLangs=project.targetLangs),
    )
    # Allow server-side processing/indexing to catch up
    import time; time.sleep(5)
    try:
        yield jobs
    finally:
        try:
            if jobs.jobs:
                refs = [UidReference(uid=j.uid) for j in jobs.jobs]
                client.job.delete_parts(project_uid=project.uid,
                                        job_part_delete_references=JobPartDeleteReferences(jobs=refs),
                                        purge=True)
        except Exception as e:
            logger.warning("Failed to delete jobs on teardown: %s", e)


# -------------------------
# ASYNC FIXTURES
# -------------------------
@pytest_asyncio.fixture
async def aclient(base_url) -> AsyncIterator[AsyncPhrappy]:
    token, user, pwd = _need_creds_or_skip()
    if token:
        c = AsyncPhrappy(token=token, base_url=base_url)
    else:
        c = await AsyncPhrappy.from_creds(username=user, password=pwd)
        os.environ["PHRAPPY_TOKEN"] = c.token or ""
    try:
        yield c
    finally:
        await c.aclose()


@pytest_asyncio.fixture
async def aproject(aclient: AsyncPhrappy) -> AsyncIterator[ProjectDtoV2]:
    from datetime import datetime
    name = f"Test Project {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    dto = CreateProjectV3Dto(name=name, sourceLang="en", targetLangs=["sv", "da"])
    p = await aclient.project.create_project_v3(dto)
    try:
        yield p
    finally:
        try:
            await aclient.project.delete_project(p.uid, purge=True)
        except Exception as e:
            logger.warning("Failed to delete project %s: %s", getattr(p, "uid", "?"), e)


@pytest_asyncio.fixture
async def acreated_jobs(aclient: AsyncPhrappy, aproject, test_file: Path) -> AsyncIterator[JobListDto]:
    jobs = await aclient.job.create_job(
        project_uid=aproject.uid,
        content_disposition=cdh_generator(test_file.name),
        file_bytes=test_file.read_bytes(),
        memsource=JobCreateRequestDto(targetLangs=aproject.targetLangs),
    )
    await asyncio.sleep(5)
    try:
        yield jobs
    finally:
        try:
            if jobs.jobs:
                refs = [UidReference(uid=j.uid) for j in jobs.jobs]
                await aclient.job.delete_parts(project_uid=aproject.uid,
                                               job_part_delete_references=JobPartDeleteReferences(jobs=refs),
                                               purge=True)
        except Exception as e:
            logger.warning("Failed to delete jobs on teardown: %s", e)


# -------------------------
# SHARED UTILS
# -------------------------
@pytest.fixture
def test_file(tmp_path: Path) -> Path:
    p = tmp_path / "en_test_ÄöÖÅas£223.txt"
    p.write_bytes(b"Hello world from test txt")
    return p


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def dump_last_responses_on_failure(request):
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed:
        try:
            if "aclient" in request.fixturenames:
                client = request.getfixturevalue("aclient")
            elif "client" in request.fixturenames:
                client = request.getfixturevalue("client")
            else:
                return
            print("\n---- Last API responses (most recent last) ----")
            for r in getattr(client, "last_responses", []):
                try:
                    print(f"{r.status_code} {r.request.method} {r.request.url}")
                except Exception:
                    pass
        except Exception:
            pass
