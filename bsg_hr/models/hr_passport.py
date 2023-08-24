# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class BsgHrPassport(models.Model):
    _name = 'hr.passport'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Passport"
    _rec_name = "bsg_passport_number"
    
    bsg_passport_name = fields.Char("Name as Passport",track_visibility='always')
    bsg_passport_number = fields.Char("Passport Number",track_visibility='always')
    bsg_issuedate = fields.Date("Issue date",track_visibility='always')
    bsg_dateofbirth = fields.Date("Date of Birth",track_visibility='always')
    bsg_expirydate = fields.Date("Expiry date",default=fields.date.today(),track_visibility='always',with_hijri="True")
    is_employee = fields.Boolean("Is a Employee",track_visibility='always')
    bsg_passport_issue_country = fields.Char("Passport issue country",track_visibility='always')
    bsg_passport_issue_place = fields.Char("Passport issue Place",track_visibility='always')
    bsg_passport_status = fields.Selection([('we','With Employee'),('wc','With Company')],string="Passport Status",track_visibility='always')
    bsg_employee_id = fields.Many2one('hr.employee',string="Employee",compute='_compute_employee',store=True,track_visibility='always')
    bsg_emp_code = fields.Char(related='bsg_employee_id.employee_code', string='Employee ID')
    bsg_emp_id = fields.Char(related='bsg_employee_id.driver_code', string='Driver Code')

    @api.depends('bsg_passport_number')
    def _compute_employee(self):
        for rec in self:
            rec.bsg_employee_id = False
            if rec.bsg_passport_number:
                for res in self.env['hr.employee'].search([('bsg_passport.bsg_passport_number','=',rec.bsg_passport_number)],limit=1):
                    rec.bsg_employee_id = res.id

    @api.onchange('is_employee')
    def check_boolean(self):
        if(self.is_employee):
            self.bsg_passport_name = self._context.get('default_bsg_passport_name')
        else:
            self.bsg_passport_name = ''

    @api.constrains('bsg_passport_number')
    def _check_bsg_passport_number(self):
        for record in self:
            curr_obj = self.env[self._name].search(
                [('id', '!=', record.id), ('bsg_passport_number', '=', record.bsg_passport_number)])
            if curr_obj:
                raise ValidationError(
                    _(
                        'Your Entered Passport Number is already taken by another user %s' % curr_obj.bsg_employee_id.name))
