import re
from bs4 import BeautifulSoup

from aqt import gui_hooks


def replace_deck_node_options(deck_id: int, options_name: str, tree: str) -> str:
    """
    Function to search the overview screen's HTML for the options cog and replace it with a span with the options name.
    """
    # More flexible pattern that works after reordering
    pattern = re.compile(
        re.escape('onclick=\'return pycmd("opts:') + str(deck_id) +
        re.escape('");\'><img src=\'/_anki/imgs/gears.svg\' class=gears>')
    )
    # Replace with just the options name, right-aligned
    replacement = f'onclick=\'return pycmd("opts:{deck_id}");\'><span style="text-align: right; display: block;">{options_name}</span>'
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
                    # Move the last header cell (Options) to the first position
                    options_header = header_cells[-1]
                    options_header_copy = options_header.extract()

                    # Add title "Preset" to the options header with right alignment and padding
                    options_header_copy.string = "Preset"
                    options_header_copy['align'] = 'right'
                    options_header_copy['style'] = 'text-align: right; padding: 4px 12px;'

                    header_row.insert(0, options_header_copy)

            # Process data rows (skip header row)
            for row in table_rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])

                if len(cells) < 4:
                    continue

                # Move last cell to first position
                options_cell = cells[-1]
                options_cell_copy = options_cell.extract()
                row.insert(0, options_cell_copy)

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
            terms = deck_config.get("terms", [])
            if terms and len(terms) > 0:
                options_name = terms[0][0]  # First term's search string
            else:
                continue
        else:
            # For regular decks, get the options name
            options_name = deck_config.get("name")
            if not options_name:
                continue

        content.tree = replace_deck_node_options(
            deck_id=deck_id,
            options_name=options_name,
            tree=content.tree
        )

    # Then reorder the table columns
    content.tree = reorder_table_columns(content.tree)


# https://github.com/ankitects/anki/blob/main/qt/tools/genhooks_gui.py
gui_hooks.deck_browser_will_render_content.append(replace_home_decks_options_buttons)
