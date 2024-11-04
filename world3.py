#! /usr/bin/python
# SPDX-License-Identifier: Unlicense

import system_dynamic as sd
import world3_model as world3
from demographics import load_wpop, load_wle
from le import modify_M, read_M
import numpy
import matplotlib.pyplot as plt
import world3_modifications as w3mod

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

# Load the world3 model
def load(scenario):
    s = sd.System(init_time=1900, end_time=2100, time_step=0.2)
    world3.load(s, scenario=scenario)
    # (tweaks goes here...)
    #read_M(s)
    modify_M(s)
    #w3mod.remove_unit_constants(s)
    w3mod.adjust_le(s)
    #w3mod.recalibration23(s)
    return s

# Run a scenario and plot data with scales similar to LtG
def scenario(scenario):
    s = load(scenario)
    s.run()
    s.plot(
        ("pop",(0,12e9)), ("nr",(0,2e12)), ("io",(0,4e12)), ("f",(0,6e12)),
        ("ppolx",(0,40)), title=stitle[scenario-1], formatter="eng")

# Animate resources from 1e12 (bau1) to 2e12 (bau2)
def bau2_animation():
    s = load(2)
    NRI = s.nodes['NRI']
    nr = s.nodes['nr']
    for r in numpy.linspace(1e12, 2e12, num=10):
        NRI.val = r
        nr.hist[0] = r
        s.reset()
        s.run()
        s.plot(
            ("pop",(0,10e9)), ("nr",(0,2e12)), ("io",(0,4e12)), ("f",(0,6e12)),
            ("ppolx",(0,40)), title="State Of The World", pause=2,
            formatter="eng")
        #plt.savefig(f"bau2-{r}.svg", format="svg", transparent=True)
    plt.show()   # keep the window open after the last iteration


# Plot population and life expectancy against empirical data
def demography(scenario):
    s = load(scenario)
    load_wpop(s)
    load_wle(s)
    s.run()
    s2 = sd.System(init_time=1900, end_time=2100, time_step=0.2)
    world3.load(s2, scenario=scenario)
    load_wpop(s2)
    load_wle(s2)
    s2.run()
    nodes=[("pop",(0,10e9)), ("wpop",(0,10e9)), ("le",(0,90)), ("wle",(0,90))]
    sd.plot_nodes(s, s2, nodes=nodes, title=stitle[scenario-1], size=(8,4))

# Emit a graphviz model graph
def model_graph():
     s = sd.System(init_time=1900, end_time=2100, time_step=0.5)
     world3.load(s)
     s.graphviz(title="World3")

# Compare a modified system with an unmodified
def dual_sys_plot(scenario):
    s = load(scenario)
    s.run()
    s2 = sd.System(init_time=1900, end_time=2100, time_step=0.2)
    world3.load(s2, scenario=scenario)
    s2.run()
    nodes=[
        ("pop",(0,12e9)), ("nr",(0,2e12)), ("io",(0,4e12)), ("f",(0,6e12)),
        ("ppolx",(0,40))]
    sd.plot_nodes(s, s2, nodes=nodes, title=stitle[scenario-1])


# Run a function
import sys
if __name__ == "__main__":
    n = 2
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    scenario(n)
    #demography(n)
    #bau2_animation()
    #dual_sys_plot(n)
