import sys
import os

import wx

import wx.grid

def Debug(*arg):
    pass

sys.path.append(os.path.dirname(sys.argv[0]))

from KiBOM.columns import Columns

#import bomfunk_netlist_reader

class KiBOMTable(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self,parent)
        
        #Setup default columns
        self.SetupColumns(Columns._COLUMNS_DEFAULT)
        
    #configure column headings
    def SetupColumns(self, columns):
        
        self.CreateGrid(0, len(columns))
        
        for i,h in enumerate(columns):
            self.SetColLabelValue(i,h)

class KiBOMFrame(wx.Frame):
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent,title=title)
        
        self.panel = wx.Panel(self)
        
        self.table = KiBOMTable(self.panel)
        
        #Vertical sizer that separates the "export options" (lower) from the main table and selectors
        self.hSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #vertical sizer for srstoring the component selection options
        self.optSizer = wx.BoxSizer(wx.VERTICAL)
        
        #options
        self.showHideSizer = wx.BoxSizer(wx.VERTICAL)
        
        #add grouping option
        self.groupOption = wx.CheckBox(self.panel, label="Group Components")
        self.showHideSizer.Add(self.groupOption)
        
        self.optSizer.Add(self.showHideSizer)
        
        self.hSizer.Add(self.optSizer)
        self.hSizer.Add(self.table, 1, wx.EXPAND)
        
        self.panel.SetSizer(self.hSizer)
        
        self.AddMenuBar()
        
        self.Show(True)        
        
    def AddMenuBar(self):
        #add a menu
        filemenu = wx.Menu()
        
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit"," Exit the BoM Manager")
        
        menuBar = wx.MenuBar()
        
        menuBar.Append(filemenu,"&File")
        self.SetMenuBar(menuBar)
        
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        
    def OnExit(self, e):
        self.Close(True)
        
Debug("starting")

app = wx.App(False)

frame = KiBOMFrame(None,"KiBoM")

app.MainLoop()