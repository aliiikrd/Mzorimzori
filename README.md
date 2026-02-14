# 🔍 OSINT Telegram Bot - Enhanced Version

## 📖 Overview

Professional OSINT (Open Source Intelligence) Telegram bot for cybersecurity research and investigations. This bot provides **FREE and UNLIMITED** OSINT tools without requiring any API keys.

### ✨ Key Features

- ✅ **100% FREE** - No API keys required
- ✅ **UNLIMITED** - No rate limits on tools
- ✅ **Comprehensive IP Analysis** - Geolocation, WHOIS, ASN, reputation checks in one tool
- ✅ **Maigret Integration** - Search usernames across 3000+ platforms
- ✅ **Email Validation** - Check email validity and MX records
- ✅ **Cryptocurrency Tracking** - Bitcoin and Ethereum address analysis
- ✅ **Domain Investigation** - WHOIS, DNS records, and lookups
- ✅ **Port Scanning** - Check for open ports on targets
- ✅ **Text to Image Writer** - Generate beautiful handwritten text images
- ✅ **URL Expander** - Expand shortened URLs and see real destinations
- ✅ **Disposable Email Checker** - Detect temporary email addresses
- ✅ **Hash Generator** - Generate MD5, SHA1, SHA256, SHA512 hashes

## 🚀 Quick Start

### Installation

1. **Requirements:**
   - Python 3.10 or higher (Python 3.11 recommended)
   - pip package manager

2. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure Bot:**
   - Edit `bot.py`
   - Add your Telegram bot token from @BotFather
   - Update channel usernames for mandatory subscriptions

4. **Run Bot:**
```bash
python bot.py
```

## 📋 Available Tools

### 🌐 IP & Network Tools
- **Comprehensive IP Lookup** - All-in-one IP analysis (geolocation, WHOIS, ASN, reputation)
- **Port Scanner** - Scan common ports on targets

### 📧 Email Tools
- **Email Validation** - Verify email format and MX records

### 🌍 Domain & DNS Tools
- **WHOIS Lookup** - Domain registration information
- **DNS Lookup** - Resolve domain to IP
- **DNS Records** - Get all DNS records (A, AAAA, MX, NS, TXT, CNAME)

### 🔗 Utilities Tools
- **URL Expander** - Expand shortened URLs and reveal real destinations
- **Disposable Email Checker** - Check if email is from temporary service
- **Hash Generator** - Generate MD5, SHA1, SHA256, SHA512 hashes
- **Text to Image Writer** - Generate handwritten text images

### 👤 Username Search
- **Maigret** - Search username across 3000+ social media platforms and websites (improved filtering)

### 💰 Cryptocurrency Tools
- **Bitcoin Address Lookup** - Check balance and transaction history
- **Ethereum Address Lookup** - Check ETH balance

## 🤖 For AI Developers: How to Add New Tools

### Step-by-Step Guide for Adding New OSINT Tools

#### 1. Add Tool to Keyboard Layout

Find the appropriate menu function in `bot.py` (e.g., `get_ip_network_keyboard()`) and add your tool button:

```python
def get_ip_network_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        # ... existing buttons ...
        [
            InlineKeyboardButton("🆕 New Tool Name", callback_data="tool_new_tool"),
        ],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
```

#### 2. Add Tool Information

Add your tool's description in the `handle_tool_selection()` function's `tools_info` dictionary:

```python
tools_info = {
    # ... existing tools ...
    "tool_new_tool": {
        "name": "New Tool Name",
        "emoji": "🆕",
        "description": "What this tool does",
        "instruction": "Send the required input:",
        "example": "Example: sample input"
    },
}
```

#### 3. Add Tool Handler

Add a condition in the `execute_osint_tool()` function:

```python
async def execute_osint_tool(tool_id: str, user_input: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    # ... existing conditions ...
    elif tool_id == "tool_new_tool":
        return await new_tool_function(user_input)
```

#### 4. Implement Tool Function

Create the actual tool function:

```python
async def new_tool_function(user_input: str) -> str:
    """New Tool - Description"""
    try:
        # Your tool logic here
        # Example: API call, data processing, etc.
        
        result = (
            f"🆕 <b>New Tool Results</b>\n\n"
            f"📥 <b>Input:</b> <code>{user_input}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Results:</b>\n"
            f"• Data 1: value\n"
            f"• Data 2: value\n\n"
            f"✅ <b>Status:</b> Analysis Complete"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"New Tool error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"
```

### ⚠️ Important Guidelines for Adding Tools

