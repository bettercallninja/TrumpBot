#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🤖 TrumpBot - Enterprise Multilingual Telegram Bot | ترامپ‌بات - ربات تلگرام چندزبانه سازمانی
=============================================================================================================

🎮 A sophisticated Telegram bot for missile battle games in groups | ربات پیشرفته تلگرام برای بازی‌های نبرد موشکی در گروه‌ها

🌟 Features | ویژگی‌ها:
• 🔥 PvP battles inside groups (reply/mention to attack) | نبردهای PvP درون گروه‌ها (پاسخ/منشن برای حمله)
• 🌐 Complete bilingual FA/EN with per-user language | دوزبانه کامل فارسی/انگلیسی با زبان هر کاربر
• 🎯 Enhanced UX: inline menus, counter buttons, short commands | UX بهبود یافته: منوهای درون‌خطی، دکمه‌های شمارنده، دستورات کوتاه
• 😄 Trump-themed humor and messages | طنز و پیام‌های با موضوع ترامپ
• 🛡️ Advanced defense systems: Shield (block) & Intercept (reduce hit chance) | سیستم‌های دفاعی پیشرفته: سپر (مسدود) و رهگیری (کاهش شانس اصابت)
• ⭐ Stars Shop (XTR): Aegis Shield, Patriot Boost, MOAB Heavy Bomb | فروشگاه ستاره (XTR): سپر ایجیس، تقویت پاتریوت، بمب سنگین MOAB
• 🏅 Medals economy with daily bonus system | اقتصاد مدال با سیستم پاداش روزانه
• 🎒 Advanced inventory management + auto-use MOAB | مدیریت پیشرفته موجودی + استفاده خودکار MOAB
• 🏆 Comprehensive leaderboard /top, Detailed inventory /inv | جدول امتیازات جامع /top، موجودی تفصیلی /inv
• 🗄️ Production-ready PostgreSQL storage | ذخیره‌سازی PostgreSQL آماده تولید

