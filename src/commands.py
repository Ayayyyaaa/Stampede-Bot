import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import os
import importlib.util
from random import choice
import config

class CharacterCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="choice", description="Selects a random option from the options provided")
    @app_commands.describe(options="Separate your choices with commas")
    async def slash_choice(self, interaction: discord.Interaction, options: str):
        liste_choix = [c.strip() for c in options.split(',') if c.strip()]
        
        if len(liste_choix) < 2:
            await interaction.response.send_message("❌ I need at least two options separated by a comma to make a choice!", ephemeral=True)
            return

        resultat = choice(liste_choix) 
        await interaction.response.send_message(f"Between **{', '.join(liste_choix)}**...\n\n🎲 I chose : **{resultat}** !")

    @app_commands.command(name="tierlist", description="Shows the tierlist of the gamemode")
    @app_commands.describe(categorie="Choose the gamemode (default general)")
    @app_commands.choices(categorie=[
        Choice(name="General", value="general"),
        Choice(name="Arena", value="arena"),
        Choice(name="Campaign / Sewers", value="campaign"),
        Choice(name="Smash / Faction Sewers", value="sewers"),
        Choice(name="Mechs", value="mechs")
    ])
    async def tierlist(self, interaction: discord.Interaction, categorie: str = "general"):
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
            if not os.path.isdir(chemin_dossier): continue
            chemin_script = os.path.join(chemin_dossier, "char.py")
            if not os.path.exists(chemin_script): continue

            try:
                spec = importlib.util.spec_from_file_location(f"module_{dossier}", chemin_script)
                char_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(char_module)

                perso = char_module.get_character_data()
                note_brute = getattr(perso, f"get_{categorie}", perso.get_note)() if hasattr(perso, f"get_{categorie}") else perso.get_note()
                
                note_complete = str(note_brute).strip().upper() 
                if not note_complete or note_complete[0] not in ranking: continue

                lettre = note_complete[0]
                modificateur = note_complete[1:] if len(note_complete) > 1 else ""
                if modificateur not in ["+", "", "-"]: modificateur = ""

                ranking[lettre][modificateur].append(perso.get_nom())

            except Exception as e:
                print(f"⚠️ Error for the folder {dossier} for the tierlist : {e}")

        titres_embed = {
            "general": "<:top1:1489297584752168990> General Tier List",
            "arena": "<:arena:1488581637917769738> Arena Tier List",
            "campaign": "<:campaign:1488582421266829364> Campaign / Sewers Tier List",
            "sewers": "<:faction_sewer:1488582418985255003> Smash / Faction Sewers Tier List",
            "mechs": "<:mecha_icon:1488150151519535144> Mechs Tier List"
        }

        embed = discord.Embed(
            title=titres_embed.get(categorie, "Tier List"),
            description="Best characters for the selected gamemode.",
            color=discord.Color.gold()
        )

        tier_emojis = {"S": "<:rangS:1489296503481696316>", "A": "<:rangA:1489296517612179507>", "B": "<:rangB:1489296532455948459>", "C": "<:rangC:1489296559987490946>", "D": "<:rangD:1489296580954554469>"}

        for lettre, modificateurs in ranking.items():
            lignes_tier = []
            for mod in ["+", "", "-"]:
                persos = modificateurs[mod]
                if persos:
                    persos.sort() 
                    persos_a_afficher = [config.char_emojis.get(p, p) for p in persos]
                    lignes_tier.append(f"**{lettre}{mod}** : {' '.join(persos_a_afficher)}")

            if lignes_tier:
                emoji = tier_emojis.get(lettre, "▪️")
                embed.add_field(name=f"{emoji} Tier {lettre}", value="\n".join(lignes_tier), inline=False)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="character", description="Show some tips about the character")
    @app_commands.describe(character_name="Character name")
    async def character(self, interaction: discord.Interaction, character_name: str):
        dossier = character_name.capitalize()
        nom_fichier_image = f"{character_name.lower()}_icon.png"
        chemin_image = f"resources/TapTap/{dossier}/{nom_fichier_image}"
        nom_fichier_gif = f"{character_name.lower()}.gif"
        chemin_gif = f"resources/TapTap/{dossier}/{nom_fichier_gif}"
        chemin_script = f"resources/TapTap/{dossier}/char.py"

        if not os.path.exists(chemin_script):
            await interaction.response.send_message(f"❌ The character **{dossier}** is misspelled, not added or too weak.", ephemeral=True)
            return

        try:
            spec = importlib.util.spec_from_file_location(f"module_{dossier}", chemin_script)
            char_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(char_module)

            perso = char_module.get_character_data()
            fichiers_a_envoyer = [discord.File(chemin_image, filename=nom_fichier_image)]

            emoji, colour = config.factions[perso.get_faction()]
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
                fichiers_a_envoyer.append(discord.File(chemin_gif, filename=nom_fichier_gif)) 
                embed.set_thumbnail(url=f"attachment://{nom_fichier_gif}") 

            await interaction.response.send_message(embed=embed, files=fichiers_a_envoyer)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Server error {dossier} : `{e}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CharacterCommandsCog(bot))