import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import datetime
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import numpy as np
from io import BytesIO
import config


def _data_file(guild_id: int) -> str:
    return f"data/{guild_id}/scores.json"

def _members_file(guild_id: int) -> str:
    return f"data/{guild_id}/members.json"


def load_data(guild_id: int) -> dict:
    path = _data_file(guild_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        save_data(guild_id, {"events": []})
        return {"events": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "events" not in data:
            raise ValueError("Invalid structure")
        return data
    except (json.JSONDecodeError, ValueError):
        backup = path + ".bak"
        if os.path.exists(path):
            os.replace(path, backup)
        save_data(guild_id, {"events": []})
        return {"events": []}

def save_data(guild_id: int, data: dict):
    path = _data_file(guild_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Données membres ───────────────────────────────────────────────────────────

def load_members(guild_id: int) -> list:
    path = _members_file(guild_id)
    if not os.path.exists(path):
        save_members(guild_id, [])
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("members", [])
    except:
        return []

def save_members(guild_id: int, members: list):
    path = _members_file(guild_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"members": sorted(members)}, f, ensure_ascii=False, indent=2)


# ── Utilitaires ───────────────────────────────────────────────────────────────

def get_guild_config(interaction: discord.Interaction) -> dict | None:
    """Récupère la config du serveur et répond en erreur si inconnu."""
    return config.GUILDS.get(interaction.guild_id)

def find_event(data: dict, event_type: str, date_str: str) -> dict | None:
    for event in data["events"]:
        if event["type"] == event_type and event["date"] == date_str:
            return event
    return None


# ── Graphiques ────────────────────────────────────────────────────────────────

COLORS = {
    "smash": "#f59e0b",
    "mechs": "#ef4444",
    "grid":  "#2a2a3e",
    "bg":    "#0f0f1a",
    "panel": "#1a1a2e",
    "text":  "#e2e8f0",
    "accent":"#818cf8",
}

TYPE_LABEL = {"smash": "Smash", "mechs": "Mechs"}

def _setup_dark_fig(w=12, h=6):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["panel"])
    ax.tick_params(colors=COLORS["text"])
    ax.xaxis.label.set_color(COLORS["text"])
    ax.yaxis.label.set_color(COLORS["text"])
    ax.title.set_color(COLORS["text"])
    for spine in ax.spines.values():
        spine.set_edgecolor(COLORS["grid"])
    ax.grid(axis="y", color=COLORS["grid"], linestyle="--", linewidth=0.7, alpha=0.6)
    return fig, ax

def _buf(fig) -> BytesIO:
    buf = BytesIO()
    fig.tight_layout(pad=2)
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf


def chart_club_evolution(data: dict, event_type: str | None = None) -> BytesIO:
    events = data["events"]
    if event_type:
        events = [e for e in events if e["type"] == event_type]
    events = sorted(events, key=lambda e: e["date"])

    if not events:
        raise ValueError("Event not found")

    dates = [e["date"] for e in events]
    totals = [sum(e["scores"].values()) for e in events]
    colors = [COLORS["smash"] if e["type"] == "smash" else COLORS["mechs"] for e in events]

    fig, ax = _setup_dark_fig(12, 5)
    ax.fill_between(range(len(dates)), totals, alpha=0.15, color=COLORS["accent"])
    ax.plot(range(len(dates)), totals, color=COLORS["accent"], linewidth=2.5, zorder=3)
    ax.scatter(range(len(dates)), totals, c=colors, s=90, zorder=4, edgecolors="white", linewidth=0.8)
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels([f"{e['date']}\n{TYPE_LABEL[e['type']]}" for e in events],
                       fontsize=8, color=COLORS["text"])
    ax.set_ylabel("Total score", color=COLORS["text"])
    title = "Changes in the club's total score"
    if event_type:
        title += f"  —  {TYPE_LABEL[event_type]}"
    ax.set_title(title, fontsize=13, fontweight="bold", color=COLORS["text"], pad=12)
    for i, v in enumerate(totals):
        ax.annotate(f"{v:,}", (i, v), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8, color=COLORS["text"])
    return _buf(fig)


def chart_player_evolution(data: dict, player: str, event_type: str | None = None) -> BytesIO:
    events = data["events"]
    if event_type:
        events = [e for e in events if e["type"] == event_type]
    events = sorted(events, key=lambda e: e["date"])

    dates, scores = [], []
    for e in events:
        if player in e["scores"]:
            dates.append(f"{e['date']}\n{TYPE_LABEL[e['type']]}")
            scores.append(e["scores"][player])

    if not scores:
        raise ValueError(f"No score found for **{player}**.")

    fig, ax = _setup_dark_fig(11, 5)
    col = COLORS["smash"] if event_type == "smash" else (COLORS["mechs"] if event_type == "mechs" else COLORS["accent"])
    ax.fill_between(range(len(dates)), scores, alpha=0.2, color=col)
    ax.plot(range(len(dates)), scores, color=col, linewidth=2.5, marker="o",
            markersize=8, markeredgecolor="white", markeredgewidth=0.8, zorder=3)
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(dates, fontsize=8, color=COLORS["text"])
    ax.set_ylabel("Score", color=COLORS["text"])
    title = f"Changes in the {player} score"
    if event_type:
        title += f"  —  {TYPE_LABEL[event_type]}"
    ax.set_title(title, fontsize=13, fontweight="bold", color=COLORS["text"], pad=12)
    for i, v in enumerate(scores):
        ax.annotate(f"{v:,}", (i, v), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8, color=COLORS["text"])
    avg = np.mean(scores)
    ax.axhline(avg, color="white", linestyle=":", linewidth=1.2, alpha=0.5)
    ax.annotate(f"moy. {avg:,.0f}", xy=(len(scores) - 1, avg),
                xytext=(-40, 5), textcoords="offset points",
                fontsize=8, color="white", alpha=0.7)
    return _buf(fig)


def chart_average_per_player(data: dict, guild_id: int, event_type: str | None = None) -> BytesIO:
    events = data["events"]
    if event_type:
        events = [e for e in events if e["type"] == event_type]

    if not events:
        label = f" of type **{TYPE_LABEL[event_type]}**" if event_type else ""
        raise ValueError(f"No event found{label}. Create one first with `/add_event`.")

    members = load_members(guild_id)
    player_scores: dict[str, list] = {}
    for e in events:
        for player, score in e["scores"].items():
            if player in members:
                player_scores.setdefault(player, []).append(score)

    if not player_scores:
        label = f" for **{TYPE_LABEL[event_type]}**" if event_type else ""
        raise ValueError(f"No scores registered yet{label}. Add scores with `/add_scores`.")

    averages = {p: np.mean(s) for p, s in player_scores.items()}
    averages = dict(sorted(averages.items(), key=lambda x: x[1], reverse=True))

    players = list(averages.keys())
    values = list(averages.values())

    fig, ax = _setup_dark_fig(max(10, len(players) * 0.9 + 2), 5)
    bar_colors = [COLORS["accent"]] * len(players)
    if values:
        bar_colors[0] = COLORS["smash"]
    bars = ax.bar(players, values, color=bar_colors, width=0.6,
                  edgecolor="white", linewidth=0.4, zorder=2)
    ax.set_ylabel("Average score", color=COLORS["text"])
    title = "Average score per player"
    if event_type:
        title += f"  —  {TYPE_LABEL[event_type]}"
    ax.set_title(title, fontsize=13, fontweight="bold", color=COLORS["text"], pad=12)
    ax.set_xticks(range(len(players)))
    ax.set_xticklabels(players, rotation=30, ha="right", fontsize=9, color=COLORS["text"])
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.01,
                f"{val:,.0f}", ha="center", va="bottom", fontsize=8, color=COLORS["text"])
    return _buf(fig)


