from numba import njit
from collections import namedtuple

ResultType = namedtuple("ResultType", ["sum", "product"])


@njit
def compute_values(a, b):
    sum_ab = a + b
    product_ab = a * b
    return ResultType(sum_ab, "aaa")


result = compute_values(3, 5)
print(result.sum, result.product)  # Access by name
