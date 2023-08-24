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


class BxInvoiceTaxReportXlsx(models.TransientModel):
	_name = 'report.bsg_tranport_bx_credit_customer_collection.bx_coll'
	_inherit = 'report.report_xlsx.abstract'

	
	def generate_xlsx_report(self, workbook,input_records,lines):

		cust_info = []
		if lines.invoice_to:
			cust_info = lines.invoice_to
		else:
			cust_info = lines.customer_id
		

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
		worksheet = workbook.add_worksheet('Bx Invoice Report')


		cust_name = str(cust_info.parent_id.name)+' , '+str(cust_info.name)

		worksheet.merge_range('A1:L1','Collection Report',merge_format)
		worksheet.merge_range('A2:C2','Customer Information',main_heading)
		worksheet.merge_range('D2:F2','بيانات‬ العميل‬',main_heading)
		worksheet.write('A3','Customer Name', main_heading)
		worksheet.merge_range('B3:E3',str(cust_name),main_data)
		worksheet.write('F3','اسم‬ العميل‬', main_heading)
		worksheet.write('A4','Tax Account No', main_heading)
		worksheet.merge_range('B4:E4',str(cust_info.vat),main_data)
		worksheet.write('F4','الرقم‬ الضريبي‬', main_heading)
		worksheet.write('A5','Address', main_heading)
		worksheet.merge_range('B5:E5',str(cust_info.street),main_data)
		worksheet.write('F5','‫‪العنوان‬', main_heading)
		worksheet.write('A6','Telephone No', main_heading)
		worksheet.merge_range('B6:E6',str(cust_info.phone),main_data)
		worksheet.write('F6','رقم‬ الھاتف‬', main_heading)


		worksheet.merge_range('G2:I2','Company Information',main_heading)
		worksheet.merge_range('J2:L2','بيانات‬ الشركه‬',main_heading)
		worksheet.write('G3','Company Name', main_heading)
		worksheet.merge_range('H3:K3','مجموعة أعمال البسامي الدولية',main_data)
		worksheet.write('L3','اسم‬ الشركه‬', main_heading)
		worksheet.write('G4','Tax Account No', main_heading)
		worksheet.merge_range('H4:K4','‫‪300043273800003‬‬',main_data)
		worksheet.write('L4','الرقم‬ الضريبي‬', main_heading)
		worksheet.write('G5','Address', main_heading)
		worksheet.merge_range('H5:K5','Between Exit 10 and Exit 11, Al Bassami Building,Al Quds,Riyadh',main_data)
		worksheet.write('L5','‫‪العنوان‬', main_heading)
		worksheet.write('G6','Telephone No', main_heading)
		worksheet.merge_range('H6:K6','‫‪920005353‬‬',main_data)
		worksheet.write('L6','رقم‬ الھاتف‬', main_heading)
		
		worksheet.set_column('A:A', 15)
		worksheet.set_column('B:B', 15)
		worksheet.set_column('D:D', 15)
		worksheet.set_column('E:E', 15)
		worksheet.set_column('F:J', 15)
		worksheet.set_column('K:K', 15)
		worksheet.set_column('G:G', 15)
		worksheet.set_column('H:H', 15)
		worksheet.set_column('L:L', 20)
		

		worksheet.write('A8', 'Total Amount', main_heading1)
		worksheet.write('B8', 'Tax Amount', main_heading1)
		worksheet.write('C8', 'Taxes', main_heading1)
		worksheet.write('D8', 'Amount', main_heading1)
		worksheet.write('E8', 'Fleet Type', main_heading1)
		worksheet.write('F8', 'Delivery Branch', main_heading1)
		worksheet.write('G8', 'Shipping Branch', main_heading1)
		worksheet.write('H8', 'Customer Ref', main_heading1)
		worksheet.write('I8', 'Bx Argument Date', main_heading1)
		worksheet.write('J8', 'Bx Argument #', main_heading1)
		
		worksheet.write('A9', 'اجمالي‬ القيمه', main_heading1)
		worksheet.write('B9', 'قيمه‬ الضريبه', main_heading1)
		worksheet.write('C9', 'ضريبه', main_heading1)
		worksheet.write('D9', 'القيمه', main_heading1)
		worksheet.write('E9', 'نوع المقطورة', main_heading1)
		worksheet.write('F9', 'فرع‬ الوصول', main_heading1)
		worksheet.write('G9', 'فرع‬ الشحن', main_heading1)
		worksheet.write('H9', 'مرجع العميل', main_heading1)
		worksheet.write('I9', 'تاريخ الاتفاقية', main_heading1)
		worksheet.write('J9', 'اتفاقيه‬ شحن', main_heading1)
		# worksheet.write('K9', 'نوع‬ الخدمه‬', main_heading1)
		# worksheet.write('L9', 'اتفاقيه‬ شحن‬', main_heading1)
		
		
		row = 9
		col = 0

		cargo_ids = []
		for d in lines.transport_management_ids:
			cargo_ids.append(d)

		
		cargo_ids = sorted(cargo_ids, key=lambda k: k.bx_credit_sequnce)

		num_of_recs = len(cargo_ids)


		def number_to_spell(attrb):
			word = num2words((attrb))
			word = word.title() + " " + "SAR Only"
			return word

		price = 0
		tax_amount = 0
		total_amount = 0
		for rec in cargo_ids:

			price = price + rec.price
			tax_amount = tax_amount + rec.tax_amount
			total_amount = total_amount + rec.total_amount
				
			worksheet.write_string (row, col,str("{0:.2f}".format(rec.price)),main_data)
			worksheet.write_string (row, col+1,str("{0:.2f}".format(rec.tax_amount)),main_data)
			worksheet.write_string (row, col+2,str(sum(rec.tax_ids.mapped('amount')))+'%',main_data)
			worksheet.write_string (row, col+3,str("{0:.2f}".format(rec.total_amount)),main_data)
			worksheet.write_string (row, col+4,str(rec.fleet_type.vehicle_type_name),main_data)
			worksheet.write_string (row, col+5,str(rec.to.route_waypoint_name),main_data)
			worksheet.write_string (row, col+6,str(rec.form.route_waypoint_name),main_data)
			worksheet.write_string (row, col+7,str(rec.transport_management.customer_ref),main_data)
			worksheet.write_string (row, col+8,str(rec.order_date),main_data)
			worksheet.write_string (row, col+9,str(rec.transportation_no),main_data)

			row += 1


		loc = 'A'+str(row+2)
		loc1 = 'B'+str(row+2)
		loc2 = 'C'+str(row+2)
		loc3 = 'D'+str(row+2)
		loc4 = 'E'+str(row+2)
		loc5 = 'F'+str(row+2)
		loc6 = 'G'+str(row+2)
		loc7 = 'H'+str(row+2)
		loc8 = 'I'+str(row+2)
		loc9 = 'J'+str(row+2)
		loc10 = 'K'+str(row+2)
		loc11 = 'L'+str(row+2)
		
		end_1 = str(loc)+':'+str(loc1)
		end_2 = str(loc2)+':'+str(loc3)
		end_3 = str(loc4)+':'+str(loc5)
		end_4 = str(loc6)+':'+str(loc7)
		end_5 = str(loc8)+':'+str(loc9)
		end_6 = str(loc10)+':'+str(loc11)

		worksheet.merge_range(str(end_1),str("{0:.2f}".format(price)),main_heading)
		worksheet.merge_range(str(end_2), 'Shipping Amount' ,main_heading)
		worksheet.merge_range(str(end_3), 'قيمه‬ الشحن‬' ,main_heading)
		worksheet.merge_range(str(end_4), 'Number of Agreements',main_heading)
		worksheet.merge_range(str(end_5), str(num_of_recs) ,main_heading)
		worksheet.merge_range(str(end_6), 'عدد‬ االتفاقيات‬' ,main_heading)


		loc2 = 'A'+str(row+3)
		loc12 = 'B'+str(row+3)
		loc22 = 'C'+str(row+3)
		loc32 = 'D'+str(row+3)
		loc42 = 'E'+str(row+3)
		loc52 = 'F'+str(row+3)
		loc62 = 'G'+str(row+3)
		loc72 = 'H'+str(row+3)
		loc82 = 'I'+str(row+3)
		loc92 = 'J'+str(row+3)
		loc102 = 'K'+str(row+3)
		loc112 = 'L'+str(row+3)
		
		end_12 = str(loc2)+':'+str(loc12)
		end_22 = str(loc22)+':'+str(loc32)
		end_32 = str(loc42)+':'+str(loc52)
		end_42 = str(loc62)+':'+str(loc72)
		end_52 = str(loc82)+':'+str(loc92)
		end_62 = str(loc102)+':'+str(loc112)

		worksheet.merge_range(str(end_12),str('-'),main_heading)
		worksheet.merge_range(str(end_22), '-' ,main_heading)
		worksheet.merge_range(str(end_32), 'الخصومات‬' ,main_heading)
		worksheet.merge_range(str(end_42),str('The Bill of'),main_heading)
		worksheet.merge_range(str(end_52), str(lines.date) ,main_heading)
		worksheet.merge_range(str(end_62), ' ' ,main_heading)

		loc4 = 'A'+str(row+4)
		loc14 = 'B'+str(row+4)
		loc24 = 'C'+str(row+4)
		loc34 = 'D'+str(row+4)
		loc44 = 'E'+str(row+4)
		loc54 = 'F'+str(row+4)
		loc64 = 'G'+str(row+4)
		loc74 = 'H'+str(row+4)
		loc84 = 'I'+str(row+4)
		loc94 = 'J'+str(row+4)
		loc104 = 'K'+str(row+4)
		loc114 = 'L'+str(row+4)
		
		end_14 = str(loc4)+':'+str(loc14)
		end_24 = str(loc24)+':'+str(loc34)
		end_34 = str(loc44)+':'+str(loc54)
		end_44 = str(loc64)+':'+str(loc94)
		end_54 = str(loc84)+':'+str(loc94)
		end_64 = str(loc104)+':'+str(loc114)

		worksheet.merge_range(str(end_14),str("{0:.2f}".format(price)),main_heading)
		worksheet.merge_range(str(end_24), 'Total Amount' ,main_heading)
		worksheet.merge_range(str(end_34), 'القيمه‬ بعد‬ الخصم‬' ,main_heading)
		worksheet.merge_range(str(end_44),str(number_to_spell(price)),main_heading)
		worksheet.merge_range(str(end_64), str(lines.internal_note) ,main_heading)


		loc5 = 'A'+str(row+5)
		loc15 = 'B'+str(row+5)
		loc25 = 'C'+str(row+5)
		loc35 = 'D'+str(row+5)
		loc45 = 'E'+str(row+5)
		loc55 = 'F'+str(row+5)
		loc65 = 'G'+str(row+5)
		loc75 = 'H'+str(row+5)
		loc85 = 'I'+str(row+5)
		loc95 = 'J'+str(row+5)
		loc105 = 'K'+str(row+5)
		loc115 = 'L'+str(row+5)
		
		end_15 = str(loc5)+':'+str(loc15)
		end_25 = str(loc25)+':'+str(loc35)
		end_35 = str(loc45)+':'+str(loc55)
		end_45 = str(loc65)+':'+str(loc95)
		end_55 = str(loc85)+':'+str(loc95)
		end_65 = str(loc105)+':'+str(loc115)

		worksheet.merge_range(str(end_15),str("{0:.2f}".format(tax_amount)),main_heading)
		worksheet.merge_range(str(end_25), 'Tax Amount' ,main_heading)
		worksheet.merge_range(str(end_35), 'ضريبه‬ القيمه‬ المضافه‬' ,main_heading)
		worksheet.merge_range(str(end_45), str(number_to_spell(tax_amount)),main_heading)
		worksheet.merge_range(str(end_55), ' ',main_heading)
		worksheet.merge_range(str(end_65), ' ' ,main_heading)

		loc6 = 'A'+str(row+6)
		loc16 = 'B'+str(row+6)
		loc26 = 'C'+str(row+6)
		loc36 = 'D'+str(row+6)
		loc46 = 'E'+str(row+6)
		loc56 = 'F'+str(row+6)
		loc66 = 'G'+str(row+6)
		loc76 = 'H'+str(row+6)
		loc86 = 'I'+str(row+6)
		loc96 = 'J'+str(row+6)
		loc106 = 'K'+str(row+6)
		loc116 = 'L'+str(row+6)
		
		end_16 = str(loc6)+':'+str(loc16)
		end_26 = str(loc26)+':'+str(loc36)
		end_36 = str(loc46)+':'+str(loc56)
		end_46 = str(loc66)+':'+str(loc96)
		end_56 = str(loc86)+':'+str(loc96)
		end_66 = str(loc106)+':'+str(loc116)

		worksheet.merge_range(str(end_16),str("{0:.2f}".format(total_amount)),main_heading)
		worksheet.merge_range(str(end_26), 'Net Amount' ,main_heading)
		worksheet.merge_range(str(end_36), 'اجمالي‬ المستحق‬' ,main_heading)
		worksheet.merge_range(str(end_46), str(number_to_spell(total_amount)),main_heading)
		worksheet.merge_range(str(end_56), ' ',main_heading)
		worksheet.merge_range(str(end_66), ' ' ,main_heading)

		







		
