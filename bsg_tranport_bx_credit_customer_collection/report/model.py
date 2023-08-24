#-*- coding:utf-8 -*-

from odoo import api, models
from num2words import num2words
import base64
import re


class ReportBxInvoice(models.AbstractModel):
	_name = 'report.bsg_tranport_bx_credit_customer_collection.b_coll'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['bx.credit.customer.collection'].browse(docids)
		user = self.env['res.users'].search([('id','=',self._uid)])
		def number_to_spell(attrb):
			word = num2words((attrb))
			word = word.title() + " " + "SAR Only"
			return word

		report_value = 0

		lang_id = 0
		user_id = self.env['res.users'].search([('id','=',self._uid)])
		if user_id.lang != 'en_US':
			lang_id = 1

		cust_info = []
		if docs.invoice_to:
			cust_info = docs.invoice_to
		else:
			cust_info = docs.customer_id


		cargo_ids = []
		for d in docs.transport_management_ids:
			cargo_ids.append(d)


	
		cargo_ids = sorted(cargo_ids, key=lambda k: k.bx_credit_sequnce)

		num_of_recs = len(cargo_ids)


		price = 0
		tax_amount = 0
		total_amount = 0
		for tot in cargo_ids:
			price = price + tot.price
			tax_amount = tax_amount + tot.tax_amount
			total_amount = total_amount + tot.total_amount

		# if lang_id == 0:
		def get_cargo_ids(attr):
			len_check = 18 * int(attr)
			if len(cargo_ids) <= len_check:
				start_range = int(len_check - 18)
				return cargo_ids[start_range:]
			if len(cargo_ids) > len_check:
				start_range = int(len_check - 18)
				return cargo_ids[start_range:len_check]


		check_loops = len(cargo_ids) % 18
		

		runing_loop = 1
		exact_loop = 1
		if cargo_ids:
			runing_loop = float(int(len(cargo_ids)) / 18)
			runing_loop = format(runing_loop, '.2f')
			runing_loop = float(runing_loop)
			txt = str(runing_loop)
			txt = (txt.split("."))
			txt = int(txt[-1])
			if txt > 50 or txt == 0:
				report_value = 1
				int_value = int(runing_loop)
				if runing_loop > int_value:
					exact_loop = int_value + 2
				else:
					exact_loop = int_value + 1

			else:
				report_value = 2
				int_value = int(runing_loop)
				if runing_loop > int_value:
					exact_loop = int_value + 1
				else:
					exact_loop = int_value


		

		page_numz = []
		for ex in range(exact_loop):
			page_numz.append(ex+1)


		return {
		'doc_ids': docids,
		'doc_model':'bx.credit.customer.collection',
		'data': data,
		'docs': docs,
		'user': user,
		'number_to_spell':number_to_spell,
		'lang_id':lang_id,
		'cargo_ids':cargo_ids,
		'page_numz':page_numz,
		'get_cargo_ids':get_cargo_ids,
		'exact_loop':exact_loop,
		'cust_info':cust_info,
		'num_of_recs':num_of_recs,
		'price':price,
		'tax_amount':tax_amount,
		'total_amount':total_amount,
		'report_value':report_value,
	}


	