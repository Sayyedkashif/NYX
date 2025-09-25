
import os
import asyncio
import logging
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import Database
from config import Config
from filters import Filter
from rename import RenameHandler
from webupload import WebUploader
from admin import AdminHandler
from utils import Utils

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MovieBot:
    def __init__(self):
        self.app = Client(
            "MovieBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN
        )
        self.db = Database()
        self.filter_handler = Filter(self.db)
        self.rename_handler = RenameHandler()
        self.web_uploader = WebUploader()
        self.admin_handler = AdminHandler(self.db)
        self.utils = Utils()

    async def start(self):
        await self.app.start()
        await self.db.connect()
        logger.info("ðŸš€ Movie Bot à¤¶à¥à¤°à¥‚ à¤¹à¥‹ à¤—à¤¯à¤¾!")

        # Register handlers
        self.register_handlers()

        # Keep running
        await asyncio.Event().wait()

    def register_handlers(self):
        """Register all bot handlers"""

        # Start command
        @self.app.on_message(filters.command("start"))
        async def start_command(client, message):
            user_id = message.from_user.id
            first_name = message.from_user.first_name

            # Add user to database
            await self.db.add_user(user_id, message.from_user.username, first_name)

            start_text = f"""
ðŸŽ¬ **Advanced Movie Bot à¤®à¥‡ à¤†à¤ªà¤•à¤¾ à¤¸à¥à¤µà¤¾à¤—à¤¤ à¤¹à¥ˆ!** ðŸŽ¬

à¤¨à¤®à¤¸à¥à¤•à¤¾à¤° {first_name}! 

**âœ¨ Bot à¤•à¥‡ Features:**
ðŸ” **Smart Search** - Movie name type à¤•à¤°à¥‡à¤‚
ðŸ“ **File Rename** - Files à¤•à¥‹ rename à¤•à¤°à¥‡à¤‚  
ðŸŒ **Web Download** - Direct download links
ðŸ‘‘ **Power Results** - Beautiful movie cards
ðŸŽ¯ **Auto Filter** - Instant results

**ðŸš€ Commands:**
â€¢ Movie name à¤­à¥‡à¤œà¥‡à¤‚ (Example: Kill, Avengers)
â€¢ /rename - File rename à¤•à¤°à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤
â€¢ /help - Complete help
â€¢ /stats - Bot statistics

**ðŸŽ¥ à¤…à¤­à¥€ à¤•à¥‹à¤ˆ movie search à¤•à¤°à¥‡à¤‚!**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ¤– **Powered by Advanced Movie Bot**
            """

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("ðŸ” Search Movies", switch_inline_query_current_chat=""),
                    InlineKeyboardButton("ðŸ“š Help", callback_data="help")
                ],
                [
                    InlineKeyboardButton("ðŸ‘¨â€ðŸ’» Developer", url="https://t.me/YourUsername"),
                    InlineKeyboardButton("ðŸ“¢ Updates", url="https://t.me/YourChannel")
                ]
            ])

            await message.reply_text(start_text, reply_markup=keyboard)

        # Help command  
        @self.app.on_message(filters.command("help"))
        async def help_command(client, message):
            help_text = """
ðŸ“‹ **Movie Bot Complete Guide**

**ðŸŽ¬ Movie Search à¤•à¤°à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤:**
â€¢ Direct movie name type à¤•à¤°à¥‡à¤‚
â€¢ Keywords à¤­à¥€ use à¤•à¤° à¤¸à¤•à¤¤à¥‡ à¤¹à¥ˆà¤‚
â€¢ English à¤¯à¤¾ Hindi à¤¦à¥‹à¤¨à¥‹à¤‚ à¤®à¥‡à¤‚ search à¤•à¤°à¥‡à¤‚

**ðŸ“ File Features:**
â€¢ `/rename` - Files à¤•à¥‹ rename à¤•à¤°à¥‡à¤‚
â€¢ Auto file type detection
â€¢ Web download links à¤®à¤¿à¤²à¤¤à¥€ à¤¹à¥ˆà¤‚

**ðŸ‘‘ Power Features:**
â€¢ Smart search results  
â€¢ Beautiful movie cards
â€¢ File size à¤”à¤° quality info
â€¢ Direct download buttons

**âš¡ Quick Tips:**
â€¢ Movie name correctly spell à¤•à¤°à¥‡à¤‚
â€¢ Popular movies fast à¤®à¤¿à¤²à¤¤à¥€ à¤¹à¥ˆà¤‚
â€¢ Multiple results à¤®à¤¿à¤²à¤¨à¥‡ à¤ªà¤° select à¤•à¤°à¥‡à¤‚

**ðŸ‘¨â€ðŸ’» Admin Commands:**
â€¢ `/broadcast` - Message send à¤•à¤°à¥‡à¤‚
â€¢ `/stats` - Complete bot stats
â€¢ `/addmovie` - New movie add à¤•à¤°à¥‡à¤‚

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ¤– **Advanced Movie Bot** - Made with â¤ï¸
            """

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("ðŸ  Main Menu", callback_data="start")]
            ])

            await message.reply_text(help_text, reply_markup=keyboard)

        # Stats command
        @self.app.on_message(filters.command("stats"))
        async def stats_command(client, message):
            stats = await self.admin_handler.get_stats()
            stats_text = f"""
ðŸ“Š **Bot Statistics - Power Stats** ðŸ‘‘

ðŸŽ¬ **Total Movies:** `{stats['total_movies']:,}`
ðŸ‘¥ **Total Users:** `{stats['total_users']:,}`  
ðŸ“ˆ **Today's Downloads:** `{stats['today_downloads']:,}`
âš¡ **Active Channels:** `{stats['active_channels']}`

ðŸ“… **Bot Status:** Online âœ…
ðŸ• **Last Updated:** `{datetime.now().strftime('%d/%m/%Y %I:%M %p')}`

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
**ðŸ† Power Badge Enabled!**
ðŸš€ **High Performance Mode Active**

ðŸ¤– **Advanced Movie Bot** - Statistics
            """

            await message.reply_text(stats_text)

        # Movie search handler (main feature)
        @self.app.on_message(filters.text & ~filters.command(['start', 'help', 'stats', 'rename', 'broadcast', 'addmovie']))
        async def movie_search(client, message):
            user_id = message.from_user.id
            query = message.text.strip()

            if len(query) < 2:
                await message.reply_text("âŒ à¤•à¤® à¤¸à¥‡ à¤•à¤® 2 characters à¤•à¤¾ movie name à¤¦à¥‡à¤‚!")
                return

            # Add user if not exists
            await self.db.add_user(user_id, message.from_user.username, message.from_user.first_name)

            # Show searching message
            search_msg = await message.reply_text(f"ðŸ” '{query}' à¤•à¥‹ search à¤•à¤° à¤°à¤¹à¤¾ à¤¹à¥‚à¤...")

            # Search in database
            results = await self.filter_handler.search_movies(query)

            if not results:
                await search_msg.edit_text(
                    f"âŒ '{query}' à¤¨à¤¹à¥€à¤‚ à¤®à¤¿à¤²à¥€!\n\n"
                    "ðŸ’¡ **Tips:**\n"
                    "â€¢ Correct spelling check à¤•à¤°à¥‡à¤‚\n"
                    "â€¢ Different keywords try à¤•à¤°à¥‡à¤‚\n"
                    "â€¢ English name à¤­à¥€ try à¤•à¤°à¥‡à¤‚"
                )
                return

            # Delete searching message
            await search_msg.delete()

            # Create power results with badge
            if len(results) == 1:
                await self.send_single_movie(message, results[0], query)
            else:
                await self.send_multiple_movies(message, results, query)

        # Callback query handler
        @self.app.on_callback_query()
        async def callback_handler(client, callback_query: CallbackQuery):
            data = callback_query.data

            if data == "help":
                await help_command(client, callback_query.message)
            elif data == "start":
                await start_command(client, callback_query.message)
            elif data.startswith("movie_"):
                movie_id = data.split("_")[1]
                movie = await self.db.get_movie_by_id(movie_id)
                if movie:
                    await self.send_movie_file(callback_query, movie)
            elif data.startswith("rename_"):
                file_id = data.split("_")[1]
                await self.rename_handler.start_rename_process(callback_query, file_id)
            elif data.startswith("download_"):
                file_id = data.split("_")[1]
                download_link = await self.web_uploader.create_download_link(file_id)
                await callback_query.answer(f"ðŸŒ Download Link: {download_link}", show_alert=True)

        # Admin commands
        @self.app.on_message(filters.command("broadcast") & filters.user(Config.ADMIN_IDS))
        async def broadcast_command(client, message):
            await self.admin_handler.handle_broadcast(message)

        @self.app.on_message(filters.command("addmovie") & filters.user(Config.ADMIN_IDS))
        async def add_movie_command(client, message):
            await self.admin_handler.handle_add_movie(message)

        # File rename command
        @self.app.on_message(filters.command("rename"))
        async def rename_command(client, message):
            await self.rename_handler.handle_rename_command(message)

    async def send_single_movie(self, message, movie, query):
        """Send single movie with power badge"""

        power_badge = f"""
ðŸ† **Power Result Found!** ðŸ†
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
        """

        movie_card = f"""
{power_badge}

ðŸŽ¬ **{movie['name']}**
ðŸ“… **Year:** {movie.get('year', 'N/A')}
ðŸŽ­ **Genre:** {movie.get('genre', 'N/A')}
ðŸ“Š **Size:** {movie.get('size', 'N/A')}
ðŸ“ **Quality:** {movie.get('quality', 'HD')}
â­ **Rating:** {movie.get('rating', 'N/A')}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
        """

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("ðŸ“¥ Download File", callback_data=f"movie_{movie['_id']}"),
                InlineKeyboardButton("ðŸŒ Web Download", callback_data=f"download_{movie['file_id']}")
            ],
            [
                InlineKeyboardButton("âœï¸ Rename File", callback_data=f"rename_{movie['file_id']}"),
                InlineKeyboardButton("ðŸ” More Movies", switch_inline_query_current_chat="")
            ]
        ])

        await message.reply_text(movie_card, reply_markup=keyboard)

    async def send_multiple_movies(self, message, movies, query):
        """Send multiple movies with power badge"""

        total_movies = len(movies)

        power_header = f"""
ðŸ† **{total_movies} Power Results Found!** ðŸ†
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ” **Search:** "{query}"
ðŸ“Š **Total Results:** {total_movies}
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
        """

        # Create keyboard with movie options
        keyboard = []
        for i, movie in enumerate(movies[:10]):  # Limit to 10 results
            movie_text = f"ðŸŽ¬ {movie['name']} â€¢ {movie.get('size', 'N/A')}"
            keyboard.append([InlineKeyboardButton(movie_text, callback_data=f"movie_{movie['_id']}")])

        # Add navigation buttons
        keyboard.append([
            InlineKeyboardButton("ðŸ” New Search", switch_inline_query_current_chat=""),
            InlineKeyboardButton("ðŸ“Š All Results", callback_data="show_all")
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await message.reply_text(power_header + "**Select your movie:**", reply_markup=reply_markup)

    async def send_movie_file(self, callback_query, movie):
        """Send movie file to user"""
        try:
            file_caption = f"""
ðŸŽ¬ **{movie['name']}**
ðŸ“Š **Size:** {movie.get('size', 'N/A')}
ðŸŽ­ **Genre:** {movie.get('genre', 'N/A')}
â­ **Quality:** {movie.get('quality', 'HD')}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ¤– **@YourMovieBotUsername**
            """

            # Create download options keyboard
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("âœï¸ Rename File", callback_data=f"rename_{movie['file_id']}"),
                    InlineKeyboardButton("ðŸŒ Web Download", callback_data=f"download_{movie['file_id']}")
                ]
            ])

            # Send file based on type
            if movie['file_type'] == 'document':
                await callback_query.message.reply_document(
                    movie['file_id'],
                    caption=file_caption,
                    reply_markup=keyboard
                )
            elif movie['file_type'] == 'video':
                await callback_query.message.reply_video(
                    movie['file_id'],
                    caption=file_caption,
                    reply_markup=keyboard
                )

            # Update download count
            await self.db.update_download_count(movie['_id'])

            await callback_query.answer("âœ… Movie file sent successfully!")

        except Exception as e:
            logger.error(f"Error sending movie file: {e}")
            await callback_query.answer("âŒ File send à¤•à¤°à¤¨à¥‡ à¤®à¥‡à¤‚ error à¤†à¤ˆ!", show_alert=True)

# Run bot
if __name__ == "__main__":
    bot = MovieBot()
    asyncio.run(bot.start())
