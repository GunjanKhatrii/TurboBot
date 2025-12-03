```markdown
# TurboBot: AI-Powered Wind Turbine Performance Assistant 🌬️🤖

<div align="center">

![Wind Turbine](https://img.shields.io/badge/Industry-Renewable_Energy-green)
![AI](https://img.shields.io/badge/AI-GPT--4_|_Claude-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Your intelligent companion for wind turbine monitoring and predictive maintenance**

[Demo](#-demo) • [Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🎯 What is TurboBot?

**TurboBot** is an AI-powered conversational assistant designed to revolutionize wind turbine operations. Built by renewable energy professionals for operators in the field, TurboBot transforms complex sensor data into clear, actionable insights through natural language conversations.

Instead of drowning in 200+ sensor readings per minute across dozens of turbines, operators can simply ask TurboBot: *"What's wrong with Turbine 5?"* and get instant, intelligent analysis.

### The Problem We Solve

- 💰 **Wind turbine failures cost $250K-500K** per incident
- 📊 **Data overload**: Each turbine generates 12,000+ data points per hour
- ⏰ **Manual analysis takes hours** when decisions need to happen in minutes
- 🔧 **80% of failures are preventable** with early detection

### Our Solution

TurboBot provides:
- 🤖 **Conversational AI** that understands turbine operations
- 📈 **Real-time anomaly detection** using intelligent thresholds
- 💡 **Root cause analysis** with maintenance recommendations
- 📊 **Interactive dashboards** for visual insights
- ⚡ **Instant responses** to natural language queries

---

## ✨ Features

### 🎯 Core Capabilities

| Feature | Description |
|---------|-------------|
| **Smart Monitoring** | Real-time tracking of power output, temperature, vibration, and wind speed |
| **Anomaly Detection** | AI-powered detection of performance degradation and equipment issues |
| **Predictive Alerts** | Early warning system for potential failures (48-72 hours advance notice) |
| **Natural Language Chat** | Ask questions in plain English, get expert-level answers |
| **Trend Analysis** | Automatic identification of concerning patterns over time |
| **Maintenance Recommendations** | Actionable guidance with priority levels and cost estimates |

### 💬 Chat with TurboBot

**Example Conversations:**

```
You: "What's the current status of the turbine?"

TurboBot: "Turbine T005 is operating with warnings. Power output is 
1,245 kW (15% below expected). Temperature has risen to 72°C, which 
is 12°C above normal. I recommend checking the gearbox for potential 
bearing issues."

You: "How urgent is this?"

TurboBot: "Medium-high priority. Based on the temperature trend and 
vibration levels, I recommend scheduling an inspection within 48 hours. 
Delaying could escalate to a full gearbox failure ($250K+ repair cost)."

You: "What should I tell the maintenance team?"

TurboBot: "I'll generate a work order:

**Maintenance Report**
• Issue: Gearbox overheating with elevated vibration
• Estimated Repair Cost: $4,500
• Recommended Inspection Window: Within 48 hours
• Tools Needed: Thermal camera, vibration analyzer, gearbox oil sample kit"
```

### 📊 Dashboard Features

- **Real-time Metrics Cards**: Power, wind speed, temperature, status at a glance
- **Interactive Time-Series Charts**: Track performance over 6-48 hours
- **Power Curve Analysis**: Wind speed vs. power output visualization
- **Alert Panel**: Color-coded warnings with severity levels
- **Trend Indicators**: Automatic detection of increasing/decreasing patterns

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (3.11 recommended)
- **API Key** from OpenAI (GPT-4) or Anthropic (Claude)
- **Anaconda** (recommended) or pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/GunjanKhatrii/turbobot-wind-turbine-ai.git
cd turbobot-wind-turbine-ai

# 2. Create virtual environment
conda create -n turbobot python=3.11
conda activate turbobot

# OR using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env and add your API key:
# OPENAI_API_KEY=sk-your-key-here
# OR
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Generate Sample Data (If needed)

```bash
python src/generate_sample_data.py
```

### Run TurboBot

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` and start chatting with TurboBot! 🎉

---

## 📁 Project Structure

```
turbobot-wind-turbine-ai/
├── app.py                          # Main Streamlit application
├── src/
│   ├── __init__.py
│   ├── data_analysis.py           # Turbine data analysis module
│   ├── ai_assistant.py            # TurboBot AI integration
│   └── generate_sample_data.py    # Sample data generator
├── data/
│   ├── raw/                       # Raw SCADA data (CSV files)
│   │   └── turbine_data.csv
│   └── knowledge_base/            # Domain knowledge for RAG
│       └── turbine_manual.txt
├── notebooks/
│   └── 01_data_exploration.ipynb  # Data exploration notebook
├── docs/
│   ├── ARCHITECTURE.md            # Technical architecture
│   └── USER_GUIDE.md              # User guide
├── tests/
│   └── test_analysis.py           # Unit tests
├── .env.example                   # Environment variables template
├── .gitignore
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── LICENSE                        # MIT License
```

---

## 🛠️ Technology Stack

