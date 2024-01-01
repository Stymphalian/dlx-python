#!/usr/bin/env python
# From Donald Knuth's Paper: http://lanl.arxiv.org/pdf/cs/0011047

from pprint import pprint

class Node:
    NodeId = 0

    def __init__(self, columnHeader, rowId=None):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.columnHeader = columnHeader
        self.rowId = rowId

        self.nodeId = Node.NodeId
        Node.NodeId += 1

    def insertRight(self, other):
        sRight = self.right
        self.right = other
        other.right = sRight
        sRight.left = other
        other.left = self

    def insertDown(self, other):
        sDown = self.down
        self.down = other
        other.down = sDown
        sDown.up = other
        other.up = self

        self.columnHeader.size += 1

    def removeUpDown(self):
        # Keep the pointer of `self` intact. But remove
        # it from the linked list
        self.up.down = self.down
        self.down.up = self.up
        self.columnHeader.size -= 1

    def removeLeftRight(self):
        self.right.left = self.left
        self.left.right = self.right

    def addUpDown(self):
        # Because the pointers of `self` have been left intact
        # we can easily re-add the node back into its original
        # position in the linked list
        self.up.down = self
        self.down.up = self
        self.columnHeader.size += 1

    def addLeftRight(self):
        self.right.left = self
        self.left.right = self

    def iterateRight(self, includeSelf=True):
        current = self.right
        while current != self:
            yield current
            current = current.right
        if includeSelf:
            yield self

    def iterateLeft(self, includeSelf=True):
        current = self.left
        while current != self:
            yield current
            current = current.left
        if includeSelf:
            yield self
            
    def iterateDown(self, includeSelf=True):
        current = self.down
        while current != self:
            yield current
            current = current.down
        if includeSelf:
            yield self

    def iterateUp(self, includeSelf=True):
        current = self.up
        while current != self:
            yield current
            current = current.up
        if includeSelf:
            yield self
            
    def __str__(self):
        colName = ""
        if self.columnHeader is not None:
            colName = self.columnHeader.name
        return f"Node({self.nodeId}, {self.rowId}, {colName})"
    
    def __repr__(self):
        colName = ""
        if self.columnHeader is not None:
            colName = self.columnHeader.name
        return f"Node({self.nodeId}, {self.rowId}, {colName})"


class ColumnHeader(Node):
    def __init__(self, name):
        super().__init__(columnHeader=self, rowId=None)
        self.size = 0
        self.name = name

    def __str__(self):
        return f"ColumnHeader({self.nodeId}, {self.name})"
    
    def __repr__(self):
        return f"ColumnHeader({self.nodeId}, {self.name})"

