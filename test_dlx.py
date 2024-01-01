import dlx

import unittest
from pprint import pprint

class TestDLX2Node(unittest.TestCase):
    def assertLeftRight(self, node, left, right):
        self.assertEqual(node.left, left)
        self.assertEqual(node.right, right)

    def assertUpDown(self, node, up, down):
        self.assertEqual(node.up, up)
        self.assertEqual(node.down, down)

    def testRemoveAndAddUpDown(self):
        c = dlx.ColumnHeader("header")
        a = dlx.Node(c, "Row1")
        b = dlx.Node(c, "Row2")
        c.insertDown(a)
        a.insertDown(b)

        a.removeUpDown()

        self.assertEqual(a.up, c)
        self.assertEqual(a.down, b)
        self.assertEqual(c.up, b)
        self.assertEqual(c.down, b)
        self.assertEqual(b.up, c)
        self.assertEqual(b.down, c)

        a.addUpDown()

        self.assertEqual(c.down, a)
        self.assertEqual(c.up, b)
        self.assertEqual(a.down, b)
        self.assertEqual(a.up, c)
        self.assertEqual(b.down, c)
        self.assertEqual(b.up, a)

    def testRemoveAndAddLeftRight(self):
        columnHeader = dlx.ColumnHeader("header")
        a = dlx.Node(columnHeader, "Col1")
        b = dlx.Node(columnHeader, "Col2")
        c = dlx.Node(columnHeader, "Col3")

        a.insertRight(b)
        b.insertRight(c)

        b.removeLeftRight()
        self.assertEqual(b.left, a)
        self.assertEqual(b.right, c)
        self.assertEqual(a.left, c)
        self.assertEqual(a.right, c)
        self.assertEqual(c.left, a)
        self.assertEqual(c.right, a)

        b.addLeftRight()
        self.assertEqual(a.left, c)
        self.assertEqual(a.right, b)
        self.assertEqual(b.left, a)
        self.assertEqual(b.right, c)
        self.assertEqual(c.left, b)
        self.assertEqual(c.right, a)

    def testRemoveSingleNodes(self):
        columnHeader = dlx.ColumnHeader("header")
        a = dlx.Node(columnHeader, "Col1")
        b = dlx.Node(columnHeader, "Col2")
        a.insertRight(b)

        a.removeLeftRight()

        self.assertEqual(a.left, b)
        self.assertEqual(a.right, b)
        self.assertEqual(b.left, b)
        self.assertEqual(b.right, b)

        a.addLeftRight()
        self.assertEqual(a.left, b)
        self.assertEqual(a.right, b)
        self.assertEqual(b.left, a)
        self.assertEqual(b.right, a)

    def testIterateRightIncludeSelf(self):
        columnHeader = dlx.ColumnHeader("header")
        a = dlx.Node(columnHeader, "Col1")
        b = dlx.Node(columnHeader, "Col2")
        c = dlx.Node(columnHeader, "Col3")

        a.insertRight(b)
        b.insertRight(c)
        rows = [x.rowId for x in a.iterateRight(True)]
        self.assertListEqual(
            rows,
            ['Col2', 'Col3', 'Col1']
        )

        rows = [x.rowId for x in a.iterateRight(False)]
        self.assertListEqual(
            rows,
            ['Col2', 'Col3']
        )


