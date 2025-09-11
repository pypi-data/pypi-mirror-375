# `less-than-key`

Custom ordering for sorting and data structures, using your own less-than (`<`) function.

## What is it?

`less-than-key` lets you define a "key function" for sorting **using any custom less-than (`<`) function you like**.
It's useful anytime you want to sort or prioritize objects using arbitrary comparison logic, such as by descending
order, absolute value, length, or anything else.

## C++-Style Comparator Pattern, in Python

If you come from C++ (e.g., `std::sort` or `std::priority_queue`), you're used to passing a function (or functor) of the
form `bool operator()(const T& a, const T& b)`, which encodes your custom `<` logic. `less-than-key` explicitly brings
the C++-style comparator pattern to Python:

```
def cpp_style_lt(a, b):
    return <your-strict-weak-ordering-here>

sorted(seq, key=less_than_to_key(cpp_style_lt))     # Just like std::sort(..., cmp)
```

Like C++, you can encapsulate arbitrary ordering logic, and use it seamlessly in sorting, `heapq`, etc. - with zero
boilerplate.

## Install

```bash
pip install less-than-key
```

## Usage

```python
# coding=utf-8
from less_than_key import less_than_to_key


# Sort numbers by their absolute value, in reverse order (largest abs first)
def abs_gt(a, b):
    return abs(a) > abs(b)


lst = [-3, 7, -1, 2]
assert sorted(lst, key=less_than_to_key(abs_gt)) == [7, -3, 2, -1]


# Sort strings by length, then alphabetically
def len_then_alpha(a, b):
    if len(a) != len(b):
        return len(a) < len(b)
    return a < b


words = ['pear', 'fig', 'apple', 'date']
assert sorted(words, key=less_than_to_key(len_then_alpha)) == ['fig', 'date', 'pear', 'apple']

# Use with `heapq` for custom priority
# Use max-heap semantics
import heapq
import operator

MaxHeapLessThanKey = less_than_to_key(operator.gt)

assert MaxHeapLessThanKey(1) > MaxHeapLessThanKey(2)
assert MaxHeapLessThanKey(1) >= MaxHeapLessThanKey(2)

assert MaxHeapLessThanKey(1) < MaxHeapLessThanKey(0)
assert MaxHeapLessThanKey(1) <= MaxHeapLessThanKey(0)

assert MaxHeapLessThanKey(1) == MaxHeapLessThanKey(1)
assert MaxHeapLessThanKey(1) >= MaxHeapLessThanKey(1)
assert MaxHeapLessThanKey(1) <= MaxHeapLessThanKey(1)

assert MaxHeapLessThanKey(1) != MaxHeapLessThanKey(2)

heap = [MaxHeapLessThanKey(x) for x in [5, 3, 7]]
heapq.heapify(heap)
assert heapq.heappop(heap).value == 7
```

## API

### `less_than_to_key(less_than)`

Returns a function suitable for sorting's `key=...` parameter, wrapping values in a class that uses your custom
less-than function for all comparisons.

- **Parameters:**
    - `less_than`: `callable(a, b) -> bool`  
      Your less-than function (must provide a strict ordering, i.e., return True if a < b).
- **Returns:**  
  `function` - key function, e.g. `key=less_than_to_key(my_lt)`
- **Example:**  
  `sorted(items, key=less_than_to_key(my_lt))`

### Advanced: `LessThanKey`

You can generate specialized classes if you want to use them directly or in custom data structures:

```python
# coding=utf-8
from less_than_key import LessThanKey

AbsGreaterThanLessThanKey = LessThanKey[lambda a, b: abs(a) > abs(b)]
assert AbsGreaterThanLessThanKey(-10) < AbsGreaterThanLessThanKey(5)
```

## Why not just use `functools.cmp_to_key`?

- `functools.cmp_to_key` (in Python 3) is built for *three-way* comparison (`-1, 0, 1`) functions, but sometimes you
  want to provide only a strict less-than function.
- This package is more direct and may be easier when you already have a "less-than" function, or want tight control (
  e.g., when using with specialized containers).

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).