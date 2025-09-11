#!/usr/bin/env python
'''
   Plotting functions for Larch, wrapping the mplot plotting
   widgets which use matplotlib

Exposed functions here are
   plot:  display 2D line plot to an enhanced,
            configurable Plot Frame
   oplot: overplot a 2D line plot on an existing Plot Frame
   imshow: display a false-color map from array data on
           a configurable Image Display Frame.
'''
import time
import os
import sys
import yaml
import shutil
import wx
from pathlib import Path
from copy import deepcopy
from wxmplot import PlotFrame, ImageFrame, StackedPlotFrame
from wxmplot.interactive import get_wxapp
from wxmplot.colors import rgb2hex, hex2rgb
import larch
from ..utils import mkdir
from ..xrf import isLarchMCAGroup
from ..larchlib import ensuremod
from ..site_config import user_larchdir

from .xrfdisplay import XRFDisplayFrame


mplconfdir = Path(user_larchdir, 'matplotlib').as_posix()
mkdir(mplconfdir)
os.environ['MPLCONFIGDIR'] = mplconfdir

from matplotlib.axes import Axes
HIST_DOC = Axes.hist.__doc__

IMG_DISPLAYS = {}
PLOT_DISPLAYS = {}
FITPLOT_DISPLAYS = {}
XRF_DISPLAYS = {}
DISPLAY_LIMITS = None
_larch_name = '_plotter'

