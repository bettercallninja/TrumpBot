# TrumpBot - Advanced Telegram Battle Bot

A sophisticated Telegram bot for group-based PvP missile combat with modern Python architecture, comprehensive error handling, and bilingual support.

## 🚀 Features

### Core Gameplay
- **PvP Combat System**: Reply-based attacks with sophisticated damage calculations
- **Weapon Arsenal**: Multiple weapon types with varying damage and effects
- **Defense Systems**: Shields and intercept systems with configurable effectiveness
- **Level-based Mechanics**: Dynamic damage based on player levels and experience
- **Real-time Status**: HP tracking, active defenses, and cooldown management

### Premium Features
- **Telegram Stars Integration**: Premium items purchasable with TG Stars
- **Medal Economy**: Activity-based reward system with balanced progression
- **Inventory Management**: Comprehensive item storage and usage tracking
- **Daily Bonuses**: Regular rewards to maintain engagement

### Technical Excellence
- **Bilingual Support**: Complete FA/EN localization with user preferences
- **Async Architecture**: Full async/await implementation for optimal performance
- **Connection Pooling**: PostgreSQL with psycopg-pool for efficient database operations
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Error Handling**: Robust exception handling with logging and user feedback
- **Modular Design**: Clean separation of concerns with organized modules

### Recent Enhancements
- **Improved Weapon Selection**: Select weapons with `/attack` command without reply
- **Enhanced Defense System**: New `/shield` command for quick shield activation
- **Cross-Linked Features**: Inventory and Status screens now link to each other
- **Enhanced Stats System**: Fixed stats buttons with new weapon stats and trends views
- **Comprehensive Help**: Updated help system with clear instructions for all features

## 🏗️ Architecture

### Modern Code Structure
```
TrumpBot/
├── main.py                 # Application entry point
├── src/                    # Main package
│   ├── app.py             # Application bootstrap with error handling
│   ├── commands/          # Command handlers (modular design)
│   │   ├── attack.py      # Combat system with AttackManager class
│   │   ├── general.py     # Basic commands with enhanced error handling
│   │   ├── status.py      # Status management with StatusManager class
│   │   └── ...
│   ├── config/            # Configuration management
│   │   ├── bot_config.py  # Centralized BotConfig class
│   │   └── items.py       # Item system with enums and utilities
│   ├── database/          # Database layer
│   │   └── db_manager.py  # Modern DBManager with connection pooling
│   ├── handlers/          # Event handlers
│   ├── utils/             # Utilities and helpers
│   │   ├── helpers.py     # Refactored with manager classes
│   │   └── translations.py # Enhanced with type hints
│   └── __init__.py
├── pyproject.toml         # Modern Python project configuration
└── README.md             # This file
```

### Key Architectural Improvements
- **Class-based Configuration**: `BotConfig` class replacing scattered constants
- **Manager Pattern**: Specialized managers for different game systems
- **Connection Pooling**: Async PostgreSQL pool for optimal database performance
- **Factory Pattern**: `create_bot()` function for clean bot instantiation
- **Dependency Injection**: Clean separation between business logic and dependencies

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.8+** with async/await support
- **PostgreSQL 12+** for reliable data persistence
- **Telegram Bot Token** from @BotFather

### Environment Setup

1. **Clone and Install Dependencies**:
   ```bash
   git clone <repository-url>
   cd TrumpBot
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file with:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   DATABASE_URL=postgresql://username:password@localhost:5432/trumpbot
   
   # Optional configurations
   UNLIMITED_MISSILES=false
   LOG_LEVEL=INFO
   ```

3. **Database Setup**:
   ```bash
   # Create database
   createdb trumpbot
   
   # Tables will be auto-created on first run
   ```

### Running the Bot

**Development Mode**:
```bash
python main.py
```

**Production Mode** (with logging):
```bash
python main.py > bot.log 2>&1 &
```

## 🎮 Game Commands

### Basic Commands
- `/start` - Welcome message and main menu
- `/help` - Comprehensive help system
- `/language` - Switch between English/Persian
- `/status` - Current player status and defenses
- `/shield` - Quickly activate a shield
- `/stats` - View detailed player statistics

