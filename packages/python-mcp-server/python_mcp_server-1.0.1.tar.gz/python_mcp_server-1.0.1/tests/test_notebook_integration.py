import asyncio

import os
import socket
import time
import subprocess
import sys
import httpx
import pytest
from fastmcp.client import Client


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_server(base_url: str, timeout: float = 20.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = httpx.get(base_url + "/files/download/does_not_exist.txt")
            if r.status_code in (200, 400, 404):
                return True
        except Exception:
            pass
        time.sleep(0.25)
    return False


@pytest.fixture(scope="module")
def mcp_url_nb():
    port = _get_free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env.setdefault("MPLBACKEND", "Agg")
    env.setdefault("PYTHONUNBUFFERED", "1")
    proc = subprocess.Popen([sys.executable, "src/python_mcp_server/server.py", "--transport", "http", "--port", str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    try:
        ok = _wait_for_server(base_url)
        if not ok:
            try:
                out = proc.stdout.read()
                print("--- notebook server logs ---\n" + (out or ""))
            except Exception:
                pass
            raise RuntimeError("notebook server did not start")
        yield base_url + "/mcp"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


@pytest.mark.asyncio
async def test_notebook_run_and_export(mcp_url_nb: str):
    async with Client(mcp_url_nb) as c:
        # Run a simple plotting cell and capture artifacts
        code = (
            "import matplotlib.pyplot as plt\n"
            "plt.figure()\n"
            "plt.plot([0,1],[1,0])\n"
            "plt.title('nb')\n"
            "plt.show()\n"
        )
        res = await c.call_tool("notebook", {"action": "run", "code": code})
        nb = res.data or res.structured_content or {}
        assert nb.get("status") == "completed"
        notebook_id = nb.get("notebook_id")
        assert notebook_id
        # List cells
        cells = await c.call_tool("notebook", {"action": "cells", "notebook_id": notebook_id})
        idx = cells.data or cells.structured_content or {}
        assert idx.get("cells") and idx["cells"][0]["cell_index"] == 1
        # Export
    # Re-open client to avoid any transport idiosyncrasies between calls
    async with Client(mcp_url_nb) as c2:
        exp = await c2.call_tool("notebook", {"action": "export", "notebook_id": notebook_id, "export_to": "ipynb"})
    payload = exp.data or exp.structured_content or {}
    # Accept fallback to index when nbformat isn't installed
    if payload.get("ipynb"):
        assert payload["ipynb"].endswith(".ipynb")
    else:
        assert payload.get("index") and payload["index"].endswith("index.json")


@pytest.mark.asyncio
async def test_notebook_datasets_duckdb(mcp_url_nb: str):
    async with Client(mcp_url_nb) as c:
        # Ensure duckdb is available
        dep = await c.call_tool("install_dependencies", {"packages": ["duckdb"]})
        dpr = dep.data or dep.structured_content or {}
        assert dpr.get("returncode") == 0

        # Write a tiny CSV dataset
        csv = "x\n1\n2\n3\n"
        wr = await c.call_tool("write_file", {"path": "data/s.csv", "content": csv})
        assert (wr.data or wr.structured_content or {}).get("path") == "data/s.csv"

        # Restart kernel to ensure fresh module search path after install
        await c.call_tool("restart_kernel", {})
        # Register dataset
        reg = await c.call_tool("notebook", {"action": "datasets.register", "dataset_name": "t", "paths": ["data/*.csv"], "format": "csv"})
        r = reg.data or reg.structured_content or {}
        assert r.get("name") == "t" and r.get("schema")

        # Query
        sql = await c.call_tool("notebook", {"action": "datasets.sql", "query": "select sum(x) as s from t"})
        q = sql.data or sql.structured_content or {}
        assert q.get("columns") and q.get("rows")
        assert q.get("result_path") and q["result_path"].endswith(".parquet")


@pytest.mark.asyncio
async def test_notebook_serialization_same_id(mcp_url_nb: str):
    async with Client(mcp_url_nb) as c:
        # Create a notebook and run two cells concurrently; ensure serialized execution
        first = await c.call_tool("notebook", {"action": "run", "code": "a=1; print('first')"})
        nb = first.data or first.structured_content or {}
        notebook_id = nb.get("notebook_id")
        assert notebook_id

        async def run_cell(label):
            code = "import time; print('start'); time.sleep(0.3); print('" + label + "')"
            res = await c.call_tool("notebook", {"action": "run", "notebook_id": notebook_id, "code": code})
            return res.data or res.structured_content or {}

        r1, r2 = await asyncio.gather(run_cell("A"), run_cell("B"))
        # They should be cell 2 and 3 in some order, and not collide
        assert {r1.get("cell_index"), r2.get("cell_index")} == {2, 3}
