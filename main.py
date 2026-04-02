import discord
from discord import app_commands
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
from discord.app_commands import Choice

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


char_emojis = {
    "Toro": "<a:toro:1489280319503859802>",#1489281381224812637 1489280319503859802
    "Zykan" : "<a:zykan:1489280289027915997>",
    "Chancer" : "<a:chancer:1489282062493028372>",
    "Dax" : "<a:dax:1489282899755667668>",
    "Duke" : "<a:duke:1489282918760321166>",
    "Face" : "<a:face:1489282939597488279>",
    "Fenrus" : "<a:fenrus:1489282974342975680>",
    "Flint" : "<a:flint:1489282995528532098>",
    "Gorongo" : "<a:gorongo:1489283018697867344>",
    "Hana" : "<a:hana:1489283043964489899>",
    "Jasper" : "<a:jasper:1489283065791643840>",
    "Karma" : "<a:karma:1489283083730424019>",
    "Komodo" : "<a:komodo:1489283124218167406>",
    "Kotaro" : "<a:kotaro:1489283150159806646>",
    "Laguna" : "<a:laguna:1489283184142061810>",
    "Leene" : "<a:leene:1489283207332630670>",
    "Lilly" : "<a:lilly:1489283234570305717>",
    "Locke" : "<a:locke:1489283273938042920>",
    "Lucius" : "<a:lucius:1489283300605300836>",
    "Magus" : "<a:magus:1489283342099550359>",
    "Malric" : "<a:malric:1489283373342916740>",
    "Mazu" : "<a:mazu:1489283419715403886>",
    "Necro" : "<a:necro:1489283443220283494>",
    "Nyx" : "<a:nyx:1489283483376292004>",
    "Otto" : "<a:otto:1489283515240681512>",
    "Pyra" : "<a:pyra:1489283871802392586>",
    "Raja" : "<a:raja:1489283871802392586>",
    "Rocco" : "<a:rocco:1489283925548204094>",
    "Ruby" : "<a:ruby:1489283947480354876>",
    "Scythe" : "<a:scythe:1489283989255491594>",
    "Safros" : "<a:safros:1489283967340515430>",
    "Spekkio" : "<a:spekkio:1489284013515346062>",
    "Talon" : "<a:talon:1489284035531374662>",
    "Terryx" : "<a:terryx:1489284057920573660>",
    "Vex" : "<a:vex:1489284097301020763>",
    "Xeno" : "<a:xeno:1489284128833798244>",
    "Zemus" : "<a:zemus:1489284152304865391>",
    "Zura" : "<a:zura:1489288387268710571>"
}

