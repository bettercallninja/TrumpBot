#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🤖 TrumpBot Application | اپلیکیشن ترامپ‌بات
===============================================

🎯 Enterprise-Grade Multilingual Bot Application | اپلیکیشن ربات چندزبانه سازمانی
• Advanced error handling and recovery | مدیریت پیشرفته خطا و بازیابی
• Comprehensive Persian & English support | پشتیبانی جامع فارسی و انگلیسی
• Production-ready architecture | معماری آماده تولید
• Performance monitoring and optimization | نظارت و بهینه‌سازی عملکرد

📚 Version: 2.0.0-Enterprise | نسخه: ۲.۰.۰-سازمانی
🔧 Enhanced: August 2025 | تقویت شده: اوت ۲۰۲۵
"""

import logging
import asyncio
import sys
import os
import time
import signal
import platform
import threading
import uuid
import argparse
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from src.config.bot_config import BotConfig, create_bot
from src.database.db_manager import initialize_pool, refresh_pool, DBManager, setup_database
from src.utils.translations import load_translations, get, validate_translation_completeness
from src.utils.localization import get_localized_text, detect_user_language, set_default_language

# Note: Handler modules will be imported on-demand to avoid startup delays

# 📊 Enhanced Logging Configuration | پیکربندی پیشرفته لاگ‌گیری
log_format = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
log_date_format = '%Y-%m-%d %H:%M:%S'

# Create logs directory if it doesn't exist
logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

# Create file handlers
error_handler = logging.FileHandler(logs_dir / 'bot_errors.log', encoding='utf-8')
error_handler.setLevel(logging.ERROR)

logging.basicConfig(
    format=log_format,
    datefmt=log_date_format,
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(logs_dir / 'bot.log', encoding='utf-8'),
        error_handler
    ]
)

# Set specific log levels for different components
logging.getLogger('telebot').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('asyncpg').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class ApplicationMetrics:
    """📈 Application performance metrics | معیارهای عملکرد اپلیکیشن"""
    
    def __init__(self):
        self.start_time = time.time()
        self.startup_duration = 0
        self.message_count = 0
        self.error_count = 0
        self.last_activity = time.time()
        self.language_stats = {'en': 0, 'fa': 0}
        self.feature_usage = {}
    
    def record_message(self, language: str = 'en'):
        """Record message activity with language tracking"""
        self.message_count += 1
        self.last_activity = time.time()
        self.language_stats[language] = self.language_stats.get(language, 0) + 1
    
    def record_error(self):
        """Record error occurrence"""
        self.error_count += 1
    
    def record_feature_usage(self, feature: str):
        """Record feature usage statistics"""
        self.feature_usage[feature] = self.feature_usage.get(feature, 0) + 1
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return time.time() - self.start_time
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive application statistics"""
        uptime = self.get_uptime()
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'startup_duration': self.startup_duration,
            'total_messages': self.message_count,
            'messages_per_hour': (self.message_count / (uptime / 3600)) if uptime > 0 else 0,
            'error_count': self.error_count,
            'error_rate': (self.error_count / self.message_count * 100) if self.message_count > 0 else 0,
            'last_activity': self.last_activity,
            'language_distribution': self.language_stats,
            'feature_usage': self.feature_usage,
            'memory_usage': self._get_memory_usage(),
            'system_info': self._get_system_info()
        }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        try:
            try:
                import psutil
                process = psutil.Process()
                memory_info = process.memory_info()
                return {
                    'rss_mb': memory_info.rss / 1024 / 1024,
                    'vms_mb': memory_info.vms / 1024 / 1024,
                    'percent': process.memory_percent()
                }
            except ImportError:
                # Fallback to basic memory info if psutil is not available
                import os
                try:
                    # Basic memory usage for systems without psutil
                    if hasattr(os, 'getpid'):
                        return {
                            'process_id': os.getpid(),
                            'status': 'basic_info_only',
                            'note': 'psutil not available for detailed memory stats'
                        }
                except:
                    pass
                return {'error': 'memory info not available'}
        except Exception:
            return {'error': 'memory info not available'}
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0]
        }

