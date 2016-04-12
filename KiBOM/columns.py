
class Column:

    COL_TYPE_KICAD = "KiCAD" #Immutable columns defined within KiCAD
    COL_TYPE_FIELD = "Field" #Fields defined within KiCAD, by the user
    COL_TYPE_EXT = "External" #Fields defined in external BoM, not stored within KiCAD

    #default columns (immutable)
    COL_REFERENCE = 'Reference'
    COL_DESCRIPTION = 'Description'
    COL_VALUE = 'Value'
    COL_FP = 'Footprint'
    COL_FP_LIB = 'Footprint Lib'
    COL_PART = 'Part'
    COL_PART_LIB = 'Part Lib'
    COL_DATASHEET = 'Datasheet'
    
    #default columns for groups
    COL_GRP_QUANTITY = 'Quantity'
    
    def __init__(self, title, vis=True, colType=COL_TYPE_FIELD):
        self.title = str(title)
        self.visible = vis
        
    #column comparison
    def __eq__(self, other):
        #match based on string
        if type(other) == str:
            return other.lower() == self.title.lower()
        #match based on Column
        if type(other) == Column:
            return other.title.lower() == self.title.lower()
        #no match
        return False
        
    def __str__(self):
        return self.title

    def __repr__(self):
        return "'" + self.__str__() + "'"
        
class ColumnList:

    #all available columns
    _COLUMNS_ALL = [
               Column.COL_DESCRIPTION,
               Column.COL_PART,
               Column.COL_PART_LIB,
               Column.COL_REFERENCE,
               Column.COL_VALUE,
               Column.COL_FP,
               Column.COL_FP_LIB,
               Column.COL_DATASHEET
               ]
                   
    #default columns
    #these columns are 'immutable'
    _COLUMNS_DEFAULT = [
                Column.COL_DESCRIPTION,
                Column.COL_PART,
                Column.COL_REFERENCE,
                Column.COL_VALUE,
                Column.COL_FP
                ]

    #Columns that only exist for the 'grouped' components  
    _COLUMNS_GROUPED = [
                Column.COL_GRP_QUANTITY,
                ]

    def __str__(self):
        return " ".join(map(str,self.columns))

    def __repr__(self):
        return self.__str__()
                
    def __init__(self, cols=_COLUMNS_DEFAULT):

        self.columns = []

        #make a copy of the supplied columns
        for col in cols:
            self.AddColumn(col)
        
        self._checkDefaultColumns()

    def _hasColumn(self, col):
        #col can either be <str> or <Column>
        return col in self.columns
        
    def _checkDefaultColumns(self):
        
        #prepend any default columns that don't exist
        for c in self._COLUMNS_DEFAULT[::-1]:
            if c not in self.columns:
                self.columns = [Column(c)] + self.columns

    """
    Remove a column from the list. Specify either the heading or the index
    """
    def RemoveColumn(self, col):
        if type(col) is str:
            self.RemoveColumnByName(col)
        if type(col) is Column:
            self.RemoveColumnByName(col.title)
        elif type(col) is int and col >= 0 and col < len(self.columns):
            self.RemoveColumnByName(self.columns[col])

    def RemoveColumnByName(self, name):

        #first check if this is in an immutable colum
        if name in self._COLUMNS_DEFAULT:
            return

        #column does not exist, return
        if name not in self.columns:
            return

        try:
            index = self.columns.index(name)
            del self.columns[index]
        except ValueError:
            return

    #add a new column (if it doesn't already exist!)
    def AddColumn(self, col, index=None):

        if type(col) == Column:
            pass
        elif type(col) == str:
            col = Column(col)
        else:
            return

        #Already exists?
        if self._hasColumn(col):
            return

        if type(index) is not int or index < 0 or index >= len(self.columns): #append
            self.columns.append(col)

        #otherwise, splice the new column in
        else:
            self.columns = self.columns[0:index] + [col] + self.columns[index:]

    def VisibleColumns(self):
        return [col for col in self.columns if col.visible]


if __name__ == '__main__':
    c = ColumnList()

    c.AddColumn("Test1")
    c.AddColumn("Test1")
    c.AddColumn("Test2")
    c.AddColumn("Test3")
    c.AddColumn("Test4")
    c.AddColumn("Test2")

    c.RemoveColumn("Test2")
    c.RemoveColumn("Part")
    c.RemoveColumn(2)
    c.RemoveColumn(5)
