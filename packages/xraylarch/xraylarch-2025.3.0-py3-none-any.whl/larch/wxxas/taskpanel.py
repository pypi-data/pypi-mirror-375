import time
import os
import sys
from functools import partial
from copy import deepcopy

import numpy as np
np.seterr(all='ignore')

import wx
import wx.grid as wxgrid
import wx.lib.scrolledpanel as scrolled

from larch import Group
from larch.wxlib import (BitmapButton, SetTip, GridPanel, FloatCtrl,
                         FloatSpin, FloatSpinWithPin, get_icon, SimpleText,
                         pack, Button, HLine, Choice, Check, MenuItem, Popup,
                         CEN, LEFT, FRAMESTYLE, FileSave, GUI_COLORS,
                         FileOpen, DataTableGrid, get_font)

from larch.xafs import etok, ktoe
from larch.utils import group2dict
from larch.utils.strutils import break_longstring
from .config import LARIX_PANELS

LEFT = wx.ALIGN_LEFT
CEN |=  wx.ALL

def autoset_fs_increment(wid, value):
    """set increment for floatspin to be
    1, 2, or 5 x 10^(integer) and ~0.02 X current value
    """
    if abs(value) < 1.e-20:
        return
    ndig = int(1-round(np.log10(abs(value*0.5))))
    wid.SetDigits(ndig+2)
    c, inc = 0, 10.0**(-ndig)
    while (inc/abs(value) > 0.02):
        scale = 0.5 if (c % 2 == 0) else 0.4
        inc *= scale
        c += 1
    wid.SetIncrement(inc)

def update_confval(dest, source, attr, pref=''):
    """
    update a dict value for an attribute from a source dict
    """
    val = source.get(attr, None)
    if val is None:
        val = dest.get(pref+attr, None)
    dest[pref+attr] = val
    return val

class GroupJournalFrame(wx.Frame):
    """ edit parameters"""
    def __init__(self, parent, dgroup=None, **kws):
        self.parent = parent
        self.dgroup = dgroup
        self.n_entries = 0
        wx.Frame.__init__(self, None, -1,  'Group Journal',
                          style=FRAMESTYLE, size=(950, 700))

        panel = GridPanel(self, ncols=3, nrows=10, pad=2, itemstyle=LEFT)

        self.label = SimpleText(panel, 'Group Journal', size=(750, 30))

        export_btn = Button(panel, ' Export to Tab-Separated File', size=(225, -1),
                            action=self.export)

        add_btn = Button(panel, 'Add Entry', size=(200, -1), action=self.add_entry)
        self.label_wid = wx.TextCtrl(panel, -1, value='user comment', size=(200, -1))
        self.value_wid = wx.TextCtrl(panel, -1, value='',             size=(600, -1))

        panel.Add(self.label, dcol=3, style=LEFT)

        panel.Add(SimpleText(panel, ' Add a Journal Entry:'), dcol=1, style=LEFT, newrow=True)
        panel.Add(add_btn, dcol=1)
        panel.Add(export_btn, dcol=1, newrow=False)

        panel.Add(SimpleText(panel, ' Label:'), style=LEFT, newrow=True)
        panel.Add(self.label_wid, dcol=1, style=LEFT)

        panel.Add(SimpleText(panel, ' Value:'), style=LEFT, newrow=True)
        panel.Add(self.value_wid, dcol=2, style=LEFT)
        panel.Add((10, 10), newrow=True)

        collabels = [' Label ', ' Value ', ' Date/Time']

        colsizes = [150, 550, 150]
        coltypes = ['string', 'string', 'string']
        coldefs  = [' ', ' ', ' ']

        self.datagrid = DataTableGrid(panel, collabels=collabels,
                                      datatypes=coltypes,
                                      defaults=coldefs,
                                      colsizes=colsizes,
                                      rowlabelsize=40)

        self.datagrid.SetMinSize((925, 650))
        self.datagrid.EnableEditing(False)
        panel.Add(self.datagrid, dcol=5, drow=9, newrow=True, style=LEFT|wx.GROW|wx.ALL)
        panel.pack()

        self.parent.timers['journal_updater'] = wx.Timer(self.parent)
        self.parent.Bind(wx.EVT_TIMER, self.onRefresh,
                         self.parent.timers['journal_updater'])
        self.Bind(wx.EVT_CLOSE,  self.onClose)
        self.SetSize((950, 725))
        self.Show()
        self.Raise()
        self.parent.timers['journal_updater'].Start(1000)

        if dgroup is not None:
            wx.CallAfter(self.set_group, dgroup=dgroup)

    def add_entry(self, evt=None):
        if self.dgroup is not None:
            label = self.label_wid.GetValue()
            value = self.value_wid.GetValue()
            if len(label)>0 and len(value)>1:
                self.dgroup.journal.add(label, value)


    def onClose(self, event=None):
        self.parent.timers['journal_updater'].Stop()
        self.Destroy()

    def onRefresh(self, event=None):
        if self.dgroup is None:
            return
        if self.n_entries == len(self.dgroup.journal.data):
            return
        self.set_group(self.dgroup)


    def export(self, event=None):
        wildcard = 'CSV file (*.csv)|*.csv|All files (*.*)|*.*'
        fname = FileSave(self, message='Save Tab-Separated-Value Data File',
                         wildcard=wildcard,
                         default_file= f"{self.dgroup.filename}_journal.csv")
        if fname is None:
            return

        buff = ['Label\tValue\tDateTime']
        for entry in self.dgroup.journal:
            k, v, dt = entry.key, entry.value, entry.datetime.isoformat()
            k = k.replace('\t', '_')
            if not isinstance(v, str): v = repr(v)
            v = v.replace('\t', '   ')
            buff.append(f"{k}\t{v}\t{dt}")

        buff.append('')
        with open(fname, 'w', encoding=sys.getdefaultencoding()) as fh:
            fh.write('\n'.join(buff))

        msg = f"Exported journal for {self.dgroup.filename} to '{fname}'"
        writer = getattr(self.parent, 'write_message', sys.stdout)
        writer(msg)


    def set_group(self, dgroup=None):
        if dgroup is None:
            dgroup = self.dgroup
        if dgroup is None:
            return
        self.dgroup = dgroup
        self.SetTitle(f'Group Journal for {dgroup.filename:s}')

        label = f'Journal for {dgroup.filename}'
        desc = dgroup.journal.get('source_desc')
        if desc is not None:
            label = f'Journal for {desc.value}'
        self.label.SetLabel(label)


        grid_data = []
        rowsize = []
        self.n_entries = len(dgroup.journal.data)

        for entry in dgroup.journal:
            val = entry.value
            if not isinstance(val, str):
                val = repr(val)
            xval = break_longstring(val)
            val = '\n'.join(xval)
            rowsize.append(len(xval))
            xtime = entry.datetime.strftime("%Y/%m/%d %H:%M:%S")
            grid_data.append([entry.key, val, xtime])

        nrows = self.datagrid.table.GetRowsCount()

        if len(grid_data) > nrows:
            self.datagrid.table.AppendRows(len(grid_data)+8 - nrows)
        self.datagrid.table.Clear()
        self.datagrid.table.data = grid_data

        for i, rsize in enumerate(rowsize):
            self.datagrid.SetRowSize(i, rsize*20)

        self.datagrid.Refresh()


