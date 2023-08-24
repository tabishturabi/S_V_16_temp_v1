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

class LinkTruckTrialer(models.TransientModel):
	_name = "link.truck.trailer"
	_description = "Link Truck Trailer"

	File_slect = fields.Binary(string="Select Excel File")
	import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')

	# @api.multi
	def imoport_file(self):

# -----------------------------
		if self.import_option == 'csv':

			keys = ['truck_id', 'trailer_id']

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
										'truck_id' : field[0],
										'trailer_id' :field[1],

										})
						res = self.link_truck_trailer(values)

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

					values.update( {'truck_id' : line[0],
									'trailer_id' :line[1],								
									})
					res = self.link_truck_trailer(values)
# ------------------------------------------------------------						
		else:
			raise Warning(_("Please select any one from xls or csv formate!"))

		return res

	# @api.multi
	def link_truck_trailer(self,values):
		if values['truck_id']:
			# Validation truck and trailer ids commig from importing file
			truck_id_str = str(values['truck_id'])
			truck_id = truck_id_str.rstrip('0').rstrip('.') if '.' in truck_id_str else truck_id_str
			trailer_id = str(values['trailer_id'])
			trailer_id = trailer_id.rstrip('0').rstrip('.') if '.' in trailer_id else trailer_id
			# search vehicle and trailer on basis of above validation
			search_vehicle_id = self.env['fleet.vehicle'].search([('taq_number','=',truck_id)])
			search_trailer_id = self.env['bsg_fleet_trailer_config'].search([('trailer_taq_no','=',trailer_id)])
			# linking trailer to respective truck
			if search_vehicle_id and search_trailer_id:
				search_vehicle_id.update({
					'trailer_id' : search_trailer_id.id
					})
				search_vehicle_id.create_associated_trailer()
		else:
			print('Parent id not found')
		