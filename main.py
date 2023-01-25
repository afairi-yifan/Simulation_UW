import warnings
import os
import pandas as pd
from pandas import ExcelWriter

import config
from Function import *


if __name__ == '__main__':
    # print('yes')
    input_data = ['G1', 'G2']
    start_month = [0, 1]
    simu = Simulation(config.data_path, input_data, start_month)
    simu.run_for_this_month()
    print(simu.output_full_report())
    simu.output_to_excel()
