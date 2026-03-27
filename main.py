import discord
from discord.ext import commands
from random import randint, choice, sample
from discord.ext.commands import has_permissions, MissingPermissions

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True 
intents.reactions = True
bot = commands.Bot(command_prefix="stampede", intents=intents)
furymember = 1135533413957378108 #1378019701484945599
colead = 1133394439453278308 #1376919653670195313

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        await bot.tree.sync()
        print("✅ Extension 'invocs' et commandes slash synchronisées.")
    except Exception as e:
        print(f"❌ Erreur lors du chargement de l'extension : {e}")

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        await bot.tree.sync()
        print("✅ Extension 'invocs' et commandes slash synchronisées.")
    except Exception as e:
        print(f"❌ Erreur lors du chargement de l'extension : {e}")

@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    react_author = guild.get_member(payload.user_id)
    lead = any(role.id == colead for role in react_author.roles)
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    auteur = message.author
    await message.channel.send(f"Welcome {auteur.display_name} ! You've been accepted by {react_author.display_name}. You're now a Stampede Of Fury member !\nYou can read the rules in <#1468349920237977690> and ask any question in <#1341156549858558145>")
    if str(payload.emoji) != '🐘':
        return
    if not guild:
        return
    
    if not react_author:
        return
        
    
    if not lead:
        return
    
    role = guild.get_role(furymember)
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


bot.run('MTQ4NzA4MzEyMDYwNzEwNTA2NQ.GF56Xe.kg9L6FfwqxGFFuuZTivqa-QDW_FYWVOvg_XHkg')