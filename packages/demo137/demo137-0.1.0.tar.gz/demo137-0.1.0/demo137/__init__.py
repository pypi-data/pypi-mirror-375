# MIT License
#
# Copyright (c) 2025 Demo137
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# THE SOFTWARE.

def summarize_numbers(numbers):
    """
    Summarize a list of integers.

    Returns a dictionary with the following keys:
      - count: number of elements
      - total: sum of elements
      - min: minimum value or None if empty
      - max: maximum value or None if empty
      - average: arithmetic mean or None if empty

    This function is pure and has no side effects.
    """
    if not numbers:
        return {"count": 0, "total": 0, "min": None, "max": None, "average": None}
    total = sum(numbers)
    return {
        "count": len(numbers),
        "total": total,
        "min": min(numbers),
        "max": max(numbers),
        "average": total / len(numbers),
    }