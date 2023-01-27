import unittest
import config
import pandas as pd
from Function import *

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_individual_cohort(self):
        input_group = ['G1']
        input_start_month = [0]
        simu = Simulation(config.data_pitch_path, input_group, input_start_month)
        simu.run_for_this_month()
        list_test_vars = simu.create_test_output_var()
        truth_pd = self.make_truth_label(list_test_vars)
        # truth_pd = pd.DataFrame()
        lt_test_dataframe = simu.output_test_start_month_cohort()
        for st_month in lt_test_dataframe:
            self.assertEqual(truth_pd.equals(lt_test_dataframe[st_month]),
                             f'The output at month {st_month} '
                             f'is not consistent with groundtruth. \n\n Output dataframe: {lt_test_dataframe[st_month]} \n\n Ground Truth: {truth_pd}')

    def test_pd(self):
        a = pd.DataFrame(1, index=['f', 'f'], columns=['t', 'g'])
        x = pd.DataFrame(2, index=['f', 'f'], columns=['t', 'g'])
        self.assertTrue(a.equals(x), f'some cells are not the same')


    def make_truth_label(self, var_para):
        truth = pd.read_excel(config.ground_truth_path, sheet_name='groundtruth', skiprows=1)
        truth.index = truth['Parameter']
        truth_label = truth.loc[var_para, 0]
        return truth_label



if __name__ == '__main__':
    # unittest.main()
    group = ['G1']
    date = [0]

