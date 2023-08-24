# -*- coding: utf-8 -*-

import time
import tempfile
import binascii
import xlrd
from datetime import date, datetime,timedelta
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
from odoo.tools.mimetypes import guess_mimetype
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


import logging
import threading

class ImportOvertimeLines(models.TransientModel):
	_name = "import.overtime.lines"
	_description = "Import Overtime Lines"

	File_slect = fields.Binary(string="Select Excel File")
	import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
	overtime_hour_id = fields.Many2one('hr.employee.overtime.by.hours',string='Overtime',)

	#@api.multi
	def imoport_file(self):
		# guess mimetype from file content
		
		mimetype = guess_mimetype(base64.b64decode(self.File_slect))
		self.action_lin_therad()
		
	def action_lin_therad(self):
		threaded_calculation = threading.Thread(target=self._imoport_file, args=())
		threaded_calculation.start()
		return {'type': 'ir.actions.act_window_close'}
	
	#@api.multi
	def _imoport_file(self):
		with api.Environment.manage():
			# As this function is in a new thread, I need to open a new cursor, because the old one may be closed
			new_cr = self.pool.cursor()
			self = self.with_env(self.env(cr=new_cr))
			# -----------------------------
			if self.import_option == 'csv':
	
				keys = ['employee', 'description', 'hours']
	
				try:
					csv_data = base64.b64decode(self.File_slect)
					data_file = io.StringIO(csv_data.decode("utf-8"))
					data_file.seek(0)
					file_reader = []
					values = {}
					csv_reader = csv.reader(data_file, delimiter=',')
					file_reader.extend(csv_reader)
	
				except:
					
					raise UserError(_("Invalid file!"))
	
				for i in range(len(file_reader)):
					field = list(map(str, file_reader[i]))
					values = dict(zip(keys, field))
					if values:
						if i == 0:
							continue
						else:
							values.update({
											'employee_id':field[1],
											'description' : field[2],
											'overtime' : field[3],
											})
							
							res = self.create_overtime_lines(values)
				
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
				count = 0
				for row_no in range(sheet.nrows):
					val = {}
					if row_no <= 0:
						fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
					else:
						line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
						print("$$$$$$$$$$",line)
						values.update( {
											'employee_id':line[0],
											'description' : line[1],
											'overtime' : line[2],
										})
						res = self.create_overtime_lines(values,count)
	# ------------------------------------------------------------						
			else:
				raise Warning(_("Please select any one from xls or csv formate!"))
			new_cr.close()

	
	#@api.multi
	def create_overtime_lines(self,values,count):
		employee_id = self.find_employee(values.get('employee_id'))
		description = values.get('description')
		hours = values.get('overtime')
		hours = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(hours) * 60, 60))
		ovt_hours = ovt_minute = 00
		if (len(hours) == 0 or (len(hours) >= 3 and not hours.__contains__(':')) or len(hours) > 5):
			raise Warning(_("Please Review Hours Column"))
		if ( len(hours) == 1  or len(hours) == 2 and not hours.__contains__(':')):
			ovt_hours = hours
		if hours.__contains__(':'):
			time_list = hours.split(":")
			ovt_hours = time_list[0]
			ovt_minute = time_list[1] if time_list[1] else 00
		else:	
			raise Warning(_("Please Review Hours Column"))

		overtime_date = datetime.strptime(ovt_hours+':'+ovt_minute, '%H:%M')
		overtime_date = timedelta(days=0,hours=overtime_date.hour,minutes=overtime_date.minute).total_seconds()/3600
		overtime_line = self.env['hr.employee.overtime.line.by.hours']
		print("Line Imported------------->",employee_id,description,hours)
		if employee_id and description and overtime_date and self.overtime_hour_id.id:
			vals = {
					'overtime_rel': self.overtime_hour_id.id,
					'employee_id': employee_id.id,
					'description': description,
					'overtime': overtime_date,
					
				}
			overtime_line.create(vals)
			self.env.cr.commit()

	# ---------------------------Employee-----------------

	#@api.multi
	def find_employee(self,employee):
		EmployeeObj=self.env['hr.employee']
		employee_id = EmployeeObj.search(['|',('name','=',employee),('driver_code','=',employee)],limit=1)
		if employee_id:
			return employee_id
		else:
			return False