#! /usr/bin/python
# SPDX-License-Identifier: Unlicense

import system_dynamic as sd
from system_dynamic import C, CT
import matplotlib.pyplot as plt
import json

def load_pop(world3):
    s = world3
    s.default_cat = 'population'

    B = s.addConstant(
        "B", sd.C, val=1000, detail="Fixed births", unit="children/year")
    LE = s.addConstant(
        "LE", sd.C, val=70, detail="Fixed life expectancy", unit="years")
    P1I = s.addConstant("P1I", C, val=0)
    P2I = s.addConstant("P2I", C, val=0)
    P3I = s.addConstant("P3I", C, val=0)
    P4I = s.addConstant("P4I", C, val=0)

    # Copied from world_model.py
    M1 = world3.addConstant(
        "M1", CT, val=(
            [20, 0.0567],
            [30, 0.0366],
            [40, 0.0243],
            [50, 0.0155],
            [60, 0.0082],
            [70, 0.0023],
            [80, 0.001]),
        detail="Mortality rate 0-14 years", unit="f(le)")
    M2 = world3.addConstant(
        "M2", CT, val=(
            [20, 0.0266],
            [30, 0.0171],
            [40, 0.011],
            [50, 0.0065],
            [60, 0.004],
            [70, 0.0016],
            [80, 0.0008]),
        detail="Mortality rate 15-44 years", unit="f(le)")
    M3 = world3.addConstant(
        "M3", CT, val=(
            [20, 0.0562],
            [30, 0.0373],
            [40, 0.0252],
            [50, 0.0171],
            [60, 0.0118],
            [70, 0.0083],
            [80, 0.006]),
        detail="Mortality 45-64 years", unit="f(le)")
    M4 = world3.addConstant(
        "M4", CT, val=(
            [20, 0.13],
            [30, 0.11],
            [40, 0.09],
            [50, 0.07],
            [60, 0.06],
            [70, 0.05],
            [80, 0.04]),
        detail="Mortality older than age 65", unit="f(le)")

    p1 = world3.addStock(
        "p1", val=P1I.val, detail="0 to 14 years", unit="capita")
    p2 = world3.addStock(
        "p2", val=P2I.val, detail="15 to 44 years", unit="capita")
    p3 = world3.addStock(
        "p3", val=P3I.val, detail="45 to 64 years", unit="capita")
    p4 = world3.addStock(
        "p4", val=P4I.val, detail="older than age 65", unit="capita")

    m1 = world3.addFlow("m1", detail="Mortality 0-14", unit="rate")
    m2 = world3.addFlow("m2", detail="Mortality 15-44", unit="rate")
    m3 = world3.addFlow("m3", detail="Mortality 45-64", unit="rate")
    m4 = world3.addFlow("m4", detail="Mortality 65-", unit="rate")

    d1 = world3.addFlow("d1", detail="Deaths 0-14", unit="capita/year")
    d2 = world3.addFlow("d2", detail="Deaths 15-44", unit="capita/year")
    d3 = world3.addFlow("d3", detail="Deaths 45-64", unit="capita/year")
    d4 = world3.addFlow("d4", detail="Deaths 65-", unit="capita/year")

    mat1 = world3.addFlow("mat1", detail="Maturation 14 years", unit="rate")
    mat2 = world3.addFlow("mat2", detail="Maturation 44 years", unit="rate")
    mat3 = world3.addFlow("mat3", detail="Maturation 64 years", unit="rate")

    # Complete the population system
    pop = world3.addFlow("pop", detail="Total Population", unit="capita")
    le = world3.addFlow("le", detail="Life Expetancy", unit="years")
    b = world3.addFlow("b", detail="Births", unit="children/year")
    s.add_equation(sd.f_sum, pop, [p1,p2,p3,p4])
    s.add_equation(sd.f_sum, le, [LE])
    s.add_equation(sd.f_sum, b, [B])


    # Functions which are not defined in basic ones
    def nodes_mltpld(*l):
        out = l[0]
        for x in l[1:]:
            out = out * x
        return out
    def nodes_dif(x, y): return x - y
    def p1_evo(b, d1, mat1): return b - d1 - mat1
    def p2_evo(mat1, d2, mat2): return mat1 - d2 - mat2
    def p3_evo(mat2, d3, mat3): return mat2 - d3 - mat3
    def f_mat1(p1, m1): return p1 * (1 - m1) / 15
    def f_mat2(p2, m2): return p2 * (1 - m2) / 30
    def f_mat3(p3, m3): return p3 * (1 - m3) / 20

    # Population dynamics

    s.add_equation(p1_evo, p1, [b, d1, mat1])
    s.add_equation(nodes_mltpld, d1, [p1, m1])
    s.add_equation(sd.f_tab, m1, [M1, le])
    s.add_equation(f_mat1, mat1, [p1, m1])

    s.add_equation(p2_evo, p2, [mat1, d2, mat2])
    s.add_equation(nodes_mltpld, d2, [p2, m2])
    s.add_equation(sd.f_tab, m2, [M2, le])
    s.add_equation(f_mat2, mat2, [p2, m2])

    s.add_equation(p3_evo, p3, [mat2, d3, mat3])
    s.add_equation(nodes_mltpld, d3, [p3, m3])
    s.add_equation(sd.f_tab, m3, [M3, le])
    s.add_equation(f_mat3, mat3, [p3, m3])

    s.add_equation(nodes_dif, p4, [mat3, d4])
    s.add_equation(nodes_mltpld, d4, [p4, m4])
    s.add_equation(sd.f_tab, m4, [M4, le])

