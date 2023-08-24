# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigPettyCash(models.Model):
	_name = 'res_petty_cash_config'
	_description = "Res Config Petty Cash"


	
	def execute(self):
		self.ensure_one()
		pettyconfig = self.env.ref('advance_petty_expense_mgmt.res_petty_cash_config_data', False)
		pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).write({'product_ids' : [(6,0,self.product_ids.ids)],
								  'account_ids' : [(6,0,self.account_ids.ids)],
								  'analytic_account_ids' : [(6,0,self.analytic_account_ids.ids)],
								  'analytic_tag_ids' : [(6,0,self.analytic_tag_ids.ids)],
								  'department_ids' : [(6,0,self.department_ids.ids)],
								  'branch_ids' : [(6,0,self.branch_ids.ids)],
			  					  'cash_vendor_ids' : [(6,0,self.cash_vendor_ids.ids)],
								  'partner_type_ids' : [(6,0,self.partner_type_ids.ids)],
								  'is_with_product': self.is_with_product,
								  'is_without_product':self.is_without_product})
		return {'type': 'ir.actions.client', 'tag': 'reload'}

	@api.model
	def default_get(self, fields):
		res = super(ResConfigPettyCash, self).default_get(fields)
		pettyconfig = self.env.ref('advance_petty_expense_mgmt.res_petty_cash_config_data', False)
		if pettyconfig:
			res.update({'product_ids' : pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).product_ids.ids,
				'account_ids' : pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).account_ids.ids,
				'analytic_account_ids' : pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).analytic_account_ids.ids,
				'analytic_tag_ids' : pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).analytic_tag_ids.ids,
				'department_ids' : pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).department_ids.ids,
				'branch_ids' : pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).branch_ids.ids,
				'cash_vendor_ids' : pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).cash_vendor_ids.ids,
				'partner_type_ids' : pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).partner_type_ids.ids,
				'is_with_product':pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).is_with_product,
				'is_without_product':pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).is_without_product,
				'edit':False})
		return res

	product_ids = fields.Many2many('product.product', string="Product's")
	account_ids = fields.Many2many('account.account', string="Account's")
	analytic_account_ids = fields.Many2many('account.analytic.account', string="Analytic Account's")	
	analytic_tag_ids = fields.Many2many('account.account.tag', string="Analytic Tag's")
	department_ids = fields.Many2many('hr.department', string="Department's")
	branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branche's")
	cash_vendor_ids = fields.Many2many('res.partner', string="Cash Vendors",domain=[("is_petty_vendor",'=',True)])
	partner_type_ids = fields.Many2many('partner.type', string="Partner Types")
	is_with_product = fields.Boolean(string="With Product")
	is_without_product = fields.Boolean(string="Without Product")
	edit = fields.Boolean()
	# #onchange to for false value of Without Product
	# @api.onchange('is_with_product')
	# def _onchange_is_with_product(self):
	# 	if self.is_with_product:
	# 		self.is_without_product = False

	# #onchange to for false value of With Product
	# @api.onchange('is_without_product')
	# def _onchange_is_without_product(self):
	# 	if self.is_without_product:
	# 		self.is_with_product = False



		
	
	def product_views_show(self):
		action = self.env.ref('product.product_template_action_all')
		action = action.read()[0]
		action['domain'] = str([
			('id', 'in', self.product_ids.ids)  
		])
		return action

	
	def account_views_show(self):
		action = self.env.ref('account.action_account_form')
		action = action.read()[0]
		action['domain'] = str([
			('id', 'in', self.account_ids.ids)  
		])
		return action

	
	def analytic_account_views_show(self):
		action = self.env.ref('analytic.action_account_analytic_account_form')
		action = action.read()[0]
		action['domain'] = str([
			('id', 'in', self.analytic_account_ids.ids)  
		])
		return action	



	
	def analytic_tags_views_show(self):
		action = self.env.ref('analytic.account_analytic_tag_action')
		action = action.read()[0]
		action['domain'] = str([
			('id', 'in', self.analytic_tag_ids.ids)  
		])
		return action

	
	def department_views_show(self):
		action = self.env.ref('hr.open_module_tree_department')
		action = action.read()[0]
		action['domain'] = str([
			('id', 'in', self.department_ids.ids)  
		])
		return action

	
	def vendor_views_show(self):
		action = self.env.ref('base.action_partner_supplier_form	')
		action = action.read()[0]
		action['domain'] = str([
			('id', 'in', self.cash_vendor_ids.ids)  
		])
		return action

	
	def branch_views_show(self):
		action = self.env.ref('bsg_branch_config.action_window_bsg_branches	')
		action = action.read()[0]
		action['domain'] = str([
			('id', 'in', self.branch_ids.ids)  
		])
		return action

	
	def partner_views_show(self):
		action = self.env.ref('base_customer.action_partnertype')
		action = action.read()[0]
		action['domain'] = str([
			('id', 'in', self.partner_type_ids.ids)  
		])
		return action									