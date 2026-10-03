from __future__ import annotations

import argparse
import json
import getpass
import os

from .passport.fingerprint import fingerprint
from .passport.loader import export_passport, load
from .passport.report import verify
from .passport.signing import generate_keypair, sign_passport, verify_signature
from .passport.evidence import passport_fingerprint_from_file, sign_evidence, verify_evidence
from .registry import PassportRegistry
from .versioning import diff_passports


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="agent-passport",
        description="Inspect, verify, and export Agent Passport artifacts.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    verify_cmd = sub.add_parser("verify", help="Verify a Passport.")
    verify_cmd.add_argument("passport")

    inspect_cmd = sub.add_parser("inspect", help="Inspect a Passport.")
    inspect_cmd.add_argument("passport")

    export_cmd = sub.add_parser("export", help="Convert a Passport.")
    export_cmd.add_argument("passport")
    export_cmd.add_argument("output")

    keygen_cmd = sub.add_parser("keygen", help="Generate an Ed25519 keypair.")
    keygen_cmd.add_argument("--output", default="passport-keys.json")

    sign_cmd = sub.add_parser("sign", help="Sign a Passport JSON document.")
    sign_cmd.add_argument("passport_json")
    sign_cmd.add_argument("private_key_b64")
    sign_cmd.add_argument("issuer")
    sign_cmd.add_argument("output")

    sigverify_cmd = sub.add_parser("verify-signature", help="Verify a signed Passport JSON document.")
    sigverify_cmd.add_argument("passport_json")
    sigverify_cmd.add_argument("public_key_b64")

    sign_ev = sub.add_parser("sign-evidence", help="Sign Passport Travel evidence and bind it to a Passport.")
    sign_ev.add_argument("evidence_json")
    sign_ev.add_argument("passport")
    sign_ev.add_argument("private_key_b64")
    sign_ev.add_argument("issuer")
    sign_ev.add_argument("output")

    verify_ev = sub.add_parser("verify-evidence", help="Verify signed Passport Travel evidence.")
    verify_ev.add_argument("evidence_json")
    verify_ev.add_argument("passport")

    diff_cmd = sub.add_parser("diff", help="Compare two Passport JSON files.")
    diff_cmd.add_argument("before")
    diff_cmd.add_argument("after")
    diff_cmd.add_argument("--json", action="store_true")

    ks = sub.add_parser("keystore", help="Manage encrypted Ed25519 signing keys.")
    ks_sub = ks.add_subparsers(dest="keystore_command", required=True)
    ksi = ks_sub.add_parser("init", help="Create an encrypted signing keystore.")
    ksi.add_argument("path")
    ksi.add_argument("--issuer", default="")
    ksp = ks_sub.add_parser("public", help="Show the public key from a keystore.")
    ksp.add_argument("path")
    ksr = ks_sub.add_parser("rotate", help="Rotate the encrypted signing key.")
    ksr.add_argument("path")

    reg = sub.add_parser("registry", help="Manage the local Passport registry.")
    reg.add_argument("--db", default=".agent-passport/registry.json")
    reg_sub = reg.add_subparsers(dest="registry_command", required=True)
    rr = reg_sub.add_parser("register")
    rr.add_argument("passport_json")
    rr.add_argument("--issuer")
    rr.add_argument("--public-key")
    rr.add_argument("--require-signature", action="store_true")
    rl = reg_sub.add_parser("list")
    rl.add_argument("--all", action="store_true")
    ri = reg_sub.add_parser("inspect")
    ri.add_argument("passport_id")
    rv = reg_sub.add_parser("verify")
    rv.add_argument("passport_id")
    rx = reg_sub.add_parser("revoke")
    rx.add_argument("passport_id")
    rlts = reg_sub.add_parser("latest")
    rlts.add_argument("agent_id")
    rvv = reg_sub.add_parser("retrieve")
    rvv.add_argument("passport_id")

    args = parser.parse_args()

    if args.command == "verify":
        report = verify(args.passport)
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "PASS" else 1

    if args.command == "inspect":
        passport = load(args.passport)
        print(json.dumps({
            "agent": passport.agent.model_dump(mode="json"),
            "capabilities": passport.identity.capabilities,
            "tools": [t.model_dump(mode="json") for t in passport.tools],
            "model": passport.model.model_dump(mode="json"),
            "compatible_runtimes": passport.runtime.compatible,
            "fingerprint": fingerprint(passport),
        }, indent=2))
        return 0

    if args.command == "keygen":
        private_key, public_key = generate_keypair()
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({"algorithm": "Ed25519", "private_key": private_key, "public_key": public_key}, f, indent=2)
        print(f"Generated: {args.output}")
        return 0

    if args.command == "sign":
        with open(args.passport_json, encoding="utf-8") as f:
            data = json.load(f)
        signed = sign_passport(data, args.private_key_b64, args.issuer)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(signed, f, indent=2)
        print(f"Signed Passport: {args.output}")
        return 0

    if args.command == "verify-signature":
        with open(args.passport_json, encoding="utf-8") as f:
            data = json.load(f)
        result = verify_signature(data, args.public_key_b64)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "PASS" else 1

    if args.command == "sign-evidence":
        with open(args.evidence_json, encoding="utf-8") as f:
            evidence = json.load(f)
        passport_fp = passport_fingerprint_from_file(args.passport)
        signed = sign_evidence(evidence, passport_fp, args.private_key_b64, args.issuer)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(signed, f, indent=2)
        print(json.dumps({"status": "PASS", "passport_fingerprint": passport_fp, "output": args.output}, indent=2))
        return 0

    if args.command == "verify-evidence":
        with open(args.evidence_json, encoding="utf-8") as f:
            evidence = json.load(f)
        passport_fp = passport_fingerprint_from_file(args.passport)
        result = verify_evidence(evidence, passport_fp)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "PASS" else 1

    if args.command == "diff":
        with open(args.before, encoding="utf-8") as f:
            before = json.load(f)
        with open(args.after, encoding="utf-8") as f:
            after = json.load(f)
        result = diff_passports(before, after)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(result.pretty())
        return 0

    if args.command == "keystore":
        if args.keystore_command == "init":
            password = getpass.getpass("Keystore password: ")
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print(json.dumps({"status": "FAIL", "reason": "passwords do not match"}, indent=2))
                return 1
            result = SecureKeyStore.create(args.path, password, issuer=args.issuer)
            print(json.dumps({k: v for k, v in result.items() if k != "path"} | {"path": result["path"]}, indent=2))
            return 0
        if args.keystore_command == "public":
            print(json.dumps({"status": "PASS", "public_key": SecureKeyStore(args.path).public_key()}, indent=2))
            return 0
        if args.keystore_command == "rotate":
            password = getpass.getpass("Current keystore password: ")
            new_password = getpass.getpass("New keystore password (blank keeps current): ")
            result = SecureKeyStore(args.path).rotate(password, new_password=new_password or password)
            print(json.dumps(result, indent=2))
            return 0

    if args.command == "registry":
        registry = PassportRegistry(args.db)
        if args.registry_command == "register":
            with open(args.passport_json, encoding="utf-8") as f:
                data = json.load(f)
            entry = registry.register(data, issuer=args.issuer, public_key=args.public_key, require_signature=args.require_signature)
            print(json.dumps(entry.to_dict(), indent=2))
            return 0
        if args.registry_command == "list":
            print(json.dumps([e.to_dict() for e in registry.list(include_revoked=args.all)], indent=2))
            return 0
        if args.registry_command == "inspect":
            entry = registry.get(args.passport_id)
            if entry is None:
                print(json.dumps({"status": "FAIL", "reason": "Passport not found"}, indent=2))
                return 1
            print(json.dumps(entry.to_dict(), indent=2))
            return 0
        if args.registry_command == "verify":
            result = registry.verify_registered(args.passport_id)
            print(json.dumps(result, indent=2))
            return 0 if result["status"] == "PASS" else 1
        if args.registry_command == "latest":
            entry = registry.latest(args.agent_id)
            if entry is None:
                print(json.dumps({"status": "FAIL", "reason": "No active Passport found"}, indent=2))
                return 1
            print(json.dumps(entry.to_dict(), indent=2))
            return 0
        if args.registry_command == "retrieve":
            result = registry.retrieve_verified(args.passport_id)
            print(json.dumps(result, indent=2))
            return 0 if result["status"] == "PASS" else 1
        if args.registry_command == "revoke":
            entry = registry.revoke(args.passport_id)
            print(json.dumps(entry.to_dict(), indent=2))
            return 0

    if args.command == "export":
        passport = load(args.passport)
        output = export_passport(passport, args.output)
        print(f"Exported: {output}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())


# Dashboard helper:
# Use `python examples/day19_dashboard.py` for a dependency-free launcher.
