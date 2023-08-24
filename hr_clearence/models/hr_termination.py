# -*- coding: utf-8 -*-
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrTermination(models.Model):
    _inherit = 'hr.termination'

    # @api.multi
    def action_view_hr_clearance(self):
        action = self.env.ref('hr_clearence.hr_clearance_action').read()[0]
        action['domain'] = [('termination_id', 'in', self.ids)]
        return action

    hr_clearance_count = fields.Integer(string="HR Clearance Ccount", compute="_get_hr_clearance_count")

    def _get_hr_clearance_count(self):

        """"""
        for rec in self:
            rec.hr_clearance_count = self.env["hr.clearance"].search_count([('termination_id', 'in', rec.ids)])

    # @api.multi
    def action_create_ticket(self):
        hr_ticket_request_type = self.env['hr.ticket.request.type'].search([('ticket_check', '=', True)], limit=1)
        vals = {
            'request_date': fields.date.today(),
            'employee_id': self.employee_id.id,
            'termination_id': self.id,
            'request_type': hr_ticket_request_type.id,
            'ticket_cost': 0.0,
            'ticket_date': fields.date.today(),
            'mission_check': True,
        }
        self.env['hr.ticket.request'].create(vals)
        self.write({'is_ticket_created': True})

    # @api.multi
    def action_view_hr_ticket_request(self):
        action = self.env.ref('bsg_hr_ksa_ticket.ticket_request_action').read()[0]
        action['domain'] = [('termination_id', 'in', self.ids)]
        return action

    hr_ticket_request_count = fields.Integer(string="HR Ticket Request Count", compute="_get_hr_ticket_request_count")

    def _get_hr_ticket_request_count(self):

        """"""
        for rec in self:
            rec.hr_ticket_request_count = self.env["hr.ticket.request"].search_count([('termination_id', 'in', rec.ids)])

    # @api.multi
    def action_accountant_before_audit(self):
        res = super(HrTermination, self).action_accountant_before_audit()
        if self.eos_options == 'final_exit':
            exit_and_return = self.env['hr.exit.return'].search([('hr_termination_id','=',self.id)],limit=1)
            if not exit_and_return:
                vals = {
                    'request_for': 'employee',
                    'travel_before_date': fields.date.today(),
                    'exit_return_type': 'final',
                    'employee_id': self.employee_id.id,
                    'hr_termination_id': self.id}
                hr_exit_return = self.env['hr.exit.return'].create(vals)
        return res

    # @api.multi
    def action_view_hr_exit_return(self):
        action = self.env.ref('employee_human_resource.action_menu_government_relations').read()[0]
        action['domain'] = [('hr_termination_id', 'in', self.ids)]
        return action

    hr_exit_return_count = fields.Integer(string="HR Exit Return Count", compute="_get_hr_exit_return_count")

    def _get_hr_exit_return_count(self):

        """"""
        for rec in self:
            rec.hr_exit_return_count = self.env["hr.exit.return"].search_count([('hr_termination_id', '=', rec.id)])