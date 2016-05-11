import sys
import os

import wx

import wx.grid

def Debug(*arg):
    pass

here = os.path.abspath(os.path.dirname(sys.argv[0]))
    
sys.path.append(here)

from KiBOM.columns import ColumnList

#import bomfunk_netlist_reader

class KiBOMColumnList(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent)
        
    def SetColumns(self, columnList):
    
        self.Clear()
        
        for i,col in enumerate(columnList.columns):
            self.Append(col.title, None)
            self.Check(i,check=col.visible)
        

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
    def SetColumns(self, columnList):
        
        columns = columnList.VisibleColumns()
        
        #add in any required rows
        if self.GetNumberCols() < len(columns):
            self.AppendCols(len(columns) - self.GetNumberCols())
            
        #remove any rows as required
        if self.GetNumberCols() > len(columns):
            self.DeleteCols(self.GetNumberCols() - len(columns))
        
        for i,col in enumerate(columns):
            self.SetColLabelValue(i,col.title)

class KiBOMFrame(wx.Frame):
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent,title=title)
        
        wx.Image.AddHandler(wx.PNGHandler());
        
        self.columns = ColumnList()
        
        self.panel = wx.Panel(self)
        
        self.table = KiBOMTable(self.panel)
        
        self.table.SetColumns(self.columns)
        
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
        
        self.colList.SetColumns(self.columns)
        
        #buttons to move/add/delete columns
        self.colButtons = wx.BoxSizer(wx.HORIZONTAL)
        
        upImage = wx.Bitmap(here + "/bitmap/up.png", wx.BITMAP_TYPE_ANY)
        self.moveUp = wx.BitmapButton(self.panel, bitmap=upImage, size=upImage.GetSize())
#        self.moveUp.SetTip("Move the selected column up")
        
        downImage = wx.Bitmap(here + "/bitmap/down.png", wx.BITMAP_TYPE_ANY)
        self.moveDown = wx.BitmapButton(self.panel, bitmap=downImage, size=downImage.GetSize())
#        self.moveDown.setToolTip("Move the selected column down")
        
        newImage = wx.Bitmap(here + "/bitmap/add.png", wx.BITMAP_TYPE_ANY)
        self.newCol = wx.BitmapButton(self.panel, bitmap=newImage, size=newImage.GetSize())
#        self.newCol.setToolTip("Add a new data column")
        
        #delImage = wx.Bitmap("bitmap/del.png", wx.BITMAP_TYPE_ANY)
        #self.delCol = wx.BitmapButton(self.panel, bitmap=delImage, size=delImage.GetSize())
        
        #add the buttons
        self.colButtons.Add(self.moveUp)
        self.colButtons.Add(self.moveDown)
        #self.colButtons.Add(self.delCol)
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