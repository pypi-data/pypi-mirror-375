# Tarko Agent UI Python SDK

Python SDK for serving [`@tarko/agent-ui-builder`](https://www.npmjs.com/package/@tarko/agent-ui-builder) static assets.

## Quick Start

```bash
pip install tarko-agent-ui
# Or with uv
uv add tarko-agent-ui
```

```python
# Create app.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from tarko_agent_ui import get_agent_ui_html

app = FastAPI()

@app.get("/")
def home():
    return HTMLResponse(get_agent_ui_html(
        base_url="http://localhost:8000/api"
    ))

# Run: uvicorn app:app
# Visit: http://localhost:8000
```

**That's it!** You now have a fully functional Agent UI.

## Configuration

Customize your Agent UI with the `ui_config` parameter:

```python
get_agent_ui_html(
    base_url="http://localhost:8000/api",  # Your agent API endpoint
    ui_config={
        "title": "My Agent",
        "logo": "https://example.com/logo.png",
        "subtitle": "AI assistant for your needs",
        "welcomePrompts": [
            "What can you help me with?",
            "Tell me about your capabilities",
            "Show me an example"
        ]
    }
)
```

## Environment Variables

Use environment variables for flexible deployment:

```bash
AGENT_BASE_URL=http://my-agent.com/api python app.py
```

```python
import os
from tarko_agent_ui import get_agent_ui_html

base_url = os.getenv("AGENT_BASE_URL", "http://localhost:8000/api")
html = get_agent_ui_html(base_url=base_url)
```

## Framework Examples

<details>
<summary><strong>FastAPI</strong> (click to expand)</summary>

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from tarko_agent_ui import get_agent_ui_html

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(get_agent_ui_html(
        base_url="http://localhost:8000/api",
        ui_config={"title": "FastAPI Agent"}
    ))
```
</details>

<details>
<summary><strong>Flask</strong> (click to expand)</summary>

```python
from flask import Flask
from tarko_agent_ui import get_agent_ui_html

app = Flask(__name__)

@app.route('/')
def root():
    return get_agent_ui_html(
        base_url="http://localhost:5000/api",
        ui_config={"title": "Flask Agent"}
    )
```
</details>

<details>
<summary><strong>Django</strong> (click to expand)</summary>

```python
# views.py
from django.http import HttpResponse
from tarko_agent_ui import get_agent_ui_html

def home(request):
    html = get_agent_ui_html(
        base_url="http://localhost:8000/api",
        ui_config={"title": "Django Agent"}
    )
    return HttpResponse(html)
```
</details>

## Complete Example

See [`examples/fastapi_server.py`](examples/fastapi_server.py) for a production-ready FastAPI server with:
- Comprehensive UI configuration
- Error handling
- Environment variable support

```bash
# Try the example
git clone https://github.com/agent-infra/tarko-agent-ui-python.git
cd tarko-agent-ui-python
uv sync
python examples/fastapi_server.py
```

## API Reference

### `get_agent_ui_html(base_url, ui_config=None)` ⭐

Returns configured Agent UI HTML content with injected environment variables.

**Parameters:**
- `base_url` (str): Agent API base URL
- `ui_config` (dict, optional): UI configuration object

**Returns:** Complete HTML string ready for serving

**Note:** This is the recommended approach - no need to mount static files!

### `get_static_path()` (Advanced)

Returns absolute path to bundled static assets.

**Use case:** Only needed if you want to serve static files separately (e.g., for custom routing or CDN setup).

## How It Works

1. **Zero Dependencies**: Pure Python package with no external dependencies
2. **Pre-bundled Assets**: Static assets are included with the package
3. **Framework Agnostic**: Returns HTML strings that work with any Python web framework
4. **No Runtime Downloads**: Everything works offline after installation

## Backend Integration

To connect your Agent backend, implement the [Agent API Protocol](https://github.com/agent-infra/agent-protocol) (documentation coming soon).

## Requirements

- Python 3.8+
- Any Python web framework (FastAPI, Flask, Django, etc.)
