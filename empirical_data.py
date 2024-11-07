#! /usr/bin/python
# SPDX-License-Identifier: Unlicense

import system_dynamic as sd

# Empirical data of world population. Sources:
# https://data.worldbank.org/indicator/SP.POP.TOTL
# https://sv.wikipedia.org/wiki/V%C3%A4rldens_befolkning
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
            (1960, 3031517384),
            (1961, 3072470012),
            (1962, 3126894230),
            (1963, 3193470069),
            (1964, 3260479625),
            (1965, 3328242834),
            (1966, 3398509802),
            (1967, 3468395137),
            (1968, 3540185668),
            (1969, 3614592846),
            (1970, 3690229198),
            (1971, 3767950635),
            (1972, 3843630361),
            (1973, 3920044841),
            (1974, 3995920225),
            (1975, 4070060140),
            (1976, 4143135434),
            (1977, 4215876682),
            (1978, 4289852068),
            (1979, 4365802882),
            (1980, 4442416674),
            (1981, 4520993169),
            (1982, 4602785312),
            (1983, 4684967631),
            (1984, 4766740755),
            (1985, 4850182355),
            (1986, 4936116651),
            (1987, 5024401475),
            (1988, 5113495865),
            (1989, 5202686551),
            (1990, 5293498452),
            (1991, 5382640911),
            (1992, 5470271607),
            (1993, 5556732311),
            (1994, 5642156981),
            (1995, 5726848893),
            (1996, 5811694918),
            (1997, 5896174827),
            (1998, 5979851049),
            (1999, 6062415429),
            (2000, 6144444748),
            (2001, 6226487141),
            (2002, 6308284566),
            (2003, 6389592840),
            (2004, 6471033757),
            (2005, 6552787172),
            (2006, 6635162568),
            (2007, 6717583637),
            (2008, 6801421733),
            (2009, 6885608628),
            (2010, 6969894715),
            (2011, 7053988749),
            (2012, 7141430933),
            (2013, 7229458453),
            (2014, 7317304568),
            (2015, 7404251118),
            (2016, 7490956237),
            (2017, 7577110140),
            (2018, 7661177849),
            (2019, 7742724795),
            (2020, 7821271846),
            (2021, 7888963821),
            (2022, 7951595433),
            (2023, 8024997028),
            (2024, 8.186e9)])
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
        "wle", unit='years', detail="Empirical Life Expectancy")
    t = s.nodes['time']
    s.add_equation(sd.f_tabclip, wle, [WLE, t])

# These sources differs (not used):
# https://www.macrotrends.net/global-metrics/countries/wld/world/population
# https://www.macrotrends.net/global-metrics/countries/wld/world/life-expectancy

# Crude birth rate (cbr)
# Source: https://data.worldbank.org/indicator/SP.DYN.CBRT.IN
def load_wcbr(s):
    WCBR = s.addConstant(
        "WCBR", sd.CT, unit='births/1000persons',
        detail="Crude birth rate, empirical data",
        val=[
            (1960, 31.9085109649862),
            (1961, 31.1654969148589),
            (1962, 35.1033912209466),
            (1963, 36.2746633691201),
            (1964, 35.1318523303682),
            (1965, 34.474254891781),
            (1966, 33.4069298151443),
            (1967, 33.1250260541808),
            (1968, 33.2391071745528),
            (1969, 32.7475325973614),
            (1970, 32.4922789388489),
            (1971, 31.7598282096857),
            (1972, 31.2885032320425),
            (1973, 30.6548458176979),
            (1974, 29.794690839972),
            (1975, 29.1153685897741),
            (1976, 28.2910904364178),
            (1977, 27.8929264075199),
            (1978, 27.621339475579),
            (1979, 27.5352191155628),
            (1980, 27.5887392835125),
            (1981, 28.0709587856099),
            (1982, 28.2769096061473),
            (1983, 27.6794501610159),
            (1984, 27.4384818113339),
            (1985, 27.440721182186),
            (1986, 27.5563535943906),
            (1987, 27.4624715350153),
            (1988, 26.9838511544643),
            (1989, 26.4776012772285),
            (1990, 26.0528949569271),
            (1991, 25.4664953020972),
            (1992, 24.8158049297256),
            (1993, 24.4117955864629),
            (1994, 24.045987698374),
            (1995, 23.6237393558153),
            (1996, 23.3006595361917),
            (1997, 22.9448395226491),
            (1998, 22.5044467169184),
            (1999, 22.0712680392202),
            (2000, 21.8416353914892),
            (2001, 21.5512556291337),
            (2002, 21.2414003578483),
            (2003, 20.9576139772339),
            (2004, 20.7885169908253),
            (2005, 20.6113406718823),
            (2006, 20.4410517804909),
            (2007, 20.4044439719836),
            (2008, 20.3412855264212),
            (2009, 20.1634176306431),
            (2010, 20.0046574052708),
            (2011, 20.1192240850334),
            (2012, 20.2340866682727),
            (2013, 19.727987574404),
            (2014, 19.6427938996854),
            (2015, 19.1125702109189),
            (2016, 19.1734706466868),
            (2017, 18.699475058059),
            (2018, 18.1770198071608),
            (2019, 17.8167347974913),
            (2020, 17.2256004462707),
            (2021, 16.9420123366707),
            (2022, 16.6490741296197),
        ])
    wcbr = s.addFlow(
        "wcbr", unit='births/1000persons',
        detail="Crude birth rate, empirical data")
    t = s.nodes['time']
    s.add_equation(sd.f_tabclip, wcbr, [WCBR, t])

