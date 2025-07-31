import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import HandoffOrchestration, OrchestrationHandoffs
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.contents import ChatMessageContent, AuthorRole
from agents import create_contoso_agents
from utils.file_manager import FileManager
from utils.widget_manager import widget_manager
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Debug mode from environment
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

app = FastAPI(title="Contoso Agent Demo API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
active_sessions: Dict[str, Dict] = {}
# Use current working directory artifacts (where tools are creating files)
file_manager = FileManager(artifacts_dir="artifacts")

class ContosoWebSocketHandler:
    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.service = None
        self.agents = None
        self.orchestration = None
        self.runtime = None
        
    async def initialize_agents(self):
        """Initialize the agent system with WebSocket-compatible setup"""
        try:
            # Create Azure OpenAI service (same as handoff_demo.py)
            self.service = AzureChatCompletion(
                deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            )
            
            # Create agents using factory (same as handoff_demo.py)
            triage_agent, billing_agent, plan_agent, support_agent = create_contoso_agents(self.service)
            self.agents = {
                'triage': triage_agent,
                'billing': billing_agent,
                'plan': plan_agent,
                'support': support_agent
            }
            
            # Define handoff relationships (exact same as handoff_demo.py)
            handoffs = (
                OrchestrationHandoffs()
                .add_many(
                    source_agent=triage_agent.name,
                    target_agents={
                        billing_agent.name: "Transfer to this agent if the customer has billing issues, high bills, or wants bill analysis",
                        plan_agent.name: "Transfer to this agent if the customer asks about roaming plans, addons, or current plan details", 
                        support_agent.name: "Transfer to this agent if the customer wants to speak to a human or needs ticket creation"
                    }
                )
                .add(
                    source_agent=billing_agent.name,
                    target_agent=triage_agent.name,
                    description="Transfer back to triage agent after completing billing analysis"
                )
                .add(
                    source_agent=billing_agent.name,
                    target_agent=support_agent.name,
                    description="Transfer to support agent if billing issue cannot be resolved with available data"
                )
                .add(
                    source_agent=plan_agent.name,
                    target_agent=triage_agent.name,
                    description="Transfer back to triage agent after providing plan information"
                )
                .add(
                    source_agent=plan_agent.name,
                    target_agent=support_agent.name,
                    description="Transfer to support agent if plan issue cannot be resolved with available information"
                )
                .add(
                    source_agent=support_agent.name,
                    target_agent=triage_agent.name,
                    description="Transfer back to triage agent after creating support ticket"
                )
            )
            
            # Create handoff orchestration with WebSocket callback
            self.orchestration = HandoffOrchestration(
                members=[triage_agent, billing_agent, plan_agent, support_agent],
                handoffs=handoffs,
                agent_response_callback=self.agent_response_callback
            )
            
            # Create runtime
            self.runtime = InProcessRuntime()
            self.runtime.start()
            
            await self.send_message({
                "type": "system",
                "content": "Agents initialized successfully. Ready to chat!"
            })
            
        except Exception as e:
            await self.send_message({
                "type": "error",
                "content": f"Failed to initialize agents: {str(e)}"
            })
            
    def agent_response_callback(self, message: ChatMessageContent) -> None:
        """WebSocket-compatible agent response callback"""
        # Send message to WebSocket asynchronously
        asyncio.create_task(self.handle_agent_message(message))
        
        # DEBUG MODE: Print full raw message as JSON
        if DEBUG_MODE:
            try:
                message_dict = {
                    "name": message.name,
                    "role": str(message.role),
                    "content": message.content,
                    "items": [str(item) for item in (message.items or [])]
                }
                print(f"DEBUG_RAW_MESSAGE: {json.dumps(message_dict, indent=2)}")
            except Exception as e:
                print(f"DEBUG_RAW_MESSAGE: Error serializing message: {e}")
                print(f"DEBUG_RAW_MESSAGE: {message}")
        
        # Also print to console for debugging
        if hasattr(message, 'items') and message.items:
            for item in message.items:
                if hasattr(item, 'name') and hasattr(item, 'arguments') and not hasattr(item, 'result'):
                    print(f"🔧 [{message.name} is calling tool: {item.name}...]")
                    return
                elif hasattr(item, 'name') and hasattr(item, 'result'):
                    print(f"✅ [{message.name} completed tool: {item.name}]")
                    return
        
        if not message.content or message.content.strip() == "":
            tool_guess = ""
            if message.name == "BillingAgent":
                tool_guess = " (likely using billing analysis tools)"
            elif message.name == "PlanAgent":
                tool_guess = " (likely using plan/roaming tools)"
            elif message.name == "SupportAgent":
                tool_guess = " (likely using support ticket tools)"
            print(f"🔧 [{message.name} is working{tool_guess}...]")
        else:
            print(f"{message.name}: {message.content}")
    
    def human_response_function(self) -> ChatMessageContent:
        """This should not be called in WebSocket mode"""
        print("Warning: human_response_function called in WebSocket mode")
        return ChatMessageContent(role=AuthorRole.USER, content="")
    
    async def handle_agent_message(self, message: ChatMessageContent):
        """Handle agent messages and send via WebSocket"""
        try:
            # Check for function calls in the message items
            if hasattr(message, 'items') and message.items:
                for item in message.items:
                    # Check if this is a function call
                    if hasattr(item, 'name') and hasattr(item, 'arguments') and not hasattr(item, 'result'):
                        await self.send_message({
                            "type": "tool_start",
                            "agent": message.name or "unknown",
                            "tool": item.name,
                            "content": f"Using tool: {item.name}"
                        })
                        return
                    # Check if this is a function result
                    elif hasattr(item, 'name') and hasattr(item, 'result'):
                        await self.send_message({
                            "type": "tool_complete",
                            "agent": message.name or "unknown", 
                            "tool": item.name,
                            "content": f"Completed tool: {item.name}"
                        })
                        return
            
            # Handle regular agent responses
            if message.content and message.content.strip():
                # Extract file references
                files = self.extract_file_references(message.content)
                
                # Extract widget references
                widgets = self.extract_widget_references(message.content)
                
                await self.send_message({
                    "type": "agent_message",
                    "agent": message.name or "Alex",
                    "content": message.content,
                    "files": files,
                    "widgets": widgets
                })
            else:
                # Agent is working with tools
                tool_guess = ""
                if message.name == "BillingAgent":
                    tool_guess = " (analyzing billing data)"
                elif message.name == "PlanAgent":
                    tool_guess = " (checking plans and roaming options)"
                elif message.name == "SupportAgent":
                    tool_guess = " (handling support request)"
                
                await self.send_message({
                    "type": "agent_working",
                    "agent": message.name or "unknown",
                    "content": f"{message.name} is working{tool_guess}..."
                })
                
        except Exception as e:
            print(f"Error handling agent message: {e}")
            
    async def send_message(self, message: Dict[str, Any]):
        """Send message to WebSocket client"""
        try:
            await self.websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")
            
    async def process_user_message(self, user_message: str):
        """Process user message through agent system"""
        try:
            await self.send_message({
                "type": "user_message",
                "content": user_message
            })
            
            try:
                # Invoke the orchestration with the user message directly
                # This follows the same pattern as handoff_demo.py but adapted for WebSocket
                orchestration_result = await self.orchestration.invoke(
                    task=user_message,
                    runtime=self.runtime
                )
                
                # Wait for completion (but don't block indefinitely)
                await asyncio.wait_for(orchestration_result.get(), timeout=60.0)
                
            except asyncio.TimeoutError:
                await self.send_message({
                    "type": "error",
                    "content": "Request timed out. Please try again."
                })
                    
        except Exception as e:
            await self.send_message({
                "type": "error",
                "content": f"Error processing message: {str(e)}"
            })
            
    def extract_file_references(self, content: str) -> List[Dict[str, str]]:
        """Extract file references from agent response"""
        files = []
        pattern = r'\[FILE:([^:]+):([^\]]+)\]'
        matches = re.findall(pattern, content)
        
        for file_id, description in matches:
            file_info = file_manager.get_file_info(file_id)
            
            if file_info:
                files.append({
                    "file_id": file_id,
                    "description": description,
                    "file_type": file_info.get("file_type", "unknown"),
                    "file_path": file_info.get("file_path", "")
                })
                
        return files
    
    def extract_widget_references(self, content: str) -> List[Dict[str, Any]]:
        """Extract widget references from agent response"""
        widgets = widget_manager.extract_widget_references(content)
        if widgets:
            print(f"DEBUG: Extracted {len(widgets)} widgets from content")
            for widget in widgets:
                print(f"  - {widget['widget_type']} with {len(widget['widget_ids'])} IDs")
        return widgets

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    handler = ContosoWebSocketHandler(websocket, session_id)
    active_sessions[session_id] = {
        "handler": handler,
        "websocket": websocket
    }
    
    try:
        await handler.initialize_agents()
        
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "chat_message":
                await handler.process_user_message(message_data.get("content", ""))
                
    except WebSocketDisconnect:
        if session_id in active_sessions:
            del active_sessions[session_id]
    except Exception as e:
        print(f"WebSocket error: {e}")
        if session_id in active_sessions:
            del active_sessions[session_id]

@app.get("/files/{file_id}")
async def get_file(file_id: str):
    """Serve generated files"""
    try:
        file_path = file_manager.get_artifact_path(file_id)
        print(f"DEBUG: Serving file - file_id: {file_id}, file_path: {file_path}")
        
        if file_path and file_path.exists():
            print(f"DEBUG: File exists, serving: {file_path}")
            return FileResponse(
                path=str(file_path),
                filename=file_id,
                media_type='application/octet-stream'
            )
        else:
            print(f"DEBUG: File not found: {file_path}")
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        print(f"DEBUG: Error serving file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{file_id}/info")
async def get_file_info(file_id: str):
    """Get file metadata"""
    try:
        file_info = file_manager.get_file_info(file_id)
        if file_info:
            return file_info
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "active_sessions": len(active_sessions)}

@app.get("/demo-architecture")
async def get_demo_architecture():
    """Serve the demo architecture documentation"""
    try:
        deck_path = Path(__file__).parent.parent / "frontend" / "assets" / "deck.md"
        with open(deck_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Demo architecture documentation not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static frontend files
app.mount("/", StaticFiles(directory=str(Path(__file__).parent.parent / "frontend"), html=True), name="static")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )