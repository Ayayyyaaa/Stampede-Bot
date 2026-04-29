import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import random
import asyncio
import datetime
from zoneinfo import ZoneInfo
import config

# ── Persistance ───────────────────────────────────────────────────────────────

def _whois_file(guild_id: int) -> str:
    return f"data/{guild_id}/whois.json"

def load_whois(guild_id: int) -> dict:
    """Returns {"players": {"PlayerName": {"wins": int, "attempts": int}}}"""
    path = _whois_file(guild_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        data = {"players": {}}
        save_whois(guild_id, data)
        return data
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        data = {"players": {}}
        save_whois(guild_id, data)
        return data

def save_whois(guild_id: int, data: dict):
    path = _whois_file(guild_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def record_attempt(guild_id: int, display_name: str, won: bool):
    data = load_whois(guild_id)
    if display_name not in data["players"]:
        data["players"][display_name] = {"wins": 0, "attempts": 0}
    data["players"][display_name]["attempts"] += 1
    if won:
        data["players"][display_name]["wins"] += 1
    save_whois(guild_id, data)


# ── Utilitaires ───────────────────────────────────────────────────────────────

WHOIS_DIR = "resources/WhoIs"

def _pick_random_image() -> tuple[str, str] | None:
    """
    Returns (character_name, file_path) picked randomly from WHOIS_DIR.
    Files must be named like:  CharacterName_something.png  or  CharacterName.png
    The character name is the part before the first underscore (or dot).
    Returns None if the folder is empty or missing.
    """
    if not os.path.isdir(WHOIS_DIR):
        return None
    files = [
        f for f in os.listdir(WHOIS_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
    ]
    if not files:
        return None

    chosen = random.choice(files)
    # Derive character name: "Toro1.png" → "Toro", "Raja12.png" → "Raja"
    name_part = os.path.splitext(chosen)[0]       # strip extension
    char_name = name_part.rstrip("0123456789").capitalize()  # "toro1" → "Toro"
    return char_name, os.path.join(WHOIS_DIR, chosen)

def _normalize(text: str) -> str:
    """Lowercase + strip for loose comparison."""
    return text.strip().lower()


# ── Vue de réponse ────────────────────────────────────────────────────────────

class WhoIsView(discord.ui.View):
    """
    Collects the first correct answer OR waits until timeout.
    The actual listening is done via on_message in the cog;
    this View only provides the Give Up button.
    """
    def __init__(self, cog: "WhoIsCog", guild_id: int, char_name: str,
                 channel_id: int, timeout: float = 30.0):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.guild_id = guild_id
        self.char_name = char_name
        self.channel_id = channel_id
        self.winner: discord.Member | None = None
        self.stopped = False

    async def on_timeout(self):
        if not self.stopped:
            self.stopped = True
            self.cog._remove_active(self.channel_id)

    @discord.ui.button(label="<a:scythe:1489283989255491594> Give Up", style=discord.ButtonStyle.secondary)
    async def give_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Only the channel participants can give up (anyone can press it → reveal answer)
        self.stopped = True
        self.stop()
        self.cog._remove_active(self.channel_id)
        embed = discord.Embed(
            title="<a:zykan:1489280289027915997> Nobody found it!",
            description=f"The answer was **{self.char_name}** {config.char_emojis.get(self.char_name, '')}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )
        await interaction.response.edit_message(embed=embed, view=None, attachments=[])


# ── Cog principal ─────────────────────────────────────────────────────────────

class WhoIsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Maps channel_id → {"char_name": str, "view": WhoIsView, "message": discord.Message}
        self._active: dict[int, dict] = {}

    def _remove_active(self, channel_id: int):
        self._active.pop(channel_id, None)

    # ── /whois ────────────────────────────────────────────────────────────────

    @app_commands.command(name="whois", description="Guess the character from a mystery image!")
    async def whois(self, interaction: discord.Interaction):
        if interaction.channel_id in self._active:
            await interaction.response.send_message(
                "❌ A WhoIs game is already running in this channel! Answer it first.",
                ephemeral=True
            )
            return

        result = _pick_random_image()
        if result is None:
            await interaction.response.send_message(
                "❌ No images found in `resources/WhoIs/`. Add some images first!",
                ephemeral=True
            )
            return

        char_name, file_path = result
        filename = os.path.basename(file_path)

        embed = discord.Embed(
            title="<a:research:1488144464835776622> Who Is This Character?",
            description=(
                "Type the character's name in the chat to answer!\n"
                f"<:notif:1496819951296839811> You have **30 seconds**.\n\n"
                "*Hint: check the tier list with `/tierlist`*"
            ),
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )
        embed.set_image(url=f"attachment://{filename}")
        embed.set_footer(text=f"Started by {interaction.user.display_name}")

        view = WhoIsView(
            cog=self,
            guild_id=interaction.guild_id,
            char_name=char_name,
            channel_id=interaction.channel_id,
            timeout=30.0
        )

        file = discord.File(file_path, filename=filename)
        await interaction.response.send_message(embed=embed, file=file, view=view)
        msg = await interaction.original_response()

        self._active[interaction.channel_id] = {
            "char_name": char_name,
            "view": view,
            "message": msg,
            "guild_id": interaction.guild_id,
        }

        # Auto-reveal after timeout
        await asyncio.sleep(30)
        if interaction.channel_id in self._active:
            # Nobody answered
            self._remove_active(interaction.channel_id)
            view.stopped = True
            view.stop()
            timeout_embed = discord.Embed(
                title="<:notif:1496819951296839811> Time's up!",
                description=f"Nobody guessed it!\nThe answer was **{char_name}** {config.char_emojis.get(char_name, '')}",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
            )
            try:
                await msg.edit(embed=timeout_embed, view=None, attachments=[])
            except discord.HTTPException:
                pass

    # ── Listener on_message ───────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        session = self._active.get(message.channel.id)
        if session is None:
            return

        guess = _normalize(message.content)
        answer = _normalize(session["char_name"])

        # Accept a few typo-tolerance: just lowercase match is enough for now
        if guess != answer:
            return

        # Correct answer!
        view: WhoIsView = session["view"]
        if view.stopped:
            return  # race condition guard

        view.stopped = True
        view.stop()
        self._remove_active(message.channel.id)

        winner = message.author
        record_attempt(session["guild_id"], winner.display_name, won=True)

        emoji = config.char_emojis.get(session["char_name"], "")
        embed = discord.Embed(
            title=f"<:announcement:1496817320440500335> {winner.display_name} found it!",
            description=f"The answer was **{session['char_name']}** {emoji}\n\n+1 point for {winner.mention} <:top1:1489297584752168990>",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )
        if winner.avatar:
            embed.set_thumbnail(url=winner.avatar.url)

        try:
            await session["message"].edit(embed=embed, view=None, attachments=[])
        except discord.HTTPException:
            pass
        await message.add_reaction("✅")

    # ── /whois_ranking ────────────────────────────────────────────────────────

    @app_commands.command(name="whois_ranking", description="Leaderboard for the WhoIs game")
    async def whois_ranking(self, interaction: discord.Interaction):
        data = load_whois(interaction.guild_id)
        players = data.get("players", {})

        if not players:
            await interaction.response.send_message(
                "<:notif:1496819951296839811> No WhoIs scores yet! Start a game with `/whois`.",
                ephemeral=True
            )
            return

        # Sort by wins desc, then win-rate desc
        sorted_players = sorted(
            players.items(),
            key=lambda kv: (kv[1]["wins"], kv[1]["wins"] / max(kv[1]["attempts"], 1)),
            reverse=True
        )

        medals = ["<:rangS:1489296503481696316>", "<:rangA:1489296517612179507>", "<:rangB:1489296532455948459>"]
        lines = []
        for i, (name, stats) in enumerate(sorted_players[:15]):
            wins = stats["wins"]
            attempts = stats["attempts"]
            rate = (wins / attempts * 100) if attempts > 0 else 0
            rank_icon = medals[i] if i < 3 else f"**#{i+1}**"
            lines.append(
                f"{rank_icon} **{name}** — {wins} win{'s' if wins != 1 else ''} "
                f"/ {attempts} attempt{'s' if attempts != 1 else ''} "
                f"(*{rate:.0f}%*)"
            )

        embed = discord.Embed(
            title="<a:research:1488144464835776622> WhoIs — Leaderboard",
            description="\n".join(lines),
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )
        embed.set_footer(text=f"Top {min(15, len(sorted_players))} players · {interaction.guild.name}")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(WhoIsCog(bot))