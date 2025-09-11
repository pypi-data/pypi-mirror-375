from phrappy import Phrappy

# phrappy

Typed, batteries-included Python client for **Phrase TMS (Memsource)** generated from the public OpenAPI spec. Comes with both sync and async clients, fully equipped with first-class Pydantic v2 models.

The build process is fully automated and project release is planned to follow the Phrase TMS bi-weekly release cadence. 

> This project is **not** an official Phrase/Memsource SDK. Official documentation can be found at [developers.phrase.com](https://developers.phrase.com/en/api/tms/latest/introduction)

---

## Installation

```bash
pip install phrappy
```

**Requirements:** Python ≥ 3.10

---

## Quickstart

### 1) Authenticate to get a token
Either use your authentication method of choice directly to get a token.
```python
from phrappy import Phrappy
from phrappy.models import LoginDto

pp = Phrappy()
login_response = pp.authentication.login(LoginDto(
    userName="your_name",
    password="<password>"
))
token = login_response.token
pp.close()
```
Or use the convenience method for authenticating and getting a Phrappy instance that carries its token. 
```python
from phrappy import Phrappy

pp = Phrappy.from_creds(username="name@example.com", password="…")
me = pp.authentication.who_am_i()
print(me.user.uid)
pp.close()
```

Using a context manager closes the underlying HTTP client automatically:
```python
from phrappy import Phrappy

with Phrappy(token="<YOUR_TOKEN>") as pp:
    me = pp.authentication.who_am_i()
    print(me.user.userName)
```


### 3) Async usage
```python
import asyncio
from phrappy import AsyncPhrappy

async def main():
    async with AsyncPhrappy(token="<YOUR_TOKEN>") as app:
        me = await app.authentication.who_am_i()
        print(me.user.userName)

asyncio.run(main())
```

---

## Examples

### Create a project and upload a job (multipart)
```python
from pathlib import Path
from phrappy import Phrappy, cdh_generator
from phrappy.models import CreateProjectV3Dto, JobCreateRequestDto

with Phrappy(token="<YOUR_TOKEN>") as pp:
    proj = pp.project.create_project_v3(CreateProjectV3Dto(name="Demo", sourceLang="en", targetLangs=["sv"]))

    p = Path("example.txt"); p.write_text("Hello from phrappy")
    jobs = pp.job.create_job(
        project_uid=proj.uid,
        content_disposition=cdh_generator(p.name),
        file_bytes=p.read_bytes(),
        memsource=JobCreateRequestDto(targetLangs=proj.targetLangs),
    )
    print([j.uid for j in jobs.jobs or []])
```

### List your assigned projects
```python
me = pp.authentication.who_am_i()
page = pp.project.list_assigned_projects(me.user.uid, target_lang=["sv"])  # returns a typed page model
for item in page.content or []:
    print(item.name, item.status)
```

---

## API design

- Typed models everywhere! Inputs/outputs are Pydantic v2 models generated from the OpenAPI. You can pass either a model instance **or** a `dict` for body/header parameters; the client will validate and coerce.
- Rich method docstrings based on operation descriptions and typing information. 
- Every operation exists in both `Phrappy` and `AsyncPhrappy` under the same tag-based namespaces.
- Built on `httpx` with httpx.Client/httpx.AsyncClient under the hood.  

> If you find a mismatch between the API behavior and the generated models, please open an issue with the request/response payloads (redacted) and the package version.

---

## Configuration

- Defaults to `https://cloud.memsource.com/web`. Override via `Phrappy(base_url=...)` or `AsyncPhrappy(base_url=...)`.
- Pass `timeout=` (seconds) to the client constructor. Per-request timeouts are also supported on `make_request` if you wrap custom calls.

---

## Testing

Test suite is being built out and currently focuses on live testing to catch documentation schema drift. Live tests will create and delete assets, costing a handful of words. 

> Will gladly accept pull requests towards completion of test suite! 

```bash
# run fast tests only (default)
pytest -m "not live and not destructive" -q

# run live tests against your account (creates & deletes resources!)
export PHRAPPY_TOKEN=ApiToken_...
pytest -m live -q
```

Env vars used by live tests:
- `PHRAPPY_TOKEN` **or** (`PHRAPPY_USER` and `PHRAPPY_PASSWORD`)
- `PHRAPPY_BASE_URL` (optional)

---

## Roadmap

- Complete the test suite
- Streaming uploads/downloads
- Convenience functions for AsyncJob interactions


---

## Release notes

### 0.1.0
- Complete rewrite of build pipeline with fully automated and repeatable builds.
- Support for polymorph input and output schemas. 
- Slight change in API surface due to schema naming normalization.
- Added context manager support.
- Minimal test suite implemented.

---

## License

MIT

