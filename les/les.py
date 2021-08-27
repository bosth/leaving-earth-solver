from z3 import Optimize, Int, Or, If, unsat
from .util import required, thrust, mass, cost, ION_COST, ION_WEIGHT

DEFAULT_COMPONENT_MAX=8
RNG=(0,DEFAULT_COMPONENT_MAX)

class Planner():
    def __init__(self, load=1, juno=RNG, atlas=RNG, soyuz=RNG, proton=RNG, saturn=RNG, ion=RNG, time=RNG, cost=None, free_ions=0, rendezvous=True):
        self.load = load
        self.juno = juno
        self.atlas = atlas
        self.soyuz = soyuz
        self.proton = proton
        self.saturn = saturn
        self.cost = cost
        self.ion = ion
        self.free_ions = free_ions
        self.time = time
        self.rendezvous = rendezvous

    #def _find_ion_attach_maneuvers(self, route):
    #    if self.rendezvous:
    #        print(route)
    #        idx = None
    #        for i, maneuver in enumerate(route):
    #            if maneuver.src == self.ion_attach_point:
    #                idx = i
    #        if idx is not None:
    #            return route[idx+1:]
    #    return []

    def _find_ion_detach_maneuvers(self, route):
        if not self.rendezvous:
            return []

        rendezvous_actions = []
        for maneuver in route:
            if maneuver.time is False:
                rendezvous_actions.append(maneuver)
            else:
                rendezvous_actions.reverse()
                return rendezvous_actions

    def _plan(self, route, minimize=None):
        solver = Optimize()

        route = route.copy()
        route.reverse() # always plan backwards
        ion_detach_maneuvers = self._find_ion_detach_maneuvers(route)

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

        # add rules for each segment
        for i, maneuver in enumerate(route):
            i = len(route) - i
            d = maneuver.diff
            juno = Int("juno_{}".format(i))
            atlas = Int("atlas_{}".format(i))
            soyuz = Int("soyuz_{}".format(i))
            proton = Int("proton_{}".format(i))
            saturn = Int("saturn_{}".format(i))
            time = Int("time_{}".format(i))

            solver.add(juno>=0, juno<=self.juno[1]) 
            solver.add(atlas>=0, atlas<=self.atlas[1])
            solver.add(soyuz>=0, soyuz<=self.soyuz[1])
            solver.add(proton>=0, proton<=self.proton[1])
            solver.add(saturn>=0, saturn<=self.saturn[1])

            if maneuver.time is False:
                solver.add(time==0)
            else:
                solver.add(time>=maneuver.time)
                solver.add(Or(ion>0, time==maneuver.time))

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
        elif minimize == "mass":
            solver.minimize(t_load)
            solver.minimize(t_cost)
            solver.minimize(t_time)
        elif minimize == "cost":
            solver.minimize(t_cost)
            solver.minimize(t_time)
            solver.minimize(t_load)

        if solver.check() == unsat:
            return None, None
        else:
            return solver.model(), ion_detach_maneuvers

    def plan(self, route, minimize=None):
        model, ion_detach_maneuvers = self._plan(route, minimize)
        if model is None:
            return model
        plan = []
        for i, stage in enumerate(route):
            plan.append({"origin": stage.src.name, "destination": stage.dst.name, "difficulty": stage.diff, "components": {}})
        components = {
            "juno": 0,
            "atlas": 0,
            "soyuz": 0,
            "proton": 0,
            "saturn": 0,
            "ion": 0,
            "time": 0
        }
        mission = {}
        ions = 0
        for i in model:
            component = i.name()
            count = model[i].as_long()
            if component == "ion" and count:
                components[component] = count
            elif count:
                component, stageid = tuple(component.split("_"))
                stageid = int(stageid) - 1
                stage = plan[stageid]
                if component == "time":
                    stage["time"] = count
                else:
                    c = stage.get("components", {})
                    c[component] = count
                    stage["components"] = c
                
                if components.get(component):
                    components[component] += count
                else:
                    components[component] = count

        for i, stage in enumerate(route):
            ions = components["ion"]
            if ion_detach_maneuvers and stage == ion_detach_maneuvers[0] and ions > 0:
                plan[i]["rendezvous"] = [{"detach": ["ion", ions]}]
            elif "time" in plan[i] and ions > 0:
                plan[i]["components"]["ion"] = ions
            plan[i]["thrust"] = thrust(**plan[i]["components"], time=int(plan[i].get("time", 0)))

        t_cost = cost(**components, free_ions=self.free_ions)
        t_mass = mass(**components)
        mission["components"] = components
        mission["payload"] = self.load
        mission["mass"] = t_mass
        mission["cost"] = t_cost
        mission["plan"] = plan
        return mission