# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class ContractContract(models.Model):
    _inherit = 'contract.line'

    branch_id = fields.Many2one('bsg_branches.bsg_branches', string="Branch", track_visibility='always')
    department_id = fields.Many2one('hr.department', string="Department", track_visibility='always')
    analytic_tag_ids = fields.Many2many('account.account.tag', string="Analytic Tags", track_visibility='always')
    before_end_of_contract = fields.Integer(string="Before End Of Contract", track_visibility='always')
    next_action_list = fields.Selection( selection=[('day', 'Day(s)'), ('week', 'Week(s)'), ('month', 'Month(s)'),\
        ('month_last_day', 'Month(s) last Day'), ('year', 'Year (s)')], track_visibility='always')
    paied_every = fields.Integer(string="Paied Every")
    next_paied_list = fields.Selection( selection=[('day', 'Day(s)'), ('week', 'Week(s)'), ('month', 'Month(s)'),\
        ('month_last_day', 'Month(s) last Day'), ('year', 'Year (s)')], track_visibility='always')
    send_to_ids = fields.Many2many('res.users', string="Send To")

    #override method
    # @api.multi
    def _prepare_invoice_line(self, invoice_id=False):
        res = super(ContractContract,self)._prepare_invoice_line(invoice_id=False)
        res.update({'analytic_tag_ids' : [(6,0,self.analytic_tag_ids.ids)],
                    'branch_id' : self.branch_id.id,
                    'department_id' : self.department_id.id})
        return res
