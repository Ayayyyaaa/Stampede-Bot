import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
from zoneinfo import ZoneInfo
import config

def _format_modos(modos: list) -> str:
    return " , ".join(f"**{m}**" for m in modos)


def creer_embed_mech(server_name: str, help1: str, help2: str, modos: list, desc: str = None):
    nom_image = "resources/eventmechas.png"
    nom_image2 = "resources/tapforce.png"
    FICHIER = discord.File(nom_image, filename=nom_image)
    FICHIER2 = discord.File(nom_image2, filename=nom_image2)

    if desc:
        txt = desc
    else:
        txt = (
            "**1 -** Dont kill mechs 180 <:mech180:1488607738404671648> and below of other players, and avoid finishing off mechs unless the player doesn't mind\n"
            "**2 -** Always buy the daily 500 gem phone packs <:greyphone:1487424771200254013> -> if you have any gold phones <:goldphone:1488139733841346662> you can't use, convert them to gray phones\n"
            "**3 -** Always allow the spawner to get the first hit unless 5 minutes pass <a:research:1488144464835776622>\n"
            f"**4 -** If there is anything you need regarding the event send a private message to : {_format_modos(modos)}\n"
            "**5 -** Enjoy ! <:netero_heart:1441402964483903540>\n"
        )

    embed = discord.Embed(
        title=f"<:mecha_icon:1488150151519535144> Rules of the Mech Event in {server_name} <:mecha_icon:1488150151519535144>",
        description=txt,
        color=discord.Color.red(),
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="<:optis:1488294635519479918> Need optimizations ?", value=f"<#{help1}> or <#{help2}> for customised optimisation by our moderators\n", inline=True)
    embed.set_thumbnail(url=f"attachment://{nom_image2}")
    embed.set_image(url=f"attachment://{nom_image}")
    embed.set_footer(text=f"{server_name} !")
    return embed, [FICHIER2, FICHIER]

def creer_embed_smash(server_name: str, help1: str, help2: str, modos: list):
    nom_image = "resources/smashevent.png"
    nom_image2 = "resources/tapforce.png"
    FICHIER = discord.File(nom_image, filename=nom_image)
    FICHIER2 = discord.File(nom_image2, filename=nom_image2)
    embed = discord.Embed(
        title=f"<:mech:1487413876139102358> Rules of the Smash Event in {server_name} <:mech:1487413876139102358>",
        description=(
            "**1 -** Buy tickets at least once a day <:Pvpticket:1487183172134371388>\n"
            "**2 -** Use yours PvP tickets on day 1 until you get 4 boss tickets <:Bosstickets:1487183138273755166> \n"
            "**3 -** Attack the boss once a day\n"
            "**4 -** Use all your PvP tickets the last day (day 5) to take advantage of x2 points ! <:smashpoint:1487425123718795367>\n"
            "**5 -** Enjoy ! <:netero_heart:1441402964483903540>\n"
        ),
        color=discord.Color.gold(),
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="<:optis:1488294635519479918> Need optimizations ?", value=f"<#{help1}> or <#{help2}> for customised optimisation by our moderators\n", inline=True)
    embed.set_thumbnail(url=f"attachment://{nom_image2}")
    embed.set_image(url=f"attachment://{nom_image}")
    embed.set_footer(text=f"{server_name} !")
    return embed, [FICHIER2, FICHIER]

class AnnouncementsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utiliser_annonce_smash = False
        self.annonce_vendredi.start()

    def cog_unload(self):
        self.annonce_vendredi.cancel()

    async def _resolve(self, interaction: discord.Interaction, club: str | None):
        """Résout le club et renvoie sa config, ou répond avec un message d'erreur."""
        club_id, club_config = config.resolve_club(interaction.guild_id, channel=interaction.channel, club_override=club)
        if not club_config:
            clubs = config.get_clubs(interaction.guild_id)
            options = ", ".join(f"**{c.get('Name', cid)}**" for cid, c in clubs.items())
            await interaction.response.send_message(
                f"❌ I can't tell which club this concerns. Use this command in a channel that belongs to the right "
                f"club's category, or specify the `club` option ({options}).",
                ephemeral=True
            )
            return None
        return club_config

    @app_commands.command(name="rule_mechs", description="Show the rules for mechs events")
    @app_commands.describe(club="Which club (only needed on multi-club servers, guessed from the channel otherwise)")
    async def rule_mechs(self, interaction: discord.Interaction, club: str = None):
        cc = await self._resolve(interaction, club)
        if not cc:
            return
        help1, help2 = cc.get("help1", "0"), cc.get("help2", "0")
        modos = cc.get("modos", [])
        desc = cc.get("description")
        embed, fichiers = creer_embed_mech(cc.get("Name", interaction.guild.name), help1, help2, modos, desc)
        embed.set_author(name=f"Announce by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, files=fichiers)

    @app_commands.command(name="rule_smash", description="Show the rules for smashs events")
    @app_commands.describe(club="Which club (only needed on multi-club servers, guessed from the channel otherwise)")
    async def rule_smash(self, interaction: discord.Interaction, club: str = None):
        cc = await self._resolve(interaction, club)
        if not cc:
            return
        help1, help2 = cc.get("help1", "0"), cc.get("help2", "0")
        modos = cc.get("modos", [])
        embed, fichiers = creer_embed_smash(cc.get("Name", interaction.guild.name), help1, help2, modos)
        embed.set_author(name=f"Announce by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, files=fichiers)

    @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=ZoneInfo("Europe/Paris")))
    async def annonce_vendredi(self):
        if datetime.datetime.now(ZoneInfo("Europe/Paris")).weekday() != 4:
            return

        for guild_id, guild_config in config.GUILDS.items():
            guild = self.bot.get_guild(guild_id)

            for club_id, club_config in config.get_clubs(guild_id).items():
                salon = self.bot.get_channel(club_config.get("SALON_ANNONCE_ID"))
                if not salon:
                    continue
                if club_config.get("Name") in ("Surging Calamity","Surge"):
                    continue

                desc = club_config.get("description")
                server_name = club_config.get("Name") or (guild.name if guild else "Unknown")

                help1 = club_config.get("help1", "0")
                help2 = club_config.get("help2", "0")
                modos = club_config.get("modos", [])

                member_role_id = club_config.get("MEMBER")
                if not member_role_id:
                    continue
                message_texte = f"📣 **Event is coming ! Here is a quick reminder of the rules** <@&{member_role_id}>\nI would like All club members to add a 🔥 reaction to the requirement points so we know you will follow the rules."

                if self.utiliser_annonce_smash:
                    mon_embed, mes_fichiers = creer_embed_smash(server_name, help1, help2, modos)
                else:
                    mon_embed, mes_fichiers = creer_embed_mech(server_name, help1, help2, modos, desc)

                await salon.send(content=message_texte, embed=mon_embed, files=mes_fichiers)

        self.utiliser_annonce_smash = not self.utiliser_annonce_smash

    @annonce_vendredi.before_loop
    async def before_annonce(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AnnouncementsCog(bot))