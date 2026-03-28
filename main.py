import discord
from discord.ext import commands
import os
from random import randint, choice, sample
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
from discord.ext import tasks
import datetime
from zoneinfo import ZoneInfo

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True 
intents.reactions = True
bot = commands.Bot(command_prefix="stampede", intents=intents)
furymember = 1378019701484945599 #1135533413957378108 #1378019701484945599
colead = 1376919653670195313 #1376919653670195313
SALON_ANNONCE_ID = 1487046656783548416

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    if not annonce_vendredi.is_running():
        annonce_vendredi.start()
        print("⏱️ Tâche des annonces démarrée !")
    try:
        await bot.tree.sync()
        print("✅ Bot en ligne.")
    except Exception as e:
        print(f"❌ Erreur lors du chargement de l'extension : {e}")


@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.emoji) != '🐘':
        return
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    react_author = guild.get_member(payload.user_id)
    if not react_author:
        return
    lead = any(role.id == colead for role in react_author.roles)
    if not lead:
        return
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    
    auteur = message.author
    role = guild.get_role(furymember)
    await message.channel.send(f"Welcome {auteur.display_name} ! You've been accepted by {react_author.display_name}. You're now a Stampede Of Fury member !\nYou can read the rules in <#1468349920237977690> and ask any question in <#1341156549858558145> !\n\nYou can choose your roles with **/faction [faction-name]** :\n - Cobra  <:Cobra:1487161398017392791> \n -  Griffin <:Griffin:1487161459707478237> \n - Crane  <:Crane:1487161429458026639> \n - Mantis  <:Mantis:1487161330455674892>\n - Kodiak  <:Kodiak:1487161368086974646>\n - Howler  <:Howler:1487161297765138644> ")
    if not role:
        print("Erreur, le rôle n'existe pas")
        return
    try:
        await auteur.add_roles(role)
        print(f"Le rôle a bien été ajouté à {auteur.display_name} par {react_author.display_name}")
    except discord.Forbidden:
        print("Erreur : Le bot n'a pas la permission de donner ce rôle !")
    except discord.HTTPException as e:
        print(f"Erreur discord : {e}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
        
    contenu_minuscule = message.content.lower()

    words = {'aya' : '✨', 'hus' : '✨', 'steel' : '👑', 'kazu' : '🤮'}
    for mot, emoji in words.items():
        if mot in contenu_minuscule:
            try:
                await message.add_reaction(emoji)
            except discord.HTTPException:
                pass 
    if '67' in contenu_minuscule:
        await message.channel.send('https://klipy.com/gifs/cat-67')
    await bot.process_commands(message)


@bot.tree.command(name="rule_mechs", description="Show the rules for mechs events")
async def rule_mech(interaction: discord.Interaction):
    nom_image = "resources/eventmechas.png"
    nom_image2 = "resources/tapforce.png"
    FICHIER = discord.File(nom_image, filename=nom_image)
    FICHIER2 = discord.File(nom_image2, filename=nom_image2)
    embed = discord.Embed(
        title= "<:mech:1487413876139102358> Rules of the Mech Event in Stampede Of Fury <:mech:1487413876139102358>", # Titre cliquable si vous ajoutez url="https://..."
        description=(
        "**1 -** Dont kill mechs 200 and below of other players, and avoid finishing off mechs unless the player doesn't mind\n"
        "**2 -** Always buy the daily 500 gem phone packs -> if you have any gold phones you can't use, convert them to gray phones\n"
        "**3 -** If there is anything you need regarding the event send a private message to : **AyaGus** , **SteelOfDmcls** , **HusGus** , **Kalindrov** or **Kazukaka**\n"
        "**4 -** Enjoy ! <:Bosstickets:1487196821045645413>"
    ),
        color=discord.Color.red(),
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="📍 Need optimizations ?", value="<#1341156549858558145>", inline=True) 
    embed.add_field(name="🎯 Objectives", value="100 pops per person, we can reach the 3000 !", inline=False)

    embed.set_thumbnail(url=f"attachment://{nom_image2}") 
    embed.set_image(url=f"attachment://{nom_image}")

    embed.set_author(name=f"Announce by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text="Stampede Of Fury !")

    await interaction.response.send_message(embed=embed, files=[FICHIER2, FICHIER])

@bot.tree.command(name="rule_smash", description="Show the rules for smash events")
async def rule_smash(interaction: discord.Interaction):
    nom_image = "resources/smashevent.png"
    nom_image2 = "resources/tapforce.png"
    FICHIER = discord.File(nom_image, filename=nom_image)
    FICHIER2 = discord.File(nom_image2, filename=nom_image2)
    embed = discord.Embed(
        title= "<:mech:1487413876139102358> Rules of the Mech Event in Stampede Of Fury <:mech:1487413876139102358>", # Titre cliquable si vous ajoutez url="https://..."
        description=(
        "**1 -** Buy tickets at least once a day <:Pvpticket:1487183172134371388>\n"
        "**2 -** Use yours PvP tickets on day 1 until you get 4 boss tickets <:Bosstickets:1487183138273755166> \n"
        "**3 -** Attack the boss once a day\n"
        "**3 -** Use all your PvP tickets the last day (day 5) to take advantage of x2 points ! 🎉\n"
        "**5 -** Enjoy ! <:netero_heart:1441402964483903540>"
    ),
        color=discord.Color.red(),
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="📍 Need optimizations ?", value="<#1341156549858558145>", inline=True) 
    embed.add_field(name="🎯 Objectives", value="Follow the strategy, you can reach the 400 smash point !", inline=False)

    embed.set_thumbnail(url=f"attachment://{nom_image2}") 
    embed.set_image(url=f"attachment://{nom_image}")

    embed.set_author(name=f"Announce by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text="Stampede Of Fury !")

    await interaction.response.send_message(embed=embed, files=[FICHIER2, FICHIER])



heure_envoi = datetime.time(hour=0, minute=0, tzinfo=ZoneInfo("Europe/Paris"))
bot.utiliser_annonce_smash = True

@tasks.loop(time=heure_envoi)
async def annonce_vendredi():
    if datetime.datetime.now(ZoneInfo("Europe/Paris")).weekday() != 4:
        return
        
    salon = bot.get_channel(SALON_ANNONCE_ID)
    if not salon:
        print("Erreur : Salon d'annonce introuvable.")
        return

    message_texte = "📣 **Event is coming ! Here is a quick reminder of the rules** <@&1378019701484945599>"
    

    if bot.utiliser_annonce_smash:
        mon_embed, mes_fichiers = rule_smash()
    else:
        mon_embed, mes_fichiers = rule_mech()

    await salon.send(content=message_texte, embed=mon_embed, files=mes_fichiers)

    bot.utiliser_annonce_smash = not bot.utiliser_annonce_smash

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)