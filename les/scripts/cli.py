import click
from les import __version__
from les import Planner, find_best_paths, Locations, DEFAULT_COMPONENT_MAX
import re
import json
import logging
log = logging.getLogger("les")

class Range(click.ParamType):
    name = "range"
    def convert(self, value, param, ctx):
        if isinstance(value, tuple):
            return value
        if value is None:
            return None
        m = re.match("^[0-9]*$", value) # exact number
        if m:
            value = int(value)
            return (value, value)

        m = re.match("^-[0-9]*$", value) # maximum
        if m:
            value = abs(int(value))
            return (0, value)

        m = re.match("^[0-9]*[+]$", value) # minimum
        if m:
            value = value.strip("+")
            value = int(value)
            return (value, 900)

        m = re.match("^[0-9]-[0-9]*$", value) # range
        if m:
            values = value.split("-")
            value1 = int(values[0])
            value2 = int(values[1])
            if value1 > value2:
                return (value2, value1)
            else:
                return (value1, value2)
        
        self.fail(
            "Number must be expressed in one of the following ways: 4 (exactly 4); -4 (maximum of 4); 4+ (minimum of 4); 2-4 (between 2 and 4)",
            param,
            ctx,
        )

def find_best(missions, minimize):
    missions = [mission for mission in missions if mission]
    if minimize == "time":
        return sorted(missions, key=lambda x: x.get("time", 0))
    if minimize == "cost":
        return sorted(missions, key=lambda x: x.get("cost", 0))
    if minimize == "mass":
        return sorted(missions, key=lambda x: x.get("mass", 0))

@click.command()
@click.version_option(__version__)
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode")
@click.option("-j", "--juno", type=Range(), default="0-{}".format(DEFAULT_COMPONENT_MAX), help="Number of Juno rockets")
@click.option("-a", "--atlas", type=Range(), default="0-{}".format(DEFAULT_COMPONENT_MAX), help="Number of Atlas rockets")
@click.option("-s", "--soyuz", type=Range(), default="0-{}".format(DEFAULT_COMPONENT_MAX), help="Number of Soyuz rockets")
@click.option("-p", "--proton", type=Range(), default="0-{}".format(DEFAULT_COMPONENT_MAX), help="Number of Proton rockets")
@click.option("-n", "--saturn", type=Range(), default="0-{}".format(DEFAULT_COMPONENT_MAX), help="Number of Saturn rockets")
@click.option("-i", "--ion", type=Range(), default="0-{}".format(DEFAULT_COMPONENT_MAX), help="Number of Ion thrusters")
@click.option("-c", "--cost", type=Range(), default=None, help="Cost of mission")
@click.option("--free-ions", type=click.IntRange(min=0), default=0, help="Number of Ion thrusters available at the origin")
@click.option("-m", "--minimize", type=click.Choice(["time","cost","mass"], case_sensitive=False), default="cost", help="Minimization goal")
@click.option("--routes", type=click.Choice(["optimal","all"]+[str(i) for i in range(1,32)], case_sensitive=False), default="optimal", help="Which routes to try when there are multiple options")
@click.option("--single-stage", is_flag=True, help="Check a single stage configuration for launches from Earth (by default only a two-stage configuration will be attempted)")
@click.option("--aerobraking/--no-aerobraking", is_flag=True, help="Use aerobraking")
@click.option("--rendezvous/--no-rendezvous", default=True, help="If rendezvous technology is available, Ion thrusters will be detached when no longer needed")
@click.argument("orig", required=True, metavar="ORIGIN")
@click.argument("dest", required=True, metavar="DESTINATION")
@click.argument("payload", type=click.IntRange(min=1, max=None), default=1)
@click.option("-t", "--time", type=Range(), default=None, help="Number of time tokens")
@click.option("-y", "--year", type=click.IntRange(min=1956, max=1986), default=None, help="Year that journey starts")
def cli(verbose, juno, atlas, soyuz, proton, saturn, ion, cost, free_ions, minimize, routes, single_stage, aerobraking, rendezvous, orig, dest, payload, time, year):
    """
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    try:
        if orig == dest:
            log.error("Origin and destination may not be the same.")
            exit(1)
        orig = Locations[orig]
        dest = Locations[dest]
    except KeyError as e:
        log.error("Error finding {}. Must be one of the following:".format(e))
        for code, name in Locations.items():
            print(code.rjust(4), ": ", name, sep="")
        exit(1)
    planner = Planner(load=payload, juno=juno, atlas=atlas, soyuz=soyuz, proton=proton, saturn=saturn, ion=ion, time=time, year=year, cost=cost, free_ions=free_ions, rendezvous=rendezvous, aerobraking=aerobraking)
    paths = find_best_paths(orig, dest, path_filter=routes, single_stage=single_stage, aerobraking=aerobraking)
    log.info("Found {} paths using '{}' strategy".format(len(paths), routes))

    missions = []
    minimize_value = None
    try:
        for path in paths:
            log.debug("Planning for {}".format(path))
            mission = planner.plan(path, minimize=minimize, minimize_value=minimize_value, slingshot=year)
            if mission:
                new_mv = mission[minimize]
                log.info("Found solution using {} with value {}".format(path, new_mv))
                if minimize_value is None or new_mv < minimize_value:
                    minimize_value = new_mv
                missions.append(mission)
            else:
                log.info("Unable to find a solution using {}".format(path))
    except Exception as e:
        log.error(e)

    missions = find_best(missions, minimize)
    if missions:
        print(json.dumps(missions[0], indent=4))
    else:
        exit(1)

if __name__ == "__main__":
    cli()
