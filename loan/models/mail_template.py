# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class mail_template(models.Model):
    _inherit = 'mail.template'

    is_loan_template = fields.Boolean('Is Loan template')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: