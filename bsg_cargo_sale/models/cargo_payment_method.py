# -*- coding: utf-8 -*-

from odoo import models, fields, api

class cargo_payment_method(models.Model):
	_name = 'cargo_payment_method'
	_description = "Payment Method"
	_inherit = ['mail.thread']
	_rec_name = 'payment_method_name'

	code = fields.Char(string='Code', required=False)
	payment_method_name = fields.Char(string="Payment Method Name")
	partner_type_id = fields.Many2one('partner.type', string="Partner Type")
	extra_charges = fields.Float(string="Extra Charges",default=0.0)
	payment_type = fields.Selection(
		[
			('cash', 'Cash'),
			('credit', 'Credit'),
			('pod', 'Payment On Delivery'),
			('bank', 'Bank Transfer'),
		], string='Payment Type' )
class BsgAccountPayment(models.TransientModel):
	# _inherit = 'account.payment'
	# # Migration Note
	_inherit = 'account.payment.register'

	@api.model
	def default_get(self, fields):
		result = super(BsgAccountPayment, self.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id)).default_get(fields)
		active_ids = self._context.get('active_ids')
		active_model = self._context.get('active_model')
		if active_model == 'account.move':
			inv = self.env['account.move'].browse(active_ids)
			if inv.reversed_entry_id.cargo_sale_id:
				result.update({
					'cargo_sale_order_id':inv.reversed_entry_id.cargo_sale_id.id,
					'is_for_refund' : True,
					#'is_show_partial' : True,
					'cancel_amt' : result['amount'] - inv.single_trip_reason.stc_value,
					'cargo_sale_line_order_ids': inv.invoice_line_ids.filtered(lambda s: not s.is_paid).mapped('cargo_sale_line_id.id'),
					})
				if inv.single_trip_reason.stc_value == 0:
					result.update({'is_show_partial' : True})
			elif inv.cargo_sale_id:
				result.update({'cargo_sale_order_id':inv.cargo_sale_id.id,
							 	'cargo_sale_line_order_ids': inv.invoice_line_ids.filtered(lambda s: not s.is_paid).mapped('cargo_sale_line_id.id'),
								 'is_show_partial' : True})	

		elif self._context.get('default_amount_return_cargo_invoice'):
			inv = self.env['account.move'].browse(self._context.get('default_return_invoice_id'))
			result.update({
				'cancel_amt' : result['amount'] - inv.single_trip_reason.stc_value
				})
		if self.env.user.has_group('account.group_account_manager') or self.env.user.has_group('account.group_account_user'):
			result.update({
				'allow_edit_in_wiz' : True,
				})
		else:		
			result.update({
				'allow_edit_in_wiz' : False,
				})
		return result

	multi_invoice = fields.Boolean()
	is_allow_pay_with_fc = fields.Boolean(string="Is Allowed Payment With FC")
	show_communication_field = fields.Boolean()
	operation_number = fields.Char(string="Operation Number")
	attachment_id = fields.Binary(string="Attachment")

	is_new_order = fields.Boolean()
	cargo_sale_order_id = fields.Many2one(string="Cargo Sale ID", comodel_name="bsg_vehicle_cargo_sale", copy=False)
	cancel_amt = fields.Float(string='Cancel Amount')
	is_cancel = fields.Boolean(string='Is Cancelation', compute="_check_cancelation")
	bsg_vehicle_cargo_sale_line_ids = fields.One2many('account.cargo.line.payment','account_payment_id', string='So Line Payment')
	residual_amount = fields.Float(compute='_compute_residual_amount',store=True)
	cargo_sale_line_order_ids = fields.Many2many(string="Cargo Sale Lines", comodel_name="bsg_vehicle_cargo_sale_line", copy=False)
	is_from_cargo_line = fields.Boolean('From Cargo Line')
	is_for_old_order = fields.Boolean('Is Old Order',related='cargo_sale_order_id.is_old_order',store=True)
	is_show_partial = fields.Boolean(string="IS Enable Partial Payment")
	allow_edit_in_wiz = fields.Boolean()
	is_for_refund = fields.Boolean()
	


	@api.onchange('cargo_sale_line_order_ids')
	def _onchange_cargo_sale_line_order_ids(self):
		if self.cargo_sale_line_order_ids and not self.cargo_sale_order_id.is_old_order:
			payment_line = []
			self.bsg_vehicle_cargo_sale_line_ids = False
			invoice_id = []
			invoice_ids = []
			if not self.env.context.get('default_invoice_ids'):
				invoice_id = self.env['account.move'].browse(self.env.context.get('active_ids')).ids
			else:
				invoice_ids = self.env.context.get('default_invoice_ids')
				for record in invoice_ids:
					invoice_id.append(record[1])
			invoice_ids = self.env['account.move'].browse(invoice_id)
			for line in self.cargo_sale_line_order_ids:
				for inv_line in invoice_ids.filtered(lambda s:s.state == 'posted').mapped('invoice_line_ids').filtered(lambda s: s.cargo_sale_line_id.id == line.id.origin and not s.is_paid):
					payment_line.append({
							'cargo_sale_line_id':line.id,
							'total': inv_line.price_total,
							'account_invoice_line_id': inv_line.id,
							'amount' : inv_line.price_total - inv_line.paid_amount,
							'residual' : inv_line.price_total - inv_line.paid_amount,
						})
			self.bsg_vehicle_cargo_sale_line_ids = [(0, 0, pay_line)for pay_line in payment_line]
		else:
			self.bsg_vehicle_cargo_sale_line_ids = False

	@api.onchange('bsg_vehicle_cargo_sale_line_ids')
	def _onchange_bsg_vehicle_cargo_sale_line_ids(self):
		self.cargo_sale_line_order_ids = self.bsg_vehicle_cargo_sale_line_ids.mapped('cargo_sale_line_id')

		if self.cargo_sale_order_id:
			if self.cargo_sale_order_id.is_old_order:
				self.amount = sum(self.invoice_ids.mapped('amount_residual'))
			else:
				self.communication = ''	
				self.amount = sum(self.bsg_vehicle_cargo_sale_line_ids.mapped('currency_amount'))
				for desc in self.bsg_vehicle_cargo_sale_line_ids.mapped('account_invoice_line_id.name'):
					self.communication += str(desc +" ")

			if self.is_for_refund:
				active_id = self._context.get('active_id')
				active_model = self._context.get('active_model')
				if active_model == 'account.move':
					inv = self.env['account.move'].browse(active_id)
				elif self._context.get('default_amount_return_cargo_invoice'):
					inv = self.env['account.move'].browse(self._context.get('default_return_invoice_id'))
				if inv:
					self.cancel_amt = self.amount - inv.single_trip_reason.stc_value
					self.amount = self.amount - inv.single_trip_reason.stc_value		
		
	
	@api.depends('bsg_vehicle_cargo_sale_line_ids','line_ids.move_id','amount')
	def _compute_residual_amount(self):
		for rec in self:
			amount = 0
			rec.residual_amount = 0
			for caro_payment_line in rec.bsg_vehicle_cargo_sale_line_ids:
				amount += caro_payment_line.account_invoice_line_id.move_id.currency_id._convert(
				caro_payment_line.amount, rec.currency_id, self.env.user.company_id, fields.Date.today())
			rec.residual_amount = rec.amount - amount

		

	#def action_valiinvoice_date_payment(self):
   	#	if self.cargo_sale_order_id:
	#		self.cargo_sale_order_id.update({'state' : 'done'})
	#	return super(bsg_inherit_account_payment, self).action_valiinvoice_date_payment()


	# @api.depends('cancel_amt')
	# def _check_cancelation(self):
	# 	# Need Improvement .... exceptions are not handled....!
	# 	for rec in self:
	# 		rec.residual_amount = 0
	# 		rec.amount = 0
	# 		rec.is_cancel = False
	# 		# rec.payment_difference_handling = ''
	# 		# rec.writeoff_account_id = False
	# 		cargo_sale_id = False
	# 		if rec._context.get('active_model') == 'bsg_vehicle_cargo_sale':
	# 			cargo_sale_id = rec.env['bsg_vehicle_cargo_sale'].browse(rec._context.get('active_id'))
	# 		if rec._context.get('active_model') == 'account.move':
	# 			cargo_sale_id = rec.env['account.move'].browse(rec._context.get('active_ids'))
	# 			cargo_sale_id = cargo_sale_id.cargo_sale_id
	# 		if rec.cancel_amt > 0:
	# 			rec.is_cancel = True
	# 			rec.amount = rec.cancel_amt
	# 			active_id = rec._context.get('active_ids')
	# 			active_model = rec._context.get('active_model')
	# 			if rec._context.get('active_model') == 'bsg_vehicle_cargo_sale':
	# 				inv = rec.env['account.move'].browse(rec._context.get('default_return_invoice_id'))
	# 			else:
	# 				inv = rec.env['account.move'].browse(active_id)
	# 			# if inv.single_trip_reason.stc_value != 0:
	# 			# 	rec.payment_difference_handling = 'reconcile'
	# 			# if inv.single_trip_reason.stc_account_id:
	# 			# 	rec.writeoff_account_id = inv.single_trip_reason.stc_account_id.id

	@api.depends('cancel_amt')
	def _check_cancelation(self):
		# Need Improvement .... exceptions are not handled....!
		for rec in self:
			cargo_sale_id = False
			rec.is_cancel = False

			if rec._context.get('active_model') == 'bsg_vehicle_cargo_sale':
				cargo_sale_id = rec.env['bsg_vehicle_cargo_sale'].browse(rec._context.get('active_id'))
			if rec._context.get('active_model') == 'account.move':
				cargo_sale_id = rec.env['account.move'].browse(rec._context.get('active_ids'))
				cargo_sale_id = cargo_sale_id.cargo_sale_id
			if rec.cancel_amt > 0:
				rec.is_cancel = True
				rec.amount = rec.cancel_amt
				active_id = rec._context.get('active_id')
				active_model = rec._context.get('active_model')
				if rec._context.get('active_model') == 'bsg_vehicle_cargo_sale':
					inv = rec.env['account.move'].browse(rec._context.get('default_return_invoice_id'))
				else:
					inv = rec.env['account.move'].browse(active_id)
				if inv.single_trip_reason.stc_value != 0:
					rec.payment_difference_handling = 'reconcile'
				if inv.single_trip_reason.stc_account_id:
					rec.writeoff_account_id = inv.single_trip_reason.stc_account_id.id
