# -*- coding: utf-8 -*-
"""
This module defines both exponential and FIR based bunch by bunch damper 
feedback for tracking.
"""
import matplotlib.pyplot as plt
import numpy as np

from mbtrack2.tracking.element import Element
from mbtrack2.tracking.particles import Beam, Bunch


class TransverseExponentialDamper(Element):
    """ 
    Simple bunch by bunch damper feedback system based on exponential damping. 
    
    Parameters
    ----------
    ring : Synchrotron object
        Synchrotron to use.
    damping_time : float array of shape (2,)
        Damping time in [turn].
        If 0, the damper is not used in the considered plane.
    phase_diff : float array of shape (2,)
        Phase setting of the feedback in [deg]:
            - 90 corresponds to a pure resistive damper
            - 0 corresponds to a pure reactive damper.
    local_beta : float array of shape (2,), optional
        Beta function at the bpm/kicker location in [m].
        The default is ring.optics.local_beta.
        
    """

    def __init__(self, ring, damping_time, phase_diff, local_beta=None):
        self.ring = ring
        self.damping_time = np.array(damping_time)
        self.phase_diff = np.deg2rad(np.array(phase_diff))
        if local_beta:
            self.beta_bpm = local_beta
            self.beta_kicker = local_beta
        else:
            self.beta_bpm = ring.optics.local_beta
            self.beta_kicker = ring.optics.local_beta

    @Element.parallel
    def track(self, bunch):
        """
        Tracking method for the feedback system
        No bunch to bunch interaction, so written for Bunch object and
        @Element.parallel is used to handle Beam object.
        
        Parameters
        ----------
        bunch : Bunch or Beam object
        """
        if self.damping_time[0] != 0:
            mean_x = bunch['x'].mean()
            mean_xp = bunch['xp'].mean()
            bunch['xp'] -= (
                2 / self.damping_time[0] * np.sin(self.phase_diff[0]) *
                mean_xp) * np.sqrt(self.beta_bpm[0] / self.beta_kicker[0]) + (
                    2 / self.damping_time[0] * np.cos(self.phase_diff[0]) *
                    mean_x) / np.sqrt(self.beta_bpm[0] * self.beta_kicker[0])
        if self.damping_time[1] != 0:
            mean_y = bunch['y'].mean()
            mean_yp = bunch['yp'].mean()
            bunch['yp'] -= (
                2 / self.damping_time[1] * np.sin(self.phase_diff[1]) *
                mean_yp) * np.sqrt(self.beta_bpm[0] / self.beta_kicker[0]) + (
                    2 / self.damping_time[1] * np.cos(self.phase_diff[1]) *
                    mean_y) / np.sqrt(self.beta_bpm[0] * self.beta_kicker[0])


