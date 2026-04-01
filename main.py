import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from aiohttp import web
import asyncio
from loader import start_banner, log, success, error
from database.db import Database

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "database/data.db")
OWNER_ID = 1228718740456341514
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="+",
    intents=intents,
    help_command=None
)

tree = bot.tree

# ════════════════════════════════════════
# CONFIGURAZIONE URL (esportate per i comandi)
# ════════════════════════════════════════
WEBSITE_URL = "https://ilcovodelboss.vercel.app"
STAFF_PANEL_URL = f"{WEBSITE_URL}/admin/panel"

# ════════════════════════════════════════
# RUOLI STAFF (esportati per i comandi)
# ════════════════════════════════════════
STAFF_ROLES = ['Founder', 'Co Founder', 'Manager', 'Admin', 'Supervisor', 'Coordinator']


async def load_modules(bot, folder):
    """Carica i cogs da una cartella."""
    for file in os.listdir(f"./{folder}"):
        if file.endswith(".py") and file != "__init__.py":
            try:
                await bot.load_extension(f"{folder}.{file[:-3]}")
                success(f"Caricato: {folder}/{file}")
            except Exception as e:
                error(f"Errore caricando {file}: {e}")


@bot.event
async def on_ready():
    success(f"Bot online come {bot.user}")
    guild = discord.Object(id=GUILD_ID)

    # Sincronizza i comandi slash nella guild specifica
    # I comandi vengono automaticamente limitati alla guild tramite sync(guild=guild)
    try:
        synced = await bot.tree.sync(guild=guild)
        success(f"Slash commands sincronizzati nella guild ({len(synced)} comandi)")
    except Exception as e:
        error(f"Errore sincronizzazione guild-specific: {e}")
        # Fallback: sincronizza globalmente
        synced = await bot.tree.sync()
        success(f"Slash commands sincronizzati globalmente ({len(synced)} comandi)")


# ════════════════════════════════════════
# COMANDO ACCEDI (ora in commands/accedi.py)
# ════════════════════════════════════════
# Il comando /accedi è stato spostato nel file commands/accedi.py


# ════════════════════════════════════════
# ENDPOINT WEB API
# ════════════════════════════════════════

async def member_roles(request):
    """Restituisce i ruoli di un utente Discord."""
    user_id = request.query.get('user_id')
    auth_header = request.headers.get('Authorization', '')
    
    token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
    
    if not token or not user_id:
        return web.json_response({'error': 'Missing parameters'}, status=400)
    
    try:
        user_id_int = int(user_id)
        guild = bot.get_guild(GUILD_ID)
        member = guild.get_member(user_id_int)
        
        if not member:
            return web.json_response({'roles': []}, status=200)
        
        roles = [role.name for role in member.roles if role.name != "@everyone"]
        return web.json_response({'roles': roles}, status=200)
    except Exception as e:
        error(f"Errore endpoint: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def start_web_server():
    """Avvia il server web sulla porta specificata."""
    port = int(os.getenv("WEB_PORT", "8080"))  # Default 8080, ma puoi cambiarlo con env var
    app = web.Application()
    app.router.add_get('/api/member-roles', member_roles)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    success(f"Web server avviato su 0.0.0.0:{port}")


async def main():
    start_banner()

    log("Connessione al database...")
    Database().connect()
    success("Database connesso")

    log("Caricamento commands...")
    await load_modules(bot, "commands")

    log("Caricamento messageCommands...")
    await load_modules(bot, "messageCommands")

    log("Caricamento eventi...")
    await load_modules(bot, "events")

    log("Avvio web server API...")
    await start_web_server()

    log("Avvio bot...")
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())