JUN_COST = 1
ATL_COST = 5
SYZ_COST = 8
PRT_COST = 12
SAT_COST = 15
ION_COST = 10
JUN_THRUST = 4
ATL_THRUST = 27
SYZ_THRUST = 80
PRT_THRUST = 70
SAT_THRUST = 200
ION_THRUST = 5
JUN_WEIGHT = 1
ATL_WEIGHT = 4
SYZ_WEIGHT = 9
PRT_WEIGHT = 6
SAT_WEIGHT = 20
ION_WEIGHT = 1

def required(juno, atlas, soyuz, proton, saturn, ion, diff, load):
    return diff * (mass(juno, atlas, soyuz, proton, saturn, ion) + load)

def thrust(juno=0, atlas=0, soyuz=0, proton=0, saturn=0, ion=0, time=0):
    return juno*JUN_THRUST + atlas*ATL_THRUST + soyuz*SYZ_THRUST + proton*PRT_THRUST + saturn*SAT_THRUST + ion*ION_THRUST*time

def mass(juno, atlas, soyuz, proton, saturn, ion, time=None):
    return juno*JUN_WEIGHT + atlas*ATL_WEIGHT + soyuz*SYZ_WEIGHT + proton*PRT_WEIGHT + saturn*SAT_WEIGHT + ion*ION_WEIGHT

def cost(juno=0, atlas=0, soyuz=0, proton=0, saturn=0, ion=0, time=None, free_ions=0):
    if free_ions > ion:
        free_ions = ion
    ion -= free_ions
    return juno*JUN_COST + atlas*ATL_COST + soyuz*SYZ_COST + proton*PRT_COST + saturn*SAT_COST + ion*ION_COST
