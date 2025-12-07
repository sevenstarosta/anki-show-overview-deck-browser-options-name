import re
from bs4 import BeautifulSoup

from aqt import gui_hooks, mw

############################################################################
############################### START CONFIG ###############################
############################################################################

DEFAULT_COLUMN = 100 # Large number - puts preset column last
DEFAULT_DISPLAY_COG = True
DEFAULT_PRESET_STYLING = "text-align: left; display: block; max-width: 300px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; cursor: pointer;"
DEFAULT_PRESET_HEADER_ALIGN = "left"
DEFAULT_PRESET_HEADER_STYLE = "text-align: left; padding: 4px 12px;"
DEFAULT_PRESET_HEADER_TITLE = "Preset"

# Configurable variables
column_number = DEFAULT_COLUMN
display_cog = DEFAULT_DISPLAY_COG
styling = DEFAULT_PRESET_STYLING
preset_header_align = DEFAULT_PRESET_HEADER_ALIGN
preset_header_style = DEFAULT_PRESET_HEADER_STYLE
preset_header_title = DEFAULT_PRESET_HEADER_TITLE

# Allow user config to specify max preset name display length, ordering of columns, and whether or not to display a cog
try:
    config: dict = mw.addonManager.getConfig(__name__)
    column_number = config.get("presetColumnNumber")
    display_cog = config.get("displayPresetCog")
    styling = config.get("presetStyle")
    preset_header_align = config.get("presetHeaderAlign")
    preset_header_style = config.get("presetHeaderStyle")
    preset_header_title = config.get("presetHeaderTitle")
except:
    pass

if not isinstance(column_number, int):
    # Put preset as the first column if not provided
    column_number = DEFAULT_COLUMN

if not isinstance(display_cog, bool):
    display_cog = DEFAULT_DISPLAY_COG

if not isinstance(styling, str):
    styling = DEFAULT_PRESET_STYLING

if not isinstance(preset_header_align, str):
    preset_header_align = DEFAULT_PRESET_HEADER_ALIGN

if not isinstance(preset_header_style, str):
    preset_header_style = DEFAULT_PRESET_HEADER_STYLE

if not isinstance(preset_header_title, str) or not preset_header_title:
    preset_header_title = DEFAULT_PRESET_HEADER_TITLE

############################################################################
################################ END CONFIG ################################
############################################################################

def replace_deck_node_options(deck_id: int, options_name: str, tree: str) -> str:
    """
    Function to search the overview screen's HTML for the options cog and replace it with a span with the options name.
    """
    # More flexible pattern that works after reordering
    pattern = re.compile(
        re.escape('onclick=\'return pycmd("opts:') + str(deck_id) +
        re.escape('");\'><img src=\'/_anki/imgs/gears.svg\' class=gears>')
    )
    # Insert options name, and include options cog image if display_cog is True
    replacement = f'onclick=\'return pycmd("opts:{deck_id}");\'><span style="{styling}">{"<img src=\'/_anki/imgs/gears.svg\' class=gears>" if display_cog else ""}{options_name}</span>'
    return re.sub(pattern, replacement, tree)


def reorder_table_columns(html_content: str) -> str:
    """
    Reorder table columns to put options column before deck column.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check for table rows directly since content.tree contains only <tr> elements
        table_rows = soup.find_all('tr')

        if table_rows:
            # Process header row (first row)
            if len(table_rows) > 0:
                header_row = table_rows[0]
                header_cells = header_row.find_all(['th', 'td'])

                if len(header_cells) >= 5:
                    # Move the last header cell (Options) to column_number
                    options_header = header_cells[-1]
                    options_header_copy = options_header.extract()

                    # Add title "Preset" to the options header with right alignment and padding
                    options_header_copy.string = preset_header_title
                    options_header_copy['align'] = preset_header_align
                    options_header_copy['style'] = preset_header_style

                    # TODO doesn't work past 4 because Due gets inserted later?
                    header_row.insert(column_number, options_header_copy)

            # Process data rows (skip header row)
            for row in table_rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])

                if len(cells) < 4:
                    continue

                # Move last cell to column_number
                options_cell = cells[-1]
                options_cell_copy = options_cell.extract()
                row.insert(column_number, options_cell_copy)

            return str(soup)

        # If no rows found, return original content
        return html_content

    except Exception as e:
        # If parsing fails, return original content
        return html_content


def replace_home_decks_options_buttons(browser, content) -> None:
    '''
    Grabs all decks from the browser's collection's deck manager,
    and adds their option names to the browser's content tree
    '''
    # First add options names to the original structure
    for deck in browser.mw.col.decks.all_names_and_ids():
        deck_id = deck.id
        deck_config = browser.mw.col.decks.config_dict_for_deck_id(deck_id) or {}

        # Check if it's a filtered deck
        if deck_config.get("dyn") == 1:
            # For filtered decks, get the search terms
            if (terms:= deck_config.get("terms", [])):
                options_name = f"Filtered: {terms[0][0]}"  # First term's search string
            else:
                options_name = "Filtered Deck"
        else:
            # For regular decks, get the options name
            options_name = deck_config.get("name") or "Missing Deck Preset"

        content.tree = replace_deck_node_options(
            deck_id=deck_id,
            options_name=options_name,
            tree=content.tree
        )

    # Then reorder the table columns
    content.tree = reorder_table_columns(content.tree)


# https://github.com/ankitects/anki/blob/main/qt/tools/genhooks_gui.py
gui_hooks.deck_browser_will_render_content.append(replace_home_decks_options_buttons)
