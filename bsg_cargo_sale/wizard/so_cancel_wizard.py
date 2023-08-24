# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')
class AccountInvoiceRefund(models.TransientModel):
	"""Credit Notes"""
	_inherit = "account.move.reversal"

	@api.model
	def _get_reason(self):
		active_id = self._context.get('active_id')
		active_model = self._context.get('active_model')
		if active_model == 'bsg_vehicle_cargo_sale':
			cargo_sale_id = self.env['bsg_vehicle_cargo_sale'].browse(int(active_id))
			return cargo_sale_id.name
		else:
			if active_id:
				inv = self.env['account.move'].browse(active_id)
				return inv.name
			return ''

		

	@api.depends('invoice_date')
	# 
	def _get_refund_only(self):
		active_id = self._context.get('active_id')
		active_model = self._context.get('active_model')
		self.refund_only = False
		if active_model == 'bsg_vehicle_cargo_sale':
			cargo_sale_id = self.env['bsg_vehicle_cargo_sale'].browse(int(active_id))
			invoice_id = cargo_sale_id.invoice_ids[0]
			if len(invoice_id.payment_move_line_ids) != 0 and invoice_id.state != 'paid':
				self.refund_only = True
			else:
				self.refund_only = False			
		else:
			invoice_id = self.env['account.move'].browse(self._context.get('active_id',False))
			if len(invoice_id.payment_move_line_ids) != 0 and invoice_id.state != 'paid':
				self.refund_only = True
			else:
				self.refund_only = False

	@api.model
	def default_get(self, fields):
		result = super(AccountInvoiceRefund, self).default_get(fields)
		active_id = self._context.get('active_id')
		active_model = self._context.get('active_model')
		if self.env.user.has_group('account.group_account_manager') or self.env.user.has_group('account.group_account_user'):
			result.update({
				'allow_edit_in_wiz' : True,
				})
		else:		
			result.update({
				'allow_edit_in_wiz' : False,
				})
		if active_model == 'account.move':
			invoice_id = self.env['account.move'].browse(int(active_id))
			result['date'] = self._context.get('invoice_date', invoice_id.invoice_date)
		if self._context.get('invoice_date', False):
			result['date'] = self._context.get('invoice_date')

		if not active_id or active_model != 'bsg_vehicle_cargo_sale':
			# active_id = self.env['bsg_vehicle_cargo_sale'].browse(int(active_id))
			return result
		return result

	date = fields.Date(string='Accounting Date')
	description = fields.Char(string='Reason', required=True, default=_get_reason)
	wizard_cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale',string='Cargo Sale ID')
	shipment_type = fields.Selection(string="Shipment Type", related="wizard_cargo_sale_id.shipment_type")
	single_trip_reason = fields.Many2one('single.trip.cancel', 'One Way Reason')
	round_trip_reason = fields.Many2one('round.trip.cancel', 'Round Trip Vehicale')
	cargo_sale_line_ids = fields.Many2many('bsg_vehicle_cargo_sale_line', string='Lines to cancel')
	cancel_return_trip = fields.Boolean(default=False)
	is_old_order = fields.Boolean(related='wizard_cargo_sale_id.is_old_order',store=False)
	allow_edit_in_wiz = fields.Boolean()


	@api.onchange('cancel_return_trip')
	def _onchange_cancel_return_trip(self):
		if not self.cancel_return_trip:
			return {'domain': {'cargo_sale_line_ids': [('bsg_cargo_sale_id', '=', self.wizard_cargo_sale_id.id),
								('state', 'in', ['draft','confirm','cancel_request']),('fleet_trip_id','=',False)]}}
		else:
			return {'domain': {'cargo_sale_line_ids': [('bsg_cargo_sale_id', '=', self.wizard_cargo_sale_id.id),('is_return_canceled','=',False),('return_intiated','=',False),('state', '!=', 'cancel')]}}	
		

	#as need of MR khaleed
	@api.onchange('single_trip_reason')
	def _onchange_single_trip_reason(self):
		if self.single_trip_reason:
			self.description = self.single_trip_reason.stc_reason_name
		if self.single_trip_reason and self.single_trip_reason.is_cancel:
			self.refund_method = 'cancel'
		#elif self.single_trip_reason and not self.single_trip_reason.is_cancel:
		#	self.filter_refund = 'refund'	

	
	def compute_refund(self, mode='refund'):
		inv_obj = self.env['account.move']
		inv_tax_obj = self.env['account.invoice.tax']
		inv_line_obj = self.env['account.move.line']
		context = dict(self._context or {})
		context['cargo_sale_line_ids'] = self.cargo_sale_line_ids
		active_model = self._context.get('active_model')		
		xml_id = False

		for form in self:
			created_inv = []
			date = False
			description = False
			if active_model == 'bsg_vehicle_cargo_sale':
				for inv in self.env['bsg_vehicle_cargo_sale'].browse(int(self._context.get('default_wizard_cargo_sale_id'))).invoice_ids:
					if inv.state in ['draft', 'cancel']:
						raise UserError(_('Cannot create credit note for the draft/cancelled invoice.'))
					if inv.reconciled and mode in ('cancel', 'modify'):
						raise UserError(_('Cannot create a credit note for the invoice which is already reconciled, invoice should be unreconciled first, then only you can add credit note for this invoice.'))
					date = form.date or False
					description = form.description or inv.name
					refund = inv.refund(form.invoice_date, date, description, inv.journal_id.id)
					created_inv.append(refund.id)
					invoice = inv.read(inv_obj._get_refund_modify_read_fields())
					invoice = invoice[0]

					if mode == 'refund' and self.wizard_cargo_sale_id.shipment_type == 'return' and self.cancel_return_trip:
						
						percentage = 0.0
						inv_obj_id  = inv_obj.browse(invoice['id'])
						order_date = self.wizard_cargo_sale_id.order_date.date()
						today_date = fields.Date.today()
						diff = relativedelta(today_date, order_date).months
						for rule in self.env['round.trip.cancel'].search([]):
							if rule.rtc_from_km < diff <= rule.rtc_to_km:
								percentage = rule.rtc_percentage
						refund = refund.read(inv_obj._get_refund_modify_read_fields())
						refund = refund[0]
						if percentage >= 100:
							raise UserError(_('Cannot Create Return with 100% Discount'))
						if refund['invoice_line_ids']:
							for data in refund['invoice_line_ids']:
								invoice_line_obj = inv_line_obj.browse(data)
								cargo_sale_line_id = self.env['bsg_vehicle_cargo_sale_line'].search([('bsg_cargo_sale_id','=',self.wizard_cargo_sale_id.id),('unit_charge','=',invoice_line_obj.price_unit)],limit=1)
								amount_diff = (cargo_sale_line_id.price_line_id.addtional_price - cargo_sale_line_id.price_line_id.price)
								invoice_line_obj.write({'price_unit' : amount_diff,'discount' : percentage })

					if mode in ('cancel', 'modify'):
						movelines = inv.move_id.line_ids
						to_reconcile_ids = {}
						to_reconcile_lines = self.env['account.move.line']
						for line in movelines:
							if line.account_id.id == inv.account_id.id:
								to_reconcile_lines += line
								to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
							if line.reconciled:
								line.remove_move_reconcile()
							refund.action_post()
						for tmpline in refund.move_id.line_ids:
							if tmpline.account_id.id == inv.account_id.id:
								to_reconcile_lines += tmpline
						to_reconcile_lines.filtered(lambda l: l.reconciled == False).reconcile()
						
						if mode == 'modify':
							invoice = inv.read(inv_obj._get_refund_modify_read_fields())
							invoice = invoice[0]
							del invoice['id']
							invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
							invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
							tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
							tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
							invoice.update({
							'move_type': inv.type,
							'invoice_date': form.invoice_date,
							'state': 'draft',
							'number': False,
							'invoice_line_ids': invoice_lines,
							'tax_line_ids': tax_lines,
							'date': date,
							'ref': inv.origin,
							'fiscal_position_id': inv.fiscal_position_id.id,
							})
							for field in inv_obj._get_refund_common_fields():
								if inv_obj._fields[field].type == 'many2one':
									invoice[field] = invoice[field] and invoice[field][0]
								else:
									invoice[field] = invoice[field] or False
							inv_refund = inv_obj.create(invoice)
							inv_refund.action_post()
							body = _('Correction of <a href=# data-oe-model=account.move data-oe-id=%d>%s</a><br>Reason: %s') % (inv.id, inv.number, description)
							inv_refund.message_post(body=body)
							if inv_refund.payment_term_id.id:
								inv_refund._onchange_payment_term_invoice_date()
							created_inv.append(inv_refund.id)
					xml_id = inv.type == 'out_invoice' and 'action_invoice_out_refund' or \
							inv.type == 'out_refund' and 'action_invoice_tree1' or \
							inv.type == 'in_invoice' and 'action_invoice_in_refund' or \
							inv.type == 'in_refund' and 'action_invoice_tree2'
			else:
				for inv in inv_obj.browse(context.get('active_ids')):
					if inv.state in ['draft', 'cancel']:
						raise UserError(_('Cannot create credit note for the draft/cancelled invoice.'))
					if inv.reconciled and mode in ('cancel', 'modify'):
						raise UserError(_('Cannot create a credit note for the invoice which is already reconciled, invoice should be unreconciled first, then only you can add credit note for this invoice.'))
					date = form.date or False
					description = form.description or inv.name
					refund = inv.refund(form.invoice_date, date, description, inv.journal_id.id)
					created_inv.append(refund.id)
					if mode in ('cancel', 'modify'):
						movelines = inv.move_id.line_ids
						to_reconcile_ids = {}
						to_reconcile_lines = self.env['account.move.line']
						for line in movelines:
							if line.account_id.id == inv.account_id.id:
								to_reconcile_lines += line
								to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
							if line.reconciled:
								line.remove_move_reconcile()
							refund.action_post()
						for tmpline in refund.move_id.line_ids:
							if tmpline.account_id.id == inv.account_id.id:
								to_reconcile_lines += tmpline
						to_reconcile_lines.filtered(lambda l: l.reconciled == False).reconcile()
						if mode == 'modify':
							invoice = inv.read(inv_obj._get_refund_modify_read_fields())
							invoice = invoice[0]
							del invoice['id']
							invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
							invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
							tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
							tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
							invoice.update({
							'move_type': inv.type,
							'invoice_date': form.invoice_date,
							'state': 'draft',
							'number': False,
							'invoice_line_ids': invoice_lines,
							'tax_line_ids': tax_lines,
							'date': date,
							'invoice_origin': inv.ref,
							'fiscal_position_id': inv.fiscal_position_id.id,
							})
							for field in inv_obj._get_refund_common_fields():
								if inv_obj._fields[field].type == 'many2one':
									invoice[field] = invoice[field] and invoice[field][0]
								else:
									invoice[field] = invoice[field] or False
							inv_refund = inv_obj.create(invoice)
							body = _('Correction of <a href=# data-oe-model=account.move data-oe-id=%d>%s</a><br>Reason: %s') % (inv.id, inv.number, description)
							inv_refund.message_post(body=body)
							if inv_refund.payment_term_id.id:
								inv_refund._onchange_payment_term_date_invoice()
							created_inv.append(inv_refund.id)
					xml_id = inv.type == 'out_invoice' and 'action_invoice_out_refund' or \
							inv.type == 'out_refund' and 'action_invoice_tree1' or \
							inv.type == 'in_invoice' and 'action_invoice_in_refund' or \
							inv.type == 'in_refund' and 'action_invoice_tree2'
		if xml_id:
			result = self.env.ref('account.%s' % (xml_id)).read()[0]
			if mode == 'modify':
				# When refund method is `modify` then it will directly open the new draft bill/invoice in form view
				if inv_refund.type == 'in_invoice':
					view_ref = self.env.ref('account.view_move_form')
				else:
					view_ref = self.env.ref('account.view_move_form')
				result['views'] = [(view_ref.id, 'form')]
				result['res_id'] = inv_refund.id
			else:
				invoice_domain = safe_eval(result['domain'])
				invoice_domain.append(('id', 'in', created_inv))
				result['domain'] = invoice_domain
			return result

		return True

	
	def reverse_moves(self):
		#as need of M.Khalid
		if self.wizard_cargo_sale_id:
			if self.refund_method == 'cancel':
				account_move = self.env['account.move.line']
				for data in self.wizard_cargo_sale_id.invoice_ids:
					credit_id = False
					for payment_data in data.payment_ids:
						if payment_data:
							search_move_line_id = account_move.search([('payment_id','=',payment_data.id),('credit','!=',0)],limit=1)
							if search_move_line_id:
								credit_id = search_move_line_id.id
					if data.state == 'paid' and credit_id:
						account_move.browse(credit_id).with_context({'invoice_id' : data.id}).remove_move_reconcile()

			res = super(AccountInvoiceRefund, self.with_context(cancel_cargo_sale_line_ids= self.cargo_sale_line_ids.ids)).reverse_moves()
			refund_id = res.get('res_id')
			invoice = self.env['account.move'].browse(refund_id)
			invoice.write({
				#'single_trip_reason':self.single_trip_reason.id if self.single_trip_reason else False,
				'round_trip_reason':self.round_trip_reason.id if self.round_trip_reason else False,})

			if self.refund_method == 'cancel':
				refund_id = res.get('res_id')
				if refund_id:
					invoice = self.env['account.move'].browse(refund_id)
					if invoice:
						invoice.update({
							'wizard_cargo_sale_id':self.wizard_cargo_sale_id.id,
							'shipment_type':self.shipment_type,
							#'single_trip_reason':self.single_trip_reason.id if self.single_trip_reason else False,
							'round_trip_reason':self.round_trip_reason.id if self.round_trip_reason else False,
							})
						invoice._compute_amount()
			if self.shipment_type and (self.single_trip_reason or self.round_trip_reason or self.shipment_type == 'return') and self.refund_method != 'cancel':
				refund_id = res.get('domain')[1][2]
				if refund_id:
					invoice = self.env['account.move'].browse(refund_id)
					if invoice:
						invoice.write({
							'wizard_cargo_sale_id':self.wizard_cargo_sale_id.id,
							'cargo_sale_id':self.wizard_cargo_sale_id.id,
							'shipment_type':self.wizard_cargo_sale_id.shipment_type,
							'loc_from' : self.wizard_cargo_sale_id.loc_from.id,
							'loc_to' : self.wizard_cargo_sale_id.loc_to.id,
							'payment_method' : self.wizard_cargo_sale_id.payment_method.id,
							#'single_trip_reason':self.single_trip_reason.id if self.single_trip_reason else False,
							'round_trip_reason':self.round_trip_reason.id if self.round_trip_reason else False,
							})
					invoice._compute_amount()
					invoice.action_post()

			if self.wizard_cargo_sale_id.is_old_order:
				if not self.cancel_return_trip:
					for line_date in self.wizard_cargo_sale_id.order_line_ids:
							line_date.write({'state' : 'cancel'})
				if self.cancel_return_trip:
					for line_date in self.wizard_cargo_sale_id.order_line_ids:
							line_date.write({'is_return_canceled':True})			
				for wiz_data in self.wizard_cargo_sale_id.invoice_ids:
					for wiz_pay in wiz_data.payment_ids:
						if wiz_data and not wiz_pay and all(st == 'cancel' for st in self.wizard_cargo_sale_id.order_line_ids.mapped('state')):
							self.wizard_cargo_sale_id.write({'state' : 'cancel'})				
			else:
				if self.cancel_return_trip:
					for cargo_line in self.cargo_sale_line_ids:
						cargo_line.write({'is_return_canceled':True})
				if not self.cancel_return_trip:	
					for cargo_line in self.cargo_sale_line_ids:
						cargo_line.write({'state' : 'cancel'})
					if all(st == 'cancel' for st in self.wizard_cargo_sale_id.order_line_ids.mapped('state')):
						self.wizard_cargo_sale_id.write({'state' : 'cancel'})
			self.wizard_cargo_sale_id._amount_all()
		else: 
			res = super(AccountInvoiceRefund, self).invoice_refund()
			refund_id = res.get('res_id',False)
			if refund_id:
				inv_cargo_sale_id = self.env['account.move'].browse(self.env.context['active_id'])
				invoice = self.env['account.move'].browse(refund_id)
				invoice.write({'cargo_sale_id':inv_cargo_sale_id.cargo_sale_id.id,'round_trip_reason':self.round_trip_reason.id if self.round_trip_reason else False,})

		return res
