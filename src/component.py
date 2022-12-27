'''
Template Component main class.

'''

import json
import logging
import os
import sys
from pathlib import Path
from typing import List

from kbc.env_handler import KBCEnvHandler
from kbc.result import ResultWriter, KBCTableDef, KBCResult

from bubbleio.client import Client

# global constants'
SYSTEM_COL_PREFIX = 'bubbleinternal'

# configuration variables
KEY_API_TOKEN = '#api_token'
KEY_ENDPOINTS = 'endpoints'
KEY_ENDPOINT_NAME = 'name'
KEY_ENDPOINT_PKEY = 'pkey'
KEY_ENPOINT_FIELDS = 'fields'
KEY_ENDPOINTS_INCREMENTAL = 'incremental'
KEY_FROM_DATE = 'period_from'
KEY_TO_DATE = 'period_to'

KEY_API_URL = 'api_url'

BUBBLE_DEFAULT_FIELDS = ["_id", "_type", "Creator", "Created Date", "Modified Date"]

# #### Keep for debug
KEY_DEBUG = 'debug'
MANDATORY_PARS = [KEY_ENDPOINTS, KEY_API_TOKEN, KEY_API_URL]

APP_VERSION = '0.0.1'


class Component(KBCEnvHandler):

    def __init__(self, debug=False):
        KBCEnvHandler.__init__(self, MANDATORY_PARS, log_level=logging.DEBUG if debug else logging.INFO)
        # override debug from config
        if self.cfg_params.get(KEY_DEBUG):
            debug = True
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        logging.info('Running version %s', APP_VERSION)
        logging.info('Loading configuration...')

        try:
            self.validate_config(MANDATORY_PARS)
            self.validate_endpoints(self.cfg_params[KEY_ENDPOINTS])
        except ValueError as e:
            logging.exception(e)
            exit(1)

        self.client = Client(self.cfg_params[KEY_API_URL], self.cfg_params[KEY_API_TOKEN])
        self.writers = self._setup_writers(self.cfg_params[KEY_ENDPOINTS])

    def run(self):
        '''
        Main execution code
        '''
        params = self.cfg_params  # noqa

        since_date = to_date = None
        if params.get(KEY_FROM_DATE):
            since_date, dm = self.get_date_period_converted(params[KEY_FROM_DATE], 'today')
        if params.get(KEY_TO_DATE):
            dm, to_date = self.get_date_period_converted('100 years ago', params[KEY_TO_DATE])

        for en in params[KEY_ENDPOINTS]:
            en_name = en[KEY_ENDPOINT_NAME]

            logging.info(f'Getting results from {en_name} endpoint')
            writer = self.writers[en_name]
            self.get_and_write_data(writer, en, since_date, to_date)
            # validation enforces unique endpoints
            writer.close()
            logging.info('Storing results..')
            results = writer.collect_results()
            self.fix_headers(results, SYSTEM_COL_PREFIX)
            self.create_manifests(results, headless=True, incremental=en[KEY_ENDPOINTS_INCREMENTAL])

        # remove empty folders for empty results
        self._remove_empty_folders()
        logging.info('Finished!')

    def _setup_writers(self, endpoints):
        writers = dict()
        for e in endpoints:
            e_name = e[KEY_ENDPOINT_NAME]
            try:
                fields = json.loads(f'[{e.get(KEY_ENPOINT_FIELDS, [])}]')
                fields = self._append_system_fields(fields)
            except Exception as e:
                raise ValueError(
                    f'The provided list of columns for field "{e_name}": {e[KEY_ENPOINT_FIELDS]} is invalid! '
                    f'Check if all values are enclosed in " quote characters and separated by comma.')

            table_def = KBCTableDef([SYSTEM_COL_PREFIX + '_id'], fields, e_name, '')
            folder_path = os.path.join(self.tables_out_path, e_name)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

            wr = ResultWriter(folder_path, table_def, fix_headers=True)
            writers[e_name] = wr

        return writers

    def get_and_write_data(self, writer, endpoint, since_date=None, to_date=None):
        results = 0
        for r in self.client.get_paged_result_pages(endpoint[KEY_ENDPOINT_NAME], since_date, to_date):
            results += len(r)
            writer.write_all(r, write_header=False)
        if results == 0:
            logging.warning(f"Endpoint {endpoint['name']} returned 0 results "
                            f"for the specified period {since_date} - {to_date}")

    def fix_headers(self, results, prefix):
        for r in results:
            new_cols = list()
            for c in r.table_def.columns:
                if c.startswith('_'):
                    c = prefix + c
                new_cols.append(c)
            r.table_def.columns = new_cols

    def create_manifests(self, results: List[KBCResult], headless=False, incremental=True):
        """
        Write manifest files for the results produced by kbc.results.ResultWriter
        :param results: List of result objects
        :param headless: Flag whether results contain sliced headless tables and hence
        the `.column` attribute should be
        used in manifest file.
        :param incremental:
        :return:
        """
        for r in results:
            if not headless:
                self.configuration.write_table_manifest(r.full_path, r.table_def.destination,
                                                        r.table_def.pk,
                                                        None, incremental, r.table_def.metadata,
                                                        r.table_def.column_metadata)
            else:
                path = Path(r.full_path)
                self.configuration.write_table_manifest(str(path.parent), r.table_def.destination,
                                                        r.table_def.pk,
                                                        r.table_def.columns, incremental,
                                                        r.table_def.metadata,
                                                        r.table_def.column_metadata)

    def _remove_empty_folders(self):
        folders = list(os.walk(self.tables_out_path))[1:]

        for folder in folders:
            # folder example: ('FOLDER/3', [], ['file'])
            if not folder[2]:
                os.rmdir(folder[0])

    def _append_system_fields(self, fields):

        fields.extend(BUBBLE_DEFAULT_FIELDS)
        # dedupe
        return list(dict.fromkeys(fields))

    def validate_endpoints(self, endpoints):
        errors = set()
        for e in endpoints:
            if not e.get(KEY_ENDPOINT_NAME):
                errors.add('Endpoint name cannot be empty!')
        if errors:
            raise ValueError(f'Endpoint config is invalid: {errors}')


"""
        Main entrypoint
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_arg = sys.argv[1]
    else:
        debug_arg = False
    try:
        comp = Component(debug_arg)
        comp.run()
    except Exception as ex:
        logging.exception(ex)
        exit(1)
