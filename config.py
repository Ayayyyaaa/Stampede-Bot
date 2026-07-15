import discord


# ─────────────────────────────────────────────────────────────────────────────
# STRUCTURE
#
# Chaque serveur (guild) peut contenir un ou plusieurs "clubs". Un club
# regroupe : son propre rôle Member, son propre rôle Co-lead, ses propres
# salons (règles, aide, annonces, logs, nouveaux membres, roundtable) et sa
# propre liste de membres / scores (stockée séparément dans data/{guild_id}/{club_id}/).
#
# - Pour un serveur mono-club, mettez une seule entrée dans "CLUBS" (ex: "default").
# - Pour un serveur multi-club (ex: Surge/Calamity), mettez une entrée par club
#   et renseignez "CATEGORY_ID" avec l'ID de la catégorie Discord qui contient
#   les salons de ce club : c'est ce qui permet au bot de deviner automatiquement
#   de quel club on parle en fonction du salon où une commande/réaction/message
#   a lieu.
# ─────────────────────────────────────────────────────────────────────────────

GUILDS = {
    1386634738822811698: {
        "Name": "Surging Calamity",
        "words": {
            'aya': ['✨'],
            'hus': ['✨', '<a:tianluforhus:1488296905250308317>'],
            'steel': ['👑'],
            'kazu': ['🤮', '🇧', '🇦', '🇳'],
            'kal': ['<:Raja:1488127825859838103>', '🤡'],
            'drip': ['👴'],
            'zaza': ['<:crown:1499124023710191777>'],
            'bayrou': ['<:bayrou:1499124107936272415>']
        },
        "CLUBS": {
            "default": {
                "Name": "Surging Calamity",
                "CATEGORY_ID": None,  
                "MEMBER": 1388939509151825980,
                "COLEAD": 1386638288512745543,
                "SALON_ANNONCE_ID": 1386814190723006494,
                "SALON_LOG_ID": 1395388026426753157,
                "SALON_NEW_MEMBERS": 1499355358563532871,
                "ROUNDTABLE": 1386634739296899186,
                "help1": 1386634739296899184,
                "help2": 1388626869980758207,
                "rules": 1496975331033088130,
                "advice": 1388626869980758207,
                "modos": ["AyaGus", "SteelOfDmcls", "HusGus", "Kazukaka"],
                "screenshot_channels": [1390475371714969755, 1399384407822827541],
            }
        }
    },

    # ── Serveur avec DEUX clubs séparés ────────────────────────────────────
    1272636727588294819: {
        "Name": "Surge/Calamity",
        "words": {
            'aya': ['✨'],
            'hus': ['✨', '<a:tianluforhus:1488296905250308317>'],
            'steel': ['👑'],
            'kazu': ['🤮', '🇧', '🇦', '🇳'],
            'kal': ['<:Raja:1488127825859838103>', '🤡'],
            'drip': ['👴'],
            'zaza': ['<:crown:1499124023710191777>'],
            'bayrou': ['<:bayrou:1499124107936272415>']
        },
        "CLUBS": {
            "calamity": {
                "Name": "Calamity",
                "CATEGORY_ID": 1448681953980321882,
                "MEMBER": 1448771989996044368,
                "COLEAD": 1504527597139263638,
                "SALON_ANNONCE_ID": 1524931670124400791,
                "SALON_LOG_ID": None,
                "SALON_NEW_MEMBERS": 1326945428796866621,
                "ROUNDTABLE": 1512185869237223664,
                "help1": 1387108158727782552,
                "help2": 1387108158727782552,
                "rules": 1524931670124400791,
                "advice": 1387108158727782552,
                "modos": ["AyaGus", "SteelOfDmcls", "HusGus", "Kazukaka"],
                "description": (
                    "**1 -** Let the Spawner Hit Their Mechs First. All Mechs have a 30 Second Cooldown, Even Baby Mechs and Ascended Mechs. <a:research:1488144464835776622>\n"
                    "**2 -** You Must Achieve at Least 400 Billion Damage\n"
                    "**3 -** You Need to Summon a Minimum of 125 Boss Mechs \n"
                    "**4 -** Get to 75 Summons before the final day so all the mechs summoned are 240 or higher\n"
                    "**5 -** Summon and Kill 1 Mech in the first 24 hours, so your name appears in the Damage and Summons Leaderboard\n"
                    f"**6 -** If there is anything you need regarding the event send a private message to : {' , '.join(f'**{m}**' for m in ['AyaGus', 'SteelOfDmcls', 'HusGus', 'Kazukaka'])}\n"
                    "**7 -** Enjoy ! <:netero_heart:1441402964483903540>\n"
                    "\n\n-> If you have any issues regarding the requirements or will not be available to play the event, please let us know in advance"
                ),
                "screenshot_channels": [1463394745043914785,1466782565905076348],
            },
            "surge": {
                "Name": "Surge",
                "CATEGORY_ID": 1448684653106954240,
                "MEMBER": 1272636727588294824,
                "COLEAD": 1272636727600746571,
                "SALON_ANNONCE_ID": 1272636727600746574,
                "SALON_LOG_ID": None,
                "SALON_NEW_MEMBERS": 1512185869237223664,
                "ROUNDTABLE": 1512185869237223664,
                "help1": 1387108158727782552,
                "help2": 1387108158727782552,
                "rules": 1272636727600746574,
                "advice": 1387108158727782552,
                "modos": ["CorysClips", "MattRYeo"],
                # TODO : renseigner les salons où Surge poste ses screenshots de scores
                "screenshot_channels": [1272636727600746577,1409196858131087460],
            }
        }
    },

    1341134017684308080: {
        "Name": "Stampede Of Fury",
        "CLUBS": {
            "default": {
                "Name": "Stampede Of Fury",
                "CATEGORY_ID": None,
                "MEMBER": 1378019701484945599,
                "COLEAD": 1376919653670195313,
                "SALON_ANNONCE_ID": 1487046656783548416,
                "SALON_LOG_ID": 1488162984328036442,
                "SALON_NEW_MEMBERS": 1488162984328036442,
                "ROUNDTABLE": 1380579205363929098,
                "help1": 1341156549858558145,
                "help2": 1487546393936662769,
                "rules": 1468349920237977690,
                "advice": 1341156549858558145,
                "modos": ["AyaGus", "SteelOfDmcls", "HusGus", "Kalindrov", "Kazukaka"],
                # TODO : renseigner les salons où ce club poste ses screenshots de scores
                "screenshot_channels": [1487046063834533909,1485410450723307551],
            }
        },
        "words": {
            'aya': ['✨'],
            'hus': ['✨', '<a:tianluforhus:1488296905250308317>'],
            'steel': ['👑'],
            'kazu': ['🤮', '🇧', '🇦', '🇳'],
            'kal': ['<:Raja:1488127825859838103>', '<a:rajagif:1488138198939996272>'],
            'drip': ['👴']
        }
    },

    1112682529212866620: {
        "Name": "Ayaya's server",
        "CLUBS": {
            "default": {
                "Name": "Ayaya's server",
                "CATEGORY_ID": None,
                "MEMBER": 1497614547396071504,
                "COLEAD": 1133394439453278308,
                "SALON_ANNONCE_ID": 1497614670876639363,
                "SALON_LOG_ID": 1497614885264035910,
                "SALON_NEW_MEMBERS": 1497614885264035910,
                "ROUNDTABLE": 1112682530311786508,
                "help1": 1142405433257103441,
                "help2": 1142405433257103441,
                "rules": 1135884041158131712,
                "advice": 1497615128936448091,
                "modos": ["AyaGus", "SteelOfDmcls", "HusGus", "Kalindrov", "Kazukaka"],
                # TODO : renseigner les salons où ce club poste ses screenshots de scores
                "screenshot_channels": [1135884041158131712],
            }
        },
        "words": {
            'aya': ['✨'],
            'hus': ['✨', '<a:tianluforhus:1488296905250308317>'],
            'steel': ['👑'],
            'kazu': ['🤮', '🇧', '🇦', '🇳'],
            'kal': ['<:Raja:1488127825859838103>', '🤡'],
            'drip': ['👴'],
            'zaza': ['<:crown:1499124023710191777>'],
            'bayrou': ['<:bayrou:1499124107936272415>']
        }
    }
}


