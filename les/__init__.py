from .__version__ import __version__
from .les import Planner, DEFAULT_COMPONENT_MAX
from .location import Locations, EEso, EEo, EsoEo
from math import sqrt

def build_route(route):
    it = iter(route)
    src = next(it, None)
    
    for dst in it:
        yield src.to(dst)
        src = dst

def add_path_stats(paths, aerobraking=False):
    stats = []
    for path in paths:
        maneuvers = [m for m in path if m not in [EEso, EsoEo, EEo]]
        maneuvers = path
        diffs = [sqrt(i+10.0)*(m.get_diff(aerobraking))+m.get_time(aerobraking) for i, m in enumerate(maneuvers)]
        stats.append(sum(diffs))
    return zip(stats, paths)

def find_best_paths(src, dst, path_filter="optimal", single_stage=False, aerobraking=False):
    paths = find_paths(src, dst)
    if not paths:
        return []
    paths = add_path_stats(paths, aerobraking)
    paths = sorted(paths, key=lambda i: i[0]) # sort by stdev/mean or whatever technique we used for stats
    if path_filter != "all":
        if path_filter.isdigit():
            paths = paths[:int(path_filter)]
        else: # optimal
            threshold = paths[0][0] * 1.2 # allow slightly higher difficulty paths than the least difficult
            paths = [p for p in paths if p[0] <= threshold]
    #for p in paths:
    #    if p[1][0] != EEo:
    #        print(p)
    paths = [p[1] for p in paths]
    if single_stage:
        single_stage_paths = []
        for p in paths:
            if p[0] == EEso:
                single_stage = p.copy()[2:]
                single_stage.insert(0, EEo)
                single_stage_paths.append(single_stage)
        paths = paths + single_stage_paths
    return paths

def find_paths(src, dst):
    paths = []
    for m in src.maneuvers:
        if m == EEo: # don't use single-stage routes
            continue
        paths += _find_path(m, dst, [], [])
    return paths

def _find_path(mc, dst, path=[], visited=[]):
    visited = visited + [mc.src]
    path = path + [mc]
    if mc.dst == dst:
        return [path]
    paths = []
    for m in mc.dst.maneuvers:
        if m not in path and m.dst not in visited:
            newpaths = _find_path(m, dst, path, visited)
            for newpath in newpaths:
                paths.append(newpath)
    return paths
