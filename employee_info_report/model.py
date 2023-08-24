import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class XlsxReportEmployeeInfo(models.TransientModel):
	_name = 'employee.info.report'
	_inherit = 'report.report_xlsx.abstract'

	
	mode = fields.Selection(
		[
			('specific', 'Specific Employee'),
			('branch', 'By Branch'),
			('dept', 'By Department'),
			('company', 'By Company'),
			('emp_tag', 'By Employee Tag'),
		], default='specific',)
	branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branches")
	dept_ids = fields.Many2many('hr.department', string="Department")
	company_ids = fields.Many2many('res.company', string="Company")
	tag_ids = fields.Many2many('hr.employee.category', string="Tags")
	employee_ids = fields.Many2many('hr.employee', string="Employee Names")
	salary_payment_method = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], string = "Salary Payment Method")
	employee_state = fields.Selection([
        ('on_job', 'On Job'),
        ('on_leave', 'On leave'),
        ('return_from_holiday', 'Return From Holiday'),
        ('resignation', 'Resignation'),
        ('suspended', 'Suspended'),
        ('service_expired','Service Expired'),
        ('contract_terminated', 'Contract Terminated'),
        ('ending_contract_during_trial_period','Ending Contract During Trial Period')
        ], string='Employee State')


	# @api.multi
	def print_report(self):
		
		all_recs = self.env['hr.employee'].search([],limit=1)

		if all_recs:
			self.ensure_one()
			[data] = self.read()
			datas = {
				'ids': [],
				'model': 'hr.employee',
				'form': data,
			}
			
			report = self.env['ir.actions.report']. \
				_get_report_from_name('employee_info_report.employee_info_report_xlsx')

			report.report_file = self._get_report_base_filename()
			report = self.env.ref('employee_info_report.action_employee_info_report').report_action(all_recs, data=datas)
			return report
		else:
			raise UserError(_('There is no record in given date'))

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "Employee Information Report"
		return name
	   


	