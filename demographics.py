#! /usr/bin/python
# SPDX-License-Identifier: Unlicense

import system_dynamic as sd

# Empirical data of world population. Sources:
# https://sv.wikipedia.org/wiki/V%C3%A4rldens_befolkning
# https://www.worldometers.info/world-population/world-population-by-year/
def load_wpop(s):
    WPOP = s.addConstant(
        "WPOP", sd.CT, unit='capita', detail="World population, empirical data",
        val=[
            (1900, 1.65e9),
            (1910, 1.75e9),
            (1920, 1.86e9),
            (1930, 2.07e9),
            (1940, 2.3e9),
            (1950, 2.52e9),
            (1960, 3.02e9),
            (1970, 3.7e9),
            (1980, 4.45e9),
            (1990, 5.33e9),
            (1995, 5.76e9),
            (2000, 6.17e9),
            (2005, 6.59e9),
            (2010, 7.02e9),
            (2015, 7.47e9),
            (2020, 7.89e9),
            (2023, 8.02e9),
            (2024, 8.2e9)])
    wpop = s.addFlow(
        "wpop", unit='capita', detail="Empirical world population")
    t = s.nodes['time']
    s.add_equation(sd.f_tabclip, wpop, [WPOP, t])

# Empirical data of Life Expectancy. Source:
# https://ourworldindata.org/life-expectancy
# https://www.statista.com/statistics/805060/life-expectancy-at-birth-worldwide/
def load_wle(s):
    WLE = s.addConstant(
        "WLE", sd.CT, unit='years', detail="Life Expectancy, empirical data",
        val=[
            (1900, 32),
            (1913, 34.1),
            (1950, 46.5),
            (1958, 51.5),
            (1960, 47.7),
            (1962, 53.12),
            (1965, 53.9),
            (1970, 56.1),
            (1980, 60.6),
            (1990, 64),
            (1995, 64.9),
            (2000, 66.5),
            (2005, 68.2),
            (2010, 70.1),
            (2015, 71.8),
            (2019, 72.8),
            (2020, 72.0),
            (2021, 71.0),
            (2022, 71.71),
            (2023, 73.36),
            (2024, 73.67)])
    wle = s.addFlow(
        "wle", unit='year', detail="Empirical Life Expectancy")
    t = s.nodes['time']
    s.add_equation(sd.f_tabclip, wle, [WLE, t])

# These sources differs (not used):
# https://www.macrotrends.net/global-metrics/countries/wld/world/population
# https://www.macrotrends.net/global-metrics/countries/wld/world/life-expectancy


if __name__ == "__main__":
    s = sd.System(init_time=1900, end_time=2100, time_step=0.5)
    load_wpop(s)
    load_wle(s)
    s.run()
    s.plot(('wpop', (0,10e9)), ('wle', (0,100)))
    
