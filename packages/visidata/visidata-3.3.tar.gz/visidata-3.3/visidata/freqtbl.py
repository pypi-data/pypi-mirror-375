from copy import copy
import itertools

from visidata import vd, vlen, VisiData, Column, AttrColumn, Sheet, ColumnsSheet, ENTER, Fanout
from visidata.pivot import PivotSheet, PivotGroupRow


vd.theme_option('disp_histogram', '■', 'histogram element character')
vd.option('histogram_bins', 0, 'number of bins for histogram of numeric columns')
vd.option('numeric_binning', False, 'bin numeric columns into ranges', replay=True)


@VisiData.api
def valueNames(vd, discrete_vals, numeric_vals):
    ret = [ '+'.join(str(x) for x in discrete_vals) ]
    if isinstance(numeric_vals, tuple) and numeric_vals != (0, 0):
        ret.append('%s-%s' % numeric_vals)

    return '+'.join(ret)

class HistogramColumn(Column):
    '.sourceCol is the column to be histogrammed'
    def calcValue(col, row):
        histogram = col.sheet.options.disp_histogram
        histolen = col.width-2
        return histogram*(histolen*col.sourceCol.getTypedValue(row)//col.largest)

    def updateLargest(col, row):
        col.largest = max(col.largest, col.sourceCol.getTypedValue(row))


def makeFreqTable(sheet, *groupByCols):
    if not any(groupByCols):
        vd.fail('FreqTableSheet requires at least 1 column for grouping')
    return FreqTableSheet(sheet.name,
                          '%s_freq' % '-'.join(col.name for col in groupByCols),
                          groupByCols=groupByCols,
                          source=sheet)


class FreqTableSheet(PivotSheet):
    'Generate frequency-table sheet on currently selected column.'
    guide = '''# Frequency Table
This is a *frequency analysis* of _{sheet.groupByColsName}_ from the *{sheet.groupByCols[0].sheet}* sheet.

Each row on this sheet corresponds to a *bin* of rows on the source sheet that have a distinct value.  The _count_ and _percent_ columns show how many rows on the source sheet are in this bin.

- `Enter` to open a copy of the source sheet, with only the rows in the current bin.
- `g Enter` to open a copy of the source sheet, with a combination of the rows from all selected bins.

## Tips

- Use `+` on the source sheet, to add aggregators on other columns, and those metrics will appear as separate columns here.
- Selecting bins on this sheet will select those rows on the source sheet.
'''
    rowtype = 'bins'  # rowdef FreqRow(keys, sourcerows)

    @property
    def groupByColsName(self):
        return '+'.join(c.name for c in self.groupByCols)

    def selectRow(self, row):
        # Does not create an undo-operation for the select on the source rows. The caller should create undo-information itself.
        self.source.select(row.sourcerows, status=False, add_undo=False)     # select all entries in the bin on the source sheet
        return super().selectRow(row)  # then select the bin itself on this sheet

    def unselectRow(self, row):
        self.source.unselect(row.sourcerows, status=False, add_undo=False)
        return super().unselectRow(row)

    def addUndoSelection(self):
        self.source.addUndoSelection()
        super().addUndoSelection()

    # override Sheet operations that handle multiple rows:
    #     select(), unselect(), and toggle()
    # to make undo more efficient. Without this optimization, the memory
    # use for the undo-tracking on the source sheet is O(n^2) in the number
    # of bins selected, which can easily exceed all available memory.
    def select(self, rows, status=True, progress=True, add_undo=True):
        if add_undo:
            self.addUndoSelection()
        super().select(rows, status, progress, add_undo=False)

    def unselect(self, rows, status=True, progress=True, add_undo=True):
        if add_undo:
            self.addUndoSelection()
        super().unselect(rows, status, progress, add_undo=False)

    def toggle(self, rows, add_undo=True):
        'Toggle selection of given *rows* and corresponding rows in source sheet.'
        if add_undo:
            self.addUndoSelection()
        super().toggle(rows, add_undo=False)

    def select_row(self, row, add_undo=True):
        'Add single *row* to set of selected rows, and corresponding rows in source sheet.'
        if add_undo:
            self.addUndoSelection()
        super().select_row(row, add_undo=False)

    def unselect_row(self, row, add_undo=True):
        'Remove single *row* from set of selected rows, and remove corresponding rows in source sheet.'
        if add_undo:
            self.addUndoSelection()
        super().unselect_row(row, add_undo=False)

    def toggle_row(self, row, add_undo=True):
        'Toggle selection of given *row* and of corresponding rows in source sheet.'
        if add_undo:
            self.addUndoSelection()
        super().toggle_row(row, add_undo=False)

    def resetCols(self):
        super().resetCols()

        # add default bonus columns
        countCol = AttrColumn('count', 'sourcerows', type=vlen)
        for c in [
            countCol,
            Column('percent', type=float, getter=lambda col,row: len(row.sourcerows)*100/col.sheet.source.nRows),
        ]:
            self.addColumn(c)

        if self.options.disp_histogram:
            c = HistogramColumn('histogram', type=str, width=self.options.default_width*2, sourceCol=countCol)
            self.addColumn(c)

        # if non-numeric grouping, reverse sort by count at end of load
        if not any(vd.isNumeric(c) for c in self.groupByCols):
            self._ordering = [(countCol, True)]

    def loader(self):
        'Generate frequency table.'
        # two more threads
        histcols = [col for col in self.visibleCols if isinstance(col, HistogramColumn)]
        vd.sync(self.addAggregateCols(),
                self.groupRows(lambda row, cols=Fanout(histcols): cols.updateLargest(row)))

    def afterLoad(self):
        super().afterLoad()
        if self.nCols > len(self.groupByCols)+3:  # hide percent/histogram if aggregations added
            self.column('percent').hide()
            self.column('histogram').hide()

    def openRow(self, row):
        'open copy of source sheet with rows that are grouped in current row'
        if row.sourcerows:
            vs = copy(self.source)
            vs.names = vs.names + [vd.valueNames(row.discrete_keys, row.numeric_key)]
            vs.rows=copy(row.sourcerows)
            return vs
        vd.warning("no source rows")

    def openRows(self, rows):
        vs = copy(self.source)
        vs.names = vs.names + ["several"]
        vs.source = self
        vs.rows = list(itertools.chain.from_iterable(row.sourcerows for row in rows))
        return vs

    def openCell(self, col, row):
        return Sheet.openCell(self, col, row)


class FreqTableSheetSummary(FreqTableSheet):
    'Append a PivotGroupRow to FreqTableSheet with only selectedRows.'
    def afterLoad(self):
        self.addRow(PivotGroupRow(['Selected'], (0,0), self.source.selectedRows, {}))
        super().afterLoad()


def makeFreqTableSheetSummary(sheet, *groupByCols):
    return FreqTableSheetSummary(sheet.name,
                          '%s_freq' % '-'.join(col.name for col in groupByCols),
                          groupByCols=groupByCols,
                          source=sheet)


@VisiData.api
class FreqTablePreviewSheet(Sheet):
    @property
    def rows(self):
        return self.source.cursorRow.sourcerows


FreqTableSheet.addCommand('', 'open-preview', 'vd.push(FreqTablePreviewSheet(sheet.name, "preview", source=sheet, columns=source.columns), pane=2); vd.options.disp_splitwin_pct=50', 'open split preview of source rows at cursor')

Sheet.addCommand('F', 'freq-col', 'vd.push(makeFreqTable(sheet, cursorCol))', 'open Frequency Table grouped on current column, with aggregations of other columns')
Sheet.addCommand('gF', 'freq-keys', 'vd.push(makeFreqTable(sheet, *keyCols)) if keyCols else vd.fail("there are no key columns to group by")', 'open Frequency Table grouped by all key columns on source sheet, with aggregations of other columns')
Sheet.addCommand('zF', 'freq-summary', 'vd.push(makeFreqTableSheetSummary(sheet, Column("Total", sheet=sheet, getter=lambda col, row: "Total")))', 'open one-line summary for all rows and selected rows')

ColumnsSheet.addCommand(ENTER, 'freq-row', 'vd.push(makeFreqTable(source[0], cursorRow))', 'open a Frequency Table sheet grouped on column referenced in current row')
vd.addMenuItem('Data', 'Frequency table', 'current row', 'freq-row')

FreqTableSheet.addCommand('gu', 'unselect-rows', 'unselect(selectedRows)', 'unselect all source rows grouped in current row')
FreqTableSheet.addCommand('g'+ENTER, 'dive-selected', 'vd.push(openRows(selectedRows))', 'open copy of source sheet with rows that are grouped in selected rows')
FreqTableSheet.addCommand('', 'select-first', 'for r in rows: source.select([r.sourcerows[0]])', 'select first source row in each bin')

HistogramColumn.init('largest', lambda: 1)

vd.addGlobals(
    makeFreqTable=makeFreqTable,
    makeFreqTableSheetSummary=makeFreqTableSheetSummary,
    FreqTableSheet=FreqTableSheet,
    FreqTableSheetSummary=FreqTableSheetSummary,
    HistogramColumn=HistogramColumn,
)

vd.addMenuItems('''
    Data > Frequency table > current column > freq-col
    Data > Frequency table > key columns > freq-keys
''')
