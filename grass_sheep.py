#! /usr/bin/python
# SPDX-License-Identifier: Unlicense

"""
A *very* simple plant-herbivore model
"""

import sys
import argparse
import system_dynamic as sd
dbg = lambda *arg: 0

# The node names must be unique, so they may be prefixed with the
# category
def cat_grass(s):
    cat = "grass"
    s.default_cat = cat
    # Constants
    area = s.addConstant(
        f'{cat}_area', sd.C, detail="Area where grass grows",
        unit="ha", val=100)
    max = s.addConstant(
        f'{cat}_max', sd.C, detail="Max grass",
        unit="kg/ha", val=5500)
    rate = s.addConstant(
        f'{cat}_rate', sd.C, detail="Grass growth rate",
        unit="kg/ha/year", val=5500)
    # Stocks and Flows
    i = area.val*max.val
    grass = s.addStock(
        "grass", detail="Ammount of grass", unit="kg", val=i/2, max=i)
    growth = s.addFlow("growth", detail="Grass growth", unit="kg")
    # Equations (edges)
    s.add_equation(sd.f_mul, growth, [area, rate])
    # (this will be modified to include grazing in the final model)
    s.add_equation(sd.f_sum, grass, [growth])

# This is a simplified polulation model. If the birth rate is larger
# than the death rate, the polulation will grow exponentially.
def cat_sheep(s, br=0.5, dr=0.1):
    cat="sheep"
    s.default_cat = cat
    # Constants
    rbirth = s.addConstant(
        f'{cat}_birth_rate', sd.C, detail='Birth rate',
        unit="n/year/sheep", val=br)
    rdeath = s.addConstant(
        f'{cat}_death_rate', sd.C, detail='Death rate',
        unit="n/year/sheep", val=dr)
    # Stocks and Flows
    birth = s.addFlow("births", detail="Sheep born", unit="n/year")
    death = s.addFlow("deaths", detail="Sheep died", unit="n/year")
    sheep = s.addStock("sheep", detail='Number of sheep', unit="n", val=100)
    # Equations (edges)
    s.add_equation(sd.f_mul, birth, [sheep, rbirth])
    s.add_equation(sd.f_mul, death, [sheep, rdeath])
    # (this will be modified to include starvation in the final model)
    def f_sheep(birth, death):
        return birth - death
    s.add_equation(f_sheep, sheep, [birth, death])

def load_model(s, delay=0, br=0.5, dr=0.1):
    cat_grass(s)
    cat_sheep(s, br, dr)
    s.default_cat = None
    # Connect the grass and sheep categories (sub-systems)
    # Constants
    eats = s.addConstant(
        'eats', sd.C, detail='How much a sheep eats', unit="kg/year", val=900)
    D = s.addConstant(
        'delay_constant', sd.C, detail='Delay constant',
        unit="years", val=delay)    
    # Stocks and Flows
    graze = s.addFlow(
        "graze", detail="Grass grazed", unit="kg/year")
    starvation = s.addFlow(
        "starvation", detail="Sheep starving", unit="n")
    dd = s.addDelay3(
        'dd', detail="Delay for death by starvation", unit='n')
    # Equations (edges)
    # Really simplified, sheep that don't have food starves
    def f_starvation(grass, sheep, eat):
        supported_sheep = grass / eat
        if supported_sheep >= sheep:
            return 0
        return sheep - supported_sheep
    sheep = s.nodes["sheep"]
    grass = s.nodes["grass"]
    growth = s.nodes["growth"]
    birth = s.nodes["births"]
    death = s.nodes["deaths"]
    s.add_equation(sd.f_mul, graze, [sheep, eats])
    s.add_equation(sd.f_minus, grass, [growth, graze])
    s.add_equation(f_starvation, starvation, [grass, sheep, eats])
    s.add_equation(dd.f_delayinit, dd, [starvation, D])
    def f_sheep(birth, death, starvation):
        return birth - death - starvation
    s.add_equation(f_sheep, sheep, [birth, death, dd])

# ----------------------------------------------------------------------
# Commands;

def cmd_run(args):
    """
    Run the model and show a plot
    """
    parser = argparse.ArgumentParser(
        prog="run", description=cmd_run.__doc__)
    parser.add_argument('--ts', type=float, default=0.01, help="time-step")
    parser.add_argument(
        '--dd', type=float, default=0, help="Delay for starvation death")
    parser.add_argument('--br', type=float, default=0.5, help="Birth rate")
    parser.add_argument('--dr', type=float, default=0.1, help="Death rate")
    args = parser.parse_args(args[1:])
    s = sd.System(time_step=args.ts, end_time=25)
    load_model(s, delay=args.dd, br=args.br, dr=args.dr)
    s.run()
    s.plot_stocks(title='Grass and Sheep', size=(8,4))
    return 0

def cmd_graph(args):
    """
    Emit graphviz data for the model
    """
    s = sd.System(time_step=1, end_time=25)
    load_model(s)
    s.graphviz('grass+sheep')
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
