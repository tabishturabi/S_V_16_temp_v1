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
	_name = 'report.bsg_corporate_invoice_contract.coll_report_xlsx'
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
		worksheet = workbook.add_worksheet('Collection Report')


		cust_name = str(cust_info.parent_id.name)+' , '+str(cust_info.name)

		worksheet.merge_range('A1:N1','Collection Report',merge_format)
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
		worksheet.write('A7','Print Date', main_heading)
		worksheet.merge_range('B7:E7',str(datetime.now().strftime('%d-%m-%Y %H:%M:%S')),main_data)
		worksheet.write('F7','تاريـخ الطباعـة‬', main_heading)


		worksheet.merge_range('G2:I2','Company Information',main_heading)
		worksheet.merge_range('J2:N2','بيانات‬ الشركه‬',main_heading)
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
		worksheet.set_column('K:K', 15)
		worksheet.set_column('G:G', 15)
		worksheet.set_column('H:H', 15)
		worksheet.set_column('L:L', 20)
		worksheet.set_column('M:M', 20)
		worksheet.set_column('N:N', 20)


		worksheet.write('A8', 'Total Amount', main_heading1)
		worksheet.write('B8', 'Tax Amount', main_heading1)
		worksheet.write('C8', '%Tax', main_heading1)
		worksheet.write('D8', 'After Discount', main_heading1)
		worksheet.write('E8', '%Discount', main_heading1)
		worksheet.write('F8', 'Other Service', main_heading1)
		worksheet.write('G8', 'Amount', main_heading1)
		worksheet.write('H8', 'Delivery Branch', main_heading1)
		worksheet.write('I8', 'Shipping Branch', main_heading1)
		worksheet.write('J8', 'Plate', main_heading1)
		worksheet.write('K8', 'Chassis', main_heading1)
		worksheet.write('L8', 'Service Type', main_heading1)
		worksheet.write('M8', 'Shipping Agreement', main_heading1)
		worksheet.write('N8', 'Baptizing Number', main_heading1)

		worksheet.write('A9', 'اجمالي‬ القيمه‬', main_heading1)
		worksheet.write('B9', 'قيمه‬ الضريبه‬', main_heading1)
		worksheet.write('C9', 'ضريبه‬', main_heading1)
		worksheet.write('D9', 'بعد‬ الخصم‬', main_heading1)
		worksheet.write('E9', 'الخصم‬', main_heading1)
		worksheet.write('F9', 'خدمة أخرى‬', main_heading1)
		worksheet.write('G9', 'القيمه‬', main_heading1)
		worksheet.write('H9', 'فرع‬ الوصول‬', main_heading1)
		worksheet.write('I9', 'فرع‬ الشحن‬', main_heading1)
		worksheet.write('J9', 'اللوحه‬', main_heading1)
		worksheet.write('K9', 'الھيكل‬', main_heading1)
		worksheet.write('L9', 'نوع‬ الخدمه‬', main_heading1)
		worksheet.write('M9', 'اتفاقيه‬ شحن‬', main_heading1)
		worksheet.write('N9', 'رقم‬ التعميد‬', main_heading1)
		
		
		row = 9
		col = 0

		cargo_ids = []
		for d in lines.cargo_sale_line_ids:
			cargo_ids.append(d)

		if lines.report_branch_wise:
			cargo_ids = sorted(cargo_ids, key=lambda k: (int(k.loc_from.loc_branch_id.branch_no),k.id))
		elif lines.report_branch_wise_delivery:
			cargo_ids = sorted(cargo_ids, key=lambda k: (int(k.loc_to.loc_branch_id.branch_no),k.id))
		else:
			cargo_ids = sorted(cargo_ids, key=lambda k: k.report_seq)

		num_of_recs = len(cargo_ids)


		def number_to_spell(attrb):
			word = num2words((attrb))
			word = word.title() + " " + "SAR Only"
			return word

		net = 0
		tax = 0
		total = 0
		unittotal = 0
		tot_service = 0
		for rec in cargo_ids:

			net = net + rec.charges + rec.other_service_amount
			tax = tax + rec.tax_amount
			total = total + rec.total_without_tax
			unittotal = unittotal + rec.unit_charge+rec.additional_ship_amount
			tot_service = tot_service + rec.other_service_amount

			worksheet.write_string (row, col,str("{0:.2f}".format(rec.charges + rec.other_service_amount)),main_data)
			worksheet.write_string (row, col+1,str("{0:.2f}".format(rec.tax_amount)),main_data)
			worksheet.write_string (row, col+2,str(sum(rec.tax_ids.mapped('amount'))),main_data)
			worksheet.write_string (row, col+3,str("{0:.2f}".format(rec.total_without_tax)),main_data)
			worksheet.write_string (row, col+4,str("{0:.2f}".format(rec.discount)),main_data)
			worksheet.write_string (row, col+5,str("{0:.2f}".format(rec.other_service_amount)),main_data)
			worksheet.write_string (row, col+6,str("{0:.2f}".format(rec.unit_charge+rec.additional_ship_amount)),main_data)
			worksheet.write_string (row, col+7,str(rec.loc_to.route_waypoint_name),main_data)
			worksheet.write_string (row, col+8,str(rec.loc_from.route_waypoint_name),main_data)
			worksheet.write_string (row, col+9,str(rec.plate_no)+' '+str(rec.palte_third)+' '+str(rec.palte_second)+' '+str(rec.palte_one),main_data)
			worksheet.write_string (row, col+10,str(rec.chassis_no),main_data)
			worksheet.write_string (row, col+11,str(rec.service_type.name),main_data)
			worksheet.write_string (row, col+12,str(rec.sale_line_rec_name),main_data)
			worksheet.write_string(row,  col+13,str(rec.bsg_cargo_sale_id.baptizing_number), main_data)

			row += 1

		loc = 'A' + str(row + 2)
		loc1 = 'B' + str(row + 2)
		loc2 = 'C' + str(row + 2)
		loc3 = 'D' + str(row + 2)
		loc4 = 'E' + str(row + 2)
		loc5 = 'F' + str(row + 2)
		loc6 = 'G' + str(row + 2)
		loc7 = 'H' + str(row + 2)
		loc8 = 'I' + str(row + 2)
		loc9 = 'J' + str(row + 2)
		loc10 = 'K' + str(row + 2)
		loc11 = 'L' + str(row + 2)

		end_1 = str(loc) + ':' + str(loc1)
		end_2 = str(loc2) + ':' + str(loc3)
		end_3 = str(loc4) + ':' + str(loc5)
		end_4 = str(loc6) + ':' + str(loc7)
		end_5 = str(loc8) + ':' + str(loc9)
		end_6 = str(loc10) + ':' + str(loc11)

		worksheet.merge_range(str(end_1), str("{0:.2f}".format(unittotal)), main_heading)
		worksheet.merge_range(str(end_2), 'Shipping Amount', main_heading)
		worksheet.merge_range(str(end_3), 'قيمه‬ الشحن‬', main_heading)
		worksheet.merge_range(str(end_4), 'Number of Agreements', main_heading)
		worksheet.merge_range(str(end_5), str(num_of_recs), main_heading)
		worksheet.merge_range(str(end_6), 'عدد‬ االتفاقيات‬', main_heading)

		loc2 = 'A' + str(row + 3)
		loc12 = 'B' + str(row + 3)
		loc22 = 'C' + str(row + 3)
		loc32 = 'D' + str(row + 3)
		loc42 = 'E' + str(row + 3)
		loc52 = 'F' + str(row + 3)
		loc62 = 'G' + str(row + 3)
		loc72 = 'H' + str(row + 3)
		loc82 = 'I' + str(row + 3)
		loc92 = 'J' + str(row + 3)
		loc102 = 'K' + str(row + 3)
		loc112 = 'L' + str(row + 3)

		end_12 = str(loc2) + ':' + str(loc12)
		end_22 = str(loc22) + ':' + str(loc32)
		end_32 = str(loc42) + ':' + str(loc52)
		end_42 = str(loc62) + ':' + str(loc72)
		end_52 = str(loc82) + ':' + str(loc92)
		end_62 = str(loc102) + ':' + str(loc112)

		worksheet.merge_range(str(end_12), str("{0:.2f}".format(tot_service)), main_heading)
		worksheet.merge_range(str(end_22), 'Other Service Amount', main_heading)
		worksheet.merge_range(str(end_32), 'الخصومات‬', main_heading)
		worksheet.merge_range(str(end_42), str('The Bill of'), main_heading)
		worksheet.merge_range(str(end_52), str(lines.date), main_heading)
		worksheet.merge_range(str(end_62), ' ', main_heading)

		loc4 = 'A' + str(row + 4)
		loc14 = 'B' + str(row + 4)
		loc24 = 'C' + str(row + 4)
		loc34 = 'D' + str(row + 4)
		loc44 = 'E' + str(row + 4)
		loc54 = 'F' + str(row + 4)
		loc64 = 'G' + str(row + 4)
		loc74 = 'H' + str(row + 4)
		loc84 = 'I' + str(row + 4)
		loc94 = 'J' + str(row + 4)
		loc104 = 'K' + str(row + 4)
		loc114 = 'L' + str(row + 4)

		end_14 = str(loc4) + ':' + str(loc14)
		end_24 = str(loc24) + ':' + str(loc34)
		end_34 = str(loc44) + ':' + str(loc54)
		end_44 = str(loc64) + ':' + str(loc94)
		end_54 = str(loc84) + ':' + str(loc94)
		end_64 = str(loc104) + ':' + str(loc114)

		worksheet.merge_range(str(end_14), str("{0:.2f}".format(unittotal - total)), main_heading)
		worksheet.merge_range(str(end_24), 'Discount Amount', main_heading)
		worksheet.merge_range(str(end_34), 'القيمه‬ بعد‬ الخصم‬', main_heading)
		worksheet.merge_range(str(end_44), str(number_to_spell(net)), main_heading)
		worksheet.merge_range(str(end_64), str(lines.internal_note), main_heading)

		loc5 = 'A' + str(row + 5)
		loc15 = 'B' + str(row + 5)
		loc25 = 'C' + str(row + 5)
		loc35 = 'D' + str(row + 5)
		loc45 = 'E' + str(row + 5)
		loc55 = 'F' + str(row + 5)
		loc65 = 'G' + str(row + 5)
		loc75 = 'H' + str(row + 5)
		loc85 = 'I' + str(row + 5)
		loc95 = 'J' + str(row + 5)
		loc105 = 'K' + str(row + 5)
		loc115 = 'L' + str(row + 5)

		end_15 = str(loc5) + ':' + str(loc15)
		end_25 = str(loc25) + ':' + str(loc35)
		end_35 = str(loc45) + ':' + str(loc55)
		end_45 = str(loc65) + ':' + str(loc95)
		end_55 = str(loc85) + ':' + str(loc95)
		end_65 = str(loc105) + ':' + str(loc115)

		worksheet.merge_range(str(end_15), str("{0:.2f}".format(total)), main_heading)
		worksheet.merge_range(str(end_25), 'Amount After Discount', main_heading)
		worksheet.merge_range(str(end_35), 'ضريبه‬ القيمه‬ المضافه‬', main_heading)
		worksheet.merge_range(str(end_45), ' ', main_heading)
		worksheet.merge_range(str(end_55), ' ', main_heading)
		worksheet.merge_range(str(end_65), ' ', main_heading)

		loc6 = 'A' + str(row + 6)
		loc16 = 'B' + str(row + 6)
		loc26 = 'C' + str(row + 6)
		loc36 = 'D' + str(row + 6)
		loc46 = 'E' + str(row + 6)
		loc56 = 'F' + str(row + 6)
		loc66 = 'G' + str(row + 6)
		loc76 = 'H' + str(row + 6)
		loc86 = 'I' + str(row + 6)
		loc96 = 'J' + str(row + 6)
		loc106 = 'K' + str(row + 6)
		loc116 = 'L' + str(row + 6)

		end_16 = str(loc6) + ':' + str(loc16)
		end_26 = str(loc26) + ':' + str(loc36)
		end_36 = str(loc46) + ':' + str(loc56)
		end_46 = str(loc66) + ':' + str(loc96)
		end_56 = str(loc86) + ':' + str(loc96)
		end_66 = str(loc106) + ':' + str(loc116)

		worksheet.merge_range(str(end_16), str("{0:.2f}".format(tax)), main_heading)
		worksheet.merge_range(str(end_26), 'Tax Amount', main_heading)
		worksheet.merge_range(str(end_36), 'اجمالي‬ المستحق‬', main_heading)
		worksheet.merge_range(str(end_46), ' ', main_heading)
		worksheet.merge_range(str(end_56), ' ', main_heading)
		worksheet.merge_range(str(end_66), ' ', main_heading)

		loc7 = 'A' + str(row + 6)
		loc17 = 'B' + str(row + 6)
		loc27 = 'C' + str(row + 6)
		loc37 = 'D' + str(row + 6)
		loc47 = 'E' + str(row + 6)
		loc57 = 'F' + str(row + 6)
		loc67 = 'G' + str(row + 6)
		loc77 = 'H' + str(row + 6)
		loc87 = 'I' + str(row + 6)
		loc97 = 'J' + str(row + 6)
		loc107 = 'K' + str(row + 6)
		loc117 = 'L' + str(row + 6)

		end_17 = str(loc7) + ':' + str(loc17)
		end_27 = str(loc27) + ':' + str(loc37)
		end_37 = str(loc47) + ':' + str(loc57)
		end_47 = str(loc67) + ':' + str(loc97)
		end_57 = str(loc87) + ':' + str(loc97)
		end_67 = str(loc107) + ':' + str(loc117)

		worksheet.merge_range(str(end_17), str("{0:.2f}".format(net)), main_heading)
		worksheet.merge_range(str(end_27), 'Net Amount', main_heading)
		worksheet.merge_range(str(end_37), 'اجمالي‬ المستحق‬', main_heading)
		worksheet.merge_range(str(end_47), ' ', main_heading)
		worksheet.merge_range(str(end_57), ' ', main_heading)
		worksheet.merge_range(str(end_67), ' ', main_heading)

		







		
