#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, models
from num2words import num2words
import base64
import re


class Reportmonthcollection(models.AbstractModel):
	_name = 'report.bassami_collection_report.purchase_order_report_report'
	_description = "Report"

	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['account.collection'].browse(docids)
		user = self.env['res.users'].search([('id','=',self._uid)])
		def number_to_spell(attrb):
			word = num2words((attrb))
			word = word.title() + " " + "SAR Only"
			return word

		lang_id = 0
		user_id = self.env['res.users'].search([('id','=',self._uid)])
		if user_id.lang != 'en_US':
			lang_id = 1
		# def get_prf(attr,ids):
		# 	amt = 0
		# 	prf = self.env['purchase.req.rec.line'].search([('product_id.id','=',attr),('preq_rec.state','!=','done'),('id','!=',ids)])
		# 	for x in prf:
		# 		amt = amt + x.qty
		# 	return amt
		# def get_po(attr):
		# 	amt = 0
		# 	po = self.env['purchase.order.line'].search([('product_id.id','=',attr),('order_id.state','=',('draft','sent'))])
		# 	for x in po:
		# 		amt = amt + x.product_qty
		# 	return amt

		return {
		'doc_ids': docids,
		'doc_model':'account.collection',
		'data': data,
		'docs': docs,
		'user': user,
		'number_to_spell':number_to_spell,
		'lang_id':lang_id,
		# 'get_prf': get_prf,
		# 'get_po': get_po,
	}


