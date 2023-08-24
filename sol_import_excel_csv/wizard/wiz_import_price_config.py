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

class ImportPriceConfig(models.TransientModel):
	_name = "import.price.config"
	_description = "Import Price Config"

	# Get default option for cargo_service_id
	@api.model
	def _default_cargo_service(self):
		return self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('bsg_cargo_sale.cargo_service_id')


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
										'loc_from_branch_no' : field[0],
										'loc_to_branch_no' : field[1],
										'car_size' : field[2],
										'price'  : field[3],
										'min_price'  : field[4],
										'round_trip_fee': field[5],
										'service_type': field[6],
										'customer_type': field[8],
										})
						res = self.create_price_config(values)

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

					values.update( {'loc_from_branch_no' : line[0],
									'loc_to_branch_no' : line[1],
									'car_size' : line[2],
									'price'  : line[3],
									'min_price'  : line[4],
									'round_trip_fee': line[5],
									'service_type': line[6],
									'customer_type': line[8],
									})
					res = self.create_price_config(values)
# ------------------------------------------------------------						
		else:
			raise Warning(_("Please select any one from xls or csv formate!"))

		return res
	# @api.multi
	def create_price_config(self,values):
		location_from = self.find_location(values.get('loc_from_branch_no'))
		location_to = self.find_location(values.get('loc_to_branch_no'))
		car_size = self.find_car_size(values.get('car_size'))
		car_classfication = self.find_car_classification()
		service_type = self.find_car_service(values.get('service_type'))
		price = values.get('price')
		min_price = values.get('min_price')
		round_trip_fee = values.get('round_trip_fee')
		customer_type = values.get('customer_type')
		price_config_obj = self.env['bsg_price_config']
		price_line_obj = self.env['bsg_price_line']
		if location_from and location_to:
			data={
					'waypoint_from' : location_from.id,
					'waypoint_to' : location_to.id,
					'customer_type':customer_type,

					}
			price_config_id = price_config_obj.search([
				('waypoint_from','=',location_from.id),
				('waypoint_to','=',location_to.id),
				('customer_type','=',customer_type)
				])
			if not price_config_id:
				price_config_id = price_config_obj.create(data)
				price_line_obj.create(
					self._prepare_price_line(price_config_id.id, car_size, car_classfication,
											   service_type, price,min_price, round_trip_fee))
			else:
				price_line_id = price_line_obj.search([
					('price_config_id','=',price_config_id.id),
					('car_size','=',car_size.id),
					('car_classfication','=',car_classfication.id),
					('service_type','=',service_type.id),
					('price','=',price),
					('min_price','=',min_price),
					('addtional_price','=',round_trip_fee),
					])

				if not price_line_id:
					price_line_obj.create(
						self._prepare_price_line(price_config_id.id, car_size, car_classfication,
												   service_type, price,min_price, round_trip_fee))

				print(location_from,location_to,car_size,car_classfication,\
					service_type,price,min_price,round_trip_fee,customer_type)
				return price_config_id


	# Prepare Price Line
	# @api.multi
	def _prepare_price_line(self, price_config_id, car_size, car_classfication, service_type, price,min_price, round_trip_fee):
		data = {
			'price_config_id': price_config_id,
			'car_size': car_size.id if car_size else False,
			'car_classfication': car_classfication.id or False,
			'service_type': service_type.id or False,
			'price': price or 0,
			'min_price': min_price or 0,
			'addtional_price': round_trip_fee or 0,
		}
		return data

# ---------------------------Location-----------------

	# @api.multi
	def find_location(self,location):
		# s = str(location)
		# location = s.rstrip('0').rstrip('.') if '.' in s else s
		# BranchObj = self.env['bsg_branches.bsg_branches']
		LocationObj=self.env['bsg_route_waypoints']
		# branch_id = BranchObj.search([('branch_no','=',location)],limit=1)
		if location:
			location_id = LocationObj.search([('route_waypoint_name','=',location)],limit=1)
			if location_id:
				return location_id
			else:
				return False

# ---------------------------find_car_size-----------------

	# @api.multi
	def find_car_size(self,car_size):
		Car_Size_Obj = self.env['bsg_car_size']
		car_size_id = Car_Size_Obj.search([('car_size_name','=',car_size)],limit=1)
		if car_size_id:
			return car_size_id
		else:
			return False

# ---------------------------find_car_size-----------------

	# @api.multi
	def find_car_classification(self):
		Car_Class_Obj = self.env['bsg_car_classfication']
		car_class_id = Car_Class_Obj.search([('car_class_name','=','Normal')],limit=1)
		if car_class_id:
			return car_class_id
		else:
			return False

# ---------------------------find_car_size-----------------

	# @api.multi
	def find_car_service(self, service_type):
		Service_Obj = self.env['product.template']
		ser_type_record = Service_Obj.search([('name','=',service_type)],limit=1)
		if ser_type_record:
			service_type_id = ser_type_record
		else:
			service_type_id = self._default_cargo_service()
		if service_type_id:
			return service_type_id
		else:
			return False
