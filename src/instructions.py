import discord
from discord.ext import commands
from discord import app_commands
import config


def _build_guide_embed() -> discord.Embed:
    """Embed 1/2 : liste complète des commandes (générique, valable pour tous les clubs)."""
    description = (
        "Hey everyone !  Here is the complete guide on how to use the bot to track our events "
        "(**Smash** & **Mechs**), manage the member list, and check some stats.\n"
        "*Note : Manage commands are reserved to **Co-Leads** only, but everyone can view the charts "
        "and lists* <:capsules:1499365962175090839>\n\n"
        "### <:find_club:1526885840402251878>  **1. Member Management**\n"
        "*Keep our club's roster up to date with these commands.*\n"
        "* <:renard:1499364063036182659>  **`/member_list`** : Displays the full list of current club "
        "members. *(Public)*\n"
        "* <:players:1496861469583867987>  **`/member_add [names]`** : Add one or multiple members. "
        "Separate names with commas. You can also link a Discord account directly using `:` "
        "(`Player1, Player2:idDiscord`). *(Co-leads)*\n"
        "* <:secu:1499364065422606407>  **`/member_link [name] [member]`** : Link (or unlink) a Discord "
        "account to a player's profile in the club. *(Co-leads)*\n"
        "* <:capsules:1499364070279876608>  **`/rename [old_name] [new_name]`** : Rename a player. "
        "**Bonus:** this also updates their name across all their past event scores *(Co-leads)*\n"
        "* <:optis:1488294635519479918>  **`/member_remove [name]`** : Remove a player from the club's "
        "member list. *(Co-leads)*\n\n"
        "### <:list:1499364068702818434>  **2. Events & Score Tracking**\n"
        "*Manage Smash and Mechs events in one place.*\n"
        "> **Mandatory Date Format:** `YYYY-MM-DD` (2025-07-18)\n"
        "* <:list:1499364068702818434>  **`/list_events [event_type]`** : Lists all recorded events "
        "(you can filter by type). *(Public)*\n"
        "* <:random:1499364051883393044>  **`/add_event [event_type] [date] [description]`** : Creates "
        "a new event in the database. *(Co-leads)*\n"
        "* <:increase:1496861484569989251>  **`/add_scores [event_type] [date] [scores]`** : Register "
        "scores for multiple players at once! *(Members & Co-leads)*\n"
        "    * *Expected format:* `Player1:100, Player2:150, Player3:300`\n"
        "* ❌ **`/delete_score [event_type] [date] [player]`** : Removes a specific player's score for a "
        "specific event. *(Co-leads)*\n"
        "* <:optis:1488294635519479918>  **`/delete_player [player] [event_type] [date]`** : Completely "
        "removes a player from the history of all events (or specific ones if filtered). *(Co-leads)*\n"
        "* <:fire:1499364059697381396>  **`/delete_event [event_type] [date]`** : Deletes an "
        "entire event and all its associated scores. *(Co-leads)*\n"
        "* <:kill:1499364058187698246>  **`/clear_scores`** : **WARNING.** Completely wipes all "
        "events and scores from the database. *(Co-leads)*\n\n"
        "### <:increase:1496861484569989251>  **3. Stats & Charts (Open to everyone!)**\n"
        "*Track player's progression and the club's performance with beautiful charts.* "
        "<:list:1499364068702818434>\n"
        "* <:players:1496861469583867987>  **`/scores_club [event_type]`** : Generates a chart showing "
        "the evolution of the club's total score over time.\n"
        "* <:secu:1499364065422606407>  **`/scores_player [player] [event_type]`** : Displays the "
        "progression curve of a specific player.\n"
        "* <:increase:1496861484569989251>  **`/scores_average [event_type]`** : Shows a bar chart "
        "comparing the average scores of each player.\n"
    )
    return discord.Embed(
        title="<:increase:1496861484569989251> StampedeBot Guide : Club Scores & Management! "
              "<:increase:1496861484569989251>",
        description=description,
        color=discord.Color.blurple()
    )


def _build_howto_embed(club_config: dict) -> discord.Embed:
    """Embed 2/2 : tutoriel pas-à-pas, adapté aux salons de screenshots du club résolu."""
    screenshot_channels = club_config.get("screenshot_channels") or []
    if screenshot_channels:
        salons_txt = " or ".join(f"<#{cid}>" for cid in screenshot_channels)
        step2_intro = f"- Go to {salons_txt} and save the screenshots of the scores.\n"
    else:
        step2_intro = (
            "- Go to the channel where this event's screenshots are usually posted, and save them.\n"
        )

    description = (
        "## <a:poussin:1499364053561114804> Step 1 : Add the event\n"
        "- Use `/add_event [event_type] [date] [description]`\n"
        "   * *[event_type]* is the type of the event : **Mechs** or **Smash**\n"
        "   * *[date]* is the date of the event : YYYY-MM-DD (for example : 2026-05-20)\n"
        "   * *[description]* is optionnal. If you have something to notice for this event, you can "
        "write it here.\n\n"
        "## <:list:1499364068702818434>  Step 2 : Add scores to the event\n"
        f"{step2_intro}"
        "- Ask to an AI \"*Can you format these results as 'username1:score1, username2:score2' ?*\"\n"
        "- Copy the result\n"
        "- Use `/add_scores [event_type] [date] [scores]`\n"
        "   * *[event_type]* is the type of the event : **Mechs** or **Smash**\n"
        "   * *[date]* is the date of the event : YYYY-MM-DD (for example : 2026-05-20)\n"
        "   * *[scores]* is the scores of the event. You must paste the result of the list "
        "(username1:score1, username2:score2)\n\n"
        "## <:secu:1499364065422606407>  Step 3 : Check out the result\n"
        "- That's it ! You can now look at the various charts to see the scores of the different "
        "members and the club, with the commands listed above."
    )
    return discord.Embed(
        title="<:increase:1496861484569989251> How to manage scores ? <:increase:1496861484569989251>",
        description=description,
        color=discord.Color.blurple()
    )


class InstructionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="instructions", description="Show the full bot guide (commands + how-to)")
    @app_commands.describe(club="Which club (only needed on multi-club servers, guessed from the channel otherwise)")
    async def instructions(self, interaction: discord.Interaction, club: str = None):
        club_config = {}
        if interaction.guild_id and config.get_guild_config(interaction.guild_id):
            _, resolved = config.resolve_club(
                interaction.guild_id, channel=interaction.channel, club_override=club
            )
            if resolved:
                club_config = resolved

        embed_guide = _build_guide_embed()
        embed_howto = _build_howto_embed(club_config)
        await interaction.response.send_message(embeds=[embed_guide, embed_howto])


async def setup(bot):
    await bot.add_cog(InstructionsCog(bot))
