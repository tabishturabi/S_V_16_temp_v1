# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_


class EmpServiceRefuseWizard(models.TransientModel):
    _name = "empservice.refuse.wizard"
    _description = "Refuse Reason Wizard"

    reason = fields.Text(string='Reason', required=True)
    effective_ids = fields.Many2many('employee.service')

    @api.model
    def default_get(self, fields):
        res = super(EmpServiceRefuseWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'effective_ids': active_ids,
        })
        return res

    
    def effective_refuse_reason(self):
        if self.effective_ids:
            for rec in self.effective_ids:
                if rec.service_type.service_name == 'salary_intro_letter':
                    if rec.certification:
                        if rec.state == 'cancel':
                            rec.state = 'done'
                        elif rec.state == 'done':
                            rec.state = 'waiting_finance'
                        elif rec.state == 'waiting_finance':
                            rec.state = 'top_management_secretary'
                        elif rec.state == 'top_management_secretary':
                            rec.state = 'hr_specialist'
                        elif rec.state == 'hr_specialist':
                            rec.state = 'draft'
                    else:
                        if rec.state == 'cancel':
                            rec.state = 'done'
                        elif rec.state == 'done':
                            rec.state = 'hr_specialist'
                        elif rec.state == 'hr_specialist':
                            rec.state = 'draft'
                elif rec.service_type.service_name == 'letter_of_authority':
                    if rec.certification:
                        if rec.state == 'cancel':
                            rec.state = 'done'
                        elif rec.state == 'done':
                            rec.state = 'waiting_finance'
                        elif rec.state == 'waiting_finance':
                            rec.state = 'top_management_secretary'
                        elif rec.state == 'top_management_secretary':
                            rec.state = 'hr_supervisor'
                        elif rec.state == 'hr_supervisor':
                            rec.state = 'hr_specialist'
                        elif rec.state == 'hr_specialist':
                            rec.state = 'direct_manager'
                        elif rec.state == 'direct_manager':
                            rec.state = 'draft'
                    else:
                        if rec.state == 'cancel':
                            rec.state = 'done'
                        elif rec.state == 'done':
                            rec.state = 'hr_supervisor'
                        elif rec.state == 'hr_supervisor':
                            rec.state = 'hr_specialist'
                        elif rec.state == 'hr_specialist':
                            rec.state = 'direct_manager'
                        elif rec.state == 'direct_manager':
                            rec.state = 'draft'
                elif rec.service_type.service_name == 'salary_transfer_letter':
                    if rec.state == 'cancel':
                        rec.state = 'done'
                    elif rec.state == 'done':
                        rec.state = 'hr_supervisor'
                    elif rec.state == 'hr_supervisor':
                        rec.state = 'hr_specialist'
                    elif rec.state == 'hr_specialist':
                        rec.state = 'draft'
                elif rec.service_type.service_name == 'experience_certificate':
                    if rec.state == 'cancel':
                        rec.state = 'done'
                    elif rec.state == 'done':
                        rec.state = 'hr_specialist'
                    elif rec.state == 'hr_specialist':
                        rec.state = 'direct_manager'
                    elif rec.state == 'direct_manager':
                        rec.state = 'draft'
                elif rec.service_type.service_name == 'other':
                    if rec.certification:
                        if rec.state == 'cancel':
                            rec.state = 'done'
                        elif rec.state == 'done':
                            rec.state = 'waiting_finance'
                        elif rec.state == 'waiting_finance':
                            rec.state = 'top_management_secretary'
                        elif rec.state == 'top_management_secretary':
                            rec.state = 'hr_specialist'
                        elif rec.state == 'hr_specialist':
                            rec.state = 'direct_manager'
                        elif rec.state == 'direct_manager':
                            rec.state = 'draft'
                    else:
                        if rec.state == 'cancel':
                            rec.state = 'done'
                        elif rec.state == 'done':
                            rec.state = 'hr_specialist'
                        elif rec.state == 'direct_manager':
                            rec.state = 'hr_specialist'
                        elif rec.state == 'direct_manager':
                            rec.state = 'draft'
                rec.refusal_reason = self.reason
        return {'type': 'ir.actions.act_window_close'}


class EmpServiceCancelReason(models.TransientModel):
    _name = "empservice.cancel.wizard"
    _description = "Cancel Reason Wizard"

    reason = fields.Text(string='Reason', required=True)
    effective_ids = fields.Many2many('employee.service')

    @api.model
    def default_get(self, fields):
        res = super(EmpServiceCancelReason, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'effective_ids': active_ids,
        })
        return res

    
    def effective_cancel_reason(self):
        if self.effective_ids:
            for rec in self.effective_ids:
                rec.write({'state': 'cancel','cancel_reason':self.reason})


        return {'type': 'ir.actions.act_window_close'}
