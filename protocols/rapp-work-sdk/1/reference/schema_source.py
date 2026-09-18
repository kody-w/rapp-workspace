"""Generate the four closed RAPP Work SDK/1 JSON schemas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = "rapp-work-sdk/1"
DRAFT = "https://json-schema.org/draft/2020-12/schema"
URI = "https://github.com/kody-w/rapp-workspace/raw/main/protocols/rapp-work-sdk/1/schemas/"
RAPPID = (
    r"^rappid:@(?=[^/]{1,39}/)[a-z0-9]+(?:-[a-z0-9]+)*/"
    r"(?=[^:]{1,100}:)[a-z0-9]+(?:-[a-z0-9]+)*:[0-9a-f]{64}$"
)


def obj(properties: dict, required: list[str] | None = None) -> dict:
    return {
        "type": "object",
        "properties": properties,
        "required": required if required is not None else list(properties),
        "additionalProperties": False,
    }


def text(maximum: int = 512, minimum: int = 1, pattern: str | None = None) -> dict:
    value = {"type": "string", "minLength": minimum, "maxLength": maximum}
    if pattern:
        value["pattern"] = pattern + r"(?![\s\S])"
    return value


def array(items: dict, maximum: int = 128) -> dict:
    return {
        "type": "array",
        "items": items,
        "minItems": 0,
        "maxItems": maximum,
        "uniqueItems": True,
    }


def nullable(value: dict) -> dict:
    return {"oneOf": [value, {"type": "null"}]}


def defs() -> dict:
    hex40 = text(40, 40, r"^[0-9a-f]{40}$")
    hex64 = text(64, 64, r"^[0-9a-f]{64}$")
    utc = text(24, 24, r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$")
    world = text(128, 1, r"^[^\u0000-\u001f\u007f]+$")
    wave = obj({"space": {"const": "rapp/1:wave"}, "hash": hex64})
    capability = obj(
        {
            "id": text(128),
            "version": text(64),
            "locator": text(1024),
            "sha256": nullable(hex64),
            "discovery_only": {"const": True},
            "activation_authorized": {"const": False},
            "execution_authorized": {"const": False},
            "grants_authority": {"const": False},
        }
    )
    return {
        "hex40": hex40,
        "hex64": hex64,
        "utc": utc,
        "rappid": text(213, 76, RAPPID),
        "world": world,
        "wave": wave,
        "organization_pointer": obj(
            {
                "workspace_profile": {"const": "rapp-workspace/1"},
                "composite": wave,
                "verification_status": {
                    "enum": ["address-reference-only", "verified-local-receipt"]
                },
                "verification_receipt": nullable(wave),
                "routing_only": {"const": True},
                "content_copied": {"const": False},
                "grants_authority": {"const": False},
            }
        ),
        "hive_endpoint": obj(
            {
                "id": text(128),
                "hive_rappid": text(213, 76, RAPPID),
                "world_id": world,
                "transport": text(64),
                "locator_sha256": hex64,
                "verification_status": {"enum": ["described-unverified", "verified"]},
                "verification_receipt": nullable(wave),
                "publication_authorized": {"const": False},
                "grants_authority": {"const": False},
            }
        ),
        "hive_vector": obj(
            {
                "hive_rappid": text(213, 76, RAPPID),
                "vector_sha256": hex64,
                "verification_status": {"enum": ["described-unverified", "verified"]},
                "verification_receipt": wave,
                "publication_authorized": {"const": False},
                "grants_authority": {"const": False},
            }
        ),
        "capability": capability,
    }


def document(name: str, body: dict) -> dict:
    return {
        "$schema": DRAFT,
        "$id": URI + name + ".schema.json",
        "$defs": defs(),
        **body,
    }


def schemas() -> dict[str, dict]:
    ref = lambda name: {"$ref": f"#/$defs/{name}"}
    parent = obj(
        {
            "profile": {"const": "rapp-work/1"},
            "repository": {"const": "https://github.com/kody-w/rapp-1"},
            "commit": ref("hex40"),
            "path": {"const": "protocols/rapp-work/1/SPEC.md"},
            "spec_sha256": ref("hex64"),
        }
    )
    pin = obj(
        {
            "pin": ref("hex40"),
            "sequence": {"type": "integer", "minimum": 0, "maximum": 65535},
            "spec_sha256": ref("hex64"),
            "status": {"enum": ["migration-source-only", "current"]},
            "fresh_install": {"type": "boolean"},
            "profile_artifact": nullable(
                obj(
                    {
                        "path": text(
                            256,
                            1,
                            r"^history/[0-9a-f]{40}/profile[.]json$",
                        ),
                        "sha256": ref("hex64"),
                        "bytes": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 4 * 1024 * 1024,
                        },
                    }
                )
            ),
        }
    )
    profile = document(
        "profile",
        obj(
            {
                "schema": {"const": PROFILE + "/profile"},
                "profile": {"const": PROFILE},
                "parent": parent,
                "workspace_sibling": obj(
                    {
                        "profile": {"const": "rapp-workspace/1"},
                        "spec_sha256": ref("hex64"),
                        "manifest_sha256": ref("hex64"),
                        "identity_unchanged": {"const": True},
                        "normative_bytes_unchanged": {"const": True},
                    }
                ),
                "sidecar": obj(
                    {
                        "path": {"const": ".rapp-work"},
                        "mode": {"const": "offline-first"},
                        "network_default": {"const": "disabled"},
                        "atomic_generation_pointer": {"const": True},
                        "native_workspace_copy": {"const": False},
                    }
                ),
                "pins": {
                    "type": "array",
                    "items": pin,
                    "minItems": 1,
                    "maxItems": 32,
                    "uniqueItems": True,
                },
                "current_pin": ref("hex40"),
                "authority": obj(
                    {
                        "discovery_only": {"const": True},
                        "hive_publication": {"const": False},
                        "plugin_activation": {"const": False},
                        "native_workspace_mutation": {"const": False},
                        "grants_authority": {"const": False},
                    }
                ),
            }
        ),
    )
    discovery = document(
        "discovery",
        obj(
            {
                "schema": {"const": PROFILE + "/discovery"},
                "profile": {"const": PROFILE},
                "installed_pin": ref("hex40"),
                "workspace_rappid": ref("rappid"),
                "world_id": ref("world"),
                "organization_pointers": array(ref("organization_pointer"), 1024),
                "hive_endpoints": array(ref("hive_endpoint"), 256),
                "hive_vectors": array(ref("hive_vector"), 256),
                "plugins": array(ref("capability"), 256),
                "skills": array(ref("capability"), 256),
                "static_apis": array(ref("capability"), 256),
                "network_default": {"const": "disabled"},
                "discovery_only": {"const": True},
                "native_workspace_copied": {"const": False},
                "publication_authorized": {"const": False},
                "grants_authority": {"const": False},
            }
        ),
    )
    install = document(
        "install",
        obj(
            {
                "schema": {"const": PROFILE + "/install"},
                "profile": {"const": PROFILE},
                "workspace_rappid": ref("rappid"),
                "world_id": ref("world"),
                "workspace_spec": nullable(text(128)),
                "workspace_identity_sha256": ref("hex64"),
                "profile_sha256": ref("hex64"),
                "installed_pin": ref("hex40"),
                "current_pin": ref("hex40"),
                "current_generation_sha256": ref("hex64"),
                "discovery_sha256": ref("hex64"),
                "installed_utc": ref("utc"),
                "updated_utc": nullable(ref("utc")),
                "last_update_plan_digest": nullable(ref("hex64")),
                "sidecar_path": {"const": ".rapp-work"},
                "mode": {"const": "offline-first"},
                "network_default": {"const": "disabled"},
                "native_workspace_copied": {"const": False},
                "workspace_identity_preserved": {"const": True},
                "publication_authorized": {"const": False},
                "grants_authority": {"const": False},
            }
        ),
    )
    plan = obj(
        {
            "profile": {"const": PROFILE},
            "workspace_rappid": ref("rappid"),
            "world_id": ref("world"),
            "from_pin": ref("hex40"),
            "to_pin": ref("hex40"),
            "from_generation_sha256": ref("hex64"),
            "from_profile_sha256": ref("hex64"),
            "target_profile_sha256": ref("hex64"),
            "target_discovery_sha256": ref("hex64"),
            "operations": {
                "const": [
                    "write-complete-generation",
                    "atomically-replace-install-pointer",
                ]
            },
            "network_access": {"const": False},
            "native_workspace_copy": {"const": False},
            "publication_authorized": {"const": False},
            "grants_authority": {"const": False},
        }
    )
    update = document(
        "update",
        obj(
            {
                "schema": {"const": PROFILE + "/update"},
                "status": {"enum": ["planned", "prepared"]},
                "plan_digest": ref("hex64"),
                "plan": plan,
                "prepared_utc": nullable(ref("utc")),
            }
        ),
    )
    return {
        "profile.schema.json": profile,
        "install.schema.json": install,
        "update.schema.json": update,
        "discovery.schema.json": discovery,
    }


def encoded(value: dict) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    expected = schemas()
    failures = []
    for name, value in expected.items():
        path = ROOT / "schemas" / name
        raw = encoded(value)
        if args.check:
            if not path.is_file() or path.read_bytes() != raw:
                failures.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    actual = {path.name for path in (ROOT / "schemas").glob("*.json")}
    failures.extend(sorted(actual - expected.keys()))
    print(
        f"{len(expected)} RAPP Work SDK/1 schemas | "
        + ("FAIL " + ", ".join(failures) if failures else "PASS")
    )
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
