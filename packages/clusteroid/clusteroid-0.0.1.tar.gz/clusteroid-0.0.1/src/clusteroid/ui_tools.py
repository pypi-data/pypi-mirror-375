
from textual.widgets import DataTable

def table_save_pos(table: DataTable):
    save = dict()
    save["selected_row"] = table.cursor_row
    save["selected_col"] = table.cursor_column
    save["scroll_x"], save["scroll_y"] = table.scroll_offset
    return save
    
def table_load_pos(table: DataTable, saved: dict):
    if saved["selected_row"] is not None and saved["selected_row"] < table.row_count:
        if saved["selected_col"] is not None and saved["selected_col"] < len(table.ordered_columns):
            table.cursor_coordinate = (saved["selected_row"], saved["selected_col"])
    table.scroll_to(saved["scroll_x"], saved["scroll_y"], animate=False)

