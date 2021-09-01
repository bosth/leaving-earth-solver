Locations = {}
JUPITER_SLINGSHOT = range(1956, 1987, 2)
SATURN_SLINGSHOT = range(1957, 1987, 3)
URANUS_SLINGSHOT = range(1957, 1987, 5)
NEPTUNE_SLINGSHOT = range(1958, 1987, 6)

class _Location:
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.maneuvers = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def connect(self, dst, diff, time=False, ab_diff=None, ab_time=None, slingshot=None):
        maneuver = _Maneuver(self, dst, diff, time=time, ab_diff=ab_diff, ab_time=ab_time, slingshot=slingshot)
        self.maneuvers.append(maneuver)
        return maneuver

    def to(self, dst):
        for m in self.maneuvers:
            if m.dst == dst:
                return m

class _Maneuver:
    def __init__(self, src, dst, diff, time=False, ab_diff=None, ab_time=None, slingshot=None):
        self.src = src
        self.dst = dst
        self.diff = diff
        self.time = time
        self.ab_diff = ab_diff
        self.ab_time = ab_time
        self.slingshot = slingshot

    def get_diff(self, aerobraking=False):
        if aerobraking and self.ab_diff:
            return self.ab_diff
        else:
            return self.diff

    def __str__(self):
        return "{}->{}".format(self.src, self.dst)

    def __repr__(self):
        return "{}-({})->{}".format(self.src.code, self.diff, self.dst.code)

def create_location(name, code):
    l = _Location(name, code)
    Locations[code] = l

def connect_locations(l1, l2, diff, time=False, ab_diff=None, ab_time=False, slingshot=None):
    l1 = Locations[l1]
    l2 = Locations[l2]
    maneuver = l1.connect(l2, diff, time=time, ab_diff=ab_diff, ab_time=ab_time, slingshot=slingshot)
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
create_location("Earth cycler", "Ec")
create_location("Mars cycler", "Mc")
create_location("Outer planets transfer", "opt")
create_location("Jupiter orbit", "Jo")
create_location("Jupiter fly-by", "Jfb")
create_location("Ganymede", "G")
create_location("Ganymede orbit", "Go")
create_location("Io", "I")
create_location("Europa", "W")
create_location("Callisto", "K")
create_location("Saturn orbit", "So")
create_location("Saturn fly-by", "Sfb")
create_location("Titan", "T")
create_location("Titan orbit", "To")
create_location("Enceladus", "D")
create_location("Uranus fly-by", "Ufb")
create_location("Neptune fly-by", "Nfb")

# sub orbital connections
EEo   = connect_locations("E",   "Eo",  8)
EEso  = connect_locations("E",   "Eso", 3)
EsoE  = connect_locations("Eso", "E",   0)
EsoEo = connect_locations("Eso", "Eo",  5)

