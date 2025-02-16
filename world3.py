#!/usr/bin/env python
# SPDX-License-Identifier: Unlicense
"""
Runs the world3 model. Example:

./world3.py --scenario 2 run    # BAU2

The model is based on https://github.com/Juji29/MyWorld3 which is an
excellent model IMO.

The model can be executed with (pre-programmed) modifications.

./world3.py mods                     # Print modification help
./world3.py -s 2 -m le,modify_m run  # Modified life expectancy

The github.com/TimSchell98/PyWorld3-03 model can also be used for comparison,
especially for the "recalibration23" mod described in
https://onlinelibrary.wiley.com/doi/10.1111/jiec.13442
This model unfortunately is not correctly updated to the 2003 calibration.

./world3.py pyworld3 --recal23

"""
import sys
import os
import argparse
import json
import numpy
import matplotlib.pyplot as plt
import system_dynamic as sd
import world3_model as world3
import le
import world3_modifications as w3mod
import empirical_data as emp

dbg = lambda *arg: 0
stitle=[
    "BAU",
    "BAU2",
    "Pollution Control",
    "Land Yield Tech",
    "Land Protection",
    "CT",
    "Zero Pop Growth",
    "Stable Industrial Output",
    "SW Change Year 2002",
    "SW Change Year 1982",
    "SW Change Year 2032",
]
# State of the World nodes for printing
sow_nodes=[
    ("pop",(0,12e9)), ("nr",(0,2e12)), ("io",(0,4e12)), ("f",(0,6e12)),
    ("ppolx",(0,40))]

# Translate constant name PyWorld3-03 -> world3.
# Used to set recalibration constants for world3 runs
def constant_name(s, n):
    nmap = {
        "icor2": "", # This is a flow in 2003 update
        "pp19": "PPOLI", # Same value
        "apct": "",  # Is y4000, so it doesn't matter
        "ghup": "",  # In world3 "HUP" is used, but with the same value (4)
        "faipm": "", # ??? "Fraction agricultural input pers mtl"
        "pp70": "",  # PPOLI for 1970 (not used)
        "dppolx": "",# ??? "Desired persistent pollution index
        "tdt": "",   # ??? "Technology development time",
        "nruf1": "NRUFI",
        "druf": "",  # ??? "desired resource utilization rate"
    }
    # Easiest first
    if n in s.nodes:
        return n
    if n in nmap:
        return nmap[n]
    # Constants are most often upper case
    nn = n.upper()
    if nn in s.nodes:
        return nn
    if conf.version == 1972:
        print(f"Ignored in the 1972 version: {n}")
        return ""
    raise ValueError(f"Unknown node name: {n}")

# Read the recelibration constants from PyWorld3-03
def recal23_constants():
    with open("constants.json", 'r') as file:
        data = json.load(file)
    #for key in iter(data['constants']):
    #    dbg(key, data['constants'][key]['value'])
    return data

# Run the PyWorld3-03 model.
# The "State of the World nodes" (sow) nodes are transfered to a
# world3 model for plotting
def pyworld3_run(recal23=False):
    from pyworld3 import World3
    pyworld3 = World3(dt = conf.ts, pyear = 4000)
    if recal23:
        data = recal23_constants()
        params = dict()
        for k in iter(data['constants']):
            params[k] = data['constants'][k]['value']
        pyworld3.init_world3_constants(**params)
    else:
        if conf.scenario == 1:
            pyworld3.init_world3_constants()
        else:
            # All scenarions > 1 are treated as BAU2
            pyworld3.init_world3_constants(nri=2e12)
    pyworld3.init_world3_variables()
    pyworld3.set_world3_table_functions()
    pyworld3.set_world3_delay_functions()
    pyworld3.run_world3(fast=False)

    s = sd.System(init_time=1900, end_time=2100, time_step=conf.ts)
    world3.load(s, scenario=conf.scenario, version=conf.version)
    # Note: the world3 model misses the last sample in hist
    s.nodes["time"].hist = pyworld3.time[:-1]
    s.nodes["f"].hist = pyworld3.f[:-1]
    s.nodes["nr"].hist = pyworld3.nr[:-1]
    s.nodes["io"].hist = pyworld3.io[:-1]
    s.nodes["pop"].hist = pyworld3.pop[:-1]
    s.nodes["ppolx"].hist = pyworld3.ppolx[:-1]
    return s

