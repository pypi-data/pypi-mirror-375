
# FluxGraph

FluxGraph is a lightweight, modular framework for building agentic AI workflows with full control and flexibility.  
It integrates **FastAPI, Celery, Redis**, and supports **direct LLM API calls** with extensible tooling.

---

## 🚀 Features
- **Full Control**: Direct API calls without heavy abstractions.  
- **Flexible Orchestration**: Works with LangGraph, AutoGen, or custom FastAPI workflows.  
- **Scalable**: Redis + Celery support for distributed workloads.  
- **Tooling Layer**: Extensible Python functions for DB queries, APIs, and custom tasks.  
- **Multi-LLM Support**: OpenAI, Anthropic, Ollama, or local LLMs.  
- **Persistence & Memory**: Optional Redis, PostgreSQL, or Vector DB integration.  
- **Feedback Loop (RLHF-ready)**: Collects user ratings for model fine-tuning.

---

## 🏗️ Architecture
- **Client/User** → FastAPI layer  
- **Agent Registry** → Stores and manages agents  
- **Flux Orchestrator** → Executes agent flows  
- **Adapters** → LangGraph / Custom Orchestration  
- **Tooling Layer** → Extensible Python functions  
- **LLM Providers** → OpenAI, Anthropic, Ollama, Local models  
- **Persistence Layer** → Redis, PostgreSQL, Vector DB  
- **Feedback Loop** → RLHF integration for continuous improvement  

---

## 📦 Installation
```bash
git clone https://github.com/ihtesham-jahangir/fluxgraph.git
cd fluxgraph
pip install -r requirements.txt
```

---

## ⚡ Quick Start
```python
from fluxgraph import Agent, Orchestrator

# Define an agent
class MyAgent(Agent):
    def run(self, query: str):
        return f"Processed: {query}"

# Register agent
orchestrator = Orchestrator()
orchestrator.register("my_agent", MyAgent())

# Execute
response = orchestrator.run("my_agent", "Hello FluxGraph!")
print(response)
```

---

## 📊 Roadmap
- [x] MVP with FastAPI + Orchestrator  
- [x] Tooling Layer (Python functions)  
- [ ] RLHF feedback integration  
- [ ] Auto-scaling with Docker + Kubernetes  
- [ ] GUI dashboard for monitoring  

---

## 🤝 Contributing
We welcome contributions! Please fork the repo, open issues, or submit PRs.

---

## 📜 License
MIT License © 2025 FluxGraph Team