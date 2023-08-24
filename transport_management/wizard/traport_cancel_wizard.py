# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class AccountInvoiceRefund(models.TransientModel):
	"""Credit Notes"""
	# Migration Notes
	# _inherit = "account.invoice.refund"
	_inherit = "account.move.reversal"

	@api.model
	def _get_reason(self):
		active_id = self._context.get('active_id')
		active_model = self._context.get('active_model')
		if active_model == 'bsg_vehicle_cargo_sale':
			cargo_sale_id = self.env['bsg_vehicle_cargo_sale'].browse(int(active_id))
			return cargo_sale_id.name
		elif active_model == 'transport.management':
			transport_id = self.env['transport.management'].browse(int(active_id))
			return transport_id.transportation_no
		else:
			context = dict(self._context or {})
			active_id = context.get('active_id', False)
			if active_id:
				inv = self.env['account.move'].browse(active_id)
				return inv.name
			return ''

	@api.depends('invoice_date')
	# 
	def _get_refund_only(self):
		active_id = self._context.get('active_id')
		active_model = self._context.get('active_model')
	
		if active_model == 'bsg_vehicle_cargo_sale':
			cargo_sale_id = self.env['bsg_vehicle_cargo_sale'].browse(int(active_id))
			invoice_id = cargo_sale_id.invoice_ids[0]
			if len(invoice_id.payment_move_line_ids) != 0 and invoice_id.state != 'paid':
				self.refund_only = True
			else:
				self.refund_only = False			
		elif active_model == 'transport.management':
			transport_id = self.env['transport.management'].browse(int(active_id))
			if self._context.get('default_wizard_transport_id') and not self._context.get('context_for_invoice'):
				invoice_id = transport_id.payment.reconciled_invoice_ids
				if len(invoice_id.payment_move_line_ids) != 0 and invoice_id.state != 'paid':
					self.refund_only = True
				else:
					self.refund_only = False
			elif self._context.get('context_for_invoice'):
				invoice_id = transport_id.invoice_id
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


	description = fields.Char(string='Reason', required=True, default=_get_reason)
	wizard_transport_id = fields.Many2one('transport.management',string='Transport Management')
	shipment_transport_type = fields.Selection(string="Shipment Transport Type", related="wizard_transport_id.agreement_type")
	transport_single_trip_reason = fields.Many2one('single.trip.cancel', 'One Way Reason')
	transport_round_trip_reason = fields.Many2one('round.trip.cancel', 'Round Trip Vehicale')


	# @api.multi
	def compute_refund(self, mode='refund'):
		inv_obj = self.env['account.move']
		inv_tax_obj = self.env['account.invoice.tax']
		inv_line_obj = self.env['account.move.line']
		context = dict(self._context or {})
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
					if form.wizard_cargo_sale_id.is_old_order:
						refund = inv.refund(form.invoice_date, date, description, inv.journal_id.id)
					else:
						if not form.cargo_sale_line_ids:
							raise UserError(_('Please Choose Lines First!!!'))
						refund = inv.with_context(cargo_sale_line_ids=form.cargo_sale_line_ids).refund(form.invoice_date, date, description, inv.journal_id.id)
					
					#To Add Deduct Line From Customer
					if form.single_trip_reason.stc_reason_type in ['fixed','percentage'] and form.single_trip_reason.stc_value > 0:
						deduct_inv_line = {
							'invoice_id':refund.id,
							'name': form.single_trip_reason.stc_reason_name ,
							'account_id': form.single_trip_reason.stc_account_id.id,
							'price_unit': form.single_trip_reason.stc_reason_type == 'percentage' and -(refund.amount_untaxed *form.single_trip_reason.stc_value/100)\
								 or -(form.single_trip_reason.stc_value),
							'quantity': 1,
							'is_deduct':True,
							'cargo_sale_line_id':form.cargo_sale_line_ids[0].id,
							'branch_id' : refund.wizard_cargo_sale_id.loc_from.loc_branch_id and refund.wizard_cargo_sale_id.loc_from.loc_branch_id.id or False,
							#'account_analytic_id': line.account_analytic_id.id,
							#'analytic_tag_ids': line.analytic_tag_ids.ids,
							'invoice_line_tax_ids': [(6, 0, form.single_trip_reason.tax_ids and form.single_trip_reason.tax_ids.ids or [])],
							
						}
						refund.invoice_line_ids.sudo().create(deduct_inv_line)
						refund._compute_amount()
					created_inv.append(refund.id)

					invoice = inv.read(inv_obj._get_refund_modify_read_fields())
					invoice = invoice[0]

					if mode == 'refund' and form.wizard_cargo_sale_id.shipment_type == 'return' and form.cancel_return_trip:
						
						percentage = 0.0
						inv_obj_id  = inv_obj.browse(invoice['id'])
						order_date = form.wizard_cargo_sale_id.order_date.date()
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
								#percentage += invoice_line_obj.discount
								if form.wizard_cargo_sale_id.is_old_order:
									cargo_sale_line_id = self.env['bsg_vehicle_cargo_sale_line'].search([('bsg_cargo_sale_id','=',form.wizard_cargo_sale_id.id),('unit_charge','=',invoice_line_obj.price_unit)],limit=1)
								else:
									cargo_sale_line_id = invoice_line_obj.cargo_sale_line_id
								amount_diff = (cargo_sale_line_id.price_line_id.price - (cargo_sale_line_id.price_line_id.price*2*invoice_line_obj.discount/100))
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
							'invoice_origin': inv.origin,
							'fiscal_position_id': inv.fiscal_position_id.id,
							})
							for field in inv_obj._get_refund_common_fields():
								if inv_obj._fields[field].type == 'many2one':
									invoice[field] = invoice[field] and invoice[field][0]
								else:
									invoice[field] = invoice[field] or False
							inv_refund = inv_obj.create(invoice)
							inv_refund.action_post()
							body = _('Correction of <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a><br>Reason: %s') % (inv.id, inv.number, description)
							inv_refund.message_post(body=body)
							if inv_refund.payment_term_id.id:
								inv_refund._onchange_payment_term_date_invoice()
							created_inv.append(inv_refund.id)
					xml_id = inv.type == 'out_invoice' and 'action_invoice_out_refund' or \
							inv.type == 'out_refund' and 'action_invoice_tree1' or \
							inv.type == 'in_invoice' and 'action_invoice_in_refund' or \
							inv.type == 'in_refund' and 'action_invoice_tree2'
			elif active_model == 'transport.management':
				if self._context.get('default_wizard_transport_id') and not self._context.get('context_for_invoice'):				
					for transport in self.env['transport.management'].browse(int(self._context.get('default_wizard_transport_id'))):
						transport.write({'is_created_return_bill' : True})

					for inv in self.env['transport.management'].browse(int(self._context.get('default_wizard_transport_id'))).payment.reconciled_invoice_ids:
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
								'invoice_origin': inv.origin,
								'fiscal_position_id': inv.fiscal_position_id.id,
								})
								for field in inv_obj._get_refund_common_fields():
									if inv_obj._fields[field].type == 'many2one':
										invoice[field] = invoice[field] and invoice[field][0]
									else:
										invoice[field] = invoice[field] or False
								inv_refund = inv_obj.create(invoice)
								inv_refund.action_post()
								body = _('Correction of <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a><br>Reason: %s') % (inv.id, inv.number, description)
								inv_refund.message_post(body=body)
								if inv_refund.payment_term_id.id:
									inv_refund._onchange_payment_term_date_invoice()
								created_inv.append(inv_refund.id)
						xml_id = inv.type == 'out_invoice' and 'action_invoice_out_refund' or \
								inv.type == 'out_refund' and 'action_invoice_tree1' or \
								inv.type == 'in_invoice' and 'action_invoice_in_refund' or \
								inv.type == 'in_refund' and 'action_invoice_tree2'				
				elif self._context.get('context_for_invoice'):

					for transport in self.env['transport.management'].browse(int(self._context.get('default_wizard_transport_id'))):
						transport.write({'is_created_return_invoice' : True})

					for inv in self.env['transport.management'].browse(int(self._context.get('default_wizard_transport_id'))).invoice_id:
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
								'invoice_origin': inv.origin,
								'fiscal_position_id': inv.fiscal_position_id.id,
								})
								for field in inv_obj._get_refund_common_fields():
									if inv_obj._fields[field].type == 'many2one':
										invoice[field] = invoice[field] and invoice[field][0]
									else:
										invoice[field] = invoice[field] or False
								inv_refund = inv_obj.create(invoice)
								inv_refund.action_post()
								body = _('Correction of <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a><br>Reason: %s') % (inv.id, inv.number, description)
								inv_refund.message_post(body=body)
								if inv_refund.payment_term_id.id:
									inv_refund._onchange_payment_term_date_invoice()
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
							'invoice_origin': inv.origin,
							'fiscal_position_id': inv.fiscal_position_id.id,
							})
							for field in inv_obj._get_refund_common_fields():
								if inv_obj._fields[field].type == 'many2one':
									invoice[field] = invoice[field] and invoice[field][0]
								else:
									invoice[field] = invoice[field] or False
							inv_refund = inv_obj.create(invoice)
							body = _('Correction of <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a><br>Reason: %s') % (inv.id, inv.number, description)
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

	# @api.multi
	def reverse_moves(self):
		
		if self.wizard_transport_id and self.refund_method == 'cancel':
			account_move = self.env['account.move.line']
			for data in self.wizard_transport_id.invoice_id:
				credit_id = False
				for payment_data in data.payment_ids:
					if payment_data:
						search_move_line_id = account_move.search([('payment_id','=',payment_data.id),('credit','!=',0)],limit=1)
						if search_move_line_id:
							credit_id = search_move_line_id.id
				if data.state == 'paid' and credit_id:
					account_move.browse(credit_id).with_context({'invoice_id' : data.id}).remove_move_reconcile()

		res = super(AccountInvoiceRefund, self).reverse_moves()
		if self.refund_method == 'cancel' and self.wizard_transport_id:
			refund_id = res.get('domain')[1][2]
			if refund_id:
				invoice = self.env['account.move'].browse(refund_id)
				if invoice:
					invoice.update({
						'return_customer_tranport_id':self.wizard_transport_id.id,
						'shipment_type': 'oneway' if self.shipment_transport_type == 'one_way' else 'return',
						'single_trip_reason':self.transport_single_trip_reason.id if self.transport_single_trip_reason else False,
						'round_trip_reason':self.transport_round_trip_reason.id if self.transport_round_trip_reason else False,
						})
		if self.wizard_transport_id and self.shipment_transport_type and (self.transport_single_trip_reason or self.transport_round_trip_reason) and self.refund_method != 'cancel':
			refund_id = res.get('domain')[1][2]
			if refund_id:
				invoice = self.env['account.move'].browse(refund_id)
				if invoice:
					invoice.update({
						'return_vendor_tranport_id' : self.wizard_transport_id if not self._context.get('context_for_invoice') else False,
						'return_customer_tranport_id':self.wizard_transport_id.id if self._context.get('context_for_invoice') else False,
						'shipment_type': 'oneway' if self.shipment_transport_type == 'one_way' else 'return',
						'single_trip_reason': self.transport_single_trip_reason.id if self.transport_single_trip_reason else False,
						'round_trip_reason': self.transport_round_trip_reason.id if self.transport_round_trip_reason else False,
						})
				invoice.action_post()
		# if self.wizard_transport_id:
		# 	self.wizard_transport_id.write({'state' : 'cancel'})
		return res
