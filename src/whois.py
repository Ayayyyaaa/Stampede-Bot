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
TIMEOUT_SECONDS = 30

def _pick_random_image() -> tuple[str, str] | None:
    """
    Returns (character_name, file_path) picked randomly from WHOIS_DIR.
    Files are named like: toro1.png, baron12.png → name = strip digits + capitalize.
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
    name_part = os.path.splitext(chosen)[0]                          # "toro1"
    char_name = name_part.rstrip("0123456789").capitalize()          # "Toro"
    return char_name, os.path.join(WHOIS_DIR, chosen)

def _normalize(text: str) -> str:
    return text.strip().lower()


# ── Modal de réponse ──────────────────────────────────────────────────────────

class AnswerModal(discord.ui.Modal, title="Who is this character?"):
    answer = discord.ui.TextInput(
        label="Character name",
        placeholder="Type the character's name here...",
        min_length=1,
        max_length=50
    )

    def __init__(self, view: "WhoIsView"):
        super().__init__()
        self.whois_view = view

    async def on_submit(self, interaction: discord.Interaction):
        guess = _normalize(self.answer.value)
        correct = _normalize(self.whois_view.char_name)

        if self.whois_view.stopped:
            await interaction.response.send_message(
                "⏰ Too late, the game already ended!", ephemeral=True
            )
            return

        if guess != correct:
            await interaction.response.send_message(
                f"❌ **{self.answer.value}** is not the right answer, try again!",
                ephemeral=True
            )
            return

        # Correct!
        self.whois_view.stopped = True
        self.whois_view.stop()
        if self.whois_view.timeout_task:
            self.whois_view.timeout_task.cancel()
        self.whois_view.cog._remove_active(self.whois_view.channel_id)

        winner = interaction.user
        record_attempt(self.whois_view.guild_id, winner.display_name, won=True)

        emoji = config.char_emojis.get(self.whois_view.char_name, "")
        embed = discord.Embed(
            title=f"<:announcement:1496817320440500335> {winner.display_name} found it!",
            description=(
                f"The answer was **{self.whois_view.char_name}** {emoji}\n\n"
                f"+1 point for {winner.mention} <:top1:1489297584752168990>"
            ),
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )
        if winner.avatar:
            embed.set_thumbnail(url=winner.avatar.url)

        await interaction.response.edit_message(embed=embed, view=None, attachments=[])


# ── Vue principale ────────────────────────────────────────────────────────────

class WhoIsView(discord.ui.View):
    def __init__(self, cog: "WhoIsCog", guild_id: int, char_name: str, channel_id: int):
        super().__init__(timeout=None)   # timeout handled manually via task
        self.cog = cog
        self.guild_id = guild_id
        self.char_name = char_name
        self.channel_id = channel_id
        self.stopped = False
        self.timeout_task: asyncio.Task | None = None
        self.message: discord.Message | None = None

    @discord.ui.button(label="Answer", style=discord.ButtonStyle.primary, emoji="🔍")
    async def answer_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.stopped:
            await interaction.response.send_message("⏰ The game already ended!", ephemeral=True)
            return
        await interaction.response.send_modal(AnswerModal(self))

    @discord.ui.button(label="Give Up", style=discord.ButtonStyle.secondary, emoji="🏳️")
    async def give_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.stopped:
            await interaction.response.send_message("⏰ The game already ended!", ephemeral=True)
            return
        self.stopped = True
        self.stop()
        if self.timeout_task:
            self.timeout_task.cancel()
        self.cog._remove_active(self.channel_id)

        embed = discord.Embed(
            title="😔 Nobody found it!",
            description=f"The answer was **{self.char_name}** {config.char_emojis.get(self.char_name, '')}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )
        await interaction.response.edit_message(embed=embed, view=None, attachments=[])


# ── Cog principal ─────────────────────────────────────────────────────────────

class WhoIsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._active: dict[int, dict] = {}

    def _remove_active(self, channel_id: int):
        self._active.pop(channel_id, None)

    async def _run_timeout(self, view: WhoIsView, char_name: str):
        """Waits TIMEOUT_SECONDS then reveals the answer if nobody guessed."""
        await asyncio.sleep(TIMEOUT_SECONDS)
        if view.stopped:
            return
        view.stopped = True
        view.stop()
        self._remove_active(view.channel_id)

        embed = discord.Embed(
            title="<:notif:1496819951296839811> Time's up!",
            description=(
                f"Nobody guessed it!\n"
                f"The answer was **{char_name}** {config.char_emojis.get(char_name, '')}"
            ),
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )
        try:
            await view.message.edit(embed=embed, view=None, attachments=[])
        except discord.HTTPException:
            pass

    # ── /whois ────────────────────────────────────────────────────────────────

    @app_commands.command(name="whois", description="Guess the character from a mystery image!")
    async def whois(self, interaction: discord.Interaction):
        if interaction.channel_id in self._active:
            await interaction.response.send_message(
                "❌ A WhoIs game is already running in this channel! Finish it first.",
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
                "Click **Answer** and type the character's name!\n"
                f"<:notif:1496819951296839811> You have **{TIMEOUT_SECONDS} seconds**.\n\n"
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
        )

        file = discord.File(file_path, filename=filename)
        await interaction.response.send_message(embed=embed, file=file, view=view)
        msg = await interaction.original_response()
        view.message = msg

        self._active[interaction.channel_id] = {
            "char_name": char_name,
            "view": view,
            "guild_id": interaction.guild_id,
        }

        # Start timeout as a background task (doesn't block the command)
        task = asyncio.create_task(self._run_timeout(view, char_name))
        view.timeout_task = task

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