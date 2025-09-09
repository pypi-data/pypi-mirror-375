#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes and methods of keywords used in 'crystal' input file (d12).
"""
from CRYSTALClear.base.inputbase import BlockBASE

class Crystal_inputBASE(BlockBASE):
    """
    The base class of Crystal_input class
    """

    def __init__(self):
        # Initialize the object to empty values
        self._block_bg = None  # Avoid empty bg and ed lines
        self._block_ed = None
        self._block_data = ''
        self._block_attr = ['geom', 'basisset', 'scf']

    @property
    def geom(self):
        if not hasattr(self, '_block_geom'):
            self.set_geom()
        return self._block_geom

    def set_geom(self, obj=None):
        """
        Geom subblock

        Args:
            obj (Geom | str): A block object of 'GEOM' submodule. Or a string
                in CRYSTAL d12 format.
        """
        from CRYSTALClear.base.crysd12 import Geom

        self._block_geom = Geom()
        if obj == None:  # Initialize block
            return
        elif type(obj) == str:
            if obj == '': # Clean data
                self._block_geom.clean_block()
            else:
                dimen_list = ['CRYSTAL\n', 'SLAB\n', 'POLYMER\n', 'MOLECULE\n',
                              'HELIX\n', 'EXTERNAL\n', 'DLVINPUT\n']
                title = obj.split('\n')[0]
                if title in dimen_list: # No title line
                    self._block_geom.analyze_text(obj)
                else: # Have title line
                    self._block_geom.title(title)
                    self._block_geom.analyze_text(obj)
        else:
            self._block_geom = obj

    @property
    def basisset(self):
        if not hasattr(self, '_block_basisset'):
            self.set_basisset()
        return self._block_basisset

    def set_basisset(self, obj=None):
        """
        Basis set subblock

        Args:
            obj (BasisSet | str): A block object of basis set submodule. Or a
                string in CRYSTAL d12 format
        """
        from CRYSTALClear.base.crysd12 import BasisSet

        self._block_basisset = BasisSet()
        if obj == None:  # Initialize block
            return
        elif type(obj) == str:
            if obj == '':# Clean data
                self._block_basisset.clean_block()
            else:
                self._block_basisset.analyze_text(obj)
        else:
            self._block_basisset = obj

    @property
    def scf(self):
        if not hasattr(self, '_block_scf'):
            self.set_scf()
        return self._block_scf

    def set_scf(self, obj=None):
        """
        SCF subblock

        Args:
            obj (SCF | str): A block object of SCF submodule. Or a string in
                CRYSTAL d12 format
        """
        from CRYSTALClear.base.crysd12 import SCF

        self._block_scf = SCF()
        if obj == None:  # Initialize block
            return
        elif type(obj) == str:
            if obj == '': # Clean data
                self._block_scf.clean_block()
            else:
                self._block_scf.analyze_text(obj)
        else:
            self._block_scf = obj

    def from_file(self, file):
        """
        Generate a CrystalInputBASE obj from a d12 file. A 'complete' d12 file
        with geometry, basis set and SCF blocks is suggested.
        """
        import re

        inp = open(file, 'r')
        data = inp.read()
        inp.close()
        data_lines = data.strip().split('\n')

        self.set_geom()
        self.set_basisset()
        self.set_scf()

        # Divide data into 3 blocks
        text = ['', '', '']
        # Case 1: No BASISSET keyword
        if 'BASISSET' not in data:
            geom_end = 1
            bs_end = 2
            end_counter = 0
            block_counter = 0
            subblock_key = ['OPTGEOM', 'FREQCALC',
                            'ANHARM', 'CPHF', 'CPKS', 'ELASTCON', 'EOS']
            for d in data_lines:
                d = d.strip()
                text[block_counter] += d + '\n'
                if d in subblock_key:
                    geom_end += 1
                    bs_end += 1
                elif 'END' in d:
                    end_counter += 1

                if end_counter == geom_end:
                    geom_end = -1
                    block_counter += 1
                elif end_counter == bs_end:
                    bs_end = -1
                    block_counter += 1
        # Case 2: BASISSET keyword
        else:
            self.basisset._block_ed = None
            self.geom._block_ed = None
            block_counter = 0
            for d in data_lines:
                d = d.strip()
                if d == 'BASISSET':
                    block_counter += 1
                    text[block_counter] += d + '\n'
                elif d in self.scf._block_key and block_counter == 1:  # Avoid same keywords. e.g. TOLDEE
                    block_counter += 1
                    text[block_counter] += d + '\n'
                else:
                    text[block_counter] += d + '\n'

        # Title line
        self.geom.title(data_lines[0])
        # The 0D geometry keyword 'MOLECULE' and the molecular crystal option 'MOLECULE'
        if 'MOLECULE' not in data_lines[1] and 'MOLECULE' in text[0]:
            text[0] = re.sub('MOLECULE', 'MOLEISO', text[0])

        self.geom.analyze_text(text[0])
        if 'BASISSET' not in data:
            self.basisset.from_string(text[1])
        else:
            self.basisset.analyze_text(text[1])
        self.scf.analyze_text(text[2])

        return self

    def to_file(self, file):
        """
        Write data to a file
        """
        out = open(file, 'w')
        # If objects are set separately, BASISSET might coincide with 'ENDGEOM'
        if 'BASISSET' in self.data and 'ENDGEOM' in self.data:
            self.geom._block_ed = ''
        out.write('%s' % self.data)
        out.close()


class Geom(BlockBASE):
    """
    Geometry block object
    """

    def __init__(self):
        self._block_bg = 'Generated by CRYSTALClear\n'  # Set title as bg label
        self._block_ed = 'ENDGEOM\n'
        self._block_data = ''
        self._block_dict = {  # The sequence of keywords should follow rules in the manual
            'CRYSTAL'   : '_basegeom',
            'SLAB'      : '_basegeom',
            'POLYMER'   : '_basegeom',
            'HELIX'     : '_basegeom',
            'MOLECULE'  : '_basegeom',
            'EXTERNAL'  : '_basegeom',
            'DLVINPUT'  : '_basegeom',
            'SUPERCEL'  : '_sp_matrix',
            'SUPERCELL' : '_sp_matrix',
            'SUPERCON'  : '_sp_matrix',
            'SCELCONF'  : '_sp_matrix',
            'SCELPHONO' : '_sp_matrix',
            'ATOMBSSE'  : '_atombsse',
            'ATOMDISP'  : '_atomdisp',
            'ATOMINSE'  : '_atominse',
            'ATOMORDE'  : '_atomorde',
            'ATOMREMO'  : '_atomremo',
            'MOLEISO'   : '_moleiso', # The original 'MOLECULE' option to isolate molecules
            'EXTPRT'    : '_extprt',
            'CIFPRT'    : '_cifprt',
            'CIFPRTSYM' : '_cifprtsym',
            'COORPRT'   : '_coorprt',
            'TESTGEOM'  : '_testgeom',
            'OPTGEOM'   : 'optgeom',  # Sub-block properties must be named without the initial underscore
            'FREQCALC'  : 'freqcalc',
        }
        key = list(self._block_dict.keys())
        attr = list(self._block_dict.values())
        self._block_key = sorted(set(key), key=key.index)
        self._block_attr = sorted(set(attr), key=attr.index)

    @property
    def data(self):
        """
        Settings in all the attributes are summarized here. Covers the data
        property in BlockBASE, to address the ambiguity of 'MOLECULE' keywords.
        """
        import re

        self.update_block()
        text = ''
        for i in [self._block_bg, self._block_data, self._block_ed]:
            if i == None:
                continue
            text += i

        return re.sub('MOLEISO', 'MOLECULE', text)

    def title(self, title='Generated by CRYSTALClear'):
        self._block_bg = '{}\n'.format(title)

    def crystal(self, IGR=None, latt=[], atom=[], IFLAG=0, IFHR=0, IFSO=0, origin=[]):
        """
        Define 'CRYSTAL' structure

        Args:
            sg (int): Space group number. Parameter IGR in the manual
            latt (list): Minimal set of crystallographic cell parameters
            atom (list): Natom \* 4 list of conventional atomic number and 3D 
                fractional coordinates.
            IFLAG (int): See the manual
            IFHR (int): See the manual
            IFSO (int): See the manual
            origin (list): *IFSO > 1* See the manual
        """
        if IGR == None:  # No entry. Return keyword
            self._basegeom = super(Geom, self).assign_keyword('CRYSTAL', [])
            return
        elif IGR == '':  # Clean data
            self._basegeom = super(Geom, self).assign_keyword('CRYSTAL', [], '')
            return

        if IFSO <= 1:
            shape = [3, 1]
            value = ['{:<3d}'.format(int(IFLAG)), '{:<3d}'.format(int(IFHR)), '{:<3d}'.format(int(IFSO)),
                     '{:<3d}'.format(int(IGR))]
        else:
            shape = [3, 3, 1]
            value = ['{:<3d}'.format(int(IFLAG)), '{:<3d}'.format(int(IFHR)), '{:<3d}'.format(int(IFSO)),
                     '{:<12.6f}'.format(origin[0]), '{:<12.6f}'.format(origin[1]), '{:<12.6f}'.format(origin[2]),
                     '{:<3d}'.format(int(IGR))]

        shape += [len(latt), ]
        value += ['{:<12.6f}'.format(i) for i in latt]

        # Format atoms - frac 12 digits, cart 16 digits
        atom = [['{:<4d}'.format(int(a[0])), '{0: 12.8f}'.format(a[1]),
                 '{0: 12.8f}'.format(a[2]), '{0: 12.8f}'.format(a[3])] for a in atom]
        atominput = super(Geom, self).set_list(len(atom), atom)
        shape += atominput[0]
        value += atominput[1]

        self._basegeom = super(Geom, self).assign_keyword('CRYSTAL', shape, value)

    def slab(self, IGR=None, latt=[], atom=[]):
        """
        Define 'SLAB' structure
        """
        if IGR == None:  # No entry. Return keyword
            self._basegeom = super(Geom, self).assign_keyword('SLAB', [])
            return
        elif IGR == '':  # Clean data
            self._basegeom = super(Geom, self).assign_keyword('SLAB', [], '')
            return

        shape = [1, ]
        value = ['{:<3d}'.format(int(IGR)), ]

        shape += [len(latt), ]
        value += ['{:<12.6f}'.format(i) for i in latt]

        # Format atoms - frac 12 digits, cart 16 digits
        atom = [['{:<4d}'.format(int(a[0])), '{0: 12.8f}'.format(a[1]),
                 '{0: 12.8f}'.format(a[2]), '{0: 16.8f}'.format(a[3])] for a in atom]
        atominput = super(Geom, self).set_list(len(atom), atom)
        shape += atominput[0]
        value += atominput[1]

        self._basegeom = super(Geom, self).assign_keyword('SLAB', shape, value)

    def polymer(self, IGR=None, latt=[], atom=[]):
        """
        Define 'POLYMER' structure
        """
        if IGR == None:  # No entry. Return keyword
            self._basegeom = super(Geom, self).assign_keyword('POLYMER', [])
            return
        elif IGR == '':  # Clean data
            self._basegeom = super(Geom, self).assign_keyword('POLYMER', [], '')
            return

        shape = [1, ]
        value = ['{:<3d}'.format(int(IGR)), ]

        shape += [len(latt), ]
        value += ['{:<12.6f}'.format(i) for i in latt]

        # Format atoms - frac 12 digits, cart 16 digits
        atom = [['{:<4d}'.format(int(a[0])), '{0: 12.8f}'.format(a[1]),
                 '{0: 16.8f}'.format(a[2]), '{0: 16.8f}'.format(a[3])] for a in atom]
        atominput = super(Geom, self).set_list(len(atom), atom)
        shape += atominput[0]
        value += atominput[1]

        self._basegeom = super(Geom, self).assign_keyword('POLYMER', shape, value)

    def helix(self, N1=None, N2=0, latt=[], atom=[]):
        """
        Define 'HELIX' structure

        Args:
            N1 (int): See the manual
            N2 (int): See the manual
        """
        if N1 == None:  # No entry. Return keyword
            self._basegeom = super(Geom, self).assign_keyword('HELIX', [])
            return
        elif N1 == '':  # Clean data
            self._basegeom = super(Geom, self).assign_keyword('HELIX', [], '')
            return

        shape = [2, ]
        value = ['{:<3d}'.format(int(N1)), '{:<3d}'.format(int(N2)), ]

        shape += [len(latt), ]
        value += ['{:<12.6f}'.format(i) for i in latt]

        # Format atoms - frac 12 digits, cart 16 digits
        atom = [['{:<4d}'.format(int(a[0])), '{0: 12.8f}'.format(a[1]),
                 '{0: 16.8f}'.format(a[2]), '{0: 16.8f}'.format(a[3])] for a in atom]
        atominput = super(Geom, self).set_list(len(atom), atom)
        shape += atominput[0]
        value += atominput[1]

        self._basegeom = super(Geom, self).assign_keyword('HELIX', shape, value)

    def molecule(self, IGR=None, atom=[]):
        """
        Define 'MOLECULE' structure
        """
        import warnings

        # The 0D geometry keyword 'MOLECULE' and the molecular crystal option 'MOLECULE'
        if hasattr(self, '_basegeom'):
            warnings.warn("Geometry definition exists. To launch the MOLECULE option that isolates molecules from lattice, use the 'self.moleiso' method.", stacklevel=2)

        if IGR == None:  # No entry. Return keyword
            self._basegeom = super(Geom, self).assign_keyword('MOLECULE', [])
            return
        elif IGR == '':  # Clean data
            self._basegeom = super(Geom, self).assign_keyword('MOLECULE', [], '')
            return

        shape = [1, ]
        value = ['{:<3d}'.format(int(IGR)), ]

        # Format atoms - frac 12 digits, cart 16 digits
        atom = [['{:<4d}'.format(int(a[0])), '{0: 16.8f}'.format(a[1]),
                 '{0: 16.8f}'.format(a[2]), '{0: 16.8f}'.format(a[3])] for a in atom]
        atominput = super(Geom, self).set_list(len(atom), atom)
        shape += atominput[0]
        value += atominput[1]

        self._basegeom = super(Geom, self).assign_keyword('MOLECULE', shape, value)

    def external(self, key='EXTERNAL'):
        """
        Define 'EXTERNAL' structure
        """
        self._basegeom = super(Geom, self).assign_keyword(key, [])

    def dlvinput(self, key='DLVINPUT'):
        """
        Define 'DLVINPUT' structure
        """
        self._basegeom = super(Geom, self).assign_keyword(key, [])

    def supercel(self, mx=None):
        """
        Supercell by 'SUPERCEL' keyword

        Args:
            mx (array | list | str): ndimen \* ndimen matrix, [] or ''
        """
        shape, value = super(Geom, self).set_matrix(mx)
        self._sp_matrix = super(Geom, self).assign_keyword('SUPERCEL', shape, value)

    def supercon(self, mx=None):
        """
        Supercell by 'SUPERCON' keyword
        """
        shape, value = super(Geom, self).set_matrix(mx)
        self._sp_matrix = super(Geom, self).assign_keyword('SUPERCON', shape, value)

    def scelconf(self, mx=None):
        """
        Supercell by 'SCELCONF' keyword
        """
        shape, value = super(Geom, self).set_matrix(mx)
        self._sp_matrix = super(Geom, self).assign_keyword('SCELCONF', shape, value)

    def scelphono(self, mx=None):
        """
        Supercell by 'SCELPHONO' keyword
        """
        shape, value = super(Geom, self).set_matrix(mx)
        self._sp_matrix = super(Geom, self).assign_keyword('SCELPHONO', shape, value)

    def atombsse(self, IAT=None, NSTAR=None, RMAX=None):
        self._atombsse = super(Geom, self).assign_keyword('ATOMBSSE', [3, ], [IAT, NSTAR, RMAX])

    def atomdisp(self, NDISP=None, atom=[]):
        """
        ATOMDISP keyword

        Args:
            NDISP (int): See manual
            atom (list): NDISP\*4 list. Including LB, DX, DY, DZ
        """
        shape, value = super(Geom, self).set_list(NDISP, atom)
        self._atomdisp = super(Geom, self).assign_keyword('ATOMDISP', shape, value)

    def atominse(self, NINS=None, atom=[]):
        """
        ATOMINSE keyword

        Args:
            NINS (int): See manual
            atom (list): NINS\*4 list. Including NA, X, Y, Z
        """
        shape, value = super(Geom, self).set_list(NINS, atom)
        self._atominse = super(Geom, self).assign_keyword('ATOMINSE', shape, value)

    def atomorde(self, key='ATOMORDE'):
        self._atomorde = super(Geom, self).assign_keyword(key, [])

    def atomremo(self, NL=None, atom=[]):
        """
        ATOMREMO keyword

        Args:
            NL (int): See manual
            atom (list): NL\*1 list. Including LB
        """
        shape, value = super(Geom, self).set_list(NL, atom)
        self._atomremo = super(Geom, self).assign_keyword('ATOMREMO', shape, value)

    def moleiso(self, NMOL=None, atom=[]):
        """
        .. note::

            Corresponds to the **option** MOLECULE to isolate molecules from
            lattice. Only the method's name is changed to avoid ambiguity with
            the one to set 0D geometry.

        Args:
            NMOL (int)
            atom (list[list[int]]): NMOL\*4 list. See CRYSTAL manual.
        """
        shape, value = super(Geom, self).set_list(NMOL, atom)
        self._moleiso = super(Geom, self).assign_keyword('MOLECULE', shape, value)

    def extprt(self, key='EXTPRT'):
        self._extprt = super(Geom, self).assign_keyword(key, [])

    def cifprt(self, key='CIFPRT'):
        self._cifprt = super(Geom, self).assign_keyword(key, [])

    def cifprtsym(self, key='CIFPRTSYM'):
        self._cifprtsym = super(Geom, self).assign_keyword(key, [])

    def coorprt(self, key='COORPRT'):
        self._coorprt = super(Geom, self).assign_keyword(key, [])

    def testgeom(self, key='TESTGEOM'):
        conflict = ['_block_optgeom', '_block_freqcalc', '_testgeom']
        super(Geom, self).clean_conflict('_testgeom', conflict)

        self._testgeom = super(Geom, self).assign_keyword(key, [])

    @property
    def optgeom(self):
        """
        Subblock object OPTGEOM
        """
        if not hasattr(self, '_block_optgeom'):
            self.set_optgeom()
        return self._block_optgeom

    def set_optgeom(self, obj=None):
        """
        Optgeom subblock

        Args:
            obj (Optgeom | str): A block object of 'OPTGEOM' submodule. Or a
                string in CRYSTAL d12 format
        """
        from CRYSTALClear.base.crysd12 import Optgeom

        conflict = ['_block_optgeom', '_block_freqcalc', '_testgeom']
        super(Geom, self).clean_conflict('_block_optgeom', conflict)

        self._block_optgeom = Optgeom()
        if obj == None:  # Initialize block
            return
        elif type(obj) == str:
            if obj == '': # Clean data
                self._block_optgeom.clean_block()
            else:
                self._block_optgeom.analyze_text(obj)
        else:
            self._block_optgeom = obj

    @property
    def freqcalc(self):
        """
        Subblock object FREQCALC
        """
        if not hasattr(self, '_block_freqcalc'):
            self.set_freqcalc()
        return self._block_freqcalc

    def set_freqcalc(self, obj=None):
        """
        Freqcalc subblock

        Args:
            obj (Freqcalc | str): A block object of 'FREQCALC' submodule. Or a
                string in CRYSTAL d12 format
        """
        from CRYSTALClear.base.crysd12 import Freqcalc

        conflict = ['_block_optgeom', '_block_freqcalc', '_testgeom']
        super(Geom, self).clean_conflict('_block_freqcalc', conflict)

        self._block_freqcalc = Freqcalc()
        if obj == None:  # Initialize block
            return
        elif type(obj) == str:
            if obj == '': # Clean data
                self._block_freqcalc.clean_block()
            else:
                self._block_freqcalc.analyze_text(obj)
        else:
            self._block_freqcalc = obj


class Optgeom(BlockBASE):
    """
    OPTGEOM block object
    """

    def __init__(self):
        self._block_bg = 'OPTGEOM\n'
        self._block_ed = 'ENDOPT\n'
        self._block_data = ''
        self._block_dict = {
            'FULLOPTG'    : '_opttype',
            'CELLONLY'    : '_opttype',
            'INTREDUN'    : '_opttype',
            'ITATOCEL'    : '_opttype',
            'CVOLOPT'     : '_opttype',
            'HESSIDEN'    : '_opthess',
            'HESSMOD1'    : '_opthess',
            'HESSMOD2'    : '_opthess',
            'HESSNUM'     : '_opthess',
            'TOLDEG'      : '_toldeg',
            'TOLDEX'      : '_toldex',
            'TOLDEE'      : '_toldee',
            'MAXCYCLE'    : '_maxcycle',
            'FRAGMENT'    : '_fragment',
            'RESTART'     : '_restart',
            'FINALRUN'    : '_finalrun',
            'EXTPRESS'    : '_extpress',
            'ALLOWTRUSTR' : '_usetrustr',
            'NOTRUSTR'    : '_usetrustr',
            'MAXTRADIUS'  : '_maxtradius',
            'TRUSTRADIUS' : '_trustradius',
            'ONELOG'      : '_printonelog',
            'NOXYZ'       : '_printxyz',
            'NOSYMMOPS'   : '_printsymmops',
            'PRINTFORCES' : '_printforces',
            'PRINTHESS'   : '_printhess',
            'PRINTOPT'    : '_printopt',
            'PRINT'       : '_print',
        }
        key = list(self._block_dict.keys())
        attr = list(self._block_dict.values())
        self._block_key = sorted(set(key), key=key.index)
        self._block_attr = sorted(set(attr), key=attr.index)

    def fulloptg(self, key='FULLOPTG'):
        self._opttype = super(Optgeom, self).assign_keyword(key, [])

    def cellonly(self, key='CELLONLY'):
        self._opttype = super(Optgeom, self).assign_keyword(key, [])

    def intredun(self, key='INTREDUN'):
        self._opttype = super(Optgeom, self).assign_keyword(key, [])

    def itatocel(self, key='ITATOCEL'):
        self._opttype = super(Optgeom, self).assign_keyword(key, [])

    def cvolopt(self, key='CVOLOPT'):
        self._opttype = super(Optgeom, self).assign_keyword(key, [])

    def hessiden(self, key='HESSIDEN'):
        self._opthess = super(Optgeom, self).assign_keyword(key, [])

    def hessmod1(self, key='HESSMOD1'):
        self._opthess = super(Optgeom, self).assign_keyword(key, [])

    def hessmod2(self, key='HESSMOD2'):
        self._opthess = super(Optgeom, self).assign_keyword(key, [])

    def hessnum(self, key='HESSNUM'):
        self._opthess = super(Optgeom, self).assign_keyword(key, [])

    def toldeg(self, TG=None):
        self._toldeg = super(Optgeom, self).assign_keyword('TOLDEG', [1, ], TG)

    def toldex(self, TX=None):
        self._toldex = super(Optgeom, self).assign_keyword('TOLDEX', [1, ], TX)

    def toldee(self, IG=None):
        self._toldee = super(Optgeom, self).assign_keyword('TOLDEE', [1, ], IG)

    def maxcycle(self, MAX=None):
        self._maxcycle = super(Optgeom, self).assign_keyword('MAXCYCLE', [1, ], MAX)

    def fragment(self, NL=None, LB=[]):
        """
        Args:
            NL (int | str): Number of atoms. See manual. Or ''
            LB (list[int]): Label of atoms. See manual
        """
        shape, value = super(Optgeom, self).set_list(NL, LB)
        self._fragment = super(Optgeom, self).assign_keyword('FRAGMENT', shape, value)

    def restart(self, key='RESTART'):
        self._restart = super(Optgeom, self).assign_keyword(key, [])

    def finalrun(self, ICODE=None):
        self._finalrun = super(Optgeom, self).assign_keyword('FINALRUN', [1, ], ICODE)

    def extpress(self, pres=None):
        self._extpress = super(Optgeom, self).assign_keyword('EXTPRESS', [1, ], pres)

    def allowtrustr(self, key='ALLOWTRUSTR'):
        self._usetrustr = super(Optgeom, self).assign_keyword(key, [])

    def notrustr(self, key='NOTRUSTR'):
        self._usetrustr = super(Optgeom, self).assign_keyword(key, [])

    def maxtradius(self, TRMAX=None):
        import warnings

        if hasattr(self, '_usetrustr'):
            if self._usetrustr == 'NOTRUSTR\n':
                warnings.warn("The pre-set 'NOTRUSTR' keyword will be removed.", stacklevel=2)
                self.notrustr('')
        self._maxtradius = super(Optgeom, self).assign_keyword('MAXTRADIUS', [1, ], TRMAX)

    def trustradius(self, TRADIUS=None):
        import warnings

        if hasattr(self, '_usetrustr'):
            if self._usetrustr == 'NOTRUSTR\n':
                warnings.warn("The pre-set 'NOTRUSTR' keyword will be removed.", stacklevel=2)
                self.notrustr('')
        self._trustradius = super(Optgeom, self).assign_keyword('TRUSTRADIUS', [1, ], TRADIUS)

    def onelog(self, key='ONELOG'):
        self._printonelog = super(Optgeom, self).assign_keyword(key, [])

    def noxyz(self, key='NOXYZ'):
        self._printxyz = super(Optgeom, self).assign_keyword(key, [])

    def nosymmops(self, key='NOSYMMOPS'):
        self._printsymmops = super(Optgeom, self).assign_keyword(key, [])

    def printforces(self, key='PRINTFORCES'):
        self._printforces = super(Optgeom, self).assign_keyword(key, [])

    def printhess(self, key='PRINTHESS'):
        self._printhess = super(Optgeom, self).assign_keyword(key, [])

    def printopt(self, key='PRINTOPT'):
        self._printopt = super(Optgeom, self).assign_keyword(key, [])

    def print(self, key='PRINT'):
        self._print = super(Optgeom, self).assign_keyword(key, [])


class Freqcalc(BlockBASE):
    """
    FREQCALC block object
    """

    def __init__(self):
        self._block_bg = 'FREQCALC\n'
        self._block_ed = 'ENDFREQ\n'
        self._block_data = ''
        self._block_dict = {  # The sequence of keywords should follow rules in the manual
            'NOOPTGEOM'  : '_nooptgeom',  # A tailored sub-block
            'PREOPTGEOM' : 'optgeom',  # A tailored sub-block
            'DISPERSION' : '_dispersion',
            'BANDS'      : '_bands',
            'NUMDERIV'   : '_numderiv',
            'STEPSIZE'   : '_stepsize',
            'RESTART'    : '_restart',
            'MODES'      : '_modes',
            'NOMODES'    : '_modes',
            'PRESSURE'   : '_pressure',
            'TEMPERAT'   : '_temperat',
        }
        key = list(self._block_dict.keys())
        attr = list(self._block_dict.values())
        self._block_key = sorted(set(key), key=key.index)
        self._block_attr = sorted(set(attr), key=attr.index)

    def nooptgeom(self, key='NOOPTGEOM'):
        conflict = ['_block_optgeom', '_nooptgeom']
        super(Freqcalc, self).clean_conflict('_nooptgeom', conflict)

        self._nooptgeom = super(Freqcalc, self).assign_keyword(key, [])

    @property
    def optgeom(self):
        try:
            return self._block_optgeom
        except AttributeError:
            raise AttributeError(
                "Attribute does not exist.  'preoptgeom' should be specified at first")

    def preoptgeom(self, obj=None):
        """
        Args:
            obj (Optgeom): An Optgeom block object
        """
        import warnings

        warnings.warn(
            "Keyword 'PREOPTGEOM' is launched. To set geometric optimization keywords, use 'self.optgeom' attribute.")

        conflict = ['_block_optgeom', '_nooptgeom']
        super(Freqcalc, self).clean_conflict('_block_optgeom', conflict)

        if obj == None:  # New obj
            self._block_optgeom = Optgeom()
            self._block_optgeom._block_bg = 'PREOPTGEOM\n'
            self._block_optgeom._block_ed = 'END\n'
        elif obj == '':
            self._block_optgeom.clean_block()
        else:
            self._block_optgeom = obj
            self._block_optgeom._block_bg = 'PREOPTGEOM\n'
            self._block_optgeom._block_ed = 'END\n'

    def dispersion(self, key='DISPERSION'):
        self._dispersion = super(Freqcalc, self).assign_keyword(key, [])

    def bands(self, ISS=None, NSUB=None, NLINE=None, points=[]):
        if ISS == None:
            self._bands = super(Freqcalc, self).assign_keyword('BANDS', [])
        elif ISS == '':
            self._bands = super(Freqcalc, self).assign_keyword('', [])
        else:
            shape, value = super(Freqcalc, self).set_list(NLINE, points)
            self._bands = super(Freqcalc, self).assign_keyword('BANDS', [2, ] + shape, [ISS, NSUB] + value)

    def modes(self, key='MODES'):
        self._modes = super(Freqcalc, self).assign_keyword(key, [])

    def nomodes(self, key='NOMODES'):
        self._modes = super(Freqcalc, self).assign_keyword(key, [])

    def numderiv(self, N=None):
        self._numderiv = super(Freqcalc, self).assign_keyword(
            'NUMDERIV', [1, ], N)

    def pressure(self, NP=None, P1=None, P2=None):
        self._pressure = super(Freqcalc, self).assign_keyword(
            'PRESSURE', [3, ], [NP, P1, P2])

    def restart(self, key='RESTART'):
        self._restart = super(Freqcalc, self).assign_keyword('RESTART', [])

    def stepsize(self, STEP=None):
        self._stepsize = super(Freqcalc, self).assign_keyword('NUMDERIV', [1, ], STEP)

    def temperat(self, NT=None, T1=None, T2=None):
        self._temperat = super(Freqcalc, self).assign_keyword('TEMPERAT', [3, ], [NT, T1, T2])


class BasisSet(BlockBASE):
    """
    Basis Set block object
    """

    def __init__(self):
        self._block_bg = ''
        self._block_ed = 'ENDBS\n'
        self._block_data = ''
        self._block_dict = {  # The sequence of keywords should follow rules in the manual
            'BASISSET' : '_basisset',
            'GHOSTS'   : '_ghosts',
        }
        key = list(self._block_dict.keys())
        attr = list(self._block_dict.values())
        self._block_key = sorted(set(key), key=key.index)
        self._block_attr = sorted(set(attr), key=attr.index)

    def basisset(self, NAME=None):
        self._basisset = super(BasisSet, self).assign_keyword(
            'BASISSET', [1, ], NAME)
        if NAME == '':
            self._block_ed = 'ENDBS\n'
        else: # Otherwise _block_bg and _block_ed = '', this block would be recoginzed as an empty block
            self._block_ed = None

    def from_bse(self, name, element, filename=None, append=False):
        """
        Download basis set definitions from `Basis Set Exchange <https://www.basissetexchange.org/>`_.

        Args:
            name (str): Basis set's name.
            element (list[str] | list[int] | list[list[str | int, int]]): List
                of elements, specified by either atomic number or label. When
                a nelement\*2 list is used, the second entry is recognized as
                conventional atomic numbers.
            filename (None | str): If not None, print basis set definitions to
                a text file
            append (bool): Whether to cover old entries. If the old entry
                contains 'BASISSET', it will be removed anyway.
        """
        from CRYSTALClear.base.basisset import BasisSetBASE

        self._check_bs(append)
        if type(element[0]) == list or type(element[0]) == tuple:
            element_real = [i[0] for i in element]
            zconv = [i[1] for i in element]
            bs_obj = BasisSetBASE.from_bse(name, element_real, zconv)
        else:
            bs_obj = BasisSetBASE.from_bse(name, element)

        self._basisset += bs_obj.data

        if filename != None:
            bs_obj.to_file(file=filename)

    def from_string(self, string, fmt='crystal', filename=None, append=False):
        """
        Basis set from a string

        Args:
            string (str): A line of string. Use '\\n' to break lines. The ending
                line '99 0' is needed but not 'END'.
            fmt (str): Format of basis set string. if not 'crystal', this
                method calls `Basis Set Exchange API <https://molssi-bse.github.io/basis_set_exchange/index.html>`_ to convert it.
            filename (None | str): See ``from_bse``
            append (bool): See ``from_bse``
        """
        from CRYSTALClear.base.basisset import BasisSetBASE

        self._check_bs(append)
        bs_obj = BasisSetBASE.from_string(string, fmt)
        self._basisset += bs_obj.data

        if filename != None:
            bs_obj.to_file(file=filename)

    def from_file(self, file, fmt='crystal', filename=None, append=False):
        """
        Basis set from a file

        Args:
            file (file): A formatted text file with basis set definitions. The
                ending line '99 0' is needed but not 'END'.
            fmt (str): Format of basis set string. if not 'crystal', this
                method calls `Basis Set Exchange API <https://molssi-bse.github.io/basis_set_exchange/index.html>`_ to convert it.
            filename (None | str): See ``from_bse``
            append (bool): See ``from_bse``
        """
        from CRYSTALClear.base.basisset import BasisSetBASE

        self._check_bs(append)
        bs_obj = BasisSetBASE.from_file(file, fmt)
        self._basisset += bs_obj.data

        if filename != None:
            bs_obj.to_file(file=filename)

    def from_obj(self, bs_obj, filename=None, append=False):
        """
        Define basis set from a BasisSetBASE object.

        Args:
            bs_obj (BasisSetBASE): A CRYSTALClear.base.basisset.BasisSetBASE
                object.
            filename (None | str): See ``from_bse``
            append (bool): See ``from_bse``
        """
        self._check_bs(append)
        self._basisset += bs_obj.data

        if filename != None:
            bs_obj.to_file(file=filename)

    def _check_bs(self, append):
        """
        Check basis set definitions. Not an independent method that designed to
        be called.
        """
        import warnings
        import re

        if hasattr(self, '_basisset') and append == False:
            warnings.warn('The previous basis set will be erased.', stacklevel=2)
            self._basisset = ''
            if 'BASISSET' in self._basisset:
                self._block_ed = 'ENDBS\n'
        elif hasattr(self, '_basisset') and append == True:
            if 'BASISSET' in self._basisset:
                warnings.warn("'BASISSET' detected. The previous definition will be erased anyway.",
                              stacklevel=2)
                self._basisset = ''
                self._block_ed = 'ENDBS\n'
            else:
                self._basisset = re.sub(r'99\s+0\n$', "", self._basisset)
        else:
            self._basisset = ''

    def ghosts(self, NA=None, LA=[]):
        shape, value = super(BasisSet, self).set_list(NA, LA)
        self._ghosts = super(BasisSet, self).assign_keyword(
            'GHOSTS', shape, value)


class SCF(BlockBASE):
    """
    SCF block object
    """

    def __init__(self):
        self._block_bg = ''
        self._block_ed = 'ENDSCF\n'
        self._block_data = ''
        self._block_dict = {  # The sequence of keywords should follow rules in the manual
            'FIXINDEX' : '_fixbg',
            'DFT'      : 'dft',  # DFT sub-block
            'DFTD3'    : 'dftd3',  # DFTD3 sub-block
            'GCP'      : 'gcp',  # GCP sub-block
            'GCPAUTO'  : '_gcpauto',
            'SMEAR'    : '_smear',
            'ATOMSPIN' : '_atomspin',
            'TOLDEE'   : '_toldee',
            'DIIS'     : '_diis',
            'NODIIS'   : '_diis',
            'DIISALLK' : '_diisallk',
            'HISTDIIS' : '_histdiis',
            'PRTDIIS'  : '_prtdiis',
            'MAXCYCLE' : '_maxcycle',
            'GUESSP'   : '_guessp',
            'FMIXING'  : '_fmixing',
            'NOBIPOLA' : '_nobipola',
            'NOBIPCOU' : '_nobipcou',
            'NOBIPEXC' : '_nobipexc',
            'TOLINTEG' : '_tolinteg',
            'LDREMO'   : '_ldremo',
            'BIPOSIZE' : '_biposize',
            'EXCHSIZE' : '_exchsize',
            'SHRINK'   : '_shrink',
            'EXCHANGE' : '_exchange',
            'POSTSCF'  : '_postscf',
            'PPAN'     : '_ppan',
            'GRADCAL'  : '_gradcal',
            'CMPLXFAC' : '_cmplxfac',
            'REPLDATA' : '_repldata',
            'STDIAG'   : '_stdiag',
            'GEOM'     : 'fixgeom',  # FIXINDEX - GEOM subblock. Must be put at the end
            'BASE'     : 'fixbase',  # FIXINDEX - BASE subblock. Must be put at the end. GEBA subblock not supported
        }
        key = list(self._block_dict.keys())
        attr = list(self._block_dict.values())
        self._block_key = sorted(set(key), key=key.index)
        self._block_attr = sorted(set(attr), key=attr.index)

    @property
    def dft(self):
        """
        Subblock object DFT
        """
        if not hasattr(self, '_block_dft'):
            self.set_dft()
        return self._block_dft

    def set_dft(self, obj=None):
        """
        DFT subblock

        Args:
            obj (DFT | str): A block object of 'DFT' submodule. Or a string in
                CRYSTAL d12 format
        """
        from CRYSTALClear.base.crysd12 import DFT

        self._block_dft = DFT()
        if obj == None:  # Initialize block
            return
        elif type(obj) == str:
            if obj == '': # Clean data
                self._block_dft.clean_block()
            else:
                self._block_dft.analyze_text(obj)
        else:
            self._block_dft = obj

    @property
    def dftd3(self):
        """
        Subblock object DFTD3
        """
        if not hasattr(self, '_block_dftd3'):
            self.set_dftd3()
        return self._block_dftd3

    def set_dftd3(self, obj=None):
        """
        DFTD3 subblock

        Args:
            obj (DFTD3 | str): A block object of 'DFTD3' submodule. Or a string
                in CRYSTAL d12 format
        """
        from CRYSTALClear.base.crysd12 import DFTD3

        self._block_dftd3 = DFTD3()
        if obj == None:  # Initialize block
            return
        elif type(obj) == str:
            if obj == '': # Clean data
                self._block_dftd3.clean_block()
            else:
                self._block_dftd3.analyze_text(obj)
        else:
            self._block_dftd3 = obj

    @property
    def gcp(self):
        """
        Subblock object GCP
        """
        if not hasattr(self, '_block_gcp'):
            self.set_gcp()
        return self._block_gcp

    def set_gcp(self, obj=None):
        """
        GCP subblock

        Args:
            obj (GCP | str): A block object of 'GCP' submodule. Or a string in
                CRYSTAL d12 format.
        """
        from CRYSTALClear.base.crysd12 import GCP

        self._block_gcp = GCP()
        if obj == None:  # Initialize block
            return
        elif type(obj) == str:
            if obj == '': # Clean data
                self._block_gcp.clean_block()
            else:
                self._block_gcp.analyze_text(obj)
        else:
            self._block_gcp = obj

    @property
    def fixgeom(self):
        try:
            return self._block_fixgeom
        except AttributeError:
            raise AttributeError(
                "Attribute does not exist. 'fixindex' is not defined.")

    @property
    def fixbase(self):
        try:
            return self._block_fixbase
        except AttributeError:
            raise AttributeError(
                "Attribute does not exist. 'fixindex' is not defined.")

    def fixindex(self, key1=None, obj1=None, obj2=None):
        """
        Args:
            key1 (str): 'GEOM', 'BASE' or 'GEBA'. Fixindex block keywords
            obj1 (Geom | BasisSet): Geometry or basis set object.
            obj2 (BasisSet): *key1 = GEBA only*. Basis set object.
        """
        import warnings

        if key1 == None:
            self._fixbg = super(SCF, self).assign_keyword('FIXINDEX', [])

        elif key1 == '':
            self._fixbg = super(SCF, self).assign_keyword('FIXINDEX', [], '')
            self._block_ed = 'ENDSCF\n'
            if hasattr(self, '_block_fixgeom'):
                self._block_fixgeom.clean_block()
            elif hasattr(self, '_block_fixbase'):
                self._block_fixbase.clean_block()

        elif key1 == 'GEOM':
            warnings.warn( "'GEOM' keyword of 'FIXINDEX' is identified. Use 'fixgeom' for attributes of the geometry subblock.",
                          stacklevel=2)
            self._fixbg = super(SCF, self).assign_keyword('FIXINDEX', [])
            self._block_fixgeom = Geom()
            if obj1 == None:
                self._block_fixgeom._block_bg = 'ENDSCF\nGEOM\n'
                self._block_fixgeom._block_ed = 'END\n'
                self._block_ed = None # Not '', or the block would be recoginized as an empty one
            elif obj1 == '':
                self._block_fixgeom.clean_block()
                self._block_ed = 'ENDSCF\n'
            else:
                self._block_fixgeom = obj1
                self._block_fixgeom._block_bg = 'ENDSCF\nGEOM\n'
                self._block_fixgeom._block_ed = 'END\n'
                self._block_ed = None # Not '', or the block would be recoginized as an empty one

        elif key1 == 'BASE':
            warnings.warn("'BASE' keyword of 'FIXINDEX' is identified. Use 'fixbase' for attributes of the basis set subblock.",
                          stacklevel=2)
            self._fixbg = super(SCF, self).assign_keyword('FIXINDEX', [])
            self._block_fixbase = BasisSet()
            if obj1 == None:
                self._block_fixbase._block_bg = 'ENDSCF\nBASE\n'
                self._block_fixbase._block_ed = 'END\n'
                self._block_ed = None # Not '', or the block would be recoginized as an empty one
            elif obj1 == '':
                self._block_fixbase.clean_block()
                self._block_ed = 'ENDSCF\n'
            else:
                self._block_fixbase = obj1
                self._block_fixbase._block_bg = 'ENDSCF\nBASE\n'
                self._block_fixbase._block_ed = 'END\n'
                self._block_ed = None # Not '', or the block would be recoginized as an empty one

        # GEBA subblock not supported
        # elif key1 == 'GEBA':
        #     warnings.warn("'GEBA' keyword of 'FIXINDEX' is identified. Use 'fixgeom' for attributes of the geometry subblock and 'fixbase' for attributes of the basis set subblock.")
        #     self._block_fixgeom = Geom()
        #     self._block_fixbase = BasisSet()
        #     if obj1 == None:
        #         self._block_fixgeom._block_bg = 'GEBA\n'
        #         self._block_fixgeom._block_ed = ''
        #         self._block_fixbase._block_bg = ''
        #         self._block_fixbase._block_ed = 'END\n'
        #     elif obj1 == '':
        #         self._block_fixgeom.clean_block()
        #         self._block_fixbase.clean_block()
        #     else:
        #         self._block_fixgeom = obj1
        #         self._block_fixgeom._block_bg = 'GEBA\n'
        #         self._block_fixgeom._block_ed = ''
        #         self._block_fixbase = obj2
        #         self._block_fixbase._block_bg = ''
        #         self._block_fixbase._block_ed = 'END\n'

        else:
            raise ValueError('Keyword error. Allowed keywords: GEOM, BASE. GEBA not supported.')

    def biposize(self, ISIZE=None):
        self._biposize = super(SCF, self).assign_keyword('BIPOSIZE', [1, ], ISIZE)

    def exchsize(self, ISIZE=None):
        self._exchsize = super(SCF, self).assign_keyword('EXCHSIZE', [1, ], ISIZE)

    def toldee(self, ITOL=None):
        self._toldee = super(SCF, self).assign_keyword('TOLDEE', [1, ], ITOL)

    def guessp(self, key='GUESSP'):
        self._guessp = super(SCF, self).assign_keyword(key, [])

    def atomspin(self, NA=None, LA=[]):
        shape, value = super(SCF, self).set_list(NA, LA)
        self._atomspin = super(SCF, self).assign_keyword('ATOMSPIN', shape, value)

    def tolinteg(self, ITOL1=None, ITOL2=None, ITOL3=None, ITOL4=None, ITOL5=None):
        conflict = ['_tolinteg', '_nobipola', '_nobipcou', '_nobipexc']
        super(SCF, self).clean_conflict('_tolinteg', conflict)
        self._tolinteg = super(SCF, self).assign_keyword(
            'TOLINTEG', [5, ], [ITOL1, ITOL2, ITOL3, ITOL4, ITOL5]
        )

    def nobipola(self, key='NOBIPOLA'):
        conflict = ['_tolinteg', '_nobipola', '_nobipcou', '_nobipexc']
        super(SCF, self).clean_conflict('_nobipola', conflict)
        self._nobipola = super(SCF, self).assign_keyword(key, [])

    def nobipcou(self, key='NOBIPCOU'):
        conflict = ['_tolinteg', '_nobipola', '_nobipcou', '_nobipexc']
        super(SCF, self).clean_conflict('_nobipcou', conflict)
        self._nobipcou = super(SCF, self).assign_keyword(key, [])

    def nobipexc(self, key='NOBIPEXC'):
        conflict = ['_tolinteg', '_nobipola', '_nobipcou', '_nobipexc']
        super(SCF, self).clean_conflict('_nobipexc', conflict)
        self._nobipexc = super(SCF, self).assign_keyword(key, [])

    def ldremo(self, value):
        self._ldremo = super(SCF, self).assign_keyword('LDREMO', [1, ], value)

    def maxcycle(self, MAX=None):
        self._maxcycle = super(SCF, self).assign_keyword('MAXCYCLE', [1, ], MAX)

    def fmixing(self, IPMIX=None):
        self._maxcycle = super(SCF, self).assign_keyword('FMIXING', [1, ], IPMIX)

    def shrink(self, IS=None, ISP=None, IS1=None, IS2=None, IS3=None):
        if IS1 == None:
            self._shrink = super(SCF, self).assign_keyword('SHRINK', [2, ], [IS, ISP])
        else:
            self._shrink = super(SCF, self).assign_keyword('SHRINK', [2, 3],
                                                           [IS, ISP, IS1, IS2, IS3])

    def gcpauto(self, key='GCPAUTO'):
        self._gcpauto = super(SCF, self).assign_keyword(key, [])

    def smear(self, WIDTH=None):
        self._smear = super(SCF, self).assign_keyword('SMEAR', [1, ], WIDTH)

    def ppan(self, key='PPAN'):
        self._ppan = super(SCF, self).assign_keyword(key, [])

    def gradcal(self, key='GRADCAL'):
        self._gradcal = super(SCF, self).assign_keyword(key, [])

    def exchange(self, key='EXCHANGE'):
        self._exchange = super(SCF, self).assign_keyword(key, [])

    def postscf(self, key='POSTSCF'):
        self._postscf = super(SCF, self).assign_keyword(key, [])

    def diis(self, key='DIIS'):
        self._diis = super(SCF, self).assign_keyword(key, [])

    def nodiis(self, key='NODIIS'):
        self._diis = super(SCF, self).assign_keyword(key, [])

    def diisallk(self, key='DIISALLK'):
        import warnings

        if hasattr(self, '_diis'):
            if 'NODIIS' in self._diis:
                warnings.warn("Keyword 'NODIIS' is set. It will be removed.",
                              stacklevel=2)
                self._diis = ''
        self._diisallk = super(SCF, self).assign_keyword(key, [])

    def histdiis(self, NCYC=None):
        import warnings

        if hasattr(self, '_diis'):
            if 'NODIIS' in self._diis:
                warnings.warn("Keyword 'NODIIS' is set. It will be removed.",
                              stacklevel=2)
                self._diis = ''
        self._histdiis = super(SCF, self).assign_keyword('HISTDIIS', [1,], NCYC)

    def prtdiis(self, key='PRTDIIS'):
        import warnings

        if hasattr(self, '_diis'):
            if 'NODIIS' in self._diis:
                warnings.warn("Keyword 'NODIIS' is set. It will be removed.",
                              stacklevel=2)
                self._diis = ''
        self._prtdiis = super(SCF, self).assign_keyword(key, [])

    def cmplxfac(self, WEIGHT=None):
        self._cmplxfac = super(SCF, self).assign_keyword('CMPLXFAC', [1, ], WEIGHT)

    def repldata(self, key='REPLDATA'):
        self._repldata = super(SCF, self).assign_keyword(key, [])

    def stdiag(self, key='STDIAG'):
        self._stdiag = super(SCF, self).assign_keyword(key, [])


class DFT(BlockBASE):
    """
    DFT block object
    """

    def __init__(self):
        self._block_bg = 'DFT\n'
        self._block_ed = 'ENDDFT\n'
        self._block_data = ''
        self._block_dict = {  # The sequence of keywords should follow rules in the manual
            'SPIN'     : '_spin',
            'EXCHANGE' : '_exchange',
            'CORRELAT' : '_correlat',
            'OLDGRID'  : '_gridsz',
            'LGRID'    : '_gridsz',
            'XLGRID'   : '_gridsz',
            'XXLGRID'  : '_gridsz',
            'XXXLGRID' : '_gridsz',
            'RADIAL'   : '_gridr',
            'ANGULAR'  : '_grida',
            'SVWN'     : '_xcfunc', # Standalone keywords for text analysis - I know it's a stupid idea - to ensure interactive i/o
            'BLYP'     : '_xcfunc',
            'PBEXC'    : '_xcfunc',
            'PBESOLXC' : '_xcfunc',
            'SOGGAXC'  : '_xcfunc',
            'SOGGA11'  : '_xcfunc',
            'B3PW'     : '_xcfunc',
            'B3LYP'    : '_xcfunc',
            'PBE0'     : '_xcfunc',
            'PBESOL0'  : '_xcfunc',
            'B1WC'     : '_xcfunc',
            'WC1LYP'   : '_xcfunc',
            'B97H'     : '_xcfunc',
            'PBE0-13'  : '_xcfunc',
            'SOGGA11X' : '_xcfunc',
            'MPW1PW91' : '_xcfunc',
            'MPW1K'    : '_xcfunc',
            'HSE06'    : '_xcfunc',
            'HSESOL'   : '_xcfunc',
            'SC-BLYP'  : '_xcfunc',
            'HISS'     : '_xcfunc',
            'RSHXLDA'  : '_xcfunc',
            'WB97'     : '_xcfunc',
            'WB97X'    : '_xcfunc',
            'LC-WPBE'  : '_xcfunc',
            'LC-WPBESOL': '_xcfunc',
            'LC-WBLYP' : '_xcfunc',
            'LC-BLYP'  : '_xcfunc',
            'CAM-B3LYP': '_xcfunc',
            'LC-PBE'   : '_xcfunc',
            'M06L'     : '_xcfunc',
            'REVM06L'  : '_xcfunc',
            'MN15L'    : '_xcfunc',
            'SCAN'     : '_xcfunc',
            'R2SCAN'   : '_xcfunc',
            'B1B95'    : '_xcfunc',
            'MPW1B95'  : '_xcfunc',
            'MPW1B1K'  : '_xcfunc',
            'PW6B95'   : '_xcfunc',
            'PWB6K'    : '_xcfunc',
            'M05'      : '_xcfunc',
            'M052X'    : '_xcfunc',
            'M06'      : '_xcfunc',
            'M062X'    : '_xcfunc',
            'M06HF'    : '_xcfunc',
            'MN15'     : '_xcfunc',
            'REVM06'   : '_xcfunc',
            'SCAN0'    : '_xcfunc',
            'R2SCANH'  : '_xcfunc',
            'R2SCAN0'  : '_xcfunc',
            'R2SCAN50' : '_xcfunc',
            'MN15'     : '_xcfunc',
            'BLYP-D3'  : '_xcfunc',
            'PBE-D3'   : '_xcfunc',
            'B97-D3'   : '_xcfunc',
            'B3LYP-D3' : '_xcfunc',
            'PBE0-D3'  : '_xcfunc',
            'PW1PW-D3' : '_xcfunc',
            'M06-D3'   : '_xcfunc',
            'HSE06-D3' : '_xcfunc',
            'HSESOL-D3': '_xcfunc',
            'LC-WPBE-D3': '_xcfunc',
            'B3LYP-D3' : '_xcfunc',
            'PBEH3C'   : '_xcfunc',
            'HSE3C'    : '_xcfunc',
            'B973C'    : '_xcfunc',
            'PBESOL03C': '_xcfunc',
            'HSESOL3C' : '_xcfunc',
        }
        key = list(self._block_dict.keys())
        attr = list(self._block_dict.values())
        self._block_key = sorted(set(key), key=key.index)
        self._block_attr = sorted(set(attr), key=attr.index)

    def spin(self, key='SPIN'):
        self._spin = super(DFT, self).assign_keyword(key, [])

    def exchange(self, ex=None):
        if hasattr(self, '_xcfunc'):
            raise AttributeError(
                'Exchange-correlation functional is already set.')
        self._exchange = super(DFT, self).assign_keyword('EXCHANGE', [1, ], ex)

    def correlat(self, cor=None):
        if hasattr(self, '_xcfunc'):
            raise AttributeError('Exchange-correlation functional is already set.')
        self._correlat = super(DFT, self).assign_keyword('CORRELAT', [1, ], cor)

    def xcfunc(self, xc=None):
        if hasattr(self, '_exchange') or hasattr(self, '_correlat'):
            raise AttributeError('Separate keywords are set for exchange / correlation functionals.')
        self._xcfunc = super(DFT, self).assign_keyword(None, [1, ], xc)

    def lgrid(self, key='LGRID'):
        self._gridsz = super(DFT, self).assign_keyword(key, [])

    def oldgrid(self, key='OLDGRID'):
        self._gridsz = super(DFT, self).assign_keyword(key, [])

    def xlgrid(self, key='XLGRID'):
        self._gridsz = super(DFT, self).assign_keyword(key, [])

    def xxlgrid(self, key='XXLGRID'):
        self._gridsz = super(DFT, self).assign_keyword(key, [])

    def xxxlgrid(self, key='XXXLGRID'):
        self._gridsz = super(DFT, self).assign_keyword(key, [])

    def radial(self, NR=None, RL=[], IL=[]):
        if hasattr(self, '_gridsz'):
            raise AttributeError("Pre-defined integrated grid '{}' is defined.".format(self._gridsz[:-1]))
        if NR != None and NR != '':
            if len(RL) != len(IL) and NR != len(RL):
                raise ValueError('Inconsistent definition of parameters.')
        self._gridr = super(DFT, self).assign_keyword('RADIAL', [1, len(RL), len(IL)], [NR, ] + RL + IL)

    def angular(self, NI=None, AL=[], LEV=[]):
        if hasattr(self, '_gridsz'):
            raise AttributeError("Pre-defined integrated grid '{}' is defined.".format(self._gridsz[:-1]))
        if NI != None and NI != '':
            if len(AL) != len(LEV) and NI != len(AL):
                raise ValueError('Inconsistent definition of parameters.')
        self._grida = super(DFT, self).assign_keyword('ANGULAR', [1, len(AL), len(LEV)], [NI, ] + AL + LEV)


class DFTD3(BlockBASE):
    """
    DFTD3 block object
    """

    def __init__(self):
        self._block_bg = 'DFTD3\n'
        self._block_ed = 'END\n'
        self._block_data = ''
        self._block_dict = {  # The sequence of keywords should follow rules in the manual
            'VERSION'   : '_version',
            'FUNC'      : '_func',
            'ABC'       : '_abc',
            'S6'        : '_s6',
            'S8'        : '_s8',
            'A1'        : '_a1',
            'A2'        : '_a2',
            'RS6'       : '_rs6',
            'RS8'       : '_rs8',
            'RADIUS'    : '_radius',
            'CNRADIUS'  : '_cnradius',
            'ABCRADIUS' : '_abcradius',
            'PRINTC6'   : '_printc6',
        }
        key = list(self._block_dict.keys())
        attr = list(self._block_dict.values())
        self._block_key = sorted(set(key), key=key.index)
        self._block_attr = sorted(set(attr), key=attr.index)

    def version(self, NAT=None):
        self._version = super(DFTD3, self).assign_keyword('VERSION', [1, ], NAT)

    def func(self, CHAR=None):
        self._func = super(DFTD3, self).assign_keyword('FUNC', [1, ], CHAR)

    def abc(self, key='ABC'):
        self._abc = super(DFTD3, self).assign_keyword(key, [])

    def s6(self, s6=None):
        self._s6 = super(DFTD3, self).assign_keyword('S6', [1, ], s6)

    def s8(self, s8=None):
        self._s8 = super(DFTD3, self).assign_keyword('S8', [1, ], s8)

    def a1(self, a1=None):
        self._a1 = super(DFTD3, self).assign_keyword('A1', [1, ], a1)

    def a2(self, a1=None):
        self._a2 = super(DFTD3, self).assign_keyword('A2', [1, ], a2)

    def rs6(self, rs6=None):
        self._rs6 = super(DFTD3, self).assign_keyword('RS6', [1, ], rs6)

    def rs8(self, rs8=None):
        self._rs8 = super(DFTD3, self).assign_keyword('RS8', [1, ], rs8)

    def radius(self, radius=None):
        self._radius = super(DFTD3, self).assign_keyword('RADIUS', [1, ], radius)

    def cnradius(self, cnradius=None):
        self._cnradius = super(DFTD3, self).assign_keyword('CNRADIUS', [1, ], cnradius)

    def abcradius(self, abcradius=None):
        self._abcradius = super(DFTD3, self).assign_keyword('ABCRADIUS', [1, ], abcradius)

    def printc6(self, key='PRINTC6'):
        self._printc6 = super(DFTD3, self).assign_keyword(key, [])


class GCP(BlockBASE):
    """
    GCP block object
    """

    def __init__(self):
        self._block_bg = 'GCP\n'
        self._block_ed = 'END\n'
        self._block_data = ''
        self._block_dict = {  # The sequence of keywords should follow rules in the manual
            'METHOD'     : '_method',
            'SIGMA'      : '_sigma',
            'ALPHA'      : '_alpha',
            'BETA'       : '_beta',
            'ETA'        : '_eta',
            'RADIUS'     : '_radius',
            'PRINTEMISS' : '_printemiss',
        }
        key = list(self._block_dict.keys())
        attr = list(self._block_dict.values())
        self._block_key = sorted(set(key), key=key.index)
        self._block_attr = sorted(set(attr), key=attr.index)

    def method(self, method=None):
        self._method = super(GCP, self).assign_keyword('METHOD', [1, ], method)

    def sigma(self, sigma=None):
        self._sigma = super(GCP, self).assign_keyword('SIGMA', [1, ], sigma)

    def alpha(self, alpha=None):
        self._alpha = super(GCP, self).assign_keyword('ALPHA', [1, ], alpha)

    def beta(self, beta=None):
        self._beta = super(GCP, self).assign_keyword('BETA', [1, ], beta)

    def eta(self, eta=None):
        self._eta = super(GCP, self).assign_keyword('ETA', [1, ], eta)

    def radius(self, radius=None):
        self._radius = super(GCP, self).assign_keyword('RADIUS', [1, ], radius)

    def printemiss(self, key='PRINTEMISS'):
        self._printemiss = super(GCP, self).assign_keyword(key, [])
