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
import itertools
import numpy as np

def generate_test_results(my_function, cases, print_cases=True):
    """
    Generates test results by applying a given function to a set of cases, returning both the input and output.
    The results dictionary is intended to use as input to tests in the `pytest` framework.
    
    Parameters
    ----------
    my_function : callable
        The function to be tested. It should accept keyword arguments.
    cases : dict or str
        A dictionary where keys are case names and values are dictionaries of parameters,
        or a string representing the path to a CSV file containing the cases.
        The CSV file should have the following format:
        Example:
        ```
        case,a,b,c
        case1,1,4,7
        case2,2,5,8
        case3,3,6,9
        ```

    print_cases : bool, optional
        If True, prints the results of each case. Default is True.
    Returns
    -------
    dict
        A dictionary containing the input parameters and the corresponding output for each case.
    Raises
    ------
    ValueError
        If `cases` is neither a dictionary nor a path to a CSV file.
        
    Examples
    --------
    >>> def add(a, b):
    ...     return {'sum': a + b}
    >>> cases = {
    ...     'case1': {'a': 1, 'b': 2},
    ...     'case2': {'a': 3, 'b': 4}
    ... }
    >>> generate_test_data(add, cases)
    {'case1': {'input': {'a': 1, 'b': 2}, 'output': {'sum': 3}},
     'case2': {'input': {'a': 3, 'b': 4}, 'output': {'sum': 7}}}
    """



    if type(cases) is str and cases[-4:] =='.csv':
        cases = pd.read_csv(cases, index_col=0)
        cases = cases.to_dict(orient='index')
    elif type(cases) is dict:
        pass
    else:
        raise ValueError('Cases must be a dictionary or a csv file')

    results = {key : {'input' : value} for key, value in cases.items()}

    for case_name, params in cases.items():
        result = my_function(**params)

        results[case_name]['output'] = {}

        if type(result) is dict:
            for key, val in result.items():
                results[case_name]['output'][key] = val
        else:
            results[case_name]['output'] = result

    if print_cases:
        # Print the results
        print('{')
        for case_name, params in results.items():
            print(f"'{case_name}': {params},")
        print('}')

    return results


def create_test_cases(inputs, print_cases=True):
    """
    Generate test cases from input parameters.
    Parameters
    ----------
    inputs : dict
        A dictionary where keys are parameter names and values are lists or numpy arrays of parameter values.
    print_cases : bool, optional
        If True, print the generated test cases. Default is True.
    Returns
    -------
    dict
        A dictionary where keys are case names (e.g., 'case1', 'case2', ...) and values are dictionaries of parameter combinations.
    Examples
    --------
    >>> inputs = {
    ...     'param1': [1, 2],
    ...     'param2': np.array([3, 4])
    ... }
    >>> create_test_cases(inputs)
    {
        'case1': {'param1': 1, 'param2': 3},
        'case2': {'param1': 1, 'param2': 4},
        'case3': {'param1': 2, 'param2': 3},
        'case4': {'param1': 2, 'param2': 4}
    }
    """

    keys = inputs.keys()
    values = [v.tolist() if isinstance(v, np.ndarray) else v for v in inputs.values()]
    combinations = list(itertools.product(*values))
    df = pd.DataFrame(combinations, columns=keys)
    df.index = [f'case{i}' for i in range(1, len(df) + 1)]

    cases = df.to_dict(orient='index')
    
    if print_cases:
        print('{')
        for case_name, params in cases.items():
            print(f"'{case_name}': {params},")
        print('}')
        
    return cases
