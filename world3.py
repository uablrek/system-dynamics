#! /usr/bin/python

import system_dynamic as sd
import world3_model as world3
from demographics import load_wpop, load_wle

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
    s.run()
    s.plot(
        ("pop",(0,10e9)), ("nr",(0,2e12)), ("io",(0,4e12)), ("f",(0,6e12)),
        ("ppolx",(0,40)), title="State Of The World")

# Plot population and life expectancy against empirical data
def demography(scenario):
    s = sd.System(init_time=1900, end_time=2100, time_step=0.5)
    world3.load(s, scenario=scenario)
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
