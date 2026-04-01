class Personnage:
    def __init__(self, nom, faction, note, arena, campaign, faction_sewers, tips, mechs='_Coming soon..._'):
        self.nom = nom
        self.faction = faction
        self.note = note
        self.arena = arena
        self.campaign = campaign
        self.faction_sewers = faction_sewers
        self.tips = tips
        self.mechs = mechs

    # Les Getters
    def get_nom(self):
        return self.nom

    def get_faction(self):
        return self.faction

    def get_note(self):
        return self.note

    def get_arena(self):
        return self.arena

    def get_campaign(self):
        return self.campaign

    def get_faction_sewers(self):
        return self.faction_sewers

    def get_tips(self):
        return self.tips
    
    def get_mechs(self):
        return self.mechs