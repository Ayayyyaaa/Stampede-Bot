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

DATA_FILE = "data/scores.json"


def load_data() -> dict:
    """Charge les données depuis le fichier JSON, crée le fichier si nécessaire."""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        save_data({"events": []})
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: dict):
    """Sauvegarde les données dans le fichier JSON."""
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_event(data: dict, event_type: str, date_str: str) -> dict | None:
    """Trouve un événement par type et date."""
    for event in data["events"]:
        if event["type"] == event_type and event["date"] == date_str:
            return event
    return None


COLORS = {
    "smash": "#f59e0b",   # gold
    "mechs": "#ef4444",   # red
    "grid":  "#2a2a3e",
    "bg":    "#0f0f1a",
    "panel": "#1a1a2e",
    "text":  "#e2e8f0",
    "accent":"#818cf8",
}

TYPE_LABEL = {"smash": "<:Pvp_ticket:1487193877990478067> Smash", "mechs": "<:mecha_icon:1488150151519535144> Mechs"}

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
    title = f"<:faction:1488292952618045440> Changes in the club's total score"
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
    title = f"<a:research:1488144464835776622> Changes in the {player} score"
    if event_type:
        title += f"  —  {TYPE_LABEL[event_type]}"
    ax.set_title(title, fontsize=13, fontweight="bold", color=COLORS["text"], pad=12)

    for i, v in enumerate(scores):
        ax.annotate(f"{v:,}", (i, v), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8, color=COLORS["text"])

    # ligne moyenne
    avg = np.mean(scores)
    ax.axhline(avg, color="white", linestyle=":", linewidth=1.2, alpha=0.5)
    ax.annotate(f"moy. {avg:,.0f}", xy=(len(scores) - 1, avg),
                xytext=(-40, 5), textcoords="offset points",
                fontsize=8, color="white", alpha=0.7)

    return _buf(fig)

def chart_average_per_player(data: dict, event_type: str | None = None) -> BytesIO:
    events = data["events"]
    if event_type:
        events = [e for e in events if e["type"] == event_type]

    if not events:
        raise ValueError("No event found")

    player_scores: dict[str, list] = {}
    for e in events:
        for player, score in e["scores"].items():
            player_scores.setdefault(player, []).append(score)

    if not player_scores:
        raise ValueError("No registered score found")

    averages = {p: np.mean(s) for p, s in player_scores.items()}
    averages = dict(sorted(averages.items(), key=lambda x: x[1], reverse=True))

    players = list(averages.keys())
    values = list(averages.values())

    fig, ax = _setup_dark_fig(max(10, len(players) * 0.9 + 2), 5)

    bar_colors = [COLORS["accent"]] * len(players)
    if values:
        bar_colors[0] = COLORS["smash"]  # top joueur en or

    bars = ax.bar(players, values, color=bar_colors, width=0.6,
                  edgecolor="white", linewidth=0.4, zorder=2)

    ax.set_ylabel("Average score", color=COLORS["text"])
    title = "<:top1:1489297584752168990> Average score per player"
    if event_type:
        title += f"  —  {TYPE_LABEL[event_type]}"
    ax.set_title(title, fontsize=13, fontweight="bold", color=COLORS["text"], pad=12)
    ax.set_xticks(range(len(players)))
    ax.set_xticklabels(players, rotation=30, ha="right", fontsize=9, color=COLORS["text"])

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.01,
                f"{val:,.0f}", ha="center", va="bottom", fontsize=8, color=COLORS["text"])

    return _buf(fig)


class ScoresCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_event", description="Add an event (smash/mechs) with a date")
    @app_commands.describe(
        event_type="Type of event",
        date="Date of the event (YYYY-MM-DD format)",
        description="Optional description of the event"
    )
    @app_commands.choices(event_type=[
        Choice(name="<:Pvp_ticket:1487193877990478067> Smash", value="smash"),
        Choice(name="<:mecha_icon:1488150151519535144> Mechs", value="mechs"),
    ])
    async def add_event(self, interaction: discord.Interaction,
                        event_type: str, date: str, description: str = ""):

        if not any(r.id in (config.COLEAD,) for r in interaction.user.roles):
            await interaction.response.send_message("❌ You don't have the permissions to do that", ephemeral=True)
            return

        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid date format. Use **YYYY-MM-DD** (ex: 2025-07-18).", ephemeral=True)
            return

        data = load_data()
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
        save_data(data)

        embed = discord.Embed(
            title=f"{TYPE_LABEL[event_type]} — Event added !",
            description=f"<:calendar:1496816276780224512> **Date :** {date}\n<:usefull:1488294635519479918> **Description :** {description or '—'}",
            color=discord.Color.from_str(COLORS["smash"] if event_type == "smash" else COLORS["mechs"]),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Added by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add_score", description="Adds or updates a member's score for an event")
    @app_commands.describe(
        event_type="Event type",
        date="Date of the event (YYYY-MM-DD format)",
        player="Player's name",
        score="Score achieved"
    )
    @app_commands.choices(event_type=[
        Choice(name="<:Pvp_ticket:1487193877990478067> Smash", value="smash"),
        Choice(name="<:mecha_icon:1488150151519535144> Mechs", value="mechs"),
    ])
    async def add_score(self, interaction: discord.Interaction,
                        event_type: str, date: str, player: str, score: int):

        if not any(r.id in (config.COLEAD, config.FURYMEMBER) for r in interaction.user.roles):
            await interaction.response.send_message("❌ You don't have the permission to do that.", ephemeral=True)
            return

        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid date format. Use **YYYY-MM-DD**.", ephemeral=True)
            return

        data = load_data()
        event = find_event(data, event_type, date)
        if not event:
            await interaction.response.send_message(
                f"❌ No events **{TYPE_LABEL[event_type]}** found for the **{date}**.\n"
                "First, create it using `/add_event`.", ephemeral=True)
            return

        old_score = event["scores"].get(player)
        event["scores"][player] = score
        save_data(data)

        action = "updated" if old_score is not None else "added"
        diff = f" *(former : {old_score:,})*" if old_score is not None else ""
        total = sum(event["scores"].values())

        embed = discord.Embed(
            title=f"<:announcement:1496817320440500335> Score {action} — {TYPE_LABEL[event_type]}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="<a:terryx:1489284057920573660> Player", value=player, inline=True)
        embed.add_field(name="<:optis:1488294635519479918> Score", value=f"{score:,}{diff}", inline=True)
        embed.add_field(name="<:calendar:1496816276780224512> Event", value=date, inline=True)
        embed.add_field(name="<:top1:1489297584752168990> Total club", value=f"{total:,}", inline=False)
        embed.set_footer(text=f"Par {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="scores_club", description="Chart: Change in the club’s total score")
    @app_commands.describe(event_type="Filter by type (optional)")
    @app_commands.choices(event_type=[
        Choice(name="All events", value="all"),
        Choice(name="<:Pvp_ticket:1487193877990478067> Smash only", value="smash"),
        Choice(name="<:mecha_icon:1488150151519535144> Mechs only", value="mechs"),
    ])
    async def scores_club(self, interaction: discord.Interaction, event_type: str = "all"):
        await interaction.response.defer()
        data = load_data()
        try:
            buf = chart_club_evolution(data, None if event_type == "all" else event_type)
        except ValueError as e:
            await interaction.followup.send(f"❌ {e}", ephemeral=True)
            return

        file = discord.File(buf, filename="scores_club.png")
        embed = discord.Embed(
            title="<a:research:1488144464835776622> Changes in the club's total score",
            color=discord.Color.blurple()
        )
        embed.set_image(url="attachment://scores_club.png")
        await interaction.followup.send(embed=embed, file=file)

    # ── /scores_player ───────────────────────────────────────────────────────
    @app_commands.command(name="scores_player", description="Chart: a player's score over time")
    @app_commands.describe(
        player="Player's name",
        event_type="Filter by type (optional)"
    )
    @app_commands.choices(event_type=[
        Choice(name="All events", value="all"),
        Choice(name="<:Pvp_ticket:1487193877990478067> Smash only", value="smash"),
        Choice(name="<:mecha_icon:1488150151519535144> Mechs only", value="mechs"),
    ])
    async def scores_player(self, interaction: discord.Interaction,
                             player: str, event_type: str = "all"):
        await interaction.response.defer()
        data = load_data()
        try:
            buf = chart_player_evolution(data, player, None if event_type == "all" else event_type)
        except ValueError as e:
            await interaction.followup.send(f"❌ {e}", ephemeral=True)
            return

        file = discord.File(buf, filename="scores_player.png")
        embed = discord.Embed(
            title=f"<a:research:1488144464835776622> Changes of {player} score",
            color=discord.Color.blurple()
        )
        embed.set_image(url="attachment://scores_player.png")
        await interaction.followup.send(embed=embed, file=file)

    # ── /scores_average ──────────────────────────────────────────────────────
    @app_commands.command(name="scores_average", description="Chart: average score for each player")
    @app_commands.describe(event_type="Filter by type (optional)")
    @app_commands.choices(event_type=[
        Choice(name="All events", value="all"),
        Choice(name="<:Pvp_ticket:1487193877990478067> Smash only", value="smash"),
        Choice(name="<:mecha_icon:1488150151519535144> Mechs only", value="mechs"),
    ])
    async def scores_average(self, interaction: discord.Interaction, event_type: str = "all"):
        await interaction.response.defer()
        data = load_data()
        try:
            buf = chart_average_per_player(data, None if event_type == "all" else event_type)
        except ValueError as e:
            await interaction.followup.send(f"❌ {e}", ephemeral=True)
            return

        file = discord.File(buf, filename="scores_average.png")
        embed = discord.Embed(
            title="<:top1:1489297584752168990> Average score per player",
            color=discord.Color.gold()
        )
        embed.set_image(url="attachment://scores_average.png")
        await interaction.followup.send(embed=embed, file=file)

    @app_commands.command(name="list_events", description="List all recorded events")
    @app_commands.describe(event_type="Filter by type (optional)")
    @app_commands.choices(event_type=[
        Choice(name="All events", value="all"),
        Choice(name="<:Pvp_ticket:1487193877990478067> Smash only", value="smash"),
        Choice(name="<:mecha_icon:1488150151519535144> Mechs only", value="mechs"),
    ])
    async def list_events(self, interaction: discord.Interaction, event_type: str = "all"):
        data = load_data()
        events = data["events"]
        if event_type != "all":
            events = [e for e in events if e["type"] == event_type]
        events = sorted(events, key=lambda e: e["date"], reverse=True)

        if not events:
            await interaction.response.send_message("No events recorded.", ephemeral=True)
            return

        embed = discord.Embed(
            title="<:announcement:1496817320440500335> List of events",
            color=discord.Color.blurple()
        )
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
    @app_commands.describe(
        event_type="Event type",
        date="Date of the event (YYYY-MM-DD format)"
    )
    @app_commands.choices(event_type=[
        Choice(name="All events", value="all"),
        Choice(name="<:Pvp_ticket:1487193877990478067> Smash only", value="smash"),
        Choice(name="<:mecha_icon:1488150151519535144> Mechs only", value="mechs"),
    ])
    async def delete_event(self, interaction: discord.Interaction, event_type: str, date: str):
        if not any(r.id in (config.COLEAD,) for r in interaction.user.roles):
            await interaction.response.send_message("❌ Only co-leads can delete an event.", ephemeral=True)
            return
 
        data = load_data()
        event = find_event(data, event_type, date)
        if not event:
            await interaction.response.send_message(
                f"❌ No events **{TYPE_LABEL[event_type]}** found for the **{date}**.", ephemeral=True)
            return
 
        nb_joueurs = len(event["scores"])
        total = sum(event["scores"].values())

        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.confirmed = False
 
            @discord.ui.button(label="✅ Confirm deletion", style=discord.ButtonStyle.danger)
            async def confirm(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    await btn_interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
                    return
                self.confirmed = True
                self.stop()
                data2 = load_data()
                data2["events"] = [e for e in data2["events"]
                                   if not (e["type"] == event_type and e["date"] == date)]
                save_data(data2)
                embed_ok = discord.Embed(
                    title="<:notif:1496819951296839811> Event deleted",
                    description=f"**{TYPE_LABEL[event_type]}** from **{date}** deleted.\n"
                                f"<:faction:1488292952618045440> {nb_joueurs} players — <:top1:1489297584752168990> Total was : {total:,}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                embed_ok.set_footer(text=f"Par {btn_interaction.user.display_name}")
                await btn_interaction.response.edit_message(embed=embed_ok, view=None)
 
            @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    await btn_interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
                    return
                self.stop()
                await btn_interaction.response.edit_message(
                    content="<:usefull:1488293835137093683> Deletion cancelled.", embed=None, view=None)
 
        embed_confirm = discord.Embed(
            title="<a:nyx:1489283483376292004> Confirm deletion",
            description=f"You are about to delete **{TYPE_LABEL[event_type]}** from **{date}**.\n"
                        f"<:faction:1488292952618045440> {nb_joueurs} joueur(s) — <:top1:1489297584752168990> Total : {total:,}\n\n"
                        "**This action cannot be undone.**",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed_confirm, view=ConfirmView(), ephemeral=True)
 
    # ── /delete_player ───────────────────────────────────────────────────────
    @app_commands.command(name="delete_player", description="Supprime un joueur de tous les événements (ou d'un seul)")
    @app_commands.describe(
        player="Name of the player to be removed",
        event_type="Limit to one event type (optional)",
        date="Limit to a specific date (optional, format YYYY-MM-DD)"
    )
    @app_commands.choices(event_type=[
        Choice(name="All events", value="all"),
        Choice(name="<:Pvp_ticket:1487193877990478067> Smash only", value="smash"),
        Choice(name="<:mecha_icon:1488150151519535144> Mechs only", value="mechs"),
    ])
    async def delete_player(self, interaction: discord.Interaction,
                             player: str, event_type: str = "all", date: str = ""):
        if not any(r.id in (config.COLEAD,) for r in interaction.user.roles):
            await interaction.response.send_message("❌ Only co-leads can remove a player.", ephemeral=True)
            return
 
        data = load_data()

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
            scope = f"pour l'événement du **{date}**"
 
        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
 
            @discord.ui.button(label="<:announcement:1496817320440500335> Confirm", style=discord.ButtonStyle.danger)
            async def confirm(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    await btn_interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
                    return
                self.stop()
                data2 = load_data()
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
                save_data(data2)
                embed_ok = discord.Embed(
                    title="<:notif:1496819951296839811> Player removed",
                    description=f"**{player}** taken from **{count}** event(s).",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                embed_ok.set_footer(text=f"By {btn_interaction.user.display_name}")
                await btn_interaction.response.edit_message(embed=embed_ok, view=None)
 
            @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    await btn_interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
                    return
                self.stop()
        embed_confirm = discord.Embed(
            title="<a:nyx:1489283483376292004> Confirm deletion ?",
            description=f"Delete **{player}** {scope} ?\n\n**Cette action est irréversible.**",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed_confirm, view=ConfirmView(), ephemeral=True)
 
    # ── /delete_score ────────────────────────────────────────────────────────
    @app_commands.command(name="delete_score", description="Removes a player's score for a specific event")
    @app_commands.describe(
        event_type="Event type",
        date="Date of the event (YYYY-MM-DD format)",
        player="Player's name"
    )
    @app_commands.choices(event_type=[
        Choice(name="<:Pvp_ticket:1487193877990478067> Smash", value="smash"),
        Choice(name="<:mecha_icon:1488150151519535144> Mechs", value="mechs"),
    ])
    async def delete_score(self, interaction: discord.Interaction,
                            event_type: str, date: str, player: str):
        if not any(r.id in (config.COLEAD,) for r in interaction.user.roles):
            await interaction.response.send_message("❌ You don't have the permissions to do that.", ephemeral=True)
            return
 
        data = load_data()
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
        save_data(data)
 
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


async def setup(bot):
    await bot.add_cog(ScoresCog(bot))