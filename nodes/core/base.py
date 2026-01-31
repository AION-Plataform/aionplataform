from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseNode(ABC):
    """
    Abstract Base Class for all AION Nodes.
    Enforces a standard interface for execution.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node's logic.
        
        Args:
            inputs: A dictionary where keys are input port names (or previous node IDs) 
                   and values are the data received.
        
        Returns:
            A dictionary representing the outputs of this node.
        """
        pass
