import discord
from discord import app_commands
from main import WEBSITE_URL, STAFF_PANEL_URL, STAFF_ROLES

# ════════════════════════════════════════
# COMANDO ACCEDI
# ════════════════════════════════════════

@app_commands.command(name="accedi", description="Ottieni il link per accedere al sito web")
async def accedi(interaction: discord.Interaction):
    """Comando che manda il link appropriato basato sui ruoli dell'utente."""
    member = interaction.guild.get_member(interaction.user.id)

    if not member:
        await interaction.response.send_message("❌ Errore: non riesco a trovare il tuo profilo nel server.", ephemeral=True)
        return

    # Controlla se l'utente ha ruoli staff
    user_roles = [role.name for role in member.roles if role.name != "@everyone"]
    is_staff = any(role in STAFF_ROLES for role in user_roles)

    if is_staff:
        # Link per staff
        embed = discord.Embed(
            title="🔐 Accesso Staff",
            description="Hai accesso al pannello amministrativo!",
            color=0xe63030
        )
        embed.add_field(
            name="Link",
            value=f"[Clicca qui per accedere]({STAFF_PANEL_URL})",
            inline=False
        )
        embed.set_footer(text="Il Covo Del Boss - Staff Panel")
    else:
        # Link per utenti normali
        embed = discord.Embed(
            title="🌐 Accesso Sito Web",
            description="Benvenuto nel sito web della community!",
            color=0x3498db
        )
        embed.add_field(
            name="Link",
            value=f"[Clicca qui per accedere]({WEBSITE_URL})",
            inline=False
        )
        embed.set_footer(text="Il Covo Del Boss - Community")

    await interaction.response.send_message(embed=embed, ephemeral=True)


# ════════════════════════════════════════
# SETUP FUNCTION
# ════════════════════════════════════════

async def setup(bot):
    """Aggiunge il comando al bot."""
    bot.tree.add_command(accedi)