# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError

class bsg_customer_contract(models.Model):
	_name = 'bsg_customer_contract'
	_inherit = ['mail.thread']
	_description = 'Customer Contract'
	_rec_name = 'contract_name'

	#Total Discount
	def _get_amount_total(self, line_ids, sum_lines):
		for order in self:
			contract_lines = order.contract_line_ids.filtered(lambda res: res.id not in line_ids)
			if contract_lines:
				amount_total = sum(contract_lines.mapped('price'))
				return sum_lines + amount_total
			else:
				return line_ids and sum_lines or 0
	
	is_invoice_create = fields.Boolean(string="Is Create Invoice", track_visibility=True)		
	contract_name = fields.Char(string='Contract Name', track_visibility=True)
	cont_customer = fields.Many2one(string="Customer Name", comodel_name="res.partner", track_visibility=True)
	cont_start_date = fields.Date(string='Contract Start Date', track_visibility=True,)
	cont_end_date = fields.Date(string='Contract End Date', track_visibility=True,)
	contract_line_ids = fields.One2many(string="Contract Lines",ondelete="cascade", comodel_name="bsg_customer_contract_line", inverse_name="cust_contract_id", track_visibility=True)
	active = fields.Boolean(string="Active", track_visibility=True, default=True)
	state = fields.Selection(
		[
			('draft', 'Draft'),
			('confirm', 'Active Contract'),
			('cancel', 'Declined')
		], string='State', default="draft", track_visibility=True,)
	max_sales_limit = fields.Float(string="Total Contract Amount", track_visibility=True)
	total_sales = fields.Float(string="Used Amount",compute='_compute_no_of_sales', track_visibility=True)
	remainder_amt = fields.Float(string="Remaining Balance",compute='_compute_no_of_sales',store=True, track_visibility=True)
	draft_so_amt = fields.Float(string="Draft So Amount",compute='_compute_no_of_sales')
	free_satha_service = fields.Boolean(string="Free Satha Service", track_visibility=True)
	internal_shipment_pirce = fields.Float(string="Internal Shipment Price")
	shipment_type = fields.Selection([('picking_only','Picking Only'),('droping_only','Droping Only'),('both','Both')],string="Shipmnet Type", track_visibility=True)
	cont_invoice_to = fields.Many2one(string="Invoice To", comodel_name="bsg_route_waypoints", track_visibility=True)
	mail_sended = fields.Boolean('Mail Sended')
	reg_expiry_check = fields.Boolean(string='Registration Expiry Check')
	
	no_of_sales = fields.Integer(
		compute='_compute_no_of_sales', track_visibility=True)

	total_amount = fields.Monetary(string='Total Amount', readonly=True, track_visibility='onchange', track_sequence=6)
	currency_id = fields.Many2one(string="Currency", comodel_name="res.currency", track_visibility=True)
	collection_created_by = fields.Many2many('hr.employee', 'cust_employee_rel', 'customer_id', 'employee_id',
											 string='Collection Created By')
	remark = fields.Char(string="Remarks", translate=True, track_visibility='always')
	sales_teams_ids = fields.Many2many('hr.employee', 'cust_employee_sales_teams_rel', 'customer_id', 'employee_id',
									   string="Sales Teams")
	attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
	reg_expiry_check = fields.Boolean(string='Registration Expiry Check')
	contract_no = fields.Char(string='Contract NO')
	contract_date = fields.Date(string='Contract Date')
	check_decline_access = fields.Boolean("Contract cancel by accountant only")

	
	def _compute_attachment_number(self):
		for cust_contract in self:
			cust_contract.attachment_number = self.env['ir.attachment'].search_count(
				[('res_model', '=', 'bsg_customer_contract'), ('res_id', '=', cust_contract.id)])

	
	def action_get_attachment_view(self):
		self.ensure_one()
		res = self.env['ir.actions.act_window'].for_xml_id('bsg_customer_contract', 'action_attachment')
		return res



	@api.constrains('cont_start_date','cont_end_date')
	def _check_start_end_date(self):
		if self.cont_end_date < self.cont_start_date:
			raise ValidationError('Contract End date can’t be less then Start date')
	
	# Contact limit should be greater then 0 
	@api.constrains('max_sales_limit')
	def _check_max_sales_limit(self):
		if self.max_sales_limit <= 0:
			raise ValidationError(_("Contractual amount must be greater then 0"))

	
	def open_attach_wizard(self):
		view_id = self.env.ref('bsg_customer_contract.view_attachment_cust_contract_form').id
		# default_name = str(self.issue_date) + str(
		# 	self.document_type_id.document_type_id) + " " + "الشاحنة رقم" + " " + str(
		# 	self.document_id.taq_number) + " " + "لصادرة في تاريخ" + " "
		return {
			'name': _('Attachments'),
			'res_model': 'ir.attachment',
			'view_type': 'form',
			'context': "{'default_res_model': '%s','default_res_id': %d,}" % ("bsg_customer_contract", self.id,),
			'type': 'ir.actions.act_window',
			'views': [(view_id, 'form')],
			'view_id': view_id,
			'target': 'new',
		}
	

	
	def _compute_no_of_sales(self):
		for rec in self:
			rec.draft_so_amt = 0.0
			rec.no_of_sales = 0.0
			rec.total_sales = 0.0
			rec.remainder_amt = 0.0
			if rec.cont_customer:
				no_of_sales = 0.0
				total = 0.0
				draft_total = 0.0
				remaining = rec.max_sales_limit
				query = """SELECT count(*), sum(total_amount) FROM bsg_vehicle_cargo_sale
							   WHERE customer = %s AND customer_contract = %s AND state not in ('draft', 'cancel');"""
				query_draft_sale = """SELECT count(*), sum(total_amount) FROM bsg_vehicle_cargo_sale
							   WHERE active != false AND customer = %s AND customer_contract = %s AND state = 'draft';"""
				print('................rec.cont_customer.id.....',rec.cont_customer.id)
				self.env.cr.execute(query, (str(rec.cont_customer.id),str(rec.id),))
				query_results = self.env.cr.dictfetchall()
				if query_results and query_results[0].get('sum') != None:
					total = query_results[0].get('sum')
					no_of_sales = query_results[0].get('count')
					self.env.cr.execute(query_draft_sale, (str(rec.cont_customer.id),str(rec.id),))
					query_results_draft = self.env.cr.dictfetchall()
					if query_results_draft and query_results_draft[0].get('sum') != None:
						draft_total = query_results_draft[0].get('sum')
					# bsg_cargo_sale_id = self.env['bsg_vehicle_cargo_sale'].search([('customer_contract','=',rec.id),('state','=','draft')])

					# for rep in bsg_cargo_sale_id:
						# draft_total += rep.total_amount
					# remaining = rec.max_sales_limit - (total + draft_total) AS per khaild request, 17 August see nexr line.

					remaining = rec.max_sales_limit - total
				rec.draft_so_amt = 	draft_total
				rec.no_of_sales = no_of_sales
				rec.total_sales = total
				rec.remainder_amt = remaining
			return True

	
	def write(self, vals):
		if vals.get('contract_line_ids', False):
			line_ids = []
			sum_lines = 0
			for line in vals['contract_line_ids']:
				if line[2]:
					line_ids.append(line[1])
					sum_lines += line[2]['price']
			vals['total_amount'] = self._get_amount_total(line_ids, sum_lines)
		CusContract = super(bsg_customer_contract, self).write(vals)
		coll_creators_list = self.collection_created_by.mapped('name')
		coll_creators_names = ','.join(coll_creators_list)
		sales_teams_list = self.sales_teams_ids.mapped('name')
		sales_teams_names = ','.join(sales_teams_list)
		msg = _(
			"""<div class="o_thread_message_content">
                <ul class="o_mail_thread_message_tracking">
                    <li>Collection Created By : <span>{coll_creators_names}</span></li>
                    <li>Sales Teams : <span>{sales_teams_names}</span></li>
                </ul>
                </div>
                """.format(
				coll_creators_names=coll_creators_names,
				sales_teams_names=sales_teams_names,
			)
		)
		self.message_post(body=msg)
		return CusContract

	#Overiding the create method
	@api.model
	def create(self, vals):
		CusContract = super(bsg_customer_contract, self).create(vals)
		CusContract.contract_name = self.env['ir.sequence'].next_by_code('bsg_customer_contract_code')
		CusContract.total_amount=sum(CusContract.contract_line_ids.mapped('price'))
		return CusContract
	#write method
	# 
	# def write(self,vals):
	# 	if vals.get('contract_line_ids'):
	# 		contract_line_ids = vals.get('contract_line_ids')
	# 		for cli in contract_line_ids:
	# 			if cli[2] and isinstance(cli[1],int):
	# 				line_id = self.env['bsg_customer_contract_line'].search([('id','=',int(cli[1]))])
	# 				msg = _(
	# 				"""<div class="o_thread_message_content">
	# 	                <p>Customer Contract line Old Value</p>
	# 	                <ul class="o_mail_thread_message_tracking">
	# 	                <li>From : <span>{loc_from}</span></li>
	# 	                <li>To : <span>{loc_to}</span></li>
	# 	                <li>Car Size : <span>{car_size}</span></li>
	# 	                <li>Service Type : <span>{service_type}</span></li>
	# 	                <li>Price : <span>{price}</span></li>
	# 	                </ul>
	# 	                </div>
	# 	                """.format(
	# 	                    loc_from=line_id.loc_from.route_waypoint_name,
	# 	                    loc_to=line_id.loc_to.route_waypoint_name,
	# 	                    car_size=line_id.car_size.car_size_name,
	# 	                    service_type=line_id.service_type.name,
	# 	                    price=line_id.price
	# 	                )
	# 	            )
	# 				line_id.cust_contract_id.message_post(body=msg)
	# 	CusContract = super(bsg_customer_contract, self).write(vals)
	# 	if vals.get('contract_line_ids'):
	# 		contract_line_ids = vals.get('contract_line_ids')
	# 		for cli in contract_line_ids:
	# 			if cli[2] and isinstance(cli[1],int):
	# 				line_id = self.env['bsg_customer_contract_line'].search([('id','=',int(cli[1]))])
	# 				msg = _(
	# 				"""<div class="o_thread_message_content">
	# 	                <p>Customer Contract line Modified</p>
	# 	                <ul class="o_mail_thread_message_tracking">
	# 	                <li>From : <span>{loc_from}</span></li>
	# 	                <li>To : <span>{loc_to}</span></li>
	# 	                <li>Car Size : <span>{car_size}</span></li>
	# 	                <li>Service Type : <span>{service_type}</span></li>
	# 	                <li>Price : <span>{price}</span></li>
	# 	                </ul>
	# 	                </div>
	# 	                """.format(
	# 	                    loc_from=line_id.loc_from.route_waypoint_name,
	# 	                    loc_to=line_id.loc_to.route_waypoint_name,
	# 	                    car_size=line_id.car_size.car_size_name,
	# 	                    service_type=line_id.service_type.name,
	# 	                    price=line_id.price
	# 	                )
	# 	            )
	# 				line_id.cust_contract_id.message_post(body=msg)
	# 	contract_id = self.env['bsg_customer_contract_line'].search(['|',('cust_contract_id','=',self.id),('active','=',False)])
	# 	for res in contract_id:
	# 		if res:
	# 			res.write({'active':self.active})
	# 	return CusContract

	# Overiding Unlink method
	
	def unlink(self):
		for order in self:
			if order.state != 'draft' or order.no_of_sales>0:
				raise UserError(
					_('You can not delete a confirmed Sale Order.'),
				)
		return super(bsg_customer_contract, self).unlink()

	
	def copy(self, default=None):
		"""
			Create a new record in bsg_customer_contract model from existing one 
			with line ids.
		"""
		res =  super(bsg_customer_contract, self).copy(default)
		for line in self.contract_line_ids:
			self.env['bsg_customer_contract_line'].create({'loc_from' : line.loc_from.id or False,
													   'loc_to' : line.loc_to.id or False,													   
													   'car_size' : line.car_size.id or False,
													   'service_type' : line.service_type.id or False,
													   'price' : line.price or 0.0,
													   'partner_id' : line.partner_id.id or False,
													   'cust_contract_id': res.id
													   })
		return res
		
	
	def confirm_btn(self):
		self.state = 'confirm'

	
	def set_draft_btn(self):
		self.state='draft'

	
	def decline(self):
		if self.check_decline_access:
			if not self.env.user.has_group('account.group_account_manager') or not self.env.user.has_group('account.group_account_user') or not self.env.user._is_admin():
				raise ValidationError(_("No access to cancel this record"))
		self.state = 'cancel'

	#View Contract Sale
	
	def action_sale_view(self):
		xml_id = 'bsg_cargo_sale.view_vehicle_cargo_sale_tree'
		tree_view_id = self.env.ref(xml_id).id
		xml_id = 'bsg_cargo_sale.view_vehicle_cargo_sale_form'
		form_view_id = self.env.ref(xml_id).id
		return {
					'name': _(self.contract_name),
					'view_type': 'form',
					'view_mode': 'tree,form',
					'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
					'res_model': 'bsg_vehicle_cargo_sale',
					'domain': [('customer_contract', 'in', self.ids),('customer','=', self.cont_customer.id),('state','not in',['draft', 'cancel'])],
					'type': 'ir.actions.act_window',
				}

	# Import contract lines 
	
	def import_contract_lines(self):
		view_id = self.env.ref('bsg_customer_contract.wizard_import_contract_lines').id
		return {
				'type': 'ir.actions.act_window',
				'name': 'Name',
				'view_mode': 'form',
				'view_type': 'form',
				'res_model': 'import.contract.lines',
				'view_id': view_id,
				'target': 'new',
				'context': {
					'default_contract_id': self.id,
					}
			}

