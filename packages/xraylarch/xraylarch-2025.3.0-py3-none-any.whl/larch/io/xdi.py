#!/usr/bin/env python
"""
Read/Write XAS Data Interchange Format for Python
"""
import os
from ctypes import c_long, c_double, c_char_p, c_void_p, pointer, Structure

__version__ = '1.2.0larch'

from numpy import array, exp, log, sin, arcsin

from .. import Group
from ..larchlib import get_dll
from ..utils import read_textfile, bytes2str, str2bytes
from ..utils.physical_constants import RAD2DEG, PLANCK_HC
from .columnfile import read_ascii

class XDIFileStruct(Structure):
    "emulate XDI File"
    _fields_ = [('nmetadata',     c_long),
                ('narrays',       c_long),
                ('npts',          c_long),
                ('narray_labels', c_long),
                ('nouter',        c_long),
                ('error_lineno',  c_long),
                ('dspacing',      c_double),
                ('xdi_libversion',c_char_p),
                ('xdi_version',   c_char_p),
                ('extra_version', c_char_p),
                ('filename',      c_char_p),
                ('element',       c_char_p),
                ('edge',          c_char_p),
                ('comments',      c_char_p),
                ('error_line',    c_char_p),
                ('error_message', c_char_p),
                ('array_labels',  c_void_p),
                ('outer_label',   c_char_p),
                ('array_units',   c_void_p),
                ('meta_families', c_void_p),
                ('meta_keywords', c_void_p),
                ('meta_values',   c_void_p),
                ('array',         c_void_p),
                ('outer_array',   c_void_p),
                ('outer_breakpts', c_void_p)]

string_attrs = ('comments', 'edge', 'element', 'error_line',
                'error_message', 'extra_version', 'filename',
                'outer_label', 'xdi_libversion', 'xdi_pyversion',
                'xdi_version')


def tostr(val):
    if isinstance(val, str):
        return val
    if isinstance(val, bytes):
        return val.decode()
    return str(val)

def tostrlist(address, nitems):
    return [str(i, 'utf-8') for i in (nitems*c_char_p).from_address(address)]

def add_dot2path():
    """add this folder to begninng of PATH environmental variable"""
    sep = ':'
    if os.name == 'nt': sep = ';'
    paths = os.environ.get('PATH','').split(sep)
    paths.insert(0, os.path.abspath(os.curdir))
    os.environ['PATH'] = sep.join(paths)


XDILIB = None
def get_xdilib():
    """make initial connection to XDI dll"""
    global XDILIB
    if XDILIB is None:
        XDILIB = get_dll('xdifile')
        XDILIB.XDI_errorstring.restype   = c_char_p
    return XDILIB

class XDIFileException(Exception):
    """XDI File Exception: General Errors"""
    def __init__(self, msg, **kws):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return self.msg

