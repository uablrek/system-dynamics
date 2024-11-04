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

# Recalibration23 from:
# https://onlinelibrary.wiley.com/doi/full/10.1111/jiec.13442
def recalibration23(s):
    ALIC1 = s.nodes['ALIC1']  # default 14??
    PPTD = s.nodes['PPTD']
    HSID = s.nodes['HSID']
    LPD = s.nodes['LPD']
    PPGF1 = s.nodes['PPGF1']
    LFPF = s.nodes['LFPF']
    ALLN = s.nodes['ALLN']
    PALT = s.nodes['PALT']
    NRI = s.nodes['NRI']
    IMTI = s.nodes['IMTI']
    IMEF = s.nodes['IMEF']
    PL = s.nodes['PL']
    FRPM = s.nodes['FRPM']
    SFPC = s.nodes['SFPC']
    #FAIPM is named FIPM
    FIPM = s.nodes['FIPM']
    SD = s.nodes['SD']
    MTFN = s.nodes['MTFN']
    AMTI = s.nodes['AMTI']
    SAD = s.nodes['SAD']
    FSPD = s.nodes['FSPD']
    UILDT = s.nodes['UILDT']

    ALIC1.val=15.24
    PPTD.val=116.38
    HSID.val=38.24
    LPD.val=33.84
    PPGF1.val=1.53
    LFPF.val=1.02
    ALLN.val=1351.20
    PALT.val=4.22e9
    NRI.val=1.3e12
    IMTI.val=11.06
    IMEF.val=0.11
    PL.val=0.10
    FRPM.val=0.02
    SFPC.val=233.69
    FIPM.val=0.001    # FAIPM
    SD.val=0.06
    MTFN.val=9.45
    AMTI.val=0.77
    SAD.val=13.38
    FSPD.val=0.61
    UILDT.val=0.53
    # re-initiate stocks that are already initiated!
    nr = s.nodes['nr']
    nr.hist[0] = nr.val = NRI.val
    ppol = s.nodes['ppol']
    ppol.hist[0] = ppol.val = PPGF1.val

# Test the faulty value used in Recalibration23. 2 when should be 14
def faulty_alic1(s):
    ALIC1 = s.nodes['ALIC1']
    ALIC1.val=2
