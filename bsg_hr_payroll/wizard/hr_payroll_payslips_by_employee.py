# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    payslip_run_id = fields.Many2one('hr.payslip.run', string='Batch', default=lambda self:self.env.context.get('active_id'))
    
    @api.onchange('payslip_run_id')
    def set_employee_ids_domain(self):
        slip_ids =  self.payslip_run_id.slip_ids
        domain = []
        if slip_ids:
            slip_emp_ids = [emp.id for emp in slip_ids.mapped('employee_id')]
            domain = [('id', 'not in', slip_emp_ids), ('suspend_salary','!=',True),('has_open_contract','=', True)]
        else:
            domain = [('suspend_salary','!=',True),('has_open_contract','=', True)]
        return {'domain': {'employee_ids':domain}}

    
    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note','description'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        description = run_data.get('description')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'category_ids': employee.category_ids and [(6, 0, employee.category_ids.ids)] or [],
                'employee_state': employee.employee_state,
                'salary_payment_method': employee.salary_payment_method,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
                'company_id': employee.company_id.id,
                'description': description,
                'department_id': employee.department_id.id or False,
                'branch_id': employee.branch_id.id or False,
                'job_id': employee.job_id.id or False
            }
            payslips += self.env['hr.payslip'].create(res)
        for slip in payslips:
            slip.sudo().onchange_employee()
            slip.sudo().compute_sheet()
        return {'type': 'ir.actions.act_window_close'}