📚 Version: 2.0.0-Enterprise | نسخه: ۲.۰.۰-سازمانی
🔧 Enhanced: August 2025 | تقویت شده: اوت ۲۰۲۵
🏗️ Architecture: Enterprise-grade multilingual bot | معماری: ربات چندزبانه سازمانی
"""

import os
import sys
import logging
import platform
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows event loop policy early for psycopg compatibility
if platform.system() == 'Windows':
    import asyncio
    try:
        # Set Windows-compatible event loop policy for async database operations
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except (AttributeError, RuntimeError):
        pass

# 🔧 Environment Setup | راه‌اندازی محیط
# Load environment variables from .env file | بارگذاری متغیرهای محیط از فایل .env
load_dotenv()

# 📊 Setup basic logging | راه‌اندازی لاگ‌گیری اولیه
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """
    🚀 Main entry point for TrumpBot application | نقطه ورود اصلی برای اپلیکیشن ترامپ‌بات
    
    This function serves as the primary entry point that delegates to the main
    application in the src package for better organization and maintainability.
    
    این تابع به عنوان نقطه ورود اصلی که به اپلیکیشن اصلی در پکیج src 
    واگذار می‌کند برای سازماندهی و نگهداری بهتر عمل می‌کند.
    """
    try:
        # Display startup banner | نمایش بنر راه‌اندازی
        logger.info("="*80)
        logger.info("🤖 TrumpBot v2.0.0 Enterprise Starting Up | ترامپ‌بات نسخه ۲.۰.۰ سازمانی در حال راه‌اندازی")
        logger.info("="*80)
        logger.info("🎮 Multilingual Telegram Bot | ربات تلگرام چندزبانه")
        logger.info("🌟 Advanced gaming, economy, and social features | ویژگی‌های پیشرفته بازی، اقتصادی و اجتماعی")
        logger.info("🔧 Enterprise-grade architecture | معماری سازمانی")
        logger.info("="*80)
        
        # Validate environment | اعتبارسنجی محیط
        logger.info("🔍 Validating environment and dependencies...")
        logger.info("🔍 اعتبارسنجی محیط و وابستگی‌ها...")
        
        # Check Python version | بررسی نسخه پایتون
        python_version = sys.version_info
        if python_version < (3, 8):
            logger.error(f"❌ Python 3.8+ required. Current: {python_version.major}.{python_version.minor}")
            logger.error(f"❌ پایتون ۳.۸+ مورد نیاز است. فعلی: {python_version.major}.{python_version.minor}")
            sys.exit(1)
        
        logger.info(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        logger.info(f"✅ نسخه پایتون: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check required environment variables | بررسی متغیرهای محیط ضروری
        required_env_vars = ['BOT_TOKEN', 'DATABASE_URL']
        missing_vars = []
        
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            logger.error(f"❌ متغیرهای محیط ضروری مفقود: {', '.join(missing_vars)}")
            logger.error("💡 Please check your .env file and ensure all required variables are set")
            logger.error("💡 لطفاً فایل .env خود را بررسی کنید و اطمینان حاصل کنید که تمام متغیرهای ضروری تنظیم شده‌اند")
            sys.exit(1)
        
        logger.info("✅ Environment validation passed")
        logger.info("✅ اعتبارسنجی محیط موفق بود")
        
        # Import and run the main application | وارد کردن و اجرای اپلیکیشن اصلی
        logger.info("📦 Loading main application modules...")
        logger.info("📦 بارگذاری ماژول‌های اپلیکیشن اصلی...")
        
        try:
            from src.app import cli_interface
            
            logger.info("✅ Application modules loaded successfully")
            logger.info("✅ ماژول‌های اپلیکیشن با موفقیت بارگذاری شدند")
            
            # Run the main application | اجرای اپلیکیشن اصلی
            logger.info("🚀 Starting TrumpBot application...")
            logger.info("🚀 شروع اپلیکیشن ترامپ‌بات...")
            
            return cli_interface()
            
        except ImportError as e:
            logger.error(f"❌ Failed to import application modules: {e}")
            logger.error(f"❌ خطا در وارد کردن ماژول‌های اپلیکیشن: {e}")
            logger.error("💡 Please ensure the src package is properly installed")
            logger.error("💡 لطفاً اطمینان حاصل کنید که پکیج src به درستی نصب شده است")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Application interrupted by user")
        logger.info("👋 اپلیکیشن توسط کاربر متوقف شد")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Unexpected error during startup: {e}")
        logger.error(f"💥 خطای غیرمنتظره در طول راه‌اندازی: {e}")
        logger.error("🔍 Stack trace:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    """
    🎯 Entry point when script is run directly | نقطه ورود هنگام اجرای مستقیم اسکریپت
    
    This section handles the direct execution of the main.py file and ensures
    proper error handling and exit codes for production deployment.
    
    این بخش اجرای مستقیم فایل main.py را مدیریت می‌کند و اطمینان حاصل 
    می‌کند که مدیریت خطا و کدهای خروج برای استقرار تولید مناسب باشد.
    """
    try:
        # Run the main function and capture success status
        # اجرای تابع اصلی و گرفتن وضعیت موفقیت
        success = main()
        
        # Exit with appropriate code based on success status
        # خروج با کد مناسب بر اساس وضعیت موفقیت
        exit_code = 0 if success else 1
        
        if success:
            logger.info("🎉 TrumpBot application completed successfully")
            logger.info("🎉 اپلیکیشن ترامپ‌بات با موفقیت تکمیل شد")
        else:
            logger.error("❌ TrumpBot application completed with errors")
            logger.error("❌ اپلیکیشن ترامپ‌بات با خطا تکمیل شد")
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("👋 Application interrupted by user during shutdown")
        logger.info("👋 اپلیکیشن توسط کاربر در طول خاموش شدن متوقف شد")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Critical error in main entry point: {e}")
        logger.error(f"💥 خطای حیاتی در نقطه ورود اصلی: {e}")
        logger.error("🔍 Stack trace:", exc_info=True)
        sys.exit(1)
