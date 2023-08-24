import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta
from num2words import num2words


class TaxReportXlsx(models.TransientModel):
	_name = 'report.fleet_status_report.fleetstatus_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'


	def generate_xlsx_report(self, workbook,input_records,docs):
		

		main_heading = workbook.add_format({
			"bold": 1, 
			"border": 1,
			"align": 'center',
			"valign": 'vcenter',
			"font_color":'black',
			"bg_color": '#D3D3D3',
			'font_size': '10',
			})

		main_heading1 = workbook.add_format({
			"bold": 1, 
			"border": 1,
			"align": 'left',
			"valign": 'vcenter',
			"font_color":'black',
			"bg_color": '#D3D3D3',
			'font_size': '10',
			})

		main_heading2 = workbook.add_format({
			"bold": 1, 
			"border": 1,
			"align": 'center',
			"valign": 'vcenter',
			"font_color":'black',
			"bg_color": 'red',
			'font_size': '10',
			})

		# Create a format to use in the merged range.
		merge_format = workbook.add_format({
			'bold': 1,
			'border': 1,
			'align': 'center',
			'valign': 'vcenter',
			'font_size': '13',
			"font_color":'black',
			'bg_color': '#D3D3D3'})

		main_data = workbook.add_format({
			"align": 'left',
			"valign": 'vcenter',
			'font_size': '8',
			})
		merge_format.set_shrink()
		main_heading.set_text_justlast(1)
		main_data.set_border()
		worksheet = workbook.add_worksheet('Fleet Status Report')


		worksheet.merge_range('A1:F1','Fleet Status Report',merge_format)

		
		
		worksheet.set_column('A:A', 15)
		worksheet.set_column('B:B', 25)
		worksheet.set_column('C:F', 15)
		
		

		worksheet.write('A3', 'Branch #', main_heading1)
		worksheet.write('B3', 'Branch Name', main_heading1)
		worksheet.write('C3', 'Trucks Available', main_heading1)
		worksheet.write('D3', 'Trucks Coming', main_heading1)
		worksheet.write('E3', 'Cars To Ship', main_heading1)
		worksheet.write('F3', 'Arrived Cars', main_heading1)
			
		row = 3
		col = 0

		lines = []
		lines_1 = []
		for x in docs.fleet_line_ids:
			if x.branch_no:
				lines.append(x)
			else:
				lines_1.append(x)

		if lines:
			lines = sorted(lines, key=lambda k: int(k.branch_no))
		
		
		for rec in lines:

			worksheet.write_string (row, col,str(rec.branch_id.branch_no),main_data)
			worksheet.write_string (row, col+1,str(rec.branch_id.branch_ar_name),main_data)
			worksheet.write_string (row, col+2,str(rec.trucks_available),main_data)
			worksheet.write_string (row, col+3,str(rec.trucks_comming),main_data)
			worksheet.write_string (row, col+4,str(rec.shiping_cars),main_data)
			worksheet.write_string (row, col+5,str(rec.arrived_cars),main_data)
			
			row += 1

		for new in lines_1:

			worksheet.write_string (row, col,str(new.branch_id.branch_no),main_data)
			worksheet.write_string (row, col+1,str(new.branch_id.branch_ar_name),main_data)
			worksheet.write_string (row, col+2,str(new.trucks_available),main_data)
			worksheet.write_string (row, col+3,str(new.trucks_comming),main_data)
			worksheet.write_string (row, col+4,str(new.shiping_cars),main_data)
			worksheet.write_string (row, col+5,str(new.arrived_cars),main_data)
			
			row += 1







		
