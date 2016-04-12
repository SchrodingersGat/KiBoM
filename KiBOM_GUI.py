import sys
import os

import wx

import wx.grid

def Debug(*arg):
    pass

sys.path.append(os.path.dirname(sys.argv[0]))

from KiBOM.columns import Columns

#import bomfunk_netlist_reader

class KiBOMColumnList(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent)
        
        self.InitColumns(Columns._COLUMNS_DEFAULT)
        
    def InitColumns(self, cols):
    
        self.Clear()
        
        self.AppendItems(cols)
        

class KiBOMTable(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self,parent)
        
        #Setup default columns
        self.InitColumns()
        
    #configure column headings
    def InitColumns(self):
        
        self.CreateGrid(0, 1)
        
        self.SetColLabelValue(0,"Unitialized")
        
    """
    Perform a complete refresh of the columns
    """
    def SetColumns(self, columns):
        
        #add in any required rows
        if self.GetNumberCols() < len(columns):
            self.AppendCols(len(columns) - self.GetNumberCols())
            
        #remove any rows as required
        if self.GetNumberCols() > len(columns):
            self.DeleteCols(self.GetNumberCols() - len(columns))
        
        for i,h in enumerate(columns):
            self.SetColLabelValue(i,h)

class KiBOMFrame(wx.Frame):
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent,title=title)
        
        self.columns = Columns()
        
        self.panel = wx.Panel(self)
        
        self.table = KiBOMTable(self.panel)
        
        self.table.SetColumns(self.columns.columns)
        
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
        
        #list of available columns
        self.colListSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.colListTitle = wx.StaticText(self.panel, label="Columns:", style=wx.ALIGN_LEFT)
        self.colListSizer.Add(self.colListTitle)
        
        self.colList = KiBOMColumnList(self.panel)
        self.colListSizer.Add(self.colList)
        
        #buttons to move/add/delete columns
        self.colButtons = wx.BoxSizer(wx.HORIZONTAL)
        
        self.moveColUp = wx.Button(self.panel, label="Up")
        self.moveColDown = wx.Button(self.panel, label="Down")
        self.newCol = wx.Button(self.panel, label="Add")
        self.delCol = wx.Button(self.panel, label="Del")
        
        #add the buttons
        self.colButtons.Add(self.moveColUp)
        self.colButtons.Add(self.moveColDown)
        self.colButtons.Add(self.delCol)
        self.colButtons.Add(self.newCol)
        
        self.colListSizer.Add(self.colButtons)
        
        self.optSizer.Add(self.colListSizer)
        
        #add the main layout widgets
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