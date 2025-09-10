# tests/test_core.py
import json
import os
import sys
import subprocess
from pathlib import Path

import pytest

# Import from installed package or src layout
try:
    from mattstash import (
        MattStash,
        DEFAULT_KDBX_SIDECAR_BASENAME,
    )
    from pykeepass import PyKeePass
except Exception as e:  # pragma: no cover - helpful error if import fails
    raise


def _read_sidecar(db_path: Path) -> str:
    sidecar = db_path.parent / DEFAULT_KDBX_SIDECAR_BASENAME
    return sidecar.read_text().strip()


@pytest.fixture()
def temp_db(tmp_path: Path) -> Path:
    """Create an isolated directory for each test to hold DB + sidecar."""
    d = tmp_path / "mattstash"
    d.mkdir()
    return d / "test.kdbx"


def test_bootstrap_creates_db_and_sidecar(temp_db: Path):
    assert not temp_db.exists()
    sidecar = temp_db.parent / DEFAULT_KDBX_SIDECAR_BASENAME
    assert not sidecar.exists()

    ms = MattStash(path=str(temp_db))  # triggers bootstrap when both missing

    assert temp_db.exists(), "KDBX database should be created"
    assert sidecar.exists(), "Sidecar password file should be created"

    # Password should resolve from the sidecar
    assert ms.password == _read_sidecar(temp_db)


def test_get_and_list_roundtrip(temp_db: Path):
    ms = MattStash(path=str(temp_db))

    # Open the new DB and add entries
    kp = PyKeePass(str(temp_db), password=ms.password)
    grp = kp.root_group
    kp.add_entry(grp, title="ServiceA", username="alice", password="alicepw", url="https://a.example", notes="n1")
    kp.add_entry(grp, title="ServiceB", username="bob", password="bobpw", url="https://b.example", notes="n2")
    kp.save()

    # list
    creds = ms.list()
    names = {c.credential_name for c in creds}
    assert {"ServiceA", "ServiceB"}.issubset(names)

    # get
    a = ms.get("ServiceA", show_password=True)
    assert a is not None
    assert a.username == "alice"
    assert a.password == "alicepw"
    assert a.url == "https://a.example"


def test_simple_secret_put_get_api(temp_db: Path):
    ms = MattStash(path=str(temp_db))
    # store a simple secret (credstash-like)
    result = ms.put("api-token", value="sekrit")
    assert isinstance(result, dict)
    assert result["name"] == "api-token"
    assert result["value"] == "*****"  # masked by default

    masked = ms.get("api-token")
    assert isinstance(masked, dict)
    assert masked["name"] == "api-token"
    assert masked["value"] == "*****"

    revealed = ms.get("api-token", show_password=True)
    assert isinstance(revealed, dict)
    assert revealed["value"] == "sekrit"


def test_hydrate_env_sets_vars(temp_db: Path, monkeypatch: pytest.MonkeyPatch):
    ms = MattStash(path=str(temp_db))

    kp = PyKeePass(str(temp_db), password=ms.password)
    grp = kp.root_group
    e = kp.add_entry(grp, title="AWS-Creds", username="AKIA_TEST", password="SECRET_TEST", url=None, notes=None)
    # add a custom property via pykeepass API
    e.set_custom_property("REGION", "us-east-1")
    kp.save()

    # ensure env is clean
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)

    ms.hydrate_env({
        "AWS-Creds:AWS_ACCESS_KEY_ID": "AWS_ACCESS_KEY_ID",
        "AWS-Creds:AWS_SECRET_ACCESS_KEY": "AWS_SECRET_ACCESS_KEY",
        "AWS-Creds:REGION": "AWS_REGION",
    })

    assert os.environ.get("AWS_ACCESS_KEY_ID") == "AKIA_TEST"
    assert os.environ.get("AWS_SECRET_ACCESS_KEY") == "SECRET_TEST"
    assert os.environ.get("AWS_REGION") == "us-east-1"


@pytest.mark.parametrize("as_module", [True, False])
def test_cli_list_and_get(temp_db: Path, as_module: bool):
    # Pre-populate DB with one entry
    ms = MattStash(path=str(temp_db))
    kp = PyKeePass(str(temp_db), password=ms.password)
    grp = kp.root_group
    kp.add_entry(grp, title="CLI-Test", username="u", password="p", url="https://cli.example", notes="note")
    kp.save()

    if as_module:
        cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "list"]
    else:
        # console-script path (requires pyproject entry point). Still valid to attempt here.
        cmd = ["mattstash", "--db", str(temp_db), "list"]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "CLI-Test" in proc.stdout

    # Now test `get` JSON output
    if as_module:
        cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "get", "CLI-Test", "--json"]
    else:
        cmd = ["mattstash", "--db", str(temp_db), "get", "CLI-Test", "--json"]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["credential_name"] == "CLI-Test"
    assert payload["username"] == "u"


