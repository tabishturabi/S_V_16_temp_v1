from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    payslip_run = env['ir.model'].search([('model', '=', 'hr.payslip.run')])
    payslip_run.update({'track': True})
    payslip = env['ir.model'].search([('model', '=', 'hr.payslip')])
    payslip.update({'track': True})
    employee = env['ir.model'].search([('model', '=', 'hr.employee')])
    employee.update({'track': True})
    env['ir.model'].search([('model', '=', 'hr.contract')]).update({'track': True})