class DLX:
    def __init__(self):
        self.rows = None
        self.columns = None

        self.listHeader = None
        self.columnIds = {}
        self.rowIds = {}
        self.solution = {}

    """
    Arguments:
        columns: A list of strings which represent the elements of the Set.
                 These are used as the name of the columns.
    Return: DLX object
    """
    def setColumns(self, columns):
        self.columns = columns
        return self
            
    """
    Arguments:
        rows: A list of lists. The inner list should contain integers which are the 
            indices into the columns array which was used in setColumns
            These are considered the 'constraints' of the covering
    Return: DLX object
    """
    def setRows(self, rows):
        self.rows = rows
        return self
    
    """
    Returns all the solutions for the covering. This is a generator function.
    If you only want a single solution just call it once. Otherwise iterate
    through all the solutions.

    Return: list[int] returns a list of integers which are the row indices which
            are included in the covering.
            If None is returned then no solution exists
    """
    def solve(self):
        self._linkTogether()
        for solution in self._search(0):
            yield solution

    # Given all the columns and rows for this DLX
    # we will create all the left-right, up-down linked lists 
    def _linkTogether(self):
        if self.columns is None or self.rows is None:
            raise Exception("Must first setColumns before trying to solve()")
        if self.rows is None:
            raise Exception("Must first setRows before trying to solve()")
        
        columnObjects = []
        rowObjects = []

        self.columnIds = {}
        self.rowIds = {}

        # Set the column headers
        self.listHeader = ColumnHeader(None)
        current = self.listHeader
        for ci, c in enumerate(self.columns):
            newColumn = ColumnHeader(c)
            current.insertRight(newColumn)
            current = newColumn
            columnObjects.append(newColumn)
            self.columnIds[ci] = current

        # Iterate through every row and link them up-down and left-right
        for rowNum, row in enumerate(self.rows):
            currentNode = None

            rowIds = {}
            for ri, columnIndex in enumerate(row):
                lastColumnNode = columnObjects[columnIndex]
                newNode = Node(
                    lastColumnNode.columnHeader, 
                    (rowNum,ri)
                    # str([x+1 for x in row])
                )

                # Link up and down
                lastColumnNode.insertDown(newNode)
                # Link left and right
                if currentNode is not None:
                    currentNode.insertRight(newNode)
                
                # update the pointers
                currentNode = newNode
                columnObjects[columnIndex] = newNode
                rowIds[ri] = currentNode
            
            rowObjects.append(currentNode)
            self.rowIds[rowNum] = rowIds

    def _search(self, depth):
        if self._columnsAreCovered():
            yield [x.rowId[0] for x in self.solution.values()]
            return

        # Choose a column to try and cover
        columnHeader = self._chooseColumn()
        if columnHeader == self.listHeader or columnHeader.size == 0:
            # there are no more rows but we still have columns 
            # we need to cover. There is no solution, so return
            return

        self._coverColumn(columnHeader)

        for rowNode in columnHeader.iterateDown(False):
            # Add row `R` as apart of the solution
            self.solution[depth] = rowNode
            self._coverRow(rowNode)

            # recursive call to find solutions for sub-problem
            for solution in self._search(depth+1):
                yield solution

            # backtrack
            self._uncoverRow(rowNode)
            del self.solution[depth]

        self._uncoverColumn(columnHeader)

    # Find the column which has the smallest number of rows 
    def _chooseColumn(self):
        bestColumn = None
        for columnHeader in self.listHeader.iterateRight(False):
            if bestColumn is None:
                bestColumn = columnHeader
            elif columnHeader.size < bestColumn.size:
                bestColumn = columnHeader
        return bestColumn
    
    def _coverRow(self, rowNode: Node):
        for currentNode in rowNode.iterateRight(False):
            columnHeader = currentNode.columnHeader
            self._coverColumn(columnHeader)
        
    def _uncoverRow(self, rowNode: Node):
        for currentNode in rowNode.iterateLeft(False):
            columnHeader = currentNode.columnHeader
            self._uncoverColumn(columnHeader)

    def _coverColumn(self, columnHeader: ColumnHeader):
        # remove this column from the listHeaders
        columnHeader.removeLeftRight()

        # go through every row belonging to this column
        # for every column in which those rows belong 
        # remove it from that column
        for rowNode in columnHeader.iterateDown(includeSelf=False):
            for rightNeighbour in rowNode.iterateRight(includeSelf=False):
                rightNeighbour.removeUpDown()

    def _uncoverColumn(self, columnHeader: ColumnHeader):
        # go through every row belonging to this column
        # for every column in which those rows belong 
        # re-add it to the column
        for rowNode in columnHeader.iterateUp(includeSelf=False):
            for rightNeighbour in rowNode.iterateLeft(includeSelf=False):
                rightNeighbour.addUpDown()

        # re-add this column back into the listHeaders
        columnHeader.addLeftRight()

    def _columnsAreCovered(self):
        return self.listHeader.right == self.listHeader
    
    def _printMat(self):
        rep = self._getDlxRepresentation()
        pprint(self._createMatrix(rep, True))
    
    def _getDlxRepresentation(self):
        columnHeaders = []
        rowsFromTopLeft = []
        seenRows = set([])
        for columnHeader in self.listHeader.iterateRight(False):
            columnHeaders.append(
                (
                    columnHeader.nodeId,
                    columnHeader.name,
                    columnHeader.left.nodeId,
                    columnHeader.right.nodeId,
                    [x.nodeId for x in columnHeader.iterateDown(False)],
                    columnHeader.size
                )
            )

            for rowNode in columnHeader.iterateDown(False):
                rows = []
                if rowNode.nodeId in seenRows:
                    continue
                seenRows.add(rowNode.nodeId)
                for node in rowNode.iterateRight():
                    seenRows.add(node.nodeId)
                    rows.append((
                        node.nodeId,
                        node.rowId,
                        node.columnHeader.name,
                        node.columnHeader.nodeId,
                        node.left.nodeId,
                        node.right.nodeId,
                        node.up.nodeId,
                        node.down.nodeId
                    ))
                rows = [rows[-1]] + rows[0:-1]
                rowsFromTopLeft.append(rows)
        rowsFromTopLeft.sort(key=lambda x: x[1])

        return {
            "columnHeaders": columnHeaders,
            "rows": rowsFromTopLeft
        }

    def _createMatrix(self, rep, pretty=False):
        numberOfCols = len(rep["columnHeaders"])
        mapping = {}
        for ci, col in enumerate(rep["columnHeaders"]):
            mapping[col[0]] = ci

        matrix = []
        if pretty:
            matrix.append(["{0:<3}".format(str(x[1])) for x in rep["columnHeaders"]])
        # matrix.append([x[1] for x in rep["columnHeaders"]])
        for row in rep["rows"]:
            entry = [0 for _ in range(numberOfCols)]
            for c in row:
                if pretty:
                    entry[mapping[c[3]]] = c[0]
                else:
                    entry[mapping[c[3]]] = 1
            if pretty:
                matrix.append(["{0:<3}".format(str(x)) for x in entry])
            else:
                matrix.append(entry)
            
        return matrix

    def test(self):
        self.testChooseColumn()
        # self._linkTogether()
        # for current in self.listHeader.iterateRight():
        #     print(current.name, current.size)
        # for rowId,_ in enumerate(self.rows):
        #     print(self._getRow(rowId))
        # pprint(self._toMatrix())


def main():
    dlx = DLX()

    # The columns represents the elements of the Set. These should
    # be strings which present the name of the column
    columns = [1,2,3,4,5,6,7]

    # A list of lists. The lists should contain the index of the 
    # the column which belongs to this constraint
    rows = [
        [x-1 for x in [1,4,7]], # A
        [x-1 for x in [1,4]], # B
        [x-1 for x in [4,5,7]], # C
        [x-1 for x in [3,5,6]], # D
        [x-1 for x in [2,3,6,7]], # E
        [x-1 for x in [2,7]], # F
    ]
    dlx.setColumns(columns)
    dlx.setRows(rows) 

    # Solution is a list of integers, which are indices into the provided
    # list of rows.
    # for example:
    # [1,3,5] corresponds to
    # 1: [1,4]
    # 3: [3,5,6]
    # 5: [2,7]
    solutions = [x for x in dlx.solve()]
    pprint(solutions)

if __name__ == "__main__":
    main()