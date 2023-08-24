from odoo import models, fields, api, _

class HrExitAccount(models.Model):
    _name = 'hr.exit.account'
    _description = "Hr Exit Account"

    account_id = fields.Many2one('account.account', string="Account")
    journal_id = fields.Many2one('account.journal', string="Journal")

    
    def execute_settings(self):
        self.ensure_one()
        account_settings = self.env.ref('employee_human_resource.hr_exit_account_data', False)
        account_settings.sudo().write({
            'account_id': self.account_id.id,
            'journal_id': self.journal_id.id,
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def default_get(self, fields):
        res = super(HrExitAccount, self).default_get(fields)
        account_settings = self.env.ref('employee_human_resource.hr_exit_account_data', False)
        if account_settings:
            res.update({
                'account_id': account_settings.account_id.id,
                'journal_id': account_settings.journal_id.id,
            })
        return res