# Crude death rate (cdr)
# Source: https://data.worldbank.org/indicator/SP.DYN.CDRT.IN
def load_wcdr(s):
    WCDR = s.addConstant(
        "WCDR", sd.CT, unit='deaths/1000persons',
        detail="Crude death rate, empirical data",
        val=[
            (1960, 17.2341254913345),
            (1961, 14.5832939377514),
            (1962, 13.6164985188679),
            (1963, 13.4591291805959),
            (1964, 13.5292751103444),
            (1965, 13.3572905497885),
            (1966, 12.939855546048),
            (1967, 12.687222028332),
            (1968, 12.4406891339189),
            (1969, 12.2875124288142),
            (1970, 12.1398932582013),
            (1971, 12.2632382706644),
            (1972, 11.7617667758091),
            (1973, 11.4688810018691),
            (1974, 11.3835638184725),
            (1975, 11.3072020603216),
            (1976, 11.1505886217805),
            (1977, 10.7876626788349),
            (1978, 10.5490619576359),
            (1979, 10.3826790249015),
            (1980, 10.3501940568321),
            (1981, 10.1987307687688),
            (1982, 10.1171356335209),
            (1983, 10.1662407147209),
            (1984, 10.0433402470467),
            (1985, 9.92247452333324),
            (1986, 9.73374986177912),
            (1987, 9.56378996122941),
            (1988, 9.52903627428197),
            (1989, 9.30092178096296),
            (1990, 9.26137388174831),
            (1991, 9.22376020749671),
            (1992, 9.14001915096397),
            (1993, 9.14276225148319),
            (1994, 9.1059074763929),
            (1995, 8.98604292220804),
            (1996, 8.88698380395277),
            (1997, 8.75608576535661),
            (1998, 8.69811294269177),
            (1999, 8.58526127739029),
            (2000, 8.49352556933214),
            (2001, 8.41870553478693),
            (2002, 8.36193248953214),
            (2003, 8.29905313832744),
            (2004, 8.20286329453069),
            (2005, 8.15380474473476),
            (2006, 8.07392404630547),
            (2007, 8.03887650781162),
            (2008, 8.03564433598639),
            (2009, 7.91861709590891),
            (2010, 7.8752431317084),
            (2011, 7.78588320129082),
            (2012, 7.73200337229862),
            (2013, 7.65931992557108),
            (2014, 7.58187341863372),
            (2015, 7.57192209458954),
            (2016, 7.513983991006),
            (2017, 7.4965646643379),
            (2018, 7.48970644648313),
            (2019, 7.47219923843719),
            (2020, 8.03342483844351),
            (2021, 8.72793539272072),
            (2022, 8.37902007109049),
        ])
    wcdr = s.addFlow(
        "wcdr", unit='deaths/1000persons',
        detail="Crude death rate, empirical data")
    t = s.nodes['time']
    s.add_equation(sd.f_tabclip, wcdr, [WCDR, t])

