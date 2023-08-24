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


class TaxReportXlsx(models.TransientModel):
	_name = 'report.bsg_tax_report.bsg_tax_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	# @api.multi
	def generate_xlsx_report(self, workbook, input_records, lines):
		data = input_records['form']

		domain = [('order_date','>=',data['form']),('order_date','<=',data['to']),('state','!=','cancel')]

		if data['payment_method_ids']:
			payment_methods = []
			for pay in data['payment_method_ids']:
				payment_methods.append(pay)
			domain.append(('payment_method.id','in',payment_methods))

		trans = self.env['bsg_vehicle_cargo_sale_line'].search(domain, order='order_date')
		

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
		worksheet = workbook.add_worksheet('Tax Report')


		worksheet.merge_range('A1:G1','Tax Report',merge_format)
		worksheet.write('A2', 'Date From', main_heading)
		worksheet.write('B2', str(data['form']), main_data)
		worksheet.write('C2', 'Date To', main_heading)
		worksheet.write('D2', str(data['to']), main_data)
		worksheet.write('F2', 'Report Type', main_heading)
		worksheet.write('G2', str(data['filters']), main_data)

		worksheet.set_column('A:B', 20)
		worksheet.set_column('C:G', 15)


		if data['filters'] == 'detail':

			worksheet.write('A4', 'SO #', main_heading1)
			worksheet.write('B4', 'Customer', main_heading1)
			worksheet.write('C4', 'From', main_heading1)
			worksheet.write('D4', 'To', main_heading1)
			worksheet.write('E4', 'Total without Tax', main_heading1)
			worksheet.write('F4', 'Charges With Tax', main_heading1)
			worksheet.write('G4', 'Tax Amount', main_heading1)
			

			worksheet.write('A5', 'رقم الاتفاقية', main_heading1)
			worksheet.write('B5', 'إسم العميل', main_heading1)
			worksheet.write('C5', 'فرع الشحن', main_heading1)
			worksheet.write('D5', 'فرع الوصول', main_heading1)
			worksheet.write('E5', 'المبلغ بدون الضريبة', main_heading1)
			worksheet.write('F5', 'المبلغ مع الضريبة', main_heading1)
			worksheet.write('G5', 'قيمة الضريبة', main_heading1)
			

		
			row = 5
			col = 0

			tot_charges = 0
			tot_with_tax = 0
			tot_tax = 0

			for rec in trans:

				if rec.order_date and ((str(rec.order_date)[:10]) >= data['form'] and (str(rec.order_date)[:10]) <= data['to']) and '*' not in rec.sale_line_rec_name:

					charges_with_tax = 0
					tax_amount = 0
					charges_with_tax = rec.charges + (rec.charges*0.05)
					tax_amount = rec.charges*0.05
					
					worksheet.write_string (row, col,str(rec.sale_line_rec_name),main_data)
					worksheet.write_string (row, col+1,str(rec.customer_id.name),main_data)
					worksheet.write_string (row, col+2,str(rec.loc_from.route_waypoint_name),main_data)
					worksheet.write_string (row, col+3,str(rec.loc_to.route_waypoint_name),main_data)
					worksheet.write_string (row, col+4,str("{0:.2f}".format(rec.charges)),main_data)
					worksheet.write_string (row, col+5,str("{0:.2f}".format(charges_with_tax)),main_data)
					worksheet.write_string (row, col+6,str("{0:.2f}".format(tax_amount)),main_data)

					tot_charges = tot_charges + rec.charges
					tot_with_tax = tot_with_tax + charges_with_tax
					tot_tax = tot_tax + tax_amount

					row += 1

			loc = 'A'+str(row+1)
			loc1 = 'D'+str(row+1)
			loc2 = 'E'+str(row+1)
			loc3 = 'F'+str(row+1)
			loc4 = 'G'+str(row+1)
			

			end_loc = str(loc)+':'+str(loc1)
			worksheet.merge_range(str(end_loc), 'Total' ,main_heading)
			worksheet.write_string(str(loc2),str("{0:.2f}".format(tot_charges)),main_heading1)
			worksheet.write_string(str(loc3),str("{0:.2f}".format(tot_with_tax)),main_heading1)
			worksheet.write_string(str(loc4),str("{0:.2f}".format(tot_tax)),main_heading1)


		else:

			if not data['payment_method_ids']:

				worksheet.write('A4', 'SO #', main_heading1)
				worksheet.write('B4', 'Total without Tax', main_heading1)
				worksheet.write('C4', 'Charges With Tax', main_heading1)
				worksheet.write('D4', 'Tax Amount', main_heading1)
				

				worksheet.write('A5', 'رقم الاتفاقية', main_heading1)
				worksheet.write('B5', 'المبلغ بدون الضريبة', main_heading1)
				worksheet.write('C5', 'المبلغ مع الضريبة', main_heading1)
				worksheet.write('D5', 'قيمة الضريبة', main_heading1)

				row = 5
				col = 0

				tot_charges = 0
				tot_with_tax = 0
				tot_tax = 0
				count = 0

				for rec in trans:

					if rec.order_date and ((str(rec.order_date)[:10]) >= data['form'] and (str(rec.order_date)[:10]) <= data['to']) and '*' not in rec.sale_line_rec_name:

						charges_with_tax = 0
						tax_amount = 0
						charges_with_tax = rec.charges + (rec.charges*0.05)
						tax_amount = rec.charges*0.05

						tot_charges = tot_charges + rec.charges
						tot_with_tax = tot_with_tax + charges_with_tax
						tot_tax = tot_tax + tax_amount
						count = count + 1


				worksheet.write_string (row, col,str(count),main_data)
				worksheet.write_string (row, col+1,str("{0:.2f}".format(tot_charges)),main_data)
				worksheet.write_string (row, col+2,str("{0:.2f}".format(tot_with_tax)),main_data)
				worksheet.write_string (row, col+3,str("{0:.2f}".format(tot_tax)),main_data)


			if data['payment_method_ids']:

				worksheet.write('A4', 'Payment Method', main_heading1)
				worksheet.write('B4', 'SO #', main_heading1)
				worksheet.write('C4', 'Total without Tax', main_heading1)
				worksheet.write('D4', 'Charges With Tax', main_heading1)
				worksheet.write('E4', 'Tax Amount', main_heading1)
				
				worksheet.write('A5', 'طريقة الدفع', main_heading1)
				worksheet.write('B5', 'رقم الاتفاقية', main_heading1)
				worksheet.write('C5', 'المبلغ بدون الضريبة', main_heading1)
				worksheet.write('D5', 'المبلغ مع الضريبة', main_heading1)
				worksheet.write('E5', 'قيمة الضريبة', main_heading1)

				row = 5
				col = 0


				for pay in data['payment_method_ids']:

					tot_charges = 0
					tot_with_tax = 0
					tot_tax = 0
					count = 0
					display_name = self.env['cargo_payment_method'].search([('id','=',pay)])

					for rec in trans:

						if rec.order_date and ((str(rec.order_date)[:10]) >= data['form'] and (str(rec.order_date)[:10]) <= data['to']) and '*' not in rec.sale_line_rec_name and rec.payment_method.id == pay:

							charges_with_tax = 0
							tax_amount = 0
							charges_with_tax = rec.charges + (rec.charges*0.05)
							tax_amount = rec.charges*0.05

							tot_charges = tot_charges + rec.charges
							tot_with_tax = tot_with_tax + charges_with_tax
							tot_tax = tot_tax + tax_amount
							count = count + 1


					worksheet.write_string (row, col,str(display_name.display_name),main_data)
					worksheet.write_string (row, col+1,str(count),main_data)
					worksheet.write_string (row, col+2,str("{0:.2f}".format(tot_charges)),main_data)
					worksheet.write_string (row, col+3,str("{0:.2f}".format(tot_with_tax)),main_data)
					worksheet.write_string (row, col+4,str("{0:.2f}".format(tot_tax)),main_data)

					row += 1












		
