import discord
from discord.ext import commands
import os
from random import randint, choice, sample
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
from discord.ext import tasks
import datetime
from zoneinfo import ZoneInfo
import re
import asyncio
import importlib.util

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True 
intents.reactions = True
bot = commands.Bot(command_prefix="stampede", intents=intents)
furymember = 1378019701484945599 #1135533413957378108 #1378019701484945599
colead = 1376919653670195313 #1376919653670195313
SALON_ANNONCE_ID = 1487046656783548416
SALON_LOG_ID = 1488162984328036442
ROUNDTABLE = 1380579205363929098
factions = {"Cobra" : ("<:Cobra:1487161398017392791>",discord.Color.dark_purple()),
            "Griffin" : ("<:Griffin:1487161459707478237>",discord.Color.light_grey()),
            "Crane" : ("<:Crane:1487161429458026639>",discord.Color.dark_blue()),
            "Mantis" : ("<:Mantis:1487161330455674892>",discord.Color.green()),
            "Kodiak" : ("<:Kodiak:1487161368086974646>",discord.Color.red()),
            "Howler" : ("<:Howler:1487161297765138644>",discord.Color.orange())}

admin = {'kazukuta' : 689011423208013842,
         'kalindrov': 226383207510179841,
         'steel' : 445665967381676032,
         'ayagus' : 716927140796301312,
         'husgus' : 694477321536798760}


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
        value=(
            "Use **/faction [faction-name]** to chose :\n\n"
            " <:Cobra:1487161398017392791> **Cobra** \n"
            " <:Griffin:1487161459707478237> **Griffin** \n"
            " <:Crane:1487161429458026639> **Crane** \n"
            " <:Mantis:1487161330455674892> **Mantis** \n"
            " <:Kodiak:1487161368086974646> **Kodiak** \n"
            " <:Howler:1487161297765138644> **Howler** "
        ),
        inline=False
    )

    await message.channel.send(content=f"Bienvenue {auteur.mention} !", embed=embed)
    
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
    
    if message.channel.id == ROUNDTABLE:
        if message.author.id in [admin['kazukuta'], admin['husgus']]:
            heure_actuelle = datetime.datetime.now(ZoneInfo("Europe/Paris")).hour
            if 0 <= heure_actuelle < 6:
                try:
                    await message.add_reaction("🌿") 
                except discord.HTTPException:
                    pass
                if randint(1, 10) == 1:
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
    contenu_minuscule = contenu_minuscule.replace('-','')
    contenu_minuscule = contenu_minuscule.replace('/','')
    contenu_minuscule = contenu_minuscule.replace('_','')
    if re.search(r'\b67\b', contenu_minuscule):
        await message.channel.send('https://klipy.com/gifs/cat-67')
    await bot.process_commands(message)

