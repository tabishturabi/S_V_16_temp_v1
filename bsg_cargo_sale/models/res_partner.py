# -*- coding: utf-8 -*-
import re
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class bsg_inherit_res_partner(models.Model):
	_inherit = 'res.partner'

	name = fields.Char(index=True, track_visibility='always')
	is_from_cargo_sale = fields.Boolean(string="IS From Cargo Sale")
	allow_rates = fields.Boolean(string="Define Rates")
	bsg_rate_ids = fields.One2many(string="Rates", comodel_name="bsg_customer_rates", inverse_name="partner_id")
	iqama_no = fields.Char(string="Iqama/ID")
	po_box = fields.Char(string="PO Box", copy=False)
	attention = fields.Char(string="Attention", copy=False)
	fax = fields.Char(string="Fax", copy=False)
	max_credit_limit = fields.Float(string="Max Credit Limit")
	customer_type = fields.Selection(string="Customer Type", selection=[
		('1','Saudi'),    
		('2','Non-Saudi'),    
		('3','Corporate'),  
	])
	customer_nationality = fields.Many2one(string="Nationality", comodel_name="res.country")
	customer_id_type = fields.Selection(string="ID Type", selection=[
		('saudi_id_card','Saudi ID Card'),
		('iqama','Iqama'),
		('gcc_national','GCC National'),
		('passport','Passport'),
		('other','Other'),
	])
	customer_id_card_no = fields.Char(string="ID Card No")
	customer_visa_no = fields.Char(string="Visa No / Passport No")
	customer_business = fields.Char(string="Business Sector")
	block_list_reason = fields.Text(
		string='Reason',
	)
	cc_sms = fields.Boolean(string="CC Sms", track_visibility=True)
	customer_number = fields.Char(string="Customer Number")
	block_list = fields.Boolean(
		string='Black List',track_visibility=True
	)
	no_of_copy = fields.Integer(string='No of Copy')
	default_discount = fields.Float(string="Default Discount %")
	commmercial_number = fields.Char("Commercial Number")
	commercial_reg_expiry_date = fields.Date("Commercial Registration Expiry Date")
	is_credit_customer = fields.Boolean(related="partner_types.is_credit_customer", store=True,
										string='Is Credit Custoer')
	is_customer = fields.Boolean(related="partner_types.is_custoemer", store=True,
								 string='Is Customer')

	#for add validation as need of Customer Number should be unique
	@api.constrains('customer_number')
	def customer_number_constrains(self):
		for data in self:
			if data.customer_number:
				customer_number =  str(data.customer_number)
				search_param = customer_number.casefold()
				search_param_upper = customer_number.upper()
				search_id = self.search(['|',('customer_number','=',search_param_upper),('customer_number','=',search_param)])
				if len(search_id) > 1:
					raise UserError('Customer Number Must Be Unique..!')

	@api.constrains('name','partner_types')
	def customer_name_partner_types(self):
		for data in self:
			aml = self.env['account.move.line'].search([('partner_id', '=', data.id)])
			if len(aml) > 0:
				if data.name or data.partner_types:
					if not self.env.user.has_group('account.group_account_user') and not self.env.user.has_group('account.group_account_manager'):
						raise UserError('You are not allowed update partner information')

	
	def name_all_numbers(self):
		for rec in self:
			name = rec.name.replace(' ', '')
			if name.isdigit():
				return True
			return False

	# Overiding create method
	@api.model
	def create(self, vals):
		res = super(bsg_inherit_res_partner, self).create(vals)
		if res.partner_types:
			# partner_types = self.env['partner.type'].browse(vals.get('partner_types'))
			if not self.env.user.has_group('base_customer.group_credit_customer') and res.partner_types.is_credit_customer:
				raise UserError(_('You have no access to create Credit Customer.......!'))
		# res = super(bsg_inherit_res_partner, self).create(vals)
		if res.name_all_numbers():
			raise UserError("Customer name can not be a Number")
		return res
		
	
	def write(self,vals):
		res = super(bsg_inherit_res_partner, self).write(vals)
		if vals.get('partner_types', False):
			if not self.env.user.has_group('base_customer.group_credit_customer') and self.partner_types.is_credit_customer:
				raise UserError(_('You have no access to create Credit Customer.......!'))
		if vals.get('name', False):
			if self.name_all_numbers():
				raise UserError("Customer name can not be a Number")
		
		return res

	#for restiction if customer was used in contract or cargo sale than not allow to delete...! 
	
	def unlink(self):
		for data in self:
			bsg_customer_contract_id = self.env['bsg_customer_contract'].search([('cont_customer','=',data.id)])
			if bsg_customer_contract_id:
				raise UserError(_('You can not delete a record if the Customer is Used On Customer Contract..!'))
			cargo_sale_id = self.env['bsg_vehicle_cargo_sale'].search([('customer','=',data.id)])
			if cargo_sale_id:
				raise UserError(_('You can not delete a record if the Customer is Used On Cargo Sale..!'))
		return super(bsg_inherit_res_partner, self).unlink()

	@api.constrains('commmercial_number')
	def commmercial_number_constaints(self):
		for data in self:
			if data.commmercial_number:
				commmercial_number =  str(data.commmercial_number)
				search_param = commmercial_number.casefold()
				search_param_upper = commmercial_number.upper()
				search_id = self.search(['|',('commmercial_number','=',search_param_upper),('commmercial_number','=',search_param)])
				if len(search_id) > 1:
					raise UserError('Commercial Number Must Be Unique..!')

		if self.commmercial_number:
			if not self.commmercial_number.isdigit():
				raise UserError(_('Only Interger Value Accepted filed of Commercial Number..!'))

	_sql_constraints = [
	('value_iqama_no_uniq', 'unique (iqama_no,company_id)', 'This iqama_no already exists !'),
	('value_customer_id_card_no_uniq', 'unique (customer_id_card_no)', 'This customer_id_card_no already exists !')
	]

	#need to override becase need default value when create new contact from fly
	
	@api.depends('country_id','is_company')
	def _compute_product_pricelist(self):
		for data in self:
			if data._context.get('default_property_product_pricelist'):
				data.property_product_pricelist = data._context.get('default_property_product_pricelist')
		else:
			company = self.env.context.get('force_company', False)
			res = self.env['product.pricelist']._get_partner_pricelist_multi(self.ids)
			for p in self:
				p.property_product_pricelist = res.get(p.id)

	# 
	# @api.constrains('iqama_no')
	# def _check_iqama_no(self):
	# 	if self.customer_id_type in ['iqama']:
	# 		if self.iqama_no and self.customer_type == '2':
	# 			match = re.match(r'2[0-9]{9}', self.iqama_no)
	# 			if match is None or len(str(self.iqama_no)) != 10:
	# 				raise UserError(
	# 					_('Iqama no must be start from 2 and must have 10 digits.'),
	# 				)

	# 
	@api.constrains('customer_id_card_no')
	def _check_customer_id_card_no(self):
		if self.customer_id_type in ['saudi_id_card']:
			if self.customer_id_card_no:
				match = re.match(r'1[0-9]{9}', self.customer_id_card_no)
				if match is None or len(self.customer_id_card_no) != 10:
					raise UserError(
						_('Customer ID Card no must be start from 1 and must have 10 digits.'),
					)
			elif self.customer_type == 3 and self.customer_id_card_no:
				match = re.match(r'[127][0-9]{6}', self.customer_id_card_no)
				if match is None or len(self.customer_id_card_no) != 7:
					raise UserError(
						_('Customer ID Card no must be start from 1 or 2 or 7 and must have 7 digits.'),
					)

	# 
	@api.constrains('customer_visa_no')
	def _check_customer_visa_no(self):
		if self.customer_visa_no:
			match = re.match(r'[a-zA-Z0-9]', self.customer_visa_no)
			if match is None or len(self.customer_visa_no) > 15:
				raise UserError(
					_('Visa/Passport no must contain Alphanumeric and 15 digits!'),
				)


	@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
		args = args or []
		domain = []
		# if self._context.get('default_is_company') == True and self._context.get('partner_type_val'):
		# 	args = ['|',('ref', '=', name),('name', operator, name),('customer','=',True),('customer_type','=',self._context.get('partner_type_val'))]
		# elif self._context.get('default_is_company') == False and self._context.get('partner_type_val'):
		# 	args = ['|',('ref', '=', name),('name', operator, name),('customer','=',True),('customer_type','=',self._context.get('partner_type_val'))]
		args = [('customer_rank', '>', 0)]
		if self._context.get('partner_type_val'):
			args = [('customer_rank', '>', 0), ('partner_types', '=', self._context.get('partner_type_val'))]

		if name:
			print('........name...........',name)
			if self._context.get('default_is_company') == True and self._context.get('partner_type_val'):
				args = [('customer_rank','>',0),('partner_types','=',self._context.get('partner_type_val'))]
			elif self._context.get('default_is_company') == False and self._context.get('partner_type_val'):
				args = [('customer_rank','>',0),('partner_types','=',self._context.get('partner_type_val'))]
		# Be sure name_search is symetric to name_get
			name = name.split(' / ')[-1]
			print('........name split...........', name)
			print('........name split...........', name)
			domain = ['|','|','|','|','|','|','|',('vat',operator, name),('mobile',operator, name),\
			('phone',operator, name),('email', operator, name),\
			('iqama_no',operator, name),('customer_id_card_no',operator, name)\
			,('ref', operator, name),('name', operator, name)]
			if self._context.get('default_partner_types') and not self._context.get('default_is_petty_vendor'):
				args = [('customer_rank','>',0),('partner_types','=',self._context.get('partner_type_val'))]
			# args += [('block_list','!=',True)]
			if operator in expression.NEGATIVE_TERM_OPERATORS:
				domain = ['&', '!'] + domain[1:]
			return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
		partner_category_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
		return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)



	@api.onchange('customer_type')
	def _onchange_customer_type(self):
		if self.customer_type and self.customer_type == '1':
			self.customer_nationality = self.env['res.country'].search([('code','=','SA'),('phone_code','=','966')])[0].id
			self.customer_id_type = 'saudi_id_card'
		elif self.customer_type and self.customer_type == '2':
			self.customer_id_type = 'iqama'

	# Overiding create method
	@api.model
	def create(self, vals):
		if vals.get('partner_types'):
			partner_types = self.env['partner.type'].browse(vals.get('partner_types'))
			if not self.env.user.has_group('base_customer.group_credit_customer') and partner_types.is_credit_customer:
				raise UserError(
					_('You have no access to create Credit Customer.......!'),
				)
		res = super(bsg_inherit_res_partner, self).create(vals)
		
		return res


	#View Customer Contract 
	
	def action_contract_view(self):
		xml_id = 'bsg_customer_contract.view_bsg_customer_contract_tree'
		tree_view_id = self.env.ref(xml_id).id
		xml_id = 'bsg_customer_contract.view_bsg_customer_contract_form'
		form_view_id = self.env.ref(xml_id).id
		return {
					'name': _('Contract of '+ str(self.name)),
					'view_type': 'form',
					'view_mode': 'tree,form',
					'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
					'res_model': 'bsg_customer_contract',
					'domain': [('cont_customer', 'in', self.ids)],
					'type': 'ir.actions.act_window',
				}

