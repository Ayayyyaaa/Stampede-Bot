from character import Personnage

def get_character_data():
    chancer = Personnage(
        nom="Dax",
        faction="Cobra",
        note="9/10",
        astuce1="Utilisez sa compétence A pour infliger des dégâts de zone massifs.",
        astuce2="Gardez son ultime pour le bon moment lors des combats de groupe.",
        points_forts="• Gros dégâts de zone\n• Très mobile",
        faiblesses="• Faible en 1 contre 1\n• Sensible aux contrôles"
    )
    return chancer