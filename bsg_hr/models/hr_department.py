# -*- coding: utf-8 -*-
from odoo import api, fields, models

class BsgInheritHrDepartment(models.Model):
	_inherit = 'hr.department'

	is_branch = fields.Boolean(string='Is Branch ?')
	bsg_branch_id = fields.Many2one(string="Branch", comodel_name="bsg_branches.bsg_branches")
	branch_type = fields.Selection(selection=[('section', 'Section'), ('unit', 'Unit'), ('area', 'Area')],string="Branch Type")


	@api.onchange('bsg_branch_id')
	def _onchange_bsg_branch_id(self):
		if self.is_branch and self.bsg_branch_id:
			self.name = self.bsg_branch_id.branch_ar_name

	# 
	# def write(self,vals):
	# 	res = super(BsgInheritHrDepartment, self).write(vals)
	# 	if vals.get('manager_id', False):
	# 		employees = self.env['hr.employee'].sudo().with_context(force_company=self.env.user.company_id.id,company_id=self.env.user.company_id.id).search([('department_id','=',self.id)])
	# 		employees.write({'parent_id':vals.get('manager_id')})
	# 	return res
