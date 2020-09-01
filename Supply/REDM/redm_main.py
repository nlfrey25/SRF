import pandas
from tqdm import tqdm
import logging

from modeling.develop import develop
from modeling.data_augmentation import fill_in_price_data
from utils.interface import \
    load_parameters, empty_folder, save_to_file, get_args
import utils.config as config
import psycopg2

import sys
sys.path.append("../..")
from machine_settings import *

def run(mgra_dataframe):
    output_dir = config.parameters['output_directory']
    simulation_years = config.parameters['simulation_years']
    simulation_begin = config.parameters['simulation_begin']

    # the number of tqdm progress bar steps per simulation year
    checkpoints = 7
    progress = tqdm(desc='progress', total=simulation_years *
                    checkpoints, position=0)

    mgra_dataframe = fill_in_price_data(mgra_dataframe)
    save_to_file(mgra_dataframe, output_dir, 'preprocessed.csv')

    for i in range(simulation_years):
        forecast_year = simulation_begin + i + 1
        progress.set_description('starting year {}'.format(i+1))

        # develop enough land to meet demand for this year.
        mgra_dataframe, progress = develop(mgra_dataframe, progress)
        if mgra_dataframe is None:
            print('program terminated, {} years were completed'.format(i))
            return
        progress.update()

        progress.set_description('saving year {}'.format(i+1))
        save_to_file(mgra_dataframe, output_dir, 'year{}_{}.csv'.format(
            i + 1, forecast_year))
        progress.update()
    progress.close()
    return

def connect_to_aa():
        ## Set up database connection parameters
        parameters  = load_parameters("../../"+db_param_files)

        return psycopg2.connect(
        database=parameters['aa_database'],
        host=parameters['aa_host'],
        port=parameters['aa_port'],
        user=parameters['aa_user'],
        password=parameters['aa_password'])
        

if __name__ == "__main__":
    # load parameters
    args = get_args()
    if args.test:
        config.parameters = load_parameters('test_parameters.yaml')
    else:
        config.parameters = load_parameters('parameters.yaml')

    if config.parameters is not None:
        # prep output directory
        output_dir = config.parameters['output_directory']
        empty_folder(output_dir)
        save_to_file(config.parameters, output_dir, 'parameters.txt')
        # configure logging level
        if config.parameters['debug']:
            logging.basicConfig(level=logging.DEBUG)
        # load dataframe
        #mgra_dataframe = pandas.read_csv(config.parameters['input_filename'])
        conn = connect_to_aa()
        mysql = 'select * from {}.\"{}\"'.format(config.parameters['srf_schema'], config.parameters['srf_inputtbl'])
        mgra_dataframe = pandas.read_sql(mysql, conn)
        conn.close()
        run(mgra_dataframe)
    else:
        print('could not load parameters, exiting')