class XDIFile(object):
    """ XAS Data Interchange Format:

    See https://github.com/XraySpectrscopy/XAS-Data-Interchange

    for further details

    >>> xdi_file = XDFIile(filename)

    Principle methods:
      read():     read XDI data file, set column data and attributes
      write(filename):  write xdi_file data to an XDI file.
    """
    _invalid_msg = "invalid data for '%s':  was expecting %s, got '%s'"

    def __init__(self, filename=None, labels=None):
        self.filename = filename
        self.xdi_pyversion =  __version__
        # self.xdilib = get_xdilib()
        self.comments = []
        self.data = []
        self.attrs = {}
        self.status = None
        self.user_labels = labels
        if self.filename:
            self.read(self.filename)

    def write(self, filename):
        "write out an XDI File"
        print( 'Writing XDI file not currently supported')

    def read(self, filename=None):
        """read validate and parse an XDI datafile into python structures
        """
        if filename is None and self.filename is not None:
            filename = self.filename

        text = read_textfile(filename)
        lines = text.split('\n')
        if len(text) < 256 or len(lines) < 6:
            msg = [f'Error reading XDIFile {filename}',
                   'data file too small to be valid XDI']
            raise ValueError('\n'.join(msg))

        pxdi = pointer(XDIFileStruct())

        xdilib = get_xdilib()
        self.status = xdilib.XDI_readfile(filename.encode(), pxdi)
        if self.status < 0:
            msg =  bytes2str(xdilib.XDI_errorstring(self.status))
            xdilib.XDI_cleanup(pxdi, self.status)
            msg = 'Error reading XDIFile %s\n%s' % (filename, msg)
            raise ValueError(msg)

        xdi = pxdi.contents
        for attr in dict(xdi._fields_):
            setattr(self, attr, getattr(xdi, attr))

        self.array_labels = tostrlist(xdi.array_labels, self.narrays)

        if self.user_labels is not None:
            ulab = self.user_labels.replace(',', ' ')
            ulabs = [l.strip() for l in ulab.split()]
            self.array_labels[:len(ulabs)] = ulabs

        arr_units         = tostrlist(xdi.array_units, self.narrays)
        self.array_units  = []
        self.array_addrs  = []
        for unit in arr_units:
            addr = ''
            if '||' in unit:
                unit, addr = [x.strip() for x in unit.split('||', 1)]
            self.array_units.append(unit)
            self.array_addrs.append(addr)

        mfams = tostrlist(xdi.meta_families, self.nmetadata)
        mkeys = tostrlist(xdi.meta_keywords, self.nmetadata)
        mvals = tostrlist(xdi.meta_values,   self.nmetadata)
        self.attrs = {}
        for fam, key, val in zip(mfams, mkeys, mvals):
            fam = fam.lower()
            key = key.lower()
            if fam not in self.attrs:
                self.attrs[fam] = {}
            self.attrs[fam][key] = val

        parrays = (xdi.narrays*c_void_p).from_address(xdi.array)[:]
        self.data = [(xdi.npts*c_double).from_address(p)[:] for p in parrays]

        nout = xdi.nouter
        outer, breaks = [], []
        if nout > 1:
            outer  = (nout*c_double).from_address(xdi.outer_array)[:]
            breaks = (nout*c_long).from_address(xdi.outer_breakpts)[:]
        for attr in ('outer_array', 'outer_breakpts', 'nouter'):
            delattr(self, attr)
        self.outer_array    = array(outer)
        self.outer_breakpts = array(breaks)

        self.data = array(self.data)
        self.data.shape = (self.narrays, self.npts)
        self._assign_arrays()
        for attr in ('nmetadata', 'narray_labels', 'meta_families',
                     'meta_keywords', 'meta_values', 'array'):
            delattr(self, attr)
        xdilib.XDI_cleanup(pxdi, 0)

    def _assign_arrays(self):
        """assign data arrays for principle data attributes:
           energy, angle, i0, itrans, ifluor, irefer,
           mutrans, mufluor, murefer, etc.  """

        xunits = 'eV'
        xname = None
        ix = -1
        self.data = array(self.data)

        for idx, name in enumerate(self.array_labels):
            dat = self.data[idx,:]
            setattr(self, name, dat)
            if name in ('energy', 'angle'):
                ix = idx
                xname = name
                units = self.array_units[idx]
                if units is not None:
                    xunits = units

        # convert energy to angle, or vice versa
        monodat = {}
        if 'mono' in  self.attrs:
            monodat = self.attrs['mono']
        elif 'monochromator' in  self.attrs:
            monodat = self.attrs['monochromator']

        if ix >= 0 and 'd_spacing' in monodat:
            dspacing = monodat['d_spacing'].strip()
            dunits = 'Angstroms'
            if ' ' in dspacing:
                dspacing, dunits = dspacing.split(None, 1)
            self.dspacing = float(dspacing)
            self.dspacing_units = dunits

            omega = PLANCK_HC/(2*self.dspacing)
            if xname == 'energy' and not hasattr(self, 'angle'):
                energy_ev = self.energy
                if xunits.lower() == 'kev':
                    energy_ev = 1000. * energy_ev
                self.angle = RAD2DEG * arcsin(omega/energy_ev)
            elif xname == 'angle' and not hasattr(self, 'energy'):
                angle_rad = self.angle
                if xunits.lower() in ('deg', 'degrees'):
                    angle_rad = angle_rad / RAD2DEG
                self.energy = omega/sin(angle_rad)

        if hasattr(self, 'i0'):
            if hasattr(self, 'itrans') and not hasattr(self, 'mutrans'):
                self.mutrans = -log(self.itrans / (self.i0+1.e-12))
            elif hasattr(self, 'mutrans') and not hasattr(self, 'itrans'):
                self.itrans  =  self.i0 * exp(-self.mutrans)
            if hasattr(self, 'ifluor') and not hasattr(self, 'mufluor'):
                self.mufluor = self.ifluor/(self.i0+1.e-12)

            elif hasattr(self, 'mufluor') and not hasattr(self, 'ifluor'):
                self.ifluor =  self.i0 * self.mufluor

        if hasattr(self, 'itrans'):
            if hasattr(self, 'irefer') and not hasattr(self, 'murefer'):
                self.murefer = -log(self.irefer / (self.itrans+1.e-12))

            elif hasattr(self, 'murefer') and not hasattr(self, 'irefer'):
                self.irefer = self.itrans * exp(-self.murefer)