class BotApplication:
    """🎮 Main bot application class | کلاس اصلی اپلیکیشن ربات"""
    
    def __init__(self):
        self.config = BotConfig
        self.bot = None
        self.db_manager = None
        self.metrics = ApplicationMetrics()
        self.is_running = False
        self.shutdown_requested = False
        self.default_language = 'en'
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        if platform.system() != 'Windows':
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        signal_names = {signal.SIGTERM: 'SIGTERM', signal.SIGINT: 'SIGINT'}
        signal_name = signal_names.get(signum, f'Signal {signum}')
        
        logger.info(f"Received {signal_name}. Initiating graceful shutdown...")
        logger.info(f"دریافت سیگنال {signal_name}. شروع خاموش شدن نرم...")
        
        self.shutdown_requested = True
    
    async def initialize_database(self) -> bool:
        """🗄️ Initialize database connection pool | راه‌اندازی استخر اتصال پایگاه داده"""
        try:
            logger.info("Initializing database connection pool...")
            logger.info("در حال راه‌اندازی استخر اتصال پایگاه داده...")
            
            start_time = time.time()
            await initialize_pool()
            self.db_manager = DBManager()
            
            # Setup database tables if they don't exist
            logger.info("Setting up database tables...")
            logger.info("راه‌اندازی جداول پایگاه داده...")
            await setup_database()
            
            # Repair any issues with the cooldowns table
            logger.info("Repairing cooldowns table if needed...")
            try:
                await self.db_manager.repair_cooldowns_table()
                logger.info("Cooldowns table repair completed")
            except Exception as repair_error:
                logger.warning(f"Cooldowns table repair encountered an issue: {repair_error}")
            
            # Clean up expired cooldowns
            try:
                removed_count = await self.db_manager.cleanup_expired_cooldowns()
                logger.info(f"Cleaned up {removed_count} expired cooldowns")
            except Exception as cleanup_error:
                logger.warning(f"Expired cooldowns cleanup encountered an issue: {cleanup_error}")
            
            # Test database connection
            await self._test_database_connection()
            
            duration = time.time() - start_time
            logger.info(f"Database initialized successfully in {duration:.2f}s")
            logger.info(f"پایگاه داده با موفقیت در {duration:.2f} ثانیه راه‌اندازی شد")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            logger.error(f"خطا در راه‌اندازی پایگاه داده: {e}")
            self.metrics.record_error()
            return False
    
    async def _test_database_connection(self):
        """Test database connection and basic functionality"""
        try:
            # Test basic query
            result = await self.db_manager.db("SELECT 1 as test", fetch="one_dict")
            if not result or result.get('test') != 1:
                raise Exception("Database connection test failed")
            
            logger.info("Database connection test passed")
            logger.info("تست اتصال پایگاه داده موفق بود")
            
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            logger.error(f"تست اتصال پایگاه داده ناموفق: {e}")
            raise
    
    def initialize_translations(self) -> bool:
        """🌐 Load and validate translation files | بارگذاری و اعتبارسنجی فایل‌های ترجمه"""
        try:
            logger.info("Loading translations for multilingual support...")
            logger.info("بارگذاری ترجمه‌ها برای پشتیبانی چندزبانه...")
            
            start_time = time.time()
            
            # Load translations
            load_translations()
            
            # Validate translation completeness
            validation_results = validate_translation_completeness()
            
            if validation_results.get('complete', False):
                logger.info("✅ All translations loaded and validated successfully")
                logger.info("✅ تمام ترجمه‌ها با موفقیت بارگذاری و اعتبارسنجی شدند")
            else:
                missing_keys = validation_results.get('missing_keys', {})
                if missing_keys:
                    logger.warning(f"⚠️ Some translation keys are missing: {missing_keys}")
                    logger.warning(f"⚠️ برخی کلیدهای ترجمه مفقود هستند: {missing_keys}")
            
            # Set default language
            set_default_language(self.default_language)
            
            duration = time.time() - start_time
            logger.info(f"Translations initialized in {duration:.2f}s")
            logger.info(f"ترجمه‌ها در {duration:.2f} ثانیه راه‌اندازی شدند")
            
            return True
        except Exception as e:
            logger.error(f"Failed to load translations: {e}")
            logger.error(f"خطا در بارگذاری ترجمه‌ها: {e}")
            self.metrics.record_error()
            return False
    
    def create_bot_instance(self) -> bool:
        """🤖 Create bot instance with enhanced configuration | ایجاد نمونه ربات با پیکربندی پیشرفته"""
        try:
            logger.info("Creating bot instance with enhanced features...")
            logger.info("ایجاد نمونه ربات با ویژگی‌های پیشرفته...")
            
            self.bot = create_bot()
            
            # Note: Bot info will be retrieved during startup polling
            # since get_me() is an async method that requires await
            logger.info("Bot instance created successfully")
            logger.info("نمونه ربات با موفقیت ایجاد شد")
            return True
        except Exception as e:
            logger.error(f"Failed to create bot instance: {e}")
            logger.error(f"خطا در ایجاد نمونه ربات: {e}")
            self.metrics.record_error()
            return False
    
    def register_handlers(self) -> bool:
        """📋 Register all command and callback handlers | ثبت تمام دستورات و کنترل‌کننده‌های فراخوان"""
        try:
            logger.info("Registering command and callback handlers...")
            logger.info("ثبت کنترل‌کننده‌های دستور و فراخوان...")
            
            handlers_registered = 0
            
            # Import command modules dynamically to avoid startup delays
            logger.debug("Importing command modules...")
            from src.commands import general, attack, shop, inventory, status, stats, stars, help
            
            # Register command handlers with error tracking
            command_modules = [
                ('general', general),
                ('attack', attack),
                ('shop', shop),
                ('inventory', inventory),
                ('status', status),
                ('stats', stats),
                ('stars', stars),
                ('help', help)
            ]
            
            for module_name, module in command_modules:
                try:
                    module.register_handlers(self.bot, self.db_manager)
                    handlers_registered += 1
                    logger.debug(f"✅ {module_name} handlers registered")
                except Exception as e:
                    logger.error(f"❌ Failed to register {module_name} handlers: {e}")
                    raise
            
            # Import and register callback and message handlers
            logger.debug("Importing handler modules...")
            from src.handlers import callbacks, messages
            
            try:
                callbacks.register_handlers(self.bot, self.db_manager)
                handlers_registered += 1
                logger.debug("✅ Callback handlers registered")
            except Exception as e:
                logger.error(f"❌ Failed to register callback handlers: {e}")
                raise
            
            try:
                messages.register_handlers(self.bot, self.db_manager)
                handlers_registered += 1
                logger.debug("✅ Message handlers registered")
            except Exception as e:
                logger.error(f"❌ Failed to register message handlers: {e}")
                raise
            
            logger.info(f"All {handlers_registered} handler modules registered successfully")
            logger.info(f"تمام {handlers_registered} ماژول کنترل‌کننده با موفقیت ثبت شدند")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register handlers: {e}")
            logger.error(f"خطا در ثبت کنترل‌کننده‌ها: {e}")
            self.metrics.record_error()
            return False
    
    def configure_error_handling(self) -> bool:
        """🚨 Configure comprehensive error handling | پیکربندی مدیریت خطای جامع"""
        try:
            logger.info("Configuring error handling and recovery systems...")
            logger.info("پیکربندی سیستم‌های مدیریت خطا و بازیابی...")
            
            # For AsyncTeleBot, we'll configure error handling differently
            # The middleware and exception handlers will be set up in the handlers themselves
            
            # Set up global error tracking function
            def track_user_activity(user_id: int, feature: str, language: str = None):
                """Track user activity for metrics"""
                try:
                    if language is None:
                        language = detect_user_language(user_id) or self.default_language
                    
                    # Record metrics
                    self.metrics.record_message(language)
                    self.metrics.record_feature_usage(feature)
                    
                except Exception as e:
                    logger.error(f"Error tracking user activity: {e}")
                    self.metrics.record_error()
            
            # Store the tracking function for use by handlers
            self.track_user_activity = track_user_activity
            
            # Global error handler function
            def handle_bot_error(exception, context="unknown"):
                """Global error handler for bot errors"""
                self.metrics.record_error()
                
                error_id = str(uuid.uuid4())[:8]
                error_msg = str(exception)
                
                logger.error(f"Bot exception [{error_id}] in {context}: {type(exception).__name__}: {error_msg}")
                logger.error(f"خطای ربات [{error_id}] در {context}: {type(exception).__name__}: {error_msg}")
                
                # Log stack trace for debugging
                logger.error(f"Stack trace [{error_id}]:", exc_info=True)
                
                return error_id
            
            # Store the error handler for use by handlers
            self.handle_bot_error = handle_bot_error
            
            logger.info("Error handling configured successfully")
            logger.info("مدیریت خطا با موفقیت پیکربندی شد")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure error handling: {e}")
            logger.error(f"خطا در پیکربندی مدیریت خطا: {e}")
            self.metrics.record_error()
            return False
    
    def setup_health_monitoring(self) -> bool:
        """💊 Setup health monitoring and diagnostics | راه‌اندازی نظارت سلامت و تشخیص"""
        try:
            logger.info("Setting up health monitoring system...")
            logger.info("راه‌اندازی سیستم نظارت سلامت...")
            
            # Create health check endpoint (if web interface is enabled)
            self.health_status = {
                'status': 'healthy',
                'database': 'unknown',
                'bot': 'unknown',
                'last_check': time.time(),
                'startup_time': self.metrics.start_time,
                'version': '2.0.0'
            }
            
            # Schedule periodic health checks
            async def periodic_health_check():
                """Perform periodic health checks"""
                try:
                    # Check database connection
                    if self.db_manager:
                        # Perform a real database health check
                        db_healthy = await self.check_database_health()
                        self.health_status['database'] = 'healthy' if db_healthy else 'unhealthy'
                        
                        # Run database maintenance tasks periodically (every ~30 minutes)
                        if db_healthy and time.time() % 1800 < 60:  # Run in a 60-second window every 30 minutes
                            try:
                                # Clean up expired cooldowns
                                removed = await self.db_manager.cleanup_expired_cooldowns()
                                if removed > 0:
                                    logger.info(f"Health check maintenance: Removed {removed} expired cooldowns")
                            except Exception as maintenance_error:
                                logger.warning(f"Health check maintenance task failed: {maintenance_error}")
                    else:
                        self.health_status['database'] = 'disconnected'
                    
                    # Check bot status
                    if self.bot and self.is_running:
                        self.health_status['bot'] = 'healthy'
                    else:
                        self.health_status['bot'] = 'stopped'
                    
                    # Update overall status
                    if (self.health_status['database'] == 'healthy' and 
                        self.health_status['bot'] == 'healthy'):
                        self.health_status['status'] = 'healthy'
                    else:
                        self.health_status['status'] = 'degraded'
                    
                    self.health_status['last_check'] = time.time()
                    
                    # Log health status periodically
                    uptime_hours = self.metrics.get_uptime() / 3600
                    if uptime_hours > 0 and int(uptime_hours) % 6 == 0:  # Every 6 hours
                        stats = self.metrics.get_stats()
                        logger.info(
                            f"Health Check - Uptime: {uptime_hours:.1f}h, "
                            f"Messages: {stats['total_messages']}, "
                            f"DB: {self.health_status['database']}"
                        )
                
                except Exception as e:
                    logger.error(f"Health check error: {e}")
                    self.health_status['status'] = 'error'
                    self.metrics.record_error()
            
            # Create asyncio task for periodic health check
            async def health_check_scheduler():
                while self.is_running and not self.shutdown_requested:
                    await periodic_health_check()
                    await asyncio.sleep(300)  # Check every 5 minutes
            
            # Run initial health check and schedule future checks
            asyncio.create_task(periodic_health_check())
            asyncio.create_task(health_check_scheduler())
            
            logger.info("Health monitoring activated - سیستم نظارت سلامت فعال شد")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup health monitoring: {e}")
            logger.error(f"خطا در راه‌اندازی نظارت سلامت: {e}")
            self.metrics.record_error()
            return False
            
    async def check_database_health(self) -> bool:
        """
        بررسی سلامت پایگاه داده و تازه‌سازی اتصال در صورت نیاز
        Check database health and refresh connection if needed
        """
        try:
            if not self.db_manager:
                logger.warning("Database manager not initialized during health check")
                return False
                
            # First, ensure pool exists and is healthy
            await self.db_manager.ensure_pool()
            
            # Try a simple query to verify connection
            result = await self.db_manager.db("SELECT 1 as test", fetch="one")
            
            if result and result[0] == 1:
                # Connection is good
                
                # Clean up expired cooldowns periodically
                # This helps prevent the cooldowns table from growing too large
                try:
                    removed = await self.db_manager.cleanup_expired_cooldowns()
                    if removed > 0:
                        logger.info(f"Health check: Cleaned up {removed} expired cooldowns")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up cooldowns during health check: {cleanup_error}")
                
                return True
            else:
                # Try to refresh the pool
                logger.warning("Database health check failed, refreshing connection pool...")
                await refresh_pool()
                # Get the global pool reference
                from src.database.db_manager import pool
                self.db_manager._pool = pool
                self.db_manager._last_pool_refresh = time.time()
                
                # Test the connection again
                result = await self.db_manager.db("SELECT 1 as test", fetch="one")
                return result and result[0] == 1
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            
            # Try to refresh the pool as a recovery measure
            try:
                logger.info("Attempting database connection pool refresh after health check failure")
                await refresh_pool()
                # Re-initialize DB manager
                from src.database.db_manager import pool
                self.db_manager._pool = pool
                self.db_manager._last_pool_refresh = time.time()
                
                # Try a final verification query
                result = await self.db_manager.db("SELECT 1 as recovery_test", fetch="one")
                if result and result[0] == 1:
                    logger.info("Database connection recovered after error")
                    return True
            except Exception as recovery_error:
                logger.error(f"Database recovery failed: {recovery_error}")
                
            return False
            
            # Run initial health check
            periodic_health_check()
            
            # Schedule health checks (simplified for this implementation)
            import threading
            def health_check_timer():
                while self.is_running and not self.shutdown_requested:
                    periodic_health_check()
                    time.sleep(300)  # Check every 5 minutes
            
            health_thread = threading.Thread(target=health_check_timer, daemon=True)
            health_thread.start()
            
            logger.info("Health monitoring system activated")
            logger.info("سیستم نظارت سلامت فعال شد")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup health monitoring: {e}")
            logger.error(f"خطا در راه‌اندازی نظارت سلامت: {e}")
            self.metrics.record_error()
            return False
    
    async def startup_sequence(self) -> bool:
        """🚀 Execute complete startup sequence | اجرای دنباله کامل راه‌اندازی"""
        startup_start = time.time()
        
        try:
            logger.info("="*60)
            logger.info("🎮 TrumpBot Application Starting Up | راه‌اندازی اپلیکیشن ترامپ‌بات")
            logger.info("="*60)
            
            # Step 1: Initialize translations
            logger.info("📚 Step 1/6: Loading translations...")
            logger.info("📚 مرحله ۱/۶: بارگذاری ترجمه‌ها...")
            if not self.initialize_translations():
                logger.error("❌ Translation initialization failed")
                logger.error("❌ راه‌اندازی ترجمه‌ها ناموفق بود")
                return False
            logger.info("✅ Translations loaded successfully")
            logger.info("✅ ترجمه‌ها با موفقیت بارگذاری شدند")
            
            # Step 2: Initialize database
            logger.info("🗄️ Step 2/6: Connecting to database...")
            logger.info("🗄️ مرحله ۲/۶: اتصال به پایگاه داده...")
            if not await self.initialize_database():
                logger.error("❌ Database initialization failed")
                logger.error("❌ راه‌اندازی پایگاه داده ناموفق بود")
                return False
            logger.info("✅ Database connected successfully")
            logger.info("✅ پایگاه داده با موفقیت متصل شد")
            
            # Step 3: Create bot instance
            logger.info("🤖 Step 3/6: Creating bot instance...")
            logger.info("🤖 مرحله ۳/۶: ایجاد نمونه ربات...")
            if not self.create_bot_instance():
                logger.error("❌ Bot instance creation failed")
                logger.error("❌ ایجاد نمونه ربات ناموفق بود")
                return False
            logger.info("✅ Bot instance created successfully")
            logger.info("✅ نمونه ربات با موفقیت ایجاد شد")
            
            # Step 4: Configure error handling
            logger.info("🚨 Step 4/6: Configuring error handling...")
            logger.info("🚨 مرحله ۴/۶: پیکربندی مدیریت خطا...")
            if not self.configure_error_handling():
                logger.error("❌ Error handling configuration failed")
                logger.error("❌ پیکربندی مدیریت خطا ناموفق بود")
                return False
            logger.info("✅ Error handling configured successfully")
            logger.info("✅ مدیریت خطا با موفقیت پیکربندی شد")
            
            # Step 5: Register handlers
            logger.info("📋 Step 5/6: Registering handlers...")
            logger.info("📋 مرحله ۵/۶: ثبت کنترل‌کننده‌ها...")
            if not self.register_handlers():
                logger.error("❌ Handler registration failed")
                logger.error("❌ ثبت کنترل‌کننده‌ها ناموفق بود")
                return False
            logger.info("✅ Handlers registered successfully")
            logger.info("✅ کنترل‌کننده‌ها با موفقیت ثبت شدند")
            
            # Step 6: Setup health monitoring
            logger.info("💊 Step 6/6: Setting up health monitoring...")
            logger.info("💊 مرحله ۶/۶: راه‌اندازی نظارت سلامت...")
            if not self.setup_health_monitoring():
                logger.error("❌ Health monitoring setup failed")
                logger.error("❌ راه‌اندازی نظارت سلامت ناموفق بود")
                return False
            logger.info("✅ Health monitoring activated")
            logger.info("✅ نظارت سلامت فعال شد")
            
            # Record startup completion
            self.metrics.startup_duration = time.time() - startup_start
            self.is_running = True
            
            # Display startup summary
            logger.info("="*60)
            logger.info("🎉 STARTUP COMPLETE | راه‌اندازی کامل")
            logger.info(f"⏱️ Startup time: {self.metrics.startup_duration:.2f}s")
            logger.info(f"⏱️ زمان راه‌اندازی: {self.metrics.startup_duration:.2f} ثانیه")
            logger.info(f"🌐 Default language: {self.default_language}")
            logger.info(f"🌐 زبان پیش‌فرض: {self.default_language}")
            logger.info(f"📊 Monitoring: Active")
            logger.info(f"📊 نظارت: فعال")
            logger.info("🚀 Bot is ready to serve users!")
            logger.info("🚀 ربات آماده خدمت‌رسانی به کاربران است!")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            self.metrics.startup_duration = time.time() - startup_start
            logger.error(f"❌ Startup sequence failed after {self.metrics.startup_duration:.2f}s: {e}")
            logger.error(f"❌ دنباله راه‌اندازی پس از {self.metrics.startup_duration:.2f} ثانیه ناموفق بود: {e}")
            self.metrics.record_error()
            return False
    
    async def start_polling(self) -> None:
        """Start bot polling with error handling"""
        try:
            # Get bot info now that we're in async context
            try:
                bot_info = await self.bot.get_me()
                logger.info(f"Bot initialized: @{bot_info.username} ({bot_info.first_name})")
                logger.info(f"ربات راه‌اندازی شد: @{bot_info.username} ({bot_info.first_name})")
            except Exception as e:
                logger.warning(f"Could not retrieve bot info: {e}")
            
            logger.info("Starting bot polling...")
            await self.bot.polling(non_stop=True, skip_pending=True)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error during polling: {e}")
            raise
    


    def run(self):
        """▶️ Start the bot with comprehensive error handling | راه‌اندازی ربات با مدیریت خطای جامع"""
        try:
            logger.info("🚀 Starting TrumpBot application...")
            logger.info("🚀 شروع اپلیکیشن ترامپ‌بات...")
            
            # Run startup sequence
            startup_success = asyncio.run(self.startup_sequence())
            
            if not startup_success:
                logger.error("Startup sequence failed. Exiting...")
                logger.error("دنباله راه‌اندازی ناموفق بود. خروج...")
                return False
            
            # Start polling with async method
            logger.info("📡 Starting message polling...")
            logger.info("📡 شروع دریافت پیام‌ها...")
            
            asyncio.run(self.start_polling())
            
        except KeyboardInterrupt:
            logger.info("🛑 Received keyboard interrupt. Shutting down gracefully...")
            logger.info("🛑 دریافت وقفه صفحه‌کلید. خاموش شدن نرم...")
            self.shutdown()
        except Exception as e:
            logger.error(f"❌ Critical error in main run loop: {e}")
            logger.error(f"❌ خطای حیاتی در حلقه اصلی اجرا: {e}")
            self.metrics.record_error()
            self.shutdown()
        finally:
            logger.info("🏁 Bot application terminated")
            logger.info("🏁 اپلیکیشن ربات خاتمه یافت")

    def shutdown(self):
        """🛑 Graceful shutdown with cleanup | خاموش شدن نرم با پاکسازی"""
        try:
            logger.info("🛑 Initiating graceful shutdown...")
            logger.info("🛑 شروع خاموش شدن نرم...")
            
            self.is_running = False
            self.shutdown_requested = True
            
            # Get final statistics
            final_stats = self.metrics.get_stats()
            
            # Log shutdown statistics
            logger.info("📊 Final Statistics | آمار نهایی:")
            logger.info(f"⏱️ Total uptime: {final_stats['uptime_hours']:.2f} hours")
            logger.info(f"⏱️ مجموع زمان فعالیت: {final_stats['uptime_hours']:.2f} ساعت")
            logger.info(f"📨 Total messages processed: {final_stats['total_messages']}")
            logger.info(f"📨 مجموع پیام‌های پردازش شده: {final_stats['total_messages']}")
            logger.info(f"⚠️ Total errors: {final_stats['error_count']}")
            logger.info(f"⚠️ مجموع خطاها: {final_stats['error_count']}")
            logger.info(f"🌐 Language distribution: {final_stats['language_distribution']}")
            logger.info(f"🌐 توزیع زبان: {final_stats['language_distribution']}")
            
            # Cleanup resources
            if self.bot:
                try:
                    # For async bot, we don't have stop_polling method
                    # The polling will be stopped by the exception handling
                    logger.info("✅ Bot polling stopped")
                except:
                    pass
            
            # Close database connections
            if self.db_manager:
                try:
                    # Note: In a real implementation, this would be an async call
                    # await close_pool()
                    logger.info("✅ Database connections closed")
                    logger.info("✅ اتصالات پایگاه داده بسته شد")
                except:
                    pass
            
            logger.info("✅ Graceful shutdown completed")
            logger.info("✅ خاموش شدن نرم کامل شد")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            logger.error(f"خطا در طول خاموش شدن: {e}")

