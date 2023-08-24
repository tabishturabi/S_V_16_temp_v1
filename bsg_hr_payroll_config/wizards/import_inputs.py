# -*- coding: utf-8 -*-

import time
from datetime import datetime
import tempfile
import binascii
import xlrd
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models,fields,exceptions,api,_
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

import threading


class ImportInputs(models.TransientModel):
    _name = "import.inputs"
    _description = "Import Inputs"

    File_slect = fields.Binary(string="Select Excel File",required=True)
    import_option = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File')], string='Select', default='xls')
    other_input_id = fields.Many2one('hr.salary.rule', string='Other Inputs',required=True)
    batch_id = fields.Many2one('hr.payslip.run',string='Batch')


    
    def download_failed_log_file(self):
        data = {}
        return self.env.ref('bsg_hr_payroll_config.failed_logs_xlsx_id').report_action(self,data=data)




    
    def action_imoport_file(self):
        if self.import_option == 'csv':

            keys = ['employee_id', 'amount', 'description']

            try:
                csv_data = base64.b64decode(self.File_slect)
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
                values = dict(zip(keys,field))
                if values:
                    if i == 0:
                        continue
                    else:
                        values.update({
                            'employee_id': field[0],
                            'amount': field[1],
                            'description': field[2]
                        })
                        self.update_input_lines(values)
            net_total = sum(self.batch_id.slip_ids.mapped('total_net'))
            self.batch_id.batch_net_total = net_total
            bsg_type_id = self.env['hr.emp.doc.type'].search([('bsg_name','=',self.other_input_id.name)],limit=1)
            name='ملف متغيرات %s لشهر %s  '%(self.other_input_id.name,datetime.today().strftime("%m/%Y"))
            if bsg_type_id:
                attachment_vals = {
                    'name': name,
                    'datas': self.File_slect,
                    'store_fname': 'Import Input.csv',
                    'bsg_type':bsg_type_id.id,
                    'res_model': 'hr.payslip.run',
                    'res_id': self.batch_id.id,
                }
            else:
                bsg_type_create_id = self.env['hr.emp.doc.type'].create({
                    'bsg_name':self.other_input_id.name
                }).id
                attachment_vals = {
                    'name': name,
                    'datas': self.File_slect,
                    'store_fname': 'Import Input.csv',
                    'bsg_type': bsg_type_create_id,
                    'res_model': 'hr.payslip.run',
                    'res_id': self.batch_id.id,
                }




            attachement = self.env['ir.attachment'].create(attachment_vals)
            msg = _(
                """<div class="o_thread_message_content">
                    <p>Other Imported Inputs</p>
                    <ul class="o_mail_thread_message_tracking">
                    <li>Other Input : <span>{input}</span></li>
                    <li>File Name : <span>{name}</span></li>
                    <li>Other File Imported : <span>{attachement}</span></li>
                    </ul>
                    </div>
                    """.format(
                    input=self.other_input_id.name,
                    name=name,
                    attachement=attachement
                )
            )
            self.batch_id.message_post(body=msg)
            # ---------------------------------------
        elif self.import_option == 'xls':
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.File_slect))
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
                    self.update_input_lines(values)
            net_total = sum(self.batch_id.slip_ids.mapped('total_net'))
            self.batch_id.batch_net_total = net_total
            bsg_type_id = self.env['hr.emp.doc.type'].search([('bsg_name', '=', self.other_input_id.name)], limit=1)
            name = ' ملف متغيرات %s لشهر %s  ' % (self.other_input_id.name, datetime.today().strftime("%m/%Y"))
            if bsg_type_id:
                attachment_vals = {
                    'name': name,
                    'datas': self.File_slect,
                    'store_fname': 'Import Input.csv',
                    'bsg_type': bsg_type_id.id,
                    'res_model': 'hr.payslip.run',
                    'res_id': self.batch_id.id,
                }
            else:
                bsg_type_create_id = self.env['hr.emp.doc.type'].create({
                    'bsg_name': self.other_input_id.name
                }).id
                attachment_vals = {
                    'name': name,
                    'datas': self.File_slect,
                    'store_fname': 'Import Input.csv',
                    'bsg_type': bsg_type_create_id,
                    'res_model': 'hr.payslip.run',
                    'res_id': self.batch_id.id,
                }
            attachement=self.env['ir.attachment'].create(attachment_vals)
            msg = _(
                """<div class="o_thread_message_content">
                    <p>Other Imported Inputs</p>
                    <ul class="o_mail_thread_message_tracking">
                    <li>Other Input : <span>{input}</span></li>
                    <li>File Name : <span>{name}</span></li>
                    <li>Other File Imported : <span>{attachement}</span></li>
                    </ul>
                    </div>
                    """.format(
                    input=self.other_input_id.name,
                    name=name,
                    attachement=attachement
                )
            )
            self.batch_id.message_post(body=msg)
            # ------------------------------------------------------------
        else:
            raise Warning(_("Please select any one from xls or csv formate!"))

    def update_input_lines(self,values):
        updated_recs_list=[]
        if self.batch_id:
            slip_id = self.env['hr.payslip'].search([('payslip_run_id', '=',  self.batch_id.id), ('employee_id.driver_code', 'in', [values['employee_id'], values['employee_id'].upper()])], limit=1)
            if slip_id:
                input_line_ids = slip_id.input_line_ids.filtered(lambda inp:inp.code == self.other_input_id.code)
                for input_line_id in input_line_ids:
                    if input_line_id:
                        input_line_id.write({
                            'amount': float(values['amount']),
                            'description': values['description']
                        })
                        #slip_id.with_context({'no_batch_total_update': True}).compute_sheet()