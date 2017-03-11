# -*- coding: utf-8 -*-

## \package wizbin.depends

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language       import GT
from dbr.log            import DebugEnabled
from dbr.log            import Logger
from globals.ident      import btnid
from globals.ident      import inputid
from globals.ident      import pgid
from globals.strings    import TextIsEmpty
from globals.tooltips   import SetPageToolTips
from input.list         import ListCtrlESS
from input.select       import Choice
from input.text         import TextArea
from ui.button          import CreateButton
from ui.dialog          import ConfirmationDialog
from ui.layout          import BoxSizer
from ui.panel           import BorderedPanel
from ui.style           import layout as lyt
from wiz.helper         import GetMainWindow
from wiz.helper         import GetPage
from wiz.wizard         import WizardPage


## Page defining dependencies
class Page(WizardPage):
    ## Constructor
    #
    #  \param parent
    #    Parent <b><i>wx.Window</i></b> instance
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.DEPENDS)
        
        # Override default title
        self.SetTitle(GT(u'Dependencies and Conflicts'))
        
        # Bypass checking this page for build
        self.prebuild_check = False
        
        # Buttons to open, save, & preview control file
        self.btn_open = CreateButton(self, btnid.BROWSE, GT(u'Browse'), u'browse', name=u'btn browse')
        self.btn_save = CreateButton(self, btnid.SAVE, GT(u'Save'), u'save', name=u'btn save')
        self.btn_preview = CreateButton(self, btnid.PREVIEW, GT(u'Preview'), u'preview', name=u'btn preview')
        
        txt_package = wx.StaticText(self, label=GT(u'Dependency/Conflict Package Name'), name=u'package')
        txt_version = wx.StaticText(self, label=GT(u'Version'), name=u'version')
        
        self.ti_package = TextArea(self, size=(300,25), name=u'package')
        
        opts_operator = (
            u'>=',
            u'<=',
            u'=',
            u'>>',
            u'<<',
            )
        
        self.sel_operator = Choice(self, choices=opts_operator, name=u'operator')
        
        self.ti_version = TextArea(self, name=u'version')
        
        self.ti_package.SetSize((100,50))
        
        pnl_categories = BorderedPanel(self)
        
        self.DefaultCategory = u'Depends'
        
        rb_dep = wx.RadioButton(pnl_categories, label=GT(u'Depends'), name=self.DefaultCategory, style=wx.RB_GROUP)
        rb_pre = wx.RadioButton(pnl_categories, label=GT(u'Pre-Depends'), name=u'Pre-Depends')
        rb_rec = wx.RadioButton(pnl_categories, label=GT(u'Recommends'), name=u'Recommends')
        rb_sug = wx.RadioButton(pnl_categories, label=GT(u'Suggests'), name=u'Suggests')
        rb_enh = wx.RadioButton(pnl_categories, label=GT(u'Enhances'), name=u'Enhances')
        rb_con = wx.RadioButton(pnl_categories, label=GT(u'Conflicts'), name=u'Conflicts')
        rb_rep = wx.RadioButton(pnl_categories, label=GT(u'Replaces'), name=u'Replaces')
        rb_break = wx.RadioButton(pnl_categories, label=GT(u'Breaks'), name=u'Breaks')
        
        self.categories = (
            rb_dep, rb_pre, rb_rec,
            rb_sug, rb_enh, rb_con,
            rb_rep, rb_break,
        )
        
        # Buttons to add and remove dependencies from the list
        btn_add = CreateButton(self, btnid.ADD)
        btn_append = CreateButton(self, btnid.APPEND)
        btn_remove = CreateButton(self, btnid.REMOVE)
        btn_clear = CreateButton(self, btnid.CLEAR)
        
        # ----- List
        self.lst_deps = ListCtrlESS(self, inputid.LIST, name=u'list')
        self.lst_deps.SetSingleStyle(wx.LC_REPORT)
        self.lst_deps.InsertColumn(0, GT(u'Category'), width=150)
        self.lst_deps.InsertColumn(1, GT(u'Package(s)'))
        
        # wx 3.0 compatibility
        if wx.MAJOR_VERSION < 3:
            self.lst_deps.SetColumnWidth(100, wx.LIST_AUTOSIZE)
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        wx.EVT_KEY_DOWN(self.ti_package, self.SetDepends)
        wx.EVT_KEY_DOWN(self.ti_version, self.SetDepends)
        
        btn_add.Bind(wx.EVT_BUTTON, self.SetDepends)
        btn_append.Bind(wx.EVT_BUTTON, self.SetDepends)
        btn_remove.Bind(wx.EVT_BUTTON, self.SetDepends)
        btn_clear.Bind(wx.EVT_BUTTON, self.SetDepends)
        
        wx.EVT_KEY_DOWN(self.lst_deps, self.SetDepends)
        
        # *** Layout *** #
        
        LEFT_BOTTOM = lyt.ALGN_LB
        
        lyt_top = wx.GridBagSizer()
        lyt_top.SetCols(6)
        lyt_top.AddGrowableCol(3)
        
        # Row 1
        lyt_top.Add(txt_package, (1, 0), flag=LEFT_BOTTOM)
        lyt_top.Add(txt_version, (1, 2), flag=LEFT_BOTTOM)
        lyt_top.Add(self.btn_open, (0, 3), (4, 1), wx.ALIGN_RIGHT)
        lyt_top.Add(self.btn_save, (0, 4), (4, 1))
        lyt_top.Add(self.btn_preview, (0, 5), (4, 1))
        
        # Row 2
        lyt_top.Add(self.ti_package, (2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        lyt_top.Add(self.sel_operator, (2, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        lyt_top.Add(self.ti_version, (2, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        
        lyt_categories = wx.GridSizer(4, 2, 5, 5)
        
        for C in self.categories:
            lyt_categories.Add(C, 0)
        
        pnl_categories.SetAutoLayout(True)
        pnl_categories.SetSizer(lyt_categories)
        pnl_categories.Layout()
        
        lyt_buttons = BoxSizer(wx.HORIZONTAL)
        
        lyt_buttons.AddMany((
            (btn_add, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_append, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_remove, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_clear, 0, wx.ALIGN_CENTER_VERTICAL),
            ))
        
        lyt_mid = wx.GridBagSizer()
        lyt_mid.SetCols(2)
        
        lyt_mid.Add(wx.StaticText(self, label=u'Categories'), (0, 0), (1, 1), LEFT_BOTTOM)
        lyt_mid.Add(pnl_categories, (1, 0), flag=wx.RIGHT, border=5)
        lyt_mid.Add(lyt_buttons, (1, 1), flag=wx.ALIGN_BOTTOM)
        
        lyt_list = BoxSizer(wx.HORIZONTAL)
        lyt_list.Add(self.lst_deps, 1, wx.EXPAND)
        
        lyt_main = BoxSizer(wx.VERTICAL)
        # Spacer is less on this page because text is aligned to bottom
        lyt_main.AddSpacer(5)
        lyt_main.Add(lyt_top, 0, wx.EXPAND|lyt.PAD_LR, 5)
        lyt_main.Add(lyt_mid, 0, lyt.PAD_LR, 5)
        lyt_main.Add(lyt_list, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## Add a category & dependency to end of list
    #  
    #  \param category
    #    Category label
    #  \param value
    #    Dependency value
    def AppendDependency(self, category, value):
        self.lst_deps.AppendStringItem((category, value))
    
    
    ## Retrieves the default category to use
    def GetDefaultCategory(self):
        return self.DefaultCategory
    
    
    ## Reads & parses page data from a formatted text file
    #
    #  \param filename
    #    File path to open
    #  \see wiz.wizard.WizardPage.ImportFromFile
    def ImportFromFile(self, d_type, d_string):
        Logger.Debug(__name__, GT(u'Importing {}: {}'.format(d_type, d_string)))
        
        values = d_string.split(u', ')
        
        for V in values:
            self.lst_deps.InsertStringItem(0, d_type)
            self.lst_deps.SetStringItem(0, 1, V)
    
    
    ## \see wiz.wizard.WizardPage.InitPage
    def InitPage(self):
        control_page = GetPage(pgid.CONTROL)
        self.btn_open.Bind(wx.EVT_BUTTON, control_page.OnBrowse)
        self.btn_save.Bind(wx.EVT_BUTTON, control_page.OnSave)
        self.btn_preview.Bind(wx.EVT_BUTTON, control_page.OnPreviewControl)
        
        return True
    
    
    ## Resets all fields on page to default values
    def Reset(self):
        for C in self.categories:
            if C.GetName() == self.DefaultCategory:
                C.SetValue(True)
                break
        
        self.ti_package.Clear()
        self.sel_operator.Reset()
        self.ti_version.Clear()
        self.lst_deps.DeleteAllItems()
    
    
    ## Adds/Appends/Removes dependency to list
    def SetDepends(self, event=None):
        try:
            key_id = event.GetKeyCode()
        
        except AttributeError:
            key_id = event.GetEventObject().GetId()
        
        addname = self.ti_package.GetValue()
        oper = self.sel_operator.GetStringSelection()
        ver = self.ti_version.GetValue()
        addver = u'({}{})'.format(oper, ver)
        
        if key_id in (btnid.ADD, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            if TextIsEmpty(addname):
                return
            
            category = self.GetDefaultCategory()
            for C in self.categories:
                if C.GetValue():
                    category = C.GetName()
                    break
            
            if TextIsEmpty(ver):
                self.AppendDependency(category, addname)
            
            else:
                self.AppendDependency(category, u'{} {}'.format(addname, addver))
        
        elif key_id == btnid.APPEND:
            selected_count = self.lst_deps.GetSelectedItemCount()
            
            Logger.Debug(__name__, u'Appending to {} items'.format(selected_count))
            
            if not TextIsEmpty(addname) and self.lst_deps.GetItemCount() and selected_count:
                selected_rows = self.lst_deps.GetSelectedIndexes()
                
                if DebugEnabled():
                    Logger.Debug(__name__, u'Selected rows:')
                    for R in selected_rows:
                        print(u'\t{}'.format(R))
                
                for listrow in selected_rows:
                    Logger.Debug(__name__, u'Setting list row: {}'.format(listrow))
                    
                    # Get item from second column
                    colitem = self.lst_deps.GetItem(listrow, 1)
                    # Get the text from that item
                    prev_text = colitem.GetText()
                    
                    if not TextIsEmpty(ver):
                        new_text = u'{} | {} {}'.format(prev_text, addname, addver)
                    
                    else:
                        new_text = u'{} | {}'.format(prev_text, addname)
                    
                    Logger.Debug(__name__, u'Appended item: {}'.format(new_text))
                    
                    self.lst_deps.SetStringItem(listrow, 1, new_text)
        
        elif key_id in (btnid.REMOVE, wx.WXK_DELETE):
            self.lst_deps.RemoveSelected()
        
        elif key_id == btnid.CLEAR:
            if self.lst_deps.GetItemCount():
                if ConfirmationDialog(GetMainWindow(), GT(u'Confirm'),
                        GT(u'Clear all dependencies?')).ShowModal() in (wx.ID_OK, wx.OK):
                    self.lst_deps.DeleteAllItems()
        
        if event:
            event.Skip()
    
    
    ## Sets the page's fields data
    #
    #  \param data
    #    Text to parse for field values
    def Set(self, data):
        self.lst_deps.DeleteAllItems()
        for item in data:
            item_count = len(item)
            while item_count > 1:
                item_count -= 1
                self.lst_deps.InsertStringItem(0, item[0])
                self.lst_deps.SetStringItem(0, 1, item[item_count])
