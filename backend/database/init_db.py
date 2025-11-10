"""
Database initialization script
Run this to create all tables and verify the database setup
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.database.schema import db
from backend.config import config


def init_database():
    """Initialize the database"""
    print("🚀 Initializing KeenAI-Quant Database...")
    print(f"📁 Database path: {config.database['path']}")
    
    # Create data directory if it doesn't exist
    db_path = Path(config.database['path'])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    db.init_db()
    
    print("\n✅ Database initialization complete!")
    print("\n📊 Available tables:")
    print("  - historical_candles: OHLCV data storage")
    print("  - trades: Trade execution records")
    print("  - ai_decisions: AI agent decision logs")
    print("  - agent_performance: AI agent metrics")
    print("  - system_logs: System event logs")
    print("  - strategy_performance: Strategy metrics")
    print("  - risk_events: Risk management events")
    print("  - backtest_results: Backtest execution results")
    
    return True


if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
