from odoo import models,fields,exceptions,api,_
from datetime import datetime
from odoo.exceptions import UserError,ValidationError,Warning
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import tempfile
import binascii
import xlrd

import logging

_logger = logging.getLogger(__name__)
import io

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class FailedLogs(models.AbstractModel):
    _name = 'report.bsg_hr_payroll_config.failed_logs_xlsx'
    _inherit ='report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook,lines,data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        main_heading = workbook.add_format({
            "bold": 0,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": 'white',
            'font_size': '10',
        })
        main_heading2 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#acadb2',
            'font_size': '12',
        })
        wb_sheet = workbook.add_worksheet('Failed Logs')
        wb_sheet.set_column('A2:A2',30)
        wb_sheet.set_column('B:M',15)
        row=1
        col=0
        failed_logs_dict = {}
        dict_key = 0
        logs_repeat_list = []
        if data.batch_id:
            if data.batch_id.slip_ids:
                for slip_id in data.batch_id.slip_ids:
                    if slip_id:
                        if slip_id.employee_id.driver_code:
                            if slip_id.employee_id.driver_code not in logs_repeat_list:
                                logs_repeat_list.append(slip_id.employee_id.driver_code)

        if data.import_option == 'csv':

            keys = ['employee_id', 'amount', 'description']

            try:
                csv_data = base64.b64decode(data.File_slect)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                values = {}
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)

            except:
                raise Warning(_("Invalid file!"))
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                # print('.......values.....', values)
                if values:
                    if i == 0:
                        continue
                    else:
                        values.update({
                            'employee_id': field[0],
                            'amount': field[1],
                            'description': field[2]
                        })
                        if values['employee_id'] not in logs_repeat_list and  values['employee_id'].upper() not in logs_repeat_list:
                            failed_logs_dict[dict_key] = {
                                'employee_id': values['employee_id'],
                                'amount': values['amount'],
                                'description': values['description']
                            }
                            dict_key += 1



            # ---------------------------------------
        elif data.import_option == 'xls':
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(data.File_slect))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)

            except:
                raise Warning(_("Invalid file!"))
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:

                    line = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                        row.value), sheet.row(row_no)))
                    values.update({
                        'employee_id': line[0],
                        'amount': line[1],
                        'description': line[2]
                    })
                    if values['employee_id'] not in logs_repeat_list and values['employee_id'].upper() not in logs_repeat_list:
                        failed_logs_dict[dict_key] = {
                            'employee_id': values['employee_id'],
                            'amount': values['amount'],
                            'description': values['description']
                        }
                        dict_key += 1

            # ------------------------------------------------------------
        else:
            raise Warning(_("Please select any one from xls or csv formate!"))
        if failed_logs_dict:
            wb_sheet.write(row,col,'Employee ID',main_heading2)
            wb_sheet.write(row,col+1,'Amount',main_heading2)
            wb_sheet.write(row,col+2,'Description',main_heading2)
            row+=1
            for key,value in failed_logs_dict.items():
                wb_sheet.write_string(row,col, value['employee_id'], main_heading)
                wb_sheet.write_string(row, col+1, value['amount'], main_heading)
                wb_sheet.write_string(row, col+2, value['description'], main_heading)
                row+=1






















































