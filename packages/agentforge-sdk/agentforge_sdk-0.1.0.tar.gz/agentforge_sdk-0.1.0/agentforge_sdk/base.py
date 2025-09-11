from abc import ABC , abstractmethod
from typing import Dict, Any

class ToolContext:
    def __init__(self, config:Dict[str, Any]):
        self._config= config
        
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Safely retrieves a configuration value (e.g., an API key)
        provided by the end-user when they configured the Agent.
        """
        return self._config.get(key, default)
    
class BaseTool(ABC):
    """
    The base class for all AgentForge tools.
    Your tool class must inherit from this.
    """

    def __init__(self, context: ToolContext):
        self.context = context

    @abstractmethod
    def run(self, **kwargs) -> str:
        """
        The entry point for your tool.
        The arguments are provided by the LLM based on your manifest.
        Must return a string.
        """
        pass