class bsg_customer_contract_line(models.Model):
	_name = 'bsg_customer_contract_line'
	_inherit = ['mail.thread']
	_description = 'Customer Contract Line'
	_rec_name = 'cust_contract_id'
	
	active = fields.Boolean(default=True,
        help="By unchecking the active field, you may hide a fiscal position without deleting it.",track_visibility=True)
	loc_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints", track_visibility=True)
	loc_to = fields.Many2one(string="To", comodel_name="bsg_route_waypoints", track_visibility=True)
	car_size = fields.Many2one(string="Car Size", comodel_name="bsg_car_size", track_visibility=True)
	service_type = fields.Many2one(string="Service Type", comodel_name="product.template", track_visibility=True)
	price = fields.Float(string="Price", track_visibility=True)
	partner_id = fields.Many2one(string="Partner", comodel_name="res.partner", track_visibility=True)
	cust_contract_id = fields.Many2one(string="Contract No",ondelete="cascade", comodel_name="bsg_customer_contract", track_visibility=True)
	customer_id = fields.Many2one(string="Customer Name", comodel_name="res.partner",related='cust_contract_id.cont_customer', track_visibility=True)
	cont_start = fields.Date('Contract Start Date',related='cust_contract_id.cont_start_date', track_visibility=True)
	cont_end = fields.Date('Contract End Date',related='cust_contract_id.cont_end_date', track_visibility=True)
	max_sale = fields.Float('Total Contract Amount',related='cust_contract_id.max_sales_limit', track_visibility=True, store=True)
	use_amount = fields.Float('Used Amount',related='cust_contract_id.total_sales', track_visibility=True)
	remainder_amt = fields.Float('Remaining Balance',related='cust_contract_id.remainder_amt', track_visibility=True)
	is_invoice = fields.Boolean('Is Create Invoice',related='cust_contract_id.is_invoice_create', track_visibility=True)
	free_satha_service = fields.Boolean(string="Free Satha Service",related='cust_contract_id.free_satha_service', track_visibility=True)
	shipment_type = fields.Selection([('picking_only','Picking Only'),('droping_only','Droping Only'),('both','Both')],related='cust_contract_id.shipment_type',string="Shipmnet Type", track_visibility=True)
	check_sale = fields.Boolean('Check Sale') #compute='_compute_check_sale' TDO: find another way other than compute
	
