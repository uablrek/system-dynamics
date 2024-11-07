#! /usr/bin/python
# SPDX-License-Identifier: Unlicense

import system_dynamic as sd
import world3_model as world3
import empirical_data as emp
from le import modify_M, read_M
import numpy
import matplotlib.pyplot as plt
import world3_modifications as w3mod

ts=0.5
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
# State of the World nodes
sow_nodes=[
    ("pop",(0,12e9)), ("nr",(0,2e12)), ("io",(0,4e12)), ("f",(0,6e12)),
    ("ppolx",(0,40))]

# Load the world3 model
def load(scenario):
    s = load_unmodified(scenario)
    # (tweaks goes here...)
    #read_M(s)
    modify_M(s)
    #w3mod.remove_unit_constants(s)
    w3mod.adjust_le(s)
    #w3mod.recalibration23(s)
    return s
def load_unmodified(scenario):
    s = sd.System(init_time=1900, end_time=2100, time_step=ts)
    world3.load(s, scenario=scenario)
    return s
# Run both an unmodified and a modified model
def run_both(scenario):
    s = load(scenario)
    s.run()
    s2 = load_unmodified(scenario)
    s2.run()
    return s, s2

# Run a scenario and plot data with scales similar to LtG
def scenario(scenario):
    s = load(scenario)
    s.run()
    s.plot(*sow_nodes, title=stitle[scenario-1], formatter="eng")

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
        s.plot(*sow_nodes, title="State Of The World", pause=2, formatter="eng")
        #plt.savefig(f"bau2-{r}.svg", format="svg", transparent=True)
    plt.show()   # keep the window open after the last iteration


# Compare population and life expectancy to empirical data
def demography(scenario):
    s = load(scenario)
    emp.load_wpop(s)
    emp.load_wle(s)
    s.run()
    s2 = load_unmodified(scenario)
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
    sd.plot_nodes(s, s2, nodes=nodes, title=stitle[scenario-1], size=(8,4))

# Emit a graphviz model graph
def model_graph():
     s = sd.System(init_time=1900, end_time=2100, time_step=0.5)
     world3.load(s)
     s.graphviz(title="World3")

# Compare a modified system with an unmodified
def compare(scenario):
    s, s2 = run_both(scenario)
    sd.plot_nodes(s, s2, nodes=sow_nodes, title=stitle[scenario-1])

def compare_welfare(scenario):
    s, s2 = run_both(scenario)
    nodes=[
        ("fpc",(0, 1e3)),("le",(0, 90)),("sopc",(0, 1e3)),("ciopc",(0, 250))]
    sd.plot_nodes(s, s2, nodes=nodes, title=stitle[scenario-1], formatter='')
    nodes=[("hwi",(0, 1)),("hef",(0, 4))]
    sd.plot_nodes(s, s2, nodes=nodes, title=stitle[scenario-1], formatter='')

# Compare BAU and BAU2
def compare_bau():
    s = load_unmodified(2)
    s.run()
    s2 = load_unmodified(1)
    s2.run()
    sd.plot_nodes(s, s2, nodes=sow_nodes, title="BAU2 (and BAU)")

def crude_rates(scenario):
    s = load(scenario)
    emp.load_wcbr(s)
    emp.load_wcdr(s)
    s.run()
    s2 = load_unmodified(scenario)
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
    sd.plot_nodes(s, s2, nodes=nodes, title=stitle[scenario-1])

def recalibrate_hef(scenario):
    s = load(scenario)
    emp.load_whef(s)
    w3mod.recalibrate_hef(s)
    s.run()
    s2 = load_unmodified(scenario)
    emp.load_whef(s2)
    w3mod.recalibrate_hef(s2)
    s2.run()
    nodes=[
        ("hef",(0,25e9)), ("algha",(0,25e9)), ("whef",(0,25e9)),
        ("walg",(0,25e9))]
    sd.plot_nodes(s, s2, nodes=nodes, title=stitle[scenario-1])
    
# Run a function
import sys
if __name__ == "__main__":
    n = 2
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    #scenario(n)
    #demography(n)
    #bau2_animation()
    #compare(n)
    #compare_welfare(n)
    #compare_bau()
    #crude_rates(n)
    recalibrate_hef(n)
