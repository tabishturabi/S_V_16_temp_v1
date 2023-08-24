# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class OtherServiceItems(models.Model):
	_name = 'other_service_items'
	_description = "Other Service Items"

	# 
	@api.depends('cost', 'tax_ids')
	def _get_price(self):
		self.tax_amount = 0
		if self.product_id:
			if self.tax_ids:
				currency = self.currency_id or None
				quantity = 1
				product = self.product_id
				taxes = self.tax_ids.compute_all((self.cost), currency, quantity,
												 product=product)#, partner=self.cargo_sale_id.customer_id
				self.tax_amount = taxes['total_included'] - taxes['total_excluded']

	# 
	@api.depends('tax_amount','cost')
	def _get_without_tax_price(self):
		self.without_tax_amount = 0
		if self.tax_amount:
			self.without_tax_amount = self.cost
		else:
			self.without_tax_amount = self.cost

	@api.onchange('product_id')
	def _onchange_amont(self):
		if self.product_id and not (self.cargo_sale_id.loc_from.is_international or self.cargo_sale_id.loc_to.is_international):
			self.tax_ids = [(6,0,self.product_id.taxes_id.ids)]   


	# Get Other Service Invoice Status
	# 
	def _other_service_invoice_state(self):
		for rec in self:
			rec.is_other_service_status = False
			other_service_invoice = self.env['account.move'].search([('other_service_line_id','=',rec.id),('is_other_service_invoice','=',True)],limit=1)
			if other_service_invoice:
				if other_service_invoice.payment_state == 'paid':
					rec.is_other_service_status = True
				else:
					rec.is_other_service_status = False

	@api.model
	def default_get(self, fields):
		result = super(OtherServiceItems, self).default_get(fields)
		if self.env.user.has_group('payments_enhanced.group_allowed_pay_with_fc'):
			result.update({
				'is_allow_pay_with_fc' : True,
				})
		else:
			result.update({
				'is_allow_pay_with_fc' : False,
				})
		return result		 
		
	product_id = fields.Many2one('product.product',string="Other Services",domain="[('type', '=', 'service'),('is_international','=',True)]")
	cost = fields.Float(string="Price")
	qty = fields.Float(string="Qty")
	description = fields.Text(string="Desription")
	cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale',string="Cargo Sale ID")
	tax_ids = fields.Many2many('account.tax', string="Taxes")
	tax_amount = fields.Float(compute='_get_price', digits=dp.get_precision('Cargo Sale'))
	without_tax_amount = fields.Float(compute="_get_without_tax_price", digits=dp.get_precision('Cargo Sale'))
	is_invoice_create = fields.Boolean(string="Is Invoice Created")	

	is_other_service_invoice = fields.Boolean(string="Is Other Service Invoice")
	is_other_service_status = fields.Boolean(string="Is Other Service", compute="_other_service_invoice_state")
	cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line',string="Cargo Sale Line",required=True)
	currency_id = fields.Many2one(string="Currency", comodel_name="res.currency",
                                          default=lambda self: self.env.user.company_id.currency_id.id)
	is_allow_pay_with_fc = fields.Boolean(string="Is Allowed Payment With FC")
    										  
	
	@api.onchange('cargo_sale_id')
	def _onchange_cargo_sale_id(self):
		if self.cargo_sale_id:
			if not self.cargo_sale_line_id:
				if len(self.cargo_sale_id.order_line_ids.ids) == 1:
					self.cargo_sale_line_id = self.cargo_sale_id.order_line_ids[0].id

	# Register Payment For other Services
	
	def other_serive_register_payment(self):
		view_id = self.env.ref('account.view_account_payment_register_form').id
		journal_id = self.env['account.journal'].search([('type', '=', 'cash')], limit=1)
		if not journal_id:
			raise UserError(_("There is no cash journal defined please define in accounting."))
		other_service_invoice = self.env['account.move'].search([('other_service_line_id','=',self.id),('is_other_service_invoice','=',True)],limit=1)
		return {
			'type': 'ir.actions.act_window',
			'name': 'Name',
			'view_mode': 'form',
			'view_type': 'form',
			'res_model': 'account.payment',
			'view_id': view_id,
			'target': 'new',
			'context': {
				'default_payment_type': 'inbound',
				'default_partner_id': self.cargo_sale_id.customer.id,
				'default_partner_type': 'customer',
				'default_amount': other_service_invoice.amount_residual,
				'default_communication': self.cargo_sale_id.name,
				'default_show_invoice_amount': False,
				'default_invoice_ids': [(4, other_service_invoice.id, None)]
			}
		}

	#for creating other service invoice
	
	def create_other_serive_invoice(self):
		if self.cost == 0:
			raise UserError(
					_('You can not create invoice with Price 0 ...!'),
				)
		inv_obj = self.env['account.move']
		inv_line_obj = self.env['account.move.line']
		inv_data = self.cargo_sale_id.with_context({'other_service_line_id' : self.id})._prepare_invoice_for_other_service()
		invoice = inv_obj.create(inv_data)
		line_name = str(self.cargo_sale_line_id.name) + '-' + str(self.description if self.description else "Other Service")
		inv_line_obj.create(self.cargo_sale_id._prepare_invoice_line(invoice.id, self.product_id.property_account_income_id.id,
							line_name, self.cost, False,
						   	self.tax_ids if self.tax_ids else False, False, self.product_id.id))
		invoice._compute_amount()
		invoice.action_post()
		self.write({'is_other_service_invoice' : True})
	#restcit user to delete if state not in draft
	
	def unlink(self):
		"""
			Delete all record(s) from table heaving record id in ids
			return True on success, False otherwise

			@return: True on success, False otherwise
		"""
		for rec in self:
			if rec.is_invoice_create:
				raise UserError(
					_('You can not delete a Created Invoice record...!!!'),
				)
			if self.env.user.id != rec.create_uid.id and not self.env.user.has_group('account.group_account_manager'):	
				raise UserError(
					_('You Are Not Autherize To Delete This Record...!!!'),
				)
		return super(OtherServiceItems, self).unlink()
