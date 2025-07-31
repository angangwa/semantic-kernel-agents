# Architecture Overview

## Core Concept: Multi-Agent Orchestration

This demo shows how multiple AI agents can work together to handle complex customer service scenarios. The architecture is simple at its core:

```
User → Triage Agent → Specialist Agent → Response with Data
```

## Starting Simple: Terminal Demo (`handoff_demo.py`)

The terminal demo shows the **pure agent orchestration** without any web complexity:

### How It Works
1. **Create agents** using a factory function
2. **Define handoffs** between agents
3. **Process messages** in a loop
4. **Agents use tools** to get real data

### Key Code Pattern
```python
# Create agents
triage, billing, plan, support = create_contoso_agents(service)

# Define who can hand off to whom
handoffs = OrchestrationHandoffs()
    .add_many(source=triage, targets={
        billing: "for billing issues",
        plan: "for roaming questions"
    })

# Process user messages
orchestration.invoke(task=user_message, runtime=runtime)
```

That's it! The complexity comes from coordinating these agents, not from the infrastructure.

## Agent Components

### Agents (`agents/`)
Each agent is a specialized assistant:
- **Instructions**: What the agent should do
- **Tools**: Functions the agent can call
- **Handoff rules**: When to transfer to others

### Tools (`tools/`)
Python functions that agents can call:
- **BillingTools**: Read CSV data, analyze charges, create charts
- **PlanTools**: Check plan details, suggest addons
- **SupportTools**: Create tickets, schedule callbacks

### Data (`data/`)
- Simulated customer data in pandas DataFrames
- Bills, plans, usage - all in memory
- No database needed for the demo

## Message Flow in Detail

1. **User Message** → "Why is my bill high?"
2. **Triage Agent** → Recognizes billing question
3. **Handoff** → Transfers to BillingAgent
4. **BillingAgent** → Calls tools:
   - `get_recent_bills()` → Gets bill history
   - `analyze_high_charges()` → Finds expensive items
5. **Response** → Specific data: "£89.50 roaming in USA on Nov 3rd"

## Tool Usage Visibility

Both demos show exactly what agents are doing:
```
🔧 [BillingAgent is calling tool: get_recent_bills...]
✅ [BillingAgent completed tool: get_recent_bills]
🔧 [BillingAgent is calling tool: analyze_high_charges...]
✅ [BillingAgent completed tool: analyze_high_charges]
```

This transparency helps understand the agent's decision process.

## Web UI: One Way to Expose Agents

The web UI (`main.py`) is just one way to expose the agents:

### Additional Complexity
- **WebSocket** for real-time updates
- **FastAPI** for HTTP endpoints
- **Frontend** for user interface
- **File serving** for generated artifacts

### Same Core Pattern
Despite the added complexity, it uses the **exact same**:
- Agent creation
- Handoff definitions
- Orchestration invocation
- Tool usage patterns

The only difference is input/output:
- Terminal: `input()` → print
- Web: WebSocket message → JSON response

## Key Insights

1. **Agents are simple** - Just instructions + tools
2. **Orchestration is powerful** - Manages the complexity
3. **Tools provide data** - No hardcoded responses
4. **UI is separate** - Agents work anywhere

Start with the terminal demo to understand agents, then explore how the web UI exposes the same functionality in a different way.