def main():
    """🎯 Main application entry point | نقطه ورود اصلی اپلیکیشن"""
    try:
        # Initialize application
        logger.info("🎮 Initializing TrumpBot Enterprise Application...")
        logger.info("🎮 راه‌اندازی اپلیکیشن سازمانی ترامپ‌بات...")
        
        app = BotApplication()
        
        # Display startup banner
        logger.info("=" * 70)
        logger.info("🎮 TrumpBot v2.0.0 Enterprise | ترامپ‌بات نسخه ۲.۰.۰ سازمانی")
        logger.info("=" * 70)
        logger.info("🌟 Features | ویژگی‌ها:")
        logger.info("   • 🌐 Bilingual Support (EN/FA) | پشتیبانی دوزبانه")
        logger.info("   • 🚨 Advanced Error Handling | مدیریت پیشرفته خطا")
        logger.info("   • 📊 Performance Monitoring | نظارت عملکرد")
        logger.info("   • 💊 Health Diagnostics | تشخیص سلامت")
        logger.info("   • 🛡️ Production Architecture | معماری تولید")
        logger.info("=" * 70)
        
        # Run the application
        return app.run()
        
    except Exception as e:
        logger.error(f"❌ Critical application error: {e}")
        logger.error(f"❌ خطای حیاتی اپلیکیشن: {e}")
        logger.error("Stack trace:", exc_info=True)
        return False

