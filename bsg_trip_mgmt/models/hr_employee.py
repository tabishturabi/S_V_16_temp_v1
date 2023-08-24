# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class HrEmployee(models.Model):
	_inherit = 'res.partner'

	is_staff = fields.Boolean(string="IS Staff")
	is_workshop = fields.Boolean(string="IS Workshop")


class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	partner_id = fields.Many2one('res.partner', string="Related Partner")
	partner_type_id = fields.Many2one('partner.type', string="Partner Type") 

	driver_rewards =  fields.Selection([('by_delivery', 'By Delivery A'),
									('by_delivery_b', 'By Delivery B'),
                                    ('by_revenue', 'By Revenue'),
                                    ('not_applicable', 'Not Applicable')],
                                   string='Driver Reward',
								   default="not_applicable"
								   )
	# @api.multi
	def action_create_user(self):
		for rec in self:
			if rec.partner_id and rec.partner_id.user_ids:
				rec.write({
					'user_id':rec.partner_id.user_ids[0].id
				})
				rec.partner_id.sudo().write({'lang': 'ar_001'})
				rec.partner_id.user_ids[0].sudo().write({'lang': 'ar_001'})
				break
			if not rec.driver_code:
				raise ValidationError(_("[ Driver code/Employee ID ] is required to create a user for this employee!"))
			user_temp = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('id', '=', 481)])
			
			if user_temp:				
				if rec.partner_id:
					user_id = user_temp.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).copy(default={'company_id': self.env.user.company_id.id, 'partner_id': rec.partner_id.id,'name': rec.name, 'login': rec.driver_code.lower(), 'password': rec.driver_code.lower()})
				else:
					user_id = user_temp.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).copy(default={'company_id': self.env.user.company_id.id, 'name': rec.name, 'login': rec.driver_code})
			else:
				if rec.partner_id:
					user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create({
						'name': rec.name,
						'login':rec.driver_code.lower(),
						'password': rec.driver_code.lower(),
					})
				else:
					user_id = user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create({
						'name': rec.name,
						'login': rec.driver_code.lower(),
						'password': rec.driver_code.lower()
					})
			user_id.partner_id.sudo().write({'lang': 'ar_001'})
			user_id.sudo().write({'lang': 'ar_001'})
			rec.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).write({
					'partner_id': user_id.partner_id.id,
					'user_id': user_id.id
				})
		return True
	@api.onchange('is_driver')
	def on_change_is_driver(self):
		for rec in self:
			driver_rewards = False
			if rec.is_driver:
				type_id = 6
			else:
				type_id = 7
				driver_rewards = 'not_applicable'

			res = self.env['partner.type'].search([('id','=',type_id)],limit=1)
			rec.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).partner_type_id = res and res.id or False
			rec.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).driver_rewards = driver_rewards

	# @api.multi
	def action_view_employee_reward(self):        
		search_id = self.env['employee_reward_history'].search([('employee_id','=',self.id)])
		return {
		'name': _('Driver Reward'),
		'view_type': 'form',
		'view_mode': 'tree,form',
		'res_model': 'employee_reward_history',
		'view_id': False,
		'type': 'ir.actions.act_window',
		'domain': [('id', 'in', search_id.ids)],
		}


	#Technical use: fix old data .. link employee to partner
	# @api.multi
	def link_partner(self):
		employees = self.search([])
		for rec in employees:
			partner_id = self.env['res.partner'].search([('name', '=', rec.name)])
			if len(partner_id) == 1:
				rec.partner_id = partner_id.id

	def mapp_keys(self):
		return {
			'bsg_empigama':'igama_no',
			'bsg_national_id': 'customer_id_card_no',
			'country_id': 'customer_nationality',
			'bsg_passport':'customer_visa_no',
			'employee_code': 'ref'
		}
			
    # Overiding create method 
	@api.model
	def create(self, vals): 
		res = super(HrEmployee, self).create(vals)
		partner_id = False
		domain_list = []
		if res.bsg_empiqama and res.bsg_empiqama.bsg_iqama_name:
			domain_list.append(('iqama_no', '=', res.bsg_empiqama.bsg_iqama_name))
		if res.bsg_national_id and res.bsg_national_id.bsg_nationality_name:
			domain_list.append(('customer_id_card_no', '=', res.bsg_national_id.bsg_nationality_name))
		if res.bsg_passport and res.bsg_passport.bsg_passport_number:
			domain_list.append(('customer_visa_no', '=', res.bsg_passport.bsg_passport_number))
		if domain_list:
			if len(domain_list) == 3:
				domain = ['|', domain_list[0], domain_list[1], '|', domain_list[2]]
			elif len(domain_list) == 2:
				domain = ['|', domain_list[0], domain_list[1]]
			else:
				domain = domain_list
			partner_id = self.env['res.partner'].search(domain, limit=1)
		partner_vals = {
				'name' : res.name,
				'customer_rank' : 1,
				'supplier_rank' : 1,
				'is_staff' : True,
				'iqama_no': res.bsg_empiqama and res.bsg_empiqama.bsg_iqama_name or False,
				'customer_id_card_no': res.bsg_national_id and res.bsg_national_id.bsg_nationality_name or False,
				'customer_visa_no': res.bsg_passport and res.bsg_passport.bsg_passport_number or False,
				'function': res.job_id and res.job_id.name or False,
				'phone':res.work_phone,
				'mobile': res.mobile_phone,
				'partner_types': res.partner_type_id and res.partner_type_id.id or False
			}

		if not partner_id:
			partner_id = self.env['res.partner'].create(partner_vals)
		else:
			partner_id.write(partner_vals)
		partner_id._onchange_partner_types()
		res.partner_id = partner_id.id
		return res

	# @api.multi
	def write(self, vals):
		res = super(HrEmployee, self).write(vals)
		for rec in self:
			if rec.partner_id:
				partener_vals = {}
				if vals.get('name',False):
					partener_vals.update({'name':rec.name})
				if vals.get('bsg_empiqama',False):
					partener_vals.update({'iqama_no': rec.bsg_empiqama and rec.bsg_empiqama.bsg_iqama_name or False})
				if vals.get('bsg_national_id',False):
					partener_vals.update({'customer_id_card_no': rec.bsg_national_id and rec.bsg_national_id.bsg_nationality_name or False})
				if vals.get('bsg_passport',False):
					partener_vals.update({'customer_visa_no': rec.bsg_passport and rec.bsg_passport.bsg_passport_number or False})
				if vals.get('job_id',False):
					partener_vals.update({'function': rec.job_id and rec.job_id.name or False})
				if vals.get('work_phone',False):
					partener_vals.update({'phone':rec.work_phone})
				if vals.get('mobile_phone',False):
					partener_vals.update({'mobile':rec.mobile_phone})
				if vals.get('partner_type_id', False) and rec.partner_type_id:
					partener_vals.update({'partner_types': rec.partner_type_id.id})
				if partener_vals:
					rec.partner_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).write(partener_vals)
				rec.partner_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id)._onchange_partner_types()
		return res
		


class EmployeeRewardHistory(models.Model):
	_name = "employee_reward_history"
	_description = "Employee Reward History"
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = 'trip_id'

	# 
	def _compute_total_amount(self):
		self.total_amount = self.reward_amount - self.fine_amount

	trip_id = fields.Many2one('fleet.vehicle.trip',string="Trip ID")
	employee_id = fields.Many2one('hr.employee',string="Driver")
	reward_type = fields.Selection([
            ('by_delivery','Reward By Delivery'),('by_revenue','By Revenue')],string="Reward Type")
	currency_id = fields.Many2one('res.currency',string="Currency")
	reward_amount = fields.Float(string="Reward Amount")
	state = fields.Selection([
	        ('unpaid','UnPaid'),('paid','Paid')],string="Status")
	fine_amount = fields.Float(string="Fine")
	total_amount = fields.Float(string="Total Reward",compute="_compute_total_amount")
	waypoint_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints")
	waypoint_to = fields.Many2one(string="To", comodel_name="bsg_route_waypoints")	
	no_of_cars = fields.Integer(string="No of Cars")