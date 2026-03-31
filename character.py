class Personnage:
    def __init__(self, nom, faction, note, astuce1, astuce2, points_forts, faiblesses):
        self.nom = nom
        self.faction = faction
        self.note = note
        self.astuce1 = astuce1
        self.astuce2 = astuce2
        self.points_forts = points_forts
        self.faiblesses = faiblesses

    # Les Getters
    def get_nom(self):
        return self.nom

    def get_faction(self):
        return self.faction

    def get_note(self):
        return self.note

    def get_astuce1(self):
        return self.astuce1

    def get_astuce2(self):
        return self.astuce2

    def get_points_forts(self):
        return self.points_forts

    def get_faiblesses(self):
        return self.faiblesses