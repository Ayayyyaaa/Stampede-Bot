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

TYPE_LABEL = {"smash": "⚔️ Smash", "mechs": "🤖 Mechs"}

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
        raise ValueError("Aucun événement trouvé pour ce filtre.")

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
    ax.set_ylabel("Score total", color=COLORS["text"])
    title = f"📈 Évolution du score total du club"
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
        raise ValueError(f"Aucun score trouvé pour **{player}**.")

    fig, ax = _setup_dark_fig(11, 5)
    col = COLORS["smash"] if event_type == "smash" else (COLORS["mechs"] if event_type == "mechs" else COLORS["accent"])

    ax.fill_between(range(len(dates)), scores, alpha=0.2, color=col)
    ax.plot(range(len(dates)), scores, color=col, linewidth=2.5, marker="o",
            markersize=8, markeredgecolor="white", markeredgewidth=0.8, zorder=3)

    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(dates, fontsize=8, color=COLORS["text"])
    ax.set_ylabel("Score", color=COLORS["text"])
    title = f"🎯 Évolution de {player}"
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
        raise ValueError("Aucun événement trouvé pour ce filtre.")

    player_scores: dict[str, list] = {}
    for e in events:
        for player, score in e["scores"].items():
            player_scores.setdefault(player, []).append(score)

    if not player_scores:
        raise ValueError("Aucun score enregistré.")

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

    ax.set_ylabel("Score moyen", color=COLORS["text"])
    title = "🏆 Score moyen par joueur"
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

    @app_commands.command(name="add_event", description="Ajoute un événement (smash/mechs) avec une date")
    @app_commands.describe(
        event_type="Type d'événement",
        date="Date de l'événement (format YYYY-MM-DD)",
        description="Description optionnelle de l'événement"
    )
    @app_commands.choices(event_type=[
        Choice(name="⚔️ Smash", value="smash"),
        Choice(name="🤖 Mechs", value="mechs"),
    ])
    async def add_event(self, interaction: discord.Interaction,
                        event_type: str, date: str, description: str = ""):

        # Vérification rôle
        if not any(r.id in (config.COLEAD, config.FURYMEMBER) for r in interaction.user.roles):
            await interaction.response.send_message("❌ Vous n'avez pas la permission.", ephemeral=True)
            return

        # Validation date
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await interaction.response.send_message(
                "❌ Format de date invalide. Utilisez **YYYY-MM-DD** (ex: 2025-07-18).", ephemeral=True)
            return

        data = load_data()
        if find_event(data, event_type, date):
            await interaction.response.send_message(
                f"⚠️ Un événement **{TYPE_LABEL[event_type]}** existe déjà pour le **{date}**.", ephemeral=True)
            return

        data["events"].append({
            "type": event_type,
            "date": date,
            "description": description,
            "scores": {}
        })
        save_data(data)

        embed = discord.Embed(
            title=f"{TYPE_LABEL[event_type]} — Événement ajouté !",
            description=f"📅 **Date :** {date}\n📝 **Description :** {description or '—'}",
            color=discord.Color.from_str(COLORS["smash"] if event_type == "smash" else COLORS["mechs"]),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Ajouté par {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add_score", description="Ajoute ou met à jour le score d'un membre pour un événement")
    @app_commands.describe(
        event_type="Type d'événement",
        date="Date de l'événement (format YYYY-MM-DD)",
        player="Nom du joueur",
        score="Score obtenu"
    )
    @app_commands.choices(event_type=[
        Choice(name="⚔️ Smash", value="smash"),
        Choice(name="🤖 Mechs", value="mechs"),
    ])
    async def add_score(self, interaction: discord.Interaction,
                        event_type: str, date: str, player: str, score: int):

        if not any(r.id in (config.COLEAD, config.FURYMEMBER) for r in interaction.user.roles):
            await interaction.response.send_message("❌ Vous n'avez pas la permission.", ephemeral=True)
            return

        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await interaction.response.send_message(
                "❌ Format de date invalide. Utilisez **YYYY-MM-DD**.", ephemeral=True)
            return

        data = load_data()
        event = find_event(data, event_type, date)
        if not event:
            await interaction.response.send_message(
                f"❌ Aucun événement **{TYPE_LABEL[event_type]}** trouvé pour le **{date}**.\n"
                "Créez-le d'abord avec `/add_event`.", ephemeral=True)
            return

        old_score = event["scores"].get(player)
        event["scores"][player] = score
        save_data(data)

        action = "mis à jour" if old_score is not None else "ajouté"
        diff = f" *(ancien : {old_score:,})*" if old_score is not None else ""
        total = sum(event["scores"].values())

        embed = discord.Embed(
            title=f"✅ Score {action} — {TYPE_LABEL[event_type]}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Joueur", value=player, inline=True)
        embed.add_field(name="🎯 Score", value=f"{score:,}{diff}", inline=True)
        embed.add_field(name="📅 Événement", value=date, inline=True)
        embed.add_field(name="🏆 Total club", value=f"{total:,}", inline=False)
        embed.set_footer(text=f"Par {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="scores_club", description="Graphique : évolution du score total du club")
    @app_commands.describe(event_type="Filtrer par type (optionnel)")
    @app_commands.choices(event_type=[
        Choice(name="Tous les événements", value="all"),
        Choice(name="⚔️ Smash uniquement", value="smash"),
        Choice(name="🤖 Mechs uniquement", value="mechs"),
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
            title="📈 Évolution du score total du club",
            color=discord.Color.blurple()
        )
        embed.set_image(url="attachment://scores_club.png")
        await interaction.followup.send(embed=embed, file=file)

    # ── /scores_player ───────────────────────────────────────────────────────
    @app_commands.command(name="scores_player", description="Graphique : évolution du score d'un joueur")
    @app_commands.describe(
        player="Nom du joueur",
        event_type="Filtrer par type (optionnel)"
    )
    @app_commands.choices(event_type=[
        Choice(name="Tous les événements", value="all"),
        Choice(name="⚔️ Smash uniquement", value="smash"),
        Choice(name="🤖 Mechs uniquement", value="mechs"),
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
            title=f"🎯 Évolution de {player}",
            color=discord.Color.blurple()
        )
        embed.set_image(url="attachment://scores_player.png")
        await interaction.followup.send(embed=embed, file=file)

    # ── /scores_average ──────────────────────────────────────────────────────
    @app_commands.command(name="scores_average", description="Graphique : score moyen de chaque joueur")
    @app_commands.describe(event_type="Filtrer par type (optionnel)")
    @app_commands.choices(event_type=[
        Choice(name="Tous les événements", value="all"),
        Choice(name="⚔️ Smash uniquement", value="smash"),
        Choice(name="🤖 Mechs uniquement", value="mechs"),
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
            title="🏆 Score moyen par joueur",
            color=discord.Color.gold()
        )
        embed.set_image(url="attachment://scores_average.png")
        await interaction.followup.send(embed=embed, file=file)

    # ── /list_events ─────────────────────────────────────────────────────────
    @app_commands.command(name="list_events", description="Liste tous les événements enregistrés")
    @app_commands.describe(event_type="Filtrer par type (optionnel)")
    @app_commands.choices(event_type=[
        Choice(name="Tous les événements", value="all"),
        Choice(name="⚔️ Smash uniquement", value="smash"),
        Choice(name="🤖 Mechs uniquement", value="mechs"),
    ])
    async def list_events(self, interaction: discord.Interaction, event_type: str = "all"):
        data = load_data()
        events = data["events"]
        if event_type != "all":
            events = [e for e in events if e["type"] == event_type]
        events = sorted(events, key=lambda e: e["date"], reverse=True)

        if not events:
            await interaction.response.send_message("📭 Aucun événement enregistré.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📋 Liste des événements",
            color=discord.Color.blurple()
        )
        for e in events[:15]:  # max 15 pour éviter l'overflow de l'embed
            nb_joueurs = len(e["scores"])
            total = sum(e["scores"].values())
            desc = e.get("description", "") or "—"
            embed.add_field(
                name=f"{TYPE_LABEL[e['type']]}  —  {e['date']}",
                value=f"👥 {nb_joueurs} joueur(s)  •  🏆 Total : {total:,}\n📝 {desc}",
                inline=False
            )
        if len(data["events"]) > 15:
            embed.set_footer(text=f"Affichage des 15 derniers événements sur {len(data['events'])} total.")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(ScoresCog(bot))