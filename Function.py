import pandas as pd
import numpy as np
import config
from pandas import ExcelWriter
import copy
###########
# Constants
###########
LIFE_SPAN = 240
LOWER_BOUND_MONTH = -12
ONE_YR = 12

class Simulation:
    '''
    Input file contains two kinds of files, global data and distinct input data file.
    '''
    def __init__(self, input_path, list_cohort_name, cohort_start_date):
        self.create_new_test = None
        self.current_month = 0
        self.input_path = input_path
        self.list_cohort_name = list_cohort_name
        self.cohort_start_date = cohort_start_date
        self.list_output_vars = []
        self.collection_cohort_data = {}
        self.group_cohort = {}
        self.financial_report = pd.DataFrame()
        self.init_data()
        self.test_output_var = self.create_test_output_var()
        ## test dataframe case
        self.test_cohort_df = {}


    def init_data(self):
        dataloader = DataLoader(self.input_path, self.list_cohort_name)
        self.list_output_vars = dataloader.give_outputs_variables()[1]
        # print(self.list_output_vars)
        list_data = dataloader.extract_data_from_list()
        self.collection_cohort_data = dict(zip(self.list_cohort_name, list_data))


    ###########
    # Conditions to run for this month
    ###########
    def run_for_this_month(self):
        '''
        Check for new cohort: for current month == cohort start month, then init new cohort --> cohort class init
        Run all cohort: aggregate all cohort reports.
        increase one month
        :return:
        '''
        assert len(self.cohort_start_date) == len(self.list_cohort_name), f'Cohort name and start date input are not the same.'
        self.create_new_test = False
        for numb in range(len(self.cohort_start_date)):
            if self.current_month == self.cohort_start_date[numb]:
                new_cohort = Cohort(self.collection_cohort_data[self.list_cohort_name[numb]], self.current_month, self.list_output_vars)
                self.group_cohort[self.current_month] = new_cohort
                self.create_new_test = True
                assert len(new_cohort.output_financial_report().index) == len(self.group_cohort[0].output_financial_report().index), f'new cohort should have the same month.'
        self.run_all_cohort()
        # self.create_test_dataframe_start_month(self.create_new_test)
        self.current_month += 1

    def run_all_cohort(self):
        for month in self.group_cohort:
            self.group_cohort[month].update_one_month()

    def run_for_whole_time_span(self):
        for _ in range(LIFE_SPAN):
            self.run_for_this_month()

    ###########
    # Output Results
    ###########
    def output_full_report(self, nice=True):
        if nice:
            self.nice_print_report_format()
        fina_report = pd.DataFrame()
        for month in self.group_cohort:
            if fina_report.empty:
                fina_report = pd.concat([fina_report, self.group_cohort[month].output_financial_report()])
            else:
                fina_report = fina_report.add(self.group_cohort[month].output_financial_report())
                self.assert_addition_reports()
        return fina_report

    def update_full_report(self):
        self.financial_report = self.output_full_report()

    def output_to_excel(self):
        output_file = self.output_full_report(False)
        output = output_file.transpose()
        with ExcelWriter(f'{config.save_path}') as writer:
            output.to_excel(writer, sheet_name='Simulation_output_test')

    def nice_print_report_format(self):
        print('Current simulation month is: ', self.current_month - 1)
        print('\n-----------')
        print('This financial report is \n')

    ###########
    # Test Output Results
    ###########
    #TODO: Store a tested array and setup output dataframe array to be tested
    def create_test_output_var(self):
        var_list = []
        var_list = self.list_output_vars.copy()
        print(var_list)
        var_list.pop(-1)
        var_list.pop(-1)
        assert len(var_list) == 38, f'The number of the list is not correct'
        assert var_list[-1] == 'Operating_cash_flow_Output_Cash_flow', f'Output var list is not correct.'
        return var_list

    def create_test_dataframe_start_month(self, create_new_test):
        if create_new_test:
            test_cohort = self.group_cohort[-1]
            pd = test_cohort.output_financial_report()
            test_pd = pd.loc[self.current_month, self.test_output_var]
            self.test_cohort_df[self.current_month] = test_pd.copy()
            self.create_new_test = False
        else:
            pass

    def output_test_start_month_cohort(self):
        return self.test_cohort_df.copy()

    # TODO: test the addition array when those array merges.
    def assert_addition_reports(self):
        return None
        # Random index or columns variables and test them
        # assert
        # assert




