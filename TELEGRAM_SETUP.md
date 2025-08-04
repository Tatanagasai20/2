# Telegram Bot Setup & Employee Matching Guide

## How Telegram User Identification Works

### 🔍 **What Information Telegram Provides to Bots:**
- ✅ **User ID**: Unique numeric identifier (e.g., 123456789)
- ✅ **Full Name**: Display name set by user (e.g., "John Doe")
- ✅ **Username**: Optional handle (e.g., @johndoe) - many users don't have one
- ❌ **Phone Number**: NOT accessible to bots for privacy reasons

### 📋 **How Our System Matches Employees:**

#### 1. **First Time Setup (Manual Database Entry)**
```bash
# HR adds employee data manually
Employee ID: EMP001
Employee Name: John Doe
Phone Number: +1234567890
Telegram ID: (empty initially)
```

#### 2. **Automatic Linking Process**
When an employee sends their first "login" message:

**Step 1:** Bot checks if Telegram ID already exists in database
- If found → Use existing employee record

**Step 2:** If not found, try name matching:
- **Exact Match**: "John Doe" (Telegram) → "John Doe" (Database)
- **Partial Match**: "John" → "John Doe" (if unique)
- **Case Insensitive**: "JOHN DOE" → "John Doe"

**Step 3:** Try username matching (if employee username = employee ID):
- Username: @EMP001 → Employee ID: EMP001

**Step 4:** If match found:
- Link Telegram ID to employee record
- Future logins use Telegram ID directly

#### 3. **Example Matching Scenarios**

**✅ Scenario 1: Perfect Name Match**
```
Database: "John Doe"
Telegram: "John Doe"
Result: ✅ Matched and linked
```

**✅ Scenario 2: Username as Employee ID**
```
Database: Employee ID "EMP001"
Telegram: Username "@emp001" 
Result: ✅ Matched and linked
```

**❌ Scenario 3: No Match**
```
Database: "John Doe"
Telegram: "Johnny D"
Result: ❌ Employee not found - Contact HR
```

## 🚀 **Setup Instructions**

### Step 1: Create Telegram Bot
```bash
1. Message @BotFather on Telegram
2. Send: /newbot
3. Choose bot name: "YourCompany Attendance Bot"
4. Choose username: "yourcompany_attendance_bot"
5. Copy the bot token
```

### Step 2: Add Bot to Group
```bash
1. Create a Telegram group for your employees
2. Add your bot to the group
3. Make bot an admin (optional but recommended)
4. Get the group chat ID (see below)
```

### Step 3: Get Group Chat ID
```bash
# Method 1: Using getUpdates API
1. Send a message in your group
2. Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
3. Look for: "chat":{"id":-XXXXXXXXX,"title":"Your Group Name"}
4. Copy the negative number (e.g., -1001234567890)

# Method 2: Using our bot
1. Add bot to group
2. Send any message
3. Check bot logs for chat ID
```

### Step 4: Configure Environment Variables
```bash
# telegram-bot/.env
BOT_TOKEN=1234567890:ABCdef1234ghIkl-zyx57W2v1u123ew11
GROUP_CHAT_ID=-1001234567890
BACKEND_API_URL=http://backend:5000
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/employee_attendance
```

## 👥 **Employee Onboarding Process**

### For HR:
1. **Add employee to database first:**
```bash
docker exec -it backend python add_employees.py
# Enter: EMP001, John Doe, +1234567890
```

2. **Verify employee added:**
```bash
# Check list shows employee as "❌ Not Linked"
```

### For Employees:
1. **Join the company Telegram group**
2. **Set proper Telegram display name:**
   - Go to Settings → Edit Profile
   - Set "First Name" and "Last Name" to match database
   - Example: If database has "John Doe", set Telegram name as "John Doe"

3. **Send first login message:**
```
login
```

4. **Bot response if successful:**
```
✅ Login successful!
👤 Name: John Doe
🆔 Employee ID: EMP001
🕘 Time: 9:00 AM
📅 Date: 01/01/2024
```

5. **Bot response if not found:**
```
❌ Employee not found in system.

📋 Your Telegram Details:
• Name: Johnny D
• Username: @johnd
• ID: 123456789

💡 Please contact HR to:
1. Add your details to the system
2. Link your Telegram account

📞 Make sure your Telegram name matches your employee name in the database.
```

## 🔧 **Troubleshooting Common Issues**

### Issue 1: "Employee not found"
**Cause:** Name mismatch between Telegram and database
**Solution:**
- Check employee name in database: `docker exec -it backend python add_employees.py` → Option 3
- Ask employee to update Telegram display name to match exactly
- Or manually link by Telegram ID

### Issue 2: Multiple employees match same name
**Cause:** Common names like "John" matching multiple "John Smith", "John Doe"
**Solution:**
- Use more specific names in database
- Ask employees to use full names in Telegram
- Manual linking by HR

### Issue 3: Bot not responding
**Cause:** Incorrect bot token or group chat ID
**Solution:**
```bash
# Test bot token
curl -X GET "https://api.telegram.org/bot<BOT_TOKEN>/getMe"

# Check group chat ID
curl -X GET "https://api.telegram.org/bot<BOT_TOKEN>/getUpdates"
```

### Issue 4: Employee changes Telegram name
**Cause:** Employee already linked but changed display name
**Solution:** No problem - system uses stored Telegram ID, not name

## 📱 **Best Practices**

### For HR:
1. **Standardize naming convention:**
   - Database: "FirstName LastName" (e.g., "John Doe")
   - Ask employees to match this format in Telegram

2. **Pre-populate employee data:**
   - Add all employees to database before deployment
   - Use consistent ID format (e.g., EMP001, EMP002)

3. **Monitor linking status:**
   - Regularly check which employees are linked
   - Follow up with unlinked employees

### For Employees:
1. **Set clear Telegram display name:**
   - Use real name, not nicknames
   - Match company records exactly
   - Example: "John Doe" not "Johnny" or "J.Doe"

2. **Test the system:**
   - Send "login" and "logout" messages
   - Verify attendance is recorded correctly
   - Report issues to HR immediately

## 🔐 **Privacy & Security**

- ✅ **Bot cannot access phone numbers** - Telegram privacy protection
- ✅ **Only works in designated group** - Configured GROUP_CHAT_ID
- ✅ **Employee data encrypted** - MongoDB Atlas encryption
- ✅ **Telegram ID linking** - Once linked, uses secure ID system
- ✅ **HR dashboard protected** - Username/password authentication

## 📊 **Monitoring & Maintenance**

```bash
# Check employee linking status
docker exec -it backend python add_employees.py
# Choose option 3: List all employees

# View bot logs
docker logs telegram-bot

# Check attendance records
# Access HR dashboard at http://your-ip/
# Login: hr.admin / hr.password
```