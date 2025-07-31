# Contoso Multi-Agent AI Demo

This is a demonstration of a multi-agent AI system for Contoso customer support, showcasing agent orchestration patterns. **This is a demo for educational purposes only.**

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Azure OpenAI API access

### Setup Instructions

1. **Create and activate a virtual environment**:
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure Azure OpenAI credentials**:
Create a `.env` file in the project root:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Running the Demo

#### 🎯 Terminal Demo (Start Here!)
The terminal demo is the best way to understand how agents work without web complexity:
```bash
cd backend
python handoff_demo.py
```
- Shows pure agent orchestration logic
- See real-time tool usage: `🔧 [BillingAgent is calling tool: analyze_high_charges...]`
- Understand agent handoffs and responses
- Type 'quit' to exit

#### 🌐 Web UI (Advanced)
Once you understand the agents, try the full web interface:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Access at http://localhost:8000

## 🏗️ Architecture

The demo includes four specialized agents:

- **Alex (Triage)** - First point of contact, routes queries to specialists
- **BillingAgent** - Analyzes bills and identifies high charges  
- **PlanAgent** - Recommends roaming plans and addons
- **SupportAgent** - Creates support tickets for human handoff

## 📁 Structure

```
./
├── backend/
│   ├── agents/         # Agent implementations
│   ├── tools/          # Agent-specific tools
│   ├── data/           # Dummy customer data
│   ├── utils/          # Helper utilities
│   ├── handoff_demo.py # Terminal demo (start here!)
│   └── main.py         # Web UI server
├── frontend/           # Web interface files
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🎓 Understanding the Demo

### Start with Terminal Demo
The `handoff_demo.py` file shows the core concepts:
- How agents are created and configured
- How handoffs between agents work
- How agents use tools to analyze data
- How the orchestration manages conversations

### Key Concepts
1. **Agent Orchestration** - Alex coordinates specialist agents
2. **Tool Usage** - Agents use tools to analyze bills, check plans
3. **Handoffs** - Agents transfer control based on expertise
4. **Real Responses** - All data comes from tools, not hardcoded

### Example Interactions
Try these queries:
- "Why is my bill so high?"
- "I need a roaming plan for Europe"
- "What's included in my current plan?"
- "I want to speak to a human"

## 📝 Technical Details

### Agent Tools
- **BillingTools**: Analyzes CSV bill data, creates charts
- **PlanTools**: Provides plan details and recommendations
- **SupportTools**: Creates tickets and schedules callbacks

### Data Flow
1. User asks question
2. Alex analyzes intent
3. Specialist agent is engaged
4. Agent uses tools to gather data
5. Response includes specific details from data

See [ARCHITECTURE.md](ARCHITECTURE.md) for more technical details.

## 📚 Next Steps

1. Start with `handoff_demo.py` to understand agents
2. Read the agent code in `agents/` directory
3. Explore how tools work in `tools/` directory
4. Try the web UI to see a full implementation

Remember: The focus is on coordinating agents, not in the web interface!