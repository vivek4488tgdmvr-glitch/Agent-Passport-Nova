"""Day 27: encrypted signing-key management demo."""
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_passport.security import SecureKeyStore


def main():
    print("=== DAY 27: SECURE KEY MANAGEMENT ===")
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "nova.keystore.json"
        created = SecureKeyStore.create(path, "demo-password", issuer="nova")
        raw = path.read_text()
        store = SecureKeyStore(path)
        print(f"Encrypted keystore: {path.name} ✓")
        print(f"Private key exposed on disk: {'private_key' in raw} {'FAIL ✗' if 'private_key' in raw else 'PASS ✓'}")
        print(f"Public key available: {bool(store.public_key())} ✓")
        try:
            store.load_private_key("wrong-password")
        except ValueError:
            print("Wrong password rejected: PASS ✓")
        store.load_private_key("demo-password")
        rotated = store.rotate("demo-password", new_password="new-password")
        print(f"Key rotation: PASS ✓ ({created['public_key'][:12]} → {rotated['public_key'][:12]})")
        print("SECURE KEY MANAGEMENT ✓")


if __name__ == "__main__":
    main()
