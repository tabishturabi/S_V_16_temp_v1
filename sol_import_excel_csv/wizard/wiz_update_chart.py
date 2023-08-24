# -*- coding: utf-8 -*-

import time
from datetime import datetime
import tempfile
import binascii
import xlrd
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
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

class UpdateChartAccount(models.TransientModel):
	_name = "update.chart.account"
	_description = "Update Chart Of Accounts"

	File_slect = fields.Binary(string="Select Excel File")
	import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')

	# @api.multi
	def imoport_file(self):

# -----------------------------
		if self.import_option == 'csv':

			keys = ['code', 'name', 'user_type_id']

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
				values = dict(zip(keys, field))
				if values:
					if i == 0:
						continue
					else:
						values.update({
										'code' : field[0],
										'parent_id' :field[9],

										})
						res = self.update_chart_accounts(values)

# ---------------------------------------
		elif self.import_option == 'xls':
			try:
				fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
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
					fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
				else:
					
					line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))

					values.update( {'code' : line[0],
									'parent_id' :line[9],								
									})
					res = self.update_chart_accounts(values)
# ------------------------------------------------------------						
		else:
			raise Warning(_("Please select any one from xls or csv formate!"))

		return res

	# @api.multi
	def update_chart_accounts(self,values):
		if values['parent_id']:
			parent_id_str = str(values['parent_id'])
			parent_id = parent_id_str.rstrip('0').rstrip('.') if '.' in parent_id_str else parent_id_str
			code_str = str(values['code'])
			code = code_str.rstrip('0').rstrip('.') if '.' in code_str else code_str
			print(self.env['account.account'].search([('code','=',parent_id)]))
			account_id  = self.env['account.account'].search([('code','=',code)])
			account_id.update({
				'parent_id' : self.env['account.account'].search([('code','=',parent_id)]).id
				})
		else:
			print('Parent id not found')
		