class PyXDIFile(object):
    """ XAS Data Interchange Format:

    read XDI file with Python, emulate XDFile

    >>> xdi_file = PyXDFIile(filename)

    Principle methods:
      read():     read XDI data file, set column data and attributes
    """
    _invalid_msg = "invalid data for '%s':  was expecting %s, got '%s'"

    def __init__(self, filename=None, labels=None):
        self.filename = filename
        self.xdi_pyversion =  __version__
        self.comments = []
        self.data = []
        self.attrs = {}
        self.status = None
        self.user_labels = labels
        if self.filename:
            self.read(self.filename)

    def read(self, filename=None):
        """read validate and parse an XDI datafile into python structures
        """
        if filename is None and self.filename is not None:
            filename = self.filename

        text = read_textfile(filename)
        lines = text.split('\n')
        if len(text) < 256 or len(lines) < 6:
            msg = [f'Error reading XDIFile {filename}',
                   'data file too small to be valid XDI']
            raise ValueError('\n'.join(msg))

        line0 = lines[0].strip()
        xdi_version = None
        if line0.startswith('#') and 'XDI/' in line0:
            try:
                words = line0.split('XDI/')
                xdi_version = words[1]
            except:
                pass

        if xdi_version is None:
            msg = [f'Error reading XDIFile {filename}',
                   'invalid XDI version in fist line']
            raise ValueError('\n'.join(msg))

        self.xdi_version = xdi_version
        afile = read_ascii(filename)

        self.data = afile.data
        self.array_labels = afile.array_labels
        for attr in self.array_labels:
            setattr(self, attr, getattr(afile, attr))
        self.array_addrs = [' ']*len(self.array_labels)
        self.array_units = [' ']*len(self.array_labels)
        attrs = {'column': {}}
        commentline = None
        for iline, hline in enumerate(afile.header):
            if hline.startswith('#'):
                hline = hline[1:].strip()
            # column units
            if hline.startswith('XDI/'):
                continue
            elif hline.startswith('Column.'):
                colnum, value = hline.split(':', 1)
                attrs['column'][colnum] = value
                colnum = int(colnum.replace('Column.', '')) - 1
                if '#' in value:
                    value = value[:value.find('#')]
                words = value.strip().split()
                if len(words) > 1:
                    units = words[1].strip()
                    if '||' in units:
                        unit, addr = [x.strip() for x in units.split('||', 1)]
                        self.array_addrs[colnum] = addr
                    self.array_units[colnum] = units
            elif hline.startswith('///'):
                commentline = iline
            elif commentline is None:
                metaname, value = hline.split(':', 1)
                metaname = metaname.lower()
                if '.' in metaname:
                    family, field = metaname.split('.', 1)
                else:
                    continue
                if family not in attrs:
                    attrs[family] = {}
                attrs[family][field] = value
                if '||' in value:
                    value, addr = [x.strip() for x in value.split('||', 1)]
                if 'element.symbol' in metaname:
                    self.element = value
                elif 'element.edge' in metaname:
                    self.edge = value
                elif 'element' in field:
                    self.element = value
                elif 'edge' in field:
                    self.edge = value
                elif 'mono' in family and 'dspacing' in field:
                    self.d_spacing = float(value)
                elif 'mono' in family and 'd_spacing' in field:
                    self.d_spacing = float(value)
                elif 'scan' in family and 'start_time' in field:
                    self.start_time = value
                elif 'scan' in family and 'end_time' in field:
                    self.end_time = value

        comments = []
        if commentline is not None:
            for hline in afile.header[commentline+1:]:
                if hline.startswith('----'):
                    break
                comments.append(hline[1:].strip())
        self.comments = '\n'.join(comments)
        self.attrs = attrs
        self._assign_arrays()

    def _assign_arrays(self):
        """assign data arrays for principle data attributes:
           energy, angle, i0, itrans, ifluor, irefer,
           mutrans, mufluor, murefer, etc.  """

        xunits = 'eV'
        xname = None
        ix = -1
        self.data = array(self.data)

        for idx, name in enumerate(self.array_labels):
            dat = self.data[idx,:]
            setattr(self, name, dat)
            if name in ('energy', 'angle'):
                ix = idx
                xname = name
                units = self.array_units[idx]
                if units is not None:
                    xunits = units

        # convert energy to angle, or vice versa
        monodat = {}
        if 'mono' in  self.attrs:
            monodat = self.attrs['mono']
        elif 'monochromator' in  self.attrs:
            monodat = self.attrs['monochromator']

        if ix >= 0 and 'd_spacing' in monodat:
            dspacing = monodat['d_spacing'].strip()
            dunits = 'Angstroms'
            if ' ' in dspacing:
                dspacing, dunits = dspacing.split(None, 1)
            self.dspacing = float(dspacing)
            self.dspacing_units = dunits

            omega = PLANCK_HC/(2*self.dspacing)
            if xname == 'energy' and not hasattr(self, 'angle'):
                energy_ev = self.energy
                if xunits.lower() == 'kev':
                    energy_ev = 1000. * energy_ev
                self.angle = RAD2DEG * arcsin(omega/energy_ev)
            elif xname == 'angle' and not hasattr(self, 'energy'):
                angle_rad = self.angle
                if xunits.lower() in ('deg', 'degrees'):
                    angle_rad = angle_rad / RAD2DEG
                self.energy = omega/sin(angle_rad)

        if hasattr(self, 'i0'):
            if hasattr(self, 'itrans') and not hasattr(self, 'mutrans'):
                self.mutrans = -log(self.itrans / (self.i0+1.e-12))
            elif hasattr(self, 'mutrans') and not hasattr(self, 'itrans'):
                self.itrans  =  self.i0 * exp(-self.mutrans)
            if hasattr(self, 'ifluor') and not hasattr(self, 'mufluor'):
                self.mufluor = self.ifluor/(self.i0+1.e-12)

            elif hasattr(self, 'mufluor') and not hasattr(self, 'ifluor'):
                self.ifluor =  self.i0 * self.mufluor

        if hasattr(self, 'itrans'):
            if hasattr(self, 'irefer') and not hasattr(self, 'murefer'):
                self.murefer = -log(self.irefer / (self.itrans+1.e-12))

            elif hasattr(self, 'murefer') and not hasattr(self, 'irefer'):
                self.irefer = self.itrans * exp(-self.murefer)


