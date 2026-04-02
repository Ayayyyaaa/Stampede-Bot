import discord
from discord.ext import commands
import datetime
from zoneinfo import ZoneInfo
import re
import asyncio
import config # On importe ton fichier de configuration

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) != '🐘':
            return
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        react_author = guild.get_member(payload.user_id)
        if not react_author:
            return
        
        lead = any(role.id == config.COLEAD for role in react_author.roles)
        if not lead:
            return
        
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        auteur = message.author
        role = guild.get_role(config.FURYMEMBER)
        
        embed = discord.Embed(
            title="<:Raja:1488127825859838103> Welcome in Stampede Of Fury ! <:Raja:1488127825859838103>",
            description=f"Congratulations **{auteur.display_name}**, you've been accepted by **{react_author.display_name}** !\nYou're now a SoF member !\n",
            color=discord.Color.dark_purple()
        )
        if auteur.avatar:
            embed.set_thumbnail(url=auteur.avatar.url)

        embed.add_field(
            name="<a:research:1488144464835776622> Useful channels",
            value="• Read the rules in <#1468349920237977690>\n• Ask your questions in <#1341156549858558145>\n",
            inline=False
        )
        embed.add_field(
            name="<:faction:1488292952618045440> Chose your faction",
            value="Use **/faction [faction-name]** to chose :\n\n"
                  " <:Cobra:1487161398017392791> **Cobra** \n"
                  " <:Griffin:1487161459707478237> **Griffin** \n"
                  " <:Crane:1487161429458026639> **Crane** \n"
                  " <:Mantis:1487161330455674892> **Mantis** \n"
                  " <:Kodiak:1487161368086974646> **Kodiak** \n"
                  " <:Howler:1487161297765138644> **Howler** ",
            inline=False
        )

        await message.channel.send(content=f"Bienvenue {auteur.mention} !", embed=embed)
        
        if role:
            try:
                await auteur.add_roles(role)
            except discord.HTTPException as e:
                print(f"Erreur discord : {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.channel.id == config.ROUNDTABLE:
            if message.author.id in [config.admin['kazukuta'], config.admin['husgus']]:
                heure_actuelle = datetime.datetime.now(ZoneInfo("Europe/Paris")).hour
                if 0 <= heure_actuelle < 6:
                    try:
                        await message.add_reaction("🌿") 
                    except discord.HTTPException:
                        pass
                    import random
                    if random.randint(1, 10) == 1:
                        await message.reply("Go touch grass 🌱")
            
        contenu_minuscule = message.content.lower()
        words = {
            'aya' : ['✨'], 
            'hus' : ['✨','<a:tianluforhus:1488296905250308317>'], 
            'steel' : ['👑'], 
            'kazu' : ['🤮', '🇧', '🇦', '🇳'],
            'kal' : ['<:Raja:1488127825859838103>', '<a:rajagif:1488138198939996272>'], 
            'drip' : ['👴']
        }
        for mot, liste in words.items():
            if mot in contenu_minuscule:
                for emoji in liste:
                    try:
                        await message.add_reaction(emoji)
                    except discord.HTTPException:
                        pass 
                        
        contenu_minuscule = contenu_minuscule.replace('-','').replace('/','').replace('_','')
        if re.search(r'\b67\b', contenu_minuscule):
            await message.channel.send('https://klipy.com/gifs/cat-67')

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        salon_log = self.bot.get_channel(config.SALON_LOG_ID)
        if not salon_log:
            return

        suppresseur = message.author

        if message.guild:
            await asyncio.sleep(3)
            try:
                async for entree in message.guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=5):
                    if entree.target.id == message.author.id:
                        temps_ecoule = discord.utils.utcnow() - entree.created_at
                        if temps_ecoule.total_seconds() < 15:
                            suppresseur = entree.user
                            break 
            except discord.Forbidden:
                pass

        embed = discord.Embed(
            title="🗑️ Deleted Message",
            description=message.content or "*Message sans texte (image, embed...)*",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )
        embed.add_field(name="Author", value=message.author.mention, inline=True)
        nom_suppresseur = "Himself" if suppresseur == message.author else suppresseur.mention
        embed.add_field(name="Deleted by", value=nom_suppresseur, inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.set_thumbnail(url=message.author.display_avatar.url)
        
        await salon_log.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EventsCog(bot))