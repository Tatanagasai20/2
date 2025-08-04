import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json
from config import Config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

class AttendanceBot:
    def __init__(self):
        self.config = Config()
        
    def apply_grace_period(self, timestamp):
        """Apply grace period logic for login times"""
        ist_time = timestamp.astimezone(self.config.TIMEZONE)
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if ist_time.weekday() >= 5:  # Saturday or Sunday
            return timestamp
            
        # Check if login is within grace period (9:00-9:05 AM)
        if (ist_time.hour == self.config.WORK_START_HOUR and 
            ist_time.minute <= self.config.GRACE_PERIOD_MINUTES):
            # Set time to exactly 9:00 AM
            grace_time = ist_time.replace(hour=self.config.WORK_START_HOUR, minute=0, second=0, microsecond=0)
            return grace_time
        
        return timestamp
    
    def is_valid_work_time(self, timestamp):
        """Check if timestamp is within working hours"""
        ist_time = timestamp.astimezone(self.config.TIMEZONE)
        
        # Check if it's a weekday
        if ist_time.weekday() >= 5:  # Saturday or Sunday
            return False
            
        # Check if within working hours (9 AM - 6 PM)
        if (ist_time.hour >= self.config.WORK_START_HOUR and 
            ist_time.hour < self.config.WORK_END_HOUR):
            return True
            
        return False
    
    async def send_to_backend(self, data):
        """Send attendance data to backend API"""
        try:
            response = requests.post(
                f"{self.config.BACKEND_API_URL}/api/attendance",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            logger.error(f"Error sending data to backend: {e}")
            return None
    
    async def handle_login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle employee login"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        timestamp = datetime.now(self.config.TIMEZONE)
        
        # Check if message is from the designated group
        if str(chat_id) != self.config.GROUP_CHAT_ID:
            return
        
        # Check if it's valid work time
        if not self.is_valid_work_time(timestamp):
            await update.message.reply_text(
                f"⚠️ Login is only allowed during working hours (9 AM - 6 PM IST) on weekdays."
            )
            return
        
        # Apply grace period
        adjusted_timestamp = self.apply_grace_period(timestamp)
        
        # Prepare data for backend
        attendance_data = {
            "employee_name": user.full_name,
            "phone_number": user.username,  # Assuming username is phone number
            "telegram_id": user.id,
            "action": "login",
            "timestamp": adjusted_timestamp.isoformat(),
            "original_timestamp": timestamp.isoformat(),
            "is_grace_applied": adjusted_timestamp != timestamp
        }
        
        # Send to backend
        result = await self.send_to_backend(attendance_data)
        
        if result:
            grace_msg = " (Grace period applied)" if adjusted_timestamp != timestamp else ""
            await update.message.reply_text(
                f"✅ Login successful!\n"
                f"👤 Name: {user.full_name}\n"
                f"🕘 Time: {adjusted_timestamp.strftime('%I:%M %p')}{grace_msg}\n"
                f"📅 Date: {adjusted_timestamp.strftime('%d/%m/%Y')}"
            )
        else:
            await update.message.reply_text("❌ Login failed. Please try again.")
    
    async def handle_logout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle employee logout"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        timestamp = datetime.now(self.config.TIMEZONE)
        
        # Check if message is from the designated group
        if str(chat_id) != self.config.GROUP_CHAT_ID:
            return
        
        # Prepare data for backend
        attendance_data = {
            "employee_name": user.full_name,
            "phone_number": user.username,  # Assuming username is phone number
            "telegram_id": user.id,
            "action": "logout",
            "timestamp": timestamp.isoformat()
        }
        
        # Send to backend
        result = await self.send_to_backend(attendance_data)
        
        if result and result.get('duration'):
            duration = result['duration']
            await update.message.reply_text(
                f"✅ Logout successful!\n"
                f"👤 Name: {user.full_name}\n"
                f"🕘 Time: {timestamp.strftime('%I:%M %p')}\n"
                f"📅 Date: {timestamp.strftime('%d/%m/%Y')}\n"
                f"⏱️ Duration: {duration}"
            )
        else:
            await update.message.reply_text("❌ Logout failed or no active login found.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all messages to detect login/logout commands"""
        if not update.message or not update.message.text:
            return
            
        message_text = update.message.text.lower().strip()
        
        # Check for login commands
        if any(cmd in message_text for cmd in self.config.LOGIN_COMMANDS):
            await self.handle_login(update, context)
        
        # Check for logout commands
        elif any(cmd in message_text for cmd in self.config.LOGOUT_COMMANDS):
            await self.handle_logout(update, context)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "👋 Welcome to Employee Attendance Bot!\n\n"
            "Commands:\n"
            "• Type 'login', 'checkin', or 'in' to check in\n"
            "• Type 'logout', 'checkout', or 'out' to check out\n\n"
            "Working Hours: 9:00 AM - 6:00 PM IST\n"
            "Grace Period: 5 minutes (9:00-9:05 AM counted as 9:00 AM)\n\n"
            "📝 Note: Only works in the designated group chat."
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "🆘 Employee Attendance Bot Help\n\n"
            "📝 How to use:\n"
            "1. Send 'login' message when you start work\n"
            "2. Send 'logout' message when you finish work\n\n"
            "⏰ Working Hours:\n"
            "• Monday to Friday: 9:00 AM - 6:00 PM IST\n"
            "• Grace period: 9:00-9:05 AM (recorded as 9:00 AM)\n\n"
            "✅ Valid login commands: login, checkin, in\n"
            "✅ Valid logout commands: logout, checkout, out\n\n"
            "❗ Important: Bot only works in the designated group chat."
        )
        await update.message.reply_text(help_message)
    
    def run(self):
        """Start the bot"""
        if not self.config.BOT_TOKEN:
            logger.error("BOT_TOKEN not found in environment variables")
            return
        
        # Create application
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start polling
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = AttendanceBot()
    bot.run()