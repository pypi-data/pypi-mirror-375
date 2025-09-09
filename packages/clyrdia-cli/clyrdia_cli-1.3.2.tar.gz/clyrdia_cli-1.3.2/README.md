# Clyrdia CLI MVP

🚀 **Lean, powerful, and rapidly deployable AI quality gates for CI/CD**

> **Note**: This is the MVP version of Clyrdia CLI. For the full version, see the main repository.

Clyrdia MVP is a streamlined version focused exclusively on providing automated AI quality gates in CI/CD pipelines. This version eliminates complexity and focuses on the core value proposition: helping teams run `clyrdia-cli benchmark` inside a GitHub Action and see clear, valuable results.

## 🎯 MVP Focus

- **Single Use Case**: Automated AI quality gates in CI/CD
- **Two Providers Only**: OpenAI and Anthropic (production-ready models)  
- **Two-Tier System**: Developer (Free) and Business ($500/month)
- **Zero Complexity**: No team management, no complex features, just benchmarking

## 🚀 Quick Start

### 1. Installation

```bash
pip install clyrdia-cli
```

### 2. Authentication

```bash
clyrdia-cli login
```

### 3. Initialize Benchmark

```bash
clyrdia-cli init --name "My CI/CD Quality Gate"
```

### 4. Set API Keys

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### 5. Run Benchmark

```bash
clyrdia-cli benchmark
```

### 6. View Results

```bash
clyrdia-cli dashboard
```

## 📋 Available Commands

### Authentication
- `login` - Authenticate with API key
- `logout` - Remove authentication  
- `status` - Show account status

### Core Benchmarking
- `init` - Initialize benchmark configuration
- `benchmark` - Run AI benchmark tests
- `models` - List available models
- `compare` - Compare two models

### Results & Dashboard
- `dashboard` - Start local dashboard
- `dashboard-status` - Check dashboard status

### Management
- `cache` - Manage result cache
- `tutorial` - Show quick start guide
- `version` - Show version info
- `commands` - Show command reference

### CI/CD Integration
- `cicd generate` - Generate CI/CD templates
- `cicd platforms` - List CI/CD platforms
- `cicd test` - Test CI/CD functionality

## 🤖 Supported Models

### OpenAI
- `gpt-4o` - Flagship multimodal model
- `gpt-4o-mini` - Fast, cost-effective model
- `gpt-4o-2024-08-01` - Specific version

### Anthropic
- `claude-3-5-sonnet-20241022` - Balanced performance
- `claude-3-5-haiku-20241022` - Fast and efficient
- `claude-3-opus-20240229` - Most capable model

## 💰 Pricing

- **Developer**: Free - 100 credits/month
- **Business**: $500/month - 25,000 credits/month + CI/CD features

## 🔧 CI/CD Integration

Generate GitHub Actions workflow:

```bash
clyrdia-cli cicd generate --platform github-actions
```

This creates a workflow that:
- Runs on every push and PR
- Executes AI quality gates
- Fails the build if quality thresholds aren't met
- Uploads results as artifacts

## 📊 Dashboard

The local dashboard provides:
- Real-time metrics and analytics
- Model performance comparison
- Cost analysis and optimization
- Historical trend analysis
- Detailed result inspection

## 🏗️ Architecture

The MVP uses a simplified architecture:

```
clyrdia/
├── core/           # Consolidated core logic
│   ├── licensing.py    # Authentication & credits
│   ├── benchmarking.py # Benchmark execution
│   ├── providers.py    # OpenAI & Anthropic only
│   ├── evaluator.py    # Quality assessment
│   ├── caching.py      # Result caching
│   ├── database.py     # SQLite storage
│   └── models.py       # All data classes
├── cli_mvp.py      # MVP CLI implementation
├── dashboard.py    # Local dashboard
└── config.py       # Configuration
```

## 🎯 Key Simplifications

1. **Consolidated Core**: All core logic in single `core/` directory
2. **Two Providers Only**: OpenAI and Anthropic (no Google, Cohere, etc.)
3. **Two-Tier System**: Developer and Business only (no Pro tier)
4. **Essential Commands**: Only commands that directly support CI/CD quality gates
5. **Simplified Database**: No complex team management tables
6. **Decoupled Dashboard**: No Node.js process management

## 🚀 Getting to $100k MRR

This MVP is designed for rapid deployment and customer acquisition:

1. **Fast Testing**: Minimal surface area for bugs
2. **Clear Value**: Focused on one high-value use case
3. **Easy Sales**: Simple two-tier pricing
4. **Quick Onboarding**: Streamlined user experience
5. **CI/CD Native**: Built for the target market

## 📈 Next Steps

1. Deploy MVP to production
2. Get first 10 paying customers
3. Iterate based on feedback
4. Add features only if they directly support the core use case
5. Scale to $100k MRR

---

**Built for speed. Built for value. Built for CI/CD.**