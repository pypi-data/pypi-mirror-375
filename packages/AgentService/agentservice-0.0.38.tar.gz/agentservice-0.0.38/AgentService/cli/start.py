
import click
from loguru import logger as log

from AgentService.agent import Agent
from AgentService.agent.agent_tool import AgentTool
from AgentService.config import Config
from AgentService.db import Db
from AgentService.app import start_app


@click.group()
def group():
    pass


@group.command('start', help="Command that starts AgentService project")
def start_project():
    log.info(f"Starting AgentService project")

    agents = Agent.__subclasses__()
    if not len(agents):
        log.critical(f"No agent can be found")
        return

    first_agent = agents[0]
    log.info(f"Found {len(agents)} agents. Using first one: {first_agent.__name__}")

    tools = list(map(lambda x: x(), AgentTool.__subclasses__()))
    log.info(f"Found {len(tools)} tools")

    config = Config()

    agent = first_agent(
        openai_key=config.open_ai_key,
        tools=tools
    )
    config.set_agent(agent)

    db = Db()
    db.connect(config.db_name, config.db_uri)

    start_app()
