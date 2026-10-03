from pathlib import Path
import yaml

from agent_passport.passport.schema import Passport


def load_passport(path: str | Path) -> Passport:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return Passport.model_validate(data)


def verify_passport(path: str | Path) -> dict[str, object]:
    try:
        passport = load_passport(path)
        return {
            "status": "PASS",
            "agent": passport.agent.name,
            "checks": [
                "schema",
                "identity",
                "behavior",
                "tools",
                "runtime",
            ],
        }
    except Exception as exc:
        return {
            "status": "FAIL",
            "error": str(exc),
        }
