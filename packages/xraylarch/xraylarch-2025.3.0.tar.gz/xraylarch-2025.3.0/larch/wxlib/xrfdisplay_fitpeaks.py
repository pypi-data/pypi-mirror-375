#!/usr/bin/env python
"""
fitting GUI for XRF display
"""
import sys
import time
import copy
from functools import partial
from threading import Thread
from pathlib import Path
import json
import numpy as np
import wx
import wx.lib.agw.pycollapsiblepane as CP
import wx.lib.scrolledpanel as scrolled
import wx.dataview as dv
DVSTYLE = dv.DV_SINGLE|dv.DV_VERT_RULES|dv.DV_ROW_LINES

from pyshortcuts import uname, fix_filename
from lmfit import Parameter, Minimizer

from . import (SimpleText, FloatCtrl, FloatSpin, Choice, Font, pack,
               Button, Check, HLine, GridPanel, RowPanel, CEN, LEFT,
               RIGHT, FileSave, GUIColors, FRAMESTYLE, BitmapButton,
               SetTip, GridPanel, Popup, FloatSpinWithPin, get_icon,
               flatnotebook, PeriodicTablePanel,
               FONTSIZE, FONTSIZE_FW)

from xraydb import (material_mu, xray_edge, materials, add_material,
                    atomic_number, atomic_symbol, xray_line)
# from .notebooks import flatnotebook
# from .periodictable import PeriodicTablePanel
from .parameter import ParameterPanel

from larch import Group

from ..math import peak_indices
from ..xrf import xrf_background, MCA, FanoFactors
from ..utils import json_dump, json_load, gformat
from ..utils.jsonutils import encode4js, decode4js
from ..utils.physical_constants import E_MASS
from ..site_config import user_larchdir
from .xrfdisplay_utils import (XRFGROUP, mcaname, XRFRESULTS_GROUP,
                               MAKE_XRFRESULTS_GROUP)

def read_filterdata(flist, _larch):
    """ read filters data"""
    materials = _larch.symtable.get_symbol('_xray._materials')
    out = {}
    out['None'] = ('', 0)
    for name in flist:
        if name in materials:
            out[name]  = materials[name]
    return out

def VarChoice(p, default=0, size=(90, -1)):
    if default in (False, 'False', 'Fix', 'No'):
        default = 0
    else:
        default = 1
    return Choice(p, choices=['Fix', 'Vary'],
                  size=size, default=default)

NFILTERS = 4
MIN_CORREL = 0.10

tooltips = {'ptable': 'Select Elements to include in model',
            'cen': 'centroid of peak',
            'step': 'size of step extending to low energy side of peak, fraction of peak height',
            'gamma': 'gamma (lorentzian-like weight) of Voigt function',
            'tail': 'intensity of tail function at low energy side of peak',
            'beta': 'width of tail function at low energy side of peak',
            'sigma': 'scale sigma from Energy/Noise by this amount',
        }

CompositionUnits = ('ng/mm^2', 'wt %', 'ppm')

Detector_Materials = ['Si', 'Ge']
EFano_Text = 'Peak Widths:  sigma = sqrt(E_Fano * Energy + Noise**2) '
Geom_Text = 'Angles in degrees: 90=normal to surface, 0=grazing surface'
Energy_Text = 'All energies in keV'


FitTols = ['1.e-2', '3.e-3', '1.e-3', '3.e-4', '1.e-4', '3.e-5', '1.e-5',
           '3.e-6', '1.e-6', '3.e-7', '1.e-7']
FitSteps = ['1.e-2', '3.e-3', '1.e-3', '3.e-4', '1.e-4', '3.e-5', '1.e-5',
            '3.e-6', '1.e-6', '3.e-7', '1.e-7']

FitMaxNFevs = ['200', '500', '1000', '1500', '2000', '3000', '5000', '10000']

xrfmod_setup = """### XRF Model: {mca_label:s}  @ {datetime:s}
# mca data group for fit:
{XRFGROUP}.workmca = {mcagroup}

# setup XRF Model:
_xrfmodel = xrf_model(xray_energy={en_xray:.2f}, count_time={count_time:.5f},
                      energy_min={en_min:.2f}, energy_max={en_max:.2f})

_xrfmodel.set_detector(thickness={det_thk:.5f}, material='{det_mat:s}',
                cal_offset={cal_offset:.5f}, cal_slope={cal_slope:.5f},
                vary_cal_offset={cal_vary!r}, vary_cal_slope={cal_vary!r},
                peak_step={peak_step:.5f}, vary_peak_step={peak_step_vary:s},
                peak_tail={peak_tail:.5f}, vary_peak_tail={peak_tail_vary:s},
                peak_beta={peak_beta:.5f}, vary_peak_beta={peak_beta_vary:s},
                peak_gamma={peak_gamma:.5f}, vary_peak_gamma={peak_gamma_vary:s},
                noise={det_noise:.5f}, vary_noise={det_noise_vary:s})"""

xrfmod_scattpeak = """
# add scatter peak
_xrfmodel.add_scatter_peak(name='{peakname:s}', center={_cen:.2f},
                amplitude=1e5, step={_step:.5f}, tail={_tail:.5f}, beta={_beta:.5f},
                sigmax={_sigma:.5f},  vary_center={vcen:s}, vary_step={vstep:s},
                vary_tail={vtail:s}, vary_beta={vbeta:s}, vary_sigmax={vsigma:s})"""

xrfmod_fitscript = """
# run XRF fit, save results
_xrffitresult = _xrfmodel.fit_spectrum({XRFGROUP}.workmca, energy_min={emin:.2f}, energy_max={emax:.2f},
                                       fit_toler={fit_toler:.6g}, fit_step={fit_step:.6g}, max_nfev={max_nfev:d})
_xrfresults.insert(0, _xrffitresult)
########
"""

xrfmod_filter = "_xrfmodel.add_filter('{name:s}', {thick:.5f}, vary_thickness={vary:s})"
xrfmod_matrix = "_xrfmodel.set_matrix('{name:s}', {thick:.5f}, density={density:.5f})"
xrfmod_pileup = "_xrfmodel.add_pileup(scale={scale:.3f}, vary={vary:s})"
xrfmod_escape = "_xrfmodel.add_escape(scale={scale:.3f}, vary={vary:s})"

xrfmod_savejs = "_xrfresults[{nfit:d}].save('{filename:s}')"

xrfmod_elems = """
# add elements
for atsym in {elemlist:s}:
    _xrfmodel.add_element(atsym)
#endfor
del atsym"""

Filter_Lengths = ['microns', 'mm', 'cm']
Filter_Materials = ['None', 'air', 'nitrogen', 'helium', 'kapton',
                    'beryllium', 'aluminum', 'mylar', 'pmma']


DEF_CONFIG = { "mca_name": "", "escape_use": True, "escape_amp": 0.25,
               "pileup_use": True, "pileup_amp": 0.2, "escape_amp_vary":
               True, "pileup_amp_vary": True, "cal_slope": 0.01,
               "cal_offset": 0, "cal_vary": True, "det_mat": "Si", "det_thk":
               0.4, "det_noise_vary": True,
               "en_xray": 30, "en_min": 2.5, "en_max": 30,
               "flux_in": 1e9, "det_noise": 0.035, "angle_in": 45.0,
               "angle_out": 45.0, "det_dist": 50.0, "det_area": 50.0,
               "elements": [16, 17, 18, 20, 22, 24, 25, 26, 28, 29, 30],
               "filter1_mat": "beryllium", "filter1_thk": 0.025, "filter1_var": False,
               "filter2_mat": "air", "filter2_thk": 50.0, "filter2_var": False,
               "filter3_mat": "kapton", "filter3_thk": 0.0, "filter3_var": False,
               "filter4_mat": "aluminum", "filter4_thk": 0.0, "filter4_var": False,
               "matrix_mat": "", "matrix_thk": 0.0, "matrix_den": 1.0,
               "peak_step": 0.025, "peak_gamma": 0.05, "peak_tail": 0.1,
               "peak_beta": 0.5,  "peak_step_vary": False, "peak_tail_vary": False,
               "peak_gamma_vary": False, "peak_beta_vary": False,
               "elastic_use": True, "elastic_cen_vary": False, "elastic_step_vary": False,
               "elastic_beta_vary": False, "elastic_tail_vary": False,
               "elastic_sigma_vary": False, "elastic_cen": 30,
               "elastic_step": 0.025, "elastic_tail": 0.1,
               "elastic_beta": 0.5, "elastic_sigma": 1.0,
               "compton1_use": True, "compton1_cen_vary": True,
               "compton1_step_vary": True, "compton1_beta_vary": False,
               "compton1_tail_vary": False, "compton1_sigma_vary": False,
               "compton1_cen": 12.1875, "compton1_step": 0.025, "compton1_tail": 0.25,
               "compton1_beta": 2.0, "compton1_sigma": 1.5,
               "compton2_use": True, "compton2_cen_vary": True, "compton2_step_vary": False,
               "compton2_beta_vary": False, "compton2_tail_vary": False,
               "compton2_sigma_vary": False, "compton2_cen": 11.875,
               "compton2_step": 0.025, "compton2_tail": 0.25, "compton2_beta": 2.5,
               "compton2_sigma": 2.0, "count_time": 120.0,
              }