class TestDLX2(unittest.TestCase):
    def assertLeftRight(self, node, left, right):
        self.assertEqual(node.left, left)
        self.assertEqual(node.right, right)

    def assertUpDown(self, node, up, down):
        self.assertEqual(node.up, up)
        self.assertEqual(node.down, down)

    def setUp(self):
        dlx.Node.NodeId = 0
        self.dlx = dlx.DLX()
        self.columns = [1,2,3,4,5,6,7]
        self.rows = [
            [x-1 for x in [1,4,7]], # A
            [x-1 for x in [1,4]], # B
            [x-1 for x in [4,5,7]], # C
            [x-1 for x in [3,5,6]], # D
            [x-1 for x in [2,3,6,7]], # E
            [x-1 for x in [2,7]], # F
        ]
        self.dlx.setColumns(self.columns)
        self.dlx.setRows(self.rows) 
        self.dlx._linkTogether()

        self.column1 = self.dlx.listHeader.right
        self.column2 = self.column1.right
        self.column3 = self.column2.right
        self.column4 = self.column3.right
        self.column5 = self.column4.right
        self.column6 = self.column5.right
        self.column7 = self.column6.right

        self.row1 = self.column1.down
        self.row2 = self.row1.down
        self.row3 = self.column4.down.left
        self.row4 = self.column3.down
        self.row5 = self.column2.down
        self.row6 = self.column2.down.down

        self.row1Ids = [8, 9, 10]
        self.row2Ids = [11, 12]
        self.row3Ids = [13, 14, 15]
        self.row4Ids = [16, 17, 18]
        self.row5Ids = [19, 20, 21, 22]
        self.row6Ids = [23, 24]

    def testLinkTogether(self):
        d = dlx.DLX()
        dlx.Node.NodeId = 0
        columns = [1,2,3,4,5,6,7]
        rows = [
            [x-1 for x in [1,4,7]], # A
            [x-1 for x in [1,4]], # B
            [x-1 for x in [4,5,7]], # C
            [x-1 for x in [3,5,6]], # D
            [x-1 for x in [2,3,6,7]], # E
            [x-1 for x in [2,7]], # F
        ]
        d.setColumns(columns)
        d.setRows(rows) 
        d._linkTogether()

        column1 = d.listHeader.right
        column2 = column1.right
        column3 = column2.right
        column4 = column3.right
        column5 = column4.right
        column6 = column5.right
        column7 = column6.right

        row1 = column1.down
        row2 = row1.down
        row3 = column4.down.down.down
        row4 = column3.down
        row5 = column2.down
        row6 = column2.down.down

        self.assertIsInstance(column1, dlx.ColumnHeader)
        self.assertIsInstance(column2, dlx.ColumnHeader)
        self.assertIsInstance(column3, dlx.ColumnHeader)
        self.assertIsInstance(column4, dlx.ColumnHeader)
        self.assertIsInstance(column5, dlx.ColumnHeader)
        self.assertIsInstance(column6, dlx.ColumnHeader)
        self.assertIsInstance(column7, dlx.ColumnHeader)
        self.assertIsInstance(row1, dlx.Node)
        self.assertIsInstance(row2, dlx.Node)
        self.assertIsInstance(row3, dlx.Node)
        self.assertIsInstance(row4, dlx.Node)
        self.assertIsInstance(row5, dlx.Node)
        self.assertIsInstance(row6, dlx.Node)

        self.assertEqual(column1.nodeId, 1)
        self.assertEqual(column2.nodeId, 2)
        self.assertEqual(column3.nodeId, 3)
        self.assertEqual(column4.nodeId, 4)
        self.assertEqual(column5.nodeId, 5)
        self.assertEqual(column6.nodeId, 6)
        self.assertEqual(column7.nodeId, 7)

        # [x-1 for x in [4,7,1]], # A
        # [x-1 for x in [4,1]], # B
        # [x-1 for x in [5,7,4]], # C
        # [x-1 for x in [5,6,3]], # D
        # [x-1 for x in [3,6,7,2]], # E
        # [x-1 for x in [7,2]], # F
        def nodeIds(node):
            x = [x.nodeId for x in node.iterateRight()]
            return [x[-1]] + x[0:-1]
        self.assertListEqual(nodeIds(row1), [8, 9, 10])
        self.assertListEqual(nodeIds(row2), [11, 12])
        self.assertListEqual(nodeIds(row3), [13, 14, 15])
        self.assertListEqual(nodeIds(row4), [16, 17, 18])
        self.assertListEqual(nodeIds(row5), [19, 20, 21, 22])
        self.assertListEqual(nodeIds(row6), [23, 24])

        def nodeIds(node):
            x = [x.nodeId for x in node.iterateDown()]
            return [x[-1]] + x[0:-1]
        self.assertListEqual(nodeIds(column1), [1, 8, 11])
        self.assertListEqual(nodeIds(column2), [2, 19, 23])
        self.assertListEqual(nodeIds(column3), [3, 16, 20])
        self.assertListEqual(nodeIds(column4), [4, 9, 12, 13])
        self.assertListEqual(nodeIds(column5), [5, 14, 17])
        self.assertListEqual(nodeIds(column6), [6, 18, 21])
        self.assertListEqual(nodeIds(column7), [7, 10, 15, 22, 24])

        #
        #  1   2   3   4   5   6   7
        #  8           9           10       [1,4,7]
        #  11          12                   [1,4]
        #              13  14      15       [4,5,7]
        #          16      17  18           [3,5,6]
        #      19  20          21  22       [2,3,6,7]
        #      23                  24       [2,7]

    def testChooseColumn(self):
        chosenColumn = self.dlx._chooseColumn()
        self.assertEqual(chosenColumn.nodeId, 1)
        self.assertEqual(chosenColumn.size, 2)

    def testCoverAndUnCoverColumn(self):
        LR_Nodes = []
        UD_Nodes = []
        beforeRowNodes = {}
        beforeColumnNodes = []
        beforeOtherColumnNodes = {}
        for node in self.column2.iterateDown():
            LR_Nodes.append((node.left, node.right))
            UD_Nodes.append((node.up, node.down))
            beforeColumnNodes.append(node)
            beforeRowNodes[node.nodeId] = [r for r in node.iterateRight()]

            if node == self.column2:
                continue
            for r in node.iterateRight():
                if r.columnHeader == self.column2:
                    continue
                beforeOtherColumnNodes[r.columnHeader.nodeId] = [r.nodeId for r in r.columnHeader.iterateDown()]

        # do the cover
        self.dlx._coverColumn(self.column2)

        # Assert that column2 still has all of it's column elements
        self.assertListEqual(
            [node for node in self.column2.iterateDown()],
            beforeColumnNodes
        )
        self.assertEqual(self.column2.size, 2)
        
        # Every node in the column should still have intact pointers
        for i,node in enumerate(self.column2.iterateDown()):
            self.assertLeftRight(node, LR_Nodes[i][0], LR_Nodes[i][1])
            self.assertUpDown(node, UD_Nodes[i][0], UD_Nodes[i][1])

        # Every row from the covered column should still be intact
        for node in self.column2.iterateDown(False):
            self.assertListEqual(
                beforeRowNodes[node.nodeId],
                [r for r in node.iterateRight()]
            ) 

        # All the other columns should not longer have a reference
        # to these rows
        for node in self.column2.iterateDown(False):
            for r in node.iterateRight():
                if r.columnHeader == self.column2:
                    continue
                got = set([r.nodeId for r in r.columnHeader.iterateDown()])
                self.assertTrue(r.nodeId not in got)
                self.assertTrue(r.columnHeader.size < len(got))

        # do the uncover
        self.dlx._uncoverColumn(self.column2)

        AfterLR_Nodes = []
        AfterUD_Nodes = []
        afterRowNodes = {}
        afterColumnNodes = []
        afterOtherColumnNodes = {}
        for node in self.column2.iterateDown():
            AfterLR_Nodes.append((node.left, node.right))
            AfterUD_Nodes.append((node.up, node.down))
            afterColumnNodes.append(node)
            afterRowNodes[node.nodeId] = [r for r in node.iterateRight()]

            if node == self.column2:
                continue
            for r in node.iterateRight():
                if r.columnHeader == self.column2:
                    continue
                afterOtherColumnNodes[r.columnHeader.nodeId] = [r.nodeId for r in r.columnHeader.iterateDown()]

        self.assertListEqual(LR_Nodes, AfterLR_Nodes)
        self.assertListEqual(UD_Nodes, AfterUD_Nodes)
        self.assertListEqual(beforeColumnNodes, afterColumnNodes)
        for nodeId in beforeRowNodes:
            self.assertListEqual(
                beforeRowNodes[nodeId],
                afterRowNodes[nodeId]
            )
        for nodeId in beforeOtherColumnNodes:
            self.assertListEqual(
                beforeOtherColumnNodes[nodeId],
                afterOtherColumnNodes[nodeId]
            )
        for node in self.column2.iterateDown(False):
            for r in node.iterateRight(False):
                got = set([r.nodeId for r in r.columnHeader.iterateDown(False)])
                self.assertEqual(r.columnHeader.size, len(got))

    def testMultipleCoverCols(self):
        beforeRep = self.dlx._getDlxRepresentation()
        self.dlx._coverColumn(self.column1)
        self.dlx._coverColumn(self.column2)
        self.dlx._coverColumn(self.column3)
        self.dlx._coverColumn(self.column4)
        self.dlx._uncoverColumn(self.column4)
        self.dlx._uncoverColumn(self.column3)
        self.dlx._uncoverColumn(self.column2)
        self.dlx._uncoverColumn(self.column1)
        afterRep = self.dlx._getDlxRepresentation()

        self.assertDictEqual(
            beforeRep,
            afterRep
        )
        # print()
        # pprint(self.dlx._createMatrix(beforeRep, True))
        # pprint(self.dlx._createMatrix(afterRep, True))
        # pprint(self.dlx._createMatrix(self.dlx._getDlxRepresentation(), pretty=True))

    def testCoverAndUncoverRow(self):
        beforeRep = self.dlx._getDlxRepresentation()
        self.dlx._coverColumn(self.dlx.columnIds[0])
        self.dlx._uncoverColumn(self.dlx.columnIds[0])
        afterRep = self.dlx._getDlxRepresentation()
        self.assertDictEqual(beforeRep, afterRep)
        # pprint(self.dlx._createMatrix(beforeRep, True))
        # pprint(self.dlx._createMatrix(afterRep, True))

    def testSolve(self):
        allSolutions = [x for x in self.dlx.solve()]
        self.assertEqual(len(allSolutions), 1)
        self.assertSetEqual(set(allSolutions[0]), set([1,3,5]))

    def testSolveNoSolution(self):
        pass

        # # pprint(self.dlx._createMatrix(beforeRep, True))
        # print()
        # beforeRep = self.dlx._getDlxRepresentation()
        # pprint(self.dlx._createMatrix(beforeRep, True))
        # row_4_1 = self.dlx.rowIds[4][1]
        # self.assertEqual(row_4_1.nodeId, 20)

        # # Covering row 4_1 means we must remove 
        # # columns 2, 3, 7, and 7
        # self.dlx._coverRow(row_4_1)
        # self.dlx._uncoverRow(row_4_1)
        # afterRep = self.dlx._getDlxRepresentation()

        # pprint(self.dlx._createMatrix(beforeRep, True))
        # pprint(self.dlx._createMatrix(afterRep, True))

        # self.dlx._coverColumn(self.dlx

        # self.assertEqual(
        #     self.dlx.rowIds[4][1].up,
        #     self.dlx.rowIds[3][0]
        # )

        # rep = self.dlx._getDlxRepresentation()
        # pprint(rep)
        # pprint(self.dlx._createMatrix(self.dlx._getDlxRepresentation(), pretty=True))
        # pprint(self.dlx.columnIds)
        # pprint(self.dlx.rowIds)
        #
        #  1   2   3   4   5   6   7
        #  8           9           10       [1,4,7]
        #  11          12                   [1,4]
        #              13  14      15       [4,5,7]
        #          16      17  18           [3,5,6]
        #      19  20          21  22       [2,3,6,7]
        #      23                  24       [2,7]

        #  1   2   3   4   5   6   7
        #          8       9   10           [3,5,6]
        #  11          12          13       [1,4,7]
        #      14  15          16           [2,3,6]
        #  17          18                   [1,4]
        #      19                  20       [2,7]
        #              21  22      23       [4,5,7]
        pass


if __name__ == '__main__':
    unittest.main()