def recal23(s):
    data = recal23_constants()
    for c in iter(data['constants']):
        n = constant_name(s, c)
        if not n:
            continue
        s.nodes[n].val = data['constants'][c]['value']
    world3.reinit_stocks(s)
    s.reset()

def modify_world3(s, mod):
    match mod:
        case "read_m":
            le.modify_M(s)
        case "modify_m":
            le.modify_M(s)
        case "le":
            w3mod.adjust_le(s)
        case "remove_uconst":
            w3mod.remove_unit_constants(s)
        case "recal23":
            recal23(s)
        case _:
            print("Modification ignored: ", mod)

def modify_help():
    print('''Comma separated list of:
    read_m - Read M from file
    modify_m - Modify M values
    le - Adjust Life Expectancy 
    remove_uconst - Remove unused unit constants
    recal23 - Recalibration23
''')

def load_world3(modify=True):
    s = sd.System(init_time=1900, end_time=2100, time_step=conf.ts)
    world3.load(s, scenario=conf.scenario, version=conf.version)
    if modify and conf.mods:
        for m in conf.mods.split(','):
            modify_world3(s, m)
    return s

def print23_constants():
    data = recal23_constants()
    load_world3()
    s = sd.System(init_time=1900, end_time=2100, time_step=1)
    world3.load(s, scenario=conf.scenario)
    for key in iter(data['constants']):
        n = constant_name(s, key)
        v1 = data['constants'][key]['value']
        if not n:
            print(f"Node not found in world3: {key}={v1}")
            continue
        v2 = s.nodes[n].val
        if v1 != v2:
            print(f"Constant {n}: {v2} -> {v1}")

def emit_category(s, cat):
    if not cat in s.categories():
        print("Categories:", s.categories(), file=sys.stderr)
        return
    print(f'digraph "World3 - {cat}" {{')
    s.graphviz_cat(cat)
    # Emit all internal edges
    for _,n in s.nodes.items():
        if type(n) == sd.NodeConstant:
            continue
        if n.cat != cat:
            continue
        for x in n.succ:
            if x.cat != cat:
                continue
            print(f'{n.name} -> {x.name}')
    # Collect all external edges. I.e ending "cat" but starts outside
    for _,n in s.nodes.items():
        if type(n) == sd.NodeConstant:
            continue
        if n.cat != cat:
            continue
        for x in n.pred:
            if type(x) == sd.NodeConstant:
                continue
            if x.cat == cat:
                continue
            if x.cat == "SYSTEM":
                continue
            if x.cat == "indexes":
                print("Input from index node", x.name, file=sys.stderr)
            s.emit_node(x, emit_category=True)
            print(f'{x.name} -> {n.name}')
    
    print('}')

def emit_cat(s, nodes, cat):
    print(f'subgraph cluster_{cat} {{')
    print(f'label="{cat}"')
    print('pencolor=lightgrey')
    for nn in nodes:
        n = s.nodes[nn]
        if n.cat == cat:
            s.emit_node(n)
    print('}')

# ----------------------------------------------------------------------
# Commands;

def cmd_pyworld3(args):
    """
    Run PyWorld3-03 and compare with world3 (dashed lines)
    """
    parser = argparse.ArgumentParser(
        prog="pyworld3", description=cmd_pyworld3.__doc__)
    parser.add_argument(
        '--recal23', action='store_true', help="Run recalibration23")
    parser.add_argument(
        '--print23', action='store_true', help="Print recal23 constants")
    args = parser.parse_args(args[1:])
    if args.print23:
        print23_constants()
        return 0
    s1 = pyworld3_run(args.recal23)
    s2 = load_world3()
    if args.recal23:
        recal23(s2)
    s2.run()
    sd.plot_nodes(s1, s2, nodes=sow_nodes, title=stitle[conf.scenario-1])

