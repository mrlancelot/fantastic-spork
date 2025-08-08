from llama_index.core.agent.workflow import AgentWorkflow
from .flights import search_flights  # Updated import path
from .restaurant_agent import RestaurantAgent
from typing import Dict, Any, Optional
import logging
from llama_index.core.agent.workflow import AgentStream, AgentOutput, ToolCallResult, ToolCall

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentWorkflowServiceError(Exception):
    """Custom exception for agent workflow service errors."""
    pass

class AgentWorkflowService:
    """Service class for managing agent workflows."""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize the agent workflow service.
        
        Args:
            api_token: Optional API token for MCP agents
        """
        self.api_token = api_token
        self._workflow = None
        self._flight_agent = None
        self._restaurant_agent = None
        self._initialized = False
        
        logger.info("AgentWorkflowService initialized")
    
    async def initialize(self) -> None:
        """Initialize the workflow and agents."""
        if self._initialized:
            return
            
        try:
            logger.info("Initializing agent workflow service...")
            
            # Initialize agents
            # self._flight_agent = FlightAgent(api_token=self.api_token)
            self._restaurant_agent = RestaurantAgent(api_token=self.api_token)
            
            # Initialize the agents
            # await self._flight_agent.initialize()
            await self._restaurant_agent.initialize()
            
            # Create the workflow
            self._workflow = AgentWorkflow(
                agents=[self._restaurant_agent.agent],
                root_agent=self._restaurant_agent.agent.name,
                initial_state={
                },
            )
            
            self._initialized = True
            logger.info("Agent workflow service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent workflow service: {e}")
            raise AgentWorkflowServiceError(f"Initialization failed: {e}")
    
    async def get_workflow(self) -> AgentWorkflow:
        """Get the initialized workflow.
        
        Returns:
            The AgentWorkflow instance
            
        Raises:
            AgentWorkflowServiceError: If workflow is not initialized
        """
        if not self._initialized:
            await self.initialize()
            
        if self._workflow is None:
            raise AgentWorkflowServiceError("Workflow not properly initialized")
            
        return self._workflow
    
    async def run_workflow(self, query: str, **kwargs) -> Any:
        """Run the workflow with a given query.
        
        Args:
            query: The query to process
            **kwargs: Additional parameters for the workflow
            
        Returns:
            The workflow response
            
        Raises:
            AgentWorkflowServiceError: If workflow execution fails
        """
        try:
            workflow = await self.get_workflow()
            logger.info(f"Running workflow with query: {query}")
            
            # Run the workflow and await the handler to get the result
            handler = workflow.run(query, **kwargs)
            current_agent = None
            async for event in handler.stream_events():
                if isinstance(event, AgentStream):
                    print(event.delta, end="", flush=True)
                if (
                    hasattr(event, "current_agent_name")
                    and event.current_agent_name != current_agent
                ):
                    current_agent = event.current_agent_name
                    print(f"\n{'='*50}")
                    print(f"🤖 Agent: {current_agent}")
                    print(f"{'='*50}\n")
                elif isinstance(event, AgentOutput):
                    if event.response.content:
                        print("📤 Output:", event.response.content)
                    if event.tool_calls:
                        print(
                            "🛠️  Planning to use tools:",
                            [call.tool_name for call in event.tool_calls],
                        )
                elif isinstance(event, ToolCallResult):
                    print(f"🔧 Tool Result ({event.tool_name}):")
                    print(f"  Arguments: {event.tool_kwargs}")
                    print(f"  Output: {event.tool_output}")
                elif isinstance(event, ToolCall):
                    print(f"🔨 Calling Tool: {event.tool_name}")
                    print(f"  With arguments: {event.tool_kwargs}")
            result = await handler
            
            logger.info("Workflow executed successfully")
            logger.info(f"Workflow result: {result}")
            
            # The result is the final output from the workflow
            # For AgentWorkflow, this typically contains the agent's response
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise AgentWorkflowServiceError(f"Workflow execution failed: {e}")
    
    async def get_flight_agent(self):
        """Get the flight agent instance.
        
        Returns:
            The FlightAgent instance
        """
        if not self._initialized:
            await self.initialize()
            
        return self._flight_agent
    
    async def get_restaurant_agent(self) -> RestaurantAgent:
        """Get the restaurant agent instance.
        
        Returns:
            The RestaurantAgent instance
        """
        if not self._initialized:
            await self.initialize()
            
        return self._restaurant_agent
    
    def get_workflow_state(self) -> Dict[str, Any]:
        """Get the current workflow state.
        
        Returns:
            The current workflow state
        """
        if self._workflow is None:
            return {}
            
        return {
            "initialized": self._initialized,
            "has_workflow": self._workflow is not None,
            "has_flight_agent": self._flight_agent is not None,
            "has_restaurant_agent": self._restaurant_agent is not None,
        }

# Singleton instance management
_workflow_service_instance: Optional[AgentWorkflowService] = None

def get_agent_workflow_service(api_token: Optional[str] = None) -> AgentWorkflowService:
    """Get or create the agent workflow service singleton.
    
    Args:
        api_token: Optional API token for MCP agents
        
    Returns:
        The AgentWorkflowService singleton instance
    """
    global _workflow_service_instance
    
    if _workflow_service_instance is None:
        _workflow_service_instance = AgentWorkflowService(api_token=api_token)
        logger.info("Created new AgentWorkflowService singleton instance")
    
    return _workflow_service_instance

# Convenience function for backward compatibility
def get_agent_workflow(api_token: Optional[str] = None) -> AgentWorkflow:
    """Get the agent workflow instance (backward compatibility).
    
    Args:
        api_token: Optional API token for MCP agents
        
    Returns:
        The AgentWorkflow instance
        
    Note:
        This is a synchronous wrapper that should be used carefully.
        Prefer using the service class directly for async operations.
    """
    service = get_agent_workflow_service(api_token=api_token)
    # Note: This returns the service, not the workflow directly
    # since we can't await in a sync function
    return service