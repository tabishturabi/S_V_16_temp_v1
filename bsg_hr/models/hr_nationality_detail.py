# -*- coding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api, exceptions,_
from odoo.exceptions import UserError
import re
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class BsgHrNationalId(models.Model):
    _name = 'hr.nationality'
    _description = "National IDs"
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = "bsg_nationality_name"

    bsg_id = fields.Many2one('hr.id.type',string="ID Type",track_visibility='always')
    bsg_nationality_name = fields.Char('ID No.',copy=False,track_visibility='always')
    bsg_employee = fields.Many2one('hr.employee',string="Employee",track_visibility='always', domain=[('country_id.code', 'ilike', 'SA')])
    bsg_issuedate = fields.Date("Issue date",track_visibility='always')
    bsg_expirydate = fields.Date("Expiry date",track_visibility='always')
    bsg_dateofbirth = fields.Date("Date of Birth",track_visibility='always')
    bsg_placeofissue = fields.Char("Place of Issue",track_visibility='always')
    bsg_department = fields.Many2one('hr.department',related="bsg_employee.department_id",string="Department",track_visibility='always')
    bsg_bloodgroup = fields.Selection([
        ('A+','A+'),
        ('B+','B+'),
        ('A-','A-'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),

    ],string="Blood Group",track_visibility='always')
    bsg_dependent = fields.Boolean("Dependent",track_visibility='always')
    bsg_family = fields.One2many('hr.iqama.family', 'nif', string="Family Iqama",track_visibility='always')
    # @api.constrains('bsg_nationality_name')
    # def check_bsg_nationality_name(self):
    #     national_id = self.env['hr.nationality'].search([('bsg_nationality_name','=',self.bsg_nationality_name),('id','!=',self.id)])
    #     if national_id:
    #         raise UserError(_("Your Entered ID No is already taken by another user"))
    bsg_emp_code = fields.Char(related='bsg_employee.employee_code',string='Employee ID')
    bsg_emp_id = fields.Char(related='bsg_employee.driver_code',string='Driver Code')

    @api.constrains('bsg_nationality_name')
    def _check_bsg_nationality_name(self):
        for record in self:
            curr_obj = self.env[self._name].search(
                [('id', '!=', record.id), ('bsg_nationality_name', '=', record.bsg_nationality_name)])
            if curr_obj:
                raise ValidationError(
                    _(
                        'Your Entered ID No is already taken by another user %s' % curr_obj.bsg_employee.name))

    @api.onchange('bsg_nationality_name')
    def nationality_regex(self):
        if(self.bsg_nationality_name):
            results = re.match('^(1)[0-9]?', self.bsg_nationality_name, flags=0)
            if not results:
                raise UserError(_('Invalid Id No Entry'))


class BsgIdType(models.Model):
    _name = 'hr.id.type'
    _description = "ID Type"
    _rec_name = "bsg_name"

    bsg_name = fields.Char("ID")

