# -*- coding: utf-8 -*-

from odoo import fields,api,models,_
from odoo.exceptions import Warning, ValidationError
import re

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    @api.model
    def _get_department_id(self):
        department_rec = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return department_rec.department_id.display_name
    
    @api.model
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee_rec.driver_code
    
    emp_id = fields.Char(string='Employee ID',default=_get_employee_id)
    user = fields.Char(string='Users',default=lambda self: self.env.user.name)
    branch = fields.Char(string='Branch',compute="_get_branch_id")
    department_id = fields.Char(string='Department',default=_get_department_id)
    app_name_id = fields.Many2one('app.config',string='App Name')
    type_id = fields.Many2one('type.config',string='Type')
    trip = fields.Char(string='Trip ID')
    so = fields.Char(string='SO #')
    importance = fields.Selection([('very_high','هام وعاجل جدا'),('high','عاجل'),('normal','عادي')],string='Importance',default='normal')
    attachment_id = fields.Many2many('ir.attachment',string='Attachment')
    root_cause_id = fields.Many2one('root.causes', string="Root Cause")
    customer_mobile = fields.Char(string="Customer Mobile", related="partner_id.mobile")
    user_last_response = fields.Char(string="User Last Response")

    # @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        # CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        raw_text = kwargs.get('body', False)
        message_type = kwargs.get('message_type', False)
        sub_type = kwargs.get('subtype', False)
        cleantext = ''
        if message_type == 'comment' and sub_type == 'mail.mt_comment':
            if raw_text:
                # cleantext = re.sub(CLEANR, '', kwargs.get('body', False))
                self.user_last_response = raw_text
        return super(HelpdeskTicket, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)


    # @api.multi
    def _get_branch_id(self):
        for rec in self:
            rec.branch = False
            employee_id = self.env['hr.employee'].search([('user_id', '=', rec.create_uid.id)], limit=1)
            if employee_id:
                rec.branch = employee_id.branch_id.branch_ar_name
    
    @api.model
    def create(self,vals):
        res = super(HelpdeskTicket,self).create(vals)
        if vals.get('attachment_id'):
            res.message_post(attachment_ids=res.attachment_id.ids)
        return res

    def write(self,vals):
        res = super(HelpdeskTicket,self).write(vals)
        if 'stage_id' in vals:
            if self.partner_id.id == self.env.user.partner_id.id:
                template_id = self.env.ref('bsg_helpdesk_operations.helpdesk_user_mail').id
                self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)
            if self.user_id.id == self.env.user.id:
                template_id = self.env.ref('bsg_helpdesk_operations.helpdesk_customer_mail').id
                email_template = self.env['mail.template'].browse(template_id)

    # @api.multi
    @api.onchange('stage_id')
    def root_cause_valid(self):
        if self.team_id.id in self.stage_id.team_ids.ids and self.stage_id.is_closed:
            if not self.root_cause_id:
                raise ValidationError(_("Root cause is required"))


class helpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'

    is_re_open = fields.Boolean("For Re-open")
    is_closed = fields.Boolean("For Closed Stage")

class HelpDeskRootCauses(models.Model):
    _name = 'root.causes'
    _description = "Help Desk Root Causes"

    name = fields.Char(string="Root Cause")

