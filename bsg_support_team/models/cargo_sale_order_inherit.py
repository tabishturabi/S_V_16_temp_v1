# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class BsgVehicleCargoSale(models.Model):
	_inherit = 'bsg_vehicle_cargo_sale'


	#for opening a wizard to change the customer
	
	def change_customer(self):
		data = {'default_cargo_sale_id' : self.id, 'default_partner_types' : self.partner_types.id}
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'cange_so_customer',
			'view_id'   :  self.env.ref('bsg_support_team.cange_so_customer_form').id,
			'view_mode': 'form',
			# 'view_type': 'form',
			'context' : data,
			'target': 'new',
		}

	# this method to create and validate invoice for support team
	def invoice_support_create_validate(self):
		self.invoice_support_create()
		self.message_post(body="Invoice Created By : --> " + str(self.env.user.name))
		if self.invoice_ids:
			for inv in self.invoice_ids:
				inv.action_post()

	# invoice creation method for support team
	
	def invoice_support_create(self):
		inv_obj = self.env['account.move']
		inv_line_obj = self.env['account.move.line']
		# journal_id = self.env['account.move'].default_get(['journal_id'])
		for order in self:
			inv_data = order._prepare_invoice()
			invoice = inv_obj.create(inv_data)
			for line in order.order_line_ids:
				account_id = line.service_type.property_account_income_id.id if line.service_type.property_account_income_id else self._default_inv_line_account_id()
				product_id = self.env['product.product'].search([('product_tmpl_id', '=', line.service_type.id)],
																limit=1).id
				if not account_id:
					raise UserError(
						_('Account Invoice Line account is missing!! Please add in configuration'),
					)
				car_details = line.car_make.car_maker.car_make_name + " " + line.car_model.car_model_name + " " + line.car_size.car_size_name
				plate_no = False
				if line.plate_no:
					plate_no = line.plate_no + line.palte_one + line.palte_second + line.palte_third
				else:
					plate_no = line.non_saudi_plate_no
				data = self._prepare_invoice_line(invoice.id, account_id, car_details,
											   line.unit_charge, line.discount, line.tax_ids, line.account_id,
											   product_id,plate_no=plate_no)
				data.update({'cargo_sale_line_id':line.id})
				line = inv_line_obj.create(data)
				# inv_line_obj.create(
				# 	self._prepare_invoice_line(invoice.id, account_id, car_details,
				# 							   line.unit_charge, line.discount, line.tax_ids, line.account_id,
				# 							   product_id))

			if order.is_satah and order.satah_line:
				for satah in order.satah_line:
					product_id = self.env['product.product'].search([('product_tmpl_id', '=', line.service_type.id)],
																	limit=1).id
					account_income_id = self.env['product.product'].search([('is_satah', '=', True)], limit=1)
					account_id = account_income_id.property_account_income_id.id if account_income_id.property_account_income_id else self._default_satah_account_id()
					if not account_id:
						raise UserError(
							_('Satah Service account is missing!! Please add in configuration'),
						)
					inv_line_obj.create(
						self._prepare_invoice_line(invoice.id, account_id, "Satah Service", satah.price, False,
												   line.tax_ids, line.account_id, product_id))
		# self._get_total_of_demurrae_cost()
		# if self.final_price != 0:
		# 	product_id = self.env['product.product'].search([('name', '=', 'Demurrage Cost')])
		# 	if not product_id:
		# 		product_id = self.env['product.product'].create({'name': 'Demurrage Cost', 'type': 'service'})
		# 		invoice_line_vals = {
		# 			'name': product_id.name,
		# 			'product_id': product_id.id,
		# 			'account_id': product_id.property_account_income_id.id,
		# 			'price_unit': self.final_price,
		# 			'quantity': 1,
		# 			'discount': self.discount_price,
		# 			'invoice_id': invoice.id,
		# 		}
		# 		invoice_line_ids = self.env['account.move.line'].create(invoice_line_vals)
		# 		self.write({'is_demurrage_inovice': True})
		invoice.compute_taxes()
	
	#for getting if user have access or not...!
	def _get_user_access(self):	
		if self.env.user.has_group('bsg_support_team.group_change_so_payment_type'):
			self.is_support_team = True
		else:
			self.is_support_team = False

	is_support_team = fields.Boolean(string="Is Support Team", compute="_get_user_access")
