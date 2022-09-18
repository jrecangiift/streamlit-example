from collections import namedtuple

import math
import pandas as pd


import draclient as dcl
from PIL import Image

clientsList = ['BDI','BRI','BJB','BNI']

months = [4,5,6,7,8]

cl = dcl.DRAClient()



for client in clientsList:
    for month in months:
        cl.buildUsageData(client, month,2022)


#cl.buildUsageData('BNI',6,2022)

cl.updateUsageAndAggregateExecutionStatus()

x = cl.df_usage
y = cl.df_aggregate

print(x)
print(y)