### Combat System
- `/attack [user] [weapon]` - Attack another player
- Reply to a message + `/attack` - Quick attack with current weapon
- Use `/attack` without reply to select your weapon first
- Weapon types: `moab`, `f22`, `nuclear`, `mega_nuke`, `stealth_bomber`

### Defense System
- `/shield` - Quick command to activate your shield
- `/status` - View and activate your defense systems
- Defense types: `shield` (blocks attacks), `intercept` (reduces hit chance)

### Economy & Inventory
- `/shop` - Browse and purchase items
- `/inventory` or `/inv` - View and manage owned items
- `/stars` - Telegram Stars premium shop
- `/top` - Leaderboard system
- `/stats` - View your combat statistics

## 🔧 Advanced Configuration

### Bot Configuration Class
```python
from src.config.bot_config import BotConfig

config = BotConfig
# Access to all game constants:
# - DAMAGE_MULTIPLIERS
# - DEFENSE_EFFECTIVENESS  
# - ATTACK_COOLDOWN
# - UNLIMITED_MISSILES
```

### Database Manager
```python
from src.database.db_manager import DBManager

db = DBManager()
# Modern async operations with connection pooling
result = await db.db("SELECT * FROM players WHERE user_id=%s", (user_id,), fetch="one_dict")
```

### Custom Item System
```python
from src.config.items import ITEMS, ItemType, PaymentType

# Define new items with full type safety
# Support for different payment methods and categories
```

## 🔒 Security & Performance

### Database Security
- **Parameterized Queries**: Full protection against SQL injection
- **Connection Pooling**: Efficient resource management
- **Error Isolation**: Database errors don't crash the application

### Rate Limiting & Cooldowns
- **Attack Cooldown**: Configurable delay between attacks
- **Defense Timers**: Time-based defense expiration
- **Activity Tracking**: Automatic activity point calculation

### Error Handling
- **Graceful Degradation**: Errors don't interrupt bot operation
- **User Feedback**: Meaningful error messages in user's language
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## 🌐 Internationalization

### Language Support
- **English (en)**: Complete translation set
- **Persian/Farsi (fa)**: Full localization including RTL considerations
- **Per-user Settings**: Individual language preferences stored in database

### Adding New Languages
1. Add translations to `src/utils/translations.py`
2. Update language selection handlers
3. Test with both LTR and RTL text layouts

## 🚀 Performance Optimizations

### Database Optimizations
- **Connection Pooling**: Reuse connections for better performance
- **Efficient Queries**: Optimized SQL with proper indexing
- **Batch Operations**: Reduced database round-trips

### Memory Management
- **Async Patterns**: Non-blocking operations throughout
- **Resource Cleanup**: Proper connection and resource management
- **Type Hints**: Better memory usage with static analysis

## 🔍 Monitoring & Debugging

### Logging System
- **Structured Logging**: Consistent log format with timestamps
- **Error Tracking**: Comprehensive exception logging
- **Performance Metrics**: Database query timing and performance data

### Health Checks
- **Database Connection**: Automatic connection health verification
- **Bot Status**: Regular polling status monitoring
- **Error Recovery**: Automatic reconnection on failures

## 🛡️ Deployment

### Production Checklist
- [ ] Environment variables properly configured
- [ ] Database backup strategy in place
- [ ] Log rotation configured
- [ ] Monitor bot performance metrics
- [ ] Set up error alerting

### Docker Deployment (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 🤝 Contributing

### Code Style
- **Type Hints**: Required for all functions and classes
- **Docstrings**: Comprehensive documentation for all public methods
- **Error Handling**: Proper exception handling with user feedback
- **Testing**: Add tests for new features

### Development Workflow
1. Fork the repository
2. Create feature branch with descriptive name
3. Implement changes with proper error handling
4. Add/update tests and documentation
5. Submit pull request with detailed description

## 📞 Support
- **t.me/@bettercallninja**

### Common Issues
- **Import Errors**: Ensure all `__init__.py` files exist
- **Database Connection**: Verify DATABASE_URL format and credentials
- **Permission Issues**: Check bot admin permissions in target groups

### Getting Help
- Check logs for detailed error information
- Verify environment variable configuration
- Test database connectivity independently
- Review Telegram Bot API documentation

---

**TrumpBot** - Modern Telegram gaming bot with enterprise-grade architecture and comprehensive feature set.
