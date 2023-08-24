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


import logging
import threading

class ImportContractLines(models.TransientModel):
	_name = "import.contract.lines"
	_description = "Import Contract Lines"

	File_slect = fields.Binary(string="Select Excel File")
	import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
	contract_id = fields.Many2one('bsg_customer_contract',string='Active Contract',)

	
	def imoport_file(self):
		self.action_lin_therad()
		
	def action_lin_therad(self):
		threaded_calculation = threading.Thread(target=self._imoport_file, args=())
		threaded_calculation.start()
		return {'type': 'ir.actions.act_window_close'}
	
	
	def _imoport_file(self):
		with api.Environment.manage():
			# As this function is in a new thread, I need to open a new cursor, because the old one may be closed
			new_cr = self.pool.cursor()
			self = self.with_env(self.env(cr=new_cr))
			# -----------------------------
			if self.import_option == 'csv':
	
				keys = ['loc_from', 'loc_to', 'car_size','service_type','price']
	
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
											'cont_customer':field[1],
											'loc_from' : field[2],
											'loc_to' : field[3],
											'car_size' : field[4],
											'service_type'  : field[5],
											'price'  : field[6],
											})
							
							res = self.create_contract_lines(values)
				
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
						values.update( {
											'cont_customer':line[1],
											'loc_from' : line[2],
											'loc_to' : line[3],
											'car_size' : line[4],
											'service_type' : line[5],
											'price'  : line[6],
										})
						res = self.create_contract_lines(values,count)
	# ------------------------------------------------------------						
			else:
				raise Warning(_("Please select any one from xls or csv formate!"))
			new_cr.close()

	
	
	def create_contract_lines(self,values,count):
		cont_customer = (values.get('cont_customer'))
		loc_from = self.find_location(values.get('loc_from'))
		loc_to = self.find_location(values.get('loc_to'))
		car_size = self.find_car_size(values.get('car_size'))
		service_type = self.find_car_service(values.get('service_type'))
		price = values.get('price')
		contract_line = self.env['bsg_customer_contract_line']
		print("Contract Line Imported------------->",cont_customer,loc_from,loc_to,car_size,service_type,price)
		if loc_from and loc_to and self.contract_id.id:
			vals = {
					'cust_contract_id': self.contract_id.id,
					'loc_from': loc_from.id,
					'loc_to': loc_to.id or False,
					'car_size': car_size.id or False,
					'service_type': service_type.id or False,
					'price': float(price),
				}
			if cont_customer == self.contract_id.cont_customer.name:
				contract_line.create(vals)
				self.env.cr.commit()


	# Prepare Price Line
	
	def _prepare_contract_line(self, contract_id, loc_from, loc_to, car_size, service_type, price):
		data = {
			'cust_contract_id': contract_id.id,
			'loc_from': loc_from.id,
			'loc_to': loc_to.id or False,
			'car_size': car_size.id or False,
			'service_type': service_type.id or False,
			'price': price or 0,
		}
		return data

# ---------------------------Location-----------------

	
	def find_location(self,location):
		LocationObj=self.env['bsg_route_waypoints']
		location_id = LocationObj.search([('route_waypoint_name','=',location)],limit=1)
		if location_id:
			return location_id
		else:
			return False

# ---------------------------find_car_size-----------------

	
	def find_car_size(self,car_size):
		Car_Size_Obj = self.env['bsg_car_size']
		car_size_id = Car_Size_Obj.search([('car_size_name','=',car_size)],limit=1)
		if car_size_id:
			return car_size_id
		else:
			return False


# ---------------------------find_car_size-----------------

	
	def find_car_service(self, service_name):
		# s = str(service_name)
		# service_name = s.rstrip('0').rstrip('.') if '.' in s else s
		Service_Obj = self.env['product.template']
		service_type_id = Service_Obj.search([('name','=',service_name)],limit=1)
		if service_type_id:
			return service_type_id
		else:
			return False
