#! /usr/bin/python

import system_dynamic as sd
import world3_model as world3

def scenario(scenario):
    s = sd.System(init_time=1900, end_time=2100, time_step=0.5)
    world3.load(s, scenario=scenario)
    s.run()
    s.plot("pop", "nr", "io", "f", "ppolx", title="State Of The World")
    s.plot("fpc", "le", "sopc", "ciopc", title="Material Standard Of Living")

def bau2():
    s = sd.System(init_time=1900, end_time=2100, time_step=0.5)
    world3.load(s, scenario=2)
    nri = s.nodes['NRI']
    nr = s.nodes['nr']
    for c in [1e12, 1.2e12, 1.4e12, 1.6e12, 1.8e12, 2e12]:
        s.reset()
        nri.val = c
        nr.val = nr.hist[0] = c
        s.run()
        s.plot(
            "pop", "nr", "io", "f", "ppolx", title="State Of The World")

if __name__ == "__main__":
    scenario(2)