def read_xdi(filename, labels=None):
    """read an XDI File into a Group

    Arguments:
       filename (str): name of file to read
       labels (str or None):  string to use for setting array names [None]

    Returns:
      Group

      A data group containing data read from file, with XDI attributes and
      conventions.

    Notes:
       1. See https://github.com/XraySpectrscopy/XAS-Data-Interchange

       2. if `labels` is `None` (default), the names of the output arrays
          will be determined from the XDI column label in the XDI header.
          To override these array names, use a string with space or comma
          separating names for the arrays.


    Example:
       >>> from larch.io import xdi
       >>> fe3_data = read_xdi('FeXAFS_Fe2O3.001')
       >>> print(fe3_data.array_labels)
       ['energy', 'mutrans', 'i0']

       >>> fec3 = read_xdi('fe3c_rt.xdi', labels='e, x, y')
       >>> print(fec3.array_labels)
       ['e', 'x', 'y']

    See Also:
        read_ascii

    """
    xdif = XDIFile(filename, labels=labels)
    group = Group()
    for key, val in xdif.__dict__.items():
        if not key.startswith('_'):
            if key in string_attrs:
                val = tostr(val)
            setattr(group, key, val)
    group.__name__ ='XDI file %s' % filename
    doc = ['%i arrays, %i npts' % (xdif.narrays, xdif.npts)]
    arr_labels = getattr(xdif, 'array_labels', None)
    if arr_labels is not None:
        doc.append("Array Labels: %s" % repr(arr_labels))
    group.__doc__ = '\n'.join(doc)

    group.path = filename
    path, fname = os.path.split(filename)
    group.filename = fname
    return group
