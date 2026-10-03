from agent_passport.core.agent import Agent
from agent_passport.verification.validator import verify_passport


def main() -> None:
    agent = Agent(
        agent_id="nova",
        name="Nova",
        version="0.1.0",
        capabilities=["reasoning", "structured_output"],
    )

    print("Agent:")
    print(agent.describe())

    print("\nPassport verification:")
    print(verify_passport("passport.yaml"))


if __name__ == "__main__":
    main()
