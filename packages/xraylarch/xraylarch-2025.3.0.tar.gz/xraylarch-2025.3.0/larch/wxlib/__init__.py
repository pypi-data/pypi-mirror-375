#!/usr/bin/env python
"""
wx widgets for Larch
"""
__DOC__ = '''
WxPython functions for larch

function         description
------------     ------------------------------
gcd              graphical change directory - launch browser to select working folder
fileprompt       launch file browser to select files.

'''

import locale
from pathlib import Path

from pyshortcuts import uname, fix_filename
import os
import sys
HAS_WXPYTHON = False
try:
    import wx
    HAS_WXPYTHON = True
except (ImportError, AttributeError):
    HAS_WXPYTHON = False

_larch_name = '_sys.wx'
_larch_builtins = {}

FONTSIZE = 8
FONTSIZE_FW = 8
if uname == 'win':
    FONTSIZE = 10
    FONTSIZE_FW = 11
    locale.setlocale(locale.LC_ALL, 'C')
elif uname == 'darwin':
    FONTSIZE = 11
    FONTSIZE_FW = 12

def fontsize(fixed_width=False):
    """return best default fontsize"""
    font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    if uname not in ('win', 'darwin'):
        font = font.Smaller()
    elif fixed_width:
        font = font.Larger()
    return int(font.GetFractionalPointSize())


def Font(size, serif=False, fixed_width=False):
    """define a font by size and serif/ non-serif
    f = Font(10, serif=True)
    """
    family = wx.DEFAULT
    if not serif:
        family = wx.SWISS
    if fixed_width:
        family = wx.MODERN
    return wx.Font(size, family, wx.NORMAL, wx.BOLD, 0, "")

def get_font(larger=0, smaller=0, serif=False, fixed_width=False):
    "return a font"
    fnt = Font(fontsize(fixed_width=fixed_width),
               serif=serif, fixed_width=fixed_width)
    for i in range(larger):
        fnt = fnt.Larger()
    for i in range(smaller):
        fnt = fnt.Smaller()
    return fnt


def DarwinHLine(parent, size=(700, 3)):
    """Horizontal line for MacOS
    h = HLine(parent, size=(700, 3)
    """
    msize = (size[0], int(size[1]*0.75))
    line = wx.Panel(parent, size=msize)
    line.SetBackgroundColour((196,196,196))
    return line

DARK_THEME = False
try:
    import darkdetect
    DARK_THEME = darkdetect.isDark()
except ImportError:
    DARK_THEME = False

def nullfunc(*args, **kws):
    pass

_larch_builtins = {'_sys.wx': dict(gcd=nullfunc,
                                   databrowser=nullfunc,
                                   fileprompt=nullfunc,
                                   wx_update=nullfunc)}

_larch_builtins['_plotter'] = dict(plot=nullfunc,
                                   oplot=nullfunc,
                                   newplot=nullfunc,
                                   plot_text=nullfunc,
                                   plot_marker=nullfunc,
                                   plot_arrow=nullfunc,
                                   plot_setlimits=nullfunc,
                                   plot_axvline=nullfunc,
                                   plot_axhline=nullfunc,
                                   scatterplot=nullfunc,
                                   hist=nullfunc,
                                   update_trace=nullfunc,
                                   save_plot=nullfunc,
                                   save_image=nullfunc,
                                   get_display=nullfunc,
                                   close_all_displays=nullfunc,
                                   get_cursor=nullfunc,
                                   last_cursor_pos=nullfunc,
                                   imshow=nullfunc,
                                   contour=nullfunc,
                                   xrf_plot=nullfunc,
                                   xrf_oplot=nullfunc,
                                   fit_plot=nullfunc)