# 	
# # 	@api.depends('cust_contract_id')
# 	def _compute_check_sale(self):
# 		for rec in self:
# 			if rec.cust_contract_id:
# 				cargo_line = rec.env['bsg_vehicle_cargo_sale_line'].search_count([
# 					('bsg_cargo_sale_id.customer_contract', '=', rec.cust_contract_id.id),
# # 					('service_type', '=', rec.service_type.id),
# 					('loc_from', '=', rec.loc_from.id),
# 					('loc_to', '=', rec.loc_to.id),
# 					('car_size', '=', rec.car_size.id)
# 				], limit=1)
# 			if cargo_line != 0:
# 				rec.check_sale=True
# 			else:
# 				rec.check_sale=False
	
	# 
	@api.constrains('price')
	def _price_constrains(self):
		if self.price <= 0:
			raise ValidationError(_("Price Should be greater Than 0"))
	
	# 
	@api.constrains('loc_from','loc_to','car_size','service_type')
	def check_contract_line(self):
		if self.loc_from and self.loc_to and self.car_size and self.service_type:
			record_id = self.env['bsg_customer_contract_line'].search([('loc_from','=',self.loc_from.id),('loc_to','=',self.loc_to.id),('car_size','=',self.car_size.id),('service_type','=',self.service_type.id),('id','!=',self.id),('cust_contract_id','=',self.cust_contract_id.id)])
			if record_id:
				raise UserError(_("Your Entered data already exists...!"))
			

	@api.onchange('loc_from','loc_to')
	def _oncahnge_loc_from_to(self):
		if self.loc_from:
			return {'domain': {'loc_to': [('id', '!=', self.loc_from.id)]}}
		if self.loc_to:
			return {'domain': {'loc_from': [('id', '!=', self.loc_to.id)]}}

	
	def action_duplicate_record(self):
		self.env['bsg_customer_contract_line'].create({'loc_from' : self.loc_from.id or False,
													   'loc_to' : self.loc_to.id or False,
													   'car_size' : self.car_size.id or False,
													   'service_type' : self.service_type.id or False,
													   'price' : self.price or 0.0,
													   'partner_id' : self.partner_id.id or False,
													   'cust_contract_id' : self.cust_contract_id.id or False,
			})



	@api.model
	def create(self, values):
		res =  super(bsg_customer_contract_line, self).create(values)
		msg = _(
			"""<div class="o_thread_message_content">
                <p>Customer Contract line Created</p>
                <ul class="o_mail_thread_message_tracking">
                <li>From : <span>{loc_from}</span></li>
                <li>To : <span>{loc_to}</span></li>
                <li>Car Size : <span>{car_size}</span></li>
                <li>Service Type : <span>{service_type}</span></li>
                <li>Price : <span>{price}</span></li>
                </ul>
                </div>
                """.format(
                    loc_from=res.loc_from.route_waypoint_name,
                    loc_to=res.loc_to.route_waypoint_name,
                    car_size=res.car_size.car_size_name,
                    service_type=res.service_type.name,
                    price=res.price
                )
            )
		res.cust_contract_id.message_post(body=msg)
		return res

	# 
	# def write(self, vals):
	# 	old_values = {
	# 	'loc_from':self.loc_from,
	# 	'loc_to':self.loc_to,
	# 	'car_size':self.car_size,
	# 	'service_type':self.service_type,
	# 	'price':self.price,
	# 	'partner_id':self.partner_id,
	# 	'cust_contract_id':self.cust_contract_id,
	# 	'customer_id':self.customer_id,
	# 	'cont_start':self.cont_start,
	# 	'cont_end':self.cont_end,
	# 	'max_sale':self.max_sale,
	# 	'use_amount':self.use_amount,
	# 	'remainder_amt':self.remainder_amt,
	# 	'is_invoice':self.is_invoice,
	# 	'free_satha_service':self.free_satha_service,
	# 	'shipment_type':self.shipment_type,
	# 	'active':self.active,
	# 	}
	# 	res = super(bsg_customer_contract_line,self).write(vals)
	# 	tracked_fields = self.env['bsg_customer_contract_line'].fields_get(vals)
	# 	changes, tracking_value_ids = self._message_track(tracked_fields, old_values)
	# 	if changes:
	# 		self.cust_contract_id.message_post(tracking_value_ids=tracking_value_ids)
	# 	return res


	
	def unlink(self):
		"""
		    Delete all record(s) from table heaving record id in ids
		    return True on success, False otherwise

		    @return: True on success, False otherwise
		"""
		for rec in self:
			msg = _(
			"""<div class="o_thread_message_content">
                <p>Customer Contract line Deleted</p>
                <ul class="o_mail_thread_message_tracking">
                <li>From : <span>{loc_from}</span></li>
                <li>To : <span>{loc_to}</span></li>
                <li>Car Size : <span>{car_size}</span></li>
                <li>Service Type : <span>{service_type}</span></li>
                <li>Price : <span>{price}</span></li>
                </ul>
                </div>
                """.format(
                    loc_from=rec.loc_from.route_waypoint_name,
                    loc_to=rec.loc_to.route_waypoint_name,
                    car_size=rec.car_size.car_size_name,
                    service_type=rec.service_type.name,
                    price=rec.price
                )
            )
		rec.cust_contract_id.message_post(body=msg)
		for rec in self:
			if rec.cust_contract_id:
				cargo_line = rec.env['bsg_vehicle_cargo_sale_line'].search([
					('bsg_cargo_sale_id.customer_contract', '=', rec.cust_contract_id.id),
# 					('service_type', '=', rec.service_type.id),
					('loc_from', '=', rec.loc_from.id),
					('loc_to', '=', rec.loc_to.id),
				], limit=1)
				if cargo_line and cargo_line.car_size == rec.car_size:
					raise UserError(
						_("You can not Delete a line It's Related To Cargo Sale."),
					)
			rec.cust_contract_id.total_amount = sum(rec.cust_contract_id.contract_line_ids.mapped('price')) - rec.price
# 		search_id = self.env['bsg_vehicle_cargo_sale_line'].search([('price_line_id','=',self.id)])
# 		invoice_line = self.env['account.move.line'].search([('contract_line_id','=',self.id)])
# 		if search_id:
# 			raise Warning(_('You cannot Delete these Record is still Reference'))
# 		if invoice_line:
# 			raise Warning(_('You cannot Delete these Record is still Reference'))
		# result = super(bsg_price_line, self).unlink()
		# return result
		return super(bsg_customer_contract_line, self).unlink()

class IrAttachmentExtCust(models.Model):
	_inherit = "ir.attachment"

	cus_contract_doc_type = fields.Many2one('documents.type', string="Document Type")
