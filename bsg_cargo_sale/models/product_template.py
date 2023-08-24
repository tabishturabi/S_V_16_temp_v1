# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class bsg_inherit_product_template(models.Model):
	_inherit = 'product.template'

	is_satah = fields.Boolean(string="Is Satah ?")
	satah_line_ids = fields.One2many(string="Satah Line Ids", comodel_name="bsg_product_satah_line", inverse_name="prod_tmpl_id")

	
	@api.constrains('is_satah')
	def _check_is_satah(self):
		Res = self.search([('is_satah','=',True)])
		if self.is_satah:
			if Res:
				raise UserError(
					_('There will be only one product of satah you cant create a new one..!'),
				)

	@api.model
	def create(self, values):
		"""
			Create a new record for a model bsg_inherit_product_template
			@param values: provides a data for new record

			@return: returns a id of new record
		"""
		res = super(bsg_inherit_product_template, self).create(values)
		if res.is_satah:
			satah_product = self.env['product.template'].search([('is_satah','=',True)])
			if satah_product:
				raise UserError(
					_('There will be only one product of satah you cant create a new one..!'),
				)
		return res

class BsgProdSatahLine(models.Model):
	_name = 'bsg_product_satah_line'
	_description = "Satah Product Line"

	from_km = fields.Float('From KM')
	to_km = fields.Float('To KM')
	price = fields.Float(string="Price")
	satah_type = fields.Selection(string="Satah Type", selection=[
	('satah_big','Satah Big'),
	('satah_small','Satah Small')
	], default="")
	prod_tmpl_id = fields.Many2one(string="Product Template ID", comodel_name="product.template")


	_sql_constraints = [
	    ('satah_type_uniq', 'unique (satah_type, prod_tmpl_id)', _('The satah_type must be unique !')),
	]