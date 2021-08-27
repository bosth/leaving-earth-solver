Locations = {}

class _Location:
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.maneuvers = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def connect(self, dst, diff, time=False):
        maneuver = _Maneuver(self, dst, diff, time)
        self.maneuvers.append(maneuver)
        return maneuver

    def to(self, dst):
        for m in self.maneuvers:
            if m.dst == dst:
                return m

class _Maneuver:
    def __init__(self, src, dst, diff, time=False):
        self.src = src
        self.dst = dst
        self.diff = diff
        self.time = time

    def __str__(self):
        return "{}->{}".format(self.src, self.dst)

    def __repr__(self):
        return "{}-({})->{}".format(self.src.code, self.diff, self.dst.code)

def create_location(name, code):
    l = _Location(name, code)
    Locations[code] = l

def connect_locations(l1, l2, diff, time=False):
    l1 = Locations[l1]
    l2 = Locations[l2]
    maneuver = l1.connect(l2, diff, time)
    return maneuver

create_location("Earth", "E")
create_location("Suborbital flight", "Eso")
create_location("Earth orbit", "Eo")
create_location("Lunar orbit", "Lo")
create_location("Lunar fly-by", "Lfb")
create_location("Moon", "L")
create_location("Inner planets transfer", "ipt")
create_location("Venus fly-by", "Vfb")
create_location("Venus orbit", "Vo")
create_location("Venus", "V")
create_location("Ceres", "C")
create_location("Mars fly-by", "Mfb")
create_location("Mars orbit", "Mo")
create_location("Mars", "M")
create_location("Phobos", "P")
create_location("Mercury fly-by", "Hfb")
create_location("Mercury orbit", "Ho")
create_location("Mercury", "H")

connect_locations("C", "ipt", 5, 2)
EEo = connect_locations("E", "Eo", 8)
EEso = connect_locations("E", "Eso", 3)
EsoEo = connect_locations("Eso", "Eo", 5)
connect_locations("Eso", "E",0)
connect_locations("Eo", "E", 0)
connect_locations("Eo", "ipt", 3, 1)
connect_locations("Eo", "Lfb", 2, 0)
connect_locations("Eo", "Lo", 3, 0)
connect_locations("Eo", "Mfb", 3, 3)
connect_locations("Eo", "Mo", 5, 3)
connect_locations("ipt", "C", 5, 1)
connect_locations("ipt", "Eo", 3, 1)
connect_locations("ipt", "Mo", 4, 2)
connect_locations("ipt", "Hfb", 5, 1)
connect_locations("ipt", "Vfb", 2, 1)
connect_locations("ipt", "Vo", 3, 1)
connect_locations("Lfb", "Eo", 2)
connect_locations("Lfb", "Lo", 2)
connect_locations("Lfb", "L", 4)
connect_locations("Lo", "Eo", 3)
connect_locations("Lo", "L", 2)
connect_locations("M", "Mo", 3)
connect_locations("Mfb", "M", 3)
connect_locations("Mfb", "Mo", 3, 0)
connect_locations("Mo", "Eo", 5, 3)
connect_locations("Mo", "ipt", 4, 2)
connect_locations("Mo", "M", 0)
connect_locations("Mo", "P", 1, 1)
connect_locations("Hfb", "H", 4)
connect_locations("Hfb", "Ho", 2, 0)
connect_locations("Ho", "ipt", 7, 1)
connect_locations("Ho", "H", 2)
connect_locations("H", "Ho", 2)
connect_locations("L", "Lo", 2)
connect_locations("P", "Mo", 1, 0)
connect_locations("V", "Vo", 6)
connect_locations("Vfb", "V", 1)
connect_locations("Vfb", "Vo", 1, 0)
connect_locations("Vo", "ipt", 3, 1)
connect_locations("Vo", "V", 0)
