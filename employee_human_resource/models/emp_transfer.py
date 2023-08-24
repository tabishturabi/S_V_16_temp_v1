# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class hrTransferJob(models.Model):
    _name = "hr.employee.job.transfer"
    _description = "Employee Job Transfer"
    _inherit = ['mail.thread']

    name = fields.Char(string='Reference', readonly=True)
    employee_id = fields.Many2one('hr.employee',required=True)
    job_id = fields.Many2one('hr.job', string="Current Job"
                             ,related="employee_id.job_id", readonly=True,)
    new_job_id = fields.Many2one('hr.job', string="New Job")
    state = fields.Selection(selection=[('draft', 'Draft'), ('direct_manager', 'Direct Manager Approve'),('hr_manager','Hr Manager Approve'),
                                        ('assistant_executive','Assistant Executive'),('executive_executive','Executive Director'),('done','Done') ], default='draft',track_visibility='onchange' )
    transfer_date = fields.Date(required=True, default=fields.Date.today())
    approve_date = fields.Date(readonly=True)
    notes = fields.Text()
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)',related="employee_id.country_id",readonly=1, groups="hr.group_hr_user")
    mobile_phone = fields.Char('Work Mobile',related="employee_id.mobile_phone",readonly=1,)
    work_email = fields.Char('Work Email',related="employee_id.work_email",readonly=1,)
    department_id = fields.Many2one('hr.department', 'Department',related="employee_id.department_id",readonly=1,)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.job.transfer.seq')
        return super(hrTransferJob, self).create(vals)

    def confirm(self):
        self.write({'state':'direct_manager'})

    def direct_manager(self):
        self.write({'state':'hr_manager'})

    def hr_manager(self):
        self.write({'state':'assistant_executive'})

    def assistant_executive(self):
        self.write({'state':'executive_executive'})

    def action_transfer(self):
        """
        Desc : Employee Transfer
        """
        self.employee_id.job_id = self.new_job_id.id
        self.write({'state': 'done','approve_date':fields.Date.today()})


