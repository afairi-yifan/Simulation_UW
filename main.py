import warnings
import os
import pandas as pd
from pandas import ExcelWriter
import config

from Function import *


if __name__ == '__main__':
    ### global data for generating results
    total_numb = 12 * 7 + 6
    long = range(total_numb)
    group = 6 * ['G23']
    for it in range(24, 31):
        title = 'G' + str(it)
        group += 12 * [title]
    input_data = group.copy()
    start_month = long
    simu = Simulation(config.data_pitch_path, input_data, start_month)
    simu.run_for_whole_time_span()
    print(simu.output_full_report())
    # simu.output_to_excel()
    # simu.output_numb_cohort_to_excel(0, config.test_path_1)
    simu.output_numb_cohort_to_excel(25, config.test_path_2)
    ##### Now test the retention ratio
    # input_data = ['G1']
    # start_month = [0]
    # input_data = 90 * ['G1']
    # start_month = range(90)
    # simu = Simulation(config.data_pitch_path, input_data, start_month)
    # # simu.run_for_whole_time_span()
    # for _ in range(120):
    #     simu.run_for_this_month()
    # # print(simu.output_full_report())
    # # print(simu.output_full_report())
    # simu.output_first_cohort_to_excel()
