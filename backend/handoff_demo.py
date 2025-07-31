import asyncio
import os
from dotenv import load_dotenv

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import HandoffOrchestration, OrchestrationHandoffs
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.contents import ChatMessageContent, AuthorRole

from agents import create_contoso_agents

# Load environment variables
load_dotenv()

class ContosoHandoffDemo:
    def __init__(self):
        # Create Azure OpenAI service
        self.service = AzureChatCompletion(
            deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        )
        
        # Create agents using factory
        self.triage_agent, self.billing_agent, self.plan_agent, self.support_agent = create_contoso_agents(self.service)
        
        # Define handoff relationships following the documentation pattern
        self.handoffs = (
            OrchestrationHandoffs()
            .add_many(
                source_agent=self.triage_agent.name,
                target_agents={
                    self.billing_agent.name: "Transfer to this agent if the customer has billing issues, high bills, or wants bill analysis",
                    self.plan_agent.name: "Transfer to this agent if the customer asks about roaming plans, addons, or current plan details", 
                    self.support_agent.name: "Transfer to this agent if the customer wants to speak to a human or needs ticket creation"
                }
            )
            .add(
                source_agent=self.billing_agent.name,
                target_agent=self.triage_agent.name,
                description="Transfer back to triage agent after completing billing analysis"
            )
            .add(
                source_agent=self.billing_agent.name,
                target_agent=self.support_agent.name,
                description="Transfer to support agent if billing issue cannot be resolved with available data"
            )
            .add(
                source_agent=self.plan_agent.name,
                target_agent=self.triage_agent.name,
                description="Transfer back to triage agent after providing plan information"
            )
            .add(
                source_agent=self.plan_agent.name,
                target_agent=self.support_agent.name,
                description="Transfer to support agent if plan issue cannot be resolved with available information"
            )
            .add(
                source_agent=self.support_agent.name,
                target_agent=self.triage_agent.name,
                description="Transfer back to triage agent after creating support ticket"
            )
        )
        
        # Create handoff orchestration
        # Note: We're following the same pattern as main.py where human input is handled
        # in a loop after each agent response, rather than using human_response_function.
        # Alternative approach: You can pass human_response_function to let agents decide
        # when to request human input during the conversation flow.
        self.orchestration = HandoffOrchestration(
            members=[
                self.triage_agent,
                self.billing_agent,
                self.plan_agent,
                self.support_agent
            ],
            handoffs=self.handoffs,
            agent_response_callback=self.agent_response_callback
        )
        
        # Create runtime
        self.runtime = InProcessRuntime()
    
    def agent_response_callback(self, message: ChatMessageContent) -> None:
        """Callback to handle agent responses"""
        # Check for function calls in the message items
        if hasattr(message, 'items') and message.items:
            for item in message.items:
                # Check if this is a function call
                if hasattr(item, 'name') and hasattr(item, 'arguments') and not hasattr(item, 'result'):
                    print(f"🔧 [{message.name} is calling tool: {item.name}...]")
                    return
                # Check if this is a function result
                elif hasattr(item, 'name') and hasattr(item, 'result'):
                    print(f"✅ [{message.name} completed tool: {item.name}]")
                    return
        
        # Show when agents are working with tools (empty content)
        if not message.content or message.content.strip() == "":
            # Try to determine which agent is active and guess the likely tool
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
    
    
    async def run_demo(self):
        """Run the handoff orchestration demo"""
        print("\n🤖 Contoso AI Assistant - Handoff Orchestration Pattern")
        print("=" * 60)
        print("This demo uses the Semantic Kernel HandoffOrchestration pattern")
        print("matching the exact pattern used in the web UI (main.py).")
        print("Type 'quit' or 'exit' to end the conversation.\n")
        
        # Start the runtime
        self.runtime.start()
        
        try:
            # Initial greeting from Alex
            initial_task = "A Contoso customer is on the line and needs assistance."
            orchestration_result = await self.orchestration.invoke(
                task=initial_task,
                runtime=self.runtime
            )
            await orchestration_result.get()
            
            # Main conversation loop - matching main.py pattern
            while True:
                # Get user input
                user_input = input("\nYou: ")
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit']:
                    print("\n👋 Thank you for using Contoso AI Assistant. Goodbye!")
                    break
                
                # Process user message through orchestration
                try:
                    orchestration_result = await self.orchestration.invoke(
                        task=user_input,
                        runtime=self.runtime
                    )
                    
                    # Wait for completion
                    await orchestration_result.get()
                    
                except Exception as e:
                    print(f"\n❌ Error processing message: {str(e)}")
                    
        except Exception as e:
            print(f"\n❌ Error in handoff orchestration: {str(e)}")
        
        finally:
            # Stop the runtime
            await self.runtime.stop_when_idle()

async def main():
    """Main entry point"""
    demo = ContosoHandoffDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())