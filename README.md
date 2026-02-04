# 🛡️ AI-Powered Security Operations Center (SOC)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MITRE ATT&CK](https://img.shields.io/badge/MITRE-ATT%26CK-red.svg)](https://attack.mitre.org/)
[![Kafka](https://img.shields.io/badge/Apache-Kafka-black.svg)](https://kafka.apache.org/)
[![LLM](https://img.shields.io/badge/LLM-Llama%203-purple.svg)](https://llama.meta.com/)

> An intelligent Security Operations Center that autonomously detects and responds to cyberattacks using Large Language Models (Llama 3), Machine Learning, and explainable AI mapped to the MITRE ATT&CK framework.

[🎥 Watch Demo](#demo) | [📖 Read Docs](#documentation) | [🚀 Quick Start](#quick-start) | [📊 Results](#results)

---

## 🎯 Project Highlights

- **95%+ Detection Accuracy** against real-world cyberattacks (SSH brute-force, port scans, web exploits)
- **40% Reduction in False Positives** through ML-based confidence calibration
- **Real-time Processing**: 1000+ events/minute with <500ms latency
- **Explainable AI**: Every threat includes MITRE ATT&CK technique + human-readable justification
- **Production-Grade Architecture**: Distributed, scalable, resilient with Apache Kafka

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Results](#results)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🔍 Overview

Modern Security Operations Centers (SOCs) face a critical challenge: **95% of security alerts are false positives**, overwhelming analysts and causing alert fatigue. This project addresses this problem by building an **AI-powered SOC** that:

1. **Autonomously detects** cyberattacks using local LLM (Llama 3) + Machine Learning
2. **Reduces false positives** by 40% through confidence calibration techniques
3. **Explains decisions** with MITRE ATT&CK mapping and natural language justifications
4. **Scales horizontally** using Apache Kafka message queues

### Problem Statement

- Security analysts spend **70% of their time** investigating false positives
- Traditional rule-based systems miss **zero-day attacks** and novel attack patterns
- Black-box AI decisions lack **explainability** required for security operations

### Solution

A multi-agent SOC architecture combining:
- **Unsupervised ML** (Isolation Forest) for anomaly detection
- **Large Language Models** for intelligent threat assessment
- **Confidence Calibration** (Platt/Temperature Scaling) for accuracy
- **MITRE ATT&CK Integration** for standardized threat intelligence

---

## 🏗️ Architecture

### High-Level Pipeline

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐
│  Log Tailer │ --> │  Collector   │ --> │   Features   │ --> │  Anomaly   │
│ /var/log/*  │     │ (Normalize)  │     │  Extractor   │     │  Detector  │
└─────────────┘     └──────────────┘     └──────────────┘     └────────────┘
                                                                      |
                    ┌──────────────┐     ┌──────────────┐           |
                    │  Responder   │ <-- │   Analyzer   │ <---------+
                    │   (Action)   │     │ (LLM: Llama3)│
                    └──────────────┘     └──────────────┘
                           |                     |
                    ┌──────v──────┐     ┌───────v────────┐
                    │ Trust Agent │     │ MITRE Mapper   │
                    │ (Calibrate) │     │ XAI Explainer  │
                    └─────────────┘     └────────────────┘
```

### Component Flow

| Component | Input | Output | Function |
|-----------|-------|--------|----------|
| **Log Tailer** | System logs | Raw events | Reads `/var/log/auth.log`, `/var/log/nginx/access.log` |
| **Collector** | Raw events | Normalized events | Enriches with metadata (timestamp, source IP) |
| **Feature Extractor** | Normalized events | Feature vectors | Extracts ML features (frequency, time deltas, codes) |
| **Anomaly Detector** | Feature vectors | Anomaly scores | Isolation Forest assigns 0-1 anomaly score |
| **Analyzer** | Events + scores | Threat assessment | LLM (Llama 3) analyzes threat level + confidence |
| **Trust Agent** | LLM confidence | Calibrated confidence | Platt/Temperature Scaling reduces false positives |
| **MITRE Mapper** | Threat events | MITRE techniques | Maps attacks to ATT&CK framework (T1110, T1046, T1190) |
| **XAI Explainer** | MITRE events | Explanations | Generates human-readable justifications |
| **Responder** | Final events | Actions | BLOCK / ALERT / MONITOR based on threat level |

### Distributed Architecture (Kafka)

All agents communicate via **Apache Kafka topics** for scalability:

```
events_raw → events_collected → events_with_features → events_with_anomaly
→ events_analyzed → events_calibrated → events_with_mitre → events_explained
→ events_final → alerts
```

---

## ✨ Features

### 🤖 AI-Powered Detection
- **Local LLM Integration**: Llama 3 (8B) via LM Studio for privacy & low-latency
- **Hybrid Scoring**: Combines heuristics + ML anomaly scores + LLM assessment
- **Zero-Day Detection**: Unsupervised learning detects unknown attack patterns

### 📊 Machine Learning
- **Isolation Forest**: Anomaly detection on extracted features
- **Confidence Calibration**: Platt Scaling & Temperature Scaling
- **Model Evaluation**: ROC curves, AUC, Brier scores, reliability diagrams

### 🔍 Explainability
- **MITRE ATT&CK Mapping**: Automatic technique classification (T1110, T1046, T1190)
- **XAI Module**: Natural language explanations for every threat decision
- **Transparency**: Full audit trail of detection logic

### 📈 Performance
- **Real-time**: <500ms average latency per event
- **Scalable**: Kafka architecture handles 1000+ events/min
- **Resilient**: Fault-tolerant with consumer groups

### 🎯 Attack Coverage
Validated against real-world attacks:
- ✅ **SSH Brute-Force** (Hydra) → T1110 (Credential Access)
- ✅ **Port Scanning** (Nmap) → T1046 (Discovery)
- ✅ **Web Fuzzing** (Gobuster) → T1190 (Initial Access)

---

## 🚀 Quick Start

### Prerequisites

- **OS**: Ubuntu 20.04+ (or Docker)
- **RAM**: 16GB minimum
- **Disk**: 100GB free space
- **Python**: 3.10+
- **Docker**: Latest version

### One-Command Setup (Docker)

```bash
git clone https://github.com/yourusername/ai-powered-soc.git
cd ai-powered-soc
docker-compose up -d
./scripts/setup.sh
./scripts/start_all.sh
```

### Access Dashboard

```bash
# Open in browser
http://localhost:5000
```

### Run Test Attacks

```bash
# From Kali Linux machine
cd attacks/scripts
./run_all_attacks.sh
```

---

## 📦 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/ai-powered-soc.git
cd ai-powered-soc
```

### Step 2: Install Dependencies

```bash
# System packages
sudo apt update && sudo apt install -y python3 python3-pip docker.io

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Start Infrastructure

```bash
# Start Kafka, Zookeeper, PostgreSQL
docker-compose up -d

# Create Kafka topics
./scripts/create_topics.sh

# Initialize database
./scripts/init_db.sh
```

### Step 4: Install LM Studio

```bash
# Download from: https://lmstudio.ai/
# Install and download Llama-3-8B-Instruct model
# Start local server on port 1234
```

### Step 5: Configure

```bash
# Edit configuration
nano config/config.yaml

# Set your network IPs for Kali/Ubuntu
nano attacks/config_attacks.yaml
```

### Step 6: Start Agents

```bash
# Start all SOC agents
./scripts/start_all.sh

# Check logs
tail -f logs/soc-ia.log
```

---

## 💻 Usage

### Running the Complete Pipeline

```bash
# Start SOC
source venv/bin/activate
./scripts/start_all.sh

# In another terminal, monitor events
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic events_final \
  --from-beginning
```

### Simulating Attacks (from Kali Linux)

```bash
# SSH Brute-Force
cd attacks/scripts
./01_ssh_bruteforce.sh

# Network Scan
./02_nmap_scan.sh

# Web Fuzzing
./03_http_fuzzing.sh

# Or run all attacks
./run_all_attacks.sh
```

### Viewing Results

```bash
# Web dashboard
http://localhost:5000

# Database query
psql -h localhost -U socuser -d socdb
SELECT * FROM events WHERE threat_level = 'critical';

# Jupyter notebooks (analysis)
cd notebooks
jupyter notebook
```

---

## 📊 Results

### Detection Performance

| Metric | Before AI | With AI | Improvement |
|--------|-----------|---------|-------------|
| **Detection Rate** | 78% | **95%** | **+17%** |
| **False Positive Rate** | 25% | **15%** | **-40%** |
| **Response Time** | 2.3s | **0.4s** | **-82%** |
| **Analyst Workload** | 100% | **60%** | **-40%** |

### Scientific Validation

**ROC Curve Analysis:**
- AUC Score: **0.93** (Excellent)
- Optimal threshold: 0.72

**Calibration Metrics:**
- Brier Score (before): 0.35
- Brier Score (after): **0.18** (-48%)

**MITRE ATT&CK Coverage:**
- Techniques Mapped: **10+**
- Tactics Covered: **6** (Initial Access, Execution, Discovery, Credential Access, etc.)

### Example Detections

```json
{
  "event_id": "a3b2c1d4",
  "timestamp": "2025-02-04T14:23:15Z",
  "message": "Failed password for admin from 192.168.1.100",
  "anomaly_score": 0.89,
  "threat_level": "critical",
  "llm_confidence": 0.87,
  "calibrated_confidence": 0.92,
  "mitre_techniques": [
    {
      "technique_id": "T1110",
      "technique_name": "Brute Force",
      "tactic": "Credential Access"
    }
  ],
  "xai_explanation": "This event represents a brute-force attack attempt targeting the SSH service. The repeated failed authentication attempts from a single IP (192.168.1.100) match the T1110 MITRE technique pattern.",
  "action_taken": "BLOCK"
}
```

---

## 📁 Project Structure

```
ai-powered-soc/
├── agents/                      # All SOC agents
│   ├── common/                  # Shared utilities
│   │   ├── kafka_utils.py       # Kafka producer/consumer
│   │   └── lm_client.py         # LM Studio API client
│   ├── log_tailer/              # Log ingestion
│   ├── collector/               # Event normalization
│   ├── features/                # Feature extraction
│   ├── anomaly_detector/        # Isolation Forest ML
│   ├── analyzer/                # LLM threat analysis
│   ├── trust_agent/             # Confidence calibration
│   ├── mitre_mapper/            # MITRE ATT&CK mapping
│   ├── xai_explainer/           # Explainable AI
│   └── responder/               # Automated response
│
├── attacks/                     # Attack simulation scripts (Kali)
│   └── scripts/
│       ├── 01_ssh_bruteforce.sh
│       ├── 02_nmap_scan.sh
│       └── 03_http_fuzzing.sh
│
├── config/                      # Configuration files
│   └── config.yaml              # Central config
│
├── data/                        # Data storage
│   ├── models/                  # Trained ML models
│   ├── mitre/                   # MITRE techniques DB
│   └── raw/                     # Raw logs
│
├── dashboard/                   # Web dashboard
│   ├── app.py                   # Flask app
│   └── templates/
│
├── notebooks/                   # Jupyter analysis notebooks
│   ├── calibration_analysis.ipynb
│   ├── anomaly_detection.ipynb
│   └── mitre_analysis.ipynb
│
├── scripts/                     # Automation scripts
│   ├── start_all.sh             # Start all agents
│   ├── create_topics.sh         # Kafka setup
│   └── setup.sh                 # Installation
│
├── tests/                       # Unit & integration tests
│   └── test_agents.py
│
├── docker-compose.yml           # Infrastructure orchestration
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── LICENSE                      # MIT License
```

---

## 🛠️ Technologies

### Core Technologies

- **Python 3.10+**: Main programming language
- **Apache Kafka**: Message queue for distributed architecture
- **PostgreSQL**: Event storage and analytics
- **Docker**: Containerization

### AI/ML Stack

- **LM Studio + Llama 3 (8B)**: Local LLM inference
- **scikit-learn**: Machine Learning (Isolation Forest)
- **NumPy/Pandas**: Data processing

### Security Tools

- **MITRE ATT&CK Framework**: Threat intelligence taxonomy
- **Kali Linux**: Attack simulation environment
- **Hydra**: SSH brute-force testing
- **Nmap**: Network scanning
- **Gobuster**: Web fuzzing

### DevOps

- **Flask**: Web dashboard
- **Jupyter**: Scientific analysis
- **Docker Compose**: Service orchestration

---

## 📈 Roadmap

- [x] Core pipeline (log_tailer → responder)
- [x] ML anomaly detection (Isolation Forest)
- [x] LLM integration (Llama 3)
- [x] Confidence calibration
- [x] MITRE ATT&CK mapping
- [x] Explainable AI (XAI)
- [x] Kafka distributed architecture
- [ ] Real-time dashboard (Grafana)
- [ ] Advanced ML models (Deep Learning)
- [ ] Multi-model LLM support (Mixtral, GPT)
- [ ] API for external integrations
- [ ] Kubernetes deployment



## 🙏 Acknowledgments

- **MITRE ATT&CK** for the threat intelligence framework
- **LM Studio** for local LLM inference
- **Apache Kafka** community
- **scikit-learn** contributors
- **FSTT** faculty for academic support

---

## 📚 Documentation

For detailed documentation, see:

- [Installation Guide](docs/installation.md)
- [Architecture Deep Dive](docs/architecture.md)
- [API Reference](docs/api.md)
- [Scientific Report](docs/scientific_report.pdf)

---

## 🎥 Demo

### Screenshots

**Dashboard Overview:**
![Dashboard](screenshots/dashboard.png)

**Attack Detection:**
![Attack Detection](screenshots/detection.png)

**MITRE Heatmap:**
![MITRE Heatmap](screenshots/mitre_heatmap.png)

### Video

[▶️ Watch 2-minute demo on YouTube](https://youtube.com/watch?v=your-video)



<div align="center">

Made with ❤️ by Chaimae | 🛡️ Securing the Future with AI

</div>
