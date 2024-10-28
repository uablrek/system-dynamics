#! /usr/bin/python
# SPDX-License-Identifier: Unlicense

import system_dynamic as sd
import world3_model as world3
from demographics import load_wpop, load_wle
from le import modify_M
import numpy
import matplotlib.pyplot as plt

# Run a scenario and plot data
def scenario(scenario):
    s = sd.System(init_time=1900, end_time=2100, time_step=0.5)
    world3.load(s, scenario=scenario)
    s.run()
    s.plot("pop", "nr", "io", "f", "ppolx", title="State Of The World")
    s.plot("fpc", "le", "sopc", "ciopc", title="Material Standard Of Living")

# Plot BAU2 with scales similar to LtG
def bau2():
    s = sd.System(init_time=1900, end_time=2100, time_step=0.5)
    world3.load(s, scenario=2)
    #modify_M(s)  # (makes no difference)
    s.run()
    s.plot(
        ("pop",(0,10e9)), ("nr",(0,2e12)), ("io",(0,4e12)), ("f",(0,6e12)),
        ("ppolx",(0,40)), title="State Of The World")

# Animate resources from 1e12 (bau1) to 2e12 (bau2)
def bau2_animation():
    s = sd.System(init_time=1900, end_time=2100, time_step=0.5)
    world3.load(s, scenario=2)
    NRI = s.nodes['NRI']
    nr = s.nodes['nr']
    for r in numpy.linspace(1e12, 2e12, num=10):
        NRI.val = r
        nr.hist[0] = r
        s.reset()
        s.run()
        s.plot(
            ("pop",(0,10e9)), ("nr",(0,2e12)), ("io",(0,4e12)), ("f",(0,6e12)),
            ("ppolx",(0,40)), title="State Of The World", pause=2)
        #plt.savefig(f"bau2-{r}.svg", format="svg", transparent=True)
    plt.show()   # keep the window open after the last iteration


# Plot population and life expectancy against empirical data
def demography(scenario):
    s = sd.System(init_time=1900, end_time=2100, time_step=0.5)
    world3.load(s, scenario=scenario)
    modify_M(s)    # Correct Mortality rates (no visible effect)
    load_wpop(s)
    load_wle(s)
    s.run()
    s.plot(
        ("pop",(0,10e9)), ("wpop",(0,10e9)), ("le",(0,90)), ("wle",(0,90)),
        size=(8,4))

# Emit a graphviz model graph
def model_graph():
     s = sd.System(init_time=1900, end_time=2100, time_step=0.5)
     world3.load(s)
     s.graphviz(title="World3")


# Run a function
if __name__ == "__main__":
    bau2()
    #demography(2)
