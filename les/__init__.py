from .__version__ import __version__
from .les import Planner, DEFAULT_COMPONENT_MAX
from .location import Locations, EEso, EEo, EsoEo
import statistics

def build_route(route):
    it = iter(route)
    src = next(it, None)
    
    for dst in it:
        yield src.to(dst)
        src = dst

def add_path_stats(paths):
    diffs = [sum(m.diff for m in p) for p in paths]
    stats = []
    for p in paths:
        stats.append(statistics.mean([m.diff for m in p]))
    return zip(diffs, stats, paths)

def find_best_paths(src, dst, path_filter="optimal", one_stage=False):
    paths = find_paths(src, dst, one_stage)
    if not paths:
        return []
    paths = add_path_stats(paths)
    paths = sorted(paths, key=lambda i: i[0]) # sort by total difficulty
    if path_filter != "all":
            threshold = paths[0][0] * 1.2 # allow slightly higher difficulty paths than the least difficult
            paths = [p for p in paths if p[0] <= threshold]
            if path_filter == "one":
                paths = sorted(paths, key=lambda i: i[1]) # sort by stdev/mean or whatever technique we used for stats
                paths = paths[:1]
    paths = [p[2] for p in paths]
    if one_stage:
        two_stage_paths = []
        for p in paths:
            if p[0] == EEo:
                two_stage = p.copy()[1:]
                two_stage.insert(0, EEso)
                two_stage.insert(1, EsoEo)
                two_stage_paths.append(two_stage)
        paths = paths + two_stage_paths
    return paths

def find_paths(src, dst, one_stage=False):
    paths = []
    for m in src.maneuvers:
        if one_stage and m == EEso: # we are going to ignore this option but present it later
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