@pytest.mark.parametrize("as_module", [True, False])
def test_cli_get_simple_secret_json(temp_db: Path, as_module: bool):
    ms = MattStash(path=str(temp_db))
    # create simple secret via API
    ms.put("k", value="v")

    if as_module:
        cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "get", "k", "--json"]
    else:
        cmd = ["mattstash", "--db", str(temp_db), "get", "k", "--json"]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["name"] == "k"
    assert payload["value"] == "*****"

    # show-password path
    if as_module:
        cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "get", "k", "--json", "--show-password"]
    else:
        cmd = ["mattstash", "--db", str(temp_db), "get", "k", "--json", "--show-password"]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["name"] == "k"
    assert payload["value"] == "v"


@pytest.mark.skipif("boto3" not in sys.modules and __import__("importlib").util.find_spec("boto3") is None,
                    reason="boto3 not installed")
def test_get_s3_client_builds_without_network(temp_db: Path):
    ms = MattStash(path=str(temp_db))

    # Create an S3 credential entry (endpoint in URL field, key in username, secret in password)
    kp = PyKeePass(str(temp_db), password=ms.password)
    grp = kp.root_group
    kp.add_entry(
        grp,
        title="objectstore",
        username="test-key",
        password="test-secret",
        url="http://127.0.0.1:9000",
        notes=None,
    )
    kp.save()

    client = ms.get_s3_client("objectstore", region="us-east-1", addressing="path", verbose=False)
    # botocore client should have a meta attribute
    assert hasattr(client, "meta")


@pytest.mark.parametrize("as_module", [True, False])
def test_cli_keys_lists_titles(temp_db: Path, as_module: bool):
    ms = MattStash(path=str(temp_db))
    kp = PyKeePass(str(temp_db), password=ms.password)
    grp = kp.root_group
    titles = ["KeyOne", "KeyTwo", "KeyThree"]
    for title in titles:
        kp.add_entry(grp, title=title, username="user", password="pass")
    kp.save()

    if as_module:
        base_cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "keys"]
    else:
        base_cmd = ["mattstash", "--db", str(temp_db), "keys"]

    # Run keys command and check output
    proc = subprocess.run(base_cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    for title in titles:
        assert title in proc.stdout

    # Run keys command with JSON output and check keys list
    json_cmd = base_cmd + ["--json"]
    proc = subprocess.run(json_cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    keys_list = json.loads(proc.stdout)
    for title in titles:
        assert title in keys_list


def test_delete_api_removes_entry(temp_db: Path):
    ms = MattStash(path=str(temp_db))
    kp = PyKeePass(str(temp_db), password=ms.password)
    grp = kp.root_group
    entry = kp.add_entry(grp, title="DeleteMe", username="user", password="pass")
    kp.save()

    # Confirm entry exists
    found = ms.get("DeleteMe")
    assert found is not None

    # Delete entry
    ms.delete("DeleteMe")

    # Reload DB to confirm deletion
    kp = PyKeePass(str(temp_db), password=ms.password)
    found_after = [e for e in kp.entries if e.title == "DeleteMe"]
    assert len(found_after) == 0


def test_put_get_versions(temp_db: Path):
    ms = MattStash(path=str(temp_db))
    # Put two versions of the same key
    ms.put("vkey", value="secret1")
    ms.put("vkey", value="secret2")

    versions = ms.list_versions("vkey")
    # Should return both versions in order
    assert len(versions) >= 2
    # The version numbers are padded strings, check that both versions are in the list
    padded_versions = [v['version'] if isinstance(v, dict) and 'version' in v else str(v) for v in versions]
    assert any(v.endswith("1") for v in padded_versions)
    assert any(v.endswith("2") for v in padded_versions)

    # Latest version is the default get
    latest = ms.get("vkey", show_password=True)
    assert latest["value"] == "secret2"

    # Get version 1 explicitly
    v1 = ms.get("vkey", version=1, show_password=True)
    assert v1["value"] == "secret1"


@pytest.mark.parametrize("as_module", [True, False])
def test_cli_versions_lists_versions(temp_db: Path, as_module: bool):
    ms = MattStash(path=str(temp_db))
    # Create multiple versions via API
    ms.put("vkey", value="secret1")
    ms.put("vkey", value="secret2")

    # Run CLI versions command normal mode
    if as_module:
        cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "versions", "vkey"]
    else:
        cmd = ["mattstash", "--db", str(temp_db), "versions", "vkey"]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    # Check that both padded version strings appear in stdout
    # Versions are padded numbers, e.g. "0000000001", "0000000002"
    assert "0000000001" in proc.stdout
    assert "0000000002" in proc.stdout

    # Run CLI versions command with JSON output
    if as_module:
        cmd_json = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "versions", "vkey", "--json"]
    else:
        cmd_json = ["mattstash", "--db", str(temp_db), "versions", "vkey", "--json"]

    proc = subprocess.run(cmd_json, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    versions_list = json.loads(proc.stdout)
    # Check both padded version strings in JSON list
    assert "0000000001" in versions_list
    assert "0000000002" in versions_list


@pytest.mark.parametrize("as_module", [True, False])
def test_cli_delete_removes_entry(temp_db: Path, as_module: bool):
    ms = MattStash(path=str(temp_db))
    kp = PyKeePass(str(temp_db), password=ms.password)
    grp = kp.root_group
    kp.add_entry(grp, title="ToDelete", username="user", password="pass")
    kp.save()

    if as_module:
        delete_cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "delete", "ToDelete"]
        list_cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "list"]
    else:
        delete_cmd = ["mattstash", "--db", str(temp_db), "delete", "ToDelete"]
        list_cmd = ["mattstash", "--db", str(temp_db), "list"]

    # Run delete command
    proc = subprocess.run(delete_cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr

    # Run list command to confirm deletion
    proc = subprocess.run(list_cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "ToDelete" not in proc.stdout


@pytest.mark.parametrize("as_module", [True, False])
def test_cli_put_with_comment(temp_db: Path, as_module: bool):
    if as_module:
        cmd = [
            sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db),
            "put", "with-comment", "--value", "pw123", "--comment", "this is a note"
        ]
    else:
        cmd = ["mattstash", "--db", str(temp_db), "put", "with-comment", "--value", "pw123", "--comment",
               "this is a note"]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr

    # Now fetch it back and ensure the comment is visible
    if as_module:
        cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "get", "with-comment", "--json"]
    else:
        cmd = ["mattstash", "--db", str(temp_db), "get", "with-comment", "--json"]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    # Depending on how many fields the entry has, the CLI returns either a simple-secret
    # shape (name/value[/notes]) or a full credential shape (credential_name/username/password/url/notes,...).
    if "name" in payload:  # simple secret shape
        assert payload["name"] == "with-comment"
        assert payload["value"] == "*****"
        assert payload.get("notes") == "this is a note"
    elif "credential_name" in payload:  # full credential shape (notes makes it non-simple)
        assert payload["credential_name"] == "with-comment"
        # password should be masked by default
        assert payload.get("password") == "*****"
        assert payload.get("notes") == "this is a note"
    else:
        raise AssertionError(f"Unexpected JSON shape: {payload}")


