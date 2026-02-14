#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔍 OSINT Telegram Bot - Enhanced Version 🔍              ║
║                                                                              ║
║  Purpose: Professional OSINT investigation bot for cybersecurity research   ║
║  Features: FREE & UNLIMITED OSINT tools + Maigret username search           ║
║  Language: English with emoji support                                       ║
║                                                                              ║
║  ⚠️ LEGAL NOTICE: FOR AUTHORIZED CYBERSECURITY RESEARCH ONLY ⚠️            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════════
# 📦 IMPORTS - Core Bot Libraries
# ═══════════════════════════════════════════════════════════════════════════════
import os
import sys
import json
import logging
import asyncio
import re
import socket
import dns.resolver
import requests
import hashlib
import whois
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import ipaddress
import base64
from pathlib import Path

# Telegram Bot API imports
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ChatMember
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from telegram.constants import ParseMode
from telegram.error import TelegramError

# OSINT and Investigation Libraries
import ipwhois
from bs4 import BeautifulSoup

# ═══════════════════════════════════════════════════════════════════════════════
# ⚙️ CONFIGURATION - Bot Settings
# ═══════════════════════════════════════════════════════════════════════════════

# 🔑 Bot Token - توكن البوت
BOT_TOKEN = "8114212318:AAHKWtSbVyFewpzkzAdGCcqOBMUT2jUdvLI"

# 📢 Mandatory Subscription Channels - قنوات الاشتراك الإجباري
REQUIRED_CHANNELS = [
    "@hackfirst",
    "@SpiderFoott",
]

# 🎨 Bot Configuration
BOT_CONFIG = {
    "name": "OSINT Investigation Bot",
    "version": "3.0 - Enhanced",
    "admin_ids": [7504646622],
    "max_requests_per_minute": 10,
    "timeout": 30,
    "language": "en"
}

# 📝 Logging Configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('osint_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 🎭 CONVERSATION STATES
# ═══════════════════════════════════════════════════════════════════════════════
WAITING_FOR_INPUT = 1


