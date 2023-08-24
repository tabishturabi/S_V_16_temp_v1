# -*- coding: utf-8 -*-
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CustodyRequest(models.Model):
    """"""
    _name = 'custody.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'asset_id'
    _description = "Custody Request"

    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submitted'), ('approve', 'Approved'),
                              ('assign', 'Assigned'), ('return', 'Returned'), ('refuse', 'Refused'),
                              ('cancel', 'Cancelled')], string='Status', default='draft', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    is_intangible = fields.Boolean(string="Is Intangible?")
    department_id = fields.Many2one("hr.department", related="employee_id.department_id", string="Department")
    manager_id = fields.Many2one("hr.employee", related="employee_id.parent_id", string="Manager")
    employee_job = fields.Many2one("hr.job", related="employee_id.job_id", string="Job Position")
    employee_no = fields.Char(related="employee_id.driver_code", string="Employee No")
    asset_id = fields.Many2one('account.asset', domain=[('asset_type', '=', 'purchase'), ('state', '=', 'open'),('employee_id', '=', False),('custody', '=', True)],
                               string="Asset", copy=False)
    asset_name = fields.Char(string="Asset Name")
    custody_asset_id = fields.Many2one('custody.asset', string="Custody Asset", copy=False)
    request_date = fields.Date(string="Request Date", default=fields.Date.today())
    assign_date = fields.Date(string="Assign Date", copy=False)
    return_date = fields.Date(string="Return Date", copy=False)
    desc = fields.Text(string="Description")
    clearance_in_leave = fields.Boolean(string="Clearance In Leave")


    def _get_default_delivered_by(self):
        delivered_by = self.env["hr.employee"].search([('user_id','=',self.env.user.id)],limit=1)
        return delivered_by

    def _get_default_delivered_by_dept(self):
        delivered_by = self.env["hr.employee"].search([('user_id','=',self.env.user.id)],limit=1)
        return delivered_by.department_id

    delivered_by = fields.Many2one("hr.employee",string="Delivered By",readonly=True,default=_get_default_delivered_by)
    returned_by = fields.Many2one("hr.employee",string="Returned By",readonly=True)
    returned_by_dept_id = fields.Many2one("hr.department", string="Returned By Department", readonly=True)
    delivered_by_dept_id = fields.Many2one("hr.department",string="Delivered By Department",readonly=True,default=_get_default_delivered_by_dept)
    approved_by = fields.Many2one("hr.employee", string="Approved By", readonly=True)
    approved_by_dept_id = fields.Many2one("hr.department", string="Approved By Department",readonly=True)
    submit_check = fields.Boolean(string="Submit Check",compute="get_submit_check")
    approve_check = fields.Boolean(string="Approve Check",compute="get_approve_check")
    return_check = fields.Boolean(string="Return Check",compute="get_return_check")

    def get_submit_check(self):
        for rec in self:
            if rec.create_uid.id == rec.env.user.id or rec.env.user.has_group('bsg_hr.group_branch_supervisor') or rec.env.user.has_group('bsg_hr.group_department_manager'):
                rec.submit_check = True
            else:
                rec.submit_check = False

    def get_approve_check(self):
        for rec in self:
            if rec.create_uid.id == rec.env.user.id or rec.env.user.has_group('bsg_hr.group_branch_supervisor') or rec.env.user.has_group('bsg_hr.group_department_manager') or rec.env.user.has_group('hr_custody.group_custody_request_approve'):
                rec.approve_check = True
            else:
                rec.approve_check = False

    def get_return_check(self):
        for rec in self:
            if rec.create_uid.id == rec.env.user.id or rec.env.user.has_group('bsg_hr.group_branch_supervisor') or rec.env.user.has_group('bsg_hr.group_department_manager') or rec.env.user.has_group('hr_custody.group_custody_request_return'):
                rec.return_check = True
            else:
                rec.return_check = False



    def action_submit(self):
        for rec in self:
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            approved_by = self.env["hr.employee"].search([('user_id', '=', rec.env.user.id)], limit=1)
            rec.approved_by = approved_by
            rec.approved_by_dept_id = approved_by.department_id
            rec.state = 'approve'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_assign(self):
        for rec in self:
            old_custody_asset = self.env['custody.asset'].search([('asset_id', '=', rec.asset_id.id)])
            if not old_custody_asset:
                new_custody_asset = self.env['custody.asset'].create({
                    "asset_id": rec.asset_id.id,
                })
                rec.custody_asset_id = new_custody_asset.id
            else:
                rec.custody_asset_id = old_custody_asset.id
            if rec.asset_id:
                rec.asset_id.employee_id = rec.employee_id.id
            rec.assign_date = fields.Date.today()
            rec.state = 'assign'

    def action_return(self):
        for rec in self:
            if rec.asset_id:
                rec.asset_id.employee_id = False
            rec.return_date = fields.Date.today()
            returned_by = self.env["hr.employee"].search([('user_id', '=', rec.env.user.id)], limit=1)
            rec.returned_by = returned_by
            rec.returned_by_dept_id = returned_by.department_id
            rec.state = 'return'

    def action_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'


class CustodyAsset(models.Model):
    """"""
    _name = 'custody.asset'
    _rec_name = 'asset_id'
    _description = "Custody Asset"

    asset_id = fields.Many2one('account.asset', string="Asset")
    # Migration Note
    # asset_model_id = fields.Many2one('account.asset.category', string="Asset Model", related="asset_id.category_id")
    asset_model_id = fields.Selection([('sale', 'Deferred Revenue'), ('expense', 'Deferred Expense'), ('purchase', 'Asset')], string="Asset Model", related="asset_id.asset_type")
    custody_request_ids = fields.One2many('custody.request', 'custody_asset_id', string="Custodies")


class AccountAsset(models.Model):
    """"""
    _inherit = 'account.asset'

    custody = fields.Boolean(string="Custody", default=False)
    employee_id = fields.Many2one('hr.employee', string="Employee")


class HrEmployee(models.Model):
    """"""
    _inherit = 'hr.employee'

    custody_count = fields.Integer(string="Custodies", compute="_get_custody_count")

    def _get_custody_count(self):

        """"""
        for rec in self:
            rec.custody_count = self.env["custody.request"].search_count([('employee_id', '=', rec.id),
                                                                       ('state', '=', "assign")])

    def action_get_custody(self):
        # This function is action to view employee custodies
        custodies = self.env["custody.request"].search([('employee_id', '=', self.id),
                                                              ('state', '=', "assign")])
        return {
            'name': '{} Custodies'.format(self.name),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'custody.request',
            'domain': [('employee_id', 'in', custodies.mapped('employee_id.id'))]
        }
