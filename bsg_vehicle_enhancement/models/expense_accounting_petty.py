from odoo import _, api, fields, models


class AccountExpenseExt(models.Model):
    _inherit = 'expense.accounting.petty'
    _description = 'Petty Cash Expense'

    @api.model
    def create(self, vals):
        res = super(AccountExpenseExt, self).create(vals)
        res.action_vehicle_renewel()
        return res

    def action_vehicle_renewel(self):
        vehicle_renewal_id = self.env.context.get('vehicle_renewal_id')
        if vehicle_renewal_id:
            self.env['renewal.vehicle.document'].browse(vehicle_renewal_id).write({
                'expense_id': self.id,
                'state': 'petty_cash',
            })