# ═══════════════════════════════════════════════════════════════════════════════
# 🛡️ SUBSCRIPTION CHECKER
# ═══════════════════════════════════════════════════════════════════════════════

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is subscribed to required channels"""
    user_id = update.effective_user.id
    not_subscribed = []
    
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                not_subscribed.append(channel)
        except Exception as e:
            logger.error(f"Error checking subscription for channel {channel}: {e}")
            not_subscribed.append(channel)
    
    if not_subscribed:
        keyboard = []
        for channel in not_subscribed:
            keyboard.append([InlineKeyboardButton(
                f"📢 Subscribe to {channel}", 
                url=f"https://t.me/{channel.replace('@', '')}"
            )])
        
        keyboard.append([InlineKeyboardButton("✅ I Subscribed - Check Again", callback_data="check_subscription")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "🚫 <b>Access Denied</b> 🚫\n\n"
            "⚠️ You must subscribe to our channels to use this bot:\n\n"
        )
        
        for channel in not_subscribed:
            message += f"• {channel}\n"
        
        message += "\n💡 <i>After subscribing, click 'I Subscribed' button below</i>"
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        return False
    
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 KEYBOARD LAYOUTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🌐 IP & Network", callback_data="menu_ip_network"),
            InlineKeyboardButton("📧 Email Tools", callback_data="menu_email")
        ],
        [
            InlineKeyboardButton("🌍 Domain & DNS", callback_data="menu_domain"),
            InlineKeyboardButton("👤 Username Search", callback_data="tool_maigret")
        ],
        [
            InlineKeyboardButton("🔍 WHOIS Lookup", callback_data="tool_whois"),
            InlineKeyboardButton("✍️ Write Text Image", callback_data="tool_write_text")
        ],
        [
            InlineKeyboardButton("💰 Crypto Tools", callback_data="menu_crypto"),
            InlineKeyboardButton("🔗 Utilities", callback_data="menu_utilities")
        ],
        [
            InlineKeyboardButton("ℹ️ Help & Info", callback_data="menu_help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_ip_network_keyboard() -> InlineKeyboardMarkup:
    """IP & Network tools keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🔍 IP Lookup (Comprehensive)", callback_data="tool_ip_lookup"),
        ],
        [
            InlineKeyboardButton("🔌 Port Scanner", callback_data="tool_port_scan"),
        ],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_email_keyboard() -> InlineKeyboardMarkup:
    """Email tools keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📧 Email Validation", callback_data="tool_email_valid"),
        ],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_domain_keyboard() -> InlineKeyboardMarkup:
    """Domain & DNS tools keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🔍 DNS Lookup", callback_data="tool_dns_lookup"),
        ],
        [
            InlineKeyboardButton("📊 DNS Records", callback_data="tool_dns_records"),
        ],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_utilities_keyboard() -> InlineKeyboardMarkup:
    """Utilities tools keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🔗 URL Expander", callback_data="tool_url_expander"),
        ],
        [
            InlineKeyboardButton("📧 Disposable Email Check", callback_data="tool_disposable_email"),
        ],
        [
            InlineKeyboardButton("🔐 Hash Generator", callback_data="tool_hash_generator"),
        ],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_crypto_keyboard() -> InlineKeyboardMarkup:
    """Cryptocurrency tools keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("₿ Bitcoin Address", callback_data="tool_bitcoin"),
            InlineKeyboardButton("💎 Ethereum Address", callback_data="tool_ethereum")
        ],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    
    if not await check_subscription(update, context):
        return
    
    welcome_message = (
        f"👋 <b>Welcome {user.first_name}!</b>\n\n"
        f"🛡️ <b>Professional OSINT Tool - FREE & UNLIMITED</b>\n\n"
        f"📊 <b>Features:</b>\n"
        f"• 🌐 IP & Network Analysis (Comprehensive)\n"
        f"• 📧 Email Investigation\n"
        f"• 🌍 Domain & DNS Research\n"
        f"• 👤 Username Search (Maigret - 3000+ sites)\n"
        f"• 💰 Cryptocurrency Tracking\n"
        f"• ✍️ Text to Image Writer\n"
        f"• 🔗 Useful Utilities\n"
        f"• And more :)\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚠️ <b>LEGAL NOTICE:</b>\n"
        f"<i>This tool is for authorized cybersecurity research only.</i>\n\n"
        f"<b>Subscribe @Spiderfoott</b>\n\n"
        f"💡 Select a category below to begin:\n"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = (
        "📚 <b>Bot Help & Instructions</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>🎯 How to Use:</b>\n\n"
        "1️⃣ Select a category from the main menu\n"
        "2️⃣ Choose your desired tool\n"
        "3️⃣ Follow the instructions\n"
        "4️⃣ Enter the required information\n"
        "5️⃣ Receive detailed results\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>⚙️ Commands:</b>\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/menu - Return to main menu\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ <b>All tools are FREE and UNLIMITED!</b>\n"
        "⚠️ <b>Use for legal purposes only</b>\n"
    )
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard()
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /menu command"""
    await update.message.reply_text(
        "🏠 <b>Main Menu</b>\n\nSelect a category:",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 CALLBACK HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Main callback handler for all buttons"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Menu Navigation
    if callback_data == "main_menu":
        await query.edit_message_text(
            "🏠 <b>Main Menu</b>\n\nSelect a category:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu_keyboard()
        )
    
    elif callback_data == "menu_ip_network":
        await query.edit_message_text(
            "🌐 <b>IP & Network Tools</b>\n\nSelect a tool:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_ip_network_keyboard()
        )
    
    elif callback_data == "menu_email":
        await query.edit_message_text(
            "📧 <b>Email Tools</b>\n\nSelect a tool:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_email_keyboard()
        )
    
    elif callback_data == "menu_domain":
        await query.edit_message_text(
            "🌍 <b>Domain & DNS Tools</b>\n\nSelect a tool:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_domain_keyboard()
        )
    
    elif callback_data == "menu_utilities":
        await query.edit_message_text(
            "🔗 <b>Utilities Tools</b>\n\nSelect a tool:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_utilities_keyboard()
        )
    
    elif callback_data == "menu_crypto":
        await query.edit_message_text(
            "💰 <b>Cryptocurrency Tools</b>\n\nSelect a tool:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_crypto_keyboard()
        )
    
    elif callback_data == "menu_help":
        help_text = (
            "📚 <b>Help & Information</b>\n\n"
            "This bot provides FREE & UNLIMITED OSINT tools.\n\n"
            "✅ No API keys required\n"
            "✅ No rate limits\n"
            "✅ All features are free\n\n"
            "Use /help for detailed instructions.\n"
        )
        keyboard = [[InlineKeyboardButton("« Back", callback_data="main_menu")]]
        await query.edit_message_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif callback_data == "check_subscription":
        user_id = update.effective_user.id
        not_subscribed = []
        
        for channel in REQUIRED_CHANNELS:
            try:
                member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
                if member.status in ['left', 'kicked']:
                    not_subscribed.append(channel)
            except:
                not_subscribed.append(channel)
        
        if not_subscribed:
            await query.answer("❌ You're not subscribed to all channels yet!", show_alert=True)
        else:
            await query.answer("✅ Subscription verified! Welcome!", show_alert=True)
            await query.message.delete()
            # Create a fake update for start_command
            from telegram import Message, Chat, User as TGUser
            fake_message = query.message
            fake_update = Update(update.update_id, message=fake_message)
            await start_command(fake_update, context)
    
    elif callback_data.startswith("tool_"):
        await handle_tool_selection(update, context, callback_data)


# ═══════════════════════════════════════════════════════════════════════════════
# 🛠️ TOOL HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_tool_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, tool_id: str) -> None:
    """Handle tool selection and display instructions"""
    query = update.callback_query
    
    context.user_data['current_tool'] = tool_id
    
    tools_info = {
        "tool_ip_lookup": {
            "name": "Comprehensive IP Lookup",
            "emoji": "🔍",
            "description": "Get detailed information about any IP address (Geolocation, WHOIS, Reputation, ASN, etc.)",
            "instruction": "Please send the IP address you want to investigate:",
            "example": "Example: 8.8.8.8"
        },
        "tool_port_scan": {
            "name": "Port Scanner",
            "emoji": "🔌",
            "description": "Scan for open ports on a target",
            "instruction": "Send the IP address or domain to scan:",
            "example": "Example: scanme.nmap.org"
        },
        "tool_email_valid": {
            "name": "Email Validation",
            "emoji": "📧",
            "description": "Check if an email address is valid and has MX records",
            "instruction": "Send the email address to validate:",
            "example": "Example: user@example.com"
        },
        "tool_whois": {
            "name": "WHOIS Lookup",
            "emoji": "🔍",
            "description": "Get domain registration information",
            "instruction": "Send the domain name:",
            "example": "Example: google.com"
        },
        "tool_dns_lookup": {
            "name": "DNS Lookup",
            "emoji": "🔍",
            "description": "Resolve DNS records for a domain",
            "instruction": "Send the domain name:",
            "example": "Example: example.com"
        },
        "tool_dns_records": {
            "name": "DNS Records",
            "emoji": "📊",
            "description": "Get all DNS records (A, MX, TXT, etc)",
            "instruction": "Send the domain name:",
            "example": "Example: google.com"
        },
        "tool_maigret": {
            "name": "Maigret Username Search",
            "emoji": "👤",
            "description": "Search for username across 3000+ social media platforms and websites",
            "instruction": "Send the username you want to search:",
            "example": "Example: john_doe"
        },
        "tool_write_text": {
            "name": "Write Text on Image",
            "emoji": "✍️",
            "description": "Generate beautiful handwritten text images",
            "instruction": "Send the text you want to write:",
            "example": "Example: Hello World!"
        },
        "tool_url_expander": {
            "name": "URL Expander",
            "emoji": "🔗",
            "description": "Expand shortened URLs and see the real destination",
            "instruction": "Send the shortened URL:",
            "example": "Example: bit.ly/abc123"
        },
        "tool_disposable_email": {
            "name": "Disposable Email Checker",
            "emoji": "📧",
            "description": "Check if an email is from a disposable/temporary email service",
            "instruction": "Send the email address:",
            "example": "Example: user@tempmail.com"
        },
        "tool_hash_generator": {
            "name": "Hash Generator",
            "emoji": "🔐",
            "description": "Generate MD5, SHA1, SHA256, SHA512 hashes of text",
            "instruction": "Send the text to hash:",
            "example": "Example: password123"
        },
        "tool_bitcoin": {
            "name": "Bitcoin Address Lookup",
            "emoji": "₿",
            "description": "Analyze Bitcoin address and check balance",
            "instruction": "Send Bitcoin address:",
            "example": "Example: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        },
        "tool_ethereum": {
            "name": "Ethereum Address Lookup",
            "emoji": "💎",
            "description": "Analyze Ethereum address and check balance",
            "instruction": "Send Ethereum address:",
            "example": "Example: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        },
    }
    
    tool_info = tools_info.get(tool_id, {
        "name": "Tool",
        "emoji": "🔧",
        "description": "OSINT Tool",
        "instruction": "Send the required input:",
        "example": "Example: your input"
    })
    
    message = (
        f"{tool_info['emoji']} <b>{tool_info['name']}</b>\n\n"
        f"📝 <b>Description:</b>\n{tool_info['description']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📥 <b>Instructions:</b>\n{tool_info['instruction']}\n\n"
        f"💡 {tool_info['example']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏳ <i>Waiting for your input...</i>"
    )
    
    keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="main_menu")]]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 🔬 INPUT PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

async def process_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process user input and execute selected tool"""
    user_input = update.message.text
    current_tool = context.user_data.get('current_tool', None)
    
    if not current_tool:
        return
    
    processing_msg = await update.message.reply_text(
        "⏳ <b>Processing your request...</b>\n\n"
        "🔍 <i>Gathering intelligence data...</i>",
        parse_mode=ParseMode.HTML
    )
    
    try:
        result = await execute_osint_tool(current_tool, user_input, update, context)
        
        await processing_msg.delete()
        
        keyboard = [[InlineKeyboardButton("🔄 New Search", callback_data=current_tool)],
                   [InlineKeyboardButton("« Main Menu", callback_data="main_menu")]]
        
        # Split long messages
        if len(result) > 4000:
            parts = [result[i:i+4000] for i in range(0, len(result), 4000)]
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    await update.message.reply_text(
                        part,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                else:
                    await update.message.reply_text(part, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(
                result,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
    except Exception as e:
        logger.error(f"Error processing tool {current_tool}: {e}")
        await processing_msg.edit_text(
            f"❌ <b>Error</b>\n\n"
            f"Failed to process your request.\n"
            f"Error: {str(e)}\n\n"
            f"Please try again.",
            parse_mode=ParseMode.HTML
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 TOOL IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def execute_osint_tool(tool_id: str, user_input: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Execute specific OSINT tool"""
    
    if tool_id == "tool_ip_lookup":
        return await comprehensive_ip_lookup(user_input)
    
    elif tool_id == "tool_port_scan":
        return await port_scanner(user_input)
    
    elif tool_id == "tool_email_valid":
        return await email_validation(user_input)
    
    elif tool_id == "tool_whois":
        return await domain_whois(user_input)
    
    elif tool_id == "tool_dns_lookup":
        return await dns_lookup(user_input)
    
    elif tool_id == "tool_dns_records":
        return await dns_records(user_input)
    
    elif tool_id == "tool_maigret":
        return await maigret_search(user_input, update, context)
    
    elif tool_id == "tool_write_text":
        return await write_text_image(user_input, update, context)
    
    elif tool_id == "tool_url_expander":
        return await expand_url(user_input)
    
    elif tool_id == "tool_disposable_email":
        return await check_disposable_email(user_input)
    
    elif tool_id == "tool_hash_generator":
        return await generate_hashes(user_input)
    
    elif tool_id == "tool_bitcoin":
        return await bitcoin_lookup(user_input)
    
    elif tool_id == "tool_ethereum":
        return await ethereum_lookup(user_input)
    
    else:
        return (
            f"🔧 <b>Tool: {tool_id}</b>\n\n"
            f"📥 <b>Input:</b> <code>{user_input}</code>\n\n"
            f"✅ <b>Status:</b> Tool is operational\n\n"
            f"<i>This tool is being processed...</i>"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 🔍 INDIVIDUAL TOOL FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def comprehensive_ip_lookup(ip: str) -> str:
    """Comprehensive IP Lookup - combines multiple data sources"""
    try:
        result = f"🔍 <b>Comprehensive IP Lookup</b>\n\n🌐 <b>IP Address:</b> <code>{ip}</code>\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # 1. Get basic info from ip-api.com
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
            data = response.json()
            
            if data.get('status') == 'success':
                lat = data.get('lat')
                lon = data.get('lon')
                map_link = f"https://www.google.com/maps?q={lat},{lon}"
                
                result += f"📍 <b>Geolocation:</b>\n"
                result += f"• Country: {data.get('country', 'N/A')} ({data.get('countryCode', 'N/A')})\n"
                result += f"• Region: {data.get('regionName', 'N/A')}\n"
                result += f"• City: {data.get('city', 'N/A')}\n"
                result += f"• ZIP: {data.get('zip', 'N/A')}\n"
                result += f"• Coordinates: {lat}, {lon}\n"
                result += f"• <a href='{map_link}'>View on Google Maps</a>\n\n"
                
                result += f"🌐 <b>Network:</b>\n"
                result += f"• ISP: {data.get('isp', 'N/A')}\n"
                result += f"• Organization: {data.get('org', 'N/A')}\n"
                result += f"• AS: {data.get('as', 'N/A')}\n\n"
                
                result += f"⏰ <b>Timezone:</b> {data.get('timezone', 'N/A')}\n\n"
        except Exception as e:
            result += f"⚠️ Geolocation lookup failed: {str(e)}\n\n"
        
        # 2. Get WHOIS info
        try:
            obj = ipwhois.IPWhois(ip)
            whois_results = obj.lookup_rdap()
            
            result += f"📡 <b>WHOIS Information:</b>\n"
            result += f"• ASN: <code>{whois_results.get('asn', 'N/A')}</code>\n"
            result += f"• ASN Description: {whois_results.get('asn_description', 'N/A')}\n"
            result += f"• ASN Country: {whois_results.get('asn_country_code', 'N/A')}\n"
            result += f"• CIDR: <code>{whois_results.get('asn_cidr', 'N/A')}</code>\n"
            result += f"• Registry: {whois_results.get('asn_registry', 'N/A')}\n"
            result += f"• Network Name: {whois_results.get('network', {}).get('name', 'N/A')}\n\n"
        except Exception as e:
            result += f"⚠️ WHOIS lookup failed: {str(e)}\n\n"
        
        # 3. Check if IP is private
        try:
            ip_obj = ipaddress.ip_address(ip)
            is_private = ip_obj.is_private
            result += f"🔒 <b>IP Type:</b> {'Private IP' if is_private else 'Public IP'}\n\n"
        except:
            pass
        
        result += f"✅ <b>Status:</b> Comprehensive Analysis Complete"
        
        return result
        
    except Exception as e:
        logger.error(f"Comprehensive IP Lookup error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"


async def port_scanner(target: str) -> str:
    """Port Scanner - scan common ports"""
    try:
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443]
        
        try:
            target_ip = socket.gethostbyname(target)
        except:
            target_ip = target
        
        open_ports = []
        closed_ports = []
        
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target_ip, port))
            
            if result == 0:
                open_ports.append(port)
            else:
                closed_ports.append(port)
            
            sock.close()
        
        open_ports_text = ', '.join(map(str, open_ports)) if open_ports else 'None'
        
        return (
            f"🔌 <b>Port Scan Results</b>\n\n"
            f"🎯 <b>Target:</b> <code>{target}</code>\n"
            f"🌐 <b>IP Address:</b> <code>{target_ip}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ <b>Open Ports ({len(open_ports)}):</b>\n"
            f"<code>{open_ports_text}</code>\n\n"
            f"❌ <b>Closed Ports:</b> {len(closed_ports)}\n\n"
            f"📊 <b>Scan Details:</b>\n"
            f"• Ports Scanned: {len(common_ports)}\n"
            f"• Scan Type: TCP Connect\n\n"
            f"✅ <b>Status:</b> Scan Complete"
        )
        
    except Exception as e:
        logger.error(f"Port Scanner error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"


async def email_validation(email: str) -> str:
    """Email Validation"""
    try:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid_format = bool(re.match(email_pattern, email))
        
        domain = email.split('@')[1] if '@' in email else None
        
        has_mx = False
        mx_records = []
        
        if domain:
            try:
                answers = dns.resolver.resolve(domain, 'MX')
                has_mx = True
                mx_records = [str(rdata.exchange) for rdata in answers]
            except:
                pass
        
        status = "✅ Valid" if (is_valid_format and has_mx) else "❌ Invalid"
        
        return (
            f"📧 <b>Email Validation</b>\n\n"
            f"📬 <b>Email:</b> <code>{email}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Validation Results:</b>\n"
            f"• Status: {status}\n"
            f"• Format Valid: {'✅ Yes' if is_valid_format else '❌ No'}\n"
            f"• Domain: {domain if domain else 'N/A'}\n"
            f"• MX Records: {'✅ Found' if has_mx else '❌ Not Found'}\n\n"
            f"🌐 <b>Mail Servers:</b>\n"
            f"{chr(10).join(['• ' + mx for mx in mx_records[:3]]) if mx_records else '• None found'}\n\n"
            f"✅ <b>Status:</b> Validation Complete"
        )
        
    except Exception as e:
        logger.error(f"Email Validation error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"


async def domain_whois(domain: str) -> str:
    """WHOIS Lookup for domains"""
    try:
        w = whois.whois(domain)
        
        return (
            f"🌐 <b>WHOIS Lookup</b>\n\n"
            f"🌍 <b>Domain:</b> <code>{domain}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Registration Details:</b>\n"
            f"• Registrar: {w.registrar if w.registrar else 'N/A'}\n"
            f"• Creation Date: {w.creation_date if w.creation_date else 'N/A'}\n"
            f"• Expiration Date: {w.expiration_date if w.expiration_date else 'N/A'}\n"
            f"• Updated Date: {w.updated_date if w.updated_date else 'N/A'}\n\n"
            f"👤 <b>Registrant:</b>\n"
            f"• Organization: {w.org if w.org else 'N/A'}\n"
            f"• Email: {w.emails[0] if w.emails else 'N/A'}\n\n"
            f"🌐 <b>Name Servers:</b>\n"
            f"{chr(10).join(['• ' + str(ns) for ns in (w.name_servers if w.name_servers else ['N/A'])[:5]])}\n\n"
            f"✅ <b>Status:</b> WHOIS Lookup Complete"
        )
        
    except Exception as e:
        logger.error(f"WHOIS error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"


async def dns_lookup(domain: str) -> str:
    """DNS Lookup"""
    try:
        try:
            ip = socket.gethostbyname(domain)
        except:
            ip = "N/A"
        
        return (
            f"🔍 <b>DNS Lookup</b>\n\n"
            f"🌍 <b>Domain:</b> <code>{domain}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Results:</b>\n"
            f"• IP Address: <code>{ip}</code>\n\n"
            f"✅ <b>Status:</b> DNS Lookup Complete"
        )
        
    except Exception as e:
        logger.error(f"DNS Lookup error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"


async def dns_records(domain: str) -> str:
    """Get all DNS records"""
    try:
        result = f"📊 <b>DNS Records</b>\n\n🌍 <b>Domain:</b> <code>{domain}</code>\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                result += f"<b>{record_type} Records:</b>\n"
                for rdata in answers:
                    result += f"• {rdata}\n"
                result += "\n"
            except:
                result += f"<b>{record_type} Records:</b> None\n\n"
        
        result += f"✅ <b>Status:</b> DNS Records Retrieved"
        
        return result
        
    except Exception as e:
        logger.error(f"DNS Records error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"




async def maigret_search(username: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Maigret Username Search across 3000+ sites with improved filtering"""
    try:
        # Send initial message
        status_msg = await update.message.reply_text(
            f"🔍 <b>Maigret Search Started</b>\n\n"
            f"👤 <b>Username:</b> <code>{username}</code>\n\n"
            f"⏳ <i>Searching across 3000+ platforms...</i>\n"
            f"<i>This may take a few moments...</i>",
            parse_mode=ParseMode.HTML
        )
        
        # Create temporary directory for results
        with tempfile.TemporaryDirectory() as tmpdir:
            # Run maigret with JSON output for better parsing
            cmd = [
                "python3", "-m", "maigret",
                username,
                "--timeout", "15",
                "--no-color",
                "--folderoutput", tmpdir,
                "--json", "simple"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=180)
            except subprocess.TimeoutExpired:
                process.kill()
                await status_msg.delete()
                return (
                    f"⚠️ <b>Search Timeout</b>\n\n"
                    f"The search took too long. Try again with a different username."
                )
            
            # Parse JSON output
            found_accounts = {}
            try:
                # Try to find JSON output in stdout
                json_start = stdout.find('{')
                if json_start != -1:
                    json_data = json.loads(stdout[json_start:])
                    for site, info in json_data.items():
                        if isinstance(info, dict) and info.get('status') and 'Claimed' in str(info.get('status')):
                            url = info.get('url_user', info.get('url_main', ''))
                            if url:
                                found_accounts[site] = url
            except:
                # Fallback: Parse text output
                for line in stdout.split('\n'):
                    if '[+]' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            site_name = parts[1].strip(':')
                            if site_name and site_name not in found_accounts:
                                found_accounts[site_name] = f"Found on {site_name}"
            
            # Remove duplicates and filter low-quality results
            unique_accounts = {}
            for site, url in found_accounts.items():
                site_clean = site.strip().lower()
                # Skip generic or repeated names
                if site_clean and site_clean not in unique_accounts:
                    unique_accounts[site_clean] = {
                        'name': site,
                        'url': url
                    }
            
            # Build result message
            result = f"👤 <b>Maigret Username Search</b>\n\n"
            result += f"🔍 <b>Username:</b> <code>{username}</code>\n\n"
            result += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            if len(unique_accounts) >= 1:  # At least 1 result
                result += f"✅ <b>Found on {len(unique_accounts)} platforms:</b>\n\n"
                
                # Sort by name
                sorted_accounts = sorted(unique_accounts.items(), key=lambda x: x[1]['name'])
                
                for i, (_, info) in enumerate(sorted_accounts[:50], 1):  # Limit to 50
                    name = info['name']
                    url = info['url']
                    if url and url.startswith('http'):
                        result += f"{i}. <a href='{url}'>{name}</a>\n"
                    else:
                        result += f"{i}. {name}\n"
                
                if len(unique_accounts) > 50:
                    result += f"\n<i>... and {len(unique_accounts) - 50} more platforms</i>\n"
            else:
                result += f"❌ <b>No accounts found for this username</b>\n"
                result += f"\n💡 <i>Try a different username or check spelling</i>\n"
            
            result += f"\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            result += f"📊 <b>Search Statistics:</b>\n"
            result += f"• Platforms Checked: 3000+\n"
            result += f"• Unique Accounts Found: {len(unique_accounts)}\n\n"
            result += f"✅ <b>Status:</b> Search Complete"
            
            # Delete status message
            await status_msg.delete()
            
            return result
            
    except Exception as e:
        logger.error(f"Maigret error: {e}")
        return f"❌ <b>Error:</b> {str(e)}\n\n<i>Make sure maigret is installed: pip3 install maigret</i>"


async def bitcoin_lookup(address: str) -> str:
    """Bitcoin Address Lookup"""
    try:
        response = requests.get(f"https://blockchain.info/rawaddr/{address}", timeout=10)
        data = response.json()
        
        balance_btc = data.get('final_balance', 0) / 100000000
        total_received = data.get('total_received', 0) / 100000000
        total_sent = data.get('total_sent', 0) / 100000000
        n_tx = data.get('n_tx', 0)
        
        return (
            f"₿ <b>Bitcoin Address Lookup</b>\n\n"
            f"💰 <b>Address:</b> <code>{address}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Balance Information:</b>\n"
            f"• Current Balance: <b>{balance_btc:.8f} BTC</b>\n"
            f"• Total Received: {total_received:.8f} BTC\n"
            f"• Total Sent: {total_sent:.8f} BTC\n"
            f"• Number of Transactions: {n_tx}\n\n"
            f"🔗 <b>Blockchain Explorer:</b>\n"
            f"<a href='https://blockchain.info/address/{address}'>View on Blockchain.info</a>\n\n"
            f"✅ <b>Status:</b> Lookup Complete"
        )
        
    except Exception as e:
        logger.error(f"Bitcoin Lookup error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"


async def ethereum_lookup(address: str) -> str:
    """Ethereum Address Lookup"""
    try:
        response = requests.get(f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest", timeout=10)
        data = response.json()
        
        if data.get('status') == '1':
            balance_wei = int(data.get('result', 0))
            balance_eth = balance_wei / 1000000000000000000
            
            return (
                f"💎 <b>Ethereum Address Lookup</b>\n\n"
                f"💰 <b>Address:</b> <code>{address}</code>\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📊 <b>Balance Information:</b>\n"
                f"• Current Balance: <b>{balance_eth:.8f} ETH</b>\n\n"
                f"🔗 <b>Blockchain Explorer:</b>\n"
                f"<a href='https://etherscan.io/address/{address}'>View on Etherscan</a>\n\n"
                f"✅ <b>Status:</b> Lookup Complete"
            )
        else:
            return f"❌ Failed to lookup Ethereum address"
            
    except Exception as e:
        logger.error(f"Ethereum Lookup error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"


async def write_text_image(text: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Generate handwritten text image using xditya API"""
    try:
        # Send processing message
        processing_msg = await update.message.reply_text(
            "✍️ <b>Generating handwritten text image...</b>\n\n"
            "⏳ <i>Please wait...</i>",
            parse_mode=ParseMode.HTML
        )
        
        # API endpoint
        api_url = f"https://apis.xditya.me/write?text={requests.utils.quote(text)}"
        
        # Get image
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            # Send image
            await update.message.reply_photo(
                photo=response.content,
                caption=f"✍️ <b>Handwritten Text Image</b>\n\n"
                       f"📝 <b>Text:</b> <code>{text[:100]}{'...' if len(text) > 100 else ''}</code>",
                parse_mode=ParseMode.HTML
            )
            
            # Delete processing message
            await processing_msg.delete()
            
            return "✅ Image generated successfully!"
        else:
            await processing_msg.delete()
            return f"❌ <b>Error:</b> Failed to generate image (Status: {response.status_code})"
            
    except Exception as e:
        logger.error(f"Write Text Image error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"


async def expand_url(short_url: str) -> str:
    """Expand shortened URLs"""
    try:
        # Add http:// if not present
        if not short_url.startswith(('http://', 'https://')):
            short_url = 'http://' + short_url
        
        # Make request with allow_redirects
        response = requests.head(short_url, allow_redirects=True, timeout=10)
        expanded_url = response.url
        
        # Get additional info
        try:
            final_response = requests.get(expanded_url, timeout=10)
            status_code = final_response.status_code
            content_type = final_response.headers.get('content-type', 'Unknown')
        except:
            status_code = "N/A"
            content_type = "N/A"
        
        return (
            f"🔗 <b>URL Expander</b>\n\n"
            f"📥 <b>Short URL:</b>\n<code>{short_url}</code>\n\n"
            f"📤 <b>Expanded URL:</b>\n<code>{expanded_url}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Information:</b>\n"
            f"• Status Code: {status_code}\n"
            f"• Content Type: {content_type}\n"
            f"• Redirects: {'Yes' if short_url != expanded_url else 'No'}\n\n"
            f"✅ <b>Status:</b> URL Expanded Successfully"
        )
        
    except Exception as e:
        logger.error(f"URL Expander error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"


async def check_disposable_email(email: str) -> str:
    """Check if email is from disposable email service"""
    try:
        # Common disposable email domains (free, no API needed)
        disposable_domains = [
            'tempmail.com', 'guerrillamail.com', '10minutemail.com', 'mailinator.com',
            'throwaway.email', 'temp-mail.org', 'yopmail.com', 'fakemailgenerator.com',
            'trashmail.com', 'mohmal.com', 'emailondeck.com', 'getnada.com',
            'maildrop.cc', 'mintemail.com', 'sharklasers.com', 'guerrillamailblock.com',
            'spam4.me', 'grr.la', 'getairmail.com', 'dispostable.com'
        ]
        
        domain = email.split('@')[1].lower() if '@' in email else None
        
        if not domain:
            return f"❌ <b>Error:</b> Invalid email format"
        
        is_disposable = domain in disposable_domains
        
        # Additional check using DNS (some disposable services have specific patterns)
        has_mx = False
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            has_mx = True
        except:
            pass
        
        return (
            f"📧 <b>Disposable Email Checker</b>\n\n"
            f"📬 <b>Email:</b> <code>{email}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Results:</b>\n"
            f"• Domain: <code>{domain}</code>\n"
            f"• Disposable: {'⚠️ YES - Likely disposable/temporary' if is_disposable else '✅ NO - Likely permanent'}\n"
            f"• MX Records: {'✅ Found' if has_mx else '❌ Not Found'}\n\n"
            f"💡 <b>Note:</b> This check uses a database of known disposable email providers.\n\n"
            f"✅ <b>Status:</b> Check Complete"
        )
        
    except Exception as e:
        logger.error(f"Disposable Email Check error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"


async def generate_hashes(text: str) -> str:
    """Generate multiple hash types for text"""
    try:
        # Generate hashes
        md5_hash = hashlib.md5(text.encode()).hexdigest()
        sha1_hash = hashlib.sha1(text.encode()).hexdigest()
        sha256_hash = hashlib.sha256(text.encode()).hexdigest()
        sha512_hash = hashlib.sha512(text.encode()).hexdigest()
        
        return (
            f"🔐 <b>Hash Generator</b>\n\n"
            f"📝 <b>Original Text:</b>\n<code>{text[:100]}{'...' if len(text) > 100 else ''}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Generated Hashes:</b>\n\n"
            f"<b>MD5:</b>\n<code>{md5_hash}</code>\n\n"
            f"<b>SHA1:</b>\n<code>{sha1_hash}</code>\n\n"
            f"<b>SHA256:</b>\n<code>{sha256_hash}</code>\n\n"
            f"<b>SHA512:</b>\n<code>{sha512_hash}</code>\n\n"
            f"✅ <b>Status:</b> Hashes Generated Successfully"
        )
        
    except Exception as e:
        logger.error(f"Hash Generator error: {e}")
        return f"❌ <b>Error:</b> {str(e)}"


# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """Start the bot"""
    logger.info("Starting OSINT Telegram Bot...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_user_input))
    
    # Start bot
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