connect_locations("C",   "ipt",  5, time=2)
connect_locations("C",   "opt",  3, time=1)
connect_locations("Ec",  "Eo",   3, time=0, ab_diff=0)
connect_locations("Ec",  "Mc",   0, time=3)
connect_locations("Eo",  "E",    0)
connect_locations("Eo",  "Ec",   3, time=0)
connect_locations("Eo",  "Lfb",  1, time=0)
connect_locations("Eo",  "Lo",   3, time=0)
connect_locations("Eo",  "Mfb",  3, time=3)
connect_locations("Eo",  "Mo",   5, time=3)
connect_locations("Eo",  "ipt",  3, time=1)
connect_locations("Eo",  "opt",  6, time=1)
connect_locations("H",   "Ho",   2)
connect_locations("Hfb", "H",    4)
connect_locations("Hfb", "Ho",   2, time=0)
connect_locations("Ho",  "H",    2)
connect_locations("Ho",  "ipt",  7, time=1)
connect_locations("L",   "Lo",   2)
connect_locations("Lfb", "Eo",   1, time=0)
connect_locations("Lfb", "L",    4)
connect_locations("Lfb", "Lo",   2, time=0)
connect_locations("Lo",  "Eo",   3, time=0)
connect_locations("Lo",  "L",    2)
connect_locations("M",   "Mo",   3)
connect_locations("Mc",  "Ec",   0, time=3)
connect_locations("Mc",  "M",    3)
connect_locations("Mc",  "Mo",   3, time=0, ab_diff=0)
connect_locations("Mfb", "M",    3)
connect_locations("Mfb", "Mo",   3, time=0, ab_diff=1)
connect_locations("Mfb", "ipt",  1, time=2)
connect_locations("Mfb", "Jfb",  4, time=3, slingshot=JUPITER_SLINGSHOT)
connect_locations("Mo",  "Eo",   5, time=3)
connect_locations("Mo",  "M",    0)
connect_locations("Mo",  "Mc",   3, time=0)
connect_locations("Mo",  "P",    1, time=0)
connect_locations("Mo",  "ipt",  4, time=2)
connect_locations("Mo",  "opt",  5, time=1)
connect_locations("P",   "Mo",   1, time=0)
connect_locations("V",   "Vo",   6)
connect_locations("Vfb", "V",    1)
connect_locations("Vfb", "Vo",   1, time=0, ab_diff=0)
connect_locations("Vfb", "ipt",  1, time=3)
connect_locations("Vfb", "Jfb",  1, time=1, slingshot=JUPITER_SLINGSHOT)
connect_locations("Vo",  "V",    0)
connect_locations("Vo",  "ipt",  3, time=1)
connect_locations("Vo",  "opt",  9, time=1)
connect_locations("ipt", "C",    5, time=1)
connect_locations("ipt", "Eo",   3, time=1)
connect_locations("ipt", "Hfb",  5, time=1)
connect_locations("ipt", "Mfb",  1, time=2)
connect_locations("ipt", "Mo",   4, time=2)
connect_locations("ipt", "Vfb",  2, time=1)
connect_locations("ipt", "Vo",   3, time=1)
connect_locations("opt", "C",    3, time=1)
connect_locations("opt", "Mo",   5, time=1, ab_diff=2, ab_time=1)
connect_locations("opt", "Jfb",  4, time=2, slingshot=JUPITER_SLINGSHOT)
connect_locations("opt", "Sfb",  3, time=3)
connect_locations("opt", "Ufb",  4, time=9, slingshot=URANUS_SLINGSHOT)
connect_locations("opt", "Eo",   6, time=1, ab_diff=1, ab_time=1)
connect_locations("Jfb", "Jo",  10, time=0, ab_diff=3)
connect_locations("Jfb", "Sfb",  0, time=2, slingshot=SATURN_SLINGSHOT)
connect_locations("Jfb", "opt",  4, time=2)
connect_locations("G",   "Go",   2)
connect_locations("I",   "Jo",   2, time=0)
connect_locations("Go",  "G",    2)
connect_locations("Go",  "Jo",   2, time=0)
connect_locations("Jo",  "Jfb", 10, time=0)
connect_locations("Jo",  "I",    2, time=0)
connect_locations("Jo",  "Go",   3, time=0)
connect_locations("Jo",  "W",    2, time=0)
connect_locations("Jo",  "K",    5, time=0)
connect_locations("Sfb", "Ufb",  0, time=5, slingshot=URANUS_SLINGSHOT)
connect_locations("Sfb", "So",   7, time=0, ab_diff=1)
connect_locations("Sfb", "opt",  3, time=3)
connect_locations("To",  "So",   2, time=0)
connect_locations("To",  "T",    0)
connect_locations("T",   "To",   2)
connect_locations("W",   "Jo",   2, time=0)
connect_locations("K",   "Jo",   5, time=0)
connect_locations("K",   "Jfb",  5)
connect_locations("So",  "Sfb",  7, time=0)
connect_locations("So",  "To",   2, time=0, ab_diff=1)
connect_locations("So",  "T",    1)
connect_locations("So",  "D",    2, time=0)
connect_locations("D",   "So",   2, time=0)
connect_locations("Ufb", "Nfb",  0, time=4, slingshot=NEPTUNE_SLINGSHOT)
connect_locations("Ufb", "opt",  4, time=9)
