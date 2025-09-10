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

from chtoolbox import testing
import os

def test_generate_test_results():
    cases = {'case1': {'a': 1, 'b': 2}, 
             'case2': {'a': 3, 'b': 4},
             'case3': {'a': 5, 'b': 6}}
    
    def add(a, b):
        return a+b
    
    res = testing.generate_test_results(add, cases)

    for key, value in res.items():
        assert value['output'] == value['input']['a'] + value['input']['b'] 

def test_generate_test_results_csv():
    cases = os.path.join(os.path.dirname(__file__), 'data', 'data.csv')
    
    f1 = lambda a,b,c: a+b-c

    res1 = testing.generate_test_results(f1, cases)

    for key, value in res1.items():
        assert value['output'] == value['input']['a'] + value['input']['b'] - value['input']['c']

    def f2(a,b,c):
        x = {'sum': a+b,
             'diff': a-b}
        
        return x
    
    res2 = testing.generate_test_results(f2, cases)

    for key, value in res2.items():
        assert value['output']['sum'] == value['input']['a'] + value['input']['b']
        assert value['output']['diff'] == value['input']['a'] - value['input']['b']


