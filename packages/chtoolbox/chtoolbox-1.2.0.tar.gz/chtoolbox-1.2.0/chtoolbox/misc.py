"""MIT License

Copyright (c) 2025 Christian Hågenvik

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pandas as pd
from itertools import product

def clipboard_to_dict(print_dict=True):
    """
    Converts clipboard content to a dictionary.
    If print_dict is True, the dictionary is printed.
    This function reads the clipboard content into a pandas DataFrame and converts it to a dictionary.
    If the DataFrame has two columns, it converts it to a flat dictionary.
    If the DataFrame has more than two columns, it converts it to a nested dictionary with 'index' orientation.
    Returns:
        dict: A dictionary representation of the clipboard content.

    Example 1:

    >>> # Copy a range in excel containing thw following to the clipboard:
    idx	col_a	col_b	col_c
    row_a	1	4	7
    row_b	2	5	8
    row_c	3	6	9

    >>> clipboard_to_dict()
    {'row_a': {'col_a': 1, 'col_b': 4, 'col_c': 7},
     'row_b': {'col_a': 2, 'col_b': 5, 'col_c': 8},
     'row_c': {'col_a': 3, 'col_b': 6, 'col_c': 9}}
    
    Example 2:
    >>> # Copy a range in excel containing thw following to the clipboard:
    idx	col_a
    row_a	1
    row_b	2
    row_c	3

    >>> clipboard_to_dict()
    {'row_a': 1, 'row_b': 2, 'row_c': 3}
    """
    # Read the clipboard content into a DataFrame
    df = pd.read_clipboard(header=None)
    
    if df.shape[1] == 2:
        # Convert the DataFrame to a flat dictionary
        dictionary = dict(zip(df[0], df[1]))
    else:
        # Check if the first column header is empty
        if pd.isna(df.iloc[0, 0]):
            df.columns = ['idx'] + list(df.iloc[0, 1:])
            df = df[1:]
        else:
            df.columns = df.iloc[0]
            df = df[1:]
        
        # Set the first column as the index
        df.set_index(df.columns[0], inplace=True)
        
        # Convert the DataFrame to a nested dictionary with 'index' orientation
        dictionary = df.to_dict(orient='index')

    if print_dict:
        print(dictionary)

    return dictionary


def clipboard_to_list():
    """
    Retrieve data from the system clipboard and convert it to a list.
    This function reads the clipboard content into a pandas DataFrame, 
    converts the DataFrame values into a one-dimensional list, and returns the list.
    Returns:
        list: A list containing the clipboard data.
    """

    # Read clipboard data into a DataFrame
    df = pd.read_clipboard(header=None)

    # Convert DataFrame values to a one-dimensional list
    data_list = df.values.flatten().tolist()

    # Print the list
    return data_list

   
def compare_lists_from_clipboard():
    """
    A function used to select and copy a table from Excel. 
    The table is converted into lists (one list per column in the Excel range).
    Then it compares all the lists and finds the unique elements that are not present in all the lists.
    Useful for comparing large amounts of elements from Excel.
    Dictionary containing one list per column in clipboard (Excel range).
    """
    '''
    En funksjon som brukes ved å merke og kopiere en tabell fra excel. 
    Tabellen konverteres til lister (en liste per kolonne i excel rangen)
    Deretter så sammenligner den alle listene og finner de unike elementene som ikke finnes i alle listene
    
    Nyttig for å sammenligne store mengder med elementer fra excel

    Returns
    -------
    list_dict : dict
        Dictionary containing one list per column in clipboard (excel range).
    unique_items : list
        A list of items that are not present in all the lists.
    common_items : list
        A list of items that are present in all the lists.

    '''
    # Read clipboard data as a DataFrame and convert it to dictionary
    data = pd.read_clipboard(header=None)
    list_dict = {}
    for col in data.columns:
        col_values = data[col].tolist()
        col_values = [value for value in col_values if not pd.isna(value)]
        list_dict[col] = col_values

    # Find values not present in all lists
    common_items = set.intersection(*(set(values) for values in list_dict.values()))
    unique_items = []
    for values in list_dict.values():
        for value in values:
            if value not in common_items and value not in unique_items:
                unique_items.append(value)

    # Print the resulting dictionary
    return list_dict, unique_items, list(common_items)


def generate_combination_matrix(input_dict):
    """
    Generate a DataFrame containing all possible combinations of input parameters.
    This function takes a dictionary of input parameters, where the keys are parameter names
    and the values are lists of possible values for those parameters. It generates all possible
    combinations of the parameter values and returns them as a pandas DataFrame.
    Parameters
    ----------
    input_dict : dict
        A dictionary where keys are parameter names (str) and values are lists of possible
        values for those parameters. For example:
        {
            'pressure': [10, 20],
            'GVF': [10, 20, 30],
            'WLR': [40, 60, 80],
        }
    Returns
    -------
    pandas.DataFrame
        A DataFrame where each row represents a unique combination of the input parameter values.
        The columns correspond to the keys of the input dictionary.
    Examples
    --------
    >>> input_dict = {
    ...     'pressure': [10, 20],
    ...     'GVF': [10, 20, 30],
    ...     'WLR': [40, 60, 80],
    ... }
    >>> generate_combination_matrix(input_dict)
       pressure  GVF  WLR
    0        10   10   40
    1        10   10   60
    2        10   10   80
    3        10   20   40
    4        10   20   60
    5        10   20   80
    6        10   30   40
    7        10   30   60
    8        10   30   80
    9        20   10   40
    10       20   10   60
    11       20   10   80
    12       20   20   40
    13       20   20   60
    14       20   20   80
    15       20   30   40
    16       20   30   60
    17       20   30   80
    """


    # Generate all combinations using itertools.product
    combinations = product(*input_dict.values())
    
    # Create a DataFrame from the combinations
    df = pd.DataFrame(combinations, columns=input_dict.keys())
    
    return df


def filter_dictionary(input_dict: dict, filter: str | list[str]) -> dict:
    """
    Filters a dictionary to only include keys containing the filter string(s).

    Parameters
    ----------
    input_dict : dict
        The dictionary to filter.
    filter : str or list of str
        String or list of strings to match in the dictionary keys (case-insensitive).

    Returns
    -------
    dict
        A new dictionary containing only the keys that match the filter string(s).

    Examples
    --------
    >>> input_dict = {
    ...     'pressure': [10, 20],
    ...     'GVF': [10, 20, 30],
    ...     'WLR': [40, 60, 80],
    ...     'temp': [100, 200],
    ... }
    >>> filter_dictionary(input_dict, 'pres')
    {'pressure': [10, 20]}
    >>> filter_dictionary(input_dict, ['pres', 'WLR'])
    {'pressure': [10, 20], 'WLR': [40, 60, 80]}

    Notes
    -----
    - Filtering is case-insensitive.
    - If no keys match, an empty dictionary is returned.
    """
    if isinstance(filter, str):
        filter = [filter]
    
    filtered_dict = {key: value for key, value in input_dict.items() if any(f.lower() in key.lower() for f in filter)}
    
    return filtered_dict