# ── Cog ───────────────────────────────────────────────────────────────────────

class ScoresCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _check_guild(self, interaction: discord.Interaction) -> dict | None:
        """Vérifie que le serveur est configuré et répond en erreur sinon."""
        gc = config.GUILDS.get(interaction.guild_id)
        if not gc:
            await interaction.response.send_message(
                "❌ This server is not configured.", ephemeral=True)
        return gc

    @app_commands.command(name="add_event", description="Add an event (smash/mechs) with a date")
    @app_commands.describe(
        event_type="Type of event",
        date="Date of the event (YYYY-MM-DD format)",
        description="Optional description of the event"
    )
    @app_commands.choices(event_type=[
        Choice(name="Smash", value="smash"),
        Choice(name="Mechs", value="mechs"),
    ])
    async def add_event(self, interaction: discord.Interaction,
                        event_type: str, date: str, description: str = ""):
        gc = await self._check_guild(interaction)
        if not gc:
            return
        if not any(r.id == gc["COLEAD"] for r in interaction.user.roles):
            await interaction.response.send_message("❌ You don't have the permissions to do that", ephemeral=True)
            return

        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid date format. Use **YYYY-MM-DD** (ex: 2025-07-18).", ephemeral=True)
            return

        data = load_data(interaction.guild_id)
        if find_event(data, event_type, date):
            await interaction.response.send_message(
                f"⚠️ An event **{TYPE_LABEL[event_type]}** already exists for the **{date}**.", ephemeral=True)
            return

        data["events"].append({
            "type": event_type,
            "date": date,
            "description": description,
            "scores": {}
        })
        save_data(interaction.guild_id, data)

        embed = discord.Embed(
            title=f"{TYPE_LABEL[event_type]} — Event added !",
            description=f"<:calendar:1496816276780224512> **Date :** {date}\n<:usefull:1488294635519479918> **Description :** {description or '—'}",
            color=discord.Color.from_str(COLORS["smash"] if event_type == "smash" else COLORS["mechs"]),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Added by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="add_scores", description="Add scores for the whole club at once — format: Player1:score1, Player2:score2, ...")
    @app_commands.describe(
        event_type="Event type",
        date="Date of the event (YYYY-MM-DD format)",
        scores="Scores in the format: Player1:score1, Player2:score2, ..."
    )
    @app_commands.choices(event_type=[
        Choice(name="Smash", value="smash"),
        Choice(name="Mechs", value="mechs"),
    ])
    async def add_scores(self, interaction: discord.Interaction,
                         event_type: str, date: str, scores: str):
        gc = await self._check_guild(interaction)
        if not gc:
            return
        if not any(r.id in (gc["COLEAD"], gc["MEMBER"]) for r in interaction.user.roles):
            await interaction.response.send_message("❌ You don't have the permission to do that.", ephemeral=True)
            return

        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid date format. Use **YYYY-MM-DD**.", ephemeral=True)
            return

        parsed = {}
        errors = []
        for entry in scores.split(","):
            entry = entry.strip()
            if not entry:
                continue
            if ":" not in entry:
                errors.append(f"`{entry}` — missing `:` separator")
                continue
            parts = entry.rsplit(":", 1)
            player_name = parts[0].strip()
            score_str = parts[1].strip().replace(" ", "").replace("\u202f", "").replace("\u00a0", "")
            if not player_name:
                errors.append(f"`{entry}` — empty player name")
                continue
            try:
                parsed[player_name] = int(score_str)
            except ValueError:
                errors.append(f"`{entry}` — `{score_str}` is not a valid number")

        if not parsed:
            msg = "❌ No valid entries found.\nExpected format: `Player1:score1, Player2:score2, ...`"
            if errors:
                msg += "\n\n**Errors:**\n" + "\n".join(errors)
            await interaction.response.send_message(msg, ephemeral=True)
            return

        data = load_data(interaction.guild_id)
        event = find_event(data, event_type, date)
        if not event:
            await interaction.response.send_message(
                f"❌ No events **{TYPE_LABEL[event_type]}** found for **{date}**.\n"
                "First, create it using `/add_event`.", ephemeral=True)
            return

        added, updated = [], []
        for player_name, score in parsed.items():
            if player_name in event["scores"]:
                updated.append((player_name, event["scores"][player_name], score))
            else:
                added.append((player_name, score))
            event["scores"][player_name] = score

        save_data(interaction.guild_id, data)
        total = sum(event["scores"].values())

        embed = discord.Embed(
            title=f"<:announcement:1496817320440500335> Club scores saved — {TYPE_LABEL[event_type]} · {date}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        if added:
            lines = "\n".join(f"**{p}** → {s:,}" for p, s in added)
            if len(lines) > 1024:
                lines = lines[:1020] + "\n..."
            embed.add_field(name=f"<a:terryx:1489284057920573660> Added ({len(added)})", value=lines, inline=False)
        if updated:
            lines = "\n".join(f"**{p}** → {new:,} *(was {old:,})*" for p, old, new in updated)
            if len(lines) > 1024:
                lines = lines[:1020] + "\n..."
            embed.add_field(name=f"<:optis:1488294635519479918> Updated ({len(updated)})", value=lines, inline=False)
        if errors:
            embed.add_field(name=f"⚠️ Skipped ({len(errors)})", value="\n".join(errors)[:1024], inline=False)
        embed.add_field(
            name="<:top1:1489297584752168990> Club total",
            value=f"{total:,}  ·  {len(event['scores'])} players registered",
            inline=False
        )
        embed.set_footer(text=f"By {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear_scores", description="Deletes **ALL** saved events and scores")
    async def clear_scores(self, interaction: discord.Interaction):
        gc = await self._check_guild(interaction)
        if not gc:
            return
        if not any(r.id == gc["COLEAD"] for r in interaction.user.roles):
            await interaction.response.send_message("❌ Only co-leads can do that.", ephemeral=True)
            return
        save_data(interaction.guild_id, {"events": []})
        await interaction.response.send_message("<:notif:1496819951296839811> **The scores database has been reset.** All events have been deleted.")


    @app_commands.command(name="member_add", description="Add one or more members to the club — format: Player1, Player2, ...")
    @app_commands.describe(noms="Member name(s), separated by commas")
    async def member_add(self, interaction: discord.Interaction, noms: str):
        gc = await self._check_guild(interaction)
        if not gc:
            return
        if not any(r.id == gc["COLEAD"] for r in interaction.user.roles):
            await interaction.response.send_message("❌ You don't have the permissions to do that", ephemeral=True)
            return

        members = load_members(interaction.guild_id)
        added, already = [], []
        for nom in noms.split(","):
            nom = nom.strip()
            if not nom:
                continue
            if nom in members:
                already.append(nom)
            else:
                members.append(nom)
                added.append(nom)

        if added:
            save_members(interaction.guild_id, members)

        embed = discord.Embed(
            title="Club membership update",
            color=discord.Color.green() if added else discord.Color.orange(),
            timestamp=datetime.datetime.now()
        )
        if added:
            embed.add_field(name=f"✅ Added ({len(added)})", value=", ".join(f"**{n}**" for n in added), inline=False)
        if already:
            embed.add_field(name=f"⚠️ Already in the club ({len(already)})", value=", ".join(f"**{n}**" for n in already), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="member_remove", description="Remove a player from the members' list")
    async def member_remove(self, interaction: discord.Interaction, nom: str):
        gc = await self._check_guild(interaction)
        if not gc:
            return
        if not any(r.id == gc["COLEAD"] for r in interaction.user.roles):
            await interaction.response.send_message("❌ Only co-leads can do that.", ephemeral=True)
            return
        members = load_members(interaction.guild_id)
        if nom not in members:
            await interaction.response.send_message(f"❌ {nom} is not on the list.")
            return
        members.remove(nom)
        save_members(interaction.guild_id, members)
        await interaction.response.send_message(f"<a:nyx:1489283483376292004> **{nom}** has been expelled from the club.")

    @app_commands.command(name="member_list", description="Displays the list of current members")
    async def member_list(self, interaction: discord.Interaction):
        members = load_members(interaction.guild_id)
        if not members:
            await interaction.response.send_message("The list is empty.")
            return
        await interaction.response.send_message(f"<:players:1496861469583867987> **Club members ({len(members)}) :**\n" + ", ".join(members))

    @app_commands.command(name="scores_club", description="Chart: Change in the club's total score")
    @app_commands.describe(event_type="Filter by type (optional)")
    @app_commands.choices(event_type=[
        Choice(name="All events", value="all"),
        Choice(name="Smash", value="smash"),
        Choice(name="Mechs", value="mechs"),
    ])
    async def scores_club(self, interaction: discord.Interaction, event_type: str = "all"):
        await interaction.response.defer()
        data = load_data(interaction.guild_id)
        try:
            buf = chart_club_evolution(data, None if event_type == "all" else event_type)
        except ValueError as e:
            await interaction.followup.send(f"❌ {e}", ephemeral=True)
            return
        file = discord.File(buf, filename="scores_club.png")
        embed = discord.Embed(title="<a:research:1488144464835776622> Changes in the club's total score", color=discord.Color.blurple())
        embed.set_image(url="attachment://scores_club.png")
        await interaction.followup.send(embed=embed, file=file)

    @app_commands.command(name="scores_player", description="Chart: a player's score over time")
    @app_commands.describe(player="Player's name", event_type="Filter by type (optional)")
    @app_commands.choices(event_type=[
        Choice(name="All events", value="all"),
        Choice(name="Smash", value="smash"),
        Choice(name="Mechs", value="mechs"),
    ])
    async def scores_player(self, interaction: discord.Interaction, player: str, event_type: str = "all"):
        await interaction.response.defer()
        data = load_data(interaction.guild_id)
        try:
            buf = chart_player_evolution(data, player, None if event_type == "all" else event_type)
        except ValueError as e:
            await interaction.followup.send(f"❌ {e}", ephemeral=True)
            return
        file = discord.File(buf, filename="scores_player.png")
        embed = discord.Embed(title=f"<a:research:1488144464835776622> Changes of {player} score", color=discord.Color.blurple())
        embed.set_image(url="attachment://scores_player.png")
        await interaction.followup.send(embed=embed, file=file)

    @app_commands.command(name="scores_average", description="Chart: average score for each player")
    @app_commands.describe(event_type="Filter by type (optional)")
    @app_commands.choices(event_type=[
        Choice(name="All events", value="all"),
        Choice(name="Smash", value="smash"),
        Choice(name="Mechs", value="mechs"),
    ])
    async def scores_average(self, interaction: discord.Interaction, event_type: str = "all"):
        await interaction.response.defer()
        data = load_data(interaction.guild_id)
        try:
            buf = chart_average_per_player(data, interaction.guild_id, None if event_type == "all" else event_type)
        except ValueError as e:
            await interaction.followup.send(f"❌ {e}", ephemeral=True)
            return
        file = discord.File(buf, filename="scores_average.png")
        embed = discord.Embed(title="<:top1:1489297584752168990> Average score per player", color=discord.Color.gold())
        embed.set_image(url="attachment://scores_average.png")
        await interaction.followup.send(embed=embed, file=file)

    @app_commands.command(name="list_events", description="List all recorded events")
    @app_commands.describe(event_type="Filter by type (optional)")
    @app_commands.choices(event_type=[
        Choice(name="All events", value="all"),
        Choice(name="Smash", value="smash"),
        Choice(name="Mechs", value="mechs"),
    ])
    async def list_events(self, interaction: discord.Interaction, event_type: str = "all"):
        data = load_data(interaction.guild_id)
        events = data["events"]
        if event_type != "all":
            events = [e for e in events if e["type"] == event_type]
        events = sorted(events, key=lambda e: e["date"], reverse=True)
        if not events:
            await interaction.response.send_message("No events recorded.", ephemeral=True)
            return
        embed = discord.Embed(title="<:announcement:1496817320440500335> List of events", color=discord.Color.blurple())
        for e in events[:15]:
            nb_joueurs = len(e["scores"])
            total = sum(e["scores"].values())
            desc = e.get("description", "") or "—"
            embed.add_field(
                name=f"{TYPE_LABEL[e['type']]}  —  {e['date']}",
                value=f"<:faction:1488292952618045440> {nb_joueurs} players  •  <:top1:1489297584752168990> Total : {total:,}\n📝 {desc}",
                inline=False
            )
        if len(data["events"]) > 15:
            embed.set_footer(text=f"Displaying the last 15 events out of a total of {len(data['events'])}.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="delete_event", description="Deletes an entire event and all its scores")
    @app_commands.describe(event_type="Event type", date="Date of the event (YYYY-MM-DD format)")
    @app_commands.choices(event_type=[
        Choice(name="Smash", value="smash"),
        Choice(name="Mechs", value="mechs"),
    ])
    async def delete_event(self, interaction: discord.Interaction, event_type: str, date: str):
        gc = await self._check_guild(interaction)
        if not gc:
            return
        if not any(r.id == gc["COLEAD"] for r in interaction.user.roles):
            await interaction.response.send_message("❌ Only co-leads can delete an event.", ephemeral=True)
            return

        data = load_data(interaction.guild_id)
        event = find_event(data, event_type, date)
        if not event:
            await interaction.response.send_message(
                f"❌ No events **{TYPE_LABEL[event_type]}** found for the **{date}**.", ephemeral=True)
            return

        nb_joueurs = len(event["scores"])
        total = sum(event["scores"].values())
        guild_id = interaction.guild_id

        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.confirmed = False

            async def on_timeout(self):
                for item in self.children:
                    item.disabled = True
                try:
                    await interaction.edit_original_response(content="⏱️ Confirmation timed out.", embed=None, view=None)
                except Exception:
                    pass

            @discord.ui.button(label="✅ Confirm deletion", style=discord.ButtonStyle.danger)
            async def confirm(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    await btn_interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
                    return
                self.confirmed = True
                self.stop()
                await btn_interaction.response.defer()
                data2 = load_data(guild_id)
                data2["events"] = [e for e in data2["events"]
                                   if not (e["type"] == event_type and e["date"] == date)]
                save_data(guild_id, data2)
                embed_ok = discord.Embed(
                    title="<:notif:1496819951296839811> Event deleted",
                    description=f"**{TYPE_LABEL[event_type]}** from **{date}** deleted.\n"
                                f"<:faction:1488292952618045440> {nb_joueurs} players — <:top1:1489297584752168990> Total was : {total:,}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                embed_ok.set_footer(text=f"Par {btn_interaction.user.display_name}")
                await btn_interaction.edit_original_response(embed=embed_ok, view=None)

            @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    await btn_interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
                    return
                self.stop()
                await btn_interaction.response.defer()
                await btn_interaction.edit_original_response(content="<:usefull:1488293835137093683> Deletion cancelled.", embed=None, view=None)

        embed_confirm = discord.Embed(
            title="<a:nyx:1489283483376292004> Confirm deletion",
            description=f"You are about to delete **{TYPE_LABEL[event_type]}** from **{date}**.\n"
                        f"<:faction:1488292952618045440> {nb_joueurs} joueur(s) — <:top1:1489297584752168990> Total : {total:,}\n\n"
                        "**This action cannot be undone.**",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed_confirm, view=ConfirmView(), ephemeral=True)

    @app_commands.command(name="delete_player", description="Removes a player from all events (or a specific one)")
    @app_commands.describe(
        player="Name of the player to be removed",
        event_type="Limit to one event type (optional)",
        date="Limit to a specific date (optional, format YYYY-MM-DD)"
    )
    @app_commands.choices(event_type=[
        Choice(name="All events", value="all"),
        Choice(name="Smash", value="smash"),
        Choice(name="Mechs", value="mechs"),
    ])
    async def delete_player(self, interaction: discord.Interaction,
                             player: str, event_type: str = "all", date: str = ""):
        gc = await self._check_guild(interaction)
        if not gc:
            return
        if not any(r.id == gc["COLEAD"] for r in interaction.user.roles):
            await interaction.response.send_message("❌ Only co-leads can remove a player.", ephemeral=True)
            return

        data = load_data(interaction.guild_id)
        guild_id = interaction.guild_id
        occurrences = []
        for e in data["events"]:
            if player not in e["scores"]:
                continue
            if event_type != "all" and e["type"] != event_type:
                continue
            if date and e["date"] != date:
                continue
            occurrences.append(e)

        if not occurrences:
            await interaction.response.send_message(
                f"❌ No results found for **{player}** with this filter.", ephemeral=True)
            return

        scope = f"on **{len(occurrences)}** event(s)"
        if date:
            scope = f"for the event of **{date}**"

        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)

            async def on_timeout(self):
                for item in self.children:
                    item.disabled = True
                try:
                    await interaction.edit_original_response(content="⏱️ Confirmation timed out.", embed=None, view=None)
                except Exception:
                    pass

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
            async def confirm(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    await btn_interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
                    return
                self.stop()
                await btn_interaction.response.defer()
                data2 = load_data(guild_id)
                count = 0
                for e in data2["events"]:
                    if player not in e["scores"]:
                        continue
                    if event_type != "all" and e["type"] != event_type:
                        continue
                    if date and e["date"] != date:
                        continue
                    del e["scores"][player]
                    count += 1
                save_data(guild_id, data2)
                embed_ok = discord.Embed(
                    title="<:notif:1496819951296839811> Player removed",
                    description=f"**{player}** taken from **{count}** event(s).",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                embed_ok.set_footer(text=f"By {btn_interaction.user.display_name}")
                await btn_interaction.edit_original_response(embed=embed_ok, view=None)

            @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    await btn_interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
                    return
                self.stop()
                await btn_interaction.response.defer()
                await btn_interaction.edit_original_response(content="<:usefull:1488293835137093683> Deletion cancelled.", embed=None, view=None)

        embed_confirm = discord.Embed(
            title="<a:nyx:1489283483376292004> Confirm deletion ?",
            description=f"Delete **{player}** {scope} ?\n\n**This action is irreversible.**",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed_confirm, view=ConfirmView(), ephemeral=True)

    @app_commands.command(name="delete_score", description="Removes a player's score for a specific event")
    @app_commands.describe(
        event_type="Event type",
        date="Date of the event (YYYY-MM-DD format)",
        player="Player's name"
    )
    @app_commands.choices(event_type=[
        Choice(name="Smash", value="smash"),
        Choice(name="Mechs", value="mechs"),
    ])
    async def delete_score(self, interaction: discord.Interaction,
                            event_type: str, date: str, player: str):
        gc = await self._check_guild(interaction)
        if not gc:
            return
        if not any(r.id == gc["COLEAD"] for r in interaction.user.roles):
            await interaction.response.send_message("❌ You don't have the permissions to do that.", ephemeral=True)
            return

        data = load_data(interaction.guild_id)
        event = find_event(data, event_type, date)
        if not event:
            await interaction.response.send_message(
                f"❌ No events **{TYPE_LABEL[event_type]}** found for **{date}**.", ephemeral=True)
            return

        if player not in event["scores"]:
            await interaction.response.send_message(
                f"❌ No scores found for **{player}** in this event.", ephemeral=True)
            return

        old_score = event["scores"].pop(player)
        save_data(interaction.guild_id, data)

        embed = discord.Embed(
            title="<:notif:1496819951296839811> Score deleted",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="<:faction:1488292952618045440> Player", value=player, inline=True)
        embed.add_field(name="<:optis:1488294635519479918> Score deleted", value=f"{old_score:,}", inline=True)
        embed.add_field(name="<:calendar:1496816276780224512> Event", value=f"{TYPE_LABEL[event_type]} — {date}", inline=False)
        embed.set_footer(text=f"Par {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="rename", description="Rename a player across all events and the member list")
    @app_commands.describe(
        old_name="Current name of the player",
        new_name="New name to give to the player"
    )
    async def rename(self, interaction: discord.Interaction, old_name: str, new_name: str):
        gc = await self._check_guild(interaction)
        if not gc:
            return
        if not any(r.id == gc["COLEAD"] for r in interaction.user.roles):
            await interaction.response.send_message("❌ Only co-leads can rename a player.", ephemeral=True)
            return

        old_name = old_name.strip()
        new_name = new_name.strip()

        if not old_name or not new_name:
            await interaction.response.send_message("❌ Names cannot be empty.", ephemeral=True)
            return

        if old_name == new_name:
            await interaction.response.send_message("❌ Old and new names are identical.", ephemeral=True)
            return

        data = load_data(interaction.guild_id)
        guild_id = interaction.guild_id

        # Count occurrences in events
        events_affected = [e for e in data["events"] if old_name in e["scores"]]
        if not events_affected:
            await interaction.response.send_message(
                f"❌ No scores found for **{old_name}**.", ephemeral=True)
            return

        # Check if new_name already exists (collision risk)
        collision_events = [e for e in events_affected if new_name in e["scores"]]

        members = load_members(guild_id)
        in_member_list = old_name in members

        summary = (
            f"Rename **{old_name}** → **{new_name}**\n"
            f"<:faction:1488292952618045440> **{len(events_affected)}** event(s) affected\n"
        )
        if in_member_list:
            summary += "<:usefull:1488293835137093683> Also updated in the member list\n"
        if collision_events:
            summary += (
                f"\n⚠️ **{new_name}** already has a score in **{len(collision_events)}** event(s). "
                "Scores will be **merged** (old score replaces existing one).\n"
            )
        summary += "\n**This action cannot be undone.**"

        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.confirmed = False

            async def on_timeout(self):
                for item in self.children:
                    item.disabled = True
                try:
                    await interaction.edit_original_response(content="⏱️ Confirmation timed out.", embed=None, view=None)
                except Exception:
                    pass

            @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.success)
            async def confirm(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    await btn_interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
                    return
                self.confirmed = True
                self.stop()
                await btn_interaction.response.defer()

                # Apply rename in events
                data2 = load_data(guild_id)
                count = 0
                for e in data2["events"]:
                    if old_name in e["scores"]:
                        e["scores"][new_name] = e["scores"].pop(old_name)
                        count += 1
                save_data(guild_id, data2)

                # Apply rename in member list
                members2 = load_members(guild_id)
                member_updated = False
                if old_name in members2:
                    members2.remove(old_name)
                    if new_name not in members2:
                        members2.append(new_name)
                    save_members(guild_id, members2)
                    member_updated = True

                embed_ok = discord.Embed(
                    title="<:notif:1496819951296839811> Player renamed",
                    description=(
                        f"**{old_name}** → **{new_name}**\n"
                        f"<:faction:1488292952618045440> Updated in **{count}** event(s)"
                        + ("\n<:usefull:1488293835137093683> Member list updated" if member_updated else "")
                    ),
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )
                embed_ok.set_footer(text=f"By {btn_interaction.user.display_name}")
                await btn_interaction.edit_original_response(embed=embed_ok, view=None)

            @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    await btn_interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
                    return
                self.stop()
                await btn_interaction.response.defer()
                await btn_interaction.edit_original_response(content="<:usefull:1488293835137093683> Rename cancelled.", embed=None, view=None)

        embed_confirm = discord.Embed(
            title="<a:nyx:1489283483376292004> Confirm rename",
            description=summary,
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed_confirm, view=ConfirmView(), ephemeral=True)


async def setup(bot):
    await bot.add_cog(ScoresCog(bot))