class Cohort:
    def __init__(self, input_dataframe, now_month, list_output_vars):
        ## Paras
        self.start_month = now_month
        self.current_month = now_month
        self.financial_report = pd.DataFrame()
        self.input_data = input_dataframe
        self.list_output_vars = list_output_vars
        self.init_canvas_before_start_month()
        # self.init_starting_month()
        ## special Para
        self.retention_yr = 1

    def init_canvas_before_start_month(self):
        self.financial_report = pd.DataFrame(0, index=range(LOWER_BOUND_MONTH, self.start_month), columns=self.input_data.columns)
        # take the cohort -- g1 as canvas and update data from there

    def update_one_month(self):
        self.inflate_premium()
        temp = self.input_data.copy()
        temp.index = [self.current_month]
        current_row = temp.loc[self.current_month].copy()
        current_row['Month_Input_var'] = self.current_month
        ## Update starting premium let everything easy
        wc_timeline = self.current_month - ONE_YR
        current_row = self.update_output_var(current_row, wc_timeline)
        self.append_this_month_to_report(current_row)
        self.current_month += 1
        #TODO: update the retention at the end of the fucking test
        # self.consider_retention()

    def consider_retention(self):
        #TODO: update the retention at the end of the fucking program
        assert len(self.input_data.index) == 1, f'Buggy'
        if self.current_month - self.start_month < ONE_YR:
            self.input_data.loc['Value', 'Start_avg_premium_Input_var'] *= self.input_data.loc[
                'Value', 'Inflation_Input_var']
        else:
            self.input_data.loc['Value', 'Start_avg_premium_Input_var'] *= self.input_data.loc['Value', 'Inflation_Input_var']


    def inflate_premium(self):
        assert len(self.input_data.index) == 1, f'Buggy'
        if (self.current_month - self.start_month) % ONE_YR == 0 and self.current_month != self.start_month:
            self.input_data.loc['Value', 'Start_avg_premium_Input_var'] *= self.input_data.loc['Value', 'Inflation_Input_var']

    def update_output_var(self, row, timeline):
        #TODO: new input variables as number of customers.
        work_cap_timeline = timeline
        for para in self.list_output_vars:
            # print(row[para])
            if para == 'Transacted_premium_volume_Output_Profit_Loss' or para == 'Transacted_premium_volume_Output_Cash_flow':
                row[para] = row['Start_avg_premium_Input_var'] * row['Start_Customer_Input_var']
            elif para == 'ow_Origination_Output_Profit_Loss' or para == 'ow_Origination_Output_Cash_flow':
                ratio = self.get_first_or_second_yr_ratio(row['Revenue_share_of_premium_for_new_business_Input_var'], row['Revenue_share_of_premium_for_renewal_Input_var'])
                row[para] = row['Transacted_premium_volume_Output_Profit_Loss'] * ratio
                row['Network_Output_Profit_Loss'] = row[para]
                row['Network_Output_Cash_flow'] = row[para]
            elif para == 'ow_Underwriting_engine_Output_Profit_Loss' or para == 'ow_Underwriting_engine_Output_Cash_flow':
                ratio = self.get_first_or_second_yr_ratio(0, row['Underwriting_Relative_to_premium_based_on_improvement_first_yr_Input_var'])
                row[para] = row['Transacted_premium_volume_Output_Profit_Loss'] * ratio
            elif para == 'ow_Back_office_app_Output_Profit_Loss' or para == 'ow_Back_office_app_Output_Cash_flow':
                ratio = self.get_first_or_second_yr_ratio(0, row['Backoffice_Relative_to_premium_based_on_improvement_first_year_Input_var'])
                row[para] = row['Transacted_premium_volume_Output_Profit_Loss'] * ratio
            elif para == 'Platform_Output_Profit_Loss':
                assert not np.isnan(row['ow_Back_office_app_Output_Profit_Loss']), f'back office not exist first.'
                assert not np.isnan(row['ow_Underwriting_engine_Output_Profit_Loss']), f'uw engine not exist first.'
                row[para] = row['ow_Back_office_app_Output_Profit_Loss'] + row['ow_Underwriting_engine_Output_Profit_Loss']
            elif para == 'Platform_Output_Cash_flow':
                row[para] = row['Platform_Output_Profit_Loss']
            elif para == 'Revenue_Output_Profit_Loss':
                row[para] = row['Platform_Output_Profit_Loss'] + row['Network_Output_Profit_Loss']
            elif para == 'Revenue_Output_Cash_flow':
                row[para] = row['Platform_Output_Cash_flow'] + row['Network_Output_Cash_flow']
            elif para == 'ow_Loss_Output_Profit_Loss' or para == 'ow_Loss_Output_Cash_flow':
                row[para] = 0
            elif para == 'ow_Distribution_channel_Output_Profit_Loss':
                ratio = self.get_first_or_second_yr_ratio(row['Distribution_channel_cost_as_share_of_premium_first_year_Input_var'], row['Distribution_channel_cost_as_share_of_premium_next_year_Input_var'])
                row[para] = ratio * row['Transacted_premium_volume_Output_Profit_Loss']
            elif para == 'ow_Distribution_channel_Output_Cash_flow':
                assert not np.isnan(row['ow_Distribution_channel_Output_Profit_Loss']), f'Profit loss distribution first.'
                ratio = 1 - row['Working_capital_ratio_Distribution_channel_Input_var']
                row[para] = ratio * row['ow_Distribution_channel_Output_Profit_Loss']
            elif para == 'ow_expenses_Output_Profit_Loss':
                ratio = self.get_first_or_second_yr_ratio(row['MGA_expense_ratio_as_share_of_premium_volume_first_year_Input_var'], row['MGA_expense_ratio_as_share_of_premium_volume_next_year_Input_var'])
                row[para] = row['Transacted_premium_volume_Output_Profit_Loss'] * ratio
            elif para == 'ow_expenses_Output_Cash_flow':
                assert not np.isnan(row['ow_expenses_Output_Profit_Loss']), f'To get profit&loss expense first.'
                ratio = 1 - row['Working_capital_ratio_Expenses_Input_var']
                row[para] = row['ow_expenses_Output_Profit_Loss'] * ratio
            elif para == 'ow_outsourcing_Output_Profit_Loss' or para == 'ow_outsourcing_Output_Cash_flow':
                ratio = self.get_first_or_second_yr_ratio(row['MGA_outsourcing_cost_ratio_as_share_of_premium_volume_first_year_Input_var'], row['MGA_outsourcing_cost_ratio_as_share_of_premium_volume_next_year_Input_var'])
                row[para] = ratio * row['Transacted_premium_volume_Output_Profit_Loss']
            elif para == 'Costs_Output_Profit_Loss':
                sum = row['ow_Loss_Output_Profit_Loss'] + row['ow_Distribution_channel_Output_Profit_Loss']
                row[para] = sum + row['ow_expenses_Output_Profit_Loss'] + row['ow_outsourcing_Output_Profit_Loss']
            elif para == 'Costs_Output_Cash_flow':
                sum = row['ow_Loss_Output_Cash_flow'] + row['ow_Distribution_channel_Output_Cash_flow']
                row[para] = sum + row['ow_expenses_Output_Cash_flow'] + row['ow_outsourcing_Output_Cash_flow']
            elif para == 'Net_income_Output_Profit_Loss':
                row[para] = row['Revenue_Output_Profit_Loss'] - row['Costs_Output_Profit_Loss']
            elif para == 'Net_income_Output_Cash_flow':
                row[para] = row['Revenue_Output_Cash_flow'] - row['Costs_Output_Cash_flow']
            elif para == 'Taxes_Output_Profit_Loss':
                row[para] = row['Taxes_as_share_of_net_income_Input_var'] * row['Net_income_Output_Profit_Loss']
            elif para == 'Taxes_Output_Cash_flow':
                row[para] = row['Taxes_Output_Profit_Loss']
            elif para == 'NOPAT_Output_Profit_Loss':
                row['NOPAT_Output_Profit_Loss'] = row['Net_income_Output_Profit_Loss'] - row['Taxes_Output_Profit_Loss']
            elif para == 'NOPAT_Output_Cash_flow':
                if self.current_month == self.start_month:
                    self.financial_report.loc[:self.start_month - 1, 'NOPAT_Output_Cash_flow'] = 0
                row['NOPAT_Output_Cash_flow'] = row['Net_income_Output_Cash_flow'] - row['Taxes_Output_Cash_flow']
            elif para == 'Accumulated_Output_Profit_Loss':
                last_accumulate = 0
                if self.current_month > self.start_month:
                    last_accumulate = self.financial_report.loc[:(self.current_month - 1), 'NOPAT_Output_Profit_Loss'].sum()
                row[para] = last_accumulate + row['NOPAT_Output_Profit_Loss']
            elif para == 'Loss_Output_Profit_Loss_Carrier':
                row[para] = row['Transacted_premium_volume_Output_Profit_Loss'] * row['Carrier_loss_on_premium_Input_var']
            elif para == 'Working_capital_ow_Loss_Output_Cash_flow':
                row[para] = 0
                self.financial_report.loc[work_cap_timeline, para] = row['Costs_Output_Profit_Loss'] * row['Working_capital_ratio_carrier_loss_Input_var']
            elif para == 'Working_capital_ow_Distribution_channel_Output_Cash_flow':
                if self.current_month < self.start_month + ONE_YR:
                    self.financial_report.loc[work_cap_timeline, para] = row['ow_Distribution_channel_Output_Profit_Loss'] * row['Working_capital_ratio_Distribution_channel_Input_var']
                row[para] = 0
            elif para == 'Working_capital_ow_expenses_Output_Cash_flow':
                self.financial_report.loc[work_cap_timeline, para] = row['ow_expenses_Output_Profit_Loss'] * row['Working_capital_ratio_Expenses_Input_var']
                row[para] = 0
            elif para == 'Working_capital_Output_Cash_flow':
                wc1 = 'Working_capital_ow_Loss_Output_Cash_flow'
                wc2 = 'Working_capital_ow_Distribution_channel_Output_Cash_flow'
                wc3 = 'Working_capital_ow_expenses_Output_Cash_flow'
                row[para] = row[wc1] + row[wc2] + row[wc3]
                self.financial_report.loc[work_cap_timeline, para] = self.financial_report.loc[work_cap_timeline, wc1] + self.financial_report.loc[work_cap_timeline, wc2] + self.financial_report.loc[work_cap_timeline, wc3]
            elif para == 'Operating_cash_flow_Output_Cash_flow':
                nopat = 'NOPAT_Output_Cash_flow'
                wc = 'Working_capital_Output_Cash_flow'
                self.financial_report.loc[work_cap_timeline, para] = self.financial_report.loc[work_cap_timeline, nopat] - self.financial_report.loc[work_cap_timeline, wc]
                row[para] = row['NOPAT_Output_Cash_flow'] - row['Working_capital_Output_Cash_flow']
                print(self.financial_report.loc[work_cap_timeline, nopat], self.financial_report.loc[work_cap_timeline, wc])
            elif para == 'Number_of_Customer_Output_Cash_flow':
                row[para] = row['Start_Customer_Input_var']
            elif para == 'Accumulated_Output_Cash_flow':
                ##TODO: make accumulated and ROIC correct after the pitch deck.
                op = 'Operating_cash_flow_Output_Cash_flow'
                self.financial_report.loc[work_cap_timeline, para] = self.financial_report.loc[:work_cap_timeline, op].sum()
                # print('The value of operating cash is :', self.financial_report.loc[work_cap_timeline, 'Operating_cash_flow_Output_Cash_flow'])
                row[para] = self.financial_report.loc[:self.current_month - 1, op].sum() + row[op]
            elif para == 'ROIC_Output_Cash_flow':
                ac = 'Accumulated_Output_Cash_flow'
                row[para] = row[ac] / abs(self.financial_report.loc[work_cap_timeline, ac])
        return row

    def get_first_or_second_yr_ratio(self, ratio1, ratio2):
        ratio = 0
        if self.current_month - self.start_month < ONE_YR:
            ratio = ratio1
        else:
            ratio = ratio2
        return ratio

    def append_this_month_to_report(self, row):
        row_to_concat = pd.DataFrame(row).transpose()
        self.financial_report = pd.concat([self.financial_report, row_to_concat], axis=0)
        # print(self.financial_report.copy())

    def update_financial_report(self):
        return None

    def output_financial_report(self):
        # print(self.financial_report)
        return self.financial_report.copy()


