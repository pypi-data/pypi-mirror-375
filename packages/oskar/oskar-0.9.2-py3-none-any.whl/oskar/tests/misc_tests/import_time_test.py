#!/usr/bin/env python
# python -X importtime import_time_test.py

from time import time
t = time()
import numpy as np
print(time()-t); t = time()

import pygimli as pg
print(time()-t); t = time()

import oskar as osk
print(time()-t); t = time()


print(pg.__version__)