# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import math
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, timedelta, timezone
from pytz import timezone, UTC


class EmployeeOvertimeRequest(models.Model):
    _name = 'hr.employee.overtime'
    _description = 'To Manage Multi Employee Overtime Requests'
    _inherit = 'mail.thread'
    _rec_name = 'sequence_number'

    sequence_number = fields.Char(string='Request NO', readonly=True, track_visibility='always')
    name = fields.Char(string='Request Name',required=True,track_visibility='always')
    employee_name= fields.Many2many('hr.employee',string='Employee Name',required=True,track_visibility='always')
    state = fields.Selection([('draft','Draft'),('submitted','Submitted'),('approved','Approved'),('overtime_generated','Overtime Generated')],default='draft',track_visibility='always')
    date_from = fields.Datetime(string='From',required=True,track_visibility='always')
    date_to = fields.Datetime(string='To',required=True,track_visibility='always')
    manager = fields.Many2one('res.users',string='Manager')
    description =fields.Char(string='Description',track_visibility='always')
    manager_comment = fields.Text(string='Comment By Manager',track_visibility='always')
    overtime_line = fields.One2many('hr.employee.overtime.line','overtime_rel')
    subtotal = fields.Float(string='SubTotal', readonly=True, compute='_overtime_total')
    total_overtime = fields.Float(string='Total Overtime',readonly=True,compute='_overtime_total')
    mode = fields.Selection([('by_branch','By Branch'),('by_company','By Company'),('by_department','By Department'),
                             ('by_employee','By Employee Tag')],default='by_department',string='Mode')
    department = fields.Many2one('hr.department',string='Department')
    branch = fields.Many2one('bsg_branches.bsg_branches',string='Branch')
    company = fields.Many2one('res.company',string='Company')
    employee_tag = fields.Many2one('hr.employee.category',string='Employee Tag')
    overtime_coefficient = fields.Float(string='Overtime Coefficient',default=1.0)
    report_nextslip = fields.Boolean(string='Report in next payslip')
    multi_payslip_reimburse = fields.Boolean(string='Reimburse in payslip')

    #@api.multi
    @api.depends('overtime_line.overtime', 'overtime_line.total_overtime')
    def _overtime_total(self):
        for rec in self:
            overtime_lines = rec.overtime_line
            if overtime_lines:
                overtime = sum(overtime_lines.mapped('overtime'))
                total_overtime = sum(overtime_lines.mapped('total_overtime'))
                rec.update({
                    'subtotal': overtime,
                    'total_overtime': total_overtime,
                })
            else:
                rec.update({
                    'subtotal': 0.0,
                    'total_overtime': 0.0
                })
    #@api.multi
    def write(self, vals):
        super(EmployeeOvertimeRequest, self).write(vals)
        if self.overtime_line:
            for record in self.overtime_line:
                if record:
                    record.overtime_coefficient = self.overtime_coefficient
        return True

    @api.onchange('date_from','date_to')
    def onchange_default_time(self):
        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        
        if self.date_from:
           from_date_tz = UTC.localize(self.date_from).astimezone(tz).replace(hour=00, minute=00, second=00).replace(tzinfo=None)
           self.date_from  = tz.localize(from_date_tz).astimezone(UTC).replace(tzinfo=None)

        if self.date_to:
           to_date_tz = UTC.localize(self.date_to).astimezone(tz).replace(hour=23, minute=59, second=59).replace(tzinfo=None)
           self.date_to  = tz.localize(to_date_tz).astimezone(UTC).replace(tzinfo=None)
          

    #@api.multi
    @api.onchange('overtime_line')
    def onchange_line_date(self):
        list_dates = []
        for record in self.overtime_line:
            if len(list_dates) != 0:
                for dates in list_dates:
                    if dates['from_date'] <= record.to_date and dates['to_date'] > record.from_date:
                        raise ValidationError(_('You can not have period which overlap on previous one'))
            list_dates.append({
                'from_date': record.from_date,
                'to_date': record.to_date
            })
    @api.onchange('employee_tag','mode','department','company','branch')
    def onchange_mode(self):
        for rec in self:
            rec.employee_name = False
            if rec.mode=='by_department':
                if rec.department:
                    return{'domain':{'employee_name':[('department_id','=',rec.department.id)]}}
            if rec.mode == 'by_company':
                if rec.company:
                    return{'domain':{'employee_name':[('company_id','=',rec.company.id)]}}
            if rec.mode == 'by_branch':
                if rec.branch:
                    return {'domain': {'employee_name': [('branch_id', '=', rec.branch.id)]}}
            if rec.mode == 'by_employee':
                if rec.employee_tag:
                    return {'domain': {'employee_name': [('category_ids', '=', rec.employee_tag.id)]}}
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('morsequencecode')
        user = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('id', '=', self.env.user.id)])
        branch_number = user.user_branch_id.branch_no
        if branch_number:
            vals['sequence_number'] = "OTR%s%s" % (branch_number, seq)
        else:
            vals['sequence_number'] = "OTR%s" % (seq)
        return super(EmployeeOvertimeRequest, self).create(vals)

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for overtime in self:
            if overtime.date_to < overtime.date_from:
                   raise ValidationError(_('Date from can not be greater than date to'))
            domain = [
                ('date_from', '<=', overtime.date_to),
                ('date_to', '>', overtime.date_from),
                ('employee_name', '=', overtime.employee_name.ids),
                ('id', '!=', overtime.id),
            ]
            nrequests = self.env['hr.employee.overtime'].search_count(domain)
            if nrequests:
                raise ValidationError(_('You can not have 2 requests that overlaps on the same day.'))
            if  overtime.overtime_line:
                for rec in overtime.overtime_line:
                    rec._check_date() 

    def action_submit(self):
        if self.state == 'draft':
            self.state = 'submitted'
    def action_approve(self):
        if self.state == 'submitted':
            self.state = 'approved'

    #@api.multi
    def action_generate_overtime(self):
        for rec in self:
            if rec.state == 'approved':
                for employees in rec.employee_name:
                    if employees:
                        overtime_id = rec.env['hr.overtime'].create({
                            'name': rec.name,
                            'employee_name': employees.id,
                            'state': 'approved',
                            'date_from': rec.date_from,
                            'date_to': rec.date_to,
                            'manager':rec.manager.id,
                            'description': rec.description,
                            'manager_comment': rec.manager_comment,
                            'overtime_coefficient': rec.overtime_coefficient,
                            'report_nextslip': rec.report_nextslip,
                            'emp_overtime_batch':rec.id
                                            })
                        overtime_id._onchange_employee_name()
                        for overtime_line in rec.overtime_line:
                            if overtime_line:
                                rec.env['hr.overtime.line'].create({
                                    'overtime_rel':overtime_id.id,
                                    'from_date': overtime_line.from_date,
                                    'to_date': overtime_line.to_date,
                                    'description': overtime_line.description,
                                    'overtime': overtime_line.overtime,
                                    'approved_hours': overtime_line.overtime,
                                    'per_hour_sallary':overtime_id.per_hour,
                                    'overtime_coefficient': overtime_line.overtime_coefficient,
                                    'total_overtime': overtime_line.total_overtime
                                })
                                overtime_line.compute_overtime()
                rec.state = 'overtime_generated'