class FitSpectraFrame(wx.Frame):
    """Frame for Spectral Analysis"""

    def __init__(self, parent, size=(750, 850)):
        self.parent = parent
        self._larch = parent.larch
        symtable = self._larch.symtable
        # fetch current spectra from parent
        if not symtable.has_group(XRFRESULTS_GROUP):
            self._larch.eval(MAKE_XRFRESULTS_GROUP)

        self.xrfresults = symtable.get_symbol(XRFRESULTS_GROUP)
        xrfgroup = symtable.get_group(XRFGROUP)
        mcagroup = getattr(xrfgroup, '_mca')
        self.mca = getattr(xrfgroup, mcagroup)
        self.mcagroup = f'{XRFGROUP}.{mcagroup}'

        self.config = DEF_CONFIG

        opts = getattr(xrfgroup, 'fitconfig', None)
        if opts is None:
            xrf_conffile = Path(user_larchdir, 'xrf_fitconfig.json')
            if xrf_conffile.exists():
                opts = json_load(xrf_conffile.as_posix())
        if opts is not None:
            self.config.update(opts)

        efactor = 1.0 if max(self.mca.energy) < 250. else 1000.0

        if self.mca.incident_energy is None:
            self.mca.incident_energy = 20.0
        if self.mca.incident_energy > 250:
            self.mca.incident_energy /= 1000.0

        self.nfit = 0
        self.colors = GUIColors()
        wx.Frame.__init__(self, parent, -1, 'Fit XRF Spectra',
                          size=size, style=wx.DEFAULT_FRAME_STYLE)

        mainfont = wx.Font(FONTSIZE_FW-1, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.font_fixedwidth = wx.Font(FONTSIZE_FW, wx.MODERN, wx.NORMAL,
                                       wx.NORMAL)
        self.SetFont(mainfont)

        self.wids = {}
        self.owids = {}

        pan = GridPanel(self)
        self.mca_label = self.mca.label

        self.wids['mca_name'] = SimpleText(pan, self.mca_label, size=(550, -1), style=LEFT)
        self.wids['btn_calc'] = Button(pan, 'Calculate Model', size=(150, -1),
                                       action=self.onShowModel)
        self.wids['btn_fit'] = Button(pan, 'Fit Model', size=(150, -1),
                                       action=self.onFitModel)
        self.wids['fit_message'] = SimpleText(pan, ' ', size=(300, -1), style=LEFT)

        pan.AddText("  XRF Spectrum: ", colour='#880000')
        pan.Add(self.wids['mca_name'], dcol=3)
        pan.Add(self.wids['btn_calc'], newrow=True)
        pan.Add(self.wids['btn_fit'])
        pan.Add(self.wids['fit_message'])
        self.panels = {}
        self.panels['Beam & Detector']  = self.beamdet_page
        self.panels['Filters & Matrix'] = self.materials_page
        self.panels['Elements & Peaks'] = self.elempeaks_page
        self.panels['Fit Results']        = self.fitresult_page
        self.panels['Composition'] = self.composition_page

        self.nb = flatnotebook(pan, self.panels, on_change=self.onNBChanged)
        pan.Add((5, 5), newrow=True)
        pan.Add(self.nb, dcol=5, drow=10, newrow=True)
        pan.pack()

        self.Show()
        self.Raise()

    def onNBChanged(self, event=None):
        pagelabel = self.nb._pages.GetPageText(event.GetSelection()).strip()
        if pagelabel.startswith('Composition'):
            self.UpdateCompositionPage()

    def elempeaks_page(self, **kws):
        "elements and peaks parameters"
        mca = self.parent.mca
        wids = self.wids
        p = GridPanel(self)
        self.selected_elems = []
        ptable_fontsize = 11 if uname=='darwin' else 9

        ptpanel = wx.Panel(p)
        self.ptable = PeriodicTablePanel(ptpanel, multi_select=True,
                                         fontsize=ptable_fontsize,
                                         size=(360, 180),
                                         tooltip_msg=tooltips['ptable'],
                                         onselect=self.onElemSelect)
        ptsizer = wx.BoxSizer(wx.HORIZONTAL)
        ptsizer.Add((50,50),  1, wx.ALIGN_LEFT|wx.GROW, 2)
        ptsizer.Add(self.ptable, 0, wx.ALIGN_CENTER|wx.ALL, 2)
        ptsizer.Add((5, 5), 1, wx.ALIGN_LEFT|wx.GROW, 2)
        pack(ptpanel, ptsizer)

        cnf = self.config
        for name, xmax, xinc in (('step',   1, 0.005),
                                 ('gamma', 10, 0.01),
                                 ('beta',  10, 0.01),
                                 ('tail', 1.0, 0.05)):
            fname = 'peak_%s' % name
            vname = 'peak_%s_vary' % name
            wids[fname] = FloatSpin(p, value=cnf[fname], digits=3,
                                    min_val=0, max_val=xmax,
                                    increment=xinc, tooltip=tooltips[name])
            wids[vname] = VarChoice(p, default=cnf[vname])

        btn_from_peaks = Button(p, 'Guess Peaks', size=(175, -1),
                                action=self.onElems_GuessPeaks)
        # tooltip='Guess elements from peak locations')
        btn_from_rois = Button(p, 'Use ROIS as Peaks', size=(175, -1),
                               action=self.onElems_FromROIS)
        btn_clear_elems = Button(p, 'Clear All Peaks', size=(175, -1),
                                 action=self.onElems_Clear)
        wx.CallAfter(self.onElems_GuessPeaks)

        p.AddText('Elements to model:', colour='#880000', dcol=2)
        p.Add(ptpanel, dcol=5, drow=5, pad=5,
              style=wx.ALIGN_RIGHT|wx.ALL|wx.GROW,
              newrow=True)
        irow = p.irow

        p.Add(btn_from_peaks,   icol=5, dcol=2, irow=irow)
        p.Add(btn_from_rois,    icol=5, dcol=2, irow=irow+1)
        p.Add(btn_clear_elems,  icol=5, dcol=2, irow=irow+2)
        p.irow += 5

        p.Add((2, 2), newrow=True)
        p.AddText(' Step: ')
        p.Add(wids['peak_step'])
        p.Add(wids['peak_step_vary'])

        p.AddText(' Gamma : ')
        p.Add(wids['peak_gamma'])
        p.Add(wids['peak_gamma_vary'])

        p.Add((2, 2), newrow=True)
        p.AddText(' Beta: ')
        p.Add(wids['peak_beta'])
        p.Add(wids['peak_beta_vary'])

        p.AddText(' Tail: ', size=(120, -1))
        p.Add(wids['peak_tail'])
        p.Add(wids['peak_tail_vary'])
        p.Add((2, 2), newrow=True)
        p.Add(HLine(p, size=(650, 3)), dcol=8)
        p.Add((2, 2), newrow=True)

        opts = dict(size=(100, -1), min_val=0, digits=4, increment=0.010)
        for name, escale in (('elastic',  0), ('compton1', 1), ('compton2', 2)):
            en = self.mca.incident_energy
            for i in range(escale):
                en = en * (1 - 1/(1 + (E_MASS*0.001)/en))    # Compton shift at 90 deg

            wids[f'{name:s}_use'] = Check(p, label='Include', default=cnf[f'{name:s}_use'])
            p.Add((2, 2), newrow=True)
            p.AddText("  %s Peak:" % name.title(),  colour='#880000')
            p.Add(wids[f'{name:s}_use'], dcol=2)

            for att, title, xmax, xinc, newrow in (('cen',   '  Energy (kev): ', 9e12, 0.01, True),
                                                   ('step',  '  Step: ', 1, 0.005, False),
                                                   ('sigma', '  Sigma Scale:',  10, 0.05, True),
                                                   ('beta',  '  Beta: ', 10, 0.01, False),
                                                   ('tail',  '  Tail: ', 10, 0.01, True)):
                label = f'{name:s}_{att:s}'
                val = en if att == 'cen' else cnf[label]
                wids[f'{label:s}_vary'] = VarChoice(p, default=cnf[f'{label:s}_vary'])

                wids[label] = FloatSpin(p, value=val, digits=3, min_val=0,
                                        max_val=xmax, increment=xinc,
                                        tooltip=tooltips[att])

                p.AddText(title, size=(120, -1))
                p.Add(wids[label])
                p.Add(wids[f'{label:s}_vary'])
                if newrow:
                    p.Add((2, 2), newrow=True)

            p.Add(HLine(p, size=(650, 3)), dcol=7)

        p.pack()
        return p

    def beamdet_page(self, **kws):
        "beam / detector settings"
        mca = self.mca
        en_min = 2.0
        en_max = self.mca.incident_energy

        cal_offset = getattr(mca, 'offset',  0)
        cal_slope = getattr(mca, 'slope',  0.010)
        det_noise = getattr(mca, 'det_noise',  0.035)
        escape_amp = getattr(mca, 'escape_amp', 0.25)

        if not hasattr(self.mca, 'pileup_scale'):
            self.mca.predict_pileup()
        pileup_amp = max(0.001, getattr(mca, 'pileup_scale', 0.25))

        wids = self.wids
        pdet = GridPanel(self, itemstyle=LEFT)

        def addLine(pan):
            pan.Add(HLine(pan, size=(650, 3)), dcol=6, newrow=True)

        wids['escape_use'] = Check(pdet, label='Include Escape in Fit',
                                   default=True, action=self.onUsePileupEscape)
        wids['escape_amp'] = FloatSpin(pdet, value=escape_amp,
                                         min_val=0, max_val=100, digits=3,
                                         increment=0.01, size=(125, -1))

        wids['pileup_use'] = Check(pdet, label='Include Pileup in Fit',
                                   default=True,
                                   action=self.onUsePileupEscape)
        wids['pileup_amp'] = FloatSpin(pdet, value=pileup_amp,
                                         min_val=0, max_val=100, digits=3,
                                         increment=0.01, size=(125, -1))

        wids['escape_amp_vary'] = VarChoice(pdet, default=True)
        wids['pileup_amp_vary'] = VarChoice(pdet, default=(pileup_amp>0.002))


        wids['cal_slope'] = FloatSpin(pdet, value=cal_slope,
                                      min_val=0, max_val=100,
                                      digits=4, increment=0.01, size=(125, -1))
        wids['cal_offset'] = FloatSpin(pdet, value=cal_offset,
                                      min_val=-500, max_val=500,
                                      digits=4, increment=0.01, size=(125, -1))

        wids['cal_vary'] = Check(pdet, label='Vary Calibration in Fit', default=True)

        wids['det_mat'] = Choice(pdet, choices=Detector_Materials,
                                 size=(125, -1), default=0,
                                 action=self.onDetMaterial)

        wids['det_thk'] = FloatSpin(pdet, value=0.400, size=(125, -1),
                                     increment=0.010, min_val=0, max_val=10,
                                     digits=4)

        wids['det_noise_vary'] = VarChoice(pdet, default=1)

        opts = dict(size=(125, -1), min_val=0, max_val=500, digits=3,
                    increment=0.10)
        wids['en_xray'] = FloatSpin(pdet, value=self.mca.incident_energy,
                                    action=self.onSetXrayEnergy, **opts)
        wids['en_min'] = FloatSpin(pdet, value=en_min, **opts)
        wids['en_max'] = FloatSpin(pdet, value=en_max, **opts)
        wids['flux_in'] = FloatCtrl(pdet, value=5.e10, gformat=True,
                                    minval=0, size=(125, -1))

        opts.update({'increment': 0.005})
        wids['det_noise'] = FloatSpin(pdet, value=det_noise, **opts)
        wids['det_efano'] = SimpleText(pdet, size=(250, -1),
                                       label='E_Fano= %.4e' % FanoFactors['Si'])

        opts.update(digits=1, max_val=90, min_val=0, increment=1)
        wids['angle_in'] = FloatSpin(pdet, value=45, **opts)
        wids['angle_out'] = FloatSpin(pdet, value=45, **opts)

        opts.update(digits=1, max_val=5e9, min_val=0, increment=1)
        wids['det_dist'] = FloatSpin(pdet, value=50, **opts)
        wids['det_area'] = FloatSpin(pdet, value=50, **opts)

        for notyet in ('angle_in', 'angle_out', 'det_dist', 'det_area',
                       'flux_in'):
            wids[notyet].Disable()

        wids['fit_toler'] = Choice(pdet, choices=FitTols, size=(125, -1))
        wids['fit_toler'].SetStringSelection('1.e-4')
        wids['fit_step'] = Choice(pdet, choices=FitSteps, size=(125, -1))
        wids['fit_step'].SetStringSelection('1.e-4')
        wids['fit_maxnfev'] = Choice(pdet, choices=FitMaxNFevs, size=(125, -1))
        wids['fit_maxnfev'].SetStringSelection('1000')

        pdet.AddText(' Beam Energy, Fit Range :', colour='#880000', dcol=2)
        pdet.AddText('   X-ray Energy (keV): ', newrow=True)
        pdet.Add(wids['en_xray'])
        pdet.AddText('Incident Flux (Hz): ', newrow=False)
        pdet.Add(wids['flux_in'])
        pdet.AddText('   Fit Energy Min (keV): ', newrow=True)
        pdet.Add(wids['en_min'])
        pdet.AddText('Fit Energy Max (keV): ')
        pdet.Add(wids['en_max'])
        pdet.AddText('   Fit Step Size: ', newrow=True)
        pdet.Add(wids['fit_step'])
        pdet.AddText('Fit Tolerance:  ')
        pdet.Add(wids['fit_toler'])
        pdet.AddText('   Fit Max Evaluations: ', newrow=True)
        pdet.Add(wids['fit_maxnfev'])


        addLine(pdet)
        pdet.AddText(' Energy Calibration :', colour='#880000', dcol=1, newrow=True)
        pdet.Add(wids['cal_vary'], dcol=2)
        pdet.AddText('   Offset (keV): ', newrow=True)
        pdet.Add(wids['cal_offset'])
        pdet.AddText('Slope (keV/bin) :  ')
        pdet.Add(wids['cal_slope'])

        addLine(pdet)
        pdet.AddText(' Detector Material:', colour='#880000', dcol=1, newrow=True)
        pdet.AddText(EFano_Text, dcol=3)
        pdet.AddText('   Material:  ', newrow=True)
        pdet.Add(wids['det_mat'])
        pdet.Add(wids['det_efano'], dcol=2)
        pdet.AddText('   Thickness (mm): ', newrow=True)
        pdet.Add(wids['det_thk'])
        pdet.AddText('   Noise (keV): ', newrow=True)
        pdet.Add(wids['det_noise'])
        pdet.Add(wids['det_noise_vary'], dcol=2)


        addLine(pdet)
        pdet.AddText(' Escape && Pileup:', colour='#880000', dcol=2, newrow=True)
        pdet.AddText('   Escape Scale:', newrow=True)
        pdet.Add(wids['escape_amp'])
        pdet.Add(wids['escape_amp_vary'])
        pdet.Add(wids['escape_use'], dcol=3)

        pdet.AddText('   Pileup Scale:', newrow=True)
        pdet.Add(wids['pileup_amp'])
        pdet.Add(wids['pileup_amp_vary'])
        pdet.Add(wids['pileup_use'], dcol=3)

        addLine(pdet)
        pdet.AddText(' Geometry:', colour='#880000', dcol=1, newrow=True)
        pdet.AddText(Geom_Text, dcol=3)
        pdet.AddText('   Incident Angle (deg):', newrow=True)
        pdet.Add(wids['angle_in'])
        pdet.AddText('   Exit Angle (deg):', newrow=False)
        pdet.Add(wids['angle_out'])
        pdet.AddText('   Detector Distance (mm): ', newrow=True)
        pdet.Add(wids['det_dist'])
        pdet.AddText('   Detector Area (mm^2): ', newrow=False)
        pdet.Add(wids['det_area'])


        addLine(pdet)
        pdet.pack()
        return pdet

    def materials_page(self, **kws):
        "filters and matrix settings"
        wids = self.wids
        pan = GridPanel(self, itemstyle=LEFT)

        pan.AddText(' Filters :', colour='#880000', dcol=2) # , newrow=True)
        pan.AddManyText(('  Filter #', 'Material', 'Thickness (mm)',
                         'Vary Thickness'), style=LEFT, newrow=True)
        opts = dict(size=(125, -1), min_val=0, digits=5, increment=0.005)

        for i in range(NFILTERS):
            t = 'filter%d' % (i+1)
            wids['%s_mat'%t] = Choice(pan, choices=Filter_Materials, default=0,
                                      size=(150, -1),
                                      action=partial(self.onFilterMaterial, index=i+1))
            wids['%s_thk'%t] = FloatSpin(pan, value=0.0, **opts)
            wids['%s_var'%t] = VarChoice(pan, default=0)
            if i == 0: # first selection
                wids['%s_mat'%t].SetStringSelection('beryllium')
                wids['%s_thk'%t].SetValue(0.0250)
            elif i == 1: # second selection
                wids['%s_mat'%t].SetStringSelection('air')
                wids['%s_thk'%t].SetValue(50.00)
            elif i == 2: # third selection
                wids['%s_mat'%t].SetStringSelection('kapton')
                wids['%s_thk'%t].SetValue(0.00)
            elif i == 3: # third selection
                wids['%s_mat'%t].SetStringSelection('aluminum')
                wids['%s_thk'%t].SetValue(0.00)

            pan.AddText('      %i' % (i+1), newrow=True)
            pan.Add(wids['%s_mat' % t])
            pan.Add(wids['%s_thk' % t])
            pan.Add(wids['%s_var' % t])

        pan.Add(HLine(pan, size=(650, 3)), dcol=6, newrow=True)

        pan.AddText(' Matrix:', colour='#880000', newrow=True)
        pan.AddText('    NOTE: thin film limit only',  dcol=3)

        wids['matrix_mat'] = wx.TextCtrl(pan, value='', size=(275, -1))
        wids['matrix_thk'] = FloatSpin(pan, value=0.0, **opts)
        wids['matrix_den'] = FloatSpin(pan, value=1.0, **opts)
        wids['matrix_btn'] = Button(pan, 'Use Material', size=(175, -1),
                                  action=self.onUseCurrentMaterialAsFilter)
        wids['matrix_btn'].Disable()
        pan.AddText('  Material/Formula:', dcol=1, newrow=True)
        pan.Add(wids['matrix_mat'], dcol=2)
        pan.Add(wids['matrix_btn'], dcol=3)
        pan.AddText('  Thickness (mm):', newrow=True)
        pan.Add(wids['matrix_thk'])
        pan.AddText(' Density (gr/cm^3):', newrow=False)
        pan.Add(wids['matrix_den'])

        pan.Add(HLine(pan, size=(650, 3)), dcol=6, newrow=True)

        # Materials
        pan.AddText(' Known Materials:', colour='#880000', dcol=4, newrow=True)

        mview = self.owids['materials'] = dv.DataViewListCtrl(pan, style=DVSTYLE)
        mview.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.onSelectMaterial)
        self.selected_material = ''

        mview.AppendTextColumn('Name',      width=150)
        mview.AppendTextColumn('Formula',   width=325)
        mview.AppendTextColumn('density',    width=90)
        mview.AppendToggleColumn('Filter?',  width=75)
        for col in range(4):
            this = mview.Columns[col]
            align = wx.ALIGN_LEFT
            this.Sortable = True
            this.Alignment = this.Renderer.Alignment = align

        mview.SetMinSize((725, 170))
        mview.DeleteAllItems()
        self.materials_data = {}
        for name, data in materials._read_materials_db().items():
            # print("DATA " , name, data)
            formula, density = data.formula, data.density
            self.materials_data[name] = (formula, density)
            mview.AppendItem((name, formula, "%9.6f"%density,
                              name in Filter_Materials))
        pan.Add(mview, dcol=5, newrow=True)

        pan.AddText(' Add Material:', colour='#880000', newrow=True)
        pan.Add(Button(pan, 'Add', size=(175, -1),
                       action=self.onAddMaterial))
        pan.Add((10, 10))
        bx = Button(pan, 'Update Filter List', size=(175, -1),
                    action=self.onUpdateFilterList)
        pan.Add(bx)

        self.owids['newmat_name'] = wx.TextCtrl(pan, value='', size=(175, -1))
        self.owids['newmat_dens'] = FloatSpin(pan, value=1.0, **opts)
        self.owids['newmat_form'] = wx.TextCtrl(pan, value='', size=(400, -1))


        for notyet in ('matrix_mat', 'matrix_thk', 'matrix_den',
                       'matrix_btn'):
            wids[notyet].Disable()

        pan.AddText(' Name:', newrow=True)
        pan.Add(self.owids['newmat_name'])
        pan.AddText(' Density (gr/cm^3):', newrow=False)
        pan.Add(self.owids['newmat_dens'])
        pan.AddText(' Formula:', newrow=True)
        pan.Add(self.owids['newmat_form'], dcol=3)
        pan.pack()
        return pan

    def fitresult_page(self, **kws):
        sizer = wx.GridBagSizer(3, 3)
        panel = scrolled.ScrolledPanel(self)
        # title row
        wids = self.owids
        title = SimpleText(panel, 'Fit Results', font=Font(FONTSIZE+1),
                           colour=self.colors.title, style=LEFT)

        wids['data_title'] = SimpleText(panel, '< > ', font=Font(FONTSIZE+1),
                                             colour=self.colors.title, style=LEFT)

        wids['fitlabel_lab'] = SimpleText(panel, 'Fit Label:')
        wids['fitlabel_txt'] = wx.TextCtrl(panel, -1, ' ', size=(150, -1))
        wids['fitlabel_btn'] = Button(panel, 'Set Label',  size=(150, -1),
                                      action=self.onChangeFitLabel)

        opts = dict(default=False, size=(175, -1), action=self.onPlot)
        wids['plot_comps'] = Check(panel, label='Show Components?', **opts)
        self.plot_choice = Button(panel, 'Plot',
                                  size=(150, -1), action=self.onPlot)

        self.save_result = Button(panel, 'Save Model',
                                  size=(150, -1), action=self.onSaveFitResult)
        SetTip(self.save_result, 'save model and result to be loaded later')

        self.export_fit  = Button(panel, 'Export Fit',
                                  size=(150, -1), action=self.onExportFitResult)
        SetTip(self.export_fit, 'save arrays and results to text file')

        irow = 0
        sizer.Add(title,              (irow, 0), (1, 1), LEFT)
        sizer.Add(wids['data_title'], (irow, 1), (1, 3), LEFT)

        irow += 1
        sizer.Add(self.save_result,   (irow, 0), (1, 1), LEFT)
        sizer.Add(self.export_fit,    (irow, 1), (1, 1), LEFT)
        sizer.Add(self.plot_choice,   (irow, 2), (1, 1), LEFT)
        sizer.Add(wids['plot_comps'], (irow, 3), (1, 1), LEFT)

        irow += 1
        sizer.Add(wids['fitlabel_lab'], (irow, 0), (1, 1), LEFT)
        sizer.Add(wids['fitlabel_txt'], (irow, 1), (1, 1), LEFT)
        sizer.Add(wids['fitlabel_btn'], (irow, 2), (1, 2), LEFT)


        irow += 1
        sizer.Add(HLine(panel, size=(650, 3)), (irow, 0), (1, 5), LEFT)

        irow += 1
        title = SimpleText(panel, '[[Fit Statistics]]',  font=Font(FONTSIZE+1),
                           colour=self.colors.title, style=LEFT)
        sizer.Add(title, (irow, 0), (1, 4), LEFT)

        sview = wids['stats'] = dv.DataViewListCtrl(panel, style=DVSTYLE)
        sview.SetFont(self.font_fixedwidth)
        sview.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.onSelectFit)
        sview.AppendTextColumn('Fit Label', width=120)
        sview.AppendTextColumn('N_vary', width=80)
        sview.AppendTextColumn('N_eval', width=80)
        sview.AppendTextColumn('\u03c7\u00B2', width=130)
        sview.AppendTextColumn('\u03c7\u00B2_reduced', width=130)
        sview.AppendTextColumn('Akaike Info', width=130)

        for col in range(sview.ColumnCount):
            this = sview.Columns[col]
            isort, align = True, wx.ALIGN_RIGHT
            if col == 0:
                align = wx.ALIGN_LEFT
            this.Sortable = isort
            this.Alignment = this.Renderer.Alignment = align
        sview.SetMinSize((725, 150))

        irow += 1
        sizer.Add(sview, (irow, 0), (1, 5), LEFT)

        irow += 1
        sizer.Add(HLine(panel, size=(650, 3)), (irow, 0), (1, 5), LEFT)

        irow += 1
        title = SimpleText(panel, '[[Variables]]',  font=Font(FONTSIZE+1),
                           colour=self.colors.title, style=LEFT)
        sizer.Add(title, (irow, 0), (1, 1), LEFT)

        pview = wids['params'] = dv.DataViewListCtrl(panel, style=DVSTYLE)
        pview.SetFont(self.font_fixedwidth)
        wids['paramsdata'] = []
        pview.AppendTextColumn('Parameter',      width=150)
        pview.AppendTextColumn('Refined Value',  width=130)
        pview.AppendTextColumn('Standard Error', width=130)
        pview.AppendTextColumn('% Uncertainty',  width=130)
        pview.AppendTextColumn('Initial Value',  width=130)

        for col in range(4):
            this = pview.Columns[col]
            align = wx.ALIGN_LEFT
            if col > 0:
                align = wx.ALIGN_RIGHT
            this.Sortable = False
            this.Alignment = this.Renderer.Alignment = align

        pview.SetMinSize((725, 200))
        pview.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.onSelectParameter)

        irow += 1
        sizer.Add(pview, (irow, 0), (1, 5), LEFT)

        irow += 1
        sizer.Add(HLine(panel, size=(650, 3)), (irow, 0), (1, 5), LEFT)

        irow += 1
        title = SimpleText(panel, '[[Correlations]]',  font=Font(FONTSIZE+1),
                           colour=self.colors.title, style=LEFT)

        wids['all_correl'] = Button(panel, 'Show All',
                                    size=(100, -1), action=self.onAllCorrel)

        wids['min_correl'] = FloatSpin(panel, value=MIN_CORREL,
                                       min_val=0, size=(100, -1),
                                       digits=3, increment=0.1)

        ctitle = SimpleText(panel, 'minimum correlation: ')
        sizer.Add(title,  (irow, 0), (1, 1), LEFT)
        sizer.Add(ctitle, (irow, 1), (1, 1), LEFT)
        sizer.Add(wids['min_correl'], (irow, 2), (1, 1), LEFT)
        sizer.Add(wids['all_correl'], (irow, 3), (1, 1), LEFT)

        cview = wids['correl'] = dv.DataViewListCtrl(panel, style=DVSTYLE)
        cview.SetFont(self.font_fixedwidth)
        cview.AppendTextColumn('Parameter 1',    width=150)
        cview.AppendTextColumn('Parameter 2',    width=150)
        cview.AppendTextColumn('Correlation',    width=150)

        for col in (0, 1, 2):
            this = cview.Columns[col]
            this.Sortable = False
            align = wx.ALIGN_LEFT
            if col == 2:
                align = wx.ALIGN_RIGHT
            this.Alignment = this.Renderer.Alignment = align
        cview.SetMinSize((725, 125))

        irow += 1
        sizer.Add(cview, (irow, 0), (1, 5), LEFT)
        pack(panel, sizer)
        panel.SetMinSize((725, 750))
        panel.SetupScrolling()
        return panel

    def composition_page(self, **kws):
        sizer = wx.GridBagSizer(3, 3)
        panel = scrolled.ScrolledPanel(self)
        wids = self.owids
        title = SimpleText(panel, 'Composition Results', font=Font(FONTSIZE+1),
                           colour=self.colors.title, style=LEFT)
        wids['data_title2'] = SimpleText(panel, '< > ', font=Font(FONTSIZE+1),
                                             colour=self.colors.title, style=LEFT)

        cview = wids['composition'] = dv.DataViewListCtrl(panel, style=DVSTYLE)
        cview.SetFont(self.font_fixedwidth)
        cview.AppendTextColumn(' Z ', width=50)
        cview.AppendTextColumn(' Element ', width=100)
        cview.AppendTextColumn(' Amplitude', width=170)
        cview.AppendTextColumn(' Concentration',  width=170)
        cview.AppendTextColumn(' Uncertainty',  width=180)

        for col in range(5):
            this = cview.Columns[col]
            align = wx.ALIGN_RIGHT
            if col ==  1:
                align = wx.ALIGN_LEFT
            this.Sortable = True
            this.Alignment = this.Renderer.Alignment = align

        cview.SetMinSize((725, 500))
        wids['comp_fitlabel'] = Choice(panel, choices=[''], size=(175, -1),
                                       action=self.onCompSelectFit)

        self.compscale_lock = 0.0
        wids['comp_elemchoice'] = Choice(panel, choices=[''], size=(125, -1))
        # action=self.onCompSetElemAbundance)
        wids['comp_elemscale'] = FloatSpin(panel, value=1.0, digits=5, min_val=0,
                                           increment=0.01,
                                           action=self.onCompSetElemAbundance)
        wids['comp_units'] = Choice(panel, choices=CompositionUnits, size=(125, -1))
        wids['comp_scale'] = FloatCtrl(panel, value=0, size=(200, -1), precision=5,
                                       minval=0, action=self.onCompSetScale)

        wids['comp_save'] = Button(panel, 'Save This Concentration Data',
                                   size=(200, -1), action=self.onCompSave)

        irow = 0
        sizer.Add(title,              (irow, 0), (1, 2), LEFT)
        sizer.Add(wids['data_title2'], (irow, 2), (1, 5), LEFT)
        irow += 1
        sizer.Add(SimpleText(panel, 'Fit Label:'),  (irow, 0), (1, 1), LEFT)
        sizer.Add(wids['comp_fitlabel'],            (irow, 1), (1, 5), LEFT)

        irow += 1
        sizer.Add(SimpleText(panel, 'Scale Element:'),   (irow, 0), (1, 1), LEFT)
        sizer.Add(wids['comp_elemchoice'],         (irow, 1), (1, 1), LEFT)
        sizer.Add(SimpleText(panel, ' to:'),       (irow, 2), (1, 1), LEFT)
        sizer.Add(wids['comp_elemscale'],          (irow, 3), (1, 1), LEFT)
        sizer.Add(wids['comp_units'],              (irow, 4), (1, 1), LEFT)

        irow += 1
        sizer.Add(SimpleText(panel, 'Scaling Factor:'), (irow, 0), (1, 1), LEFT)
        sizer.Add(wids['comp_scale'],              (irow, 1), (1, 3), LEFT)

        irow += 1
        sizer.Add(wids['composition'],   (irow, 0), (3, 6), LEFT)

        irow += 3
        sizer.Add(wids['comp_save'],   (irow, 0), (1, 3), LEFT)

        pack(panel, sizer)
        panel.SetMinSize((725, 750))
        panel.SetupScrolling()
        return panel

    def onCompSetScale(self, event=None, value=None):
        if len(self.xrfresults) < 1 or (time.time() - self.compscale_lock) < 0.25:
            return
        self.compscale_lock = time.time()
        owids = self.owids
        result = self.get_fitresult(nfit=owids['comp_fitlabel'].GetSelection())
        cur_elem  = owids['comp_elemchoice'].GetStringSelection()
        conc_vals = {}
        for elem in result.comps.keys():
            parname = 'amp_%s' % elem.lower()
            if parname in result.params:
                par = result.params[parname]
                conc_vals[elem] = [par.value, par.stderr]

        try:
            scale = self.owids['comp_scale'].GetValue()
        except:
            return

        owids['comp_elemscale'].SetValue(conc_vals[cur_elem][0]*scale)
        owids['composition'].DeleteAllItems()
        result.concentration_results = conc_vals
        result.concentration_scale = scale

        for elem, dat in conc_vals.items():
            zat = "%d" % atomic_number(elem)
            val, serr = dat
            rval = "%15.4f" % val
            sval = "%15.4f" % (val*scale)
            uval = "%15.4f" % (serr*scale)
            try:
                uval = uval + ' ({:.2%})'.format(abs(serr/val))
            except ZeroDivisionError:
                pass
            owids['composition'].AppendItem((zat, elem, rval, sval, uval))

    def onCompSetElemAbundance(self, event=None, value=None):
        if len(self.xrfresults) < 1  or (time.time() - self.compscale_lock) < 0.25:
            return
        self.compscale_lock = time.time()
        owids = self.owids
        result = self.get_fitresult(nfit=owids['comp_fitlabel'].GetSelection())
        cur_elem = owids['comp_elemchoice'].GetStringSelection()
        conc_vals = {}
        for elem in result.comps.keys():
            parname = 'amp_%s' % elem.lower()
            if parname in result.params:
                par = result.params[parname]
                conc_vals[elem] = [par.value, par.stderr]

        result.concentration_results = conc_vals
        elem_value = owids['comp_elemscale'].GetValue()

        scale = elem_value/conc_vals[cur_elem][0]
        result.concentration_scale = scale
        owids['comp_scale'].SetValue(scale)
        owids['composition'].DeleteAllItems()
        for elem, dat in conc_vals.items():
            zat = "%d" % atomic_number(elem)
            val, serr = dat
            rval = "%15.4f" % val
            sval = "%15.4f" % (val*scale)
            uval = "%15.4f" % (serr*scale)
            try:
                uval = uval + ' ({:.2%})'.format(abs(serr/val))
            except ZeroDivisionError:
                pass
            owids['composition'].AppendItem((zat, elem, rval, sval, uval))


    def onCompSave(self, event=None):
        result = self.get_fitresult(nfit=self.owids['comp_fitlabel'].GetSelection())
        scale = result.concentration_scale

        deffile = self.mca.label + '_' + result.label
        deffile = fix_filename(deffile.replace('.', '_')) + '_xrf.csv'
        deffile = Path(deffile).as_posix()

        wcards = "CSV (*.csv)|*.csv|All files (*.*)|*.*"
        sfile = FileSave(self, 'Save Concentration Results',
                         default_file=deffile,
                         wildcard=wcards)
        if sfile is not None:
            buff = ["# results for MCA labeled: %s" % self.mca.label,
                    "# fit label: %s" % result.label,
                    "# concentration units: %s" % self.owids['comp_units'].GetStringSelection(),
                    "# count time: %s" % result.count_time,
                    "# scale: %s" % result.concentration_scale,
                    "# Fit Report:"     ]
            for l in result.fit_report.split('\n'):
                buff.append("#    %s" % l)
            buff.append("###########")
            buff.append("#Element  Concentration  Uncertainty  Raw_Amplitude")
            for elem, dat in result.concentration_results.items():
                eout = (elem  + ' '*4)[:4]
                val, serr = dat
                rval = "%15.4f" % val
                sval = "%15.4f" % (val*scale)
                uval = "%15.4f" % (serr*scale)
                buff.append("  ".join([eout, sval, uval, rval]))
            buff.append('')
            with open(sfile, 'w', encoding=sys.getdefaultencoding()) as fh:
                fh.write('\n'.join(buff))

    def onCompSelectFit(self, event=None):
        result = self.get_fitresult(nfit=self.owids['comp_fitlabel'].GetSelection())
        cur_elem  = self.owids['comp_elemchoice'].GetStringSelection()
        self.owids['comp_elemchoice'].Clear()
        elems = [el['symbol'] for el in result.elements]
        self.owids['comp_elemchoice'].SetChoices(elems)
        if len(cur_elem) > 0:
            self.owids['comp_elemchoice'].SetStringSelection(cur_elem)
        else:
            self.owids['comp_elemchoice'].SetSelection(0)
        self.onCompSetElemAbundance()

    def UpdateCompositionPage(self, event=None):
        self.xrfresults = self._larch.symtable.get_symbol(XRFRESULTS_GROUP)
        if len(self.xrfresults) > 0:
            result = self.get_fitresult()
            fitlab = self.owids['comp_fitlabel']
            fitlab.Clear()
            fitlab.SetChoices([a.label for a in self.xrfresults])
            fitlab.SetStringSelection(result.label)
            self.onCompSelectFit()

    def onElems_Clear(self, event=None):
        self.ptable.on_clear_all()

    def onElems_GuessPeaks(self, event=None):
        mca = self.mca
        _indices = peak_indices(mca.counts*1.0, min_dist=5, threshold=0.025)
        peak_energies = mca.energy[_indices]

        elrange = range(10, 92)
        atsyms  = [atomic_symbol(i) for i in elrange]
        kalphas = [0.001*xray_line(i, 'Ka').energy for i in elrange]
        kbetas  = [0.001*xray_line(i, 'Kb').energy for i in elrange]
        self.ptable.on_clear_all()
        elems = []
        for iz, en in enumerate(peak_energies):
            for i, ex in enumerate(kalphas):
                if abs(en - ex) < 0.025:
                    elems.append(atsyms[i])
                    peak_energies[iz] = -ex

        for iz, en in enumerate(peak_energies):
            if en > 0:
                for i, ex in enumerate(kbetas):
                    if abs(en - ex) < 0.025:
                        if atsyms[i] not in elems:
                            elems.append(atsyms[i])
                        peak_energies[iz] = -ex

        en = self.wids['en_xray'].GetValue()
        emin = self.wids['en_min'].GetValue()
        for elem in elems:
            kedge  = 0.001*xray_edge(elem, 'K').energy
            l3edge = 0.001*xray_edge(elem, 'L3').energy
            l2edge = 0.001*xray_edge(elem, 'L3').energy
            if ((kedge < en and kedge > emin) or
                (l3edge < en and l3edge > emin) or
                (l2edge < en and l2edge > emin)):
                if elem not in self.ptable.selected:
                    self.ptable.onclick(label=elem)

    def onElems_FromROIS(self, event=None):
        for roi in self.mca.rois:
            words = roi.name.split()
            elem = words[0].title()
            if (elem in self.ptable.syms and
                elem not in self.ptable.selected):
                self.ptable.onclick(label=elem)
        self.onSetXrayEnergy()

    def onSetXrayEnergy(self, event=None):
        en = self.wids['en_xray'].GetValue()
        self.wids['en_max'].SetValue(en)
        self.wids['elastic_cen'].SetValue(en)
        self.wids['compton1_cen'].SetValue(en*0.975)
        self.wids['compton2_cen'].SetValue(en*0.950)
        emin = self.wids['en_min'].GetValue() * 1.25

        self.ptable.on_clear_all()
        for roi in self.mca.rois:
            words = roi.name.split()
            elem = words[0].title()
            kedge = l3edge = l2edge = 0.0
            try:
                kedge  = 0.001*xray_edge(elem, 'K').energy
                l3edge = 0.001*xray_edge(elem, 'L3').energy
                l2edge = 0.001*xray_edge(elem, 'L3').energy
            except:
                pass
            if ((kedge < en and kedge > emin) or
                (l3edge < en and l3edge > emin) or
                (l2edge < en and l2edge > emin)):
                if elem not in self.ptable.selected:
                    self.ptable.onclick(label=elem)

    def onDetMaterial(self, event=None):
        dmat = self.wids['det_mat'].GetStringSelection()
        if dmat not in FanoFactors:
            dmat = 'Si'
        self.wids['det_efano'].SetLabel('E_Fano= %.4e' % FanoFactors[dmat])

    def onFilterMaterial(self, evt=None, index=1):
        name = evt.GetString()
        den = self.materials_data.get(name, (None, 1.0))[1]
        t = 'filter%d' % (index)
        thick = self.wids['%s_thk'%t]
        if den < 0.1 and thick.GetValue() < 0.1:
            thick.SetValue(10.0)
            thick.SetIncrement(0.5)
        elif den > 0.1 and thick.GetValue() < 1.e-5:
            thick.SetValue(0.0250)
            thick.SetIncrement(0.005)

    def onUseCurrentMaterialAsFilter(self, evt=None):
        name = self.selected_material
        density = self.materials_data.get(name, (None, 1.0))[1]
        self.wids['matrix_den'].SetValue(density)
        self.wids['matrix_mat'].SetValue(name)

    def onSelectMaterial(self, evt=None):
        if self.owids['materials'] is None:
            return
        item = self.owids['materials'].GetSelectedRow()
        name = None
        if item > -1:
            name = list(self.materials_data.keys())[item]
            self.selected_material = name

        self.wids['matrix_btn'].Enable(name is not None)
        if name is not None:
            self.wids['matrix_btn'].SetLabel('Use %s'  % name)

    def onUpdateFilterList(self, evt=None):
        flist = ['None']
        for i in range(len(self.materials_data)):
            if self.owids['materials'].GetToggleValue(i, 3): # is filter
                flist.append(self.owids['materials'].GetTextValue(i, 0))

        for i in range(NFILTERS):
            t = 'filter%d' % (i+1)
            choice = self.wids['%s_mat'%t]
            cur = choice.GetStringSelection()
            choice.Clear()
            choice.SetChoices(flist)
            if cur in flist:
                choice.SetStringSelection(cur)
            else:
                choice.SetSelection(0)

    def onAddMaterial(self, evt=None):
        name    = self.owids['newmat_name'].GetValue()
        formula = self.owids['newmat_form'].GetValue()
        density = self.owids['newmat_dens'].GetValue()
        add = len(name) > 0 and len(formula)>0
        if add and name in self.materials_data:
            add = (Popup(self,
                         "Overwrite definition of '%s'?" % name,
                         'Re-define material?',
                         style=wx.OK|wx.CANCEL)==wx.ID_OK)
            if add:
                irow = list(self.materials_data.keys()).index(name)
                self.owids['materials'].DeleteItem(irow)
        if add:
            add_material(name, formula, density)
            self.materials_data[name] = (formula, density)
            self.selected_material = name
            self.owids['materials'].AppendItem((name, formula,
                                                "%9.6f"%density,
                                                False))

    def onElemSelect(self, event=None, elem=None):
        self.ptable.tsym.SetLabel('')
        self.ptable.title.SetLabel('%d elements selected' %
                                   len(self.ptable.selected))

    def onUsePileupEscape(self, event=None):
        puse = self.wids['pileup_use'].IsChecked()
        self.wids['pileup_amp'].Enable(puse)
        self.wids['pileup_amp_vary'].Enable(puse)

        puse = self.wids['escape_use'].IsChecked()
        self.wids['escape_amp'].Enable(puse)
        self.wids['escape_amp_vary'].Enable(puse)


    def onUsePeak(self, event=None, name=None, value=None):
        if value is None and event is not None:
            value = event.IsChecked()
        if name is None:
            return
        for a in ('cen', 'step', 'tail', 'sigma', 'beta'):
            self.wids['%s_%s'%(name, a)].Enable(value)
            varwid = self.wids.get('%s_%s_vary'%(name, a), None)
            if varwid is not None:
                varwid.Enable(value)

    def build_model(self, match_amplitudes=True):
        """build xrf_model from form settings"""
        vars = {'Vary':'True', 'Fix': 'False', 'True':True, 'False': False}
        opts = {}
        for key, wid in self.wids.items():
            val = None
            if hasattr(wid, 'GetValue'):
                val = wid.GetValue()
            elif hasattr(wid, 'IsChecked'):
                val = wid.IsChecked()
            elif isinstance(wid, Choice):
                val = wid.GetStringSelection()
            elif hasattr(wid, 'GetStringSelection'):
                val = wid.GetStringSelection()
            elif hasattr(wid, 'GetLabel'):
                val = wid.GetLabel()
            if isinstance(val, str) and val.title() in vars:
                val = vars[val.title()]
            opts[key] = val
        opts['count_time'] = getattr(self.mca, 'real_time', 1.0)
        if opts['count_time'] is None:
            opts['count_time'] = 1.0
        opts['datetime'] = time.ctime()
        opts['mca_label'] = self.mca_label
        opts['mcagroup'] = self.mcagroup
        opts['XRFGROUP'] = XRFGROUP
        script = [xrfmod_setup.format(**opts)]

        for peakname in ('Elastic', 'Compton1', 'Compton2'):
            t = peakname.lower()
            if opts['%s_use'% t]:
                d = {'peakname': t}
                d['_cen']  = opts['%s_cen'%t]
                d['vcen']  = opts['%s_cen_vary'%t]
                d['_step'] = opts['%s_step'%t]
                d['vstep'] = opts['%s_step_vary'%t]
                d['_tail'] = opts['%s_tail'%t]
                d['vtail'] = opts['%s_tail_vary'%t]
                d['_beta'] = opts['%s_beta'%t]
                d['vbeta'] = opts['%s_beta_vary'%t]
                d['_sigma'] = opts['%s_sigma'%t]
                d['vsigma'] = opts['%s_sigma_vary'%t]
                script.append(xrfmod_scattpeak.format(**d))

        for i in range(NFILTERS):
            t = 'filter%d' % (i+1)
            f_mat = opts['%s_mat'%t]
            if f_mat not in (None, 'None') and int(1e6*opts['%s_thk'%t]) > 1:
                script.append(xrfmod_filter.format(name=f_mat,
                                                   thick=opts['%s_thk'%t],
                                                   vary=opts['%s_var'%t]))

        m_mat = opts['matrix_mat'].strip()
        if len(m_mat) > 0 and int(1e6*opts['matrix_thk']) > 1:
            script.append(xrfmod_matrix.format(name=m_mat,
                                               thick=opts['matrix_thk'],
                                               density=opts['matrix_den']))

        if opts['pileup_use'] in ('True', True):
            script.append(xrfmod_pileup.format(scale=opts['pileup_amp'],
                                               vary=opts['pileup_amp_vary']))

        if opts['escape_use'] in ('True', True):
            script.append(xrfmod_escape.format(scale=opts['escape_amp'],
                                               vary=opts['escape_amp_vary']))

        # sort elements selected on Periodic Table by Z
        elemz = []
        for elem in self.ptable.selected:
            elemz.append( 1 + self.ptable.syms.index(elem))
        elemz.sort()
        opts['elements'] = elemz

        xrfgroup = self._larch.symtable.get_group(XRFGROUP)
        setattr(xrfgroup, 'fitconfig', opts)
        json_dump(opts, Path(user_larchdir, 'xrf_fitconfig.json'))


        syms = ["'%s'" % self.ptable.syms[iz-1] for iz in elemz]
        syms = '[%s]' % (', '.join(syms))
        script.append(xrfmod_elems.format(elemlist=syms))

        script.append("# set initial estimate of xrf intensity")
        script.append("{XRFGROUP}.workmca.xrf_init = _xrfmodel.calc_spectrum({XRFGROUP}.workmca.energy)")
        script = '\n'.join(script)
        self.model_script = script.format(group=self.mcagroup, XRFGROUP=XRFGROUP)

        self._larch.eval(self.model_script)

        cmds = []
        self._larch.symtable.get_symbol('_xrfmodel')
        self.xrfmod = self._larch.symtable.get_symbol('_xrfmodel')
        floor = 1.e-12*max(self.mca.counts)

        if match_amplitudes:
            total = 0.0 * self.mca.counts
            for name, parr in self.xrfmod.comps.items():
                nam = name.lower()
                try:
                    imax = np.where(parr > 0.99*parr.max())[0][0]
                except:  # probably means all counts are zero
                    imax = int(len(parr)/2.0)
                scale = 2.0*self.mca.counts[imax] / (parr[imax]+1.00)
                ampname = 'amp_%s' % nam
                if nam in ('elastic', 'compton1', 'compton2', 'compton',
                           'background', 'pileup', 'escape'):
                    ampname = f'{nam}_amp'
                    if nam in ('background', 'pileup', 'escape'):
                        scale = 1.0
                    if nam in ('compton2',):
                        scale *= 0.5

                paramval = self.xrfmod.params[ampname].value
                s = f"_xrfmodel.params['{ampname}'].value = {paramval*scale:.5f}"
                cmds.append(s)
                parr *= scale
                parr[np.where(parr<floor)] = floor
                total += parr
            self.xrfmod.current_model = total
            script = '\n'.join(cmds)
            self._larch.eval(script)
            self.model_script = f"{self.model_script}\n{script}"

        s = f"{XRFGROUP}.workmca.xrf_init = _xrfmodel.calc_spectrum({XRFGROUP}.workmca.energy)"
        self._larch.eval(s)

    def plot_model(self, model_spectrum=None, init=False, with_comps=False,
                   label=None):
        conf = self.parent.conf

        plotkws = {'linewidth': 2.5, 'delay_draw': True, 'grid': False,
                   'ylog_scale': self.parent.ylog_scale, 'show_legend': False,
                   'fullbox': False}

        ppanel = self.parent.panel
        ppanel.conf.reset_trace_properties()
        self.parent.plot(self.mca.energy, self.mca.counts, mca=self.mca,
                         xlabel='E (keV)', xmin=0, with_rois=False, **plotkws)

        if model_spectrum is None:
            model_spectrum = self.xrfmod.current_model if init else self.xrfmod.best_fit
        if label is None:
            label = 'model' if init else 'best fit'

        self.parent.oplot(self.mca.energy, model_spectrum,
                          label=label, color=conf.fit_color, **plotkws)

        comp_traces = []
        plotkws.update({'fill': True, 'alpha':0.35, 'show_legend': True})
        for label, arr in self.xrfmod.comps.items():
            ppanel.oplot(self.mca.energy, arr, label=label, **plotkws)
            comp_traces.append(ppanel.conf.ntrace - 1)


        yscale = {False:'linear', True:'log'}[self.parent.ylog_scale]
        ppanel.set_logscale(yscale=yscale)
        ppanel.set_viewlimits()
        ppanel.conf.auto_margins = False
        ppanel.conf.set_margins(0.1, 0.02, 0.20, 0.1)
        ppanel.conf.set_legend_location('upper right', False)
        ppanel.conf.show_legend_frame = True
        ppanel.conf.draw_legend(show=True, delay_draw=False)

        if not with_comps:
            for obj, data in ppanel.conf.legend_map.items():
                line, trace, legline, legtext = data
                if trace in comp_traces:
                    legline.set_alpha(0.50)
                    legtext.set_alpha(0.50)
                    line.set_visible(False)
                    ppanel.conf.fills[trace].set_visible(False)
        ppanel.draw()

    def onShowModel(self, event=None):
        self.build_model()
        self.plot_model(init=True, with_comps=False)
        self.wids['fit_message'].SetLabel("Initial Model Built")

    def onFitIteration(self, iter=0, pars=None):
        if iter % 10 == 0:
            nvar = len([p for p in pars.values() if p.vary])
            print(f"XRF Fit iteration {iter}, {nvar} variables")
        # pass


    def onFitModel(self, event=None):
        self.build_model()
        xrfmod = self._larch.symtable.get_symbol('_xrfmodel')
        xrfmod.iter_callback = self.onFitIteration

        fit_tol = float(self.wids['fit_toler'].GetStringSelection())
        fit_step = float(self.wids['fit_step'].GetStringSelection())
        max_nfev = int(self.wids['fit_maxnfev'].GetStringSelection())
        emin = float(self.wids['en_min'].GetValue())
        emax = float(self.wids['en_max'].GetValue())

        fit_script = xrfmod_fitscript.format(group=self.mcagroup,
                                             XRFGROUP=XRFGROUP,
                                             emin=emin, emax=emax,
                                             fit_toler=fit_tol,
                                             fit_step=fit_step,
                                             max_nfev=max_nfev)
        # print("-- > ", fit_script)

        self._larch.eval(fit_script)
        dgroup = self._larch.symtable.get_group(self.mcagroup)
        self.xrfresults = self._larch.symtable.get_symbol(XRFRESULTS_GROUP)

        try:
            xrfresult = self.xrfresults[0]
            self.wids['fit_message'].SetLabel("Fit Complete")
        except:
            self.wids['fit_message'].SetLabel("fit failed, cannot get result")
            return

        xrfresult.script = "%s\n%s" % (self.model_script, fit_script)
        xrfresult.label = "fit %d" % (len(self.xrfresults))
        self.plot_model(init=True, with_comps=False)
        for i in range(len(self.nb.pagelist)):
            if self.nb.GetPageText(i).strip().startswith('Fit R'):
                self.nb.SetSelection(i)
        time.sleep(0.002)
        self.show_results()

    def onClose(self, event=None):
        self.Destroy()

    def onSaveFitResult(self, event=None):
        result = self.get_fitresult()
        deffile = self.mca.label + '_' + result.label
        deffile = fix_filename(deffile.replace('.', '_')) + '.xrfmodel'
        deffile = Path(deffile).as_posix()
        ModelWcards = "XRF Models(*.xrfmodel)|*.xrfmodel|All files (*.*)|*.*"
        sfile = FileSave(self, 'Save XRF Model', default_file=deffile,
                         wildcard=ModelWcards)
        if sfile is not None:
            self._larch.eval(xrfmod_savejs.format(group=self.mcagroup,
                                                  nfit=self.nfit,
                                                  filename=sfile))

    def onExportFitResult(self, event=None):
        result = self.get_fitresult()
        deffile = self.mca.label + '_' + result.label
        deffile = fix_filename(deffile.replace('.', '_')) + '_xrf.txt'
        deffile = Path(deffile).as_posix()
        wcards = 'All files (*.*)|*.*'
        outfile = FileSave(self, 'Export Fit Result', default_file=deffile)
        if outfile is not None:
            buff = ['# XRF Fit %s: %s' % (self.mca.label, result.label),
                    '## Fit Script:']
            for a in result.script.split('\n'):
                buff.append('#   %s' % a)
            buff.append('## Fit Report:')
            for a in result.fit_report.split('\n'):
                buff.append('#   %s' % a)

            buff.append('#')
            buff.append('########################################')

            labels = ['energy', 'counts', 'best_fit',
                      'best_energy', 'fit_window',
                      'fit_weight', 'attenuation']
            labels.extend(list(result.comps.keys()))

            buff.append('# %s' % (' '.join(labels)))

            npts = len(self.mca.energy)
            for i in range(npts):
                dline = [gformat(self.mca.energy[i]),
                         gformat(self.mca.counts[i]),
                         gformat(result.best_fit[i]),
                         gformat(result.best_en[i]),
                         gformat(result.fit_window[i]),
                         gformat(result.fit_weight[i]),
                         gformat(result.atten[i])]
                for c in result.comps.values():
                    dline.append(gformat(c[i]))
                buff.append(' '.join(dline))
            buff.append('\n')
            with open(outfile, 'w', encoding=sys.getdefaultencoding()) as fh:
                fh.write('\n'.join(buff))

    def get_fitresult(self, nfit=None):
        if nfit is None:
            nfit = self.nfit

        self.xrfresults = self._larch.symtable.get_symbol(XRFRESULTS_GROUP)
        self.nfit = max(0, nfit)
        self.nfit = min(self.nfit, len(self.xrfresults)-1)
        return self.xrfresults[self.nfit]

    def onChangeFitLabel(self, event=None):
        label = self.owids['fitlabel_txt'].GetValue()
        result = self.get_fitresult()
        result.label = label
        self.show_results()

    def onPlot(self, event=None):
        result = self.get_fitresult()
        xrfmod = self._larch.symtable.get_symbol('_xrfmodel')
        with_comps = self.owids['plot_comps'].IsChecked()
        spect = xrfmod.calc_spectrum(self.mca.energy,
                                     params=result.params)
        self.plot_model(model_spectrum=spect, with_comps=with_comps,
                        label=result.label)

    def onSelectFit(self, evt=None):
        if self.owids['stats'] is None:
            return
        item = self.owids['stats'].GetSelectedRow()
        if item > -1:
            self.show_fitresult(nfit=item)

    def onSelectParameter(self, evt=None):
        if self.owids['params'] is None:
            return
        if not self.owids['params'].HasSelection():
            return
        item = self.owids['params'].GetSelectedRow()
        pname = self.owids['paramsdata'][item]

        cormin= self.owids['min_correl'].GetValue()
        self.owids['correl'].DeleteAllItems()

        result = self.get_fitresult()
        this = result.params[pname]
        if this.correl is not None:
            sort_correl = sorted(this.correl.items(), key=lambda it: abs(it[1]))
            for name, corval in reversed(sort_correl):
                if abs(corval) > cormin:
                    self.owids['correl'].AppendItem((pname, name, "% .4f" % corval))

    def onAllCorrel(self, evt=None):
        result = self.get_fitresult()
        params = result.params
        parnames = list(params.keys())

        cormin= self.owids['min_correl'].GetValue()
        correls = {}
        for i, name in enumerate(parnames):
            par = params[name]
            if not par.vary:
                continue
            if hasattr(par, 'correl') and par.correl is not None:
                for name2 in parnames[i+1:]:
                    if (name != name2 and name2 in par.correl and
                            abs(par.correl[name2]) > cormin):
                        correls["%s$$%s" % (name, name2)] = par.correl[name2]

        sort_correl = sorted(correls.items(), key=lambda it: abs(it[1]))
        sort_correl.reverse()

        self.owids['correl'].DeleteAllItems()

        for namepair, corval in sort_correl:
            name1, name2 = namepair.split('$$')
            self.owids['correl'].AppendItem((name1, name2, "% .4f" % corval))

    def show_results(self):
        cur = self.get_fitresult()
        self.owids['stats'].DeleteAllItems()
        for i, res in enumerate(self.xrfresults):
            args = [res.label]
            for attr in ('nvarys', 'nfev', 'chisqr', 'redchi', 'aic'):
                val = getattr(res, attr)
                if isinstance(val, int):
                    val = '%d' % val
                else:
                    val = gformat(val, 11)
                args.append(val)
            self.owids['stats'].AppendItem(tuple(args))
        self.owids['data_title'].SetLabel("%s:  %.3f sec" % (self.mca.label, cur.count_time))
        self.owids['data_title2'].SetLabel("%s:  %.3f sec" % (self.mca.label, cur.count_time))
        self.owids['fitlabel_txt'].SetValue(cur.label)
        self.show_fitresult(nfit=self.nfit)

    def show_fitresult(self, nfit=0, mca=None):
        if mca is not None:
            self.mca = mca
        result = self.get_fitresult(nfit=nfit)

        self.owids['data_title'].SetLabel("%s:  %.3f sec" % (self.mca.label, result.count_time))
        self.owids['data_title2'].SetLabel("%s:  %.3f sec" % (self.mca.label, result.count_time))
        self.result = result
        self.owids['fitlabel_txt'].SetValue(result.label)
        self.owids['params'].DeleteAllItems()
        self.owids['paramsdata'] = []
        for param in reversed(result.params.values()):
            pname = param.name
            try:
                val = gformat(param.value, 10)
            except (TypeError, ValueError):
                val = ' ??? '
            serr, perr = ' N/A ', ' N/A '
            if param.stderr is not None:
                serr = gformat(param.stderr, 10)
                try:
                    perr = '{:.3f}'.format(100.0*abs(param.stderr/param.value))
                except ZeroDivisionError:
                    perr = '?'
            extra = ' '
            if param.expr is not None:
                extra = ' = %s ' % param.expr
            elif not param.vary:
                extra = ' (fixed)'
            elif param.init_value is not None:
                extra = gformat(param.init_value, 10)

            self.owids['params'].AppendItem((pname, val, serr, perr, extra))
            self.owids['paramsdata'].append(pname)
        self.Refresh()
