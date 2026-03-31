import discord

def get_data(path, imgname):
    fichier_image = discord.File(path, filename=imgname)
    
    # Création de l'Embed personnalisé
    embed = discord.Embed(
        title="🛡️ Chancer - Le Roi des Bêtes",
        description="Voici les astuces incontournables pour bien jouer Chancer en équipe.",
        color=discord.Color.gold() 
    )
    
    # Ajout des champs
    embed.add_field(name="🗡️ Points forts", value="• Gros dégâts de zone\n• Très mobile", inline=False)
    embed.add_field(name="🛡️ Faiblesses", value="• Faible en 1 contre 1\n• Sensible aux contrôles", inline=False)
    
    # On lie l'image à la miniature (CORRECTION : on enlève le .png ici car imgname le contient déjà)
    embed.set_thumbnail(url=f"attachment://{imgname}")
    
    # On renvoie les deux objets pour que la commande principale s'en serve
    return embed, fichier_image