#! /usr/bin/python
# SPDX-License-Identifier: Unlicense

import system_dynamic as sd

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
def cat_sheep(s):
    cat="sheep"
    s.default_cat = cat
    # Constants
    rbirth = s.addConstant(
        f'{cat}_birth_rate', sd.C, detail='Birth rate',
        unit="n/year/sheep", val=0.5)
    rdeath = s.addConstant(
        f'{cat}_death_rate', sd.C, detail='Death rate',
        unit="n/year/sheep", val=0.1)
    # Stocks and Flows
    birth = s.addFlow("births", detail="Sheep born", unit="n/year")
    death = s.addFlow("deaths", detail="Sheep died", unit="n/year")
    sheep = s.addStock("sheep", detail='Number of sheep', unit="n", val=100)
    # Equations (edges)
    s.add_equation(sd.f_mul, birth, [sheep, rbirth])
    s.add_equation(sd.f_mul, death, [sheep, rdeath], sign=-1)
    # (this will be modified to include starvation in the final model)
    s.add_equation(sd.f_sum, sheep, [birth, death])

def load_model(s):
    cat_grass(s)
    cat_sheep(s)
    s.default_cat = None
    # Connect the grass and sheep categories (sub-systems)
    # Constants
    eats = s.addConstant(
        'eats', sd.C, detail='How much a sheep eats', unit="kg/year", val=900)
    # Stocks and Flows
    graze = s.addFlow(
        "graze", detail="Grass grazed", unit="kg/year")
    starvation = s.addFlow(
        "starvation", detail="Sheep starving", unit="n")
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
    s.add_equation(sd.f_mul, graze, [sheep, eats], sign=-1)
    s.add_equation(sd.f_sum, grass, [growth, graze])
    s.add_equation(f_starvation, starvation, [grass, sheep, eats], sign=-1)
    s.add_equation(sd.f_sum, sheep, [birth, death, starvation])
    grass.sign = -1 # (makes the model graph looks nicer, but have no impact)

import sys
if __name__ == "__main__":
    s = sd.System(time_step=0.1, end_time=25)
    load_model(s)
    if len(sys.argv) > 1:
        s.graphviz('grass+sheep')
        sys.exit()
    #s.trace("starvation")
    s.run()
    s.plot_stocks(title='Grass and Sheep', size=(8,4))
    #s.plot(["grass", "starvation", "graze"])