@bot.tree.command(name="tierlist", description="Shows the tierlist of the gamemode")
@app_commands.describe(categorie="Choose the gamemode (default general)")
@app_commands.choices(categorie=[
    Choice(name="General", value="general"),
    Choice(name="Smash / Arena", value="arena"),
    Choice(name="Campaign / Sewers", value="campaign"),
    Choice(name="Faction Sewers", value="sewers"),
    Choice(name="Mechs", value="mechs")
])
async def tierlist(interaction: discord.Interaction, categorie: str = "general"):
    await interaction.response.defer()

    ranking = {
        "S": {"+": [], "": [], "-": []},
        "A": {"+": [], "": [], "-": []},
        "B": {"+": [], "": [], "-": []},
        "C": {"+": [], "": [], "-": []},
        "D": {"+": [], "": [], "-": []}
    }

    base_path = "resources/TapTap"
    
    if not os.path.exists(base_path):
        await interaction.followup.send("❌ Server error")
        return

    for dossier in os.listdir(base_path):
        chemin_dossier = os.path.join(base_path, dossier)
        
        if not os.path.isdir(chemin_dossier):
            continue

        chemin_script = os.path.join(chemin_dossier, "char.py")
        if not os.path.exists(chemin_script):
            continue

        try:
            spec = importlib.util.spec_from_file_location(f"module_{dossier}", chemin_script)
            char_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(char_module)

            perso = char_module.get_character_data()
            if categorie == "arena":
                note_brute = perso.get_arena()
            elif categorie == "campaign":
                note_brute = perso.get_campaign()
            elif categorie == "sewers":
                note_brute = perso.get_faction_sewers()
            elif categorie == "mechs":
                note_brute = perso.get_mechs()
            else:
                note_brute = perso.get_note() 

            note_complete = str(note_brute).strip().upper() 

            if not note_complete or note_complete[0] not in ranking:
                continue

            lettre = note_complete[0]
            modificateur = note_complete[1:] if len(note_complete) > 1 else ""

            if modificateur not in ["+", "", "-"]:
                modificateur = ""

            ranking[lettre][modificateur].append(perso.get_nom())

        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de {dossier} pour la tierlist: {e}")

    titres_embed = {
        "general": "<:top1:1489297584752168990> General Tier List",
        "arena": "<:arena:1488581637917769738> Smash / Arena Tier List",
        "campaign": "<:campaign:1488582421266829364> Campaign / Sewers Tier List",
        "sewers": "<:faction_sewer:1488582418985255003> Sewers Tier List",
        "mechs": "<:mecha_icon:1488150151519535144> Mechs Tier List"
    }

    embed = discord.Embed(
        title=titres_embed.get(categorie, "Tier List"),
        description="Classement des personnages, du meilleur au pire.",
        color=discord.Color.gold()
    )

    tier_emojis = {"S": "<:rangS:1489296503481696316>", "A": "<:rangA:1489296517612179507>", "B": "<:rangB:1489296532455948459>", "C": "<:rangC:1489296559987490946>", "D": "<:rangD:1489296580954554469>"}

    for lettre, modificateurs in ranking.items():
        lignes_tier = []
        
        for mod in ["+", "", "-"]:
            persos = modificateurs[mod]
            if persos:
                persos.sort() 
                
                # Conversion du nom en émoji
                persos_a_afficher = [char_emojis.get(p, p) for p in persos]
                
                lignes_tier.append(f"**{lettre}{mod}** : {' '.join(persos_a_afficher)}")

        if lignes_tier:
            emoji = tier_emojis.get(lettre, "▪️")
            embed.add_field(
                name=f"{emoji} Tier {lettre}", 
                value="\n".join(lignes_tier), 
                inline=False
            )

    await interaction.followup.send(embed=embed)






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
@discord.app_commands.describe(character_name="Character name (Zemus, Spekkio, etc.)")
async def character(interaction: discord.Interaction, character_name: str):
    dossier = character_name.capitalize()

    nom_fichier_image = f"{character_name.lower()}_icon.png"
    chemin_image = f"resources/TapTap/{dossier}/{nom_fichier_image}"
    
    nom_fichier_gif = f"{character_name.lower()}.gif"
    chemin_gif = f"resources/TapTap/{dossier}/{nom_fichier_gif}"
    
    nom_fichier_py = f"{character_name.lower()}.py"
    chemin_script = f"resources/TapTap/{dossier}/char.py"

    if not os.path.exists(chemin_script):
        await interaction.response.send_message(
            f"❌ The character **{dossier}** is misspelled, not added or too weak.", 
            ephemeral=True
        )
        return

    try:
        spec = importlib.util.spec_from_file_location(f"module_{dossier}", chemin_script)
        char_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(char_module)

        perso = char_module.get_character_data()

        fichiers_a_envoyer = []

        fichier_discord = discord.File(chemin_image, filename=nom_fichier_image)
        fichiers_a_envoyer.append(fichier_discord)

        emoji, colour = factions[perso.get_faction()]
        gros_titre = f"# {emoji} {perso.get_nom()} {emoji}\n"
        embed = discord.Embed(
            description=f"{gros_titre}**Rating : {perso.get_note()}\nFaction : {perso.get_faction()}**",
            color=colour
        )
        
        embed.add_field(name="<:arena:1488581637917769738> Arena", value=perso.get_arena(), inline=True)
        embed.add_field(name="<:campaign:1488582421266829364> Campaign / Sewers", value=perso.get_campaign(), inline=True)
        embed.add_field(name="<:faction_sewer:1488582418985255003> Smash / Faction Sewers", value=perso.get_faction_sewers(), inline=False)
        embed.add_field(name="<:mecha_icon:1488150151519535144> Mechs", value=perso.get_mechs(), inline=True)
        embed.add_field(name="<:usefull:1488293835137093683> Tips", value=perso.get_tips(), inline=False)
        
        embed.set_image(url=f"attachment://{nom_fichier_image}")

        if os.path.exists(chemin_gif):
            fichier_gif = discord.File(chemin_gif, filename=nom_fichier_gif)
            fichiers_a_envoyer.append(fichier_gif) 
            embed.set_thumbnail(url=f"attachment://{nom_fichier_gif}") 

        await interaction.response.send_message(embed=embed, files=fichiers_a_envoyer)
        
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Server error {dossier} : `{e}`", 
            ephemeral=True
        )


TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)