# Human Ecological Footprint. Source
# https://data.footprintnetwork.org/#/countryTrends?cn=5001&type=BCtot,EFCtot
def load_whef(s):
    WHEF = s.addConstant(
        "WHEF", sd.CT, unit='gha',
        detail="Human Echological Footprint, empirical data",
        val=[
            (1961, 7217321032.502428),
            (1962, 7309418582.542245),
            (1963, 7341584434.898532),
            (1964, 7408940477.456671),
            (1965, 7546994525.450721),
            (1966, 8031501143.233746),
            (1967, 8604225404.411247),
            (1968, 8949426923.850641),
            (1969, 9232743117.478111),
            (1970, 10155663319.662876),
            (1971, 10395411366.771084),
            (1972, 10274157532.525644),
            (1973, 11136164680.238934),
            (1974, 11172033409.21793),
            (1975, 11273131280.518322),
            (1976, 11570888403.684881),
            (1977, 11717968760.070114),
            (1978, 12094054833.491297),
            (1979, 12480086435.859314),
            (1980, 11883409745.963528),
            (1981, 11834443187.86642),
            (1982, 11560652836.814514),
            (1983, 11445945496.15154),
            (1984, 12230107873.668663),
            (1985, 12653298063.759499),
            (1986, 12802062097.418282),
            (1987, 13066673300.780844),
            (1988, 13650217189.449493),
            (1989, 13956553929.76508),
            (1990, 13902521965.297968),
            (1991, 13680490551.035666),
            (1992, 13439369566.390871),
            (1993, 13549599796.624348),
            (1994, 14096093639.497658),
            (1995, 14438345449.253107),
            (1996, 14850440541.373367),
            (1997, 14819594011.639502),
            (1998, 14852275686.688234),
            (1999, 15506372904.377613),
            (2000, 16011850933.684244),
            (2001, 16342993121.819244),
            (2002, 15995861455.390448),
            (2003, 16371545031.625095),
            (2004, 17230567141.784863),
            (2005, 17595499782.768784),
            (2006, 17928199992.987175),
            (2007, 18612646094.448353),
            (2008, 18792502640.80563),
            (2009, 18181300455.24429),
            (2010, 19279164763.050888),
            (2011, 19789311463.75241),
            (2012, 19753859430.114788),
            (2013, 20156226250.56858),
            (2014, 20061433279.926586),
            (2015, 19862331341.06865),
            (2016, 19719782454.22692),
            (2017, 20346064690.476486),
            (2018, 20599120928.00859),
            (2019, 20491609066.0969),
            (2020, 19337586269.714252),
            (2021, 20496983850.30364),
            (2022, 20588847129.43614),
        ])
    whef = s.addFlow(
        "whef", unit='gha',
        detail="Human Echological Footprint, empirical data")
    t = s.nodes['time']
    s.add_equation(sd.f_tabclip, whef, [WHEF, t])

    # Absorption Land, empirical data.  This is derived from the
    # "Carbon" part of Human Ecological Footprint
    WALG = s.addConstant(
        "WALG", sd.CT, unit='f(t)',
        detail="Absorption Land, empirical data",
        val=[
            (1961, 3167347711.54622),
            (1962, 3168730734.51617),
            (1963, 3133624588.56726),
            (1964, 3118457745.70652),
            (1965, 3168064814.67562),
            (1966, 3514864994.53388),
            (1967, 3964021975.77819),
            (1968, 4184352067.57971),
            (1969, 4427413559.83046),
            (1970, 5258867638.02072),
            (1971, 5403634445.15474),
            (1972, 5288234009.75744),
            (1973, 5963889691.25657),
            (1974, 6013639255.8209),
            (1975, 6130109667.83915),
            (1976, 6266041373.30221),
            (1977, 6404004840.60151),
            (1978, 6589883667.26352),
            (1979, 6955646643.4798),
            (1980, 6369073973.13443),
            (1981, 6225355315.17887),
            (1982, 5828824262.54914),
            (1983, 5659235805.34398),
            (1984, 6212808666.83646),
            (1985, 6575738062.69326),
            (1986, 6632758061.02426),
            (1987, 6801086298.45038),
            (1988, 7397250630.28366),
            (1989, 7543848814.84678),
            (1990, 7348739762.83347),
            (1991, 7275556734.32967),
            (1992, 7003560139.41909),
            (1993, 7170431220.02825),
            (1994, 7630186426.85052),
            (1995, 7942806806.09973),
            (1996, 8203103882.86271),
            (1997, 8093064256.7704),
            (1998, 8072147364.82097),
            (1999, 8640065876.64487),
            (2000, 9091107381.1399),
            (2001, 9418887473.11718),
            (2002, 9045968662.90038),
            (2003, 9340769176.81319),
            (2004, 9945161630.09747),
            (2005, 10330681112.019),
            (2006, 10638317728.3805),
            (2007, 11267991003.55),
            (2008, 11390436216.69),
            (2009, 10859868667.0074),
            (2010, 11813083873.8598),
            (2011, 12176170652.3672),
            (2012, 12157723382.1442),
            (2013, 12334283889.7186),
            (2014, 12130681151.0712),
            (2015, 11952347955.298),
            (2016, 11711764745.7657),
            (2017, 12212639010.3249),
            (2018, 12419057860.6831),
            (2019, 12308693752.8125),
            (2020, 11215596012.8945),
            (2021, 12369950851.4207),
            (2022, 12456847839.2148),
        ])
    walg = s.addFlow(
        "walg", unit='gha',
        detail="Absorption Land, empirical data")
    t = s.nodes['time']
    s.add_equation(sd.f_tabclip, walg, [WALG, t])


if __name__ == "__main__":
    s = sd.System(init_time=1900, end_time=2100, time_step=1)
    load_wpop(s)
    load_wle(s)
    s.run()
    s.plot(('wpop', (0,10e9)), ('wle', (0,100)))
