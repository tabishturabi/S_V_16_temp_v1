from odoo import models, fields, api, _

class EmployeeServiceAccount(models.Model):
    _name = 'employee.service.account'
    _description = "Employee Service Account"

    account_id = fields.Many2one('account.account', string="Account")
    journal_id = fields.Many2one('account.journal', string="Journal")

    
    def execute_settings(self):
        self.ensure_one()
        account_settings = self.env.ref('employee_service.employee_service_account_data', False)
        account_settings.sudo().write({
            'account_id': self.account_id.id,
            'journal_id': self.journal_id.id,
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def default_get(self, fields):
        res = super(EmployeeServiceAccount, self).default_get(fields)
        account_settings = self.env.ref('employee_service.employee_service_account_data', False)
        if account_settings:
            res.update({
                'account_id': account_settings.account_id.id,
                'journal_id': account_settings.journal_id.id,
            })
        return res
