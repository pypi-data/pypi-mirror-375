"""
NEONPAY Raw Telegram Bot API Example - Real-world Bot Implementation
Complete ready-to-use bot with donation system and digital store
Based on real production usage patterns
"""

import asyncio
import json
import logging
from datetime import datetime

from aiohttp import ClientSession, web

from neonpay.core import PaymentStage, PaymentStatus
from neonpay.factory import create_neonpay

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token
WEBHOOK_URL = "https://yourdomain.com/webhook"  # Replace with your webhook URL
WEBHOOK_PATH = "/webhook"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = 8080

neonpay = None

# Donation options: amount and description before payment
DONATE_OPTIONS = [
    {
        "amount": 1,
        "symbol": "⭐",
        "desc": "1⭐ support: Will be used for bot server costs",
    },
    {
        "amount": 10,
        "symbol": "⭐",
        "desc": "10⭐ support: Will be spent on developing new features",
    },
    {
        "amount": 50,
        "symbol": "🌟",
        "desc": "50⭐ big support: Will be used for bot development and promotion",
    },
]

# Digital products store
DIGITAL_PRODUCTS = [
    {
        "id": "premium_access",
        "title": "Premium Access",
        "description": "Unlock all premium features for 30 days",
        "price": 25,
        "symbol": "👑",
    },
    {
        "id": "custom_theme",
        "title": "Custom Theme",
        "description": "Personalized bot theme and colors",
        "price": 15,
        "symbol": "🎨",
    },
    {
        "id": "priority_support",
        "title": "Priority Support",
        "description": "24/7 priority customer support",
        "price": 30,
        "symbol": "⚡",
    },
]


async def setup_neonpay():
    """Initialize NEONPAY with real-world configuration"""
    global neonpay
    if neonpay:
        return neonpay

    neonpay = create_neonpay(bot_token=BOT_TOKEN)

    # Create payment stages for donations
    for option in DONATE_OPTIONS:
        neonpay.create_payment_stage(
            f"donate_{option['amount']}",
            PaymentStage(
                title=f"Support {option['amount']}{option['symbol']}",
                description=option["desc"],
                price=option["amount"],
            ),
        )

    # Create payment stages for digital products
    for product in DIGITAL_PRODUCTS:
        neonpay.create_payment_stage(
            product["id"],
            PaymentStage(
                title=f"{product['symbol']} {product['title']}",
                description=product["description"],
                price=product["price"],
            ),
        )


@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        try:
            # Determine if it's a donation or product purchase
            if result.stage_id.startswith("donate_"):
                await send_message(
                    result.user_id,
                    f"Thank you! Your support: {result.amount}⭐ ❤️\n"
                    f"Your contribution helps keep the bot running!",
                )
            else:
                # Handle digital product delivery
                product = next(
                    (p for p in DIGITAL_PRODUCTS if p["id"] == result.stage_id), None
                )
                if product:
                    await send_message(
                        result.user_id,
                        f"🎉 Purchase successful!\n\n"
                        f"Product: {product['symbol']} {product['title']}\n"
                        f"Price: {product['price']}⭐\n\n"
                        f"Your digital product has been activated!\n"
                        f"Thank you for your purchase! 🚀",
                    )

            logger.info(
                f"Payment completed: user={result.user_id}, amount={result.amount}, stage={result.stage_id}"
            )

        except Exception as e:
            logger.exception(f"Failed to send post-payment message: {e}")

    logger.info("✅ NEONPAY payment system initialized")
    return neonpay