# Modify Mortality rates (experimental)
def modify_M(s):
    M1 = s.nodes['M1']
    M2 = s.nodes['M2']
    M3 = s.nodes['M3']
    M4 = s.nodes['M4']
    M1.val=(
        [20, 0.0567],
        [30, 0.0366],
        [40, 0.0241],
        [50, 0.0155],
        [60, 0.0084],
        [70, 0.0034],
        [80, 0.0013],
        [90, 0.0010])
    M2.val=(
        [20, 0.0266],
        [30, 0.0171],
        [40, 0.0100],
        [50, 0.0065],
        [60, 0.0042],
        [70, 0.0025],
        [80, 0.0025],
        [90, 0.0034])
    M3.val=(
        [20, 0.0562],
        [30, 0.0373],
        [40, 0.0252],
        [50, 0.0171],
        [60, 0.0119],
        [70, 0.0086],
        [80, 0.0055],
        [90, 0.0040])
    M4.val=(
        [20, 0.13],
        [30, 0.11],
        [40, 0.09],
        [50, 0.07],
        [60, 0.06],
        [70, 0.052],
        [80, 0.038],
        [90, 0.026])

# Read Mx constants from a json file
def read_M(s, file="data/M.json"):
    with open(file) as fd:
        d = json.load(fd)
    s.update(d)

def simple_plot(s):
    s.run()
    pop = s.nodes["pop"]
    print(f"Final {pop.hist[-1]}")
    s.plot("pop")
    #print(json.dumps(s.dict_nodes('M1', 'M2', 'M3', 'M4')))

def plot_age(s):
    x = [0, 14.99, 15, 44.99, 45, 64.99, 65, 90]
    LE = s.nodes["LE"]
    for le in range(30, 95, 5):
        LE.val = le
        s.reset()
        s.run()
        p1 = s.nodes['p1']
        p2 = s.nodes['p2']
        p3 = s.nodes['p3']
        p4 = s.nodes['p4']
        pop = s.nodes['pop']
        v1 = p1.val/pop.val/15
        v2 = p2.val/pop.val/30
        v3 = p3.val/pop.val/20
        v4 = p4.val/pop.val/25
        y = [v1,v1,v2,v2,v3,v3,v4,v4]
        fig = plt.gcf()
        fig.clear()
        fig.suptitle(f"le={le}")
        ax = plt.axes()
        ax.set_ylim(0,0.025)
        ax.plot(x, y)
        plt.pause(3)
    plt.show()

def plot_xxy(x, y):
    ax = plt.axes()
    ax.grid(axis='both', linestyle=':')
    ax.plot(x, x, '--')
    ax.plot(x, y)
    plt.show()
    
def le_test(s):
    LE = s.nodes["LE"]
    pop = s.nodes["pop"]
    x = range(28, 95, 2)
    y = []
    for le in x:
        LE.val = le
        s.reset()
        s.run()
        v = pop.hist[-1]
        y.append(v/1000)
        #print(f"{le}: {v}")
    plot_xxy(x, y)
    
if __name__ == "__main__":
    s = sd.System(init_time=0, end_time=300, time_step=1)
    load_pop(s)
    modify_M(s)
    #read_M(s, file="data/M.json")
    #s.graphviz(title="Population")
    #simple_plot(s)
    #le_test(s)
    plot_age(s)
