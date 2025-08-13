import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json
from config import Config
from pymongo import MongoClient
import pytz

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

class AttendanceBot:
    def __init__(self):
        self.config = Config()
        # Connect to MongoDB
        try:
            self.client = MongoClient(self.config.MONGODB_URI)
            self.db = self.client.employee_attendance
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
        
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
    
    def find_employee_by_telegram_id(self, telegram_id):
        """Find employee by Telegram ID"""
        try:
            if not self.db:
                return None
            return self.db.employees.find_one({'telegram_id': telegram_id, 'status': 'active'})
        except Exception as e:
            logger.error(f"Error finding employee by telegram ID: {e}")
            return None
    
    def find_employee_by_name(self, name):
        """Find employee by name (for first-time registration)"""
        try:
            if not self.db:
                return None
            # Try exact match first
            employee = self.db.employees.find_one({
                'employee_name': {'$regex': f'^{name}$', '$options': 'i'},
                'status': 'active'
            })
            if employee:
                return employee
            
            # Try partial match
            employee = self.db.employees.find_one({
                'employee_name': {'$regex': name, '$options': 'i'},
                'status': 'active'
            })
            return employee
        except Exception as e:
            logger.error(f"Error finding employee by name: {e}")
            return None
    
    def update_employee_telegram_id(self, employee_id, telegram_id):
        """Update employee with Telegram ID"""
        try:
            if not self.db:
                return False
            result = self.db.employees.update_one(
                {'employee_id': employee_id},
                {'$set': {'telegram_id': telegram_id, 'updated_at': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating employee telegram ID: {e}")
            return False
    
    async def handle_register(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle employee registration - first time setup"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Check if message is from the designated group
        if str(chat_id) != self.config.GROUP_CHAT_ID:
            return
        
        # Check if already registered
        existing_employee = self.find_employee_by_telegram_id(user.id)
        if existing_employee:
            await update.message.reply_text(
                f"✅ You are already registered!\n"
                f"👤 Name: {existing_employee['employee_name']}\n"
                f"🆔 Employee ID: {existing_employee['employee_id']}\n\n"
                f"You can now use:\n"
                f"• /login - to check in\n"
                f"• /logout - to check out"
            )
            return
        
        # Check if user has a full name
        if not user.full_name:
            await update.message.reply_text(
                f"❌ Please set your full name in Telegram first!\n\n"
                f"📱 Go to Telegram Settings → Edit Profile → Name\n"
                f"Make sure it matches your employee name in the system.\n\n"
                f"Then try /register again."
            )
            return
        
        # Try to find employee by name
        employee = self.find_employee_by_name(user.full_name.strip())
        if not employee:
            await update.message.reply_text(
                f"❌ Employee not found in system.\n\n"
                f"📋 Your Telegram Details:\n"
                f"• Name: {user.full_name}\n"
                f"• Username: @{user.username or 'Not set'}\n"
                f"• ID: {user.id}\n\n"
                f"💡 Please contact HR to:\n"
                f"1. Add your details to the system\n"
                f"2. Make sure your Telegram name matches your employee name\n\n"
                f"📞 Your Telegram name must exactly match: {user.full_name}"
            )
            return
        
        # Check if employee already has a Telegram ID
        if employee.get('telegram_id'):
            await update.message.reply_text(
                f"⚠️ This employee is already linked to another Telegram account.\n"
                f"Please contact HR to resolve this."
            )
            return
        
        # Link employee to Telegram ID
        if self.update_employee_telegram_id(employee['employee_id'], user.id):
            await update.message.reply_text(
                f"🎉 Registration successful!\n\n"
                f"👤 Name: {employee['employee_name']}\n"
                f"🆔 Employee ID: {employee['employee_id']}\n"
                f"📱 Telegram linked successfully\n\n"
                f"✅ You can now use:\n"
                f"• /login - to check in\n"
                f"• /logout - to check out\n\n"
                f"⏰ Working Hours: 9:00 AM - 6:00 PM IST\n"
                f"🕘 Grace Period: 9:00-9:05 AM (recorded as 9:00 AM)"
            )
        else:
            await update.message.reply_text(
                f"❌ Registration failed. Please try again or contact HR."
            )
    
    async def handle_login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle employee login"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        timestamp = datetime.now(self.config.TIMEZONE)
        
        # Check if message is from the designated group
        if str(chat_id) != self.config.GROUP_CHAT_ID:
            return
        
        # Find employee in database
        employee = self.find_employee_by_telegram_id(user.id)
        if not employee:
            await update.message.reply_text(
                f"❌ You are not registered yet!\n\n"
                f"📝 Please use /register first to link your Telegram account.\n\n"
                f"💡 If you're a new employee, contact HR to add you to the system."
            )
            return
        
        # Check if it's valid work time
        if not self.is_valid_work_time(timestamp):
            await update.message.reply_text(
                f"⚠️ Login is only allowed during working hours (9 AM - 6 PM IST) on weekdays."
            )
            return
        
        # Apply grace period
        adjusted_timestamp = self.apply_grace_period(timestamp)
        
        # Prepare data for backend using database employee info
        attendance_data = {
            "employee_id": employee['employee_id'],
            "employee_name": employee['employee_name'],
            "phone_number": employee.get('phone_number', ''),
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
                f"👤 Name: {employee['employee_name']}\n"
                f"🆔 Employee ID: {employee['employee_id']}\n"
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
        
        # Find employee in database
        employee = self.find_employee_by_telegram_id(user.id)
        if not employee:
            await update.message.reply_text(
                f"❌ You are not registered yet!\n\n"
                f"📝 Please use /register first to link your Telegram account."
            )
            return
        
        # Prepare data for backend using database employee info
        attendance_data = {
            "employee_id": employee['employee_id'],
            "employee_name": employee['employee_name'],
            "phone_number": employee.get('phone_number', ''),
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
                f"👤 Name: {employee['employee_name']}\n"
                f"🆔 Employee ID: {employee['employee_id']}\n"
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
            "📝 First Time Setup:\n"
            "• Use /register to link your Telegram account\n\n"
            "✅ After Registration:\n"
            "• Use /login to check in\n"
            "• Use /logout to check out\n\n"
            "⏰ Working Hours: 9:00 AM - 6:00 PM IST\n"
            "🕘 Grace Period: 5 minutes (9:00-9:05 AM counted as 9:00 AM)\n\n"
            "📝 Note: Only works in the designated group chat."
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "🆘 Employee Attendance Bot Help\n\n"
            "📝 First Time Setup:\n"
            "1. Use /register to link your Telegram account\n"
            "2. Make sure your Telegram name matches your employee name\n\n"
            "✅ Daily Usage:\n"
            "1. Send /login when you start work\n"
            "2. Send /logout when you finish work\n\n"
            "⏰ Working Hours:\n"
            "• Monday to Friday: 9:00 AM - 6:00 PM IST\n"
            "• Grace period: 9:00-9:05 AM (recorded as 9:00 AM)\n\n"
            "🔑 Commands:\n"
            "• /register - Link your Telegram account (first time only)\n"
            "• /login - Check in for the day\n"
            "• /logout - Check out for the day\n"
            "• /help - Show this help message\n\n"
            "❗ Important: Bot only works in the designated group chat."
        )
        await update.message.reply_text(help_message)
    
    def run(self):
        """Start the bot"""
        if not self.config.BOT_TOKEN:
            logger.error("BOT_TOKEN not found in environment variables")
            return
        
        if not self.db:
            logger.error("MongoDB connection failed. Cannot start bot.")
            return
        
        # Create application
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("register", self.handle_register))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start polling
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = AttendanceBot()
    bot.run()