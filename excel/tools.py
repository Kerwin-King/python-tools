from openpyxl.worksheet.worksheet import Worksheet

def unmerge_and_fill_cells(worksheet: Worksheet):
    all_merged_cells = list(worksheet.merged_cells.ranges)
    for merged_cell_range in all_merged_cells:
        merge_cell = merged_cell_range.start_cell
        worksheet.unmerge_cells(range_string=merged_cell_range.coord)
        for row_index, col_index in merged_cell_range.cells:
            cell = worksheet.cell(row=row_index, column=col_index)
            cell.value = merge_cell.value