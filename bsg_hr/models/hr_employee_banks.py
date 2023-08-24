# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class BsgHrBanks(models.Model):
    _name = 'hr.banks'
    _description = "Employee Banks"
    _rec_name = "bsg_acc_number"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    bsg_acc_number = fields.Char("Account Number",track_visibility='always')
    bsg_swift_code_id = fields.Many2one('hr.banks.details',string='Swift Code',track_visibility='always')
    bsg_bank_name = fields.Char("Bank Name",track_visibility='always')
    bsg_title = fields.Char("Title of Account",track_visibility='always')
    bsg_employee_id = fields.Many2one('hr.employee',string="Employee",compute='_compute_employee',store=True,track_visibility='always')
    bsg_emp_code = fields.Char(related='bsg_employee_id.employee_code',string='Employee ID')
    bsg_emp_id = fields.Char(related='bsg_employee_id.driver_code',string='Driver Code')

    @api.depends('bsg_title')
    def _compute_employee(self):
        for rec in self:
            rec.bsg_employee_id = False
            if rec.bsg_title:
                for res in self.env['hr.employee'].search([('bsg_bank_id.bsg_title','=',rec.bsg_title)],limit=1):
                    rec.bsg_employee_id = res.id

    @api.constrains('bsg_acc_number')
    def _check_bsg_acc_number(self):
        for record in self:
            curr_obj = self.env[self._name].search(
                [('id', '!=', record.id), ('bsg_acc_number', '=', record.bsg_acc_number)])
            if curr_obj:
                raise ValidationError(
                    _(
                        'Your Entered Account Number is already taken by another user %s' % curr_obj.bsg_employee_id.name))

