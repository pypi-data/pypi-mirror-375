# Reboot _Durable_ MCP

A framework for building _durable_ MCP servers.

- Takes advantage of the protocols ability to resume after
  disconnection.

- Allows for the server itself to be restarted(!) and any existing
  requests to be retried safely thanks to Reboot workflows.

_THIS IS IN PRE-ALPHA STAGE, EXPECT CHANGES, BUG FIXES, ETC; DO NOT RUN IN PRODUCTION!_

First grab all dependencies:

```console
uv sync
```

Activate the `venv`:

```console
source .venv/bin/activate
```

Generate code:

```console
rbt generate
```

Make sure you have Docker running:

```console
docker ps
```

And run the test(s):

```console
pytest tests
```

## Publishing to PyPI

1. Tag the release (use semantic versioning):

```console
git tag v0.x.y
```

2. Update the version in `pyproject.toml` to match the tag:

```console
TAG=$(git describe --tags --abbrev=0 | sed 's/^v//')
sed -i "s/^version = \".*\"/version = \"$TAG\"/" pyproject.toml
git add pyproject.toml && git commit -m "chore: set version to $TAG"
```

2. Clean old build artifacts:

```console
rm -rf dist build *.egg-info
```

3. (Ensure deps) Install build + upload tools (if not already in the env):

```console
uv pip install --upgrade build twine
```

4. Build sdist and wheel:

```console
python -m build
```

5. Validate artifacts:

```console
twine check dist/*
```

6. Upload to PyPI:

```console
twine upload dist/*
```

7. Push tag:

```console
git push --follow-tags origin main
```

Notes:

- Ensure `api/` generated code and `reboot/` sources are committed before building.
- If you add new packages or data files update `pyproject.toml` `[tool.hatch.build.targets.wheel].packages` or `MANIFEST.in`.
- Type information is included via `reboot/py.typed`.

### Supported client --> server _requests_:

- [x] `initialize`
- [x] `tools/call`
- [x] `tools/list`
- [ ] `prompts/get`
- [ ] `prompts/list`
- [x] `resources/list`
- [x] `resources/read`
- [x] `resources/templates/list`
- [ ] `resources/subscribe`
- [ ] `resources/unsubscribe`
- [ ] `completion/complete`
- [ ] `logging/setLevel`

### Supported client --> server _notifications_:

- [x] `notifications/initialized`
- [ ] `notifications/roots/list_changed`

### Supported client <-- server _requests_:

- [ ] `elicitation/create`
- [ ] `roots/list`
- [ ] `sampling/createMessage`

### Supported client <-- server _notifications_:

- [x] `notifications/progress`
- [x] `notifications/message`
- [x] `notifications/prompts/list_changed`
- [x] `notifications/resources/list_changed`
- [x] `notifications/tools/list_changed`
- [ ] `notifications/resources/updated`

### Supported client <--> server _notifications_:

- [ ] `notifications/cancelled`

### TODO:

- [x] `EventStore` support for resumability
- [ ] Docs
- [ ] `yapf`
- [ ] Push to `durable-mcp` in pypi.org
- [ ] Pydantic `state` for each session