### AI & ML
- **Large Language Models**: OpenAI GPT-4 / Anthropic Claude 3.5 Sonnet
- **AI Patterns**: RAG (Retrieval-Augmented Generation), ReAct (Reasoning + Acting)
- **Memory Management**: Conversation history with context retention

### Data & Analysis
- **Data Processing**: Pandas, NumPy
- **Statistical Analysis**: SciPy
- **Anomaly Detection**: Rule-based + threshold analysis

### Frontend & Visualization
- **Web Framework**: Streamlit
- **Charts**: Plotly (interactive), Matplotlib
- **UI Components**: Streamlit native components

### Development
- **Language**: Python 3.11
- **Environment Management**: Conda / venv
- **Version Control**: Git, GitHub

---

## 📖 Documentation

### How TurboBot Works

#### 1. **Data Ingestion**
TurboBot loads SCADA (Supervisory Control and Data Acquisition) data from wind turbines:
- Power output (kW)
- Wind speed (m/s)
- Temperature (°C)
- Vibration levels
- Operational status

#### 2. **Analysis Engine**
The `TurbineAnalyzer` class performs:
- **Statistical calculations**: Averages, trends, deviations
- **Anomaly detection**: Temperature thresholds, vibration limits, power curve analysis
- **Trend identification**: Increasing/decreasing patterns over time

#### 3. **AI Intelligence (TurboBot Brain)**
The `TurbineAIAssistant` uses:
- **LLM Integration**: GPT-4/Claude for natural language understanding
- **RAG Pattern**: Retrieves relevant maintenance manuals and best practices
- **Tool Use**: Triggers data analysis functions based on queries
- **Memory**: Maintains conversation context for follow-up questions

#### 4. **User Interface**
Streamlit dashboard provides:
- Real-time metrics visualization
- Interactive charts and graphs
- Chat interface for TurboBot conversations
- Alert notifications

### Agentic AI Principles

TurboBot implements the **ReAct (Reasoning + Acting) pattern**:

```
User Query → TurboBot Process:
├── 1. OBSERVE: Receive sensor data and user question
├── 2. REASON: Analyze patterns, compare to thresholds
├── 3. ACT: Run calculations, query knowledge base
├── 4. REFLECT: Evaluate findings, determine severity
└── 5. RESPOND: Generate clear, actionable answer
```

### Data Flow

```
┌─────────────────┐
│  SCADA Data     │ (CSV files)
│  (Sensors)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Analysis   │ (pandas, numpy)
│ Module          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ TurboBot AI     │ (GPT-4/Claude + RAG)
│ Assistant       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Streamlit UI    │ (Dashboard + Chat)
│                 │
└─────────────────┘
```

---

## 🎮 Usage Examples

### Quick Questions

**Status Check:**
```
You: "How's the turbine doing?"
TurboBot: "Overall status is WARNING. Operating at 1,245 kW with 
elevated temperature (72°C). Performance is 15% below expected."
```

**Issue Diagnosis:**
```
You: "Why is the power output low?"
TurboBot: "Power is low due to three factors:
1. Current output: 1,245 kW vs expected 1,460 kW
2. Temperature at 72°C indicates gearbox stress
3. Vibration at 4.2 suggests bearing wear

Likely cause: Gearbox bearing degradation reducing efficiency."
```

**Maintenance Planning:**
```
You: "What should I do about this?"
TurboBot: "Recommended actions:

**Immediate (Next 48 hours):**
• Schedule gearbox inspection
• Check bearing condition
• Take oil sample for analysis

**Priority:** Medium-High
**Estimated Cost:** $4,500 for repair
**Risk if delayed:** Possible complete failure ($250K+)"
```

**Trend Analysis:**
```
You: "Is this getting worse?"
TurboBot: "Yes, declining trend detected:
• Temperature: +8°C over last 12 hours
• Vibration: +1.2 over last 12 hours
• Power: -15% over last 12 hours

Pattern indicates accelerating degradation. Recommend expedited inspection."
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# AI Provider (choose one)
OPENAI_API_KEY=sk-your-openai-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional settings
AI_PROVIDER=openai  # or "anthropic"
AI_MODEL=gpt-4      # or "claude-3-5-sonnet-20241022"
TEMPERATURE=0.7
MAX_TOKENS=500
```

### Customization

**Adjust Detection Thresholds** (`src/data_analysis.py`):

```python
# Temperature thresholds
TEMP_WARNING = 70  # °C
TEMP_CRITICAL = 75  # °C

# Vibration thresholds
VIB_WARNING = 4.0
VIB_CRITICAL = 4.5

# Performance degradation
POWER_THRESHOLD = 0.85  # 85% of expected
```

**Modify AI Behavior** (`src/ai_assistant.py`):

```python
# Adjust system prompt for different tone/focus
self.system_prompt = """You are TurboBot, an expert wind turbine analyst.
Your personality: Professional, concise, safety-focused.
Priority: Always emphasize safety and cost implications."""
```

---

## 📊 Sample Data

### SCADA Data Format