class EmployeeOvertimeLine(models.Model):
    _name='hr.employee.overtime.line'
    _description = 'Manage Multi Employee Overtime Line Requests'

    overtime_rel = fields.Many2one('hr.employee.overtime',string='Overtime Line')
    from_date = fields.Datetime(string='From Date')
    to_date = fields.Datetime(string='To Date')
    description = fields.Char(string='Description')
    overtime =  fields.Float(string='Overtime',compute='compute_overtime')
    overtime_coefficient = fields.Float(string='Overtime Coefficient')
    total_overtime = fields.Float(string='Total Overtime',compute='compute_overtime')
    report_nextslip = fields.Boolean(string='Report in next payslip')
    payslip_reimburse = fields.Boolean(string='Reimburse in payslip')

    @api.depends('from_date', 'to_date')
    def compute_overtime(self):
        for rec in self:
            if rec.from_date and rec.to_date:
                time1 = rec.to_date - rec.from_date
                duration_in_s = time1.total_seconds()
                minutes = divmod(duration_in_s, 60)[0]
                overtime = minutes / 60
                total_overtime = overtime * rec.overtime_coefficient
                rec.update({
                    'overtime': overtime,
                    'total_overtime': total_overtime
                })
            else:
                rec.update({
                    'overtime': 0.0,
                    'total_overtime': 0.0
                })

    @api.constrains('from_date','to_date')
    def _check_date(self):
        for rec in self:
            if rec.from_date and rec.to_date:
                if rec.to_date < rec.from_date:
                   raise ValidationError(_('Date from can not be greater than date to'))
                if (rec.from_date < rec.overtime_rel.date_from or rec.from_date > rec.overtime_rel.date_to) or (rec.to_date > rec.overtime_rel.date_to or rec.to_date < rec.overtime_rel.date_from):
                    raise ValidationError(_('You can not have dates out of the range of dates above.'))                    


























