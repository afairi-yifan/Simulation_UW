import pandas as pd
import numpy as np
import config
from pandas import ExcelWriter
###########
# Constants
###########
LIFE_SPAN = 240
LOWER_BOUND_MONTH = -12

class Simulation:
    '''
    Input file contains two kinds of files, global data and distinct input data file.
    '''
    def __init__(self, input_path, list_cohort_name, cohort_start_date):
        self.current_month = 0
        self.input_path = input_path
        self.list_cohort_name = list_cohort_name
        self.cohort_start_date = cohort_start_date
        self.list_output_vars = []
        self.collection_cohort_data = {}
        self.group_cohort = []
        self.financial_report = pd.DataFrame()
        self.init_data()


    def init_data(self):
        dataloader = DataLoader(self.input_path, self.list_cohort_name)
        self.list_output_vars = dataloader.give_outputs_variables()[1]
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
        for numb in range(len(self.cohort_start_date)):
            if self.current_month == self.cohort_start_date[numb]:
                new_cohort = Cohort(self.collection_cohort_data[self.list_cohort_name[numb]], self.current_month, self.list_output_vars)
                new_cohort.update_one_month()
                self.group_cohort.append(new_cohort)
                assert len(new_cohort.output_financial_report().index) == len(self.group_cohort[0].output_financial_report().index), f'new cohort should have the same month.'
        self.run_all_cohort()
        self.current_month += 1

    def run_all_cohort(self):
        for cohort in self.group_cohort:
            cohort.update_one_month()

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
        for cohort in self.group_cohort:
            if fina_report.empty:
                fina_report = pd.concat([fina_report, cohort.output_financial_report()])
            else:
                fina_report = fina_report.add(cohort.output_financial_report())
        return fina_report

    def output_to_excel(self):
        output_file = self.output_full_report(False)
        output = output_file.transpose()
        with ExcelWriter(f'{config.save_path}') as writer:
            output.to_excel(writer, sheet_name='Simulation_output_format')

    def nice_print_report_format(self):
        print('Current simulation month is: ', self.current_month - 1)
        print('\n-----------')
        print('This financial report is \n')

class Cohort:
    def __init__(self, input_dataframe, now_month, list_output_vars):
        ## Paras
        self.start_month = now_month
        self.current_month = now_month
        self.financial_report = pd.DataFrame()
        self.input_data = input_dataframe
        self.list_output_vars = list_output_vars
        # TODO: update everything before the starting month
        self.init_canvas_before_start_month()
        # self.init_starting_month()
        ## special Para
        self.retention_yr = 0

    def init_canvas_before_start_month(self):
        self.financial_report = pd.DataFrame(index=range(LOWER_BOUND_MONTH, self.start_month), columns=self.input_data.columns)
        # take the cohort -- g1 as canvas and update data from there

    #TODO: update cohort for one month
    def update_one_month(self):
        current_row = self.input_data.copy()
        current_row.index = self.current_month
        ## Update starting premium let everything easy
        current_row['Start_premium_Input_var'] = current_row['Start_premium_Input_var'] / 12
        print(current_row)
        current_row = self.update_output_var(current_row)
        #TODO: update premium ratio

        #TODO: update monthly premium

        #TODO: update working monthly capital

        self.append_this_month_to_report()

    def update_output_var(self, row):
        for para in self.list_output_vars:
            if para == 'Transacted_premium_volume_Output_Profit_Loss' or 'Transacted_premium_volume_Output_Cash_flow':
                if (self.current_month - self.start_month) % 12 == 0 and self.current_month != self.start_month:
                    row['Start_premium_Input_var'] *= row['Inflation_Input_var']
                row['Transacted_premium_volume_Output_Profit_Loss'] = row['Start_premium_Input_var']
                row['Transacted_premium_volume_Output_Cash_flow'] = row['Start_premium_Input_var']
            elif para == 'ow_Origination_Output_Profit_Loss' or 'ow_Origination_Output_Cash_flow':
                ratio = row['Revenue_share_of_premium_for_new_business_Input_var']
                row['ow_Origination_Output_Profit_Loss'] = row['Transacted_premium_volume_Output_Profit_Loss'] * ratio
                row['ow_Origination_Output_Cash_flow'] = row['Transacted_premium_volume_Output_Profit_Loss'] * ratio
            elif para == ''
        return row

    def append_this_month_to_report(self):


    def update_financial_report(self):
        return None

    def output_financial_report(self):
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