def test_get_db_url_requires_port(temp_db: Path):
    ms = MattStash(path=str(temp_db))
    # Store creds without a port in the URL -> should raise
    ms.put("pg-creds", username="user", password="pw", url="localhost")
    with pytest.raises(ValueError):
        # database provided, but URL has no port -> error
        ms.get_db_url("pg-creds", database="testdb")


def test_get_db_url_builds_correct_url_and_masking(temp_db: Path):
    ms = MattStash(path=str(temp_db))
    ms.put("pg-creds", username="user", password="pw", url="localhost:5432")

    # Masked by default
    masked = ms.get_db_url("pg-creds", database="testdb")
    assert masked == "postgresql://user:*****@localhost:5432/testdb"

    # Unmasked when requested
    unmasked = ms.get_db_url("pg-creds", database="testdb", mask_password=False)
    assert unmasked == "postgresql://user:pw@localhost:5432/testdb"


@pytest.mark.parametrize("as_module", [True, False])
def test_cli_db_url_masks_password_and_requires_port(temp_db: Path, as_module: bool):
    ms = MattStash(path=str(temp_db))
    # Good creds with port
    ms.put("pg-creds", username="user", password="pw", url="localhost:5432")

    # Bad creds without port to check error path
    ms.put("pg-creds-np", username="user", password="pw", url="localhost")

    if as_module:
        good_cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "db-url", "pg-creds", "--database", "testdb"]
        bad_cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "db-url", "pg-creds-np", "--database", "testdb"]
    else:
        good_cmd = ["mattstash", "--db", str(temp_db), "db-url", "pg-creds", "--database", "testdb"]
        bad_cmd = ["mattstash", "--db", str(temp_db), "db-url", "pg-creds-np", "--database", "testdb"]

    # Good path: masked output, no raw password
    proc = subprocess.run(good_cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "postgresql+psycopg://user@localhost:5432/testdb" in proc.stdout
    assert "postgresql://user:pw@" not in proc.stdout

    # Bad path: should fail and mention port
    proc = subprocess.run(bad_cmd, capture_output=True, text=True)
    assert proc.returncode != 0
    assert "port" in (proc.stderr or proc.stdout).lower()


@pytest.mark.parametrize("as_module", [True, False])
def test_cli_db_url_unmasked_flag(temp_db: Path, as_module: bool):
    ms = MattStash(path=str(temp_db))
    ms.put("pg-creds", username="user", password="pw", url="localhost:5432")

    if as_module:
        cmd = [sys.executable, "-m", "mattstash.cli.main", "--db", str(temp_db), "db-url", "pg-creds", "--database", "testdb", "--mask-password", "False"]
    else:
        cmd = ["mattstash", "--db", str(temp_db), "db-url", "pg-creds", "--database", "testdb", "--mask-password", "False"]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "postgresql+psycopg://user:pw@localhost:5432/testdb" in proc.stdout
