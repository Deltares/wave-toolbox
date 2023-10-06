import sys
import os
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(1, os.getcwd())

from deltares_wave_toolbox.cores.core_wavefunctions import create_spectrum_jonswap
from deltares_wave_toolbox.cores.core_spectral import compute_spectrum_freq_serie

# create JONSWAP Spectrum ##
ff = np.linspace(0.01, 2, 1000)

spec = create_spectrum_jonswap(f=ff, fp=0.1, hm0=2)


Hm0 = spec.get_Hm0()
Tps = spec.get_Tps()
Tmm10 = spec.get_Tmm10()

spec.plot(xlim=[0, 0.5])

# create Series from spectrum ##
timeseries = spec.create_series(10, 3600, 0.1)

timeseries.plot(plot_crossing=True)


f, xFreq, isOdd = timeseries.get_fourier_comp()

plt.figure()
plt.plot(f, xFreq)

[ff, ss] = compute_spectrum_freq_serie(f, xFreq, 0.01, timeseries.nt)

plt.figure()
plt.plot(ff, ss)

var = timeseries.var()


h2perc = timeseries.get_exceedance_waveheight(2)
h10perc = timeseries.get_exceedance_waveheight(10)
Hs, Ts = timeseries.highest_waves(0.33333)
Hrms = timeseries.get_Hrms()

print("--- wave heights ---")
print("Hm0:", Hm0)
print("Hrms x sqrt(2):", Hrms * np.sqrt(2))
print("4 x sqrt(var):", 4 * np.sqrt(var))
print("Hs :", Hs)

timeseries.plot_hist_waveheight()
timeseries.plot_exceedance_waveheight()
timeseries.plot_exceedance_waveheight_Rayleigh()

print("--- wave exceedance ---")
print("h2perc:", h2perc)
print("h10perc:", h10perc)

spec2 = timeseries.get_spectrum(fres=0.01)

spec2.plot()

spec2.get_Hm0()
