"""
LangChain integration utilities for InstaVM

Simple utilities to use InstaVM with LangChain agents and tools.
"""

from typing import Any, Dict, List, Optional, Type
import json

try:
    from langchain.tools import BaseTool
    from langchain.pydantic_v1 import BaseModel, Field
    from langchain.callbacks.manager import CallbackManagerForToolRun
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Create dummy classes for type hints when LangChain not available
    class BaseTool:
        pass
    class BaseModel:
        pass
    class Field:
        @staticmethod
        def default_factory(func):
            return func

def get_langchain_tools(instavm_client):
    """Get LangChain tools for InstaVM"""
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("LangChain not installed. Run: pip install langchain")
    
    # Shared browser session reference to avoid recursion
    browser_session_ref = {"current": None}
    
    # Simple tool classes
    class CreateBrowserSessionTool(BaseTool):
        name = "create_browser_session"
        description = "Create a new browser session for web automation"
        instavm_client = instavm_client
        browser_session_ref = browser_session_ref
        
        class CreateBrowserSessionInput(BaseModel):
            width: int = Field(default=1920, description="Browser width")
            height: int = Field(default=1080, description="Browser height")
        
        args_schema: Type[BaseModel] = CreateBrowserSessionInput
        
        def _run(self, width: int = 1920, height: int = 1080, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
            try:
                session = self.instavm_client.browser.create_session(width, height)
                # Store session in shared reference
                self.browser_session_ref["current"] = session
                return f"Created browser session {session.session_id}"
            except Exception as e:
                return f"Error creating browser session: {str(e)}"
    
    class NavigateToUrlTool(BaseTool):
        name = "navigate_to_url"
        description = "Navigate browser to a URL"
        instavm_client = instavm_client
        browser_session_ref = browser_session_ref
        
        class NavigateInput(BaseModel):
            url: str = Field(description="URL to navigate to")
        
        args_schema: Type[BaseModel] = NavigateInput
        
        def _run(self, url: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
            if not self.browser_session_ref["current"]:
                return "Error: No browser session. Create one first with create_browser_session"
            try:
                self.browser_session_ref["current"].navigate(url)
                return f"Navigated to {url}"
            except Exception as e:
                return f"Error navigating to {url}: {str(e)}"
    
    class ExtractPageContentTool(BaseTool):
        name = "extract_page_content"
        description = "Extract text content from current page"
        instavm_client = instavm_client
        browser_session_ref = browser_session_ref
        
        class ExtractContentInput(BaseModel):
            selector: str = Field(default="body", description="CSS selector")
            max_length: int = Field(default=10000, description="Max content length")
        
        args_schema: Type[BaseModel] = ExtractContentInput
        
        def _run(self, selector: str = "body", max_length: int = 10000, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
            if not self.browser_session_ref["current"]:
                return "Error: No browser session active"
            try:
                elements = self.browser_session_ref["current"].extract_elements(selector, ["text"])
                if elements:
                    content = elements[0].get("text", "")[:max_length]
                    return content
                return "No content found"
            except Exception as e:
                return f"Error extracting content: {str(e)}"
    
    class ExtractElementsTool(BaseTool):
        name = "extract_elements"
        description = "Extract elements using CSS selectors"
        instavm_client = instavm_client
        browser_session_ref = browser_session_ref
        
        class ExtractElementsInput(BaseModel):
            selector: str = Field(description="CSS selector")
            attributes: List[str] = Field(default=["text"], description="Attributes to extract")
            max_results: int = Field(default=10, description="Max results")
        
        args_schema: Type[BaseModel] = ExtractElementsInput
        
        def _run(self, selector: str, attributes: List[str] = None, max_results: int = 10, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
            if not self.browser_session_ref["current"]:
                return "Error: No browser session active"
            if attributes is None:
                attributes = ["text"]
            try:
                elements = self.browser_session_ref["current"].extract_elements(selector, attributes)
                limited = elements[:max_results]
                return json.dumps({"elements": limited, "count": len(elements)})
            except Exception as e:
                return f"Error extracting elements: {str(e)}"
    
    class TakeScreenshotTool(BaseTool):
        name = "take_screenshot"
        description = "Take a screenshot of current page"
        instavm_client = instavm_client
        browser_session_ref = browser_session_ref
        
        class ScreenshotInput(BaseModel):
            full_page: bool = Field(default=True, description="Full page screenshot")
        
        args_schema: Type[BaseModel] = ScreenshotInput
        
        def _run(self, full_page: bool = True, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
            if not self.browser_session_ref["current"]:
                return "Error: No browser session active"
            try:
                screenshot = self.browser_session_ref["current"].screenshot(full_page=full_page)
                return f"Screenshot taken ({len(screenshot)} chars)"
            except Exception as e:
                return f"Error taking screenshot: {str(e)}"
    
    class ExecutePythonCodeTool(BaseTool):
        name = "execute_python_code"
        description = "Execute Python code in the cloud. Use !command for bash"
        instavm_client = instavm_client
        
        class ExecuteCodeInput(BaseModel):
            code: str = Field(description="Python code to execute")
        
        args_schema: Type[BaseModel] = ExecuteCodeInput
        
        def _run(self, code: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
            try:
                result = self.instavm_client.execute(code, language="python")
                return str(result)
            except Exception as e:
                return f"Error executing code: {str(e)}"
    
    # Create tool instances and share browser session reference
    tools = [
        CreateBrowserSessionTool(),
        NavigateToUrlTool(),
        ExtractPageContentTool(), 
        ExtractElementsTool(),
        TakeScreenshotTool(),
        ExecutePythonCodeTool()
    ]
    
    # All tools already have the shared browser_session_ref
    
    return tools

# Simple usage example:
"""
from instavm import InstaVM  
from instavm.integrations.langchain import get_langchain_tools
from langchain_openai import OpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate

# Setup
instavm_client = InstaVM(api_key="your_key")
llm = OpenAI(api_key="your_key")

# Get tools
tools = get_langchain_tools(instavm_client)

# Create agent
prompt = PromptTemplate.from_template('''
Answer the following questions as best you can. You have access to web automation tools.

Tools: {tools}
Tool Names: {tool_names}

Question: {input}
Thought: {agent_scratchpad}
''')

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run
result = agent_executor.invoke({
    "input": "Go to example.com and tell me what the main headline says"
})
print(result)
"""