class TaskPanel(wx.Panel):
    """generic panel for main tasks.   meant to be subclassed
    """
    def __init__(self, parent, controller, panel=None, **kws):
        wx.Panel.__init__(self, parent, -1, size=(550, 625), **kws)
        self.parent = parent
        self.controller = controller
        self.larch = controller.larch
        self.title = 'Generic Panel'
        self.configname = panel
        if panel in LARIX_PANELS:
            self.title = LARIX_PANELS[panel].title
            self.desc  = LARIX_PANELS[panel].desc

        self.wids = {}
        self.subframes = {}
        self.command_hist = []
        self.SetFont(get_font())
        self.titleopts = {'font': get_font(larger=1),
                          'colour': GUI_COLORS.title_red, 'style': LEFT}

        self.font_fixedwidth = get_font(fixed_width=True)

        self.panel = GridPanel(self, ncols=7, nrows=10, pad=2, itemstyle=LEFT)
        self.panel.sizer.SetVGap(5)
        self.panel.sizer.SetHGap(5)
        self.skip_process = True
        self.skip_plotting = False
        self.build_display()
        self.skip_process = False
        self.stale_groups = None

        self.fit_xspace = 'e'
        self.fit_last_erange = None

    def is_xasgroup(self, dgroup):
        return getattr(dgroup, 'datatype', 'raw').startswith('xa')

    def ensure_xas_processed(self, dgroup, force_mback=False):
        if self.is_xasgroup(dgroup):
            req_attrs = ['e0', 'mu', 'dmude', 'norm', 'pre_edge']
            if force_mback:
                req_attrs.append('norm_mback')

            if not all([hasattr(dgroup, attr) for attr in req_attrs]):
                self.parent.process_normalization(dgroup, force=True,
                                                force_mback=force_mback)
        if not hasattr(dgroup, 'xplot'):
            if hasattr(dgroup, 'xdat'):
                dgroup.xplot = deepcopy(dgroup.xdat)
            elif hasattr(dgroup, 'energy'):
                dgroup.xplot = deepcopy(dgroup.energy)

    def make_fit_xspace_widgets(self, elo=-1, ehi=1):
        self.wids['fitspace_label'] = SimpleText(self.panel, 'Fit Range (eV):')
        opts = dict(digits=2, increment=1.0, relative_e0=True)
        self.elo_wids = self.add_floatspin('elo', value=elo, **opts)
        self.ehi_wids = self.add_floatspin('ehi', value=ehi, **opts)

    def update_fit_xspace(self, arrayname, grouplist=None):
        fit_xspace = 'e'
        if arrayname.startswith('chi'):
            fit_xspace = 'r' if 'r' in arrayname else 'k'

        if fit_xspace == self.fit_xspace:
            return

        if self.fit_xspace == 'e' and fit_xspace == 'k': # e to k
            dgroup = self.controller.get_group()
            self.ensure_xas_processed(dgroup)
            e0 = getattr(dgroup, 'e0', None)
            k  = getattr(dgroup, 'k', None)
            kspace_missing = []
            if k is None:
                kspace_missing.append(dgroup)
            if grouplist is not None:
                for gname in grouplist:
                    grp = self.controller.get_group(gname)
                    self.ensure_xas_processed(grp)
                    if getattr(grp, 'k', None) is None and grp not in kspace_missing:
                        kspace_missing.append(grp)
            if e0 is None or len(kspace_missing) > 0:
                msg = ["Cannont set fit space to k-space:",
                       "these groups have chi(k) data"]
                for g in kspace_missing:
                    if g is not None:
                        msg.append(f"    {g.filename}")
                msg.append("")
                Popup(self, "\n".join(msg), "Cannot fit in k-space for this data",
                          style=wx.ICON_WARNING|wx.OK_DEFAULT)
                return

            elo = self.wids['elo'].GetValue()
            ehi = self.wids['ehi'].GetValue()
            self.fit_last_erange = (elo, ehi)
            self.wids['elo'].SetValue(etok(elo-e0))
            self.wids['ehi'].SetValue(etok(ehi-e0))
            self.fit_xspace = 'k'
            self.wids['fitspace_label'].SetLabel('Fit Range (1/\u212B):')
        elif self.fit_xspace == 'k' and fit_xspace == 'e': # k to e
            if self.fit_last_erange is not None:
                elo, ehi = self.fit_last_erange
            else:
                dgroup = self.controller.get_group()
                e0 = getattr(dgroup, 'e0', None)
                k  = getattr(dgroup, 'k', None)
                if e0 is None or k is None:
                    return
                ehi = ktoe(self.wids['elo'].GetValue()) + e0
                elo = ktoe(self.wids['ehi'].GetValue()) + e0
            self.wids['elo'].SetValue(elo)
            self.wids['ehi'].SetValue(ehi)
            self.fit_xspace = 'e'
            self.wids['fitspace_label'].SetLabel('Fit Range (eV):')


    def show_subframe(self, name, frameclass, **opts):
        shown = False
        if name in self.subframes:
            try:
                self.subframes[name].Raise()
                shown = True
            except:
                del self.subframes[name]
        if not shown:
            self.subframes[name] = frameclass(self, **opts)

    def onPanelExposed(self, **kws):
        # called when notebook is selected: process group
        self.controller.set_datatask_name(self.title)
        fname = self.controller.filelist.GetStringSelection()
        if fname in self.controller.file_groups:
            gname = self.controller.file_groups[fname]
            dgroup = self.controller.get_group(gname)
            if dgroup is not None:
                try:
                    if dgroup.datatype == 'xas':
                        self.ensure_xas_processed(dgroup)
                    self.fill_form(dgroup)
                    self.process(dgroup=dgroup)
                except:
                    pass

    def onPanelHidden(self, **kws):
        # called when notebook is de-selected: save config
        fname = self.controller.filelist.GetStringSelection()
        if fname in self.controller.file_groups:
            gname = self.controller.file_groups[fname]
            dgroup = self.controller.get_group(gname)
            if dgroup is not None:
                try:
                    conf = self.get_config()
                    conf.update(self.read_form())
                    setattr(dgroup.config, self.configname, conf)
                except:
                    pass

    def write_message(self, msg, panel=0):
        self.controller.write_message(msg, panel=panel)

    def larch_eval(self, cmd):
        """eval"""
        self.command_hist.append(cmd)
        return self.controller.larch.eval(cmd)

    def _plain_larch_eval(self, cmd):
        return self.controller.larch._larch.eval(cmd)

    def get_session_history(self):
        """return full session history"""
        larch = self.controller.larch
        return getattr(larch.input, 'hist_buff',
                       getattr(larch.parent, 'hist_buff', []))

    def larch_has_symbol(self, sym):
        """does larch have a named symbol"""
        return self.controller.larch.symtable.has_symbol(sym)

    def larch_get(self, sym):
        """get value from larch symbol table"""
        return self.controller.larch.symtable.get_symbol(sym)

    def build_display(self):
        """build display"""

        self.panel.Add(SimpleText(self.panel, self.title, **titleopts),
                       dcol=7)
        self.panel.Add(SimpleText(self.panel, ' coming soon....'),
                       dcol=7, newrow=True)
        self.panel.pack()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.LEFT|wx.CENTER, 3)
        pack(self, sizer)

    def set_defaultconfig(self, config):
        """set the default configuration for this session"""
        if self.configname not in self.controller.conf_group:
            self.controller.conf_group[self.configname] = {}
        self.controller.conf_group[self.configname].update(config)

    def get_defaultconfig(self):
        """get the default configuration for this session"""
        return deepcopy(self.controller.get_config(self.configname))

    def get_config(self, dgroup=None, with_erange=True):
        """get and set processing configuration for a group"""
        if dgroup is None:
            dgroup = self.controller.get_group()
        if not hasattr(dgroup, 'config'):
            dgroup.config = Group(__name__='Larix config')
        conf = getattr(dgroup.config, self.configname, None)
        defconf = self.get_defaultconfig()
        if conf is None:
            setattr(dgroup.config, self.configname, defconf)
        conf = getattr(dgroup.config, self.configname)
        for k, v in defconf.items():
            if k not in conf:
                conf[k] = v

        if dgroup is not None and with_erange and hasattr(dgroup, 'energy'):
            _emin = min(dgroup.energy)
            _emax = max(dgroup.energy)
            if not hasattr(dgroup, 'e0'):
                dgroup.e0 = dgroup.energy.mean()
            e0 = 5*int(dgroup.e0/5.0)
            if 'elo' not in conf:
                conf['elo'] = min(_emax, max(_emin, conf['elo_rel'] + e0))
            if 'ehi' not in conf:
                conf['ehi'] = min(_emax, max(_emin, conf['ehi_rel'] + e0))
        return conf

    def update_config(self, config, dgroup=None):
        """set/update processing configuration for a group"""
        if dgroup is None:
            dgroup = self.controller.get_group()
        conf = None
        dconf = getattr(dgroup, 'config', None)
        if dconf is not None:
            conf = getattr(dconf, self.configname, None)
        if conf is None:
            conf = self.get_defaultconfig()

        conf.update(config)
        if dgroup is not None:
            setattr(dgroup.config, self.configname, conf)

    def fill_form(self, dat, initial=False):
        if isinstance(dat, Group):
            dat = group2dict(dat)

        for name, wid in self.wids.items():
            if isinstance(wid, FloatCtrl) and name in dat:
                wid.SetValue(dat[name])

    def get_energy_ranges(self, dgroup):
        pass

    def read_form(self):
        "read for, returning dict of values"
        dgroup = self.controller.get_group()
        form_opts = {'groupname': getattr(dgroup, 'groupname', 'No Group')}
        for name, wid in self.wids.items():
            val = None
            for method in ('GetValue', 'GetStringSelection', 'IsChecked',
                           'GetLabel'):
                meth = getattr(wid, method, None)
                if callable(meth):
                    try:
                        val = meth()
                    except TypeError:
                        pass
                if val is not None:
                    break
            form_opts[name] = val
        return form_opts

    def process(self, dgroup=None, **kws):
        """override to handle data process step"""
        if self.skip_process:
            return
        self.skip_process = True

    def add_text(self, text, dcol=1, newrow=True):
        self.panel.Add(SimpleText(self.panel, text),
                       dcol=dcol, newrow=newrow)


    def add_floatspin(self, name, value, with_pin=True, parent=None,
                      relative_e0=False, **kws):
        """create FloatSpin with Pin button for onSelPoint"""
        if parent is None:
            parent = self.panel
        if with_pin:
            pin_action = partial(self.parent.onSelPoint, opt=name,
                                 relative_e0=relative_e0,
                                 callback=self.pin_callback)
            fspin, pinb = FloatSpinWithPin(parent, value=value,
                                           pin_action=pin_action, **kws)
        else:
            fspin = FloatSpin(parent, value=value, **kws)
            pinb = None

        self.wids[name] = fspin

        fspin.SetValue(value)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(fspin)
        if pinb is not None:
            sizer.Add(pinb)
        return sizer

    def pin_callback(self, opt='__', xsel=None, relative_e0=False, **kws):
        """called to do reprocessing after a point is selected as from Pin/Plot"""
        if xsel is not None and opt in self.wids:
            if relative_e0 and 'e0' in self.wids:
                xsel -= self.wids['e0'].GetValue()
            self.wids[opt].SetValue(xsel)
            wx.CallAfter(self.onProcess)

    def onPlot(self, evt=None):
        pass

    def onPlotOne(self, evt=None, dgroup=None, **kws):
        pass

    def onPlotSel(self, evt=None, groups=None, **kws):
        pass

    def onProcess(self, evt=None, **kws):
        pass
