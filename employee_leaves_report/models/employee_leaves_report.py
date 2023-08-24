from odoo import models, fields, api, _


class XlsxReportEmployeeAnnualReport(models.TransientModel):
    _name = 'employee.annual.report'
    _inherit = 'report.report_xlsx.abstract'

    form = fields.Date(string='From', required=True)
    to = fields.Date(string='To', required=True)
    employee_ids = fields.Many2many('hr.employee', string="Employee", required=True)

    # @api.multi
    def print_report(self):
        all_recs = self.env['hr.leave'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([], limit=1)
        if 1:
            self.ensure_one()
            [data] = self.read()
            datas = {
                'ids': [],
                'model': 'hr.leave',
                'form': data,
            }
            report = self.env['ir.actions.report']. \
                _get_report_from_name('employee_leaves_report.employee_leaves_report_xlsx')

            report.report_file = self._get_report_base_filename()
            report = self.env.ref('employee_leaves_report.action_employee_annual_report').report_action(all_recs,
                                                                                                        data=datas)
            return report

    # @api.multi
    def _get_report_base_filename(self):
        self.ensure_one()
        name = "Employee Annual Report"
        return name