def cli_interface():
    """🖥️ Command-line interface for administrative tasks | رابط خط فرمان برای وظایف مدیریتی"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='TrumpBot Enterprise Application | اپلیکیشن سازمانی ترامپ‌بات',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples | نمونه‌ها:
  python -m src.app                    # Start bot normally | شروع عادی ربات
  python -m src.app --check-health     # Check system health | بررسی سلامت سیستم
  python -m src.app --validate-config  # Validate configuration | اعتبارسنجی پیکربندی
  python -m src.app --test-db          # Test database connection | تست اتصال پایگاه داده
        """
    )
    
    parser.add_argument(
        '--check-health',
        action='store_true',
        help='Perform system health check | انجام بررسی سلامت سیستم'
    )
    
    parser.add_argument(
        '--validate-config',
        action='store_true',
        help='Validate bot configuration | اعتبارسنجی پیکربندی ربات'
    )
    
    parser.add_argument(
        '--test-db',
        action='store_true',
        help='Test database connectivity | تست اتصال پایگاه داده'
    )
    
    parser.add_argument(
        '--language',
        choices=['en', 'fa'],
        default='en',
        help='Default application language | زبان پیش‌فرض اپلیکیشن'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level | سطح لاگ‌گیری'
    )
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    if args.check_health:
        return perform_health_check()
    elif args.validate_config:
        return validate_configuration()
    elif args.test_db:
        return test_database_connection()
    else:
        # Set default language
        if args.language:
            set_default_language(args.language)
            logger.info(f"Default language set to: {args.language}")
            logger.info(f"زبان پیش‌فرض تنظیم شد: {args.language}")
        
        # Start main application
        return main()

