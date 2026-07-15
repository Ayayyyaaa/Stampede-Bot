import discord


GUILDS = {
    1386634738822811698 : {
        "Name": "Surging Calamity",
        "MEMBER" : 1388939509151825980,
        "COLEAD" : 1386638288512745543,
        "SALON_ANNONCE_ID" : 1386814190723006494,
        "SALON_LOG_ID" : 1395388026426753157,
        "SALON_NEW_MEMBERS" : 1499355358563532871,
        "ROUNDTABLE" : 1386634739296899186,
        "help1" : 1386634739296899184,
        "help2" : 1388626869980758207,
        "rules" : 1496975331033088130,
        "advice" : 1388626869980758207,
        "modos" : ["AyaGus", "SteelOfDmcls", "HusGus", "Kazukaka"],
        "words" : {
            'aya' : ['✨'], 
            'hus' : ['✨','<a:tianluforhus:1488296905250308317>'], 
            'steel' : ['👑'], 
            'kazu' : ['🤮', '🇧', '🇦', '🇳'],
            'kal' : ['<:Raja:1488127825859838103>', '🤡'], 
            'drip' : ['👴'],
            'zaza' : ['<:crown:1499124023710191777>'],
            'bayrou' : ['<:bayrou:1499124107936272415>']
        }
    },
    1272636727588294819 : {
        "Name": "Surge/Calamity",
        "MEMBER" : 1448771989996044368,
        "COLEAD" : 1504527597139263638,
        "SALON_ANNONCE_ID" : 1524931670124400791,
        "SALON_LOG_ID" : 0,
        "SALON_NEW_MEMBERS" : 1512185869237223664,
        "ROUNDTABLE" : 1512185869237223664,
        "help1" : 1387108158727782552,
        "help2" : 1387108158727782552,
        "rules" : 1524931670124400791,
        "advice" : 1387108158727782552,
        "description" : (
            "**1 -** Let the Spawner Hit Their Mechs First. All Mechs have a 30 Second Cooldown, Even Baby Mechs and Ascended Mechs. <a:research:1488144464835776622>\n"
            "**2 -** You Must Achieve at Least 400 Billion Damage\n"
            "**3 -** You Need to Summon a Minimum of 125 Boss Mechs \n"
            "**4 -** Get to 75 Summons before the final day so all the mechs summoned are 240 or higher\n"
            "**5 -** Summon and Kill 1 Mech in the first 24 hours, so your name appears in the Damage and Summons Leaderboard\n"
            f"**6 -** If there is anything you need regarding the event send a private message to : {' , '.join(f'**{m}**' for m in ['AyaGus', 'SteelOfDmcls', 'HusGus', 'Kazukaka'])}\n"
            "**7 -** Enjoy ! <:netero_heart:1441402964483903540>\n"
            "\n\n-> If you have any issues regarding the requirements or will not be available to play the event, please let us know in advance"
        ),
        "modos" : ["AyaGus", "SteelOfDmcls", "HusGus", "Kazukaka"],
        "words" : {
            'aya' : ['✨'], 
            'hus' : ['✨','<a:tianluforhus:1488296905250308317>'], 
            'steel' : ['👑'], 
            'kazu' : ['🤮', '🇧', '🇦', '🇳'],
            'kal' : ['<:Raja:1488127825859838103>', '🤡'], 
            'drip' : ['👴'],
            'zaza' : ['<:crown:1499124023710191777>'],
            'bayrou' : ['<:bayrou:1499124107936272415>']
        }
    },
    1341134017684308080 : {
        "Name" : "Stampede Of Fury",
        "MEMBER" : 1378019701484945599,
        "COLEAD" : 1376919653670195313,
        "SALON_ANNONCE_ID" : 1487046656783548416,
        "SALON_LOG_ID" : 1488162984328036442,
        "SALON_NEW_MEMBERS" : 1488162984328036442,
        "ROUNDTABLE" : 1380579205363929098,
        "help1" : 1341156549858558145,
        "help2" : 1487546393936662769,
        "rules" : 1468349920237977690,
        "advices" : 1341156549858558145,
        "modos" : ["AyaGus", "SteelOfDmcls", "HusGus", "Kalindrov", "Kazukaka"],
        "words" : {
            'aya' : ['✨'], 
            'hus' : ['✨','<a:tianluforhus:1488296905250308317>'], 
            'steel' : ['👑'], 
            'kazu' : ['🤮', '🇧', '🇦', '🇳'],
            'kal' : ['<:Raja:1488127825859838103>', '<a:rajagif:1488138198939996272>'], 
            'drip' : ['👴']
        }
    },
    1112682529212866620 : {
        "Name" : "Ayaya's server",
        "MEMBER" : 1497614547396071504,
        "COLEAD" : 1133394439453278308,
        "SALON_ANNONCE_ID" : 1497614670876639363,
        "SALON_LOG_ID" : 1497614885264035910,
        "SALON_NEW_MEMBERS" : 1497614885264035910,
        "ROUNDTABLE" : 1112682530311786508,
        "help1" : 1142405433257103441,
        "help2" : 1142405433257103441,
        "rules" : 1135884041158131712,
        "advices" : 1497615128936448091,
        "modos" : ["AyaGus", "SteelOfDmcls", "HusGus", "Kalindrov", "Kazukaka"],
        "words" : {
            'aya' : ['✨'], 
            'hus' : ['✨','<a:tianluforhus:1488296905250308317>'], 
            'steel' : ['👑'], 
            'kazu' : ['🤮', '🇧', '🇦', '🇳'],
            'kal' : ['<:Raja:1488127825859838103>', '🤡'], 
            'drip' : ['👴'],
            'zaza' : ['<:crown:1499124023710191777>'],
            'bayrou' : ['<:bayrou:1499124107936272415>']
        }
    }
}


factions = {
    "Cobra" : ("<:Cobra:1487161398017392791>", discord.Color.dark_purple()),
    "Griffin" : ("<:Griffin:1487161459707478237>", discord.Color.light_grey()),
    "Crane" : ("<:Crane:1487161429458026639>", discord.Color.dark_blue()),
    "Mantis" : ("<:Mantis:1487161330455674892>", discord.Color.green()),
    "Kodiak" : ("<:Kodiak:1487161368086974646>", discord.Color.red()),
    "Howler" : ("<:Howler:1487161297765138644>", discord.Color.orange())
}

admin = {
    'kazukuta' : 689011423208013842,
    'kalindrov': 226383207510179841,
    'steel' : 445665967381676032,
    'ayagus' : 716927140796301312,
    'husgus' : 694477321536798760
}

char_emojis = {
    "Toro": "<a:toro:1489280319503859802>",
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
    "Raja" : "<a:raja:1489283901473034401>",
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