def cmd_run(args):
    """
    Run a scenario and plot. If mods are used the unmodified run is
    plotted with dashed lines.
    """
    parser = argparse.ArgumentParser(prog="run", description=cmd_run.__doc__)
    parser.add_argument(
        '--welfare', action='store_true', help="Show welfare plots")
    args = parser.parse_args(args[1:])
    s = load_world3()
    s.run()
    wf_nodes=[
        ("fpc",(0, 1e3)),("le",(0, 90)),("sopc",(0, 1e3)),("ciopc",(0, 250))]
    ef_nodes=[("hwi",(0, 1)),("hef",(0, 4))]
    if conf.mods:
        # Compare with an unmodified model
        s2 = load_world3(modify=False)
        s2.run()
        sd.plot_nodes(s, s2, nodes=sow_nodes, title=stitle[conf.scenario-1])
        if args.welfare:
            sd.plot_nodes(s, s2, nodes=wf_nodes, title=stitle[conf.scenario-1])
            sd.plot_nodes(s, s2, nodes=ef_nodes, title=stitle[conf.scenario-1])
    else:
        s.plot(*sow_nodes, title=stitle[conf.scenario-1], formatter="eng")
        if args.welfare:
            s.plot(*wf_nodes, title=stitle[conf.scenario-1], formatter="")
            s.plot(*ef_nodes, title=stitle[conf.scenario-1], formatter="")
            
def cmd_bau2(args):
    """
    Run BAU2 and BAU and compare
    """
    parser = argparse.ArgumentParser(prog="bau2", description=cmd_bau2.__doc__)
    args = parser.parse_args(args[1:])
    conf.scenario = 2
    s = load_world3()
    s.run()
    conf.scenario = 1
    s2 = load_world3()
    s2.run()
    sd.plot_nodes(s, s2, nodes=sow_nodes, title="BAU2 (BAU dashed)")

def cmd_mods(args):
    modify_help()

def cmd_animate(args):
    """
    Animate resources from 1e12 (bau1) to 2e12 (bau2)
    """
    parser = argparse.ArgumentParser(
        prog="animate", description=cmd_animate.__doc__)
    parser.add_argument(
        '--save', action='store_true', help="Save plots")
    args = parser.parse_args(args[1:])
    s = load_world3()
    NRI = s.nodes['NRI']
    nr = s.nodes['nr']
    i = 0
    for r in numpy.linspace(1e12, 2e12, num=10):
        NRI.val = r
        nr.hist[0] = r
        s.reset()
        s.run()
        s.plot(*sow_nodes, title="State Of The World", pause=2, formatter="eng")
        if args.save:
            i = i + 1
            plt.savefig(f"animate-{i:02d}.svg", format="svg", transparent=True)
    plt.show()   # keep the window open after the last iteration

def cmd_graph(args):
    """
    Emit a world3 graphviz model graph. Pipe output through
    "| dot -Tsvg > model.svg" or "| dot -Tx11"
    The entire graph very complex. For learning, emit categories instead.
    """
    parser = argparse.ArgumentParser(
        prog="graph", description=cmd_graph.__doc__)
    parser.add_argument(
        '-c', '--category', default="", help="Category and it's input nodes")
    args = parser.parse_args(args[1:])
    s = sd.System(init_time=1900, end_time=2100, time_step=1)
    world3.load(s)
    if args.category:
        emit_category(s, args.category)
        return
    s.graphviz(title="World3")

def cmd_demography(args):
    """
    Compare population and life expectancy to empirical data
    """
    parser = argparse.ArgumentParser(
        prog="demography", description=cmd_demography.__doc__)
    args = parser.parse_args(args[1:])
    s = load_world3()
    emp.load_wpop(s)
    emp.load_wle(s)
    s.run()
    s2 = load_world3(modify=False)
    emp.load_wpop(s2)
    emp.load_wle(s2)
    s2.run()
    t = s.nodes["time"]
    interval=(2000,2025)
    print(f"Normalized Root Mean Square Error (or Difference): {interval}")
    nrmse = sd.nrmse_snodes(s2, 'wpop', 'pop', interval=interval)
    print(f"NRMSE(pop) = {nrmse*100:.2f}% (unmodified)")
    nrmse = sd.nrmse_snodes(s, 'wpop', 'pop', interval=interval)
    print(f"NRMSE(pop) = {nrmse*100:.2f}%")
    nrmse = sd.nrmse_snodes(s2, 'wle', 'le', interval=interval)
    print(f"NRMSE(le) = {nrmse*100:.2f}% (unmodified)")
    nrmse = sd.nrmse_snodes(s, 'wle', 'le', interval=interval)
    print(f"NRMSE(le) = {nrmse*100:.2f}%")
    nodes=[("pop",(0,10e9)), ("wpop",(0,10e9)), ("le",(0,90)), ("wle",(0,90))]
    sd.plot_nodes(s, s2, nodes=nodes, title=stitle[conf.scenario-1], size=(8,4))

