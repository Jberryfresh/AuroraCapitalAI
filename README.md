# Aurora Capital AI

> **IMPORTANT**: This software is for educational and research purposes only. Not financial advice.

## Overview

Aurora Capital AI is a multi-agent system for analyzing publicly traded equities. It combines fundamental analysis, sentiment analysis, and historical patterns to generate research reports.

## ⚠️ Disclaimers

**IMPORTANT: READ CAREFULLY**

1. **Not Financial Advice**: 
   - This software and its outputs are for educational and informational purposes only.
   - Nothing in this project constitutes financial advice, investment advice, trading advice or any other kind of advice.
   - Do not make investment decisions based solely on this software.

2. **No Warranty**:
   - This software is provided "as is" without any warranties of any kind.
   - We make no guarantees about accuracy, reliability, or suitability for any purpose.

3. **Risk Warning**:
   - Trading and investing in financial markets involves substantial risk of loss.
   - Past performance is not indicative of future results.
   - Users are solely responsible for their investment decisions.

## Features

### Phase 1 (Current)
- Fetch stock fundamentals and market data
- Analyze news sentiment
- Generate research reports with clear source citations
- Support for custom watchlists
- All outputs framed explicitly as "research only"

### Future Phases
- Portfolio simulation and scenario analysis
- Broker API integrations (read-only)
- Advanced analytics and reporting

## Technology Stack

- Python 3.11+
- PostgreSQL 16
- SQLAlchemy
- Pandas/NumPy
- Docker
- n8n (workflow automation)

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11 or higher
- PostgreSQL 16

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AuroraCapitalAI.git
   cd AuroraCapitalAI
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start PostgreSQL:
   ```bash
   docker compose up -d
   ```

5. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Project Structure

```
AuroraCapitalAI/
├── aurora/              # Main package
│   ├── agents/         # AI agents
│   ├── models/        # Database models
│   └── utils/         # Utilities
├── data/              # Data storage
├── docs/              # Documentation
├── scripts/           # Helper scripts
├── sql/              # Database migrations
└── tests/            # Test suite
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License with additional restrictions - see [LICENSE](LICENSE) file.

## Acknowledgments

- Built with OpenAI's GPT models
- Powered by various open-source libraries and tools
- Market data provided by [list your data sources]