class FIRDamper(Element):
    """ 
    Bunch by bunch damper feedback system based on FIR filters.
    
    FIR computation is based on [1].
    
    Parameters
    ----------
    ring : Synchrotron object
        Synchrotron to use.
    plane : {"x","y","s"}
        Allow to choose on which plane the damper is active.
    tune : float
        Reference (betatron or synchrotron) tune for which the damper system 
        is set.
    turn_delay : int
        Number of turn delay before the kick is applied.
    tap_number : int
        Number of tap for the FIR filter.
    gain : float
        Gain of the FIR filter.
    phase : float
        Phase of the FIR filter in [degree].
    local_beta : float, optional
        Beta function at the bpm/kicker location in [m].
        The default is ring.optics.local_beta of the considered plane.
    bpm_error : float, optional
        RMS measurement error applied to the computed mean position.
        Unit is [m] if the plane is "x" or "y" and [s] if the plane is "s".
        The default is None.
    max_kick : float, optional
        Maximum kick strength limitation.
        Unit is [rad] if the plane is "x" or "y" and no unit (delta) if the 
        plane is "s".
        The default is None.

    Attributes
    ----------
    pos : array
        Stored beam postions.
    kick : array
        Stored damper kicks.
    coef : array
        Coefficients of the FIR filter.
         
    Methods
    -------
    get_fir(tap_number, tune, phase, turn_delay, gain)
        Initialize the FIR filter and return an array containing the FIR 
        coefficients.
    plot_fir()
        Plot the gain and the phase of the FIR filter.
    track(beam_or_bunch)
        Tracking method.
    get_damping_time()
        Return damping time in [turn].
    get_tune_shift()
        Return tune shit (in tune units).
      
    References
    ----------
    [1] T.Nakamura, S.Daté, K. Kobayashi, T. Ohshima. Proceedings of EPAC 
    2004. Transverse bunch by bunch feedback system for the Spring-8 
    storage ring.
    """

    def __init__(self,
                 ring,
                 plane,
                 turn_delay,
                 tune,
                 tap_number,
                 gain,
                 phase,
                 local_beta=None,
                 bpm_error=None,
                 max_kick=None):

        self.ring = ring
        self.tune = tune
        self.turn_delay = turn_delay
        self.tap_number = tap_number
        self.phase = -phase
        self.bpm_error = bpm_error
        self.max_kick = max_kick
        self.plane = plane
        if local_beta:
            self.beta_bpm = self.beta_kicker = local_beta
        else:
            self.beta_bpm = self.beta_kicker = ring.optics.local_beta[
                0] if plane == 'x' else ring.optics.local_beta[1]
        self.gain = gain
        self.action, self.damp_idx, self.mean_idx = self._set_plane_indices(
            plane)
        self.beam_no_mpi = False

        self.pos = np.zeros((self.tap_number, 1))
        self.kick = np.zeros((self.turn_delay + 1, 1))
        self.coef = self.get_fir(self.tap_number, self.tune, self.phase,
                                 self.turn_delay, self.gain)

    def _set_plane_indices(self, plane: str):
        if plane == "x":
            return "xp", 0, 0
        elif plane == "y":
            return "yp", 1, 2
        elif plane == "s":
            return "delta", 2, 4
        else:
            raise ValueError(f"Invalid plane: {plane}")

    def get_damping_time(self):
        """Return damping time in [turn]."""
        l = np.arange(0, self.tap_number)
        return 2 / np.sum(
            self.coef * np.sin(-2 * np.pi * (l + self.turn_delay) * self.tune))

    def get_tune_shift(self):
        """Return tune shit (in tune units)."""
        l = np.arange(0, self.tap_number)
        return 1 / (2 * np.pi) * 1 / 2 * np.sum(
            self.coef * np.cos(-2 * np.pi * (l + self.turn_delay) * self.tune))

    def get_fir(self, tap_number, tune, phase, turn_delay, gain):
        """
        Compute the FIR coefficients.
        
        FIR computation is based on [1].

        Parameters
        ----------
        tap_number : int
            Number of tap for the FIR filter.
        tune : float
            Reference (betatron or synchrotron) tune for which the damper system
            is set.         
        phase : float
            Phase of the FIR filter in [degree].        
        turn_delay : int
            Number of turn delay before the kick is applied.
        gain : float
            Gain of the FIR filter.
            
        Returns
        -------
        FIR_coef : array
            Array containing the FIR coefficients.
        """
        it = np.arange(-turn_delay, -turn_delay - tap_number, -1)
        zeta = np.deg2rad(phase)
        phi = 2 * np.pi * tune
        cs = np.cos(phi * it)
        sn = np.sin(phi * it)

        cc = np.vstack([np.ones(tap_number), cs, sn, it * sn, it * cs])
        W = np.linalg.inv(cc @ cc.T)
        D = W @ cc

        fir_coef = gain * (D[1] * np.cos(zeta) + D[2] * np.sin(zeta))
        return fir_coef

    def plot_fir(self, axs=None):
        """
        Plot the gain and the phase of the FIR filter.

        Parameters
        ----------
        axs : list of 2 axes.
            Axes for gain and phase plots.
        
        Returns
        -------
        axes : list of 2 axes.
            Axes for gain and phase plots.
            
        """
        tune = np.arange(0, 1, 0.0001)
        H_FIR = np.sum([
            coef * np.exp(-1j * 2 * np.pi * k * tune)
            for k, coef in enumerate(self.coef)
        ],
                       axis=0)
        latency = np.exp(-1j * 2 * np.pi * tune * self.turn_delay)
        H_tot = H_FIR * latency

        gain = np.abs(H_tot)
        phase = np.angle(H_tot, deg=True)

        if axs is None:
            _, [ax1, ax2] = plt.subplots(2, 1)
        else:
            ax1, ax2 = axs
        ax1.plot(tune, gain)
        ax1.set_ylabel("Gain")

        ax2.plot(tune, phase)
        ax2.set_xlabel("Tune")
        ax2.set_ylabel("Phase in degree")

        return [ax1, ax2]

    def track(self, beam_or_bunch):
        """
        Tracking method.

        Parameters
        ----------
        beam_or_bunch : Beam or Bunch
            Data to track.
            
        """
        if isinstance(beam_or_bunch, Bunch):
            self._track_sb(beam_or_bunch)
        elif isinstance(beam_or_bunch, Beam):
            beam = beam_or_bunch
            if (beam.mpi_switch == True):
                self._track_sb(beam[beam.mpi.bunch_num])
            else:
                if self.beam_no_mpi is False:
                    self._init_beam_no_mpi(beam)
                for i, bunch in enumerate(beam.not_empty):
                    self._track_sb(bunch, i)
        else:
            TypeError("beam_or_bunch must be a Beam or Bunch")

    def _init_beam_no_mpi(self, beam):
        """
        Change array sizes if Beam is used without mpi.

        Parameters
        ----------
        beam : Beam
            Beam to track.

        """
        n_bunch = len(beam)
        self.pos = np.zeros((self.tap_number, n_bunch))
        self.kick = np.zeros((self.turn_delay + 1, n_bunch))
        self.beam_no_mpi = True

    def _track_sb(self, bunch, bunch_number=0):
        """
        Core of the tracking method.

        Parameters
        ----------
        bunch : Bunch
            Bunch to track.
        bunch_number : int, optional
            Number of bunch in beam.not_empty. 
            The default is 0.
            
        """
        self.pos[0, bunch_number] = bunch.mean[self.mean_idx]
        if self.bpm_error is not None:
            self.pos[0, bunch_number] += np.random.normal(0, self.bpm_error)

        kick = 0
        for k in range(self.tap_number):
            kick += self.coef[k] * self.pos[k, bunch_number]

        if self.max_kick is not None:
            if kick > self.max_kick:
                kick = self.max_kick
            elif kick < -1 * self.max_kick:
                kick = -1 * self.max_kick

        self.kick[
            -1,
            bunch_number] = kick  # / np.sqrt(self.beta_bpm * self.beta_kicker)
        bunch[self.action] += self.kick[0, bunch_number]

        self.pos[:, bunch_number] = np.roll(self.pos[:, bunch_number], 1)
        self.kick[:, bunch_number] = np.roll(self.kick[:, bunch_number], -1)
