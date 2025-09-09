#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A post-processing module for DFT lattice dynamics by harmonic and quasiharmonic
approximations (HA/QHA).
"""
from CRYSTALClear.crystal_io import Crystal_output
from CRYSTALClear import units
#from CRYSTALpytools.crystal_io import Crystal_output
#from CRYSTALpytools import units


class Mode:
    """
    Defines a vibrational mode and do analysis per mode.

    Args:
        rank (int): The rank of the mode object, from 1.
        frequency (array[float] | list[float]): Frequencies of the mode
            (Ncalc\*1). Unit: THz. Note: **NOT** angular frequency, which is
            frequency * 2pi.
        volume (array[float] | list[float]): Lattice volumes of harmonic
            calculations (Ncalc\*1). Unit: Angstrom^3
        eigenvector (array[float] | list[float]): Corresponding normalized
            eigenvectors (Ncalc\*Natom\*3).

    Returns:
        self.rank (int)
        self.ncalc (int): The number of harmonic calculations (typically at
            different volumes)
        self.frequency (array[float])
        self.volume (array[float])
        self.eigenvector (array[float])
    """

    def __init__(self, rank=0, frequency=[], volume=[], eigenvector=[]):
        import numpy as np

        self.rank = rank
        self.ncalc = len(frequency)
        self.frequency = np.array(frequency, dtype=float)
        self.volume = np.array(volume, dtype=float)
        self.eigenvector = np.array(eigenvector, dtype=complex)

    def get_zp_energy(self):
        """
        Get the zero-point energy of a single mode. *ncalc = 1 only*.

        .. math::

            E^{zp}_{i,\\mathbf{q}}=\\frac{1}{2}\\hbar\\omega_{i,\\mathbf{q}}

        Returns:
            self.zp_energy (float): Zero-point energy. Unit: KJ/mol
        """
        import numpy as np
        import scipy.constants as scst

        if self.ncalc > 1:
            raise AttributeError(
                'This module is limited to a single frequency calculation.')

        hbar_freq = self.frequency[0] * scst.Avogadro * scst.h * 1e9
        self.zp_energy = 0.5 * hbar_freq

        return self.zp_energy

    def get_u_vib(self, temperature=298.15):
        """
        Get the vibration contribution to internal energy (including zero-point
        energy) of a single mode. *ncalc = 1 only*.

        .. math::

            U^{vib}_{i,\\mathbf{q}}\\left(T\\right)=E^{zp}_{i,\\mathbf{q}}+
            \\frac{\\hbar\\omega_{i,\\mathbf{q}}}{\\exp{\\left(
                \\frac{\\hbar\\omega_{i,\\mathbf{q}}}{k_{B}T}
            \\right)}-1}

        Args:
            temperature (float, optional): Temperature where the quantity is
                computed. Unit: K

        Returns:
            self.u_vib (float): Vibration contribution to internal energy.
                Unit: KJ/mol
        """
        import numpy as np
        import scipy.constants as scst

        if self.ncalc > 1:
            raise AttributeError(
                'This module is limited to a single frequency calculation.')

        if not hasattr(self, 'zp_energy'):
            self.get_zp_energy()

        if temperature == 0 or self.frequency[0] < 1e-4:
            self.u_vib = self.zp_energy
            return self.u_vib

        hbar_freq = self.frequency[0] * scst.Avogadro * scst.h * 1e9
        kb_t = scst.k * scst.Avogadro * temperature * 1e-3
        expon = np.exp(hbar_freq / kb_t)
        self.u_vib = self.zp_energy + hbar_freq / (expon - 1)

        return self.u_vib

    def get_entropy(self, temperature):
        """
        Get the entropy of a single mode. *ncalc = 1 only*.

        .. math::

            S_{i,\\mathbf{q}}\\left(T\\right)=k_{B}\\left\\{
                \\frac{\\hbar\\omega_{i,\\mathbf{q}}}{k_{B}T\\left[
                    \\exp{\\left(
                        \\frac{\\hbar\\omega_{i,\\mathbf{q}}}{k_{B}T}
                    \\right)}-1
                \\right]}-\\ln{\\left[
                    1-\\exp{\\left(
                        -\\frac{\\hbar\\omega_{i,\\mathbf{q}}}{k_{B}T}
                    \\right)}
                \\right]}
            \\right\\}

        Args:
            temperature (float, optional): Unit: K

        Returns:
            self.entropy (float): Entropy. Unit: J/mol\*K
        """
        import numpy as np
        import scipy.constants as scst

        if self.ncalc > 1:
            raise AttributeError(
                'This module is limited to a single frequency calculation.')

        if temperature == 0 or self.frequency[0] < 1e-4:
            self.entropy = 0
            return self.entropy

        hbar_freq = self.frequency[0] * scst.Avogadro * scst.h * 1e12
        kb_t = scst.k * scst.Avogadro * temperature
        expon = np.exp(hbar_freq / kb_t)
        entS = kb_t * (hbar_freq / kb_t / (expon - 1) - np.log(1 - 1 / expon))
        self.entropy = entS / temperature

        return self.entropy

    def get_c_v(self, temperature):
        """
        Get the constant volume specific heat of a single mode. *ncalc = 1 only*.

        .. math::

            C^{V}_{i,\\mathbf{q}}=
            \\frac{\\left(\\hbar\\omega_{i,\\mathbf{q}}\\right)^{2}}{k_{B}T^{2}}
            \\frac{\\exp{
            \\left(
                \\frac{\\hbar\\omega_{i,\\mathbf{q}}}{k_{B}T}
            \\right)}
            }{\\left[
                \\exp{\\left(
                    \\frac{\\hbar\\omega_{i,\\mathbf{q}}}{k_{B}T}
                \\right)-1}
            \\right]^{2}
            }

        Args:
            temperature (float, optional): Unit: K

        Returns:
            self.c_v (float): Constant volume specific heat. Unit: J/mol\*K
        """
        import numpy as np
        import scipy.constants as scst

        if self.ncalc > 1:
            raise AttributeError(
                'This module is limited to a single frequency calculation.')

        if temperature == 0 or self.frequency[0] < 1e-4:
            self.c_v = 0
            return self.c_v

        hbar_freq = self.frequency[0] * scst.Avogadro * scst.h * 1e12
        kb_t = scst.k * scst.Avogadro * temperature
        expon = np.exp(hbar_freq / kb_t)

        self.c_v = hbar_freq**2 / kb_t / temperature * expon / (expon - 1)**2

        return self.c_v

    def get_classical_amplitude(self, struc):
        """
        Empty method - development ongoing
        """

    def polynomial_fit(self, order=[2, 3]):
        """
        Fit phonon frequency as the polynomial function of volume. *ncalc > 1 only*.

        .. note::

            To improve the accuracy of fittings, :math:`\\Delta\\omega(\\Delta V)`
            is fitted as a polynomial function without the constant term.

            :math:`\\Delta V=V-V_{min}` is used so HA phonons of the most compact
            structure is kept. See 'FIXINDEX' keyword in CRYSTAL manual for
            further information.

        Args:
            order (array[int] | list[int]], optional): Orders of polynomials.

        Returns:
            self.poly_fit (Dict[int, NumPy Polynomial]): Key - orders of power,
                Value - fitted NumPy polynomials
            self.poly_fit_rsquare (Dict[int, float]): Key - orders of power,
                Value - goodness of fittings, characterized by R^2.
        """
        import numpy as np
        import warnings
        from scipy.optimize import least_squares
        from thermodynamics import Quasi_harmonic
        #from CRYSTALpytools.thermodynamics import Quasi_harmonic

        if self.ncalc <= 1:
            raise AttributeError(
                'This modulus is limited to multiple frequency calculations.')

        if max(order) > self.ncalc - 1:
            warnings.warn(
                'Reference data not sufficient for the order of polynomial fitting.')
            warnings.warn('Too high values will be removed.')

        order = list(set(order))
        order = [p for p in order if p <= self.ncalc - 1]

        self.poly_fit = {}
        self.poly_fit_rsqaure = {}

        if self.rank == 1 or self.rank == 2 or self.rank == 3:
            for i in order:
                self.poly_fit[i] = np.polynomial.polynomial.Polynomial(
                    [0. for i in range(i + 1)])
                self.poly_fit_rsqaure[i] = 1.

            return order, self.poly_fit, self.poly_fit_rsqaure

        qha = Quasi_harmonic(filename=None)
        idx_vmin = np.argmin(self.volume)
        vmin = self.volume[idx_vmin]
        fmin = self.frequency[idx_vmin]
        dv = self.volume - vmin
        df = self.frequency - fmin
        for i in order:
            opt = least_squares(qha._poly_no_cst,
                                np.array([1. for j in range(i)]),
                                args=(dv, df))
            poly = np.polynomial.polynomial.Polynomial(np.insert(opt.x, 0, 0.))
            self.poly_fit[i] = poly
            self.poly_fit_rsqaure[i] = 1 - np.sum((df - poly(dv))**2) / np.sum((df - np.mean(df))**2)

        return order, self.poly_fit, self.poly_fit_rsqaure

    def get_gruneisen(self, order, volume):
        """
        Return to mode Grüneisen parameter. *ncalc > 1 only*.

        .. math::

            \\gamma = -\\frac{V}{\\omega(V)}\\frac{\\partial\\omega}{\\partial V}

        Args:
            order (int | list[int]): See ``polynomial_fit``
            volume (float | array): Typically the equilibrium volume

        Returns:
            self.gruneisen (dict): Key, order; Value, Gruneisen parameter
        """
        import numpy as np

        if not hasattr(self, 'poly_fit'):
            raise AttributeError(
                'Polynomial fitting is required to get Gruneisen parameters.')

        order = list(set(order))
        self.gruneisen = {}
        if type(volume) == float:
            volume = np.array([volume])
        else:
            volume = np.array(volume)

        if self.rank == 1 or self.rank == 2 or self.rank == 3:
            for i in order:
                self.gruneisen[i] = np.zeros(volume.shape)
            return self.gruneisen

        idx_vmin = np.argmin(self.volume)
        vmin = self.volume[idx_vmin]
        fmin = self.frequency[idx_vmin]
        dv = volume - vmin
        for i in order:
            dpoly = self.poly_fit[i].deriv(1)
            self.gruneisen[i] = -dpoly(dv) * volume / (self.poly_fit[i](dv) + fmin)

        return self.gruneisen


class Harmonic():
    """
    A class for harmonic phonon calclulations. It can be parameterized from a
    CRYSTAL output file, phonopy ouput file or by setting all the information
    (usually for QHA).

    Args:
        temperature (array[float] | list[float], optional): Temperatures
            where thermodynamic properties are computed. Unit: K
        pressure (array[float] | list[float], optional): Pressures where
            the thermodyanmic properties are calculated. Unit: GPa
        filename (str | None): Name of the printed-out file. If None, do not
            print out file.
        autocalc (bool): Automatically launch calculations.

    Temperatures and pressures can also be defined by ``self.thermodynamics``,
    whose entries always cover the entries here.

    Phonon dispersions are forced to be summed if the automatic scheme
    (``autocalc=True``) is launched. To get verbose outputs, call
    ``self.thermodynamics()`` first and then call ``self.print_results()``.

    Usage::

        ha = Harmonic(temperature=[0, 100, 200, 300], pressure=[0.,])
        ha.from_file('harmonic_phonon.out')
    """

    def __init__(self, temperature=[], pressure=[], filename=None, autocalc=True):
        import numpy as np

        if len(temperature) > 0:
            self.temperature = np.array(temperature, dtype=float)

        if len(pressure) > 0:
            self.pressure = np.array(pressure, dtype=float)

        self.autocalc = autocalc
        self.filename = filename

    def from_file(self, output_name, scelphono=[], read_eigvt=False,
                  imaginary_tol=-1e-4, q_overlap_tol=1e-4):
        """
        Generate the Harominc object from a HA output file. Imaginary modes and
        overlapped q points are forced to be cleaned.

        Args:
            output_name (str): Name of the output file.
            scellphono (array[float] | list[float], optional):
                The 'SCELPHONO' keyword in CRYSTAL input file. By default a
                1\*1\*1 'SCELPHONO' is assumed.
            read_eigvt (bool): Whether to read eigenvectors from output.
            imaginary_tol (float): The threshold of negative frequencies.
            q_overlap_tol (float): The threshold of overlapping points, defined
                as the 2nd norm of the difference of fractional q vectors

        Returns:
            self.structure (PyMatGen Structure): Cell reduced by SCELPHONO.
            self.natom (int): Number of atoms in the reduced cell.
            self.volume (float): Volume of the reduced cell. Unit: Angstrom^3
            self.edft (float)
            self.nqpoint (int)
            self.qpoint (list)
            self.nmode (array[int])
            self.mode (list[Mode]): List of mode objects at all the qpoints.

        :raise ValueError: If a QHA output file is read.
        """
        import numpy as np
        from crystal_io import Crystal_output
        #from CRYSTALpytools.crystal_io import Crystal_output
        from thermodynamics import Mode
        #from CRYSTALpytools.thermodynamics import Mode
        import warnings

        if hasattr(self, "volume"):
            warnings.warn("Data exists. Cannot overwrite the existing data.")
            return self

        output = Crystal_output(output_name)
        output.get_phonon(read_eigvt=read_eigvt, rm_imaginary=False, rm_overlap=False)
        strucs = _restore_pcel(output, scelphono)

        if len(strucs) != 1: # strucs and edft must have only 1 valid entry
            raise ValueError("Only the frequency calculations at constant volumes are premitted.")

        # Transfer the modes in self.freqency into lists of mode objects
        self.from_frequency(output.edft[0], output.qpoint, output.frequency,
                            output.eigenvector, structure=strucs[0],
                            imaginary_tol=imaginary_tol, q_overlap_tol=q_overlap_tol)
        # Autocalc
        if self.autocalc == True:
            self.thermodynamics(sumphonon=True)

        return self

    def from_phonopy(self, phono_yaml, struc_yaml=None, edft=None, scale=1.0,
                     imaginary_tol=-1e-4, q_overlap_tol=1e-4, q_id=None, q_coord=None):
        """
        Build a Harmonic object from `Phonopy <https://phonopy.github.io/phonopy/>`_
        'band.yaml' or 'qpoints.yaml' file.

        Args:
            phono_yaml (str): Phonopy band.yaml or qpoint.yaml file
            struc_yaml (str): Phonopy phonopy.yaml or phonopy_disp.yaml file.
                *Needed only if a qpoint.yaml file is read.*
            edft (float): DFT energy. Unit: kJ/mol
            scale (float): Scaling factor of phonon frequency.
            imaginary_tol (float): The threshold of negative frequencies.
            q_overlap_tol (float): The threshold of overlapping points, defined
                as the 2nd norm of the difference of fractional q vectors
            q_id (list[int]): Specify the id (from 0) of q points to be read.
                nqpoint\*1 list.
            q_coord (list[list]): Specify the coordinates of q points to be
                read. nqpoint\*3 list.

        ``q_id`` and ``q_coord`` should not be set simultaneously. If set,
        ``q_id`` takes priority and ``q_coord`` is ignored. If both are none,
        all the points will be read.

        :raise Exception: If the length unit in yaml file is neither 'au' nor 'angstrom'.
        :raise Exception: If q point is not found.
        """
        from thermodynamics import Phonopy
        #from CRYSTALpytools.thermodynamics import Phonopy
        import warnings

        if hasattr(self, "volume"):
            warnings.warn("Data exists. Cannot overwrite the existing data.")
            return self
        if edft == None:
            edft = 0.
            warnings.warn('DFT energy is set to 0.')

        # Get geometry
        if struc_yaml != None:
            structure = Phonopy.read_structure(struc_yaml)
        else:
            structure = Phonopy.read_structure(phono_yaml)

        qpoint, frequency = Phonopy.read_frequency(phono_yaml, q_id=q_id, q_coord=q_coord)

        # set object
        self.from_frequency(edft=edft, qpoint=qpoint, frequency=frequency*scale,
                            eigenvector=[], structure=structure,
                            imaginary_tol=imaginary_tol, q_overlap_tol=q_overlap_tol)
        # Autocalc
        if self.autocalc == True:
            self.thermodynamics(sumphonon=True)

        return self

    def from_frequency(self, edft, qpoint, frequency, eigenvector,
                       structure=None, natom=None, volume=None,
                       imaginary_tol=-1e-4, q_overlap_tol=1e-4, ignore_natom=False):
        """
        Generate a Harmonic object by specifying frequency and eigenvector.
        Imaginary modes and overlapped q points are forced to be cleaned.

        Args:
            edft (float): Electron total energy
            qpoint (list[list[array[float], float]]): Fractional coordinate
                and weight of qpoint
            frequency (array[float]): Array of frequencies. Unit: THz
            eigenvector (array[float]): Normalized eigenvectors.
            structure (Pymatgen Structure)
            natom (int)
            volume (float)
            imaginary_tol (float): The threshold of negative frequencies.
            q_overlap_tol (float): The threshold of overlapping points, defined
                as the 2nd norm of the difference of fractional q vectors
            ignore_natom (bool): Developer only.

        .. note::

            The user should define either ``structure`` or ``natom`` + ``volume``.

        Returns:
            self.structure (PyMatGen Structure): Cell reduced by SCELPHONO.
            self.natom (int): Number of atoms in the reduced cell.
            self.volume (float): Volume of the reduced cell. Unit: Angstrom^3
            self.edft (float)
            self.nqpoint (int)
            self.qpoint (list)
            self.nmode (array[int])
            self.mode (list[Mode]): List of mode objects at all the qpoints.

        :raise AttributeError: If computational data is stored in the object.
        :raise ValueError: If neither of the 2 available options are defined.
        """
        from base.crysout import PhononBASE
        #from CRYSTALpytools.base.crysout import PhononBASE
        from thermodynamics import Mode
        #from CRYSTALpytools.thermodynamics import Mode
        import numpy as np

        if hasattr(self, "mode"):
            raise AttributeError("Data exists. The current command will be ignored.")

        if structure != None:
            self.structure = structure
            self.natom = len(structure.species)
            self.volume = structure.lattice.volume
        elif natom != None and volume != None:
            self.natom = int(natom)
            self.volume = float(volume)
        else:
            if ignore_natom == False:
                raise ValueError('Geometry is not sufficiently defined. Structure or volume + natom are needed.')
            else:
                self.volume = float(volume)

        if len(qpoint) != np.size(frequency, 0):
            raise ValueError("The 1st dimension (n qpoint) of 'qpoint' and 'frequency' are not consistent.")
        if len(eigenvector) != 0 and np.size(eigenvector, 1) != np.size(frequency, 1):
            raise ValueError("The 2nd dimension (n mode) of 'frequency' and 'eigenvector' are not consistent.")

        self.edft = edft
        self.nqpoint = len(qpoint)
        self.qpoint = qpoint
        self.nmode = np.array([len(q) for q in frequency])
        self.frequency = frequency
        self.intens = []
        self.IR = []
        self.Raman = []
        self.eigenvector = eigenvector
        ## Note: Harmonic object is not a crystal_output project, but has the
        ## same attributes
        self = PhononBASE.clean_imaginary(self, threshold=imaginary_tol)
        self = PhononBASE.clean_q_overlap(self, threshold=q_overlap_tol)

        # Transfer the modes in self.freqency into lists of mode objects
        self.mode = []
        for q, freq_q in enumerate(self.frequency):
            qmode = []
            for m, freq_m in enumerate(freq_q):
                if len(self.eigenvector) != 0:
                    qmode.append(Mode(rank=m + 1,
                                      frequency=[freq_m],
                                      volume=[self.volume],
                                      eigenvector=[self.eigenvector[q, m]]))
                else:
                    qmode.append(Mode(rank=m + 1,
                                      frequency=[freq_m],
                                      volume=[self.volume]))

            self.mode.append(qmode)

        # Delete useless attribute
        delattr(self, 'intens')
        delattr(self, 'IR')
        delattr(self, 'Raman')

        return self

    def _phonon_sumup(self, temperature, calculate_zp):
        """
        Summing up inidival phonon modes at each q point. Translational modes
        with frequencies = 0 are skipped. For thermodynamics, directly call
        ``self.thermodyanmics()``.

        Args:
            temperature (float)
            calculate_zp (bool): Calculate zero-point energy or temperature
                dependent properties.

        Returns:
            zp_energy (array[float]): Zero-point energy at a q point. Returned
                if ``calculate_zp = True``.
            u_vib (array[float]): Vibrational contribution to internal energy 
                at constant temperature and a q point. Returned if 
                ``calculate_zp = False``.
            entropy (array[float]): Entropy at constant temperature and a q 
                point. Returned if ``calculate_zp = False``.
            c_v (array[float]): Constant volume specific heat at constant
                 temperature and a q point. Returned if ``calculate_zp = False``.
        """
        import numpy as np

        if calculate_zp:
            zp_energy = []
        else:
            T = temperature
            u_vib = []
            entropy = []
            c_v = []

        for qpoint in self.mode:
            if calculate_zp:
                zp_energy_q = 0.
            else:
                u_vib_q = 0.
                entropy_q = 0.
                c_v_q = 0.
            # Remove the translational modes
            for mode in qpoint:
                if np.isnan(mode.frequency) or mode.frequency <= 1e-5:
                    continue

                if calculate_zp:
                    zp_energy_q += mode.get_zp_energy()
                else:
                    u_vib_q += mode.get_u_vib(temperature=T)
                    entropy_q += mode.get_entropy(temperature=T)
                    c_v_q += mode.get_c_v(temperature=T)

            if calculate_zp:
                zp_energy.append(zp_energy_q)
            else:
                u_vib.append(u_vib_q)
                entropy.append(entropy_q)
                c_v.append(c_v_q)

        if calculate_zp:
            zp_energy = np.array(zp_energy, dtype=float)
            return zp_energy
        else:
            u_vib = np.array(u_vib, dtype=float)
            entropy = np.array(entropy, dtype=float)
            c_v = np.array(c_v, dtype=float)
            return u_vib, entropy, c_v

    def thermodynamics(self, sumphonon=True, mutewarning=False, **kwargs):
        """
        Calculate the thermodynamic properties (zp_energy, u_vib, entropy, c_v
        and Gibbs and Helmholtz free energy) of the HA system at all qpoints
        and the whole temperature/pressure range.

        Other parameters are the sum of corresponding attributes of all the
        ``Mode objects``. The Helmholtz and Gibbs free energies are defined as:

        .. math::

            F(p,V) = E_{DFT} + F_{vib}(T) = E_{DFT} + U_{vib}(T) - TS(T)

            G(p, V) = F + pV

        Args:
            temperature (array[float] | list[float], optional): Unit: K
            pressure (array[float] | list[float], optional): Unit: GPa
            sumphonon (bool): Whether to sum up the phonon contributions across
                the sampled q points and take weighted-average.
            mutewarning (bool): Whether print out warning messages of updated
                temperature and pressure (For QHA).

        Returns:
            self.helmholtz (array[float]): nqpoint\*ntemperature. Unit: KJ/mol
            self.gibbs (array[float]): nqpoint\*nPressure\*nTemperature. Unit: KJ/mol
            self.zp_energy (array[float]): Zero-point energy. nqpoint\*1. Unit: KJ/mol
            self.u_vib (array[float]): Vibrational contribution to internal
                energy. nqpoint\*ntemperature. Unit: KJ/mol
            self.entropy (array[float]): nqpoint\*ntemperature. Unit: J/mol\*K
            self.c_v (array[float]): Constant volume specific heat. 
                nqpoint\*ntemperature. Unit: J/mol\*K

        .. note::

            If ``sumphonon = True``, nqpoint = 1.

        :raise AttributeError: If temperature and pressure are defined neither here nor during initialization
        """
        import warnings
        import numpy as np
        import scipy.constants as scst

        # Generate temperature and pressure series
        if kwargs:
            if 'temperature' in kwargs:
                if hasattr(self, 'temperature') and not mutewarning:
                    warnings.warn('Temperature attribute exists. Input temperatures will be used to update the attribute.')
                self.temperature = np.array(kwargs['temperature'], dtype=float)

            if 'pressure' in kwargs:
                if hasattr(self, 'pressure') and not mutewarning:
                    warnings.warn('Pressure attribute exists. Input pressures will be used to update the attribute.')
                self.pressure = np.array(kwargs['pressure'], dtype=float)
        else:
            if not hasattr(self, 'temperature') or not hasattr(self, 'pressure'):
                raise AttributeError('Temperature and pressure should be specified.')

        zp_energy = self._phonon_sumup(temperature=0., calculate_zp=True)
        u_vib = []
        entropy = []
        c_v = []
        helmholtz = []
        gibbs = []

        for T in self.temperature:
            gibbs_t = []
            u_vib_t, entropy_t, c_v_t = self._phonon_sumup(temperature=T,
                                                           calculate_zp=False)
            helm_t = -entropy_t * T * 1e-3 + u_vib_t + self.edft

            for p in self.pressure:
                gibbs_tp = p * self.volume * scst.Avogadro * 1e-24 + helm_t
                gibbs_t.append(gibbs_tp)

            # nTemp * nqpoint
            u_vib.append(u_vib_t)
            entropy.append(entropy_t)
            c_v.append(c_v_t)
            helmholtz.append(helm_t)
            # nTemp * npress * nqpoint
            gibbs.append(gibbs_t)

        if sumphonon:
            wt = np.array([qp[1] for qp in self.qpoint])
            self.nqpoint = 1
            self.qpoint = [[np.array([0., 0., 0.]), 1.]]
            self.zp_energy = np.array([np.dot(zp_energy, wt)])
            self.u_vib = np.array([np.dot(u_vib, wt)])
            self.entropy = np.array([np.dot(entropy, wt)])
            self.c_v = np.array([np.dot(c_v, wt)])
            self.helmholtz = np.array([np.dot(helmholtz, wt)])
            self.gibbs = np.array([np.dot(gibbs, wt)])
            self.gibbs = np.transpose(self.gibbs, (0, 2, 1))
        else:
            self.zp_energy = zp_energy
            self.u_vib = np.transpose(np.array(u_vib, dtype=float))
            self.entropy = np.transpose(np.array(entropy, dtype=float))
            self.c_v = np.transpose(np.array(c_v, dtype=float))
            self.helmholtz = np.transpose(np.array(helmholtz, dtype=float))
            self.gibbs = np.transpose(np.array(gibbs, dtype=float), (2, 1, 0))

        if self.filename != None:
            self.write_HA_result()

        return self

    def write_HA_result(self):
        from thermodynamics import Output
        #from CRYSTALpytools.thermodynamics import Output
        import warnings

        if self.filename == None:
            warnings.warn('Output file not specified. Return.')
            return

        Output.write_HA_result(self)
        return


class Quasi_harmonic:
    """
    Generate and rearrange harmonic phonons, store the fitted, volume-dependent
    QHA phonon information and obtain the QHA thermodynamic properties.

    Args:
        temperature (array[float] | list[float], optional): Unit: K
        pressure (array[float] | list[float], optional): Unit: GPa
        write_out (bool): Whether to print the key information into a file.
        filename (str): Name of the output file. Valid if ``write_out = True``.

    Temperatures and pressures can also be defined by ``self.thermodynamics``,
    whose entries always cover the entries here.

    Usage::

        qha = Quasi_harmonic()
        qha.from_QHA_file('qha_phonon.out')
        qha.thermo_freq(eos_method='birch_murnaghan', temperature=[0, 100, 200, 300], pressure=[0., 0.5, 1.]):
    """

    def __init__(self, temperature=[], pressure=[], filename=None):
        import numpy as np

        if len(temperature) > 0:
            self.temperature = np.array(temperature, dtype=float)

        if len(pressure) > 0:
            self.pressure = np.array(pressure, dtype=float)

        self.filename = filename

    def from_HA_files(self, input_files, scelphono=[], imaginary_tol=-1e-4,
                      q_overlap_tol=1e-4, mode_sort_tol=0.4):
        """
        Read data from individual HA calculation outputs. Imaginary modes and
        overlapped q points are forced to be cleaned.

        Args:
            input_files (list[str]): List of phonon output filenames.
            scelphono (array[float] | list[float]): Corresponds to the
                'SCELPHONO' keyword in CRYSTAL. Either 3\*3 or ndimension\*ndimension.
                By default a 1\*1\*1 'SCELPHONO' is assumed.
            imaginary_tol (float): The threshold of negative frequencies.
            q_overlap_tol (float): The threshold of overlapping points, defined
                as the 2nd norm of the difference of fractional q vectors
            mode_sort_tol (float | None): The threshold of close mode
                overlaps. If none, do not sort modes.

        Returns:
            self (Quasi_harmonic): New Attributes listed below
            self.ncalc (int): Number of HA phonon calculations.
            self.combined_phonon (list[Harmonic]): List of Harmonic objects.
            self.combined_volume (list[float]): Volumes. Unit: Angstrom^3
            self.combined_edft (list[float]): DFT total energies. Unit: KJ/mol
            self.combined_mode (list[Mode]): List of mode objects.
        """
        from thermodynamics import Harmonic
        #from CRYSTALpytools.thermodynamics import Harmonic
        import warnings

        if hasattr(self, "ncalc"):
            warnings.warn('Data exists. The current command will be ignored.')
            return self

        if len(input_files) == 1:
            raise Exception('Only 1 input file! Use Harmonic object or from_QHA_file method.')
        else:
            self.ncalc = len(input_files)

        if mode_sort_tol != None:
            read_eigvt = True
        else:
            read_eigvt = False

        ha_list = [
            Harmonic(filename=None, autocalc=False).from_file(
                file,
                scelphono=scelphono,
                read_eigvt=read_eigvt,
                imaginary_tol=imaginary_tol,
                q_overlap_tol=q_overlap_tol
            ) for file in input_files
        ]

        self.combined_phonon, self.combined_volume, self.combined_edft, \
        self.combined_mode, close_overlap = self._combine_data(ha_list, mode_sort_tol=mode_sort_tol)
        self.nqpoint = ha_list[0].nqpoint
        self.qpoint = ha_list[0].qpoint # consistency of nqpoint is checked, but not qpoint.

        if ha_list[0].eigenvector == []:
            do_eigvt = False
        else:
            do_eigvt = True
        if self.filename != None:
            Output.write_QHA_combinedata(self)

            if mode_sort_tol != None and do_eigvt == True:
                Output.write_QHA_sortphonon(self, close_overlap)

        return self

    def from_QHA_file(self, input_file, scelphono=[], imaginary_tol=-1e-4,
                      q_overlap_tol=1e-4, mode_sort_tol=0.4):
        """
        Read data from a single QHA calculation at Gamma point. Imaginary modes
        and overlapped q points are forced to be cleaned.

        Args:
            input_files (str | list[str]): Only 1 QHA file is permitted.
            scelphono (array[float] | list[float])
            imaginary_tol (float): The threshold of negative frequencies.
            q_overlap_tol (float): The threshold of overlapping points, defined
                as the 2nd norm of the difference of fractional q vectors
            mode_sort_tol (float | None): The threshold of close mode
                overlaps. If none, do not sort modes.

        Returned attributes are consistent with ``Quasi_harmonic.from_HA_files``.

        :raise ValueError: If multiple files are defined.
        """
        from thermodynamics import Harmonic
        #from CRYSTALpytools.thermodynamics import Harmonic
        import warnings
        import re
        import numpy as np
        from pymatgen.core import Structure

        if hasattr(self, "ncalc"):
            warnings.warn('Data exists. The current command will be ignored.')
            return self

        if isinstance(input_file, list) and len(input_file) > 1:
            raise ValueError("Only a single QHA file is permitted")
        elif isinstance(input_file, list) and len(input_file) == 1:
            input_file = input_file[0]

        if mode_sort_tol != None:
            read_eigvt = True
        else:
            read_eigvt = False

        output = Crystal_output(input_file)
        output.get_phonon(read_eigvt=read_eigvt, rm_imaginary=False, rm_overlap=False)
        strucs = _restore_pcel(output, scelphono)

        self.ncalc = output.nqpoint
        self.nqpoint = 1
        self.qpoint = [[np.array([0., 0., 0.]), 1.]]

        ha_list = []
        for idx_c in range(self.ncalc):
            ha = Harmonic(filename=None, autocalc=False)
            if read_eigvt == True:
                ha.from_frequency(output.edft[idx_c], [[np.zeros([3,]), 1.]],
                                  np.array([output.frequency[idx_c],]),
                                  np.array([output.eigenvector[idx_c],]),
                                  structure=strucs[idx_c])
            else:
                ha.from_frequency(output.edft[idx_c], [[np.zeros([3,]), 1.]],
                                  np.array([output.frequency[idx_c],]),
                                  [], structure=strucs[idx_c])
            ha_list.append(ha)

        self.combined_phonon, self.combined_volume, self.combined_edft, \
        self.combined_mode, close_overlap = self._combine_data(ha_list, mode_sort_tol)

        if ha_list[0].eigenvector == []:
            do_eigvt = False
        else:
            do_eigvt = True
        if self.filename != None:
            Output.write_QHA_combinedata(self)

            if mode_sort_tol != None and do_eigvt == True:
                Output.write_QHA_sortphonon(self, close_overlap)

        return self

    def from_phonopy_files(self, phono_yaml, struc_yaml=None, edft=None,
                           imaginary_tol=-1e-4, q_overlap_tol=1e-4,
                           q_id=None, q_coord=None):
        """
        Build a QHA object from `Phonopy <https://phonopy.github.io/phonopy/>`_
        'band.yaml' or 'qpoints.yaml' file.

        Args:
            phono_yaml (list[str]): ncalc\*1 list of Phonopy band.yaml or
                qpoint.yaml files
            struc_yaml (list[str]): ncalc\*1 list of Phonopy phonopy.yaml or
                phonopy_disp.yaml files. *Needed only if a qpoint.yaml file is
                read.*
            edft (list[float]): ncalc\*1 list / array of DFT energies.
            imaginary_tol (float): The threshold of negative frequencies.
            q_overlap_tol (float): The threshold of overlapping points, defined
                as the 2nd norm of the difference of fractional q vectors
            q_id (list[int]): See ``Harmonic.from_phonopy``.
            q_coord (list[list]): See ``Harmonic.from_phonopy``.

        .. note::

            ``q_id`` and ``q_coord`` should be set once and are applicable to
            all the yaml files.

        Returned attributes are consistent with ``Quasi_harmonic.from_HA_files``.
        """
        import numpy as np
        from thermodynamics import Harmonic
        #from CRYSTALpytools.thermodynamics import Harmonic
        import warnings

        if hasattr(self, "ncalc"):
            warnings.warn('Data exists. The current command will be ignored.')
            return self

        if len(input_files) == 1:
            raise Exception('Only 1 input file! Use Harmonic object or from_QHA_file method.')
        else:
            self.ncalc = len(input_files)

        if edft == None:
            warnings.warn('DFT energy is set to 0.')
            edft = np.zeros([self.ncalc,])

        if struc_yaml == None:
            struc_yaml = [None for i in range(self.ncalc)]

        ha_list = [
            Harmonic(filename=None, autocalc=False).from_phonopy(
                phono_yaml=phono_yaml[i],
                struc_yaml=struc_yaml[i],
                edft=edft[i],
                imaginary_tol=imaginary_tol,
                q_overlap_tol=q_overlap_tol,
                q_id=q_id,
                q_coord=q_coord
            ) for i in range(self.ncalc)
        ]

        self.combined_phonon, self.combined_volume, self.combined_edft, \
        self.combined_mode, close_overlap = self._combine_data(ha_list, mode_sort_tol=None) # Eigenvector not available
        self.nqpoint = ha_list[0].nqpoint
        self.qpoint = ha_list[0].qpoint # consistency of nqpoint is checked, but not qpoint.

        if ha_list[0].eigenvector == []:
            do_eigvt = False
        else:
            do_eigvt = True
        if self.filename != None:
            Output.write_QHA_combinedata(self)

            if mode_sort_tol != None and do_eigvt == True:
                Output.write_QHA_sortphonon(self, close_overlap)

        return self

    def _combine_data(self, ha_list, mode_sort_tol):
        """
        Combine the HA calculation data and rearrange it in the ascending order
        of volumes.

        Args:
            ha_list (list[Harmonic]): List of harmonic objects.
            mode_sort_tol (float | None)

        Returns:
            combined_phonon (list[Harmonic])
            combined_volume (list[float])
            combined_edft (list[float])
            combined_mode (list[Mode])

        :raise Exception: If number of q points, modes or atoms are not consistent across the HA calculations.
        """
        import numpy as np
        import warnings
        from thermodynamics import Mode
        #from CRYSTALpytools.thermodynamics import Mode

        # Sorting data according to volumes
        sorted_vol = np.zeros([self.ncalc, 2])
        nqpoint = ha_list[0].nqpoint
        nmode = ha_list[0].nmode  # nqpoint * 1 array
        natom = ha_list[0].natom  # int
        for index, ha_phonon in enumerate(ha_list):
            sorted_vol[index, :] = [index, ha_phonon.volume]
            # Check whether the numbers of modes and atoms are consistent.
            if (natom - ha_phonon.natom) != 0 or not np.all((nmode - ha_phonon.nmode) == 0) \
            or nqpoint - ha_phonon.nqpoint != 0:
                raise Exception('The number of qpoints, modes or atoms is not consistent across the sampling points')

        sorted_vol = sorted_vol[np.argsort(sorted_vol[:, 1])]
        nmode = nmode[0]
        if ha_list[0].eigenvector == []:
            do_eigvt = False
        else:
            do_eigvt = True

        combined_phonon = []
        # Volume, ncalc * 1 array
        combined_volume = np.zeros(self.ncalc)
        # DFT total energy, ncalc * 1 array
        combined_edft = np.zeros(self.ncalc)
        # Frequency, ncalc * nqpoint * nmode array
        combined_freq = np.zeros([self.ncalc, nqpoint, nmode])
        # Eigenvector, ncalc * nqpoint * nmode * natom * 3 array
        combined_eigvt = np.zeros([self.ncalc, nqpoint, nmode, natom, 3], dtype=complex)
        for idx_new, idx_vol in enumerate(sorted_vol):
            ha_phonon = ha_list[int(idx_vol[0])]
            combined_phonon.append(ha_phonon)
            combined_volume[idx_new] = idx_vol[1]
            combined_edft[idx_new] = ha_phonon.edft
            combined_freq[idx_new] = ha_phonon.frequency
            if do_eigvt == True:
                combined_eigvt[idx_new] = ha_phonon.eigenvector

        # ncalc * nqpoint * nmode array to nqpoint * ncalc * nmode array
        combined_freq = np.transpose(combined_freq, axes=[1, 0, 2])
        if do_eigvt == True:
            # ncalc * nqpoint * nmode * natom * 3 array to nqpoint * ncalc * nmode * natom * 3 array
            combined_eigvt = np.transpose(combined_eigvt, axes=[1, 0, 2, 3, 4])

        # Sort phonon modes if requested
        close_overlap = np.zeros([nqpoint, self.ncalc, nmode, nmode], dtype=int)
        if mode_sort_tol != None and do_eigvt == True:
            for idx_q in range(nqpoint):
                combined_freq[idx_q], combined_eigvt[idx_q], close_overlap[idx_q] \
                    = self._phonon_continuity(combined_freq[idx_q],
                                              combined_eigvt[idx_q],
                                              mode_sort_tol=mode_sort_tol)
            # nqpoint * ncalc * nmode_ref * nmode_sort array to nqpoint * nmode_ref * ncalc * nmode_sort array
            close_overlap = np.transpose(close_overlap, axes=[0, 2, 1, 3])
            for q, overlap_q in enumerate(close_overlap):
                n_overlap = int(np.sum(overlap_q))
                if n_overlap > 0:
                    warnings.warn(
                        'Close overlap of phonon modes detected at qpoint {}: {} overlaps out of {}*{} mode combinations at this point.'.format(q, n_overlap, nmode, nmode),
                        stacklevel=2
                    )

        elif mode_sort_tol != None and do_eigvt == False:
            warnings.warn('Eigenvectors not read. Mode sorting not available.', stacklevel=2)

        # nqpoint * ncalc * nmode array to nqpoint * nmode * ncalc array
        combined_freq = np.transpose(combined_freq, axes=[0, 2, 1])
        if do_eigvt == True:
            # nqpoint * ncalc * nmode * natom * 3 array to nqpoint *  nmode * ncalc * natom * 3 array
            combined_eigvt = np.transpose(combined_eigvt, axes=[0, 2, 1, 3, 4])

        combined_mode = []
        for idx_q in range(nqpoint):
            combined_mode_q = []
            for idx_m in range(nmode):
                if do_eigvt == True:
                    combined_mode_q.append(
                        Mode(rank=idx_m + 1,
                             frequency=combined_freq[idx_q, idx_m, :],
                             volume=combined_volume,
                             eigenvector=combined_eigvt[idx_q, idx_m, :])
                    )
                else:
                    combined_mode_q.append(
                        Mode(rank=idx_m + 1,
                             frequency=combined_freq[idx_q, idx_m, :],
                             volume=combined_volume)
                    )

            combined_mode.append(combined_mode_q)

        return combined_phonon, combined_volume, combined_edft, combined_mode,\
               close_overlap

    @staticmethod
    def _phonon_continuity(freq, eigvt, symm=None, mode_sort_tol=0.4):
        """
        Rearrange phonon modes by their continuity. If the difference between
        the maximum scalar product of corresponding eigenvectors (normalized to
        1) and scalar products of other modes is less than 0.4, warning is
        printed due to the potential overlap of modes. Adopted from CRYSTAL17.

        .. note::

            A. Erba, *J. Chem. Phys.*, 2014, **141**, 124115.

        Args:
            freq (array[float]): Phonon frequencies. Unit: THz
            eigvt (array[float]): Eigenvectores normalized to 1
            symm (array[float]): Sub-group numbers of corresponding modes.
                *Not implemented*
            mode_sort_tol (float): The threshold of close mode overlaps.

        Returns:
            freq (array[float]): Sorted phonon frequencies
            eigvt (array[float]): Sorted eigenvectores
            close_overlap (array[bool]):ncalc\*nmode\*nmode. Whether close
                overlap is identified between the previous calculation (2nd
                dimension) and the current one (3rd).
        """
        import numpy as np
        import copy

        # Exclude negative and 0 frequencies
        ncalc = len(freq)
        nmode = len(freq[0])

        # Sort phonon
        close_overlap = np.zeros([ncalc, nmode, nmode])
        for sort_c in range(1, ncalc):
            ref_c = sort_c - 1
            ref_eigvt = copy.deepcopy(eigvt[ref_c])
            sort_eigvt = copy.deepcopy(eigvt[sort_c])
            ref_eigvt = np.reshape(ref_eigvt, [nmode, nmode], order='C')
            sort_eigvt = np.reshape(sort_eigvt, [nmode, nmode], order='C')
            mode_product = np.abs(np.dot(ref_eigvt, sort_eigvt.conjugate().T)) # row: ref_m, col: sort_m
            for ref_m in range(nmode):
                sorted_pdt = 0.
                sorted_m = 0
                if freq[ref_c, ref_m] < 1e-4 or np.isnan(freq[ref_c, ref_m]):
                    continue
                for sort_m, sort_pdt in enumerate(mode_product[ref_m, :]):
                    if freq[sort_c, sort_m] < 1e-4 or np.isnan(freq[sort_c, sort_m]):
                        continue
                    if symm != None and symm[ref_c, ref_m] != symm[sort_c, sort_m]:
                        continue

                    if sort_pdt > sorted_pdt:
                        if sort_m < ref_m:
                            if mode_product[sort_m, sort_m] > sort_pdt:
                                continue

                        sorted_pdt = sort_pdt
                        sorted_m = sort_m

                # Very poor overlaps
                if sorted_pdt < mode_sort_tol:
                    raise ValueError('Poor continuity detected! The maximum overlap is {} between Mode {}, Calc {} and Mode {}, Calc {}'.format(sorted_pdt, ref_m, ref_c, sorted_m, sort_c))
                # Look for close overlaps
                for sort_m, i in enumerate(sorted_pdt - mode_product[ref_m, :]):
                    if i > 0 and i < mode_sort_tol:
                        close_overlap[sort_c, ref_m, sort_m] = 1
                    else:
                        continue

                # products[sort_c, ref_m] = ref_pdt
                freq[[sort_c, sort_c], [sorted_m, ref_m]] = freq[[sort_c, sort_c], [ref_m, sorted_m]]
                eigvt[[sort_c, sort_c], [sorted_m, ref_m]] = eigvt[[sort_c, sort_c], [ref_m, sorted_m]]
                if symm != None:
                    symm[[sort_c, sort_c], [sorted_m, ref_m]] = symm[[sort_c, sort_c], [ref_m, sorted_m]]
                # Also update mode_product for all ref_m
                mode_product[:, [sorted_m, ref_m]] = mode_product[:, [ref_m, sorted_m]]

        return freq, eigvt, close_overlap

    def eos_fit(self, volume, energy, method, write_out=True, **kwargs):
        """
        Fit energy-volume relationship by equation of states.

        Args:
            volume (array[float]): Unit: Angstrom^3
            energy (array[float]): Unit: kJ/mol
            method (str): Name of EoS used. Consistent with
                `Pymatgen <https://pymatgen.org/pymatgen.analysis.eos.html>`_.
            write_out (bool): Whether to print EOS information.
            order (int): For DeltaFactor / Polynomial methods.
            min_ndata_factor, max_poly_order_factor, min_poly_order_factor (int):
                For the NumericalEOS method.

        Returns:
            eos (Pymatgen EOS): The fitted equation of state.
            eos_method (string): Name of the fitted equation of state
        """
        import re
        from pymatgen.analysis.eos import Murnaghan, Birch, BirchMurnaghan, \
            PourierTarantola, Vinet, DeltaFactor, NumericalEOS, PolynomialEOS
        from thermodynamics import Output
        ########from CRYSTALpytools.thermodynamics import Output

        eos_method = method
        classes = {
            "murnaghan"         : Murnaghan,
            "birch"             : Birch,
            "birch_murnaghan"   : BirchMurnaghan,
            "pourier_tarantola" : PourierTarantola,
            "vinet"             : Vinet,
            "deltafactor"       : DeltaFactor,
            "numerical_eos"     : NumericalEOS,
            "polynomial"        : PolynomialEOS,
        }
        eos = classes[method](volume, energy)
        eos_command = 'eos.fit('
        # Polynomial / Deltafactor / Numerical
        for idx, key in enumerate(kwargs.keys()):
            value = list(kwargs.values())[idx]
            eos_command += ', {}={}'.format(key, value)
        eos_command += ')'
        eval(eos_command)

        if self.filename != None and write_out == True:
            Output.write_QHA_eosfit(self, eos, method)

        return eos, method

    def freq_polynomial_fit(self, order):
        """
        Fit phonon frequencies as polynomial functions of volumes.

        Args:
            order (list[int] | array[int]): The order of polynomials used.

        Returns:
            self.fit_order (int): The optimal order of polynomial fit.

        Please also refer to ``self.poly_fit`` and ``self.poly_fit_rsquare``
        attributes of Mode class.
        """
        import numpy as np
        from thermodynamics import Output
        #from CRYSTALpytools.thermodynamics import Output

        rsquare_q = np.zeros([self.nqpoint, len(order)]) # Nqpoint * Norder
        for idx_q, mode_q in enumerate(self.combined_mode):
            for mode in mode_q:
                order_new, _, _ = mode.polynomial_fit(order=order)
                # Overall goodness at q point
                for idx_dic, dic in enumerate(mode.poly_fit_rsqaure.items()):
                    rsquare_q[idx_q, idx_dic] += dic[1] / len(mode_q)

        rsquare_tot = np.average(rsquare_q, axis=0) # 1 * Norder
        self.fit_order = order_new[np.argmax(rsquare_tot)]

        if self.filename != None:
            Output.write_QHA_polyfit(self, order_new, rsquare_q)

        return self

    def _get_harmonic_phonon(self, volume):
        """
        Get numerical phonon frequencies from fitted analytical expressions and
        generate harmonic phonon objects. Not a standalone method.

        Args:
            volume (float): Unit: Angstrom^3

        Returns:
            ha (Harmonic): Harmonic phonon object with numerical data.

        :raise Exception: If frequency is not fitted as function of volumes.
        """
        import numpy as np
        from thermodynamics import Harmonic
        #from CRYSTALpytools.thermodynamics import Harmonic
        from thermodynamics import Mode
        #from CRYSTALpytools.thermodynamics import Mode

        if not hasattr(self, 'fit_order') or not hasattr(self, 'e0_eos'):
            raise Exception('ERROR: Analytical expressions unavailable.')

        num_freq = []
        for mode_q in self.combined_mode:
            num_freq_q = []
            for mode in mode_q:
                idx_vmin = np.argmin(mode.volume)
                vmin = mode.volume[idx_vmin]
                fmin = mode.frequency[idx_vmin]
                dv = volume - vmin
                num_freq_q.append(mode.poly_fit[self.fit_order](dv) + fmin)
            num_freq.append(num_freq_q)

        num_freq = np.array(num_freq)
        ha = Harmonic(filename=None, autocalc=False).from_frequency(
            self.e0_eos(volume), self.qpoint, num_freq, [], volume=volume, ignore_natom=True)

        return ha

    def _minimize_gibbs(self, volume, temperature, pressure):
        """
        Get Gibbs free energy from the Harmonic phonon object. Used only for
        minimizing :math:`G(V;T, p)` by SciPy.

        Args:
            volume (float)
            temperature (float)
            pressure (float)

        Returns:
            ha.gibbs (float): Gibbs free energy. Unit: KJ/mol
        """
        volume = volume[0]
        ha = self._get_harmonic_phonon(volume)
        ha.thermodynamics(temperature=[temperature], pressure=[pressure])

        return ha.gibbs[0, 0, 0]

    @staticmethod
    def _poly_no_cst(param, x, y):
        """
        Define a polynomial :math:`\\Delta f(\\Delta x)` without constant term.
        Orders low to high. For SciPy. Functions of vectors not supported.
        """
        import numpy as np

        express = np.zeros([len(x)])
        for order, p in enumerate(param):
            express += p * x**(order + 1)
        return express - y

    def _clean_attr(self):
        """
        When temperature / pressure are changed, thermodynamic attributes are
        removed to keep consistency.
        """
        attr_list = ['volume', 'helmholtz', 'gibbs', 'entropy', 'c_v', 'c_p',
                     'k_t', 'k_s', 'fe_eos_method', 'fe_eos', 'gruneisen',
                     'alpha_vgru', 'c_pgru', 'k_sgru', 'alpha_v', 'vol_fit']

        for attr in attr_list:
            if hasattr(self, attr):
                delattr(self,attr)

        return self

    def thermo_freq(self, eos_method='birch_murnaghan', poly_order=[2, 3],
                    min_method='BFGS', volume_bound=None, mutewarning=False,
                    **kwargs):
        """
        Obtain thermodynamic properties by explicitly fitting phonon
        frequencies as polynomial functions of volume. DFT total energies are
        fitted as a function of volume by equation of states (EOS).

        The equilibrium volume is fitted by minimizing Gibbs free energy at
        constant temperature and pressure.

        .. math::

            V(T,p)=\\text{min}[G(V;T,p)]=\\text{min}[E_{0}(V)+F_{vib}(V;T,p)+pV)]

        Args:
            eos_method (str, optional): EOS used to fit DFT total energy and
                Helmholtz free energy (to get bulk modules).
            poly_order (array[int] | list[int], optional): The order of
                polynomials used to fit frequency as the function of volumes.
            min_method (string, optional): Minimisation algorithms.
            volume_bound (tuple-like, optional), Boundary conditions of
                equilibrium volumes. Unit: Angstrom^3
            mutewarning (bool, optional): Whether print out warning messages.
            temperature (array[float], optional): Unit: K
            pressure (array[float], optional): Unit: GPa
            order (int, optional): For DeltaFactor / Polynomial EOSs.
            min_ndata_factor, max_poly_order_factor, min_poly_order_factor (int, optional):
                For Numerical EOS.

        .. note::

            #. Valid entries of ``eos_method`` are consistent with `PyMatGen <https://pymatgen.org/pymatgen.analysis.eos.html>`_.
            #. Parameterized and tested algorithms for ``min_method``:
                * BFGS(no boundary)
                * L-BFGS-B(with boundary)

        Returns:
            self (Quasi_harmonic): New Attributes listed below
            self.temperature (array): Unit: K
            self.pressure (array): Unit: GPa
            self.volume (array): nPressure\*nTemperature, same below. Equilibrium volumes. Unit: :math:`\AA^{3}`
            self.helmholtz (array): Helmholtz free energy. Unit: kJ/mol
            self.gibbs (array): Gibbs free energy. Unit: kJ/mol
            self.entropy (array): Entropy. Unit: :math:`J.mol^{-1}.K^{-1}`
            self.c_v (array): Constant volume specific heat. Unit: :math:`J.mol^{-1}.K^{-1}`
            self.e0_eos (Pymatgen EOS): Pymatgen EOS object. EOS used to fit DFT energy.
            self.e0_eos_method (str): Name of the EOS.

        :raise ValueError: If temperature or pressure is defined neither here nor during initialization.
        """
        import numpy as np
        import warnings
        from scipy.optimize import minimize
        from thermodynamics import Output
        #from CRYSTALpytools.thermodynamics import Output

        # Generate temperature and pressure series
        if 'temperature' in kwargs:
            if hasattr(self, 'temperature') and not mutewarning:
                warnings.warn('Temperature attribute exists. Input temperatures will be used to update the attribute.',
                              stacklevel=2)
            self.temperature = np.array(kwargs['temperature'], dtype=float)
            self._clean_attr()

        if 'pressure' in kwargs:
            if hasattr(self, 'pressure') and not mutewarning:
                warnings.warn('Pressure attribute exists. Input pressures will be used to update the attribute.',
                              stacklevel=2)
            self.pressure = np.array(kwargs['pressure'], dtype=float)
            self._clean_attr()

        if not hasattr(self, 'temperature') or not hasattr(self, 'pressure'):
            raise ValueError('Temperature and pressure should be specified.')

        # Fit DFT total energy, if not done yet. Otherwise, fitted values will not be covered.
        if hasattr(self, 'e0_eos') and not mutewarning:
            warnings.warn('DFT total energy is already fitted. To keep the consistency, it will not be updated.',
                          stacklevel=2)
        else:
            eos_method = eos_method.casefold()
            eos_command = 'self.eos_fit(self.combined_volume, self.combined_edft, eos_method'
            # Polynomial / Deltafactor / Numerical
            for idx, key in enumerate(kwargs.keys()):
                if key == 'temperature' or key == 'pressure':
                    continue
                value = list(kwargs.values())[idx]
                eos_command += ', {}={}'.format(key, value)
            eos_command += ')'
            self.e0_eos, self.e0_eos_method = eval(eos_command)
        # Fit frequencies, if not done yet. Otherwise, fitted values will not be covered.
        if hasattr(self, 'fit_order') and not mutewarning:
            warnings.warn('Frequency is already fitted to polynomials. To keep the consistency, it will not be updated.',
                          stacklevel=2)
        else:
            self.freq_polynomial_fit(order=poly_order)

        # Define minimization methods
        methods = {
            'BFGS': "vol = minimize(self._minimize_gibbs, v_init, args=(t, p), method='BFGS', jac='3-point')",
            'L-BFGS-B': "vol = minimize(self._minimize_gibbs, v_init, args=(t, p), method='L-BFGS-B', jac='3-point', bounds=volume_bound)",
        }

        # Gibbs(V; T, p) minimization nPress*nTempt list
        self.volume = np.zeros([len(self.pressure), len(self.temperature)])
        v_init = np.mean(self.combined_volume)

        for idx_p, p in enumerate(self.pressure):
            for idx_t, t in enumerate(self.temperature):
                params = {'self': self,
                          'minimize': minimize,
                          'v_init': v_init,
                          't': t,
                          'p': p,
                          'volume_bound': volume_bound}
                exec(methods[min_method], params)
                self.volume[idx_p, idx_t] = params['vol'].x[0]

                if (params['vol'].x[0] < min(self.combined_volume) or params['vol'].x[0] > max(self.combined_volume)) and not mutewarning:
                    warnings.warn('Optimised volume exceeds the sampled range. Special care should be taken of.\n  Volume: %12.4f, Temperature: %6.2f, Pressure: %6.2f\n'
                                  % (params['vol'].x[0], t, p), stacklevel=2)

        # Calculate other thermodynamic properties
        self.helmholtz = np.zeros(self.volume.shape)
        self.gibbs = np.zeros(self.volume.shape)
        self.entropy = np.zeros(self.volume.shape)
        self.c_v = np.zeros(self.volume.shape)
        for idx_p, p in enumerate(self.pressure):
            for idx_t, t in enumerate(self.temperature):
                vol = self.volume[idx_p, idx_t]
                ha = self._get_harmonic_phonon(vol)
                ha.thermodynamics(temperature=[t], pressure=[p], mutewarning=True)
                self.helmholtz[idx_p, idx_t] = ha.helmholtz[0, 0]
                self.gibbs[idx_p, idx_t] = ha.gibbs[0, 0, 0]
                self.entropy[idx_p, idx_t] = ha.entropy[0, 0]
                self.c_v[idx_p, idx_t] = ha.c_v[0, 0]

        # Print output file
        if self.filename != None:
            Output.write_QHA_thermofreq(self, min_method, volume_bound)

        return self

    def thermo_gruneisen(self, eos_method='birch_murnaghan', min_method='BFGS',
                         volume_bound=None, mutewarning=False, **kwargs):
        """
        Grüneisen parameters and related properties. The macroscopic Grüneisen
        parameter is defined as:

        .. math::

            \\gamma=\\sum_{\\textbf{q}i}\\frac{\\gamma_{\\textbf{q}i}C_{V,\\textbf{q}i}}{C_{V}}

        Thermal expansion coefficient in Grüneisen model:

        .. math::

            \\alpha_{V}^{gru}=\\frac{\\gamma C_{V}}{K_{T}V}

        .. note::

            The Grüneisen model is used to fit frequencies, equivalent to using
            ``self.thermo_freq(poly_order=[1,])``.

        For arguments, see ``self.thermo_freq``.

        Returns:
            self (Quasi_harmonic): New attributes listed below. Other attributes are the same as ``self.thermo_freq``.
            self.gruneisen(array): npressure\*ntemperature, same below. Macroscopic Grüneisen parameter. Temperature should > 0.
            self.alpha_vgru (array): Thermal expansion coefficient by Grüneisen method.
            self.c_pgru (array): Constant pressure specific heat by Grüneisen method. Unit: :math:`J.mol^{-1}.K^{-1}`
            self.k_t (array): Isothermal bulk modulus. Unit: GPa.
            self.k_sgru (array): Adiabatic bulk modulus by Grüneisen method. Unit: GPa.
        """
        import numpy as np
        import scipy.constants as scst
        import warnings
        from thermodynamics import Output
        #from CRYSTALpytools.thermodynamics import Output

        if hasattr(self, 'fit_order'):
            raise AttributeError('self.gruneisen cannot be used when self.thermo_freq is already used.')

        command = 'self.thermo_freq(eos_method=eos_method, poly_order=[1,], min_method=min_method, volume_bound=volume_bound, mutewarning=mutewarning'

        for idx, key in enumerate(kwargs.keys()):
            value = list(kwargs.values())[idx]
            if type(value) == np.ndarray:
                value = list(value)
            command += ', {}={}'.format(key, value)
        command += ')'
        eval(command)

        # Get mode-specific Grüneisen parameter
        for idx_q, mode_q in enumerate(self.combined_mode):
            for idx_m, mode in enumerate(mode_q):
                self.combined_mode[idx_q][idx_m].get_gruneisen(order=[1,], volume=self.volume)

        # Macroscopic Grüneisen parameter
        sum_gCv = np.zeros(self.volume.shape, dtype=float)
        for idx_q, mode_q in enumerate(self.combined_mode):
            for idx_m, mode in enumerate(mode_q):
                c_v = np.zeros(self.volume.shape, dtype=float)
                if idx_m == 0 or idx_m == 1 or idx_m == 2:
                    continue
                # Get matrix C_v, nTempt*nPress
                idx_vmin = np.argmin(mode.volume)
                vmin = mode.volume[idx_vmin]
                fmin = mode.frequency[idx_vmin]
                dv = self.volume - vmin
                for idx_t, t in enumerate(self.temperature):
                    if t > 1e-4: # > 0K
                        kb_t = scst.k * scst.Avogadro * t
                        hbar_freq = (fmin + mode.poly_fit[1](dv[:, idx_t])) * scst.Avogadro * scst.h * 1e12
                        expon = np.exp(hbar_freq / kb_t)
                        c_v[:, idx_t] = hbar_freq**2 / kb_t / t * expon / (expon - 1)**2
                    else:
                        c_v[:, idx_t] = 0.
                sum_gCv += c_v * mode.gruneisen[1]

        # Get K_T, EOS keywords
        command = 'self.bulk_modulus(adiabatic=False'
        for idx, key in enumerate(kwargs.keys()):
            if key == 'temperature' or key == 'pressure':
                continue
            command += ', {}={}'.format(key, list(kwargs.values())[idx])
        command += ')'
        eval(command)

        self.alpha_vgru = sum_gCv / self.k_t / self.volume / 1e-21 / scst.Avogadro
        self.c_pgru = self.c_v + self.alpha_vgru**2 * self.k_t * self.volume * self.temperature * 1e-21 * scst.Avogadro

        self.gruneisen = np.zeros(self.volume.shape)
        self.k_sgru = np.zeros(self.volume.shape)
        for idx_t, t in enumerate(self.temperature):
            if t < 1e-4: # 0K
                continue
            self.gruneisen[:, idx_t] = sum_gCv[:, idx_t] / self.c_v[:, idx_t]
            self.k_sgru[:, idx_t] = self.k_t[:, idx_t] + \
                self.alpha_vgru[:, idx_t]**2 * self.volume[:, idx_t] * t * self.k_t[:, idx_t]**2 * 1e-21 * scst.Avogadro / self.c_v[:, idx_t]

        # print out options
        if self.filename != None:
            Output.write_QHA_thermogru(self)

        return self

    def thermo_eos(self, eos_method='birch_murnaghan', poly_order=[2, 3],
                   mutewarning=False, **kwargs):
        """
        Obtain thermodynamic properties by fitting EOS, which is fitted by the
        Helmholtz free energies of sampled harmonic phonons. The explicit
        sorting and fitting of frequency-volume relationship is disabled.

        Entropy is obtained by taking the derivation of Gibbs free energy at
        constant pressure.

        .. math::

            S=-\\left(\\frac{\\partial G}{\\partial T}\\right)_{p}

        Constant pressure specific heat is obtained by taking the second
        derivative of :math:`G`.

        .. math::

            C_{p}=-T\\left(\\frac{\\partial^{2}G}{\\partial T^{2}}\\right)_{p}

        .. note::

            ``poly_order`` should >= 2.

        For arguments, see ``self.thermo_freq``.

        Returns:
            self (Quasi_harmonic): New attributes listed below
            self.temperature (array): Unit: K
            self.pressure (array): Unit: GPa
            self.volume (array): nPressure\*nTemperature, same below. Equilibrium volumes. Unit: :math:`\AA^{3}`
            self.helmholtz (array): Helmholtz free energy. Unit: kJ/mol
            self.gibbs (array): Gibbs free energy. Unit: kJ/mol
            self.entropy (array): Entropy. Unit: :math:`J.mol^{-1}.K^{-1}`
            self.c_p (array): Constant pressure specific heat. Unit: :math:`J.mol^{-1}.K^{-1}`
            self.fe_eos (list[Pymatgen EOS]): nTemperature\*1 list of Pymatgen EOS objects. EOSs used to fit HA free energy at constant temperature.
            self.fe_eos_method (str): The name of EOS used.

        :raise Exception: If the number of HA calculations is less than 4.
        :raise ValueError: If temperature or pressure is defined neither here nor during initialization.
        """
        import numpy as np
        import warnings
        import re
        from scipy.optimize import fmin, least_squares
        import scipy.constants as scst
        from sympy import diff, lambdify, symbols
        from thermodynamics import Output
        #from CRYSTALpytools.thermodynamics import Output

        # Check the number of calculations
        if self.ncalc < 4:
            raise Exception('Insufficient database. Increase HA phonons')

        # Generate temperature and pressure series
        if 'temperature' in kwargs:
            if hasattr(self, 'temperature') and not mutewarning:
                warnings.warn('Temperature attribute exists. Input temperatures will be used to update the attribute.',
                              stacklevel=2)
            self.temperature = np.array(kwargs['temperature'], dtype=float)
            self._clean_attr()

        if 'pressure' in kwargs:
            if hasattr(self, 'pressure') and not mutewarning:
                warnings.warn('Pressure attribute exists. Input pressures will be used to update the attribute.',
                              stacklevel=2)
            self.pressure = np.array(kwargs['pressure'], dtype=float)
            self._clean_attr()

        if not hasattr(self, 'temperature') or not hasattr(self, 'pressure'):
            raise ValueError('Temperature and pressure should be specified.')

        # Get data for fitting. Helmholtz: nTempt*nCalc matrix
        helmholtz = np.zeros([len(self.temperature), self.ncalc], dtype=float)
        for idx_c, calc in enumerate(self.combined_phonon):
            calc.thermodynamics(sumphonon=True, mutewarning=True,
                                temperature=self.temperature, pressure=[0.])
            helmholtz[:, idx_c] = calc.helmholtz

        # Fit EOS
        eos_method = eos_method.casefold()
        if hasattr(self, 'fe_eos') and not mutewarning:
            warnings.warn('Harmonic free energy EOS is fitted. To keep the consistency, it will not be updated.',
                          stacklevel=2)
        else:
            self.fe_eos_method = eos_method
            self.fe_eos = []
            for idx_t, t in enumerate(self.temperature):
                eos_command = 'self.eos_fit(self.combined_volume, helmholtz[idx_t, :], eos_method, write_out=False'
                # Polynomial / Deltafactor / Numerical
                for idx, key in enumerate(kwargs.keys()):
                    if key == 'temperature' or key == 'pressure':
                        continue
                    value = list(kwargs.values())[idx]
                    eos_command += ', {}={}'.format(key, value)
                eos_command += ')'
                eos, _ = eval(eos_command)
                self.fe_eos.append(eos)
        # Get thermoproperties
        self.volume = np.zeros([len(self.pressure), len(self.temperature)])
        self.helmholtz = np.zeros(self.volume.shape)
        self.gibbs = np.zeros(self.volume.shape)
        self.entropy = np.zeros(self.volume.shape)
        self.c_p = np.zeros(self.volume.shape)
        v = symbols('v')
        for idx_t, eos in enumerate(self.fe_eos):
            p_eos = -diff(eos(v), v, 1)
            for idx_p, p in enumerate(self.pressure):
                p_kj = p * scst.Avogadro / 1e24  # GPa --> kJ/mol.Angstrom^3
                lam_p = lambdify(v, (p_eos - p_kj)**2, 'numpy')
                fit = fmin(lam_p, eos.v0, full_output=True, disp=False)
                if np.isnan(fit[0]) == True:
                    raise ValueError('EOS fitting failed at %6.2f K, %6.2f GPa. More sampling points needed.' % (self.temperature[idx_t], p))
                if (fit[0] < min(self.combined_volume) or fit[0] > max(self.combined_volume)) and not mutewarning:
                    warnings.warn('Optimised volume exceeds the sampled range. Special care should be taken of.\n  Volume: %12.4f, Temperature: %6.2f, Pressure: %6.2f\n'
                                  % (fit[0], t, p), stacklevel=2)
                self.volume[idx_p, idx_t] = fit[0]
                self.helmholtz[idx_p, idx_t] = eos(fit[0])
                self.gibbs[idx_p, idx_t] = eos(fit[0]) + p_kj * fit[0]

        # Second fit G(T; p), get entropy and C_p
        if max(poly_order) > len(self.temperature) - 1 and not mutewarning:
            warnings.warn('Temperature series not sufficient for the order of polynomial fitting.\n Too high values will be removed.\n',
                          stacklevel=2)

        poly_order = list(set(poly_order))
        poly_order = [p for p in poly_order if p <= len(self.temperature) - 1]

        idx_tmin = np.argmin(self.temperature)
        tmin = self.temperature[idx_tmin]
        dt = self.temperature - tmin
        for idx_p, gibbs in enumerate(self.gibbs):
            r_square = []
            func = []
            for order in poly_order:
                if order < 2:
                    warnings.warn('The minimum order of polynomial is 2. Skip this entry.')
                    continue
                gmin = gibbs[idx_tmin]
                dg = gibbs - gmin
                opt = least_squares(self._poly_no_cst,
                                    np.array([1. for i in range(order)]),
                                    args=(dt, dg))
                poly = np.polynomial.polynomial.Polynomial(np.insert(opt.x, 0, 0.))
                func.append(poly)
                r_square.append(1 - np.sum((dg - poly(dt))**2) / np.sum((dg - np.mean(dg))**2))

            self.fit_order = poly_order[np.argmax(r_square)]
            entropy = func[np.argmax(r_square)].deriv(1)
            self.entropy[idx_p, :] = -entropy(dt) * 1000.
            c_p = func[np.argmax(r_square)].deriv(2)
            self.c_p[idx_p, :] = -c_p(dt) * 1000 * self.temperature

        # Print output file
        if self.filename != None:
            Output.write_QHA_thermoeos(self)

        return self

    def expansion_vol(self, poly_order=[2, 3], plot=True, fit_fig='expansion_fit.png'):
        """
        Fit the thermal expansion curve and get thermal expansion coefficients
        at equilibrium volumes.

        The volumetric thermal expansion coefficient at constant pressure:

        .. math::

            \\alpha_{V}(T) = \\frac{1}{V(T)}\\left(\\frac{\\partial V(T)}{\\partial T}\\right)_{p}

        Args:
            poly_order (list[int]): *method = 'polynomial'*, order of polynomials.
            plot (bool): Plot V-T curves to examine the goodness of fitting. An
                interactive window will pump out to let user to specify the
                optimial fitting.
            fit_fig (str): File name for fittings. A temperal figure is printed
                to help the user choose the optimal fitting.

        Returns:
            self (Quasi_harmonic): New attributes listed below
            self.vol_fit (list): nPressure\*1. List of Numpy polynomial object, the fitted volume V(T)
            self.alpha_v (array): nPressure\*nTemperature. Expansion coefficients at equilibrium volumes
        """
        import numpy as np
        from scipy.optimize import least_squares
        import matplotlib.pyplot as plt
        import warnings
        from thermodynamics import Output
        #from CRYSTALpytools.thermodynamics import Output

        if not hasattr(self, 'volume'):
            raise AttributeError('Equilibrium volume should be fit first.')

        if max(poly_order) > self.ncalc - 1:
            warnings.warn('Reference data not sufficient for the order of polynomial fitting.')
            warnings.warn('Too high values will be removed.')

        poly_order = list(set(poly_order))
        poly_order = [p for p in poly_order if p <= self.ncalc - 1]
        poly_order = np.array(poly_order)
        # Polynomial fitting
        func = []
        rs = []
        idx_tmin = np.argmin(self.temperature)
        tmin = self.temperature[idx_tmin]
        dt = self.temperature - tmin
        for idx_p, v_p in enumerate(self.volume):
            func_p = []
            rs_p = []
            vmin = v_p[idx_tmin]
            dv = v_p - vmin
            for order in poly_order:
                opt = least_squares(self._poly_no_cst,
                                    np.array([1. for i in range(order)]),
                                    args=(dt, dv))
                poly = np.polynomial.polynomial.Polynomial(np.insert(opt.x, 0, 0.))
                r_square = 1 - np.sum((dv - poly(dt))**2) / np.sum((dv - np.mean(dv))**2)
                func_p.append(poly)
                rs_p.append(r_square)
            func.append(func_p)
            rs.append(rs_p)

        # Get the optimal fit
        rs = np.array(rs) # npress * npolyorder
        rs_mean = np.array([np.mean(rs[:, i]) for i in range(len(poly_order))])
        if plot == False:
            fit_order_idx = np.argmax(rs_mean)
            fit_order = poly_order[fit_order_idx]
        else:
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            cmap = np.vstack([np.linspace([0, 0, 1], [0, 1, 1], 20, endpoint=False),
                              np.linspace([0, 1, 1], [0, 1, 0], 20, endpoint=False),
                              np.linspace([0, 1, 0], [1, 1, 0], 20, endpoint=False),
                              np.linspace([1, 1, 0], [1, 0, 0], 21, endpoint=True)])
            for idx_p, v_p in enumerate(self.volume):
                ax.scatter(self.temperature, v_p, color='k', marker='D', s=40)
                vmin = v_p[idx_tmin]
                dv = v_p - vmin
                for idx_i, i in enumerate(poly_order):
                    t_interp = np.linspace(self.temperature.min(), self.temperature.max(), 1000)
                    c = cmap[int(idx_i / len(poly_order) * 101)]
                    if idx_p == 0:
                        txt = 'Order {:d}, R^2 {:.4f}'.format(i, rs_mean[idx_i])
                        ax.plot(t_interp, vmin + func[idx_p][idx_i](t_interp - tmin), color=c, label=txt)
                    else:
                        ax.plot(t_interp, vmin + func[idx_p][idx_i](t_interp - tmin), color=c)

            ax.legend(loc='lower right')
            fig.savefig(fname=fit_fig, dpi=200)
            # Choose optimal fit
            fit_order = input('Set the optimal fit: ')
            fit_order = int(fit_order)
            for idx, i in enumerate(poly_order):
                if int(i) == fit_order:
                    break
            fit_order_idx = idx

        self.vol_fit = [i[fit_order_idx] for i in func]
        fit_rs = [i[fit_order_idx] for i in rs]

        # Expansion coefficients
        self.alpha_v = np.zeros([len(self.pressure), len(self.temperature)])
        for idx_p, v_p in enumerate(self.volume):
            vmin = v_p[idx_tmin]
            dv = v_p - vmin
            self.alpha_v[idx_p, :] = \
                self.vol_fit[idx_p].deriv(1)(dt) / (self.vol_fit[idx_p](dt) + vmin)

        self.alpha_v[:, idx_tmin] = 0. # Lowest temperature, alpha = 0

        # Print output file
        if self.filename != None:
            Output.write_expansion_vol(self, fit_order, fit_rs)

        return self

    def bulk_modulus(self, adiabatic=True, **kwargs):
        """
        Calculate isothermal and adiabatic bulk moduli at equilibrium volumes.

        The following equations are used:

        .. math::

            K_{T}(p;T) = V(p;T)\\left(\\frac{\\partial^{2}F(V;T)}{\\partial V^{2}}\\right)_{T}

            K_{S} = K_{T} + \\frac{\\alpha^{2}_{V}VTK^{2}_{T}}{C_{V}}

        To get :math:`K_{T}`, Helmholtz free energy is fit as isothermal EOSs.
        For ``self.thermo_eos()``, that means doing nothing; For
        ``self.thermo_freq()``, EOS fitting is required, whose form is the same
        as EOS used for :math:`E_{0}`.

        Args:
            adiabatic (bool): Whether to fit adiabatic bulk modulus. Thermal
                expansion coefficient needed.
            order, min_ndata_factor, max_poly_order_factor, min_poly_order_factor
                (int, optional): To restore EOS.

        Returns:
            self (Quasi_harmonic): New attributes listed below
            self.k_t (array): nPressure\*nTemperature, same below. Isothermal bulk modulus. Unit: GPa.
            self.k_s (array): Adiabatic bulk modulus. Unit: GPa.
        """
        import scipy.constants as scst
        from sympy import diff, lambdify, symbols
        import copy
        import numpy as np
        from thermodynamics import Output
        #from CRYSTALpytools.thermodynamics import Output

        if adiabatic == True and not hasattr(self, 'alpha_v'):
            raise AttributeError('Expansion coefficient should be fit at first.')

        # Fit EOS
        if not hasattr(self, 'fe_eos'): # thermo_freq
            self.fe_eos = []
            self.fe_eos_method = self.e0_eos_method
            for idx_t, t in enumerate(self.temperature):
                eos_command = 'self.eos_fit(self.volume[:, idx_t], self.helmholtz[:, idx_t], self.e0_eos_method, write_out=False'
                # Polynomial / Deltafactor / Numerical
                for idx, key in enumerate(kwargs.keys()):
                    value = list(kwargs.values())[idx]
                    eos_command += ', {}={}'.format(key, value)
                eos_command += ')'
                eos, _ = eval(eos_command)
                self.fe_eos.append(eos)

        # Get K_T
        self.k_t = np.zeros(self.volume.shape)
        v = symbols('v')
        for idx_t, eos in enumerate(self.fe_eos):
            df = diff(eos(v), v, 2)
            lam_df = lambdify(v, df, 'numpy')
            self.k_t[:, idx_t] = self.volume[:, idx_t] * lam_df(self.volume[:, idx_t]) * 1e24 / scst.Avogadro
        # Get K_S
        if adiabatic == True:
            self.k_s = np.zeros(self.volume.shape)
            self.specific_heat()
            for idx_t, t in enumerate(self.temperature):
                if t > 1e-4: #0K
                    self.k_s[:, idx_t] = self.k_t[:, idx_t] + \
                        self.alpha_v[:, idx_t]**2 * self.volume[:, idx_t] * t * self.k_t[:, idx_t]**2 * 1e-21 * scst.Avogadro\
                        / self.c_v[:, idx_t]
                else:
                    self.k_s[:, idx_t] = 0.

        # Print output file
        if self.filename != None:
            Output.write_bulk_modulus(self, adiabatic)

        return self

    def specific_heat(self):
        """
        Calculate constant volume or pressure specific heat at equilibrium
        volumes.

        The following equation is used:

        .. math::

            C_{p} - C_{V} = \\alpha_{V}^{2}K_{T}VT

        Returns:
            self (Quasi_harmonic): New attributes listed below
            self.c_v (array): nPressure\*nTemperature, same below. Constant volume specific heat. Unit: :math:`J.mol^{-1}.K^{-1}`
            self.c_p (array): Constant pressure specific heat. Unit: :math:`J.mol^{-1}.K^{-1}`

        .. note::

            This method fits ``self.c_p`` by ``self.c_v`` when ``thermo_freq``
            and ``thermo_gruneisen`` was used. ``self.c_v`` is obtained by when
            ``thermo_eos`` is used.
        """
        import numpy as np
        import warnings
        import scipy.constants as scst
        from thermodynamics import Output
        #from CRYSTALpytools.thermodynamics import Output

        if not hasattr(self, 'alpha_v') or not hasattr(self, 'k_t'):
            raise AttributeError(
                'Expansion coefficient and bulk modulus should be fit at first.')

        if not hasattr(self, 'c_p'): # thermo_freq
            self.c_p = self.c_v + self.alpha_v**2 * self.k_t * self.volume * self.temperature * 1e-21 * scst.Avogadro
        elif not hasattr(self, 'c_v'): # thermo_eos
            self.c_v = self.c_p - self.alpha_v**2 * self.k_t * self.volume * self.temperature * 1e-21 * scst.Avogadro
        else:
            warnings.warn("Attributes 'c_v' and 'c_p' both exist. Nothing is updated.")
            return self

        # Print output file
        if self.filename != None:
            Output.write_specific_heat(self)

        return self

    def expansion_lin(self, poly_order=[2, 3], interp=None):
        """
        Fit linear expansions of lattice parameters by the 2-order Taylor
        expansion.

        .. math::

            G(\\mathbf{p})=G_{0}(\\mathbf{p_{0}})+\\Delta\\mathbf{p}^{T}\\mathbf{H}\\Delta\\mathbf{p}

        :math::`G` is Gibbs free energy. :math:`\mathbf{p}` is the vector
        of lattice parameters. :math:`\Delta\mathbf{p}` means the
        difference between the fitted and equilibrium lattice parameters.
        :math:`\mathbf{H}` is the Hessian of :math:`G` and displacements
        along lattice parameters.

        The RMS deviations (RMSD) of the following equation is minimized
        at constant temperature and pressure. But deviations from
        equilibrium volume might occur. RMSD of Gibbs free energy is
        available in output file only.

        .. math::

            \\mathbf{p_{0}} = \\min\\left\\{\\Delta\\mathbf{p}^{T}\\mathbf{H}\\Delta\\mathbf{p} - [G(\\mathbf{p})-G_{0}(T,p)]\\right\\}

        This method requires a larger number of HA calculations to ensure
        a small RMSD. Typically the number of HA calculations should
        follow the equation below, otherwise the warning massage is given.

        .. math::

            n_{HA} \\geq n_{latt} + \\sum_{i=1}^{n_{latt}}i

        :math:`n_{latt}` is the lenth of the minimial set of lattice parameters.
        The optimized lattice parameters at DFT level are used for fitting.

        .. note::

            N. Raimbault, V. Athavale and M. Rossi, *Phys. Rev. Materials*, 2019, **3**, 053605.

        Args:
            poly_order (list[int]): Order of polynomials used to fit the
                linear expansion coefficients. The optimal fit across the
                sampled temperature and pressure range of a certain lattice
                parameter is automatically chosen based on :math:`R^{2}`.
            interp (int): Number of interpolated geometries. All the HA
                geometries are used besides the interpolated ones.

        Returns:
            self (Quasi_harmonic): New attributes listed below
            self.lattice (array): nPressure\*nTemperature\*nLattice. The equilibrium values of minimal set of lattice parameters.
            self.latt_fit (list): nPressure\*nLattice. Numpy polynomial object, the fitted a(v). Linear part only.
            self.alpha_latt (array): nPressure\*nTemperature\*nLattice. Linear expansion coefficients. Linear part only.
        """
        from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
        from pymatgen.core.lattice import Lattice
        from thermodynamics import Output
        #from CRYSTALpytools.thermodynamics import Output
        from scipy.optimize import least_squares
        import numpy as np
        import warnings

        if not hasattr(self, 'volume'):
            raise AttributeError('Equilibrium volume should be fit first.')

        if not hasattr(self.combined_phonon[0], 'structure'):
            raise AttributeError('No lattice information is found in input HA calculations.')

        if max(poly_order) > len(self.temperature) - 1:
            warnings.warn('Sampled temperature points are not sufficient for the order of polynomial fitting. Some values will be removed.',
                          stacklevel=2)

        poly_order = list(set(poly_order))
        poly_order = [p for p in poly_order if p <= self.ncalc - 1]
        poly_order = np.array(poly_order)

        # Analyze the refined geometry and return to reference lattice vectors
        latt_ref = []
        for phonon in self.combined_phonon:
            struc = phonon.structure
            analyzer = SpacegroupAnalyzer(struc)
            ref_struc = analyzer.get_refined_structure()
            analyzer2 = SpacegroupAnalyzer(ref_struc)
            symm_struc = analyzer2.get_symmetrized_structure()
            sg = analyzer2.get_space_group_number()
            latt = []
            if sg >= 1 and sg < 3:  # trilinic
                for i in ['a', 'b', 'c', 'alpha', 'beta', 'gamma']:
                    latt.append(round(
                        getattr(symm_struc.lattice, i), 10
                    ))
            elif sg >= 3 and sg < 16:  # monoclinic
                for i in ['a', 'b', 'c', 'beta']:
                    latt.append(round(
                        getattr(symm_struc.lattice, i), 10
                    ))
            elif sg >= 16 and sg < 75:  # orthorhombic
                for i in ['a', 'b', 'c']:
                    latt.append(round(
                        getattr(symm_struc.lattice, i), 10
                    ))
            elif sg >= 75 and sg < 195:  # tetragonal, hexagonal and trigonal
                for i in ['a', 'c']:
                    latt.append(round(
                        getattr(symm_struc.lattice, i), 10
                    ))
            else:  # cubic
                self.lattice = self.volume**(1 / 3)
                warnings.warn('''Cubic lattice! Use self.expansion_vol.
self.lattice is stored as a nPressure * nTemperature array.''')
                return self

            latt_ref.append(latt)

        latt_ref = np.array(latt_ref)
        # Add interpolated points
        if interp != None:
            # Lattice
            interp_latt = np.linspace(np.min(latt_ref, axis=0),
                                      np.max(latt_ref, axis=0),
                                      interp + 2)
            latt_ref = np.vstack([latt_ref, interp_latt[1:-1, :]])
            ncalc = self.ncalc + interp
            # Volume
            combined_volume = self.combined_volume
            for latt in interp_latt:
                if len(latt) == 6:
                    combined_volume = np.append(
                        combined_volume,
                        Lattice.from_parameters(a=latt[0],
                                                b=latt[1],
                                                c=latt[2],
                                                alpha=latt[3],
                                                beta=latt[4],
                                                gamma=latt[5]).volume
                    )
                elif len(latt) == 4:
                    combined_volume = np.append(
                        combined_volume,
                        Lattice.from_parameters(a=latt[0],
                                                b=latt[1],
                                                c=latt[2],
                                                alpha=90.,
                                                beta=latt[3],
                                                gamma=90.).volume
                    )
                elif len(latt) == 3:
                    combined_volume = np.append(
                        combined_volume,
                        Lattice.from_parameters(a=latt[0],
                                                b=latt[1],
                                                c=latt[2],
                                                alpha=90.,
                                                beta=90.,
                                                gamma=90.).volume
                    )
                elif len(latt) == 2 and sg >= 75 and sg < 143: # Tetragonal
                     combined_volume = np.append(
                        combined_volume,
                        Lattice.from_parameters(a=latt[0],
                                                b=latt[0],
                                                c=latt[1],
                                                alpha=90.,
                                                beta=90.,
                                                gamma=90.).volume
                    )
                elif len(latt) == 2 and sg >= 143 and sg < 195: # Hexagonal and trigonal
                     combined_volume = np.append(
                        combined_volume,
                        Lattice.from_parameters(a=latt[0],
                                                b=latt[0],
                                                c=latt[1],
                                                alpha=90.,
                                                beta=90.,
                                                gamma=120.).volume
                    )
        else:
            ncalc = self.ncalc
            combined_volume = self.combined_volume

        x0 = np.average(latt_ref, axis=0)
        # Hessian initial guess - elementary matrix
        hess_dimen = len(x0)
        hess_init_mx = np.eye(hess_dimen)
        hess_init = []
        for i in range(hess_dimen):
            for j in range(i, hess_dimen):
                hess_init.append(hess_init_mx[i, j])
        x0 = np.concatenate([x0, hess_init])
        if ncalc < len(x0):
            warnings.warn('The number of sampled points is less than number of unknowns. Large deviation is expected.',
                          stacklevel=2)

        # Minimize error of Gibbs free energy
        self.lattice = np.zeros([len(self.pressure), len(self.temperature), hess_dimen])
        e_err = np.zeros([len(self.pressure), len(self.temperature)], dtype=float)
        for idx_p, p in enumerate(self.pressure):
            for idx_t, t in enumerate(self.temperature):
                fe_eq = self.gibbs[idx_p, idx_t]
                fe_ref = []
                for v in combined_volume:
                    ha = self._get_harmonic_phonon(v)
                    ha.thermodynamics(temperature=[t,], pressure=[p,])
                    fe_ref.append(ha.gibbs[0, 0, 0])
                fe_ref = np.array(fe_ref)
                opt_out = least_squares(self._minimize_latt, x0,
                                        args=(fe_eq, latt_ref, fe_ref))
                self.lattice[idx_p, idx_t, :] = opt_out.x[:hess_dimen]
                e_err[idx_p, idx_t] = opt_out.fun

        # Polynomial fit: For thermal expansion coefficients. Linear part only.
        if sg >= 1 and sg < 75: # abc
            latt_fit = self.lattice[:, :, 0:3]
        elif sg >= 75 and sg < 195: # ac
            latt_fit = self.lattice[:, :, 0:2]

        r_square = np.zeros([latt_fit.shape[0], latt_fit.shape[2], len(poly_order)]) # nPress * nLatt * nOrder
        poly_fit = [[[None for i in range(len(poly_order))] for j in range(latt_fit.shape[2])] for k in range(latt_fit.shape[0])] # nPress * nLatt * nOrder
        idx_tmin = np.argmin(self.temperature)
        dt = self.temperature - self.temperature[idx_tmin]
        for idx_p, p in enumerate(self.pressure):
            latt_t = self.lattice[idx_p, :, :] # nTempt * nLatt
            latt_t = np.transpose(latt_t, axes=(1, 0)) # nLatt * nTempt
            for idx_latt, latt in enumerate(latt_t):
                dlatt = latt - latt[idx_tmin]
                for idx_order, order in enumerate(poly_order):
                    opt_out = least_squares(self._poly_no_cst,
                                            np.array([1. for i in range(order)]),
                                            args=(dt, dlatt))
                    poly = np.polynomial.polynomial.Polynomial(np.insert(opt_out.x, 0, 0.))
                    poly_fit[idx_p][idx_latt][idx_order] = poly
                    rs = 1 - np.sum((dlatt - poly(dt))**2) / np.sum((dlatt - np.mean(dlatt))**2)
                    r_square[idx_p, idx_latt, idx_order] = rs

        # Find the optimal fit
        self.latt_fit = [[None for i in range(latt_fit.shape[2])] for j in range(latt_fit.shape[0])] # nPress * nLatt
        fit_order = [None for i in range(latt_fit.shape[2])] # nLatt * 1 list
        r_square = np.transpose(r_square, (1, 0, 2)) # nLatt * nPress * nOrder
        for idx_latt, rs_latt in enumerate(r_square):
            rs_mean = np.array([np.mean(rs_latt[:, i]) for i in range(len(poly_order))])
            fit_order_idx = np.argmax(rs_mean)
            fit_order[idx_latt] = poly_order[fit_order_idx]
            for idx_p in range(latt_fit.shape[0]):
                self.latt_fit[idx_p][idx_latt] = poly_fit[idx_p][idx_latt][fit_order_idx]
        # Numerize the linear expansion
        self.alpha_latt = np.zeros([latt_fit.shape[0], latt_fit.shape[1], latt_fit.shape[2]]) # nPress * nTempt * nLatt
        idx_tmin = np.argmin(self.temperature)
        dt = self.temperature - self.temperature[idx_tmin]
        for idx_p, p in enumerate(self.pressure):
            for idx_t, t in enumerate(self.pressure):
                for idx_latt in range(latt_fit.shape[2]):
                    lattmin = self.lattice[idx_p, idx_t, idx_tmin]
                    self.alpha_latt[idx_p, :, idx_latt] = \
                        self.latt_fit[idx_p][idx_latt].deriv(1)(dt) / (self.latt_fit[idx_p][idx_latt](dt) + lattmin)
        # Lowest temperature, alpha = 0
        self.alpha_latt[:, idx_tmin, :] = 0.

        # Print output file
        if self.filename != None:
            Output.write_expansion_latt(self, e_err, fit_order,
                                        r_square[:, :, fit_order_idx])

        return self

    @staticmethod
    def _minimize_latt(x, fe_eq, latt_ref, fe_ref):
        """
        Minimize the RMSD between pHp^T and the difference of Gibbs free
        energy. For Scipy. For fitting lattice parameters in ``self.expansion_vol``.
        """
        import numpy as np
        from scipy.constants import pi

        # Build lattice vector
        hess_dimen = latt_ref.shape[1]
        p = np.array(x[0:hess_dimen])
        # Build Hessian
        Hess = np.zeros([hess_dimen, hess_dimen])
        hess_list = x[-int(hess_dimen * (hess_dimen + 1) / 2):]
        count_elem = 0
        for i in range(hess_dimen):
            for j in range(i, hess_dimen):
                Hess[i, j] = hess_list[count_elem]
                if i != j:
                    Hess[j, i] = hess_list[count_elem]
                count_elem += 1

        # Reference data
        dfe = fe_ref - fe_eq
        rmsd = 0.
        for idx_ref, ref in enumerate(latt_ref):
            dp = p - ref
            rmsd += (np.matmul(np.matmul(dp, Hess), np.transpose(dp)) - dfe[idx_ref])**2
        rmsd = (rmsd / latt_ref.shape[0])**0.5 # Return to RMS deviation

        return rmsd


def _restore_pcel(crysout, scelphono):
    """
    Restore the primitive geometry expanded by 'SCELPHONO' and generate the
    Pymatgen Structure of the cell used for phonon calculation.

    Args:
        crysout (Crystal_output): :code:`CRYSTALpytools.io.Crystal_output` object.
        scellphono (list[int] | array[int]): ndimension\*ndimension or 3\*3
            matrix corresponds to the 'SCELPHONO' keyword.

    Returns:
        structures (list[Structure]): A list of Pymatgen Structure objects.
            nCalc\*1. For HA phonons and dispersions, nCalc=1. For QHA,
            nCalc=sampled HA points.
    """
    from pymatgen.core.structure import Structure, Molecule
    from pymatgen.core.lattice import Lattice
    import numpy as np
    import re
    import warnings

    ndimen = crysout.get_dimensionality()
    pbc = {3 : (True, True, True),
           2 : (True, True, False),
           1 : (True, False, False)}

    # Get structure. Address the issue with QHA file
    idx_line = 0
    structures = []
    # Molecule 0D
    if ndimen == 0:
        if scelphono != []:
            warnings.warn('0D system is used. There is nothing to reduce.', stacklevel=2)
        while idx_line < len(crysout.data):
            if re.match(r'^\s+GEOMETRY FOR WAVE FUNCTION', crysout.data[idx_line]):
                idx_line += 6
                all_species = []
                all_coord = []
                while re.match(r'^\s+[0-9]+\s+[A-Z]+', crysout.data[idx_line]):
                    data = crysout.data[idx_line].strip().split()
                    all_coord.append(data[4:])
                    all_species.append(data[3].capitalize())
                    idx_line += 1

                all_coord = np.array(all_coord, dtype=float)
                min_max = max([max(all_coord[:, 0]) - min(all_coord[:, 0]),
                               max(all_coord[:, 1]) - min(all_coord[:, 1]),
                               max(all_coord[:, 2]) - min(all_coord[:, 2])])
                lattice = np.identity(3)*(min_max+10)
                structures.append(Structure(lattice, all_species, all_coord))
                idx_line += 1
            else:
                idx_line += 1

        return structures

    # Other cases
    while idx_line < len(crysout.data):
        if re.match(r'^\s+DIRECT LATTICE VECTORS CARTESIAN COMPONENTS', crysout.data[idx_line]):
            idx_line += 2
            vec1 = np.array(crysout.data[idx_line].strip().split()[0:3], dtype=float)
            vec2 = np.array(crysout.data[idx_line + 1].strip().split()[0:3], dtype=float)
            vec3 = np.array(crysout.data[idx_line + 2].strip().split()[0:3], dtype=float)

            idx_line += 9
            all_species = []
            all_coord = []
            while re.match(r'^\s+[0-9]+\s+[0-9]+\s+[A-Z]+', crysout.data[idx_line]):
                data = crysout.data[idx_line].strip().split()
                all_coord.append(data[3:])
                all_species.append(data[2].capitalize())
                idx_line += 1
            all_coord = np.array(all_coord, dtype=float)
            scel_latt = np.vstack([vec1, vec2, vec3])

            if scelphono != []:
                scell_mx = np.eye(3, dtype=float)
                scell_mx[: ndimen, : ndimen] = np.array(scelphono)[: ndimen, : ndimen]
                shrink_mx = np.linalg.pinv(scell_mx)
                pcel_mx = np.dot(scel_latt, shrink_mx)
                pcel_latt = Lattice(pcel_mx, pbc=pbc[ndimen])
                all_coord = np.dot(all_coord, np.linalg.pinv(pcel_mx)).tolist() # Fractional!
                pcel_coord = []
                pcel_species = []
                for i, coord in enumerate(all_coord):
                    if any(x > 0.5 or x <= -0.5 for x in coord[0:ndimen]):
                        continue
                    else:
                        pcel_coord.append(coord)
                        pcel_species.append(all_species[i])
                struc = Structure(lattice=pcel_latt, species=pcel_species,
                                  coords=pcel_coord, coords_are_cartesian=False)
            else:
                pcel_latt = Lattice(scel_latt, pbc=pbc[ndimen])
                pcel_coord = all_coord # Cartesian!
                pcel_species = all_species
                struc = Structure(lattice=pcel_latt, species=pcel_species,
                                  coords=pcel_coord, coords_are_cartesian=True)

            structures.append(struc)
            idx_line += 1
        else:
            idx_line += 1

    if structures == []:
        raise Exception('Valid structure not found.')
    elif len(structures) > 1: # QHA / HA + PREOPTGEOM, the first entry is pre-optimized geometry
        structures = structures[1:]

    return structures


class Phonopy():
    """
    The convertor between Phonopy and CRYSTALpytools file formats
    """
    @classmethod
    def read_structure(cls, file):
        """
        Read geometry from `Phonopy <https://phonopy.github.io/phonopy/>`_
        band.yaml or phonopy.yaml or phonopy_disp.yaml files.

        Args:
            file (str): Phonopy yaml file

        Returns:
            struc (Pymatgen Structure)

        :raise Exception: If the length unit in yaml file is neither 'au' nor 'angstrom'.
        """
        import yaml
        import numpy as np
        from units import au_to_angstrom
        #from CRYSTALpytools.units import au_to_angstrom
        from pymatgen.core.structure import Structure

        struc_file = open(file, 'r')
        data = yaml.safe_load(struc_file)
        struc_file.close()

        # Get unit
        try: # band.yaml
            len_unit = data['length_unit']
        except KeyError: # phonopy.yaml
            len_unit = data['physical_unit']['length']

        if len_unit == 'angstrom':
            unit_len = 1.0
        elif len_unit == 'au':
            unit_len = au_to_angstrom(1.0)
        else:
            raise Exception("Unknown length unit. Available options: au, angstrom.")

        # Get structure
        spec = []
        coord = []
        try: # band.yaml
            latt = np.array(data['lattice'], dtype=float) * unit_len
            for idx_a, atom in enumerate(data['points']):
                spec.append(atom['symbol'])
                coord.append(atom['coordinates'])
        except KeyError: # phonopy.yaml
            latt = np.array(data['primitive_cell']['lattice'], dtype=float) * unit_len
            for idx_a, atom in enumerate(data['primitive_cell']['points']):
                spec.append(atom['symbol'])
                coord.append(atom['coordinates'])

        struc = Structure(lattice=latt, species=spec, coords=coord)

        return struc

    @classmethod
    def read_frequency(cls, file, q_id=None, q_coord=None):
        """
        Read phonon frequency from `Phonopy <https://phonopy.github.io/phonopy/>`_
        band.yaml or qpoints.yaml files. Frequency units must be THz (default
        of Phonopy).

        Args:
            file (str): Phonopy yaml file
            q_id (list[int]): Specify the id (from 0) of q points to be read.
                nqpoint\*1 list.
            q_coord (list[list]): Specify the coordinates of q points to be
                read. nqpoint\*3 list.

        ``q_id`` and ``q_coord`` should not be set simultaneously. If set,
        ``q_id`` takes priority and ``q_coord`` is ignored. If both are none,
        all the points will be read.

        Returns:
            qpoint (list): natom\*2 list. 1st element: 3\*1 array. Fractional
                coordinates of q points; 2nd element: float. Weight
            frequency (array): nqpint\*nmode array. Phonon frequency in THz.

        :raise Exception: If (some of) q point is not found.
        """
        import yaml
        import numpy as np
        import warnings

        phono_file = open(file, 'r', errors='ignore')
        data = yaml.safe_load(phono_file)
        phono_file.close()

        if q_id == None and q_coord == None:
            nqpoint = data['nqpoint']
            qinfo = np.array(range(nqpoint), dtype=int)
        elif q_id != None:
            qinfo = np.array(q_id, dtype=int)
            nqpoint = len(qinfo)
        elif q_id == None and q_coord != None:
            qinfo = np.array(q_coord, dtype=float)
            nqpoint = len(qinfo)

        natom = int(len(data['phonon'][0]['band']) / 3)

        qpoint = [[np.zeros([3, 1]), 1 / nqpoint] for i in range(nqpoint)]
        frequency = np.zeros([nqpoint, 3 * natom])
        # Read phonon
        real_q = 0
        for idx_p, phonon in enumerate(data['phonon']):
            if real_q == nqpoint:
                break

            if len(qinfo.shape) == 1: # q_id and all q points
                if idx_p == qinfo[real_q]:
                    qpoint[real_q][0] = np.array(phonon['q-position'])
                    frequency[real_q, :] = np.array([i['frequency'] for i in phonon['band']])
                    real_q += 1
                else:
                    continue
            else: # q_coord
                coord = np.array(phonon['q-position'])
                if np.linalg.norm(qinfo[real_q] - coord) < 1e-4:
                    qpoint[real_q][0] = coord
                    frequency[real_q, :] = np.array([i['frequency'] for i in phonon['band']])
                    real_q += 1
                else:
                    continue

        if real_q < nqpoint:
            raise Exception('Some q points are missing from the yaml file.')

        return qpoint, frequency

    @classmethod
    def write_force_constants(cls, hessfile='HESSFREQ.DAT', phonopyfile='FORCE_CONSTANTS'):
        """
        Write Phonopy/VASP FORCE_CONSTANTS file by CRYSTAL HESSFREQ.DAT file.

        For example, to convert the calculation 'example' with a 4\*4\*4
        supercelland get phonon frequencies at Gamma point, use the following
        code:

        .. code-block::

            >>> from CRYSTALpytools.thermodynamics import Phonopy
            >>> Phonopy.write_force_constants(hessfile='example.HESSFREQ')
            >>> phonopy --crystal --qpoints='0 0 0' -c example.out --dim='4 4 4' --readfc

        Args:
            hessfile (str): The HESSFREQ.DAT file
            phonopyfile (str): The output name

        """
        import re
        import numpy as np
        from units import H_to_eV, angstrom_to_au
        #from CRYSTALpytools.units import H_to_eV, angstrom_to_au

        # Note: Phonopy requires mass unweighted Hessian
        # Read hessfreq.dat
        file = open(hessfile, 'r')
        data = file.read()
        file.close()

        hess = np.array(data.strip().split(), dtype=float)
        natom = int((len(hess) / 9)**0.5)

        hess = np.reshape(hess, [3*natom, 3*natom], order='F')
        hess = angstrom_to_au(angstrom_to_au(H_to_eV(hess))) # Hartree.Bohr^-2 to eV.Angstrom^-2
        # Symmstrize Hessian with its lower half - Important. To address the print issue of HESSFREQ.DAT
        for i in range(3*natom):
            for j in range(i+1, 3*natom):
                hess[i, j] = hess[j, i]

        # Write force_constants
        file = open(phonopyfile, 'w')
        file.write('%4i%4i\n' % (natom, natom))
        for i in range(natom):
            for j in range(natom):
                file.write('%4i%4i\n' % (i + 1, j + 1))
                dynamic = hess[int(3 * i):int(3 * i + 3), int(3 * j):int(3 * j + 3)]
                for d in dynamic:
                    file.write('%22.15f%22.15f%22.15f\n' % (d[0], d[1], d[2]))

        file.close()

class Output():
    """
    Deal with output data file
    """
    @classmethod
    def write_HA_result(cls, ha):
        """
        Write harmonic phonon information.

        Args:
            ha (Harmonic): :code:`CRYSTALpytools.thermodynamic.Harmonic` object
        """
        import scipy.constants as scst
        from units import kjmol_to_H
        #from CRYSTALpytools.units import kjmol_to_H

        file = open(ha.filename, 'w')
        file.write('%21s%20.9e%15s%20.12e%s\n' %
                   ('# DFT TOTAL ENERGY = ', kjmol_to_H(ha.edft),
                    ' Hartree     = ', ha.edft, ' kJ/mol'))
        file.write('%21s%20.4f%15s%20.4f%s\n' %
                   ('# CELL VOLUME      = ', ha.volume,
                    ' Angstrom^3  = ', ha.volume * scst.Avogadro * 1e-24, ' cm^3/mol'))
        file.write('%s\n' % '# LATTICE PARAMETERS (ANGSTROM, DEGREE)')
        file.write('%12s%12s%12s%12s%12s%12s\n' % ('A', 'B', 'C',
                                                   'ALPHA', 'BETA', 'GAMMA'))
        file.write('%12.4f%12.4f%12.4f%12.4f%12.4f%12.4f\n\n' %
                   (ha.structure.lattice.parameters[0:6]))

        for q in range(ha.nqpoint):
            file.write('%-40s%5i\n\n' %
                       ('# HARMONIC THERMODYNAMICS AT QPOINT #', q))
            file.write('%s%20.12e%s\n\n' %
                       ('## ZERO POINT ENERGY = ', ha.zp_energy[q], ' kJ/mol'))
            file.write('%s\n\n' % '## TEMPERATURE DEPENDENT PROPERTIES')
            file.write('%8s%20s%20s%20s%20s\n' %
                       ('T(K)', 'U_vib(kJ/mol)', 'Entropy(J/mol*K)',
                        'C_V(J/mol*K)', 'Helmholtz(kJ/mol)'))
            for t, tempt in enumerate(ha.temperature):
                file.write('%8.2f%20.12e%20.12e%20.12e%20.12e\n' %
                           (tempt, ha.u_vib[q, t], ha.entropy[q, t], ha.c_v[q, t], ha.helmholtz[q, t]))

            file.write('\n')
            for idx_p, gibbs_p in enumerate(ha.gibbs[q]):
                file.write('%s%8.2f%s\n\n' % ('## GIBBS FREE ENERGY AT', ha.pressure[idx_p], ' GPa'))
                file.write('%8s%20s\n' % ('T(K)', 'Gibbs(kJ/mol)'))
                for idx_t, gibbs_t in enumerate(gibbs_p):
                    file.write('%8.2f%20.12e\n' % (ha.temperature[idx_t], gibbs_t))
                file.write('\n')
            file.write('\n')

        file.write('\n')
        file.close()

        return

    @classmethod
    def write_QHA_combinedata(cls, qha):
        """
        Write QHA combined phonon information.

        Args:
            qha (Quasi_harmonic): :code:`CRYSTALpytools.thermodynamic.Quasi_harmonic` object
        """
        file = open(qha.filename, 'w')
        file.write('%s\n' % '# COMBINED QHA DATA')
        file.write('%s' % '## SAMPLED VOLUMES(ANGSTROM^3) = ')
        for v in qha.combined_volume:
            file.write('%16.4e' % v)

        file.write('\n')

        file.write('%s' % '## DFT TOTAL ENERGIES(KJ/MOL CELL) = ')
        for e in qha.combined_edft:
            file.write('%16.6e' % e)

        file.write('\n\n')

        file.write('%s\n\n' % '## COMBINED MODES')
        for idx_q, mode_q in enumerate(qha.combined_mode):
            file.write('%s%8i\n\n' % ('### FREQUENCIES AT QPOINT #', idx_q))
            for mode in mode_q:
                file.write('%8s%22s%22s\n' % ('Mode #', 'Volume(Angstrom^3)', 'Frequency(THz)'))
                for i in range(qha.ncalc):
                    if i == 0:
                        file.write('%8i' % mode.rank)
                    else:
                        file.write('%8s' % '')

                    file.write('%22.4f%22.4f\n' % (mode.volume[i], mode.frequency[i]))
                file.write('\n')
            file.write('\n')

        file.close()
        return

    @classmethod
    def write_QHA_sortphonon(cls, qha, close_overlap):
        """
        Write QHA phonon sort information.

        Args:
            qha (Quasi_harmonic): :code:`CRYSTALpytools.thermodynamic.Quasi_harmonic`
                object.
            close_overlap (array[int]): nqpoint\*nmode_ref\*ncalc\*nmode_sort.
                Number of close overlaps.
        """
        import numpy as np

        nmode = len(qha.combined_mode[0])
        file = open(qha.filename, 'a+')
        file.write('%s\n\n' % '## CLOSE OVERLAPS OF PHONON FREQUENCIES')
        for idx_q, mode_q in enumerate(qha.combined_mode):
            file.write('%30s%8i\n\n' % ('### CLOSE OVERLAPS AT QPOINT #', idx_q))
            file.write('%s%8i\n\n' % ('    Total number of overlaps =', np.sum(close_overlap[idx_q])))
            file.write('%6s%s\n' % ('', 'Mode and calc order starts from 1. Calc number in ascending order of volume'))
            file.write('%16s%16s%16s%16s\n' %
                       ('Ref_mode #', 'Sort_mode #', 'Ref_Calc #', 'Sort_Calc #'))
            for idx_mref, mode in enumerate(mode_q):
                if np.sum(close_overlap[idx_q, idx_mref]) < 1:
                    continue
                for idx_csort in range(1, qha.ncalc):
                    for idx_msort in range(nmode):
                        if close_overlap[idx_q, idx_mref, idx_csort, idx_msort] != 0:
                            file.write('%16i%16i%16i%16i\n' %
                                       (idx_mref + 1, idx_msort + 1, idx_csort, idx_csort + 1))
            file.write('\n')

        file.close()
        return

    @classmethod
    def write_QHA_eosfit(cls, qha, eos, method):
        """
        Write QHA phonon eos fit information.

        Args:
            qha (Quasi_harmonic): :code:`CRYSTALpytools.thermodynamic.Quasi_harmonic`
                object.
            order (list[int]): Orders of polynomials
            method (str): Name of EoS used.
        """
        import scipy.constants as scst

        file = open(qha.filename, 'a+')
        file.write('%s%s\n' % ('# EQUATION OF STATES FITTED FOR ELECTRON TOTAL ENERGY: ', method))
        file.write('%s\n' % '  Electron total energy is fitted as the function of volume, of which the')
        file.write('%s\n\n' % '  formalism is given by equation of states.')
        file.write('%16s%16s%12s%12s\n' % ('E0(kJ/mol)', 'V0(Angstrom^3)', 'B0(GPa)', 'B1'))
        file.write('%16.4f%16.4f%12.4f%12.4f\n' % (eos.e0, eos.v0, eos.b0 * 1e24 / scst.Avogadro, eos.b1))
        file.write('\n')
        file.close()
        return

    @classmethod
    def write_QHA_polyfit(cls, qha, order, rsquare_q):
        """
        Write QHA phonon polynomial fit information.

        Args:
            qha (Quasi_harmonic): :code:`CRYSTALpytools.thermodynamic.Quasi_harmonic`
                object.
            order (list[int]): List of polynomial orders.
            rsquare_q (array): Nqpoint\*Norder list. Overall goodness at a q point.
        """
        file = open(qha.filename, 'a+')
        file.write('%s\n' % '# POLYNOMIAL FIT OF MODE FREQUENCY')
        file.write('%s\n' % '  Frequency of each vibrational mode is fitted as the polynomial function of')
        file.write('%s\n' % '  volume, with specified orders of power.')
        for idx_q, mode_q in enumerate(qha.combined_mode):
            file.write('%8s%8s%12s%s\n' %
                       ('Mode #', 'Order', 'R^2', '  Coeff low to high (Constant term = 0)'))
            for mode in mode_q:
                for idx_od, od in enumerate(order):
                    if idx_od == 0:
                        file.write('%8i' % mode.rank)
                    else:
                        file.write('%8s' % '')
                    file.write('%8i%10.6f%2s' % (od, mode.poly_fit_rsqaure[od], ''))
                    for idx_c, c in enumerate(mode.poly_fit[od].convert().coef):
                        if idx_c == 0:
                            continue
                        file.write('%12.4e' % c)
                    file.write('\n')
                file.write('\n')

            # Overall performance
            file.write('%s%8i\n' % ('## POLYNOMIAL FIT GOODNESS AT QPOINT #', idx_q))
            file.write('%8s%12s\n' % ('Order', 'R^2'))
            for idx_od, od in enumerate(order):
                file.write('%8i%12.6f\n' % (od, rsquare_q[idx_q, idx_od]))
            file.write('\n')

        file.write('%s%8i\n\n' % ('## THE OPTIMAL ORDER OF POLYNOMIAL =', qha.fit_order))
        file.close()

        return

    @classmethod
    def write_QHA_thermofreq(cls, qha, min_method, volume_bound):
        """
        Write QHA thermodynamics information (frequency fitting).

        Args:
            qha (Quasi_harmonic): :code:`CRYSTALpytools.thermodynamic.Quasi_harmonic`
                object.
        """
        file = open(qha.filename, 'a+')
        file.write('%s\n' % '# QHA THERMODYNAMIC PROPERTIES - FREQUENCY')
        file.write('%s\n\n' % '  QHA thermodynamic properties by explicitly fitting frequencies.')
        file.write('%s%6i\n' % ('## FREQUENCY POLYNOMIAL ORDER: ', qha.fit_order))
        file.write('%s%s\n' % ('## EQUILIBRIUM VOLUME MINIMISATION: ', min_method))
        file.write('%s%s\n' % ('## HELMHOLTZ FREE ENERGY EOS: ', qha.e0_eos_method))
        if volume_bound != None:
            file.write('%s\n' %
                       ('## CONSTRAINED VOLUME MINIMIZATION LAUNCHED. VOLUME BOUNDARIES (UNIT: ANGSTROM^3):'))
            file.write('%s%8.2f%s%8.2f\n\n' % 
                       ('## LOWER: ', volume_bound[0], ' UPPER: ', volume_bound[1]))

        for idx_p, press in enumerate(qha.pressure):
            file.write('%s%6.2f%s\n\n' % ('## THERMODYNAMIC PROPERTIES AT ', press, '  GPa'))
            file.write('%10s%20s%20s%20s%20s%20s\n' %
                       ('T(K)', 'Vol(Angstrom^3)', 'Helmholtz(kJ/mol)',
                        'Gibbs(kJ/mol)', 'Entropy(J/mol*K)', 'C_V(J/mol*K)'))
            for idx_t, tempt in enumerate(qha.temperature):
                file.write('%10.2f%20.4f%20.8e%20.8e%20.8e%20.8e\n' %
                           (tempt, qha.volume[idx_p, idx_t],
                            qha.helmholtz[idx_p, idx_t],
                            qha.gibbs[idx_p, idx_t],
                            qha.entropy[idx_p, idx_t],
                            qha.c_v[idx_p, idx_t])
                          )
            file.write('\n')

        file.write('\n')
        file.close()

        return

    @classmethod
    def write_QHA_thermogru(cls, qha):
        """
        Write QHA thermodynamics information (Grüneisen fitting).

        Args:
            qha (Quasi_harmonic): :code:`CRYSTALpytools.thermodynamic.Quasi_harmonic`
                object.
        """
        file = open(qha.filename, 'a+')
        file.write('%s\n' % '# QHA THERMODYNAMIC PROPERTIES - GRÜENEISEN MODEL')
        file.write('%s\n\n' % '  Linear dependency of frequency with volume is assumed.')
        for idx_p, p in enumerate(qha.pressure):
            file.write('%s%6.2f%s\n\n' % ('## GRÜENEISEN THERMODYNAMICS AT ', p, '  GPa'))
            file.write('%10s%10s%20s%20s%20s%20s%20s\n' %
                        ('T(K)', 'GRÜ PARAM','alpha_VGRÜ(K^-1)', 'C_v(J/mol*K)',
                         'C_pGRÜ(J/mol*K)', 'K_T(GPa)', 'K_SGRÜ(GPa)'))
            for idx_t, t in enumerate(qha.temperature):
                file.write('%10.1f%10.4f%20.8e%20.8e%20.8e%20.8e%20.8e\n' %
                            (t,
                             qha.gruneisen[idx_p, idx_t],
                             qha.alpha_vgru[idx_p, idx_t],
                             qha.c_v[idx_p, idx_t],
                             qha.c_pgru[idx_p, idx_t],
                             qha.k_t[idx_p, idx_t],
                             qha.k_sgru[idx_p, idx_t])
                          )
            file.write('\n')

        file.write('\n')
        file.close()

        return

    @classmethod
    def write_QHA_thermoeos(cls, qha):
        """
        Write QHA thermodynamics information (EOS fitting).

        Args:
            qha (Quasi_harmonic): :code:`CRYSTALpytools.thermodynamic.Quasi_harmonic`
                object.
        """
        file = open(qha.filename, 'a+')
        file.write('%s\n' % '# QHA THERMODYNAMIC PROPERTIES - EOS FIT')
        file.write('%s\n\n' % '  Thermodynamic properties obtained by overall fitting of equation of states.')
        file.write('%s%s\n' % ('## EQUATION OF STATES: ', qha.fe_eos_method))
        file.write('%s%i\n' % ('## G(T) POLYNOMIAL ORDER: ', qha.fit_order))
        file.write('%s\n' %
                   '  WARNING: Entropy at low temperature is probably inaccurate due to the poor fitting of G(T) near 0K.')
        for idx_p, press in enumerate(qha.pressure):
            file.write('%s%6.2f%s\n\n' % ('## THERMODYNAMIC PROPERTIES AT ', press, '  GPa'))
            file.write('%10s%20s%20s%20s%20s%20s\n' %
                        ('T(K)', 'Vol(Angstrom^3)', 'Helmholtz(kJ/mol)',
                         'Gibbs(kJ/mol)', 'Entropy(J/mol*K)', 'C_p(J/mol*K)'))
            for idx_t, tempt in enumerate(qha.temperature):
                file.write('%10.1f%20.4f%20.8e%20.8e%20.8e%20.8e\n' %
                               (tempt,
                                qha.volume[idx_p, idx_t],
                                qha.helmholtz[idx_p, idx_t],
                                qha.gibbs[idx_p, idx_t],
                                qha.entropy[idx_p, idx_t],
                                qha.c_p[idx_p, idx_t])
                          )
            file.write('\n')

        file.write('\n')
        file.close()

        return

    @classmethod
    def write_expansion_vol(cls, qha, fit_order, fit_rs):
        """
        Write volumetric thermal expansions.

        Args:
            qha (Quasi_harmonic): :code:`CRYSTALpytools.thermodynamic.Quasi_harmonic`
                object.
            fit_order (int): The order of polynomial used for fitting.
            fit_rs (list[float]): R^2 of fitting. nPressure\*1 list.
        """
        import numpy as np

        idx_tmin = np.argmin(qha.temperature)
        tmin = qha.temperature[idx_tmin]

        file = open(qha.filename, 'a+')
        file.write('%s\n' % '# THERMAL EXPANSION COEFFICIENTS')
        file.write('%s\n\n' % '  To get thermal expansion coefficients, equilibrium volumes are fit as polynomial function of temperature at constant pressure.')
        file.write('%s%i\n' % ('## OPTIMAL ORDER OF POLYNOMIAL: ', fit_order))
        for idx_p, p in enumerate(qha.pressure):
            file.write('%s%6.2f%s%6.4f\n\n' %
                        ('## EXPANSIONS AT ', p, '  GPa, R^2 = ', fit_rs[idx_p]))
            file.write('%10s%20s%20s\n' %
                       ('T(K)', 'Vol(Angstrom^3)', 'alpha_V(K^-1)'))
            vmin = qha.volume[idx_p, idx_tmin]
            for idx_t, t in enumerate(qha.temperature):
                file.write('%10.1f%20.4f%20.8e\n' %
                            (t, vmin + qha.vol_fit[idx_p](t - tmin), qha.alpha_v[idx_p, idx_t]))
            file.write('\n')

        file.write('\n')
        file.close()

        return

    @classmethod
    def write_bulk_modulus(cls, qha, adiabatic):
        """
        Write bulk moduli.

        Args:
            qha (Quasi_harmonic): :code:`CRYSTALpytools.thermodynamic.Quasi_harmonic`
                object.
             adiabatic (bool): Whether the adiabatic bulk modulus :math:`K_{S}`
                 is fitted.
        """
        file = open(qha.filename, 'a+')
        file.write('%s\n' % '# QHA BULK MODULI')
        file.write('%s\n\n' % '  Isothermal and adiabatic bulk moduli.')
        for idx_p, p in enumerate(qha.pressure):
            file.write('%s%6.2f%s\n\n' % ('## BULK MODULI K_T and K_S AT ', p, '  GPa'))
            if adiabatic == True:
                file.write('%10s%20s%20s\n' % ('T(K)', 'K_T(GPa)', 'K_S(GPa)'))
                for idx_t, t in enumerate(qha.temperature):
                    file.write('%10.1f%20.8e%20.8e\n' %
                               (t, qha.k_t[idx_p, idx_t], qha.k_s[idx_p, idx_t]))
                file.write('\n')
            else:
                file.write('%10s%20s\n' % ('T(K)', 'K_T(GPa)'))
                for idx_t, t in enumerate(qha.temperature):
                    file.write('%10.1f%20.8e\n' % (t, qha.k_t[idx_p, idx_t]))
                file.write('\n')

        file.write('\n')
        file.close()

        return

    @classmethod
    def write_specific_heat(cls, qha):
        """
        Write bulk moduli.

        Args:
            qha (Quasi_harmonic): :code:`CRYSTALpytools.thermodynamic.Quasi_harmonic`
                object.
        """
        file = open(qha.filename, 'a+')
        file.write('%s\n' % '# QHA SPECIFIC HEAT')
        file.write('%s\n\n' % '  Constant volume and pressure specific heat.')
        for idx_p, p in enumerate(qha.pressure):
            file.write('%s%6.2f%s\n\n' % ('## SPECIFIC HEAT C_V and C_P AT ', p, '  GPa'))
            file.write('%10s%20s%20s\n' % ('T(K)', 'C_v(J/mol*K)', 'C_p(J/mol*K)'))
            for idx_t, t in enumerate(qha.temperature):
                file.write('%10.1f%20.8e%20.8e\n' % (t, qha.c_v[idx_p, idx_t], qha.c_p[idx_p, idx_t]))
            file.write('\n')

        file.write('\n')
        file.close()

        return

    @classmethod
    def write_expansion_latt(cls, qha, e_err, fit_order, r_square):
        """
        Write linear expansion information.

        Args:
            qha (Quasi_harmonic): :code:`CRYSTALpytools.thermodynamic.Quasi_harmonic`
                object.
            e_err (array): RMS deviation of Gibbs free energy at T and p.
            fit_order (array): The order of polynomials used for fitting
                lattice parameter.
            r_square (array): R^2 of fitting. nLatt\*nPress
        """
        import numpy as np

        idx_tmin = np.argmin(qha.temperature)
        tmin = qha.temperature[idx_tmin]
        nlatt = qha.lattice.shape[2]
        nalpha = qha.alpha_latt.shape[2]

        file = open(qha.filename, 'a+')
        file.write('%s\n' % '# LINEAR THERMAL EXPANSION FIT')
        file.write('%s\n' % '  Equilibrium lattices parameters are fitted with HA geometries.')
        file.write('%s\n\n' % '  Lattice parameters at constant pressures are fitted as polynomial functions.')
        for idx_p, p in enumerate(qha.pressure):
            file.write('%s%6.2f%s\n\n' % ('## EQ. LATTICE AT ', p, '  GPa'))
            file.write('%10s' % 'T(K)')
            for i in range(nlatt):
                file.write('%18s%2i' % ('Latt. Param. -', i + 1))
            file.write('%20s\n' % 'RMSD (kJ/mol)')
            for idx_t, tempt in enumerate(qha.temperature):
                file.write('%10.2f' % tempt)
                for i in range(nlatt):
                    file.write('%20.6f' % qha.lattice[idx_p, idx_t, i])
                file.write('%20.6f\n' % e_err[idx_p, idx_t])
            file.write('\n')
            file.write('%s%6.2f%s\n\n' % ('## LATTICE EXPANSION AT ', p, '  GPa'))
            for i in range(nlatt):
                file.write('%s%8i\n' % ('  Latt. Param. No. =', i + 1))
                file.write('%s%8i\n' % ('  Order of fitting =', fit_order[i]))
                file.write('%s%8.4f\n\n' % ('  R^2 of fitting   =', r_square[i, idx_p]))
            file.write('%10s' % 'T(K)')
            for i in range(nalpha):
                file.write('%18s%2i' % ('alpha_l(K^-1) -', i + 1))
            file.write('\n')
            for idx_t, tempt in enumerate(qha.temperature):
                file.write('%10.2f' % tempt)
                for i in range(nlatt):
                    file.write('%20.8e' % qha.alpha_latt[idx_p, idx_t, i])
                file.write('\n')
            file.write('\n')

        file.write('\n')
        file.close()
        return
