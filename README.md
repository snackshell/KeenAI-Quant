# KeenAI-Quant Trading System

AI-powered quantitative trading system for 4 trading pairs: EUR/USD, XAU/USD, BTC/USD, and ETH/USD.

## Features

- **AI-Powered Decision Making**: Uses OpenRouter with DeepSeek V3.2 for intelligent trade analysis
- **4-Pair Focus**: Optimized for EUR/USD, XAU/USD, BTC/USD, ETH/USD
- **OpenAlgo Integration**: Uses OpenAlgo for MT5/Exness broker connectivity
- **Comprehensive Risk Management**: Circuit breakers, position sizing, drawdown control
- **Real-time Dashboard**: Next.js frontend with live updates
- **Backtesting Engine**: Test strategies on historical data
- **Telegram Notifications**: Leverages OpenAlgo's Telegram bot for trade alerts

## System Requirements

- **RAM**: 8GB (system will use max 4GB)
- **Storage**: 50GB free space (system will use max 40GB)
- **GPU**: Not required (AI models accessed via API)
- **CPU**: Any modern CPU (1.2GHz+)
- **OS**: Windows, Linux, or macOS

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Node.js 18+
- MT5 Terminal installed
- Exness account (or other MT5 broker)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd KeenAIQuant

# Set up Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r openalgo/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys:
# - OPENROUTER_API_KEY (get from https://openrouter.ai/)
# - MT5 credentials
# - OpenAlgo API key (generate from OpenAlgo dashboard)
```

### 4. Start OpenAlgo

```bash
# OpenAlgo provides broker integration
cd openalgo
python app.py
# Access at http://127.0.0.1:5000
# Configure MT5/Exness broker in OpenAlgo dashboard
# Generate API key from Settings → API Keys
```

### 5. Start KeenAI Backend

```bash
# In a new terminal
cd backend
python main.py
# Backend API runs on http://127.0.0.1:8000
```

### 6. Start Frontend

```bash
# In a new terminal
cd frontend
npm run dev
# Dashboard available at http://localhost:3000
```

## Project Structure

```
KeenAIQuant/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application entry
│   ├── config.py           # Configuration management
│   └── ...
├── frontend/               # Next.js frontend
│   ├── app/               # Next.js 14 app directory
│   ├── components/        # React components
│   └── ...
├── openalgo/              # OpenAlgo broker integration
│   ├── app.py            # OpenAlgo Flask app
│   ├── broker/           # Broker adapters (MT5, etc.)
│   └── services/         # Trading services
├── AI_Core/              # AI agents and strategies
│   ├── agents/          # Individual AI agents
│   ├── models/          # AI model handlers
│   └── strategies/      # Trading strategies
├── Data_Engine/         # Market data processing
│   └── technical_analysis/  # Indicators and patterns
├── Risk_Management/     # Risk controls
│   ├── circuit_breakers.py
│   ├── position_sizing.py
│   └── risk_assessor.py
├── Broker_Integration/  # OpenAlgo wrapper
├── Backtesting/        # Strategy backtesting
├── Logging_Monitoring/ # System monitoring
├── config.yaml         # Main configuration
├── .env               # Environment variables
└── README.md          # This file
```

## Configuration

Edit `config.yaml` to customize:

- **Trading pairs**: Default is EUR/USD, XAU/USD, BTC/USD, ETH/USD
- **AI model**: Choose from DeepSeek, Claude, GPT-4, Gemini, or Llama models
- **Risk parameters**: Position size, daily loss limits, drawdown thresholds
- **Strategy settings**: Enable/disable specific strategies per pair

## Trading Strategies

1. **Trend Following**: EMA crossover + ADX filter (all 4 pairs)
2. **Mean Reversion**: RSI + Bollinger Bands (EUR/USD, XAU/USD)
3. **Breakout**: Consolidation detection + volume (BTC/USD, ETH/USD)

## Risk Management

- **Max Position Size**: 25% of account per trade
- **Daily Loss Limit**: 5% of starting balance
- **Max Drawdown**: 15% from equity peak
- **Risk per Trade**: 2% of account
- **Min Risk-Reward**: 1:1.5

## API Documentation

Once the backend is running, access API docs at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Monitoring

- **Dashboard**: Real-time positions, P&L, and system status
- **Logs**: `logs/keenai.log` with daily rotation
- **Telegram**: Configure OpenAlgo's Telegram bot for mobile alerts
- **Performance Metrics**: Track AI agent and strategy performance

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style

- Python: Follow PEP 8
- TypeScript: ESLint + Prettier
- Use type hints in Python
- Use TypeScript strict mode

## Troubleshooting

### OpenAlgo Connection Issues
- Ensure OpenAlgo is running on port 5000
- Check API key is valid in OpenAlgo dashboard
- Verify MT5 terminal is logged in

### AI API Errors
- Check OPENROUTER_API_KEY is valid in .env
- Verify internet connection
- Check OpenRouter credits and rate limits at https://openrouter.ai/
- Try switching to a different model in config.yaml

### Memory Issues
- System is designed for 8GB RAM
- If issues occur, reduce buffer sizes in config.yaml
- Disable unused strategies

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Your Repo URL]
- Discord: [Your Discord]
- Documentation: [Your Docs URL]

## Disclaimer

This software is for educational purposes only. Trading involves risk. Never trade with money you cannot afford to lose. Past performance does not guarantee future results.
