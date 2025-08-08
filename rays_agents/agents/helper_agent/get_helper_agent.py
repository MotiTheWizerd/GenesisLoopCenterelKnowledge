from google.adk.agents.llm_agent import LlmAgent
from rays_agents.agents.helper_agent.get_prompt import get_prompt

def GetHelperAgent(name: str = "MirrorCore", prompt: str = None, description: str = ""):
    """
    Create a helper agent with customizable name, prompt, and description.
    
    Args:
        name: Agent name (default: "MirrorCore")
        prompt: Custom instruction prompt (default: uses get_prompt())
        description: Agent description
    
    Returns:
        LlmAgent instance
    """
    if prompt is None:
        prompt = get_prompt()
    
    return LlmAgent(
        name=name,
        model="gemini-2.0-flash", 
        instruction=prompt,
        description=description
    )
