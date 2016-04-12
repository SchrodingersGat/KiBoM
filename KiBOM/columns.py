
class Columns:

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
    
    #all available columns
    _COLUMNS_ALL = [
               COL_DESCRIPTION,
               COL_PART,
               COL_PART_LIB,
               COL_REFERENCE,
               COL_VALUE,
               COL_FP,
               COL_FP_LIB,
               COL_DATASHEET
               ]
                   
    #default columns
    #these columns are 'immutable'
    _COLUMNS_DEFAULT = [
                COL_DESCRIPTION,
                COL_PART,
                COL_REFERENCE,
                COL_VALUE,
                COL_FP
                ]
                
    _COLUMNS_GROUPED = [
                COL_GRP_QUANTITY,
                ]
    
    def __str__(self):
        return " ".join(self.columns)

    def __repr__(self):
        return self.__str__()
                
    def __init__(self, cols=_COLUMNS_DEFAULT):

        #make a copy of the supplied columns
        self.columns = [col for col in cols]
        
        self._checkDefaultColumns()

    def _hasColumn(self, title):

        title = title.lower()
        
        for c in self.columns:
            if c.lower() == title:
                return True

        return False
        
    def _checkDefaultColumns(self):
        
        #prepend any default columns that don't exist
        for c in self._COLUMNS_DEFAULT[::-1]:
            if c not in self.columns:
                self.columns = [c] + self.columns

    """
    Remove a column from the list. Specify either the heading or the index
    """
    def RemoveColumn(self, col):
        if type(col) is str:
            self.RemoveColumnByName(col)
        elif type(col) is int and col >= 0 and col < len(self.columns):
            self.RemoveColumnByName(self.columns[col])

    def RemoveColumnByName(self, name):

        name = name.lower()

        #first check if this is in an immutable colum
        if name in [c.lower() for c in self._COLUMNS_DEFAULT]:
            return

        #Obtain a <lower-case> list of all columns for comparison
        lCols = [c.lower() for c in self.columns]

        #column does not exist, return
        if name not in lCols:
            return

        try:
            index = lCols.index(name)
            del self.columns[index]
        except ValueError:
            return

    #add a new column (if it doesn't already exist!)
    def AddColumn(self, title, index=None):

        if type(title) is not str:
            return

        if self._hasColumn(title):
            return

        if type(index) is not int or index < 0 or index >= len(self.columns): #append
            self.columns.append(title)

        #otherwise, splice the new column in
        else:
            self.columns = self.columns[0:index] + [title] + self.columns[index:]

if __name__ == '__main__':
    c = Columns()

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