PLOTOPTS = {'theme': '<auto>',
            'window_size': [650, 600],
            'auto_margins': True,
            'axes_style': 'box',
            'facecolor': '#fefefe',
            'framecolor': '#fcfcfa',
            'gridcolor': '#ecece5',
            'hidewith_legend': True,
            'labelfont': 9.0,
            'legend_loc': 'best',
            'legend_onaxis': 'on plot',
            'legendfont': 8.0,
            'linecolors': ['#1f77b4', '#d62728', '#2ca02c', '#ff7f0e', '#9467bd',
                           '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
            'line_fill': False,
            'line_alpha': 1.0,
            'line_drawstyle': 'default',
            'line_marker': 'no symbol',
            'linestyle': 'solid',
            'linewidth': 2.5,
            'markersize': 4.0,
            'markercolor': 'black',
            'margins': [0.11, 0.08, 0.04, 0.14],
            'plot_type': 'lineplot',
            'scatter_normalcolor': 'blue',
            'scatter_normaledge': 'blue',
            'scatter_selectcolor': 'red',
            'scatter_selectedge': 'red',
            'scatter_size': 30,
            'show_grid': True,
            'show_legend': True,
            'show_legend_frame': False,
            'textcolor': '#000000',
            'titlefont': 10.0,
            'viewpad': 2.5,
            'xscale': 'linear',
            'yscale': 'linear',
            'y2scale': 'linear',
            'y3scale': 'linear',
            'y4scale': 'linear',
            'zoom_style': 'both x and y'}


__DOC__ = '''
General Plotting and Image Display Functions

The functions here include (but are not limited to):

function         description
------------     ------------------------------
plot             2D (x, y) plotting, with many, many options
plot_text        add text to a 2D plot
plot_marker      add a marker to a 2D plot
plot_arrow       add an arrow to a 2D plot

imshow           image display (false-color intensity image)

xrf_plot         browsable display for XRF spectra
'''

MAX_WINDOWS = 25
MAX_CURSHIST = 100
WXMPLOT_CONF = 'wxmplot.yaml'
NTRACES = 16

def get_plot_config(**kws):
    """get plot configuration dictionary"""
    conf = deepcopy(PLOTOPTS)

    saved_conf = {}
    conffile = Path(user_larchdir, WXMPLOT_CONF)
    if conffile.exists():
        saved_conf = yaml.safe_load(open(conffile.as_posix(), 'r').read())
    for key in conf:
        if key in saved_conf:
            conf[key] = saved_conf[key]
    conf.update(**kws)

    # check for theme of "<auto>"
    if conf.get('theme', '<auto>').lower().startswith('<auto>'):
        isdark = wx.SystemSettings.GetAppearance().IsDark()
        conf['theme'] = 'dark' if isdark else 'light'

    # if the saved configuration has 'traces',
    # use the first for default trace properties
    traces = saved_conf.get('traces', [{}])
    traces.extend([{}]*NTRACES)
    t0 = traces[0]

    conf['linestyle'] = t0.get('style', conf['linestyle'])
    for attr in ('linewidth', 'markersize', 'markercolor'):
        conf[attr] = t0.get(attr, conf[attr])
    for attr in ('alpha', 'drawstyle', 'fill', 'marker'):
        cname = f'line_{attr}'
        conf[cname] = t0.get(attr, conf[cname])

    # build traces from default trace properties, overwrite with saved trace properties
    conf['traces'] = []
    ncol = len(conf['linecolors'])
    for i in range(NTRACES):
        t = {'color': conf['linecolors'][i % ncol],
             'style': conf.get('linestyle', 'solid'),
             'linewidth': conf.get('linewidth', 2.5),
             'zorder': (i+1)*5,
             'fill': conf.get('line_fill', False),
             'drawstyle': conf.get('line_drawstyle', 'default'),
             'alpha': conf.get('line_alpha', 1),
             'marker': conf.get('line_marker', 'no symbol'),
             'markersize': conf.get('markersize', 4),
             'markercolor': conf.get('markercolor', 'black')}
        t.update(traces[i])
        conf['traces'].append(t)
    # print("Get Plot Config ", conf['traces'][0], conf['theme'], conf['margins'])
    return conf


def save_plot_config(win=1):
    """save plot configuration of current plot for future sessions"""
    conf = None
    display = get_display(win=win)
    if display is None:
        return
    try:
        conf = display.panel.get_config()
    except Exception:
        print("cannot save plot configuration")

    out = False
    if conf is not None:
        confstr = yaml.dump(conf, default_flow_style=None, indent=5, sort_keys=False)
        conffile = Path(user_larchdir, WXMPLOT_CONF)
        if conffile.exists():
            orig = conffile.absolute().as_posix()
            save = orig.replace('.yaml', '_1.yaml')
            try:
                shutil.copy(orig, save)
            except Exception:
                pass
        with open(conffile, 'w') as fh:
            fh.write(confstr)
        out = conffile
    return out.absolute().as_posix()

def get_panel_plot_config(panel):
    """get plot configuration for current plot (or default if that fails)"""
    try:
        conf = panel.get_config()
    except Exception:
        conf = {}
    return get_plot_config(**conf)


def set_panel_plot_config(panel, **kws):
    """set plot configuration for current plot)"""
    cnf = get_panel_plot_config(panel)
    cnf.update(**kws)
    # print("Set Panel Plot Config", cnf)
    panel.set_config(**cnf)

def get_zorders(display=None, panel=None):
    """"get list of z-orders for current traces of a display or panel
    so that a z-order can be set using the previous values
    """
    if panel is None and display is not None:
        panel = getattr(display, 'panel', None)
    zorders = [0]
    if panel is not None:
        try:
            conf = panel.conf
            ntrace = max(1, conf.ntrace)
            zorders = [t.zorder for t in conf.traces[:ntrace]]
        except:
            pass
    if len(zorders) < 1:
        zorders.append(0)
    return zorders

def get_markercolors(trace=1, linecolors=None, facecolor=None):
    """get marker face and edge colors for an integer trace and a plotconf
    dictionary.
    returns markeredge, markerface colors

    This sets the markeredge to the linecolor of the trace+2 (so, skipping over 1)

    The markerface is set to average of the edge color and the plot 'facecolor'
    with alpha set to C0
    """
    if linecolors is None:
        linecolors = PLOTOPTS['linecolors']
    if facecolor is None:
        facecolor = PLOTOPTS['facecolor']
    ncol = len(linecolors)
    edgecolor = linecolors[(2+trace) % ncol]

    ergb = hex2rgb(edgecolor[:7])
    frgb = hex2rgb(facecolor[:7])
    frgb = ( (ergb[0]+frgb[0])//2, (ergb[1]+frgb[1])//2, (ergb[2]+frgb[2])//2)
    return edgecolor, rgb2hex(frgb) + 'C0'


class XRFDisplay(XRFDisplayFrame):
    def __init__(self, wxparent=None, window=1, _larch=None,
                 size=(725, 425), **kws):
        XRFDisplayFrame.__init__(self, parent=wxparent, size=size,
                                 _larch=_larch,
                                 exit_callback=self.onExit, **kws)
        self.Show()
        self.Raise()
        self.panel.cursor_callback = self.onCursor
        self.window = int(window)
        self.title = 'XRF Display'
        self._larch = _larch
        self._xylims = {}
        self.symname = f'{_larch_name}.xrf{self.window}'
        symtable = ensuremod(self._larch, _larch_name)

        if symtable is not None:
            symtable.set_symbol(self.symname, self)
        if window not in XRF_DISPLAYS:
            XRF_DISPLAYS[window] = self

    def onExit(self, o, **kw):
        try:
            symtable = self._larch.symtable
            if symtable.has_group(_larch_name):
                symtable.del_symbol(self.symname)
        except:
            pass
        if self.window in XRF_DISPLAYS:
            XRF_DISPLAYS.pop(self.window)

        self.Destroy()

    def onCursor(self, x=None, y=None, **kw):
        symtable = ensuremod(self._larch, _larch_name)
        if symtable is None:
            return
        symtable.set_symbol(f'{self.symname}_xrf_x', x)
        symtable.set_symbol(f'{self.symname}_xrf_y', y)

class PlotDisplay(PlotFrame):
    def __init__(self, wxparent=None, window=1, _larch=None, size=None, **kws):
        PlotFrame.__init__(self, parent=None, size=size,
                           output_title='larchplot',
                           exit_callback=self.onExit, **kws)
        self.Show()
        self.Raise()
        self.panel.cursor_callback = self.onCursor
        self.panel.cursor_mode = 'zoom'
        self.window = int(window)
        self.title = 'Plot'
        self.get_config()
        self._larch = _larch
        self._xylims = {}
        self.cursor_hist = []
        self.symname = f'{_larch_name}.plot{self.window}'
        symtable = ensuremod(self._larch, _larch_name)
        if symtable is not None:
            symtable.set_symbol(self.symname, self)
            if not hasattr(symtable, f'{_larch_name}.cursor_maxhistory'):
                symtable.set_symbol(f'{_larch_name}.cursor_maxhistory', MAX_CURSHIST)

        if window not in PLOT_DISPLAYS:
            PLOT_DISPLAYS[window] = self

    def onExit(self, o, **kw):
        try:
            symtable = self._larch.symtable
            if symtable.has_group(_larch_name):
                symtable.del_symbol(self.symname)
        except:
            pass
        if self.window in PLOT_DISPLAYS:
            PLOT_DISPLAYS.pop(self.window)

        self.Destroy()

    def onCursor(self, x=None, y=None, **kw):
        symtable = ensuremod(self._larch, _larch_name)
        if symtable is None:
            return
        hmax = getattr(symtable, '%s.cursor_maxhistory' % _larch_name, MAX_CURSHIST)
        symtable.set_symbol('%s_x'  % self.symname, x)
        symtable.set_symbol('%s_y'  % self.symname, y)
        self.cursor_hist.insert(0, (x, y, time.time()))
        if len(self.cursor_hist) > hmax:
            self.cursor_hist = self.cursor_hist[:hmax]
        symtable.set_symbol('%s_cursor_hist' % self.symname, self.cursor_hist)

    def get_config(self):
        return get_panel_plot_config(self.panel)

    def set_config(self,  **kws):
        cnf = get_plot_config()
        cnf.update(**kws)
        try:
            self.panel.set_config(**cnf)
        except:
            print("could not set plot config")


class StackedPlotDisplay(StackedPlotFrame):
    def __init__(self, wxparent=None, window=1, _larch=None,  size=None, **kws):
        StackedPlotFrame.__init__(self, parent=None,
                                  exit_callback=self.onExit, **kws)
        self.Show()
        self.Raise()
        self.panel.cursor_callback = self.onCursor
        self.panel.cursor_mode = 'zoom'
        self.window = int(window)
        self.title = 'Fit Plot'
        self._larch = _larch
        self._xylims = {}
        self.cursor_hist = []
        self.symname = '%s.fitplot%i' % (_larch_name, self.window)
        symtable = ensuremod(self._larch, _larch_name)
        self.panel.canvas.figure.set_facecolor('#FDFDFB')
        self.panel_bot.canvas.figure.set_facecolor('#FDFDFB')

        if symtable is not None:
            symtable.set_symbol(self.symname, self)
            if not hasattr(symtable, '%s.cursor_maxhistory' % _larch_name):
                symtable.set_symbol('%s.cursor_maxhistory' % _larch_name, MAX_CURSHIST)

        if window not in FITPLOT_DISPLAYS:
            FITPLOT_DISPLAYS[window] = self

    def onExit(self, o, **kw):
        try:
            symtable = self._larch.symtable
            if symtable.has_group(_larch_name):
                symtable.del_symbol(self.symname)
        except:
            pass
        if self.window in FITPLOT_DISPLAYS:
            FITPLOT_DISPLAYS.pop(self.window)

        self.Destroy()

    def onCursor(self, x=None, y=None, **kw):
        symtable = ensuremod(self._larch, _larch_name)
        if symtable is None:
            return
        hmax = getattr(symtable, '%s.cursor_maxhistory' % _larch_name, MAX_CURSHIST)
        symtable.set_symbol('%s_x'  % self.symname, x)
        symtable.set_symbol('%s_y'  % self.symname, y)
        self.cursor_hist.insert(0, (x, y, time.time()))
        if len(self.cursor_hist) > hmax:
            self.cursor_hist = self.cursor_hist[:hmax]
        symtable.set_symbol('%s_cursor_hist' % self.symname, self.cursor_hist)

    def get_config(self):
        return get_panel_plot_config(self.panel)


class ImageDisplay(ImageFrame):
    def __init__(self, wxparent=None, window=1, _larch=None, size=None, **kws):
        ImageFrame.__init__(self, parent=None, size=size,
                                  exit_callback=self.onExit, **kws)
        self.Show()
        self.Raise()
        self.cursor_pos = []
        self.panel.cursor_callback = self.onCursor
        self.panel.contour_callback = self.onContour
        self.window = int(window)
        self.title = 'Image'
        self.symname = '%s.img%i' % (_larch_name, self.window)
        self._larch = _larch
        symtable = ensuremod(self._larch, _larch_name)
        if symtable is not None:
            symtable.set_symbol(self.symname, self)
        if self.window not in IMG_DISPLAYS:
            IMG_DISPLAYS[self.window] = self

    def onContour(self, levels=None, **kws):
        symtable = ensuremod(self._larch, _larch_name)
        if symtable is not None and levels is not None:
            symtable.set_symbol('%s_contour_levels'  % self.symname, levels)

    def onExit(self, o, **kw):
        try:
            symtable = self._larch.symtable
            symtable.has_group(_larch_name), self.symname
            if symtable.has_group(_larch_name):
                symtable.del_symbol(self.symname)
        except:
            pass
        if self.window in IMG_DISPLAYS:
            IMG_DISPLAYS.pop(self.window)
        self.Destroy()

    def onCursor(self,x=None, y=None, ix=None, iy=None, val=None, **kw):
        symtable = ensuremod(self._larch, _larch_name)
        if symtable is None:
            return
        set = symtable.set_symbol
        if x is not None:   set('%s_x' % self.symname, x)
        if y is not None:   set('%s_y' % self.symname, y)
        if ix is not None:  set('%s_ix' % self.symname, ix)
        if iy is not None:  set('%s_iy' % self.symname, iy)
        if val is not None: set('%s_val' % self.symname, val)

def get_display(win=1, _larch=None, wxparent=None, size=None, position=None,
                wintitle=None, xrf=False, image=False, stacked=False,
                theme=None, linewidth=None, markersize=None,
                show_grid=None, show_fullbox=None, height=None,
                width=None):
    """make a plotter"""
    # global PLOT_DISPLAYS, IMG_DISPlAYS
    if  hasattr(_larch, 'symtable'):
        if (getattr(_larch.symtable._sys.wx, 'wxapp', None) is None or
            getattr(_larch.symtable._plotter, 'no_plotting', False)):
            return None

        global DISPLAY_LIMITS
        if DISPLAY_LIMITS is None:
            displays = [wx.Display(i) for i in range(wx.Display.GetCount())]
            geoms = [d.GetGeometry() for d in displays]
            _left = min([g.Left for g in geoms])
            _right = max([g.Right for g in geoms])
            _top = min([g.Top for g in geoms])
            _bot = max([g.Bottom for g in geoms])
            DISPLAY_LIMITS = [_left, _right, _top, _bot]

    win = max(1, min(MAX_WINDOWS, int(abs(win))))
    symname = f'{_larch_name}.plot{win}'
    creator = PlotDisplay
    display_dict = PLOT_DISPLAYS
    if image:
        creator = ImageDisplay
        display_dict = IMG_DISPLAYS
        symname = f'{_larch_name}.img{win}'
    elif xrf:
        creator = XRFDisplay
        display_dict = XRF_DISPLAYS
        symname = f'{_larch_name}.xrf{win}'
    elif stacked:
        creator = StackedPlotDisplay
        display_dict = FITPLOT_DISPLAYS
        symname = f'{_larch_name}.fitplot{win}'


    def _get_disp(symname, creator, win, ddict, wxparent,
                  size, position, _larch):
        wxapp = get_wxapp()
        display = None
        new_display = False
        if win in ddict:
            display = ddict[win]
            try:
                s = display.GetSize()
            except RuntimeError:  # window has been deleted
                ddict.pop(win)
                display = None

        if display is None and hasattr(_larch, 'symtable'):
            display = _larch.symtable.get_symbol(symname, create=True)
            if display is not None:
                try:
                    s = display.GetSize()
                except RuntimeError:  # window has been deleted
                    print("get_display  no window 2")
                    display = None

        if display is None:
            display = creator(window=win, wxparent=wxparent,
                              size=size, _larch=_larch)
            new_display = True
            parent = wxapp.GetTopWindow()
            if position is not None:
                display.SetPosition(position)
            elif parent is not None:
                xpos, ypos = parent.GetPosition()
                xsiz, ysiz = parent.GetSize()
                x = xpos + xsiz*0.75
                y = ypos + ysiz*0.75
                if len(PLOT_DISPLAYS) > 0:
                    try:
                        xpos, ypos = PLOT_DISPLAYS[1].GetPosition()
                        xsiz, ysiz = PLOT_DISPLAYS[1].GetSize()
                    except:
                        pass
                off = 0.20*(win-1)
                x = max(25, xpos + xsiz*off)
                y = max(25, ypos + ysiz*off)
                global DISPLAY_LIMITS
                dlims = DISPLAY_LIMITS
                if dlims is None:
                    dlims = [0, 5000, 0, 5000]
                if y+0.75*ysiz > dlims[3]:
                    y = 40+max(40, 40+ysiz*(off-0.5))
                if x+0.75*xsiz > dlims[1]:
                    x = 20+max(10, 10+xpos+xsiz*(off-0.5))
                display.SetPosition((int(x), int(y)))
        ddict[win] = display
        return display, new_display

    plot_conf = get_plot_config()
    if size is not None:
        size = plot_conf['window_size']
    display, isnew  = _get_disp(symname, creator, win, display_dict, wxparent,
                               size, position, _larch)
    if isnew and creator in (PlotDisplay, StackedPlotDisplay):
        panels = [display.panel]
        if creator == StackedPlotDisplay:
            panels.append(display.panel_bot)
        for panel in panels:
            panel.set_config(**plot_conf)

    try:
        if wintitle is not None:
            display.SetTitle(wintitle)
        else:
            set_plotwindow_title(display, _larch=_larch)
    except:
        display_dict.pop(win)
        display, isnew = _get_disp(symname, creator, win, display_dict, wxparent,
                                   size, position, _larch)
        if wintitle is not None:
            display.SetTitle(wintitle)
        else:
            set_plotwindow_title(display, _larch=_larch)
    if  hasattr(_larch, 'symtable'):
        _larch.symtable.set_symbol(symname, display)
    return display


_getDisplay = get_display # back compatibility

def set_plotwindow_title(display, _larch=None, default='Plot'):
    title = getattr(display, 'title', default)
    win = getattr(display, 'window', 1)
    wintitle = f"{title}: #{win}"
    if _larch is not None:
        sessname = getattr(_larch.symtable._sys, 'session_name', None)
        datatask = getattr(_larch.symtable._sys, 'datatask_name', '')
        if sessname is not None:
            wintitle = f"{title}[{sessname}]: {datatask} #{win}"
    display.SetTitle(wintitle)

def _xrf_plot(x=None, y=None, mca=None, win=1, new=True, as_mca2=False, _larch=None,
              wxparent=None, size=None, side=None, yaxes=1, force_draw=True,
              wintitle=None,  **kws):
    """xrf_plot(energy, data[, win=1], options])

    Show XRF trace of energy, data

    Parameters:
    --------------
        energy :  array of energies
        counts :  array of counts
        mca:      Group counting MCA data (rois, etc)
        as_mca2:  use mca as background MCA

        win: index of Plot Frame (0, 1, etc).  May create a new Plot Frame.
        new: flag (True/False, default False) for whether to start a new plot.
        color: color for trace (name such as 'red', or '#RRGGBB' hex string)
        style: trace linestyle (one of 'solid', 'dashed', 'dotted', 'dot-dash')
        linewidth:  integer width of line
        marker:  symbol to draw at each point ('+', 'o', 'x', 'square', etc)
        markersize: integer size of marker

    See Also: xrf_oplot, plot
    """
    plotter = get_display(wxparent=wxparent, win=win, size=size,
                          _larch=_larch, wintitle=wintitle, xrf=True)
    if plotter is None:
        returne
    plotter.Raise()
    if x is None:
        return

    if isLarchMCAGroup(x):
        mca = x
        y = x.counts
        x = x.energy

    if as_mca2:
        if isLarchMCAGroup(mca):
            plotter.add_mca(mca, as_mca2=True, plot=False)
            plotter.plotmca(mca, as_mca2=True, **kws)
        elif y is not None:
            plotter.oplot(x, y, mca=mca, as_mca2=True, **kws)
    elif new:
        if isLarchMCAGroup(mca):
            plotter.add_mca(mca, plot=False)
            plotter.plotmca(mca, **kws)
        elif y is not None:
            plotter.plot(x, y, mca=mca, **kws)
    elif y is not None:
        if isLarchMCAGroup(mca):
            plotter.add_mca(mca, plot=False)
        plotter.oplot(x, y, mca=mca, **kws)


def _xrf_oplot(x=None, y=None, mca=None, win=1, _larch=None, **kws):
    """xrf_oplot(energy, data[, win=1], options])

    Overplot a second  XRF trace of energy, data

    Parameters:
    --------------
        energy :  array of energies
        counts :  array of counts
        mca:      Group counting MCA data (rois, etc)

        win: index of Plot Frame (0, 1, etc).  May create a new Plot Frame.
        color: color for trace (name such as 'red', or '#RRGGBB' hex string)
        style: trace linestyle (one of 'solid', 'dashed', 'dotted', 'dot-dash')

    See Also: xrf_plot
    """
    _xrf_plot(x=x, y=y, mca=mca, win=win, _larch=_larch, new=False, **kws)

def _plot(x,y, win=1, new=False, _larch=None, wxparent=None, size=None,
          xrf=False, stacked=False, force_draw=True, side=None, yaxes=1,
          wintitle=None, **kws):
    """plot(x, y[, win=1], options])

    Plot 2-D trace of x, y arrays in a Plot Frame, clearing any plot currently in the Plot Frame.

    Parameters:
    --------------
        x :  array of ordinate values
        y :  array of abscissa values (x and y must be same size!)

        win: index of Plot Frame (0, 1, etc).  May create a new Plot Frame.
        new: flag (True/False, default False) for whether to start a new plot.
        force_draw: flag (True/False, default Tree) for whether force a draw.
                    This will take a little extra time, and is not needed when
                    typing at the command-line, but is needed for plots to update
                    from inside scripts.
        label: label for trace
        title:  title for Plot
        xlabel: x-axis label
        ylabel: y-axis label
        ylog_scale: whether to show y-axis as log-scale (True or False)
        grid: whether to draw background grid (True or False)

        color: color for trace (name such as 'red', or '#RRGGBB' hex string)
        style: trace linestyle (one of 'solid', 'dashed', 'dotted', 'dot-dash')
        linewidth:  integer width of line
        marker:  symbol to draw at each point ('+', 'o', 'x', 'square', etc)
        markersize: integer size of marker

        drawstyle: style for joining line segments

        dy: array for error bars in y (must be same size as y!)
        yaxis='left'??
        use_dates

    See Also: oplot, newplot
    """
    plotter = get_display(wxparent=wxparent, win=win, size=size,
                          xrf=xrf, stacked=stacked,
                          wintitle=wintitle, _larch=_larch)
    if plotter is None:
        return
    plotter.Raise()
    kws['side'] = side
    kws['yaxes'] = yaxes
    if new:
        plotter.plot(x, y, **kws)
    else:
        plotter.oplot(x, y, **kws)
    if force_draw:
        wx_update(_larch=_larch)

def _redraw_plot(win=1, xrf=False, stacked=False, size=None, wintitle=None,
                 _larch=None, wxparent=None):
    """redraw_plot(win=1)

    redraw a plot window, especially convenient to force setting limits after
    multiple plot()s with delay_draw=True
    """

    plotter = get_display(wxparent=wxparent, win=win, size=size,
                          xrf=xrf, stacked=stacked,
                          wintitle=wintitle,  _larch=_larch)
    plotter.panel.unzoom_all()


def _update_trace(x, y, trace=1, win=1, _larch=None, wxparent=None,
                 side=None, yaxes=1, redraw=False, **kws):
    """update a plot trace with new data, avoiding complete redraw"""
    plotter = get_display(wxparent=wxparent, win=win, _larch=_larch)
    if plotter is None:
        return
    plotter.Raise()
    trace -= 1 # wxmplot counts traces from 0

    plotter.panel.update_line(trace, x, y, draw=True, side=side, yaxes=yaxes)
    wx_update(_larch=_larch)

def wx_update(_larch=None, **kws):
    try:
        ping = _larch.symtable.get_symbol('_sys.wx.ping')
        ping(timeout=0.001)
    except:
        pass

def _plot_setlimits(xmin=None, xmax=None, ymin=None, ymax=None, win=1, wxparent=None,
                    _larch=None):
    """set plot view limits for plot in window `win`"""
    plotter = get_display(wxparent=wxparent, win=win, _larch=_larch)
    if plotter is None:
        return
    plotter.panel.set_xylims((xmin, xmax, ymin, ymax))

def _oplot(x, y, win=1, _larch=None, wxparent=None, xrf=False, stacked=False,
           size=None, **kws):
    """oplot(x, y[, win=1[, options]])

    Plot 2-D trace of x, y arrays in a Plot Frame, over-plotting any
    plot currently in the Plot Frame.

    This is equivalent to
    plot(x, y[, win=1[, new=False[, options]]])

    See Also: plot, newplot
    """
    kws['new'] = False
    _plot(x, y, win=win, size=size, xrf=xrf, stacked=stacked,
          wxparent=wxparent, _larch=_larch, **kws)

def _newplot(x, y, win=1, _larch=None, wxparent=None,  size=None, wintitle=None,
             **kws):
    """newplot(x, y[, win=1[, options]])

    Plot 2-D trace of x, y arrays in a Plot Frame, clearing any
    plot currently in the Plot Frame.

    This is equivalent to
    plot(x, y[, win=1[, new=True[, options]]])

    See Also: plot, oplot
    """
    _plot(x, y, win=win, size=size, new=True, _larch=_larch,
          wxparent=wxparent, wintitle=wintitle, **kws)

def _plot_text(text, x, y, win=1, side=None, yaxes=1, size=None,
               stacked=False, xrf=False, rotation=None, ha='left', va='center',
               _larch=None, wxparent=None,  **kws):
    """plot_text(text, x, y, win=1, options)

    add text at x, y coordinates of a plot

    Parameters:
    --------------
        text:  text to draw
        x:     x position of text
        y:     y position of text
        win:   index of Plot Frame (0, 1, etc).  May create a new Plot Frame.
        side:  which axis to use ('left' or 'right') for coordinates.
        rotation:  text rotation. angle in degrees or 'vertical' or 'horizontal'
        ha:    horizontal alignment ('left', 'center', 'right')
        va:    vertical alignment ('top', 'center', 'bottom', 'baseline')

    See Also: plot, oplot, plot_arrow
    """
    plotter = get_display(wxparent=wxparent, win=win, size=size, xrf=xrf,
                          stacked=stacked, _larch=_larch)
    if plotter is None:
        return
    plotter.Raise()

    plotter.add_text(text, x, y, side=side, yaxes=yaxes,
                     rotation=rotation, ha=ha, va=va, **kws)

def _plot_arrow(x1, y1, x2, y2, win=1, side=None, yaxes=1,
                shape='full', color='black',
                width=0.00, head_width=0.05, head_length=0.25,
               _larch=None, wxparent=None, stacked=False, xrf=False,
                size=None, **kws):

    """plot_arrow(x1, y1, x2, y2, win=1, **kws)

    draw arrow from x1, y1 to x2, y2.

    Parameters:
    --------------
        x1: starting x coordinate
        y1: starting y coordinate
        x2: ending x coordinate
        y2: ending y coordinate
        side: which axis to use ('left' or 'right') for coordinates.
        shape:  arrow head shape ('full', 'left', 'right')
        color:  arrow color ('black')
        width:  width of arrow line (in points. default=0.0)
        head_width:  width of arrow head (in points. default=0.05)
        head_length:  length of arrow head (in points. default=0.25)
        overhang:    amount the arrow is swept back (in points. default=0)
        win:  window to draw too

    See Also: plot, oplot, plot_text
    """
    plotter = get_display(wxparent=wxparent, win=win, size=size, xrf=xrf,
                          stacked=stacked, _larch=_larch)
    if plotter is None:
        return
    plotter.Raise()
    plotter.add_arrow(x1, y1, x2, y2, side=side, yaxes=1, shape=shape,
                      color=color, width=width, head_length=head_length,
                      head_width=head_width, **kws)

def _plot_marker(x, y, marker='o', size=4, color='black', label='_nolegend_',
               _larch=None, wxparent=None, win=1, xrf=False, stacked=False, **kws):

    """plot_marker(x, y, marker='o', size=4, color='black')

    draw a marker at x, y

    Parameters:
    -----------
        x:      x coordinate
        y:      y coordinate
        marker: symbol to draw at each point ('+', 'o', 'x', 'square', etc) ['o']
        size:   symbol size [4]
        color:  color  ['black']

    See Also: plot, oplot, plot_text
    """
    plotter = get_display(wxparent=wxparent, win=win, size=None, xrf=xrf,
                          stacked=stacked, _larch=_larch)
    if plotter is None:
        return
    plotter.Raise()
    plotter.oplot([x], [y], marker=marker, markersize=size, label=label,
                 color=color, _larch=_larch, wxparent=wxparent,  **kws)

def _plot_axhline(y, xmin=0, xmax=1, win=1, wxparent=None, xrf=False,
                  stacked=False, size=None, delay_draw=False, _larch=None, **kws):
    """plot_axhline(y, xmin=None, ymin=None, **kws)

    plot a horizontal line spanning the plot axes
    Parameters:
    --------------
        y:      y position of line
        xmin:   starting x fraction (window units -- not user units!)
        xmax:   ending x fraction (window units -- not user units!)
    See Also: plot, oplot, plot_arrow
    """
    plotter = get_display(wxparent=wxparent, win=win, size=size, xrf=xrf,
                          stacked=stacked, _larch=_larch)
    if plotter is None:
        return
    plotter.Raise()
    if 'label' not in kws:
        kws['label'] = '_nolegend_'
    plotter.panel.axes.axhline(y, xmin=xmin, xmax=xmax, **kws)
    if delay_draw:
        plotter.panel.canvas.draw()

def _plot_axvline(x, ymin=0, ymax=1, win=1, wxparent=None, xrf=False,
                  stacked=False, size=None, delay_draw=False, _larch=None, **kws):
    """plot_axvline(y, xmin=None, ymin=None, **kws)

    plot a vertical line spanning the plot axes
    Parameters:
    --------------
        x:      x position of line
        ymin:   starting y fraction (window units -- not user units!)
        ymax:   ending y fraction (window units -- not user units!)
    See Also: plot, oplot, plot_arrow
    """
    plotter = get_display(wxparent=wxparent, win=win, size=size, xrf=xrf,
                          stacked=stacked, _larch=_larch)
    if plotter is None:
        return
    plotter.Raise()
    if 'label' not in kws:
        kws['label'] = '_nolegend_'
    plotter.panel.axes.axvline(x, ymin=ymin, ymax=ymax, **kws)
    if not delay_draw:
        plotter.panel.canvas.draw()

def _getcursor(win=1, timeout=15, _larch=None, wxparent=None, size=None,
               xrf=False, stacked=False, **kws):
    """get_cursor(win=1, timeout=30)

    waits (up to timeout) for cursor click in selected plot window, and
    returns x, y position of cursor.  On timeout, returns the last known
    cursor position, or (None, None)

    Note that _plotter.plotWIN_x and _plotter.plotWIN_y will be updated,
    with each cursor click, and so can be used to read the last cursor
    position without blocking.

    For a more consistent programmatic approach, this routine can be called
    with timeout <= 0 to read the most recently clicked cursor position.
    """
    plotter = get_display(wxparent=wxparent, win=win, size=size, xrf=xrf,
                          stacked=stacked, _larch=_larch)
    if plotter is None:
        return
    symtable = ensuremod(_larch, _larch_name)
    xsym = '%s.plot%i_x' % (_larch_name, win)
    ysym = '%s.plot%i_y' % (_larch_name, win)

    xval = symtable.get_symbol(xsym, create=True)
    yval = symtable.get_symbol(ysym, create=True)
    symtable.set_symbol(xsym, None)

    t0 = time.time()
    while time.time() - t0 < timeout:
        wx_update(_larch=_larch)
        time.sleep(0.05)
        if symtable.get_symbol(xsym) is not None:
            break

    # restore value on timeout
    if symtable.get_symbol(xsym, create=False) is None:
        symtable.set_symbol(xsym, xval)

    return (symtable.get_symbol(xsym), symtable.get_symbol(ysym))

def last_cursor_pos(win=None, _larch=None):
    """return most recent cursor position -- 'last click on plot'

    By default, this returns the last postion for all plot windows.
    If win is not `None`, the last position for that window will be returned

    Arguments
    ---------
    win  (int or None) index of window to get cursor position [None, all windows]

    Returns
    -------
    x, y coordinates of most recent cursor click, in user units
    """
    if  hasattr(_larch, 'symtable'):
        plotter = _larch.symtable._plotter
    else:
        return None, None
    histories = []
    for attr in dir(plotter):
        if attr.endswith('_cursor_hist'):
            histories.append(attr)

    if win is not None:
        tmp = []
        for attr in histories:
            if attr.startswith('plot%d_' % win):
                tmp.append(attr)
        histories = tmp
    _x, _y, _t = None, None, 0
    for hist in histories:
        for px, py, pt in getattr(plotter, hist, [None, None, -1]):
            if pt > _t and px is not None:
                _x, _y, _t = px, py, pt
    return _x, _y


def _scatterplot(x,y, win=1, _larch=None, wxparent=None, size=None,
          force_draw=True,  **kws):
    """scatterplot(x, y[, win=1], options])

    Plot x, y values as a scatterplot.  Parameters are very similar to
    those of plot()

    See Also: plot, newplot
    """
    plotter = get_display(wxparent=wxparent, win=win, size=size, _larch=_larch)
    if plotter is None:
        return
    plotter.Raise()
    plotter.scatterplot(x, y, **kws)
    if force_draw:
        wx_update(_larch=_larch)


def _fitplot(x, y, y2=None, panel='top', label=None, label2=None, win=1,
             _larch=None, wxparent=None, size=None, **kws):
    """fit_plot(x, y, y2=None, win=1, options)

    Plot x, y values in the top of a StackedPlot. If y2 is not None, then x, y2 values
    will also be plotted in the top frame, and the residual (y-y2) in the bottom panel.

    By default, arrays will be plotted in the top panel, and you must
    specify `panel='bot'` to plot an array in the bottom panel.

    Parameters are the same as for plot() and oplot()

    See Also: plot, newplot
    """
    plotter = get_display(wxparent=wxparent, win=win, size=size,
                          stacked=True, _larch=_larch)
    if plotter is None:
        return
    plotter.Raise()
    plotter.plot(x, y, panel='top', label=label, **kws)
    if y2 is not None:
        kws.update({'label': label2})
        plotter.oplot(x, y2, panel='top', **kws)
        plotter.plot(x, y2-y, panel='bot')
        plotter.panel.conf.set_margins(top=0.15, bottom=0.01,
                                       left=0.15, right=0.05)
        plotter.panel.unzoom_all()
        plotter.panel_bot.conf.set_margins(top=0.01, bottom=0.35,
                                           left=0.15, right=0.05)
        plotter.panel_bot.unzoom_all()


def _hist(x, bins=10, win=1, new=False,
           _larch=None, wxparent=None, size=None, force_draw=True,  *args, **kws):

    plotter = get_display(wxparent=wxparent, win=win, size=size, _larch=_larch)
    if plotter is None:
        return
    plotter.Raise()
    if new:
        plotter.panel.axes.clear()

    out = plotter.panel.axes.hist(x, bins=bins, **kws)
    plotter.panel.canvas.draw()
    if force_draw:
        wx_update(_larch=_larch)
    return out


_hist.__doc__ = """
    hist(x, bins, win=1, options)

  %s
""" % (HIST_DOC)


def _imshow(map, x=None, y=None, colormap=None, win=1, _larch=None,
            wxparent=None, size=None, **kws):
    """imshow(map[, options])

    Display an 2-D array of intensities as a false-color map

    map: 2-dimensional array for map
    """
    img = get_display(wxparent=wxparent, win=win, size=size, _larch=_larch, image=True)
    if img is not None:
        img.display(map, x=x, y=y, colormap=colormap, **kws)

def _contour(map, x=None, y=None, _larch=None, **kws):
    """contour(map[, options])

    Display an 2-D array of intensities as a contour plot

    map: 2-dimensional array for map
    """
    kws.update(dict(style='contour'))
    _imshow(map, x=x, y=y, _larch=_larch, **kws)

def _saveplot(fname, dpi=300, format=None, win=1, _larch=None, wxparent=None,
              size=None, facecolor='w', edgecolor='w', quality=90,
              image=False, **kws):
    """formats: png (default), svg, pdf, jpeg, tiff"""
    thisdir = Path.cwd().as_posix()
    if format is None:
        suffix = Path(fname).name
        if suffix is not None:
            if suffix.startswith('.'):
                suffix = suffix[1:]
            format = suffix
    if format is None: format = 'png'
    format = format.lower()
    canvas = get_display(wxparent=wxparent, win=win, size=size,
                         _larch=_larch, image=image).panel.canvas
    if canvas is None:
        return
    if format in ('jpeg', 'jpg'):
        canvas.print_jpeg(fname, quality=quality, **kws)
    elif format in ('tiff', 'tif'):
        canvas.print_tiff(fname, **kws)
    elif format in ('png', 'svg', 'pdf', 'emf', 'eps'):
        canvas.print_figure(fname, dpi=dpi, format=format,
                            facecolor=facecolor, edgecolor=edgecolor, **kws)
    else:
        print('unsupported image format: ', format)
    os.chdir(thisdir)

def _saveimg(fname, _larch=None, **kws):
    """save image from image display"""
    kws.update({'image':True})
    _saveplot(fname, _larch=_larch, **kws)

def _closeDisplays(_larch=None, **kws):
    for display in (PLOT_DISPLAYS, IMG_DISPLAYS,
                    FITPLOT_DISPLAYS, XRF_DISPLAYS):
        for win in display.values():
            try:
                win.Destroy()
            except:
                pass

def get_zoomlimits(plotpanel, dgroup):
    """save current zoom limits, to be reapplied with set_zoomlimits()"""
    view_lims = plotpanel.get_viewlimits()
    zoom_lims = plotpanel.conf.zoom_lims
    out = None
    inrange = 3
    if len(zoom_lims) > 0:
        if zoom_lims[-1] is not None:
            _ax =  list(zoom_lims[0].keys())[-1]
            if all([_ax.get_xlabel() == dgroup.plot_xlabel,
                    _ax.get_ylabel() == dgroup.plot_ylabel,
                    min(dgroup.xplot) <= view_lims[1],
                    max(dgroup.xplot) >= view_lims[0],
                    min(dgroup.yplot) <= view_lims[3],
                    max(dgroup.yplot) >= view_lims[2]]):
                out = (_ax, view_lims, zoom_lims)
    return out

def set_zoomlimits(plotpanel, limits, verbose=False):
    """set zoom limits returned from get_zoomlimits()"""
    if limits is None:
        if verbose:
            print("set zoom, no limits")
        return False
    ax, vlims, zoom_lims = limits
    plotpanel.reset_formats()
    if ax == plotpanel.axes:
        try:
            ax.set_xlim((vlims[0], vlims[1]), emit=True)
            ax.set_ylim((vlims[2], vlims[3]), emit=True)
            if len(plotpanel.conf.zoom_lims) == 0 and len(zoom_lims) > 0:
                plotpanel.conf.zoom_lims = zoom_lims
                if verbose:
                    print("set zoom, ", zoom_lims)
        except:
            if verbose:
                print("set zoom, exception")
            return False
    return True

def fileplot(filename, col1=1, col2=2, **kws):
    """gnuplot-like plot of columns from a plain text column data file,

    Arguments
    ---------
    filename, str:  name of file to be read with `read_ascii()`
    col1,     int:  index of column (starting at 1) for x-axis [1]
    col2,     int:  index of column (starting at 1) for y-axis [2]


    Examples
    --------
       > fileplot('xmu.dat', 1, 4, new=True)

    Notes
    -----
    1. Additional keywords arguments will be forwarded to `plot()`, including
          new = True/False
          title, xlabel, ylabel,
          linewidth, marker, color
    2. If discoverable, column labels will be used to label axes
    """
    from larch.io import read_ascii
    fdat = read_ascii(filename)
    ncols, npts = fdat.data.shape
    ix = max(0, col1-1)
    iy = max(0, col2-1)
    xlabel = f"col {col1}"
    flabel = f"col {col2}"
    if ix < len(fdat.array_labels):
        xlabel = fdat.array_labels[ix]
    if iy < len(fdat.array_labels):
        ylabel = fdat.array_labels[iy]

    title = f"{filename:s} {col1:d}:{col2:d}"
    if 'xlabel' in kws:
        xlabel = kws.pop('xlabel')
    if 'ylabel' in kws:
        ylabel = kws.pop('ylabel')
    if 'title' in kws:
        title = kws.pop('title')

    _plot(fdat.data[ix,:], fdat.data[iy,:], xlabel=xlabel, ylabel=ylabel,
          title=title, **kws)