class DataLoader:
    '''
    To create list of output variables and list of dataframes.
    '''
    def __init__(self, filepath, list_sheet_name):
        self.filepath = filepath
        self.list_sheet_name = self.create_sheet_name(list_sheet_name)

    def create_sheet_name(self, list_name):
        lt = []
        for name in list_name:
            lt.append(f'Cohort {name}')
        return lt

    def extract_data_from_list(self):
        lt_data = []
        for name in self.list_sheet_name:
            df = pd.read_excel(self.filepath, sheet_name=name, skiprows=1)
            improved_df = self.createDataFrameworkSuffix(df)
            outputs = self.give_outputs_variables()[0]
            df_new = self.creat_custom_dataframe(improved_df, outputs)
            lt_data.append(df_new)
        return lt_data

    def createDataFrameworkSuffix(self, df):
        df['Parameter'] = df['Parameter'] + '_' + df['Input/Output'] + '_' + df['Category']
        return df

    def give_outputs_variables(self):
        data = pd.read_excel(self.filepath, sheet_name=self.list_sheet_name[0], skiprows=1)
        df = self.createDataFrameworkSuffix(data)
        outputs = list(df.loc[df['Input/Output'] == 'Output', 'Parameter'])
        inputs = list(df.loc[df['Input/Output'] == 'Input', 'Parameter'])
        var = inputs + outputs
        list_var = [var, outputs]
        return list_var

    def creat_custom_dataframe(self, dataframe, outputs):
        index_names = dataframe['Parameter']
        dataframe = dataframe.filter(like="Value", axis=1)
        dataframe.index = index_names
        df_data = dataframe.loc[outputs]
        df_input = df_data.transpose()
        return df_input