async def send_message(user_id: int, text: str, reply_markup: dict = None):
    """Send message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": user_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    async with ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()


async def send_inline_keyboard(user_id: int, text: str, keyboard: list):
    """Send message with inline keyboard"""
    reply_markup = {"inline_keyboard": keyboard}
    return await send_message(user_id, text, reply_markup)


async def handle_start_command(user_id: int, username: str = None):
    """Handle /start command"""
    user_name = username or "Friend"

    welcome_text = (
        f"👋 Hello {user_name}!\n\n"
        f"🤖 I'm a free bot created with love by an independent developer.\n\n"
        f"📱 **Available Commands:**\n"
        f"• /help - Show all commands\n"
        f"• /donate - Support the developer\n"
        f"• /store - Digital products store\n"
        f"• /status - Bot statistics\n\n"
        f"💡 This bot is completely free to use!\n"
        f"If you find it helpful, consider supporting development."
    )

    keyboard = [
        [{"text": "❤️ Support Developer", "callback_data": "show_donate"}],
        [{"text": "🛒 Digital Store", "callback_data": "show_store"}],
        [{"text": "📋 Help", "callback_data": "show_help"}],
    ]

    await send_inline_keyboard(user_id, welcome_text, keyboard)


async def handle_donate_command(user_id: int):
    """Handle /donate command"""
    logging.info(f"/donate command received: user={user_id}")

    keyboard = [
        [
            {
                "text": f"{opt['symbol']} {opt['amount']}",
                "callback_data": f"donate:{opt['amount']}",
            }
        ]
        for opt in DONATE_OPTIONS
    ]

    await send_inline_keyboard(
        user_id, "Please choose an amount to support the developer:", keyboard
    )


async def handle_store_command(user_id: int):
    """Handle /store command"""
    logging.info(f"/store command received: user={user_id}")

    keyboard = [
        [
            {
                "text": f"{product['symbol']} {product['title']} - {product['price']}⭐",
                "callback_data": f"buy:{product['id']}",
            }
        ]
        for product in DIGITAL_PRODUCTS
    ]

    store_text = (
        "🛒 **Digital Products Store**\n\n"
        "Choose a product to purchase:\n\n"
        "💡 All products are delivered instantly after payment!"
    )

    await send_inline_keyboard(user_id, store_text, keyboard)


async def handle_status_command(user_id: int):
    """Handle /status command"""
    uptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status_text = (
        "📊 **Bot Status**\n\n"
        f"✅ Status: Online\n"
        f"⏰ Last restart: {uptime}\n"
        f"💫 Payment system: Active\n"
        f"🔧 Version: 2.0\n\n"
        f"Thank you for using this free bot!"
    )

    await send_message(user_id, status_text)


async def handle_help_command(user_id: int):
    """Handle /help command"""
    help_text = (
        "📋 **Bot Help**\n\n"
        "🆓 **This bot is completely free!**\n\n"
        "**Commands:**\n"
        "• /start - Welcome message\n"
        "• /donate - Support development\n"
        "• /store - Digital products store\n"
        "• /status - Bot statistics\n"
        "• /help - This help message\n\n"
        "**About:**\n"
        "This bot was created by an independent developer.\n"
        "All features are free, donations help keep it running!\n\n"
        "🐛 Found a bug? Contact @your_username"
    )

    await send_message(user_id, help_text)


async def handle_callback_query(user_id: int, data: str):
    """Handle callback queries"""
    try:
        if data == "show_donate":
            await handle_donate_command(user_id)
        elif data == "show_store":
            await handle_store_command(user_id)
        elif data == "show_help":
            await handle_help_command(user_id)
        elif data.startswith("donate:"):
            amount = int(data.split(":")[1])
            option = next((o for o in DONATE_OPTIONS if o["amount"] == amount), None)

            if not option:
                await send_message(user_id, "❌ Error: Selected amount not found")
                return

            # Send payment using NeonPay
            await neonpay.send_payment(user_id=user_id, stage_id=f"donate_{amount}")
            logger.info(f"Support started: user={user_id}, amount={amount}")
            await send_message(user_id, "✅ Payment message sent")

        elif data.startswith("buy:"):
            product_id = data.split(":")[1]
            product = next((p for p in DIGITAL_PRODUCTS if p["id"] == product_id), None)

            if not product:
                await send_message(user_id, "❌ Error: Product not found")
                return

            # Send payment using NeonPay
            await neonpay.send_payment(user_id=user_id, stage_id=product_id)
            logger.info(
                f"Product purchase started: user={user_id}, product={product_id}"
            )
            await send_message(user_id, "✅ Payment message sent")

    except Exception as e:
        logger.exception(f"Failed to handle callback: {e}")
        await send_message(user_id, "💥 Error occurred during payment")


async def webhook_handler(request):
    """Handle incoming webhook updates"""
    try:
        data = await request.json()
        logger.debug(f"Received update: {data}")

        if "message" in data:
            message = data["message"]
            user_id = message["from"]["id"]
            username = message["from"].get("username")
            text = message.get("text", "")

            if text.startswith("/start"):
                await handle_start_command(user_id, username)
            elif text.startswith("/donate"):
                await handle_donate_command(user_id)
            elif text.startswith("/store"):
                await handle_store_command(user_id)
            elif text.startswith("/status"):
                await handle_status_command(user_id)
            elif text.startswith("/help"):
                await handle_help_command(user_id)

        elif "callback_query" in data:
            callback_query = data["callback_query"]
            user_id = callback_query["from"]["id"]
            data_text = callback_query["data"]

            await handle_callback_query(user_id, data_text)

        return web.Response(text="OK")

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(text="Error", status=500)


async def init_app():
    """Initialize web application"""
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, webhook_handler)

    # Setup NEONPAY
    await setup_neonpay()

    return app


async def main():
    """Main function"""
    logger.info("🚀 Starting NEONPAY Raw API Bot...")

    try:
        # Create web application
        app = await init_app()

        logger.info("✅ Bot initialized successfully!")
        logger.info("💰 Donation system ready!")
        logger.info("🛒 Digital store ready!")
        logger.info(f"🔄 Starting webhook server on {WEBAPP_HOST}:{WEBAPP_PORT}")

        # Start web server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
        await site.start()

        logger.info(f"🌐 Webhook server running at {WEBHOOK_URL}")
        logger.info("Press Ctrl+C to stop...")

        # Keep running
        try:
            await asyncio.Future()
        except KeyboardInterrupt:
            logger.info("👋 Bot stopped by user")

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