def cmd_rates(args):
    """
    Compare crude rates to empirical data
    """
    parser = argparse.ArgumentParser(
        prog="rates", description=cmd_rates.__doc__)
    args = parser.parse_args(args[1:])
    s = load_world3()
    emp.load_wcbr(s)
    emp.load_wcdr(s)
    s.run()
    s2 = load_world3(modify=False)
    emp.load_wcbr(s2)
    emp.load_wcdr(s2)
    s2.run()
    print(f"Normalized Root Mean Square Error (or Difference)")
    nrmse = sd.nrmse_snodes(s2, 'wcbr', 'cbr')
    print(f"NRMSE(cbr) = {nrmse*100:.2f}% (unmodified)")
    nrmse = sd.nrmse_snodes(s, 'wcbr', 'cbr')
    print(f"NRMSE(cbr) = {nrmse*100:.2f}%")
    nrmse = sd.nrmse_snodes(s2, 'wcdr', 'cdr')
    print(f"NRMSE(cdr) = {nrmse*100:.2f}% (unmodified)")
    nrmse = sd.nrmse_snodes(s, 'wcdr', 'cdr')
    print(f"NRMSE(cdr) = {nrmse*100:.2f}%")
    nodes=[("cbr",(0,50)), ("cdr", (0,50)), ("wcbr",(0,50)), ("wcdr",(0,50))]
    sd.plot_nodes(s, s2, nodes=nodes, title=stitle[conf.scenario-1])

def cmd_hef(args):
    """
    Compare Human Ecological Footprint (hef) to empirical data.
    Note that hef is a derived value, the simulation is not affected
    """
    parser = argparse.ArgumentParser(
        prog="hef", description=cmd_hef.__doc__)
    args = parser.parse_args(args[1:])
    s = load_world3()
    emp.load_whef(s)
    w3mod.recalibrate_hef(s)
    s.run()
    s2 = load_world3(modify=False)
    emp.load_whef(s2)
    w3mod.recalibrate_hef(s2)
    s2.run()
    nodes=[
        ("hef",(0,25e9)), ("algha",(0,25e9)), ("whef",(0,25e9)),
        ("walg",(0,25e9))]
    sd.plot_nodes(s, s2, nodes=nodes, title=stitle[conf.scenario-1])

# ----------------------------------------------------------------------
# Parse args

def parse_args():
    cmdfn = [n for n in globals() if n.startswith('cmd_')]
    cmds = [x.removeprefix('cmd_') for x in cmdfn]

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', action='count', default=0, help="verbose")
    parser.add_argument('-s', '--scenario', type=int, default=1)
    parser.add_argument(
        '--version', type=int, default=2003, help="Version. 1972 or 2003")
    parser.add_argument('--ts', type=float, default=1.0, help="time-step")
    parser.add_argument('-m', '--mods', default="")    
    parser.add_argument('cmd', choices=cmds, nargs=argparse.REMAINDER)
    global conf
    conf = parser.parse_args()

    global dbg
    if conf.v:
        dbg = getattr(__builtins__, 'print')
    dbg("Program starting", conf, cmds)

    # Why is this necessary? Bug?
    if not conf.cmd:
        parser.print_help()
        sys.exit(0)
    if conf.cmd[0] not in cmds:
        print("Invalid command")
        sys.exit(1)

    cmd_function = globals()["cmd_" + conf.cmd[0]]
    sys.exit(cmd_function(conf.cmd))


if __name__ == '__main__':
    parse_args()