def creer_embed_mech():
    nom_image = "resources/eventmechas.png"
    nom_image2 = "resources/tapforce.png"
    FICHIER = discord.File(nom_image, filename=nom_image)
    FICHIER2 = discord.File(nom_image2, filename=nom_image2)
    embed = discord.Embed(
        title= "<:mecha_icon:1488150151519535144> Rules of the Mech Event in Stampede Of Fury <:mecha_icon:1488150151519535144>",
        description=(
        "**1 -** Dont kill mechs 200 <:lvlmecha:1488149380346286212> and below of other players, and avoid finishing off mechs unless the player doesn't mind\n"
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
        title= "<:mech:1487413876139102358> Rules of the Smash Event in Stampede Of Fury <:mech:1487413876139102358>", # Titre cliquable si vous ajoutez url="https://..."
        description=(
        "**1 -** Buy tickets at least once a day <:Pvpticket:1487183172134371388>\n"
        "**2 -** Use yours PvP tickets on day 1 until you get 4 boss tickets <:Bosstickets:1487183138273755166> \n"
        "**3 -** Attack the boss once a day\n"
        "**3 -** Use all your PvP tickets the last day (day 5) to take advantage of x2 points ! <:smashpoint:1487425123718795367>\n"
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

@bot.tree.command(name="rule_mechs", description="Show the rules for mechs events")
async def rule_mech(interaction: discord.Interaction):
    embed, fichiers = creer_embed_mech()
    embed.set_author(name=f"Announce by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed, files=fichiers)

@bot.tree.command(name="rule_smash", description="Show the rules for smashs events")
async def rule_mech(interaction: discord.Interaction):
    embed, fichiers = creer_embed_smash()
    embed.set_author(name=f"Announce by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed, files=fichiers)


heure_envoi = datetime.time(hour=0, minute=0, tzinfo=ZoneInfo("Europe/Paris"))
bot.utiliser_annonce_smash = True

@tasks.loop(time=heure_envoi)
async def annonce_vendredi():
    if datetime.datetime.now(ZoneInfo("Europe/Paris")).weekday() != 4:
        return
        
    salon = bot.get_channel(SALON_ANNONCE_ID)
    if not salon:
        return

    message_texte = "📣 **Event is coming ! Here is a quick reminder of the rules** <@&1378019701484945599>"
    
    # Tu appelles tes nouvelles fonctions ici !
    if bot.utiliser_annonce_smash:
        # Fais pareil pour creer_embed_smash()
        mon_embed, mes_fichiers = creer_embed_smash() 
    else:
        mon_embed, mes_fichiers = creer_embed_mech()

    await salon.send(content=message_texte, embed=mon_embed, files=mes_fichiers)
    bot.utiliser_annonce_smash = not bot.utiliser_annonce_smash

@bot.event
async def on_message_delete(message):
    salon_log = bot.get_channel(SALON_LOG_ID)
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
            print("❌ Erreur : Le bot n'a pas la permission 'Voir les logs d'audit' (View Audit Log) sur le serveur !")

    embed = discord.Embed(
        title="🗑️ Deleted Message",
        description=message.content or "*Message sans texte (image, embed...)*",
        color=discord.Color.red(),
        timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
    )

    embed.add_field(name="Author", value=message.author.mention, inline=True)
    
    # Si le suppresseur est l'auteur, on affiche "Himself"
    nom_suppresseur = "Himself" if suppresseur == message.author else suppresseur.mention
    embed.add_field(name="Deleted by", value=nom_suppresseur, inline=True)
    
    embed.add_field(name="Channel", value=message.channel.mention, inline=False)
    embed.set_thumbnail(url=message.author.display_avatar.url)
    
    await salon_log.send(embed=embed)

@bot.tree.command(name="choice", description="Selects a random option from the options provided")
@discord.app_commands.describe(options="Separate your choices with commas (e.g. heads, tails)")
async def slash_choice(interaction: discord.Interaction, options: str):
    liste_choix = [c.strip() for c in options.split(',') if c.strip()]
    
    if len(liste_choix) < 2:
        await interaction.response.send_message(
            "❌ I need at least two options separated by a comma to make a choice!", 
            ephemeral=True 
        )
        return

    resultat = choice(liste_choix) 

    await interaction.response.send_message(f"Between **{', '.join(liste_choix)}**...\n\n🎲 I chose : **{resultat}** !")



@bot.tree.command(name="character", description="Show some tips about the character")
@discord.app_commands.describe(character_name="Nom du personnage (ex: Raja, Cobra, etc.)")
async def character(interaction: discord.Interaction, character_name: str):
    dossier = character_name.capitalize()
    
    # --- CHEMINS ---
    nom_fichier_image = f"{character_name.lower()}_icon.png"
    chemin_image = f"resources/TapTap/{dossier}/{nom_fichier_image}"
    
    nom_fichier_gif = f"{character_name.lower()}.gif"
    chemin_gif = f"resources/TapTap/{dossier}/{nom_fichier_gif}"
    
    nom_fichier_py = f"{character_name.lower()}.py"
    chemin_script = f"resources/TapTap/{dossier}/{nom_fichier_py}"

    if not os.path.exists(chemin_script):
        await interaction.response.send_message(
            f"❌ Les données pour le personnage **{dossier}** n'existent pas encore ou sont mal orthographiées.", 
            ephemeral=True
        )
        return

    try:
        spec = importlib.util.spec_from_file_location(f"module_{dossier}", chemin_script)
        char_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(char_module)

        perso = char_module.get_character_data()

        # --- GESTION DES FICHIERS ---
        fichiers_a_envoyer = []
        
        # On ajoute l'icône à la liste
        fichier_discord = discord.File(chemin_image, filename=nom_fichier_image)
        fichiers_a_envoyer.append(fichier_discord)

        # --- CRÉATION DE L'EMBED ---
        emoji, colour = factions[perso.get_faction()]
        espaces_centrage = "⠀⠀⠀"
        gros_titre = f"# {espaces_centrage}{emoji} {perso.get_nom()} {emoji}\n"
        embed = discord.Embed(
            title=f"{emoji} {perso.get_nom()} {emoji}",
            description=f"{gros_titre}**Rating : {perso.get_note()}\nFaction : {perso.get_faction()}**",
            color=colour
        )
        
        embed.add_field(name="💡 Astuce 1", value=perso.get_astuce1(), inline=False)
        embed.add_field(name="💡 Astuce 2", value=perso.get_astuce2(), inline=False)
        embed.add_field(name="🗡️ Points forts", value=perso.get_points_forts(), inline=True)
        embed.add_field(name="🛡️ Faiblesses", value=perso.get_faiblesses(), inline=True)
        
        embed.set_thumbnail(url=f"attachment://{nom_fichier_image}")

        if os.path.exists(chemin_gif):
            fichier_gif = discord.File(chemin_gif, filename=nom_fichier_gif)
            fichiers_a_envoyer.append(fichier_gif) 
            embed.set_image(url=f"attachment://{nom_fichier_gif}") 

        await interaction.response.send_message(embed=embed, files=fichiers_a_envoyer)
        
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Erreur lors du chargement des données de {dossier} : `{e}`", 
            ephemeral=True
        )


TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)