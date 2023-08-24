# -*- coding: utf-8 -*-
from odoo import models, fields,api, _  


class HrPayslipXlsWizard(models.TransientModel):
	_name = 'hr.payslip.xls.wizard'
	_inherit = 'report.report_xlsx.abstract'

	payslip_run_id = fields.Many2one('hr.payslip.run', required=True)
	salary_payment_method = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], string = "Salary Payment Method")
	category_ids = fields.Many2many(
        'hr.employee.category',
        string='Tags')
	report_type = fields.Selection([('details', 'Details Sheet'), ('bank_sheet', 'Bank Sheet')],string="Report Type", default='details')
	
	# @api.multi
	def print_report(self):
		all_recs = self.payslip_run_id.slip_ids
		category_ids =  self.category_ids and self.category_ids.ids or False

		if all_recs:
			self.ensure_one()
			[data] = self.read()
			datas = {
				'ids': [],
				'model': 'hr.payslip',
				'form': data,
			}
			if self.report_type != 'bank_sheet':
				report = self.env['ir.actions.report']. \
					_get_report_from_name('bsg_hr_xlsx.hr_payslip_xls_temp')

				report.report_file = self._get_report_base_filename()
				report = self.env.ref('bsg_hr_xlsx.hr_payslip_xls_wizard_report').report_action(self.payslip_run_id,  data=datas )
			
				return report
			else:
				report = self.env['ir.actions.report']. \
					_get_report_from_name('bsg_hr_xlsx.hr_payslip_xls_bank')

				report.report_file = self._get_report_base_filename()
				report = self.env.ref('bsg_hr_xlsx.hr_payslip_xls_wizard_report_bank').report_action(self.payslip_run_id,  data=datas )
			
				return report

		else:
			raise UserError(_('There is no Payslips in the given batch'))

	# @api.multi
	def _get_report_base_filename(self):
		self.ensure_one()
		name = "HR Payroll Report"
		return name