from polyaxon._docker.executor import Executor
from polyaxon._runner.agent.sync_agent import BaseSyncAgent


class Agent(BaseSyncAgent):
    EXECUTOR = Executor
