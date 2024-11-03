# SPDX-License-Identifier: Unlicense
'''The intention is to keep the world3_model intact. That is, the
sematics of the code should not be altered. However, declarations are
altered, and "detail" and "unit" fields added.

This module contains functions the modify the world3_model once it's
loaded.
'''

import system_dynamic as sd
from le import modify_M, read_M

def remove_unit_constants(s):
    '''Remove the unit constants: OY, UAGI, UP, GDPU.
    
    I can't see the purpose of these. They all have val=1 and are used
    in f_tab_div() and other divisions
    '''
    le = s.nodes['le']
    m1 = s.nodes['m1']
    M1 = s.nodes['M1']
    s.add_equation(sd.f_tab, m1, [M1, le])
    m2 = s.nodes['m2']
    M2 = s.nodes['M2']
    s.add_equation(sd.f_tab, m2, [M2, le])
    m3 = s.nodes['m3']
    M3 = s.nodes['M3']
    s.add_equation(sd.f_tab, m3, [M3, le])
    m4 = s.nodes['m4']
    M4 = s.nodes['M4']
    s.add_equation(sd.f_tab, m4, [M4, le])
    FM = s.nodes['FM']
    fm = s.nodes['fm']
    s.add_equation(sd.f_tab, fm, [FM, le])
    CMPLE = s.nodes['CMPLE']
    cmple = s.nodes['cmple']
    ple = s.nodes['ple']
    s.add_equation(sd.f_tab, cmple, [CMPLE, ple])
    LEI = s.nodes['LEI']
    lei = s.nodes['lei']
    s.add_equation(sd.f_tab, lei, [LEI, le])
    def f_llmy(llmy2, llmy1, llmytm, t):
        return sd.f_clip(0.95 ** (t - llmytm) * llmy1 + (1 - 0.95 ** (t - llmytm)) * llmy2, llmy1, t, llmytm)
    llmy = s.nodes['llmy']
    llmy2 = s.nodes['llmy2']
    llmy1 = s.nodes['llmy1']
    LLMYTM = s.nodes['LLMYTM']
    t = s.nodes['time']
    s.add_equation(f_llmy, llmy, [llmy2, llmy1, LLMYTM, t])
    del(s.nodes['OY'])

    fpu = s.nodes['fpu']
    FPU = s.nodes['FPU']
    pop = s.nodes['pop']
    s.add_equation(sd.f_tab, fpu, [FPU, pop])
    del(s.nodes['UP'])

    jph = s.nodes['jph']
    JPH = s.nodes['JPH']
    aiph = s.nodes['aiph']
    s.add_equation(sd.f_tab, jph, [JPH, aiph])
    lymc = s.nodes['lymc']
    LYMC = s.nodes['LYMC']
    s.add_equation(sd.f_tab, lymc, [LYMC, aiph])
    mlymc = s.nodes['mlymc']
    MLYMC = s.nodes['MLYMC']
    s.add_equation(sd.f_tab, mlymc, [MLYMC, aiph])
    del(s.nodes['UAGI'])

# Adjust LE in population dynamic simulation
def adjust_le(s):
    # Remove the "bump" in simulated le (seem to be a bad idea)
    lmhs1 = s.nodes['lmhs1']
    lmhs = s.nodes['lmhs']
    #s.add_equation(sd.f_sum, lmhs, [lmhs1])
    # Adjust LE
    le = s.nodes['le']
    def f_ale(le):
        return le * 1.06
    ale = s.addFlow('ale', detail="Adjusted Life Expectancy")
    s.add_equation(f_ale, ale, [le])

    M1 = s.nodes['M1']
    M2 = s.nodes['M2']
    M3 = s.nodes['M3']
    M4 = s.nodes['M4']
    m1 = s.nodes['m1']
    m2 = s.nodes['m2']
    m3 = s.nodes['m3']
    m4 = s.nodes['m4']
    s.add_equation(sd.f_tab, m1, [M1, ale])
    s.add_equation(sd.f_tab, m2, [M2, ale])
    s.add_equation(sd.f_tab, m3, [M3, ale])
    s.add_equation(sd.f_tab, m4, [M4, ale])

