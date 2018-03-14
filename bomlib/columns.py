class ColumnList:

    #default columns (immutable)
    COL_REFERENCE = 'References'
    COL_DESCRIPTION = 'Description'
    COL_VALUE = 'Value'
    COL_FP = 'Footprint'
    COL_FP_LIB = 'Footprint Lib'
    COL_PART = 'Part'
    COL_PART_LIB = 'Part Lib'
    COL_DATASHEET = 'Datasheet'

    #default columns for groups
    COL_GRP_QUANTITY = 'Quantity Per PCB'
    COL_GRP_TOTAL_COST = 'Total Cost' #Total cost based on quantity
    COL_GRP_BUILD_QUANTITY = 'Build Quantity'

    #generated columns
    _COLUMNS_GEN = [
                COL_GRP_QUANTITY,
                COL_GRP_BUILD_QUANTITY,
                ]

    #default columns
    _COLUMNS_DEFAULT = [
               COL_DESCRIPTION,
               COL_PART,
               COL_PART_LIB,
               COL_REFERENCE,
               COL_VALUE,
               COL_FP,
               COL_FP_LIB,
               COL_GRP_QUANTITY,
               COL_GRP_BUILD_QUANTITY,
               COL_DATASHEET
               ]

    #default columns
    #these columns are 'immutable'
    _COLUMNS_PROTECTED = [
                COL_REFERENCE,
                COL_GRP_QUANTITY,
                COL_VALUE,
                COL_PART,
                COL_PART_LIB,
                COL_DESCRIPTION,
                COL_DATASHEET,
                COL_FP,
                COL_FP_LIB
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

    def _hasColumn(self, col):
        #col can either be <str> or <Column>
        return col.lower() in [c.lower() for c in self.columns]

    """
    Remove a column from the list. Specify either the heading or the index
    """
    def RemoveColumn(self, col):
        if type(col) is str:
            self.RemoveColumnByName(col)
        elif type(col) is int and col >= 0 and col < len(self.columns):
            self.RemoveColumnByName(self.columns[col])

    def RemoveColumnByName(self, name):

        #first check if this is in an immutable colum
        if name in self._COLUMNS_PROTECTED:
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

        #Already exists?
        if self._hasColumn(col):
            return

        if type(index) is not int or index < 0 or index >= len(self.columns): #append
            self.columns.append(col)

        #otherwise, splice the new column in
        else:
            self.columns = self.columns[0:index] + [col] + self.columns[index:]


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
