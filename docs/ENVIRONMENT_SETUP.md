# Environment Configuration Guide

## Overview

This document explains how to configure the TrumpBot project using environment variables. The bot uses a comprehensive `.env` file system to manage all configuration settings.

## Quick Start

1. **Copy the template:**
   ```bash
   cp .env.example .env
   ```

2. **Set required values:**
   - `BOT_TOKEN`: Get from [@BotFather](https://t.me/BotFather)
   - `DATABASE_URL`: PostgreSQL connection string
   - `ADMIN_USER_IDS`: Your Telegram user ID

3. **Start the bot:**
   ```bash
   python main.py
   ```

## Required Configuration

### Telegram Bot Settings
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_USERNAME=@YourBotUsername
BOT_NAME=YourBotName
```

### Database Connection
```env
DATABASE_URL=postgresql://username:password@localhost:5432/trumpbot
```

### Admin Access
```env
ADMIN_USER_IDS=123456789,987654321
SUPER_ADMIN_USER_ID=123456789
```

## Configuration Sections

### 1. Game Mechanics
Controls core gameplay features:
- Attack limits and cooldowns
- Damage calculations
- Defense durations
- Economic settings

### 2. Feature Flags
Toggle specific features:
- `UNLIMITED_MISSILES`: Enable unlimited missile attacks
- `FREE_STARS_ENABLED`: Allow free TG Stars distribution
- `PREMIUM_FEATURES`: Enable premium bot features
- `DEBUG_MODE`: Enable debug logging

### 3. Security Settings
Anti-abuse and security features:
- Rate limiting
- Anti-spam protection
- Input validation
- Admin command restrictions

### 4. Performance Settings
Optimization and caching:
- Database connection pooling
- Query optimization
- Caching configuration
- Async processing

### 5. Localization
Multi-language support:
- Supported languages (English, Persian)
- Default language settings
- RTL language support

## Environment-Specific Configuration

### Development Setup
```env
DEVELOPMENT_MODE=true
DEBUG_MODE=true
LOG_LEVEL=DEBUG
TEST_MODE=true
```

### Production Setup
```env
DEVELOPMENT_MODE=false
DEBUG_MODE=false
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
ANALYTICS_ENABLED=true
```

### Testing Setup
```env
TEST_MODE=true
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/trumpbot_test
DEBUG_MODE=true
```

## Advanced Configuration

### Game Modes
```env
DEFAULT_GAME_MODE=casual
TOURNAMENT_ENABLED=true
TOURNAMENT_REWARD_MULTIPLIER=2.0
```

### Economy System
```env
STARTING_MEDALS=100
STARTING_TG_STARS=5
INFLATION_RATE=0.02
TAX_RATE=0.1
```

### Monitoring and Alerts
```env
HEALTH_CHECK_ENABLED=true
ERROR_RATE_THRESHOLD=0.05
ALERT_CHAT_ID=-1001234567890
```

## Database Configuration

### PostgreSQL Connection
The bot supports PostgreSQL with connection pooling:

```env
DATABASE_URL=postgresql://user:pass@host:port/database

# Or individual settings:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trumpbot
DB_USER=username
DB_PASSWORD=password
```

### Connection Pooling
```env
DB_POOL_MIN_SIZE=1
DB_POOL_MAX_SIZE=15
```

## Logging Configuration

### Basic Logging
```env
LOG_LEVEL=INFO
LOG_FILE=logs/trumpbot.log
```

### Advanced Logging
```env
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
DB_LOG_ENABLED=false
BOT_LOG_ENABLED=true
```

## Security Best Practices

1. **Never commit `.env` files:**
   - Always use `.env.example` for templates
   - Add `.env` to `.gitignore`

2. **Use strong tokens:**
   - Generate secure bot tokens
   - Rotate tokens regularly

3. **Limit admin access:**
   - Set specific admin user IDs
   - Use separate super admin account

4. **Enable security features:**
   ```env
   RATE_LIMIT_ENABLED=true
   ANTI_SPAM_ENABLED=true
   DAMAGE_VALIDATION=true
   ```

## Troubleshooting

### Common Issues

1. **Bot not starting:**
   - Check BOT_TOKEN is valid
   - Verify database connection
   - Check log files for errors

2. **Database connection errors:**
   - Verify DATABASE_URL format
   - Check database server is running
   - Validate credentials

3. **Feature not working:**
   - Check corresponding feature flag
   - Verify admin permissions
   - Review debug logs

### Debug Mode
Enable detailed logging:
```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
BOT_LOG_LEVEL=DEBUG
```

## Configuration Validation

The bot automatically validates configuration on startup:
- Checks required variables
- Validates numeric ranges
- Verifies database connection
- Tests API credentials

## Environment File Hierarchy

1. `.env` - Main configuration (not committed)
2. `.env.example` - Template (committed)
3. Environment variables - Override file settings
4. Default values - Fallback in code

## Migration Guide

### From Basic to Enhanced Config

1. Backup current `.env`
2. Copy new `.env.example` to `.env`
3. Migrate your values
4. Update new settings as needed
5. Test configuration

### Version Updates

When updating bot versions:
1. Check for new environment variables
2. Review deprecated settings
3. Update configuration accordingly
4. Test all features

## Support

For configuration help:
1. Check this documentation
2. Review `.env.example`
3. Check bot logs
4. Consult project documentation

## Examples

### Minimal Production Config
```env
BOT_TOKEN=your_token_here
DATABASE_URL=postgresql://user:pass@host/db
ADMIN_USER_IDS=123456789
DEBUG_MODE=false
RATE_LIMIT_ENABLED=true
```

### Full Development Config
```env
BOT_TOKEN=your_token_here
DATABASE_URL=postgresql://user:pass@localhost/trumpbot_dev
ADMIN_USER_IDS=123456789
DEBUG_MODE=true
DEVELOPMENT_MODE=true
LOG_LEVEL=DEBUG
TEST_MODE=true
UNLIMITED_MISSILES=true
FREE_STARS_ENABLED=true
```

### High-Performance Production
```env
BOT_TOKEN=your_token_here
DATABASE_URL=postgresql://user:pass@host/db
ADMIN_USER_IDS=123456789
CACHE_ENABLED=true
DB_POOL_MAX_SIZE=50
QUERY_OPTIMIZATION=true
BATCH_PROCESSING=true
ANALYTICS_ENABLED=true
MONITORING_WEBHOOK_URL=https://your-monitoring.com/webhook
```
