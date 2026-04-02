import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
from zoneinfo import ZoneInfo
import config

def creer_embed_mech():
    nom_image = "resources/eventmechas.png"
    nom_image2 = "resources/tapforce.png"
    FICHIER = discord.File(nom_image, filename=nom_image)
    FICHIER2 = discord.File(nom_image2, filename=nom_image2)
    embed = discord.Embed(
        title= "<:mecha_icon:1488150151519535144> Rules of the Mech Event in Stampede Of Fury <:mecha_icon:1488150151519535144>",
        description=(
            "**1 -** Dont kill mechs 180 <:mech180:1488607738404671648> and below of other players, and avoid finishing off mechs unless the player doesn't mind\n"
            "**2 -** Always buy the daily 500 gem phone packs <:greyphone:1487424771200254013> -> if you have any gold phones <:goldphone:1488139733841346662> you can't use, convert them to gray phones\n"
            "**3 -** Always allow the spawner to get the first hit unless 5 minutes pass <a:research:1488144464835776622>\n"
            "**4 -** If there is anything you need regarding the event send a private message to : **AyaGus** , **SteelOfDmcls** , **HusGus** , **Kalindrov** or **Kazukaka**\n"
            "**5 -** Enjoy ! <:netero_heart:1441402964483903540>\n"
        ),
        color=discord.Color.red(),
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="<:optis:1488294635519479918> Need optimizations ?", value="<#1341156549858558145> or <#1487546393936662769> for customised optimisation by our moderators\n", inline=True) 
    embed.add_field(name="🎯 Objectives", value="100 pops per person, we can reach the 3000 !", inline=False)
    embed.set_thumbnail(url=f"attachment://{nom_image2}") 
    embed.set_image(url=f"attachment://{nom_image}")
    embed.set_footer(text="Stampede Of Fury !")
    return embed, [FICHIER2, FICHIER]

def creer_embed_smash():
    nom_image = "resources/smashevent.png"
    nom_image2 = "resources/tapforce.png"
    FICHIER = discord.File(nom_image, filename=nom_image)
    FICHIER2 = discord.File(nom_image2, filename=nom_image2)
    embed = discord.Embed(
        title= "<:mech:1487413876139102358> Rules of the Smash Event in Stampede Of Fury <:mech:1487413876139102358>",
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
    embed.add_field(name="<:optis:1488294635519479918> Need optimizations ?", value="<#1341156549858558145> or <#1487546393936662769> for customised optimisation by our moderators\n", inline=True) 
    embed.add_field(name="🎯 Objectives", value="Follow the strategy, you can reach the 400 smash point ! <:smashpoint:1487425123718795367>", inline=False)
    embed.set_thumbnail(url=f"attachment://{nom_image2}") 
    embed.set_image(url=f"attachment://{nom_image}")
    embed.set_footer(text="Stampede Of Fury !")
    return embed, [FICHIER2, FICHIER]

class AnnouncementsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utiliser_annonce_smash = True
        self.annonce_vendredi.start()

    def cog_unload(self):
        self.annonce_vendredi.cancel()

    @app_commands.command(name="rule_mechs", description="Show the rules for mechs events")
    async def rule_mechs(self, interaction: discord.Interaction):
        embed, fichiers = creer_embed_mech()
        embed.set_author(name=f"Announce by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, files=fichiers)

    @app_commands.command(name="rule_smash", description="Show the rules for smashs events")
    async def rule_smash(self, interaction: discord.Interaction):
        embed, fichiers = creer_embed_smash()
        embed.set_author(name=f"Announce by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, files=fichiers)

    @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=ZoneInfo("Europe/Paris")))
    async def annonce_vendredi(self):
        if datetime.datetime.now(ZoneInfo("Europe/Paris")).weekday() != 4:
            return
            
        salon = self.bot.get_channel(config.SALON_ANNONCE_ID)
        if not salon:
            return

        message_texte = "📣 **Event is coming ! Here is a quick reminder of the rules** <@&1378019701484945599>"
        
        if self.utiliser_annonce_smash:
            mon_embed, mes_fichiers = creer_embed_smash() 
        else:
            mon_embed, mes_fichiers = creer_embed_mech()

        await salon.send(content=message_texte, embed=mon_embed, files=mes_fichiers)
        self.utiliser_annonce_smash = not self.utiliser_annonce_smash

    @annonce_vendredi.before_loop
    async def before_annonce(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AnnouncementsCog(bot))