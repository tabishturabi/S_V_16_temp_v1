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


class BranchesVoucherXlsx(models.TransientModel):
	_name = 'report.bassami_branches_vouchers_report.voucher_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	# @api.multi
	def generate_xlsx_report(self, workbook, input_records, lines):
		data = input_records['form']


		branch_id = []
		for rec in data['branch_ids']:
			branch_id.append(rec)

		if data['report_type'] == 'all':
			types = "All Voucher"
			records = self.env['account.payment'].search([('date','>=',data['form']),('date','<=',data['to']),('branch_ids.id','in',branch_id),('state','not in',('draft','cancelled'))])

		if data['report_type'] == 'rec':
			types = "Receipt Voucher"
			records = self.env['account.payment'].search([('date','>=',data['form']),('date','<=',data['to']),('branch_ids.id','in',branch_id),('state','not in',('draft','cancelled')),('payment_type','=','inbound')])

		if data['report_type'] == 'pay':
			types = "Payment Voucher"
			records = self.env['account.payment'].search([('date','>=',data['form']),('date','<=',data['to']),('branch_ids.id','in',branch_id),('state','not in',('draft','cancelled')),('payment_type','=','outbound')])

		if data['report_type'] == 'trans':
			types = "Internal Transfer"
			records = self.env['account.payment'].search([('date','>=',data['form']),('date','<=',data['to']),('branch_ids.id','in',branch_id),('state','not in',('draft','cancelled')),('is_internal_transfer','=',True),])

			
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
		worksheet = workbook.add_worksheet('Branches Voucher Report')


		worksheet.merge_range('A1:L1','Branches Voucher Report',merge_format)
		worksheet.write('A2', 'Date From', main_heading)
		worksheet.write('B2', str(data['form']), main_data)
		worksheet.write('D2', 'Date To', main_heading)
		worksheet.write('E2', str(data['to']), main_data)
		worksheet.write('G2', 'Report Type', main_heading)
		worksheet.write('H2', str(types), main_data)

		worksheet.write('A3', 'Collection Voucher ref', main_heading1)
		worksheet.write('B3', 'Memo', main_heading1)
		worksheet.write('C3', 'Budget number', main_heading1)
		worksheet.write('D3', 'Operation Number', main_heading1)
		worksheet.write('E3', 'Payment Method Type', main_heading1)
		worksheet.write('F3', 'Branch', main_heading1)
		worksheet.write('G3', 'Payment Journal', main_heading1)
		worksheet.write('H3', 'Partner', main_heading1)
		worksheet.write('I3', 'Voucher Date', main_heading1)
		worksheet.write('J3', 'Voucher number', main_heading1)
		worksheet.write('K3', 'Cargo Sale', main_heading1)
		worksheet.write('L3', 'Trip', main_heading1)

		worksheet.write('A4', 'رقم مرجع السند', main_heading1)
		worksheet.write('B4', 'البيان', main_heading1)
		worksheet.write('C4', 'رقم  الموازنة', main_heading1)
		worksheet.write('D4', 'رقم الموافقة', main_heading1)
		worksheet.write('E4', 'نوع السداد', main_heading1)
		worksheet.write('F4', 'الفرع', main_heading1)
		worksheet.write('G4', 'يومية السداد', main_heading1)
		worksheet.write('H4', 'اسم العميل', main_heading1)
		worksheet.write('I4', 'تاريخ السند', main_heading1)
		worksheet.write('J4', 'رقم السند', main_heading1)
		worksheet.write('K4', 'Cargo Sale', main_heading1)
		worksheet.write('L4', 'Trip', main_heading1)

		worksheet.set_column('A:L', 18)
		# worksheet.set_column('N:Z', 18)
		# worksheet.set_column('AA:AG', 20)
		# worksheet.set_column('AH:AL', 18)
		# worksheet.set_column('AM:AR', 20)
		# worksheet.set_column('AS:AW', 20)

	
		row = 5
		col = 0
		for rec in records:

			worksheet.write_string (row, col,str(rec.collectionre),main_data)
			worksheet.write_string (row, col+1,str(rec.communication),main_data)
			worksheet.write_string (row, col+2,str(rec.budget_number),main_data)
			worksheet.write_string (row, col+3,str(rec.operation_number),main_data)
			worksheet.write_string (row, col+4,str('-'),main_data)
			worksheet.write_string (row, col+5,str(rec.branch_ids.branch_ar_name),main_data)
			worksheet.write_string (row, col+6,str(rec.journal_id.name),main_data)
			worksheet.write_string (row, col+7,str(rec.partner_id.name),main_data)
			worksheet.write_string (row, col+8,str(rec.date),main_data)
			worksheet.write_string (row, col+9,str(rec.name),main_data)
			worksheet.write_string (row, col+10,str(rec.cargo_sale_order_id.name),main_data)
			worksheet.write_string (row, col+11,str(rec.fleet_trip_id.name),main_data)

			row += 1

		
			

	
