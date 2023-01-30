import unittest
import config
import pandas as pd
from Function import *

class MyTestCase(unittest.TestCase):
    def test_individual_cohort(self):
        input_group = ['G1', 'G1', 'G1']
        input_start_month = [0, 1, 3]
        simu = Simulation(config.data_pitch_path, input_group, input_start_month)
        for _ in range(20):
            simu.run_for_this_month()
        simu.create_test_start_month_dataframe()
        list_test_vars = simu.return_test_output_var()
        truth_pd = self.make_truth_label(list_test_vars)
        # truth_pd = pd.DataFrame()
        lt_test_dataframe = simu.output_test_start_month_cohort()
        truth_round = truth_pd.round(2)
        for st_month in lt_test_dataframe:
            test_df = lt_test_dataframe[st_month].copy()
            test_df = test_df.round(2)
            lgth = len(test_df)
            self.assertTrue(len(truth_round.index) == lgth, f'The ground truth index is {len(truth_round.index)} and the test one is {lgth}')
            self.assertTrue(truth_round.equals(test_df),
                             f'The output at month {st_month} '
                             f'is not consistent with groundtruth. \n\n Output dataframe: {test_df} \n\n Ground Truth: {truth_round}')

    # def test_pd(self):
    #     a = pd.DataFrame(1, index=['f', 'f'], columns=['t', 'g'])
    #     x = pd.DataFrame(1, index=['f', 'f'], columns=['t', 'g'])
    #     self.assertTrue(a.equals(x), f'some cells are not the same')


    def make_truth_label(self, var_para):
        truth = pd.read_excel(config.ground_truth_path, sheet_name='groundtruth', skiprows=1)
        truth.index = truth['Parameter']
        truth_label = truth.loc[var_para, 0]
        return truth_label



if __name__ == '__main__':
    # unittest.main()
    group = ['G1']
    date = [0]

