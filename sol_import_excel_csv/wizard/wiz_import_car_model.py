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

class ImportCarModelConfig(models.TransientModel):
	_name = "import.carmodel.config"
	_description = "Import Car Model Config"

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
										'car_maker' : field[0],
										'car_size' : field[1],
										'car_model' : field[2],

										})
						res = self.create_car_model(values)

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

					values.update( {'car_maker' : line[0],
									'car_size' : line[1],
									'car_model' : line[2],							
									})
					res = self.create_car_model(values)
# ------------------------------------------------------------						
		else:
			raise Warning(_("Please select any one from xls or csv formate!"))

		return res
	# @api.multi
	def create_car_model(self,values):
		car_maker = self.find_car_maker(values.get('car_maker'))
		car_size = self.find_car_size(values.get('car_size'))
		car_model = self.find_car_model(values.get('car_model'))
		car_classfication = self.find_car_classification()
		car_config_obj = self.env['bsg_car_config']
		car_config_line_obj = self.env['bsg_car_line']
		if car_maker:
			data={'car_maker' : car_maker.id}

			car_config_id = car_config_obj.search([('car_maker','=',car_maker.id)])
			if not car_config_id:
				car_config_id = car_config_obj.create(data)
				car_config_line_obj.create(
					self._prepare_line(car_config_id.id, car_size, car_model, car_classfication))
			else:
				car_line_id = car_config_line_obj.search([
					('car_config_id','=',car_config_id.id),
					('car_size','=',car_size.id),
					('car_model','=',car_model.id),
					('car_classfication','=',car_classfication.id),
					])

				if not car_line_id:
					car_config_line_obj.create(
						self._prepare_line(car_config_id.id, car_size, car_model, car_classfication))

				return car_config_id


	# Prepare Price Line
	# @api.multi
	def _prepare_line(self, order_id, car_size, car_model, car_classfication):
		data = {
			'car_config_id': order_id,
			'car_size': car_size.id if car_size else False,
			'car_model': car_model.id if car_model else False,
			'car_classfication': car_classfication.id or False,
		}
		return data

# ---------------------------Find car maker-----------------

	# @api.multi
	def find_car_maker(self,car_maker):
		s = str(car_maker)
		car_maker = s.rstrip('0').rstrip('.') if '.' in s else s
		car_maker_id=self.env['bsg_car_make'].search([('car_make_old_sys_id','=',car_maker)],limit=1)
		if car_maker_id:
			return car_maker_id
		else:
			return False

# ---------------------------find_car_size-----------------

	# @api.multi
	def find_car_size(self,car_size):
		s = str(car_size)
		car_size = s.rstrip('0').rstrip('.') if '.' in s else s
		car_size_id = self.env['bsg_car_size'].search([('car_size_old_id','=',car_size)],limit=1)
		if car_size_id:
			return car_size_id
		else:
			return False

# ---------------------------find_car_model-----------------

	# @api.multi
	def find_car_model(self,car_model):
		s = str(car_model)
		car_model = s.rstrip('0').rstrip('.') if '.' in s else s
		car_model_id = self.env['bsg_car_model'].search([('car_model_old_sys_id','=',car_model)],limit=1)
		if car_model_id:
			return car_model_id
		else:
			return False


# ---------------------------find_car_model-----------------


	# @api.multi
	def find_car_classification(self):
		Car_Class_Obj = self.env['bsg_car_classfication']
		car_class_id = Car_Class_Obj.search([('car_class_name','=','Normal')],limit=1)
		if car_class_id:
			return car_class_id
		else:
			return False
