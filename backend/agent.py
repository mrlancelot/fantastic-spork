"""
Agent module for LLM-based tools and assistants.
Provides calculator, web scraping, and basic LLM completion capabilities.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.google_genai import GoogleGenAI as Gemini
from llama_index.llms.openai import OpenAI
from llama_index.tools.mcp import BasicMCPClient
from llama_index.tools.mcp.base import McpToolSpec

# Load environment variables
load_dotenv()


def get_llm(prefer_openrouter: bool = True) -> OpenAI | Gemini:
    """
    Get the appropriate LLM instance based on available API keys.
    
    Args:
        prefer_openrouter: Whether to prefer OpenRouter over Google Gemini
        
    Returns:
        LLM instance (OpenRouter GPT-4 or Google Gemini)
    """
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if prefer_openrouter and openrouter_key:
        return OpenAI(
            model="openai/gpt-4o-mini",  # Fast and cost-effective
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.3
        )
    
    # Fallback to Google Gemini
    return Gemini(model="models/gemini-2.5-pro")


# Simple calculator tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


# Create calculator agent
calculator_agent = FunctionAgent(
    tools=[multiply, add, subtract, divide],
    llm=get_llm(),
    system_prompt="You are a helpful assistant that can perform mathematical calculations.",
)


async def run_agent_with_calculator() -> str:
    """
    Run the calculator agent with a sample calculation.
    
    Returns:
        Agent response as string
    """
    response = await calculator_agent.run("What is 1234 * 4567?")
    return str(response)


async def run_agent_with_mcp() -> str:
    """
    Run an agent with MCP (Model Context Protocol) for web scraping.
    
    Returns:
        Agent response with scraped content
    
    Raises:
        Exception: If MCP token is not configured or scraping fails
    """
    api_token = os.getenv("BRIGHT_DATA_API_TOKEN")
    if not api_token:
        raise ValueError("BRIGHT_DATA_API_TOKEN environment variable is not set")
    
    try:
        # Initialize MCP client for web scraping
        http_client = BasicMCPClient(
            f"https://mcp.brightdata.com/mcp?token={api_token}"
        )
        
        mcp_tool_spec = McpToolSpec(
            client=http_client,
            allowed_tools=["scrape_as_markdown_Schema"],
            include_resources=False
        )
        
        tools = await mcp_tool_spec.to_tool_list_async()
        
        # Create scraping agent
        scraping_agent = FunctionAgent(
            tools=tools,
            llm=get_llm(),
            system_prompt=(
                "You are a helpful assistant that can scrape websites. "
                "Use the scrape_as_markdown_Schema tool to extract content from "
                "https://tabelog.com/en/tokyo/rstLst/?SrtT=rt"
            ),
        )
        
        response = await scraping_agent.run(
            "Give me the markdown of the top 3 highest rated restaurants in Tokyo"
        )
        
        return str(response)
        
    except Exception as e:
        print(f"Error in MCP agent: {e}")
        raise


async def run_agent_basic() -> str:
    """
    Run a basic LLM completion without tools.
    
    Returns:
        LLM response as string
    """
    llm = Gemini(model="models/gemini-1.5-flash")
    response = llm.complete("Write a poem about a magic backpack")
    return str(response)