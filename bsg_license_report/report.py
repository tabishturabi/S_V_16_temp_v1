import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
import re
import pandas as pd
import numpy as np
import psycopg2 as pg
import pandas.io.sql as psql
import getpass
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from odoo.tools import config
import base64
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import string
from ummalqura.hijri_date import HijriDate
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT



class BranchLicenseReportXlsx(models.TransientModel):
	_name = 'report.bsg_license_report.bsg_license_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	# @api.multi
	def generate_xlsx_report(self, workbook, input_records, lines):
		data = input_records['form']

		trans_ids = self.env['bsg.license.info'].search([])

		if data['doc_type']:
			trans_ids = trans_ids.filtered(lambda l: l.doc_type.id in data['doc_type'])

		if data['branch_ids']:
			trans_ids = trans_ids.filtered(lambda l: l.branch_id.id in data['branch_ids'])

		if data['filter_type'] == "By Issue Date":
			if data['date_type'] == "is equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.issue_date) == data['date'])
			if data['date_type'] == "is not equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.issue_date) != data['date'])
			if data['date_type'] == "is after":
				trans_ids = trans_ids.filtered(lambda l: str(l.issue_date) > data['date'])
			if data['date_type'] == "is before":
				trans_ids = trans_ids.filtered(lambda l: str(l.issue_date) < data['date'])
			if data['date_type'] == "is after or equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.issue_date) >= data['date'])
			if data['date_type'] == "is before or equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.issue_date) <= data['date'])
			if data['date_type'] == "is between":
				trans_ids = trans_ids.filtered(lambda l: str(l.issue_date) >= data['form'] and str(l.issue_date) <= data['to'])
			if data['date_type'] == "is set":
				trans_ids = trans_ids.filtered(lambda l: l.issue_date != False)
			if data['date_type'] == "is not set":
				trans_ids = trans_ids.filtered(lambda l: l.issue_date == False)

		if data['filter_type'] == "By Expiry Date":
			if data['date_type'] == "is equal to":
				record = isinstance(data['date'], str) and datetime.strptime(data['date'],
																			 DEFAULT_SERVER_DATE_FORMAT).date() or data[
							 'date']
				trans_ids = trans_ids.filtered(
					lambda l: (not isinstance(l.expiry_date, date) and l.expiry_date.date() or l.expiry_date) == record)
			if data['date_type'] == "is not equal to":
				record = isinstance(data['date'], str) and datetime.strptime(data['date'],
																			 DEFAULT_SERVER_DATE_FORMAT).date() or data[
							 'date']
				trans_ids = trans_ids.filtered(
					lambda l: (not isinstance(l.expiry_date, date) and l.expiry_date.date() or l.expiry_date) != record)
			if data['date_type'] == "is after":
				record = isinstance(data['date'], str) and datetime.strptime(data['date'],
																			 DEFAULT_SERVER_DATE_FORMAT).date() or data[
							 'date']
				trans_ids = trans_ids.filtered(
					lambda l: (not isinstance(l.expiry_date, date) and l.expiry_date.date() or l.expiry_date) > record)
			if data['date_type'] == "is before":
				record = isinstance(data['date'], str) and datetime.strptime(data['date'],
																			 DEFAULT_SERVER_DATE_FORMAT).date() or data[
							 'date']
				trans_ids = trans_ids.filtered(
					lambda l: (not isinstance(l.expiry_date, date) and l.expiry_date.date() or l.expiry_date) < record)
			if data['date_type'] == "is after or equal to":
				record = isinstance(data['date'], str) and datetime.strptime(data['date'],
																			 DEFAULT_SERVER_DATE_FORMAT).date() or data[
							 'date']
				trans_ids = trans_ids.filtered(
					lambda l: (not isinstance(l.expiry_date, date) and l.expiry_date.date() or l.expiry_date) >= record)
			if data['date_type'] == "is before or equal to":
				record = isinstance(data['date'], str) and datetime.strptime(data['date'],
																			 DEFAULT_SERVER_DATE_FORMAT).date() or data[
							 'date']
				trans_ids = trans_ids.filtered(
					lambda l: (not isinstance(l.expiry_date, date) and l.expiry_date.date() or l.expiry_date) <= record)
			if data['date_type'] == "is between":
				trans_ids = trans_ids.filtered(
					lambda l: str(l.expiry_date) >= data['form'] and str(l.expiry_date) <= data['to'])
			if data['date_type'] == "is set":
				record = isinstance(data['date'], str) and datetime.strptime(data['date'],
																			 DEFAULT_SERVER_DATE_FORMAT).date() or data[
							 'date']
				trans_ids = trans_ids.filtered(
					lambda l: (not isinstance(l.expiry_date, date) and l.expiry_date.date() or l.expiry_date) != record)
			if data['date_type'] == "is not set":
				record = isinstance(data['date'], str) and datetime.strptime(data['date'],
																			 DEFAULT_SERVER_DATE_FORMAT).date() or data[
							 'date']
				trans_ids = trans_ids.filtered(
					lambda l: (not isinstance(l.expiry_date, date) and l.expiry_date.date() or l.expiry_date) == record)


		if data['filter_type'] == "By Due To Renewal":
			if data['date_type'] == "is equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.renewal) == data['date'])
			if data['date_type'] == "is not equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.renewal) != data['date'])
			if data['date_type'] == "is after":
				trans_ids = trans_ids.filtered(lambda l: str(l.renewal) > data['date'])
			if data['date_type'] == "is before":
				trans_ids = trans_ids.filtered(lambda l: str(l.renewal) < data['date'])
			if data['date_type'] == "is after or equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.renewal) >= data['date'])
			if data['date_type'] == "is before or equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.renewal) <= data['date'])
			if data['date_type'] == "is between":
				trans_ids = trans_ids.filtered(lambda l: str(l.renewal) >= data['form'] and str(l.renewal) <= data['to'])
			if data['date_type'] == "is set":
				trans_ids = trans_ids.filtered(lambda l: l.renewal != False)
			if data['date_type'] == "is not set":
				trans_ids = trans_ids.filtered(lambda l: l.renewal == False)


		if data['filter_type'] == "By Latest Renewal Date":
			if data['date_type'] == "is equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.latest_renewal_date) == data['date'])
			if data['date_type'] == "is not equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.latest_renewal_date) != data['date'])
			if data['date_type'] == "is after":
				trans_ids = trans_ids.filtered(lambda l: str(l.latest_renewal_date) > data['date'])
			if data['date_type'] == "is before":
				trans_ids = trans_ids.filtered(lambda l: str(l.latest_renewal_date) < data['date'])
			if data['date_type'] == "is after or equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.latest_renewal_date) >= data['date'])
			if data['date_type'] == "is before or equal to":
				trans_ids = trans_ids.filtered(lambda l: str(l.latest_renewal_date) <= data['date'])
			if data['date_type'] == "is between":
				trans_ids = trans_ids.filtered(lambda l: str(l.latest_renewal_date) >= data['form'] and str(l.latest_renewal_date) <= data['to'])
			if data['date_type'] == "is set":
				trans_ids = trans_ids.filtered(lambda l: l.latest_renewal_date != False)
			if data['date_type'] == "is not set":
				trans_ids = trans_ids.filtered(lambda l: l.latest_renewal_date == False)


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
			"align": 'right',
			"valign": 'vcenter',
			"font_color":'black',
			"bg_color": '#D3D3D3',
			'font_size': '10',
			})

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
		worksheet = workbook.add_worksheet('Branch License Report')

		letters = list(string.ascii_uppercase)

		worksheet.merge_range('A1:G1',"Branch License Report",merge_format)

		worksheet.set_column('A:AZ', 18)

		if data['report_mode'] == "Document Type":

			worksheet.write('A3', 'Branch Name', main_heading1)
			worksheet.write('B3', 'Document No', main_heading1)
			worksheet.write('C3', 'Issue Date', main_heading1)
			worksheet.write('D3', 'Issue Date Hijri', main_heading1)
			worksheet.write('E3', 'Expiry Date', main_heading1)
			worksheet.write('F3', 'Expiry Date Hijri', main_heading1)
			worksheet.write('G3', 'Latest Renewal Date', main_heading1)
			worksheet.write('H3', 'Due for Renewal', main_heading1)
			worksheet.write('I3', 'Attachment', main_heading1)
			worksheet.write('J3', 'Comment', main_heading1)

			worksheet.write('A4', 'الفرع', main_heading1)
			worksheet.write('B4', 'رقم السجل', main_heading1)
			worksheet.write('C4', ' تاريخ الاصدار', main_heading1)
			worksheet.write('D4', 'تاريخ الإصدار هجري', main_heading1)
			worksheet.write('E4', 'تاريخ الانتهاء', main_heading1)
			worksheet.write('F4', 'تاريخ الإنتهاء هجري', main_heading1)
			worksheet.write('G4', 'آخر موعد للتجديد', main_heading1)
			worksheet.write('H4', ' ', main_heading1)
			worksheet.write('I4', 'المرفق', main_heading1)
			worksheet.write('J4', 'تعليق', main_heading1)


			worksheet.set_column('A:G', 18)


			docs_data = []
			for doc in trans_ids:
				if doc.doc_type not in docs_data:
					docs_data.append(doc.doc_type)



			row = 4
			col = 0

			for rec in docs_data:

				worksheet.write_string (row, col,str("Document Type"),main_heading1)
				worksheet.write_string (row, col+1,str(rec.branch_doc_type),main_data)

				row = row + 1
				col = 0

				doc_ids = trans_ids.filtered(lambda l: l.doc_type.id == rec.id)

				for  line in doc_ids:

					worksheet.write_string (row, col,str(line.branch_id.branch_ar_name),main_data)
					worksheet.write_string (row, col+1,str(line.document_no),main_data)
					worksheet.write_string (row, col+2,str(line.issue_date),main_data)
					worksheet.write_string (row, col+3,str(HijriDate.get_hijri_date(line.issue_date)),main_data)
					worksheet.write_string (row, col+4,str(line.expiry_date),main_data)
					worksheet.write_string (row, col+5,str(HijriDate.get_hijri_date(line.expiry_date)),main_data)
					worksheet.write_string (row, col+6,str(line.latest_renewal_date),main_data)
					worksheet.write_string (row, col+7,str(line.renewal),main_data)
					worksheet.write_string (row, col+8,len(line.attachment_ids) == 1 and str(line.attachment_ids.name) or ' , '.join(line.attachment_ids.mapped('name')) ,main_data)
					if line.comment:
						worksheet.write_string(row, col +9,str(line.comment), main_data)


					row += 1

				row += 1


		if data['report_mode'] == "All Details":

			docs_data = []
			for doc in trans_ids:
				if doc.doc_type not in docs_data:
					docs_data.append(doc.doc_type)


			branch_data = []
			for doc in trans_ids:
				if doc.branch_id not in branch_data:
					branch_data.append(doc.branch_id)


			arbic_list = ['رقم السجل','تاريخ الاصدار','تاريخ الإصدار هجري','تاريخ الانتهاء','تاريخ الإنتهاء هجري','آخر موعد للتجديد','المرفق']

			eng_list = ['Document No','Issue Date','Issue Date Hijri','Expiry Date','Expiry Date Hijri','Latest Renewal Date','Attachment']

			worksheet.write('A5',  'الفرع', main_heading1)
			worksheet.write('A6',  'Branch Name', main_heading1)

			colums = 1
			for s in docs_data:
				new = colums + 6
				worksheet.merge_range(3,colums,3,new,str(s.branch_doc_type),main_heading)
				colums = colums + 7

			aipha_w = 1
			for t in docs_data:
				for w in arbic_list:
					worksheet.write(4,aipha_w,str(w),main_heading)
					aipha_w += 1

			aipha_w = 1
			for t in docs_data:
				for w in eng_list:
					worksheet.write(5,aipha_w,str(w),main_heading)
					aipha_w += 1

			row = 6
			col = 0

			for br in branch_data:

				worksheet.write_string (row, col,str(br.branch_ar_name),main_data)

				row += 1

			row = 6
			col = 1

			for rec in docs_data:


				doc_data = []
				for br in branch_data:
					doc_ids = trans_ids.filtered(lambda l: l.doc_type.id == rec.id and l.branch_id.id == br.id)
					if doc_ids:
						doc_ids = doc_ids[0]
						doc_data.append({
							'document_no':doc_ids.document_no,
							'issue_date':doc_ids.issue_date and doc_ids.issue_date or '',
							'expiry_date':doc_ids.expiry_date and doc_ids.expiry_date or '',
							'latest_renewal_date':doc_ids.latest_renewal_date,
							'attachment_ids': len(doc_ids.attachment_ids) ==1 and doc_ids.attachment_ids.name or ' , '.join(doc_ids.attachment_ids.mapped('name')),
							})
					else:
						doc_data.append({
							'document_no':" ",
							'issue_date':" ",
							'expiry_date':" ",
							'latest_renewal_date':" ",
							'attachment_ids':" ",
							})


				for  line in doc_data:
					hijri_issue = line['issue_date'] != ' ' and  HijriDate.get_hijri_date(line['issue_date']) or ''
					hijri_expiry = line['expiry_date'] != ' ' and HijriDate.get_hijri_date(line['expiry_date']) or ''
					worksheet.write_string (row, col,str(line['document_no']),main_data)
					worksheet.write_string (row, col+1,str(line['issue_date']),main_data)
					worksheet.write_string (row, col+2,str(hijri_issue),main_data)
					worksheet.write_string (row, col+3,str(line['expiry_date']),main_data)
					worksheet.write_string (row, col+4,str(hijri_expiry),main_data)
					worksheet.write_string (row, col+5,str(line['latest_renewal_date']),main_data)
					worksheet.write_string (row, col+6,str(line['attachment_ids']),main_data)


					row += 1


				col += 7
				row = 6



