TurboBot expects CSV files with these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `timestamp` | datetime | Measurement time | 2024-12-03 14:30:00 |
| `turbine_id` | string | Turbine identifier | T005 |
| `wind_speed` | float | Wind speed in m/s | 9.2 |
| `power_output` | float | Power in kW | 1245.0 |
| `temperature` | float | Gearbox temp in °C | 72.5 |
| `vibration` | float | Vibration level | 4.2 |
| `status` | string | Operating status | warning |

### Data Sources

**Public Datasets:**
- [NREL Wind Toolkit](https://www.nrel.gov/grid/wind-toolkit.html)
- [Kaggle Wind Turbine SCADA](https://www.kaggle.com/datasets/berkerisen/wind-turbine-scada-dataset)
- [OpenEI Wind Data](https://openei.org/datasets/)

**Generate Synthetic Data:**
```bash
python src/generate_sample_data.py --days 7 --turbines 1
```

---

## 🧪 Testing

### Run Analysis Tests

```bash
# Test data analysis module
python src/data_analysis.py

# Test AI assistant (requires API key)
python src/ai_assistant.py
```

### Unit Tests (Coming Soon)

```bash
pytest tests/
```

---

## 🚢 Deployment

### Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add API key in **Secrets** section:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   ```
5. Click **Deploy**

Your TurboBot will be live at: `https://turbobot.streamlit.app`

### Docker Deployment (Optional)

```bash
# Build image
docker build -t turbobot .

# Run container
docker run -p 8501:8501 --env-file .env turbobot
```

---

## 🎯 Roadmap

### ✅ Completed (v1.0)
- [x] Real-time dashboard
- [x] AI chat assistant
- [x] Anomaly detection
- [x] Basic RAG implementation
- [x] Sample data generation

### 🚧 In Progress (v1.1)
- [ ] Multi-turbine support
- [ ] Historical data comparison
- [ ] Export reports (PDF)
- [ ] Email alert system

### 🔮 Future Plans (v2.0)
- [ ] Advanced ML predictions (LSTM models)
- [ ] Mobile app version
- [ ] Real-time SCADA integration
- [ ] Multi-language support
- [ ] Voice interface
- [ ] Integration with maintenance management systems

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

- 🐛 **Report Bugs**: Open an issue with detailed description
- 💡 **Suggest Features**: Share your ideas in discussions
- 📖 **Improve Documentation**: Fix typos, add examples
- 🔧 **Submit Code**: Fork, make changes, open PR

### Development Setup

```bash
# Fork the repo and clone
git clone https://github.com/YOUR_USERNAME/turbobot-wind-turbine-ai.git
cd turbobot-wind-turbine-ai

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and commit
git commit -m "Add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to functions
- Comment complex logic
- Update README for new features

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Gunjan Khatri

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 🙏 Acknowledgments

### Data Sources
- **NREL** (National Renewable Energy Laboratory) for public SCADA datasets
- **Kaggle Community** for wind turbine data contributions

### Technology
- **OpenAI** for GPT-4 API
- **Anthropic** for Claude API
- **Streamlit** for amazing web framework

### Inspiration
- Wind farm operators who inspired this project
- Renewable energy community for domain knowledge
- Open-source AI community for tools and frameworks

---

## 📞 Contact & Support

### Author

**Gunjan Khatri**
- 📧 Email: [Gunjan2002khatri@gmail.com](mailto:Gunjan2002khatri@gmail.com)
- 💼 LinkedIn: [linkedin.com/in/gunjan-khatri-b6053a203](https://www.linkedin.com/in/gunjan-khatri-b6053a203/)
- 🐙 GitHub: [@GunjanKhatrii](https://github.com/GunjanKhatrii)

### Get Help

- **Issues**: [GitHub Issues](https://github.com/GunjanKhatrii/turbobot-wind-turbine-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/GunjanKhatrii/turbobot-wind-turbine-ai/discussions)
- **Email**: For private inquiries

### Show Your Support

If TurboBot helps you or you find it interesting:
- ⭐ **Star this repository**
- 🐛 **Report bugs** you find
- 💡 **Share feature ideas**
- 📢 **Tell others** about TurboBot

---

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/GunjanKhatrii/turbobot-wind-turbine-ai?style=social)
![GitHub forks](https://img.shields.io/github/forks/GunjanKhatrii/turbobot-wind-turbine-ai?style=social)
![GitHub issues](https://img.shields.io/github/issues/GunjanKhatrii/turbobot-wind-turbine-ai)
![GitHub pull requests](https://img.shields.io/github/issues-pr/GunjanKhatrii/turbobot-wind-turbine-ai)

---

## 🎬 Demo

### Screenshots

**Dashboard View:**
![Dashboard](docs/images/dashboard.png)

**Chat Interface:**
![Chat](docs/images/chat.png)

**Alert System:**
![Alerts](docs/images/alerts.png)



<div align="center">

**Made with ❤️ for the Renewable Energy Community**

**TurboBot** - *Amplifying human expertise, not replacing it*

[⬆ Back to Top](#turbobot-ai-powered-wind-turbine-performance-assistant-)

</div>
```
