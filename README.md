<p align="center">
  <a href="https://sushmit-gujar.github.io/"><img src="assets/header.svg" width="100%" alt="Sushmit Gujar · Senior AI/ML Engineer · AI Security · Agentic AI"></a>
</p>

<p align="center">
  <a href="https://sushmit-gujar.github.io/"><b>Portfolio</b></a> &nbsp;·&nbsp;
  <a href="https://sushmit-gujar.github.io/projects/"><b>Open-source lab</b></a> &nbsp;·&nbsp;
  <a href="https://www.linkedin.com/in/sushmitt/"><b>LinkedIn</b></a>
</p>

I'm a Senior AI/ML Engineer with 8+ years of shipping production ML and GenAI in regulated industries: pharma (Johnson & Johnson), telecom (Comcast) and financial crime. My day job covers agentic AI, RAG, knowledge graphs and real-time LLM inference. On my own time I build **open-source AI security and evaluation tools**. Each one runs end to end with no paid API keys and commits its eval results, so you can check every number below yourself.

<p align="center">
  <img src="assets/lab-bus.svg" width="100%" alt="">
  <a href="https://github.com/sushmit-gujar/aiwatch"><img src="assets/card-aiwatch.svg" width="100%" alt="aiwatch: find, fix and continuously monitor AI-stack vulnerabilities. On its demo app, 272 findings auto-fixed (257 advisories to 0), 129 newly disclosed advisories flagged against a baseline; local OSV matching agrees with OSV.dev on 899/900 pinned packages; 0.03 s offline scan, 4.7 s live."></a>
  <a href="https://github.com/sushmit-gujar/loadsafe"><img src="assets/card-loadsafe.svg" width="100%" alt="loadsafe: ML model supply-chain security scanner. 100% detection and 0% FPR on its 26-file PoC corpus (picklescan 33%, modelscan 44%); 0% HIGH+ FPR on 5 public HF checkpoints; ~3.2 GB/s."></a>
  <a href="https://github.com/sushmit-gujar/mcp-warden"><img src="assets/card-mcp-warden.svg" width="100%" alt="mcp-warden: policy-as-code security gateway for MCP. 30/30 attacks stopped, 12/12 benign allowed on its own suite; held-out 3/8 (rules) and 6/8 (ensemble); +0.78 ms p50 overhead."></a>
  <a href="https://github.com/sushmit-gujar/hopscope"><img src="assets/card-hopscope.svg" width="100%" alt="hopscope: GraphRAG vs vector RAG on 1,000 HotpotQA questions. Full@5 0.699 to 0.746 (+4.7 pts, 95% CI +2.9 to +6.5) at 2.4x latency."></a>
</p>

| Project | What it is | Headline result | Links |
|---|---|---|---|
| [**aiwatch**](https://github.com/sushmit-gujar/aiwatch) | Find → fix → monitor for AI stacks: ML deps + MCP servers vs live OSV advisories, risky loaders, HF refs, model artifacts; resolver-aware fixes; daily Action with SARIF, tracking issue and dashboard | Demo app: 257 advisories → 0 after `aiwatch fix` (272 findings resolved); 129 newly disclosed advisories flagged vs a baseline; 899/900 agreement with OSV.dev | [repo](https://github.com/sushmit-gujar/aiwatch) · [dashboard](https://sushmit-gujar.github.io/aiwatch/) |
| [**loadsafe**](https://github.com/sushmit-gujar/loadsafe) | ML model supply-chain scanner (pickle/PyTorch/joblib/NumPy, safetensors, ONNX, GGUF, Keras, HF repos) → SARIF + CycloneDX ML-BOM | 100% detection / 0% FPR on its own 26-file PoC corpus (picklescan 33%, modelscan 44%) | [repo](https://github.com/sushmit-gujar/loadsafe) |
| [**mcp-warden**](https://github.com/sushmit-gujar/mcp-warden) | MCP security gateway: policy-as-code, redaction, injection scanning, pinning, exact-call approvals, tamper-evident audit | 30/30 attacks stopped, 12/12 benign allowed; held-out 6/8 (ensemble); +0.78 ms p50 | [repo](https://github.com/sushmit-gujar/mcp-warden) |
| [**hopscope**](https://github.com/sushmit-gujar/hopscope) | GraphRAG vs vector RAG multi-hop benchmark (HotpotQA, 1,000 q) | Full@5 0.699 → 0.746 (+4.7 pts, 95% CI +2.9..+6.5) at 2.4× latency | [repo](https://github.com/sushmit-gujar/hopscope) · [demo](https://sushmit-gujar.github.io/hopscope/) |

### Stack

<p align="center"><img src="assets/stack.svg" width="100%" alt="GenAI: RAG, agentic AI, multi-agent systems, LLM evaluation, embeddings, knowledge graphs, explainable AI. AI security: MCP, guardrails, OWASP LLM Top 10, MITRE ATLAS, SARIF, CycloneDX ML-BOM. ML and MLOps: Python, deep learning, NLP, MLflow, Kubeflow, Airflow, Docker, Kubernetes. Data and cloud: PySpark, SQL, Azure Databricks, Delta Lake, Snowflake, AWS Lambda, Dgraph."></p>

<sub>Every graphic here is a self-hosted SVG with no third-party stat services. Text is outlined from OFL fonts (Orbitron, JetBrains Mono, Space Grotesk) and the animation respects <code>prefers-reduced-motion</code>. To regenerate them, run <code>pip install fonttools && python scripts/build_svgs.py</code>.</sub>
