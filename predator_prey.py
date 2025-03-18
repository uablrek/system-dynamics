#! /usr/bin/python
# SPDX-License-Identifier: Unlicense

"""
Implement a predator/play model as described in:
https://en.wikipedia.org/wiki/Lotka%E2%80%93Volterra_equations
"""

import sys
import argparse
import system_dynamic as sd
dbg = lambda *arg: 0

def f_pop(births, deaths):
    return births - deaths

def max_pop(s):
    prey = s.nodes["prey"]
    predator = s.nodes["predator"]
    return max(prey.hist + predator.hist)

def csl2float(s, l):
    f = [float(i) for i in s.split(',')]
    if len(f) != l:
        raise ValueError(f"Invalid lenght. Must be {l}")
    return f

def load_model(s, c, i):
    # alpha,beta,gamma,delta in the Lotka–Volterra equations
    prbr = s.addConstant("prbr", sd.C, detail='Prey birth rate', val=c[0])
    pdeff = s.addConstant("pdeff", sd.C, detail='Predator effect', val=c[1])
    wdr = s.addConstant("pddr", sd.C, detail='Predator death rate', val=c[2])
    preff = s.addConstant("preff", sd.C, detail='Prey effect', val=c[3])

    prey = s.addStock("prey", detail='Prey', val=i[0])
    predator = s.addStock("predator", detail='Predators', val=i[1])

    prb = s.addFlow("prey_births")
    prd = s.addFlow("prey_deaths")
    pdb = s.addFlow("predator_births")
    pdd = s.addFlow("predator_deaths")

    s.add_equation(sd.f_mul, prb, [prey, prbr])
    s.add_equation(sd.f_mul, prd, [pdeff, prey, predator])
    s.add_equation(sd.f_mul, pdb, [preff, predator, prey])
    s.add_equation(sd.f_mul, pdd, [predator, wdr])

    s.add_equation(f_pop, prey, [prb, prd], ['+','-'])
    s.add_equation(f_pop, predator, [pdb, pdd], ['+','-'])

# ----------------------------------------------------------------------
# Commands;

def cmd_run(args):
    """
    Run the model and show a plot.
    The constants given with --c are:
      prey-birth-rate,predator-effect,predator-death-rate,prey-effect
      (alpha,beta,gamma,delta in the Lotka–Volterra equations)
    """
    parser = argparse.ArgumentParser(
        prog="run", description=cmd_run.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--ts', type=float, default=0.001, help="time-step")
    parser.add_argument(
        '--c', default="1.1,0.4,0.4,0.1",
        help="constants: alpha,beta,gamma,delta")
    parser.add_argument(
        '--i', default="10,10", help="initial values: prey,predator")
    args = parser.parse_args(args[1:])
    c = [float(i) for i in args.c.split(',')]
    s = sd.System(time_step=args.ts, end_time=100, time_unit="time")
    load_model(s, csl2float(args.c, 4), csl2float(args.i, 2))
    s.run()
    max = max_pop(s) * 1.1
    nodes = [("prey",(0,max)), ("predator",(0,max))]
    s.plot(*nodes, title='Predator and Prey', size=(8,4))
    return 0

def cmd_graph(args):
    """
    Emit graphviz data for the model
    """
    s = sd.System(time_step=1, end_time=25)
    load_model(s, [0,0,0,0], [0,0])
    s.graphviz('predator+prey')
    sys.exit()
    return 0

# ----------------------------------------------------------------------
# Parse args

def parse_args():
    cmdfn = [n for n in globals() if n.startswith('cmd_')]
    cmds = [x.removeprefix('cmd_') for x in cmdfn]

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', action='count', default=0, help="verbose")
    parser.add_argument('cmd', choices=cmds, nargs=argparse.REMAINDER)
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
    
if __name__ == "__main__":
    parse_args()
