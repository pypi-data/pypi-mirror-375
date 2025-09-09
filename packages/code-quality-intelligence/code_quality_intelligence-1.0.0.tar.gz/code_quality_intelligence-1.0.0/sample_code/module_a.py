import os
import sys


def add(a, b):
    total = 0
    for i in range(a):
        for j in range(b):
            if i == j:
                total += 1
    return total


def dangerous_eval(code):
    return eval(code)


try:
    x = 1 / 0
except:
    pass