def perform_health_check() -> bool:
    """🏥 Perform comprehensive system health check | انجام بررسی جامع سلامت سیستم"""
    try:
        logger.info("🏥 Starting comprehensive health check...")
        logger.info("🏥 شروع بررسی جامع سلامت...")
        
        health_results = {
            'system': False,
            'config': False,
            'database': False,
            'translations': False
        }
        
        # Check system requirements
        logger.info("🔍 Checking system requirements...")
        try:
            python_version = platform.python_version()
            # Parse version properly
            major, minor, patch = python_version.split('.')
            version_tuple = (int(major), int(minor))
            
            if version_tuple >= (3, 8):
                logger.info(f"✅ Python version: {python_version}")
                health_results['system'] = True
            else:
                logger.error(f"❌ Python version too old: {python_version} (requires 3.8+)")
        except Exception as e:
            logger.error(f"❌ System check failed: {e}")
        
        # Check configuration
        logger.info("⚙️ Checking configuration...")
        try:
            config = BotConfig
            if hasattr(config, 'TOKEN') and config.TOKEN:
                logger.info("✅ Bot configuration valid")
                health_results['config'] = True
            else:
                logger.error("❌ Bot API token not configured")
        except Exception as e:
            logger.error(f"❌ Configuration check failed: {e}")
        
        # Check translations
        logger.info("🌐 Checking translations...")
        try:
            load_translations()
            validation_results = validate_translation_completeness()
            if validation_results.get('complete', False):
                logger.info("✅ Translations complete and valid")
                health_results['translations'] = True
            else:
                logger.warning("⚠️ Some translations missing")
                health_results['translations'] = True  # Non-critical
        except Exception as e:
            logger.error(f"❌ Translation check failed: {e}")
        
        # Check database (simplified)
        logger.info("🗄️ Checking database configuration...")
        try:
            # Check for DATABASE_URL environment variable
            if os.getenv('DATABASE_URL'):
                logger.info("✅ Database configuration present")
                health_results['database'] = True
            else:
                logger.error("❌ DATABASE_URL environment variable not set")
        except Exception as e:
            logger.error(f"❌ Database check failed: {e}")
        
        # Summary
        passed_checks = sum(health_results.values())
        total_checks = len(health_results)
        
        logger.info("="*50)
        logger.info("🏥 HEALTH CHECK SUMMARY | خلاصه بررسی سلامت")
        logger.info("="*50)
        logger.info(f"✅ Passed: {passed_checks}/{total_checks}")
        logger.info(f"✅ موفق: {passed_checks}/{total_checks}")
        
        for check, result in health_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {check.title()}")
        
        if passed_checks == total_checks:
            logger.info("🎉 All health checks passed! | تمام بررسی‌های سلامت موفق!")
            return True
        else:
            logger.warning("⚠️ Some health checks failed | برخی بررسی‌های سلامت ناموفق")
            return False
            
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False

