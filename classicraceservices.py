import pandas as pd

def parse_url(url, start_row = 2, members = None):
    """
    Utility function for parsing a given URL of results, specific to
    the Classic Race Services web format. If provided, the list of
    members helps filter out non-members from the results list.

    Parameters
    ----------
    url : string
        The URL of the overall results page.

    start_row : int
        Starting row into the table of the results (default: 2).
    members :
        The list of ARR members to retain from the results.

    Returns
    -------
    results : list
        A list of tuples, where each tuple contains the name and overall place.
    """
    page = pd.read_html(url)[0]
    results = []
    skiprow = False
    for row in range(start_row, page.shape[0]):
        if skiprow:
            # This was set because of a "break" in the HTML table (see below).
            # There's a header which has to be skipped.
            skiprow = False
            continue

        item = page.iloc[row]
        if str(item[1]) == 'nan':
            # We encountered a break.
            skiprow = True
            continue

        # Build the tuple.
        to_add = (item[1], int(item[0]))
        if members is None or item[1].lower() in members:
            results.append(to_add)
    return sorted(results, key = lambda i: i[1])
