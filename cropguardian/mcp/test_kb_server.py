"""Protocol test: start the MCP server as a subprocess and speak JSON-RPC over stdio like a client."""

import json
import subprocess
import sys
from pathlib import Path

SERVER = Path(__file__).with_name("kb_server.py")


def session(*messages: dict) -> list[dict]:
    payload = "".join(json.dumps(m) + "\n" for m in messages)
    out = subprocess.run(
        [sys.executable, str(SERVER)], input=payload.encode(), capture_output=True, timeout=30, check=True
    ).stdout.decode("utf-8")
    return [json.loads(line) for line in out.splitlines() if line.strip()]


INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}}}
READY = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def call(i: int, name: str, args: dict) -> dict:
    return {"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": name, "arguments": args}}


def test_handshake_and_tool_list() -> None:
    r = session(INIT, READY, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert len(r) == 2  # the notification gets no reply
    assert r[0]["result"]["protocolVersion"] == "2025-06-18"
    assert r[0]["result"]["serverInfo"]["name"] == "cropguardian-kb"
    assert {t["name"] for t in r[1]["result"]["tools"]} == {"search_kb", "list_diseases", "get_source"}
    assert all(t["annotations"]["readOnlyHint"] for t in r[1]["result"]["tools"])


def test_search_returns_cited_passages_for_a_disease() -> None:
    r = session(INIT, call(2, "search_kb", {"question": "পটাশ", "disease": "rice_blast", "k": 3}))
    data = r[1]["result"]["structuredContent"]
    assert r[1]["result"]["isError"] is False and 1 <= len(data["results"]) <= 3
    assert {x["disease"] for x in data["results"]} == {"rice_blast"}
    assert all(x["source_id"] == "brri_fs04_blast" and x["context"] for x in data["results"])


def test_bad_inputs_are_tool_errors_not_crashes() -> None:
    r = session(
        INIT,
        call(2, "search_kb", {"disease": "not_a_disease"}),
        call(3, "search_kb", {"k": 99}),
        call(4, "get_source", {"source_id": "../../etc/passwd"}),
        call(5, "nope", {}),
        {"jsonrpc": "2.0", "id": 6, "method": "resources/list"},
    )
    assert r[1]["result"]["isError"] and r[2]["result"]["isError"] and r[3]["result"]["isError"]
    assert r[4]["error"]["code"] == -32602 and r[5]["error"]["code"] == -32601


def test_garbage_line_gets_parse_error() -> None:
    out = subprocess.run([sys.executable, str(SERVER)], input=b"{not json\n", capture_output=True, timeout=30).stdout
    assert json.loads(out)["error"]["code"] == -32700


def test_source_metadata_lists_exclusions() -> None:
    r = session(INIT, call(2, "get_source", {"source_id": "brri_fs10_ufra"}))
    data = r[1]["result"]["structuredContent"]
    assert "Bangladesh Rice Research Institute" in data["publisher"] and data["excluded"]
