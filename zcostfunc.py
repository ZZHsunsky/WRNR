import math

def linear_increase(x):
    return 5 * x

def fast_slow_increase(x):
    return math.log(x+1)

def slow_fast_increase(x):
    return x**2

def sigmod_func(x):
    return 1000 / (1 + math.e ** (10 - x / 3))