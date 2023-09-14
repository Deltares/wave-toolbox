import numpy as np
import matplotlib.pyplot as plt



import deltares_wave_toolbox.spectrum as spectrum

import deltares_wave_toolbox.cores.core_engine as engine_core
import deltares_wave_toolbox.cores.core_time as core_time
import deltares_wave_toolbox.cores.core_spectral as core_spectral



class WaveHeights():



    def __init__(self,hwave,twave):
        hwave,tSize =engine_core.convert_to_vector(hwave)
        twave,xSize =engine_core.convert_to_vector(twave)
        print('test')

      
        self.hwave = hwave
        self.twave = twave

    def __str__(self):
        return f"Series with {len(self.hwave)} elements"

    def __repr__(self):
        return f"{type(self).__name__} (series  nt = {self.nt})"

    def sort(self):
        """ Sorts the wave height and wave period.
        The sorting is done such that in hWaveSorted the wave heights of hWave
        are sorted in descending order. This same sorting is applied to 
        tWave.
        """
        self.hwave, self.twave = core_time.sort_wave_params(self.hwave,self.twave)

    def get_Hrms(self):
        Hrms = np.sqrt(np.mean( self.hwave**2 ))
        return Hrms
    
    def get_Hs(self):
        """ Compute Hs

        Returns:
            float: Hs
        """
        Hs = self.highest_waves(1/3)
        return Hs   
    
    def get_exceedance_waveheight(self, excPerc):
        """
        EXCEEDANCEWAVEHEIGHT  Computes wave height with given exceedance probability
        
        This function computes the wave height hExcPerc with given exceedance
        probability percentage excPerc. 

        Args:
            excPerc (float): exceedance probability percentage. excPerc = 2 means an  
                exceedance percentage of 2%. The value of excPerc should 
                not exceed 100, or be smaller than 0

        Returns:
            hExcPerc(float):  wave height with given exceedance probability
        """
        self.hwave,self.twave = core_time.sort_wave_params(self.hwave,self.twave)
        hExcPerc = core_time.exceedance_wave_height(hWaveSorted=self.hwave,excPerc=excPerc)
        return hExcPerc
    
    def highest_waves(self, fracP):
        """
        HIGHEST_WAVES_PARAMS  Computes wave parameters of selection largest waves

        This function computes the wave height hFracP and wave period tFracP by
        taking the average of the fraction fracP of the highest waves. When
        fracP = 1/3, then hFracP is equal to the significant wave height and
        tFracP is equal to the significant wave period. 
    
        Subject: time domain analysis of waves

        Args:
            fracP       : double 
                fraction. Should be between 0 and 1

        Returns:
            hFracP     : double
                    average of the wave heights of the highest fracP waves
            tFracP     : double 
                    average of the wave periods of the highest fracP waves
        """
        self.hwave,self.twave = core_time.sort_wave_params(self.hwave,self.twave)
        hFracP,tFracP = core_time.highest_waves_params(hWaveSorted=self.hwave,tWaveSorted=self.twave ,fracP=fracP)
        return hFracP,tFracP
    



class Series(WaveHeights):
    """ Series object

    Args:
        WaveHeights (_type_): _description_

    Returns:
        _type_: _description_
    """


    def __init__(self,time,x):
        time,tSize =engine_core.convert_to_vector(time)
        x,xSize =engine_core.convert_to_vector(x)

        assert tSize[0]==xSize[0], 'Input error: array sizes differ in dimension'
      
        self.time = time
        self.x = x
        self.nt = len(time)

        [hWave, tWave, aCrest, aTrough, tCrest, tTrough] = self._determine_individual_waves()
        super().__init__(hWave, tWave)


    def __str__(self):
        return f"Series with {self.nt} elements"

    def __repr__(self):
        return f"{type(self).__name__} (series  nt = {self.nt})"
    
    def get_crossing(self,typeCross='down'):
        """ Get zero crossings

        Args:
            typeCross (str, optional): type of crossing ('up' or 'down'). Defaults to 'down'.

        Returns:
            float and array: nWave with number of waves and tCross with the moments in time with a crossing
        """
        nWave,tCross = core_time.determine_zero_crossing(t=self.time,x=self.time,typeCross=typeCross)
        return nWave,tCross
    
    def get_spectrum(self,fres=0.01):
        """create spectrum

        Args:
            fres (float, optional): frequency resolution. Defaults to 0.01.

        Returns:
            Spectrum object: Spectrum
        """

        [f, S] = core_spectral.compute_spectrum_time_serie(self.time,self.x,fres)
        return spectrum.Spectrum(f, S)
    
    def get_fourier_comp(self):
        """ get Fourier components from series

        Returns:
            array: f, frequency array
            array: xFreq, fourrier components
            isOdd: logical
        """
        f,xFreq,isOdd = core_spectral.time2freq_nyquist(self.time, self.time)
        return f, xFreq, isOdd
    
    def _determine_individual_waves(self,typeCross='down'):
        """ dtermine individual waves in series

        Args:
            typeCross (str, optional): type of crossing (down or up). Defaults to 'down'.

        Returns
            tWave    : array double (1D)
                    1D array containing the periods of the individual waves
            hWave    : array double (1D)
                    1D array containing the wave heights of the individual waves
            aCrest   : array double (1D)
                    1D array containing the maximum amplitudes of the crest of
                    the individual waves
            aTrough  : array double (1D)
                    1D array containing the maximum amplitudes of the trough of
                    the individual waves
            tCrest   : array double (1D)
                    1D array containing the time at which maximum crest 
                    amplitude of the individual waves occurs
            tTrough  : array double (1D)
                    1D array containing the time at which maximum trough 
                    amplitude of the individual waves occurs
            Notes: 
                * All these arrays have a length equal to nWave, which is the number of
                waves in the wave train
                * The values of aTrough are always smaller than zero
                * hWave = aCrest - aTrough
        """
        nWave,tCross = core_time.determine_zero_crossing(t=self.time,x=self.x,typeCross=typeCross)
        hWave, tWave, aCrest, aTrough, tCrest, tTrough = core_time.determine_params_individual_waves(tCross=tCross,t=self.time,x=self.x)
        return hWave, tWave, aCrest, aTrough, tCrest, tTrough

    def plot(self,savepath=None,fig=None):
        """ Plot Series

        Args:
            savepath (str, optional): path to save figure. Defaults to None.
            fig (figure object, optional): figure object. Defaults to None.
        """

        if fig is None:
            fig = plt.figure()
        plt.plot(self.time,self.x)
        plt.grid('on')
        plt.xlabel('time [$s$]')
        plt.ylabel('z [$m$]')
        if savepath is not None:
            plt.savefig(savepath)


    
