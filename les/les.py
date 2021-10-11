from z3 import Optimize, Int, Or, If, unsat, IntVector
from .util import required, thrust, mass, cost, ION_COST, ION_WEIGHT

DEFAULT_COMPONENT_MAX=8
RNG=(0,DEFAULT_COMPONENT_MAX)

class Planner():
    def __init__(self, load=1, juno=RNG, atlas=RNG, soyuz=RNG, proton=RNG, saturn=RNG, ion=RNG, time=None, year=None, cost=None, free_ions=0, rendezvous=True, aerobraking=False):
        self.load = load
        self.juno = juno
        self.atlas = atlas
        self.soyuz = soyuz
        self.proton = proton
        self.saturn = saturn
        self.cost = cost
        self.ion = ion
        self.free_ions = free_ions
        self.rendezvous = rendezvous
        self.aerobraking = aerobraking
        
        self.year = year
        if self.year:
            # limit the total journey time by the starting year that the user provided
            if time is None:
                self.time = (0, 1986-self.year)
            else:
                self.time = (min(1986-year, time[0]), 
                             min(1986-year, time[1]))
        else:
            if time is None:
                self.time = (0, 1986 - 1956)
            else:
                self.time = time

    """
    Find the point in the route where ions can be detached, i.e. when all remaining maneuvers can not take time.
    """
    def _find_ion_detach_maneuvers(self, route):
        if self.rendezvous:
            rendezvous_actions = []
            for maneuver in route:
                if maneuver.get_time(self.aerobraking) is False:
                    rendezvous_actions.append(maneuver)
                else:
                    rendezvous_actions.reverse()
                    return rendezvous_actions
        return []

    """
    Check if there are any slingshot maneuvers in this route.
    """
    def _find_slingshot_maneuvers(self, route):
        for manuever in route:
            if manuever.slingshot:
                return True
        return False

    def _plan(self, route, minimize=None, minimize_value=None):
        solver = Optimize()

        ion_detach_maneuvers = self._find_ion_detach_maneuvers(route)
        slingshot_maneuvers = self._find_slingshot_maneuvers(route)
        if slingshot_maneuvers:
            if not self.year:
                #raise Exception("To perform a slingshot maneuver, a starting year must be specified.")
                return None, None

        a_juno = IntVector("juno", len(route))
        a_atlas = IntVector("atlas", len(route))
        a_soyuz = IntVector("soyuz", len(route))
        a_proton = IntVector("proton", len(route))
        a_saturn = IntVector("saturn", len(route))
        a_time = IntVector("time", len(route))
        if self.year:
            a_year = IntVector("year", len(route))

        # ions are allocated per mission not per segment
        ion = Int("ion")
        solver.add(ion>=self.ion[0])
        solver.add(ion<=self.ion[1])

        # running totals
        t_juno = 0
        t_atlas = 0
        t_soyuz = 0
        t_proton = 0
        t_saturn = 0
        t_load = self.load
        t_cost = If(self.free_ions>ion, 0, (ion-self.free_ions)*ION_COST)
        t_time = 0
        # add rules for each maneuver (0 is the last maneuver in the route)
        for i, maneuver in enumerate(route):
            d = maneuver.get_diff(self.aerobraking)
            juno = a_juno[i]
            atlas = a_atlas[i]
            soyuz = a_soyuz[i]
            proton = a_proton[i]
            saturn = a_saturn[i]
            time = a_time[i]

            solver.add(juno>=0, juno<=self.juno[1]) 
            solver.add(atlas>=0, atlas<=self.atlas[1])
            solver.add(soyuz>=0, soyuz<=self.soyuz[1])
            solver.add(proton>=0, proton<=self.proton[1])
            solver.add(saturn>=0, saturn<=self.saturn[1])

            if slingshot_maneuvers or self.year:
                if maneuver.get_time(self.aerobraking) is False:
                    solver.add(time==0)
                    if i == len(route) - 1:
                        solver.add(a_year[i]>=self.year)
                    else:
                        solver.add(a_year[i]==a_year[i+1])
                else:
                    if maneuver.slingshot: # slingshots have fixed duration
                        solver.add(time==maneuver.get_time(self.aerobraking))
                        available_years = []
                        for available_year in maneuver.slingshot:
                            if available_year >= self.year and available_year <= self.year + self.time[1]:
                                available_years.append(a_year[i]==available_year)
                        solver.add(Or(*available_years))
                    else:
                        solver.add(time>=maneuver.get_time(self.aerobraking))
                    if i == len(route) - 1:
                        solver.add(a_year[i]>=self.year)
                    else:
                        solver.add(a_year[i]==a_year[i+1]+a_time[i+1])
            else:
                if maneuver.get_time(self.aerobraking) is False:
                    solver.add(time==0)
                else:
                    solver.add(time>=maneuver.get_time(self.aerobraking))

            if maneuver in ion_detach_maneuvers:
                solver.add(thrust(juno, atlas, soyuz, proton, saturn, ion, time) >= required(juno, atlas, soyuz, proton, saturn, 0, d, t_load))
            else:
                solver.add(thrust(juno, atlas, soyuz, proton, saturn, ion, time) >= required(juno, atlas, soyuz, proton, saturn, ion, d, t_load))

            t_juno += juno
            t_atlas += atlas
            t_soyuz += soyuz
            t_proton += proton
            t_saturn += saturn
            t_load += mass(juno, atlas, soyuz, proton, saturn, 0) # do not add ions since they only count once
            t_cost += cost(juno, atlas, soyuz, proton, saturn, 0) # do not add ions since they only count once
            t_time += time

        if self.cost:
            solver.add(t_cost>=self.cost[0], t_cost<=self.cost[1]) 

        solver.add(t_juno>=self.juno[0], t_juno<=self.juno[1]) 
        solver.add(t_atlas>=self.atlas[0], t_atlas<=self.atlas[1])
        solver.add(t_soyuz>=self.soyuz[0], t_soyuz<=self.soyuz[1])
        solver.add(t_proton>=self.proton[0], t_proton<=self.proton[1])
        solver.add(t_saturn>=self.saturn[0], t_saturn<=self.saturn[1])
        solver.add(t_time>=self.time[0], t_time<=self.time[1])

        if minimize == "time":
            solver.minimize(t_time)
            solver.minimize(t_cost)
            solver.minimize(t_load)
            if minimize_value is not None:
                solver.add(t_time <= minimize_value)
        elif minimize == "mass":
            solver.minimize(t_load)
            solver.minimize(t_cost)
            solver.minimize(t_time)
            if minimize_value is not None:
                solver.add(t_load <= minimize_value)
        elif minimize == "cost":
            solver.minimize(t_cost)
            solver.minimize(t_time)
            solver.minimize(t_load)
            if minimize_value is not None:
                solver.add(t_cost <= minimize_value)
        if self.year:
            solver.minimize(a_year[0]) # prefer the soonest arrival date
            solver.maximize(a_year[len(route)-1])

        if solver.check() == unsat:
            return None, None
        else:
            return solver.model(), ion_detach_maneuvers

    def plan(self, route, minimize=None, minimize_value=None, slingshot=False):
        route = list(reversed(route))
        model, ion_detach_maneuvers = self._plan(route, minimize, minimize_value)
        if model is None:
            return model
        plan = []
        for maneuver in route:
            if self.aerobraking and maneuver.ab_diff is not None:
                plan.append({"origin": maneuver.src.name, "destination": maneuver.dst.name, "difficulty": maneuver.ab_diff, "components": {}, "aerobraking": True})
            else:
                plan.append({"origin": maneuver.src.name, "destination": maneuver.dst.name, "difficulty": maneuver.diff, "components": {}, "aerobraking": False})
        components = {}
        t_time = 0
        mission = {}
        ions = 0
        for key in model:
            val = model[key].as_long()
            key = key.name()

            if key == "ion" and val > 0:
                components[key] = val
            elif val > 0:
                key, i = tuple(key.split("__"))
                i = int(i)
                if key == "year" and i == len(route):
                    continue

                stage = plan[i]
                if key == "time":
                    stage["time"] = val
                    t_time += val
                elif key == "year":
                    stage["year"] = val
                else:
                    c = stage.get("components", {})
                    c[key] = val
                    stage["components"] = c
                    if components.get(key):
                        components[key] += val
                    else:
                        components[key] = val

        for i, stage in enumerate(route):
            ions = components.get("ion", 0)
            if ion_detach_maneuvers and stage == ion_detach_maneuvers[0] and ions > 0:
                plan[i]["rendezvous"] = [{"detach": ["ion", ions]}]
            elif "time" in plan[i] and ions > 0:
                plan[i]["components"]["ion"] = ions
            plan[i]["thrust"] = thrust(**plan[i]["components"], time=int(plan[i].get("time", 0)))
            plan[i]["slingshot"] = stage.slingshot is not None

        plan = list(reversed(plan))

        if self.year:
            mission["start"] = plan[0]["year"]
            mission["end"] = plan[-1]["year"] + plan[-1].get("time", 0)

        t_cost = cost(**components, free_ions=self.free_ions)
        t_mass = mass(**components)
        mission["components"] = components
        mission["payload"] = self.load
        mission["mass"] = t_mass
        mission["cost"] = t_cost
        mission["time"] = t_time
        mission["plan"] = plan
        return mission