if HAS_WXPYTHON:
    from wxutils import (set_sizer, pack, SetTip, HLine, Check,
                         MenuItem, Popup, RIGHT, LEFT, CEN , LTEXT,
                         FRAMESTYLE, hms, DateTimeCtrl, Button,
                         TextCtrl, ToggleButton, BitmapButton, Choice,
                         YesNo, SimpleText, LabeledTextCtrl,
                         HyperText, get_icon, OkCancel,
                         SavedParameterDialog, GridPanel, RowPanel,
                         make_steps, set_float, FloatCtrl,
                         EditableListBox,
                         FileDropTarget, NumericCombo, FloatSpin,
                         FileOpen, FileSave, SelectWorkdir,
                         FloatSpinWithPin, flatnotebook,
                         PeriodicTablePanel, gcd, ExceptionPopup,
                         show_wxsizes, panel_pack)

    from .filechecklist import FileCheckList
    from .wxcolors import COLORS, GUIColors, GUI_COLORS, set_color
    from . import larchframe
    from . import larchfilling
    from . import readlinetextctrl

    from .larchframe import LarchFrame, LarchPanel
    from .columnframe import ColumnDataFileFrame, EditColumnFrame
    from .athena_importer import AthenaImporter
    from .specfile_importer import SpecfileImporter
    from .xas_importer import XasImporter
    from .reportframe import ReportFrame, DictFrame, DataTableGrid, CSVFrame
    from .gui_utils import (databrowser, fileprompt, LarchWxApp, wx_update)
    from .larch_updater import LarchUpdaterDialog
    from .parameter import ParameterWidgets, ParameterPanel
    from .xafsplots import plotlabels

    from .feff_browser import FeffResultsFrame, FeffResultsPanel
    from .cif_browser import CIFFrame
    from .structure2feff_browser import Structure2FeffFrame

    _larch_builtins = {'_sys.wx': dict(gcd=gcd,
                                       databrowser=databrowser,
                                       fileprompt=fileprompt,
                                       wx_update=wx_update)}

    from .plotter import (_plot, _oplot, _newplot, _plot_text, fileplot,
                          _plot_marker, _plot_arrow, _plot_setlimits,
                          _plot_axvline, _plot_axhline, _scatterplot,
                          _hist, _update_trace, _saveplot, _saveimg,
                          get_display, _closeDisplays, _getcursor,
                          last_cursor_pos, _imshow, _contour, _xrf_plot,
                          _xrf_oplot, _fitplot, _redraw_plot,
                          get_zoomlimits, set_zoomlimits,
                          save_plot_config, get_plot_config,
                          get_panel_plot_config, set_panel_plot_config,
                          get_zorders, get_markercolors, set_plotwindow_title)

    if uname == 'darwin':
        HLine = DarwinHLine

    _larch_builtins['_plotter'] = dict(plot=_plot, oplot=_oplot,
                                       newplot=_newplot, plot_text=_plot_text,
                                       plot_marker=_plot_marker,
                                       plot_arrow=_plot_arrow,
                                       plot_setlimits=_plot_setlimits,
                                       plot_axvline=_plot_axvline,
                                       plot_axhline=_plot_axhline,
                                       scatterplot=_scatterplot, hist=_hist,
                                       update_trace=_update_trace,
                                       save_plot=_saveplot,
                                       save_image=_saveimg,
                                       save_plot_config=save_plot_config,
                                       get_plot_config=get_plot_config,
                                       get_display=get_display,
                                       close_all_displays=_closeDisplays,
                                       get_cursor=_getcursor,
                                       last_cursor_pos=last_cursor_pos,
                                       imshow=_imshow, contour=_contour,
                                       xrf_plot=_xrf_plot,
                                       xrf_oplot=_xrf_oplot,
                                       fit_plot=_fitplot,
                                       fileplot=fileplot,
                                       redraw_plot=_redraw_plot)

    _larch_builtins['_xafs'] = dict(redraw=xafsplots.redraw,
                                    plotlabels=plotlabels,
                                    plot_mu=xafsplots.plot_mu,
                                    plot_bkg=xafsplots.plot_bkg,
                                    plot_chie=xafsplots.plot_chie,
                                    plot_chik=xafsplots.plot_chik,
                                    plot_chir=xafsplots.plot_chir,
                                    plot_chiq=xafsplots.plot_chiq,
                                    plot_wavelet=xafsplots.plot_wavelet,
                                    plot_chifit=xafsplots.plot_chifit,
                                    plot_path_k=xafsplots.plot_path_k,
                                    plot_path_r=xafsplots.plot_path_r,
                                    plot_paths_k=xafsplots.plot_paths_k,
                                    plot_paths_r=xafsplots.plot_paths_r,
                                    plot_feffdat=xafsplots.plot_feffdat,
                                    plot_diffkk=xafsplots.plot_diffkk,
                                    plot_prepeaks_fit=xafsplots.plot_prepeaks_fit,
                                    plot_prepeaks_baseline=xafsplots.plot_prepeaks_baseline,
                                    plot_pca_components=xafsplots.plot_pca_components,
                                    plot_pca_weights=xafsplots.plot_pca_weights,
                                    plot_pca_fit=xafsplots.plot_pca_fit,
                                    plot_curvefit=xafsplots.plot_curvefit,
                                    )


    def _larch_init(_larch):
        """add ScanFrameViewer to _sys.gui_apps """
        if _larch is None:
            return
        _sys = _larch.symtable._sys
        if not hasattr(_sys, 'gui_apps'):
            _sys.gui_apps = {}
        # _sys.gui_apps['xrfviewer'] = ('XRF Spectrum Viewer', XRFDisplayFrame)

    #############################
    ## Hack System and Startfile on Windows totry to track down
    ## weird error of starting other applications, like Mail
    if uname == 'win':
        from os import system as os_system
        from os import startfile as os_startfile

        def my_system(command):
            print(f"#@-> os.system: {command}")
            return os_system(command)

        def my_startfile(filepath, operation=None):
            print(f"#@-> os.startfile: {filepath}, {operation}")
            try:
                if operation is None:
                    return os_startfile(filepath)
                else:
                    return os_startfile(filepath, operation)
            except WindowsError:
                print(f"#@-> os.startfile failed: {filepath}, {operation}")

        os.system = my_system
        os.startfile = my_startfile
    #############################