factions = {
    "Cobra": ("<:Cobra:1487161398017392791>", discord.Color.dark_purple()),
    "Griffin": ("<:Griffin:1487161459707478237>", discord.Color.light_grey()),
    "Crane": ("<:Crane:1487161429458026639>", discord.Color.dark_blue()),
    "Mantis": ("<:Mantis:1487161330455674892>", discord.Color.green()),
    "Kodiak": ("<:Kodiak:1487161368086974646>", discord.Color.red()),
    "Howler": ("<:Howler:1487161297765138644>", discord.Color.orange())
}

admin = {
    'kazukuta': 689011423208013842,
    'kalindrov': 226383207510179841,
    'steel': 445665967381676032,
    'ayagus': 716927140796301312,
    'husgus': 694477321536798760
}

char_emojis = {
    "Toro": "<a:toro:1489280319503859802>",
    "Zykan": "<a:zykan:1489280289027915997>",
    "Chancer": "<a:chancer:1489282062493028372>",
    "Dax": "<a:dax:1489282899755667668>",
    "Duke": "<a:duke:1489282918760321166>",
    "Face": "<a:face:1489282939597488279>",
    "Fenrus": "<a:fenrus:1489282974342975680>",
    "Flint": "<a:flint:1489282995528532098>",
    "Gorongo": "<a:gorongo:1489283018697867344>",
    "Hana": "<a:hana:1489283043964489899>",
    "Jasper": "<a:jasper:1489283065791643840>",
    "Karma": "<a:karma:1489283083730424019>",
    "Komodo": "<a:komodo:1489283124218167406>",
    "Kotaro": "<a:kotaro:1489283150159806646>",
    "Laguna": "<a:laguna:1489283184142061810>",
    "Leene": "<a:leene:1489283207332630670>",
    "Lilly": "<a:lilly:1489283234570305717>",
    "Locke": "<a:locke:1489283273938042920>",
    "Lucius": "<a:lucius:1489283300605300836>",
    "Magus": "<a:magus:1489283342099550359>",
    "Malric": "<a:malric:1489283373342916740>",
    "Mazu": "<a:mazu:1489283419715403886>",
    "Necro": "<a:necro:1489283443220283494>",
    "Nyx": "<a:nyx:1489283483376292004>",
    "Otto": "<a:otto:1489283515240681512>",
    "Pyra": "<a:pyra:1489283871802392586>",
    "Raja": "<a:raja:1489283901473034401>",
    "Rocco": "<a:rocco:1489283925548204094>",
    "Ruby": "<a:ruby:1489283947480354876>",
    "Scythe": "<a:scythe:1489283989255491594>",
    "Safros": "<a:safros:1489283967340515430>",
    "Spekkio": "<a:spekkio:1489284013515346062>",
    "Talon": "<a:talon:1489284035531374662>",
    "Terryx": "<a:terryx:1489284057920573660>",
    "Vex": "<a:vex:1489284097301020763>",
    "Xeno": "<a:xeno:1489284128833798244>",
    "Zemus": "<a:zemus:1489284152304865391>",
    "Zura": "<a:zura:1489288387268710571>"
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS "CLUB"
# ─────────────────────────────────────────────────────────────────────────────

def get_guild_config(guild_id: int) -> dict | None:
    return GUILDS.get(guild_id)


def get_clubs(guild_id: int) -> dict:
    """Retourne le dict {club_id: club_config} du serveur (vide si non configuré)."""
    return GUILDS.get(guild_id, {}).get("CLUBS", {})


def get_words(guild_id: int) -> dict:
    return GUILDS.get(guild_id, {}).get("words", {})


def resolve_club(guild_id: int, channel=None, club_override: str | None = None):
    """
    Devine le club concerné pour ce serveur.

    Ordre de priorité :
    1. S'il n'y a qu'un seul club sur ce serveur -> on le retourne directement.
    2. Si un club a été précisé explicitement (paramètre de commande) -> on le
       cherche par id ou par nom (insensible à la casse).
    3. Sinon, on regarde la catégorie Discord du salon (`channel.category_id`)
       et on la compare à `CATEGORY_ID` de chaque club.

    Retourne (club_id, club_config) ou (None, None) si impossible à déterminer.
    """
    clubs = get_clubs(guild_id)
    if not clubs:
        return None, None

    if len(clubs) == 1:
        only_id = next(iter(clubs))
        return only_id, clubs[only_id]

    if club_override:
        key = club_override.strip().lower()
        if key in clubs:
            return key, clubs[key]
        for cid, cfg in clubs.items():
            if cfg.get("Name", "").strip().lower() == key:
                return cid, cfg

    if channel is not None:
        category_id = getattr(channel, "category_id", None)
        if category_id:
            for cid, cfg in clubs.items():
                if cfg.get("CATEGORY_ID") == category_id:
                    return cid, cfg

    return None, None


def find_club_by_role(guild_id: int, role_ids: set) -> tuple:
    """Retourne (club_id, club_config) du club dont MEMBER ou COLEAD est dans role_ids."""
    for cid, cfg in get_clubs(guild_id).items():
        if cfg.get("MEMBER") in role_ids or cfg.get("COLEAD") in role_ids:
            return cid, cfg
    return None, None