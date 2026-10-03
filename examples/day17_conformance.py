import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_passport.conformance import BehaviorCase, ConformanceRunner


def nova_behavior(user_input):
    # Reference behavior for the demo: structured response with stable shape.
    if not isinstance(user_input, str):
        raise TypeError("input must be text")
    return {"echo": user_input, "length": len(user_input)}


cases = [
    BehaviorCase(
        "structured-output",
        "passport",
        expected_output={"echo": "passport", "length": 8},
    ),
    BehaviorCase(
        "output-is-object",
        "agent",
        expected_output_type="dict",
    ),
    BehaviorCase(
        "invalid-input",
        123,
        expected_error="TypeError",
    ),
]

report = ConformanceRunner(nova_behavior).run(cases)

print("=== DAY 17: BEHAVIORAL CONFORMANCE ===")
print(report.pretty())
print("\nEvidence:")
print("✓ Declared behavior tested")
print("✓ Output contract tested")
print("✓ Failure behavior tested")
print("✓ Agent behavior can be verified before migration")
