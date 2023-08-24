from odoo import api, fields, models, _


class ResCompanyExt(models.Model):
    _inherit = "res.company"

    custom_right_header = fields.Binary(string="Header", readonly=False)
    currency_exchange_journal_id = fields.Many2one('account.journal', string="Exchange Gain or Loss Journal", domain=[('type', '=', 'general')])