#### ✅ DO:
- **Use FREE APIs only** - No paid APIs or API keys required
- **Check for rate limits** - Ensure the API/service is unlimited or has high limits
- **Add error handling** - Always wrap code in try-except blocks
- **Format results nicely** - Use HTML formatting with emojis
- **Test thoroughly** - Make sure the tool works before committing
- **Document the tool** - Add clear description and examples

#### ❌ DON'T:
- **Don't add tools requiring API keys** - This bot is meant to be free and unlimited
- **Don't add rate-limited tools** - Avoid tools that will stop working after X requests
- **Don't add duplicate tools** - Check if similar functionality exists
- **Don't add non-OSINT tools** - Keep the bot focused on investigation tools
- **Don't hardcode sensitive data** - Use environment variables if needed

### 📝 Example: Adding a New Domain Age Checker

```python
# 1. Add button to domain keyboard
def get_domain_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        # ... existing buttons ...
        [
            InlineKeyboardButton("📅 Domain Age", callback_data="tool_domain_age"),
        ],
        # ...
    ]
    return InlineKeyboardMarkup(keyboard)

# 2. Add tool info
tools_info = {
    # ...
    "tool_domain_age": {
        "name": "Domain Age Checker",
        "emoji": "📅",
        "description": "Check how old a domain is",
        "instruction": "Send the domain name:",
        "example": "Example: google.com"
    },
}

# 3. Add handler
elif tool_id == "tool_domain_age":
    return await check_domain_age(user_input)

# 4. Implement function
async def check_domain_age(domain: str) -> str:
    """Check Domain Age"""
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        age = datetime.now() - creation_date
        age_years = age.days / 365.25
        
        return (
            f"📅 <b>Domain Age Checker</b>\n\n"
            f"🌍 <b>Domain:</b> <code>{domain}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Age Information:</b>\n"
            f"• Created: {creation_date.strftime('%Y-%m-%d')}\n"
            f"• Age: {age_years:.1f} years ({age.days} days)\n\n"
            f"✅ <b>Status:</b> Check Complete"
        )
        
    except Exception as e:
        logger.error(f"Domain Age error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"
```

## 🔧 Free APIs Used

This bot uses only free and unlimited (or high-limit) APIs:

- **ip-api.com** - IP geolocation (no key required)
- **blockchain.info** - Bitcoin address lookups (no key required)
- **etherscan.io** - Ethereum lookups (no key for basic features)
- **bgpview.io** - BGP/ASN information (no key required)
- **apis.xditya.me** - Text to image generation (no key required)
- **Built-in Python libraries** - DNS, WHOIS, socket operations, hashlib
- **Maigret** - Open source username search tool (3000+ sites)

## 📊 Changelog (v3.1)

### Added
- ✨ **Text to Image Writer** - Generate handwritten text images using free API
- 🔗 **URL Expander** - Expand shortened URLs
- 📧 **Disposable Email Checker** - Detect temporary email services
- 🔐 **Hash Generator** - Generate multiple hash types

### Improved
- 👤 **Maigret Search** - Enhanced filtering to remove duplicate results
- 👤 **Maigret Search** - Increased minimum results threshold
- 👤 **Maigret Search** - Better parsing with JSON output
- 👤 **Maigret Search** - Now searches 3000+ platforms (updated from 2000+)

### Removed
- ❌ **Phone Number Lookup** - Removed as requested (non-functional)
- ❌ **phonenumbers** library dependency

---

## 🚀 Future Tool Ideas (FREE ONLY)

Potential tools to add (must be free and unlimited):

- 🌐 Certificate Transparency logs search
- 📊 Git repository search (via public APIs)
- 🔍 Wayback Machine historical data
- 🌍 Reverse IP lookup (via DNS)
- 💾 Paste site search (public pastes)
- 🔗 QR Code generator/decoder
- 📧 Email header analyzer
- 🔒 SSL/TLS certificate checker

---

## 🛡️ Security & Legal

- **⚠️ FOR AUTHORIZED USE ONLY** - This tool is for legitimate cybersecurity research
- **📜 Comply with Laws** - Users must comply with all applicable laws (GDPR, CCPA, etc.)
- **🚫 No Illegal Use** - Developers are not responsible for misuse
- **🔒 Privacy** - Respect privacy and data protection regulations

## 📄 License

MIT License - See LICENSE file

## 👥 Contributing

Contributions are welcome! When adding new tools:
1. Ensure they are FREE and UNLIMITED
2. Follow the code structure outlined above
3. Test thoroughly before submitting PR
4. Update this README with tool descriptions

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Contact bot admin (configure in bot settings)

---

**Version:** 3.1 Enhanced  
**Last Updated:** 2026-02-14  
**Telegram Bot API:** python-telegram-bot 20.7  
**Python:** 3.10+ (3.11 recommended)

---

Made with ❤️ for the OSINT community
