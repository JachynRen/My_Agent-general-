"""桌面 Agent Demo 程序入口。"""
from agent.core import Agent
from agent.ui import ChatWindow


def main() -> None:
    agent = Agent(name="小助手")
    app = ChatWindow(agent)
    app.run()


if __name__ == "__main__":
    main()

