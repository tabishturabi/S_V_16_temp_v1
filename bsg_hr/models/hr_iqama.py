# -*- coding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError
import re
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class BsgHrIqama(models.Model):
    _name = 'hr.iqama'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Iqama"
    _rec_name = "bsg_iqama_name"

    bsg_iqama_name = fields.Char('Iqama/ID No.', copy=False, track_visibility='always')
    yearly_iqama_cost = fields.Float('Yearly Iqama Cost', copy=False, track_visibility='always')
    bsg_employee = fields.Many2one('hr.employee', string="Employee", track_visibility='always',
                                   domain=[('country_id.code', 'not ilike', 'SA')])
    bsg_issuedate = fields.Date("Issue date", track_visibility='always')
    bsg_expirydate = fields.Date("Expiry date", track_visibility='always')
    bsg_dateofbirth = fields.Date("Date of Birth", track_visibility='always')
    bsg_job_pos = fields.Char("Job Position", track_visibility='always')
    bsg_arrivaldate = fields.Date("Arrival Date in Saudi", track_visibility='always')
    bsg_placeofissue = fields.Char("Place of Issue", track_visibility='always')
    bsg_department = fields.Many2one('hr.department',related='bsg_employee.department_id', string="Department", track_visibility='always')
    bsg_bloodgroup = fields.Selection([
        ('A+', 'A+'),
        ('B+', 'B+'),
        ('A-', 'A-'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),

    ], string="Blood Group", track_visibility='always')
    bsg_dependent = fields.Boolean("Dependent", track_visibility='always')
    bsg_family = fields.One2many('hr.iqama.family', 'hif', string="Family Iqama", track_visibility='always')
    guarantor_id = fields.Many2one('bsg.hr.guarantor', track_visibility='always')
    bayan_issue_number = fields.Char("Bayan Issue Number", track_visibility='always', required=True)

    @api.constrains('bsg_iqama_name')
    def _check_bsg_iqama_name(self):
        for record in self:
            curr_obj = self.env[self._name].search(
                [('id', '!=', record.id), ('bsg_iqama_name', '=', record.bsg_iqama_name)])
            if curr_obj:
                raise ValidationError(
                    _('Your Entered Iqama number is already taken by another user %s' % curr_obj.bsg_employee.name))
            if record.bsg_iqama_name:
                if len(record.bsg_iqama_name) < 10:
                    raise UserError(_("Iqama ID No. number must be more than 10 digits."))

    #     @api.constrains('bsg_iqama_name')
    #     def check_bsg_iqama_name(self):
    #         iqama_id = self.env['hr.iqama'].search([('bsg_iqama_name','=',self.bsg_iqama_name),('id','!=',self.id)])
    #         if iqama_id:
    #             raise UserError(_("Your Entered Iqama number is already taken by another user"))

    @api.onchange('bsg_iqama_name')
    def iqama_regex(self):
        if (self.bsg_iqama_name):
            result = re.match('^(2)[0-9]?', self.bsg_iqama_name, flags=0)
            if (result):
                print("Match")
            else:
                print("Failed")
                raise UserError(_('Invalid Iqama Entry'))


class BsgHrIqamaFamily(models.Model):
    _name = 'hr.iqama.family'
    _description = "Iqama Family"

    bsg_name = fields.Char("Name")
    hif = fields.Char(string="Iqama NO")
    nif = fields.Many2one('hr.nationality', string="NID Reference")
    employee_id = fields.Many2one('hr.employee', string="Employee Reference")
    bsg_iqamanumber = fields.Char("Iqama Number")
    bsg_iqamaexpiry = fields.Date("Iqama Expiry")
    bsg_iqamaissueplace = fields.Char("Iqama Issues Place")
    dob = fields.Date(string="DOB",default=fields.Date.today())
    phone = fields.Char(string='Phone')
    is_emergency = fields.Boolean(string='Is Emergency?')
    bsg_relation = fields.Selection([('father', 'Father'),('mother', 'Mother'),('husband', 'Husband'),('wife', 'Wife'),('son', 'Son'), ('daughter', 'Daughter'), ('other', 'Other')], string="Relation")




class BsgHrGuarantor(models.Model):
    _name = 'bsg.hr.guarantor'

    no = fields.Char('Guarantor No')
    name = fields.Char('Guarantor Name')