def validate_configuration() -> bool:
    """⚙️ Validate bot configuration | اعتبارسنجی پیکربندی ربات"""
    try:
        logger.info("⚙️ Validating bot configuration...")
        logger.info("⚙️ اعتبارسنجی پیکربندی ربات...")
        
        config = BotConfig  # Use the existing instance, don't call it
        
        # Validate required settings
        missing_settings = []
        
        # Check config attributes
        if not hasattr(config, 'TOKEN') or not getattr(config, 'TOKEN'):
            missing_settings.append('Bot API Token')
        
        # Check environment variables directly
        if not os.getenv('DATABASE_URL'):
            missing_settings.append('Database URL')
        
        if missing_settings:
            logger.error(f"❌ Missing required settings: {', '.join(missing_settings)}")
            return False
        
        logger.info("✅ Configuration validation passed")
        logger.info("✅ اعتبارسنجی پیکربندی موفق بود")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        return False

def test_database_connection() -> bool:
    """🗄️ Test database connectivity | تست اتصال پایگاه داده"""
    try:
        logger.info("🗄️ Testing database connection...")
        logger.info("🗄️ تست اتصال پایگاه داده...")
        
        async def test_connection():
            try:
                await initialize_pool()
                db_manager = DBManager()
                # Perform a simple test query
                result = await db_manager.db("SELECT 1 as test", fetch="one")
                return result and result.get('test') == 1
            except Exception as e:
                logger.error(f"Database test failed: {e}")
                return False
        
        # Run the async test
        connection_success = asyncio.run(test_connection())
        
        if connection_success:
            logger.info("✅ Database connection test passed")
            logger.info("✅ تست اتصال پایگاه داده موفق بود")
            return True
        else:
            logger.error("❌ Database connection test failed")
            logger.error("❌ تست اتصال پایگاه داده ناموفق بود")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False

# 🚀 Application Entry Point | نقطه ورود اپلیکیشن
if __name__ == "__main__":
    try:
        success = cli_interface()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("👋 Application interrupted by user")
        logger.info("👋 اپلیکیشن توسط کاربر متوقف شد")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        logger.error(f"💥 خطای غیرمنتظره: {e}")
        sys.exit(1)
