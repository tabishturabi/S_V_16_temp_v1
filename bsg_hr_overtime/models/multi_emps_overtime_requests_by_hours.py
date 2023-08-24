# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import math
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, timedelta, timezone
from pytz import timezone, UTC


class EmployeeOvertimeRequestByHours(models.Model):
    _name = 'hr.employee.overtime.by.hours'
    _description = 'To Manage Employee Overtime Requests By Total Hours'
    _inherit = 'mail.thread'
    _rec_name = 'sequence_number'

    sequence_number = fields.Char(string='Request NO', readonly=True, track_visibility='always')
    name = fields.Char(string='Request Name',required=True,track_visibility='always')
    state = fields.Selection([('draft','Draft'),('submitted','Submitted'),('approved','Approved'),('overtime_generated','Overtime Generated')],default='draft',track_visibility='always')
    date_from = fields.Datetime(string='From',required=True,track_visibility='always')
    date_to = fields.Datetime(string='To',required=True,track_visibility='always')
    manager = fields.Many2one('res.users',string='Manager')
    description =fields.Char(string='Description',track_visibility='always')
    manager_comment = fields.Text(string='Comment By Manager',track_visibility='always')
    overtime_line = fields.One2many('hr.employee.overtime.line.by.hours','overtime_rel')
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
    total_hours_payslip_reimburse = fields.Boolean(string='Reimburse in payslip')
    overtime_ids = fields.One2many('hr.overtime','emp_overtime_batch_by_hours')

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
        super(EmployeeOvertimeRequestByHours, self).write(vals)
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
          


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('multisequencecode')
        user = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('id', '=', self.env.user.id)])
        branch_number = user.user_branch_id.branch_no
        if branch_number:
            vals['sequence_number'] = "OTBR%s%s" % (branch_number, seq)
        else:
            vals['sequence_number'] = "OTBR%s" % (seq)
        return super(EmployeeOvertimeRequestByHours, self).create(vals)

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for overtime in self:
            if overtime.date_to < overtime.date_from:
                   raise ValidationError(_('Date from can not be greater than date to'))
            '''domain = [
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
                    rec._check_date()''' 

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
                for line in rec.overtime_line:
                    if line:
                        overtime_id = rec.env['hr.overtime'].create({
                            'name': rec.name,
                            'employee_name': line.employee_id.id,
                            'state': 'approved',
                            'date_from': rec.date_from,
                            'date_to': rec.date_to,
                            'manager':rec.manager.id,
                            'description': rec.description,
                            'manager_comment': rec.manager_comment,
                            'overtime_coefficient': rec.overtime_coefficient,
                            'report_nextslip': rec.report_nextslip,
                            'emp_overtime_batch_by_hours':rec.id,
                            'allow_overtime_per_employee':True,
                                            })
                        overtime_id._onchange_employee_name()
                        overtime_line_id = rec.env['hr.overtime.line'].create({
                                    'overtime_rel':overtime_id.id,
                                    'ovt_hours' : line.overtime,
                                    'approved_hours' : line.approved_hours,
                                    'description': line.description,
                                    'overtime': line.overtime,
                                    'per_hour_sallary':overtime_id.per_hour,
                                    'overtime_coefficient': line.overtime_coefficient,
                                    'total_overtime': line.total_overtime
                                })
                        overtime_line_id.compute_overtime_hours()        
            rec.state = 'overtime_generated'


    # Import overtime lines 
    #@api.multi
    def import_overtime_lines(self):
        view_id = self.env.ref('bsg_hr_overtime.wizard_import_overtime_lines').id
        return {
                'type': 'ir.actions.act_window',
                'name': 'Name',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'import.overtime.lines',
                'view_id': view_id,
                'target': 'new',
                'context': {
                    'default_overtime_hour_id': self.id,
                    }
            }

class EmployeeOvertimeLineByHours(models.Model):
    _name='hr.employee.overtime.line.by.hours'
    _description = 'To Manage Employee Overtime Requests Line By Total Hours'

    overtime_rel = fields.Many2one('hr.employee.overtime.by.hours')
    employee_id = fields.Many2one('hr.employee',string='Employee',required=True,track_visibility='always')
    description = fields.Char(string='Description')
    overtime =  fields.Float(string='Overtime Hours')
    approved_hours = fields.Float(string='Approved Hours')
    overtime_coefficient = fields.Float(string='Overtime Coefficient')
    total_overtime = fields.Float(string='Total Overtime',compute='compute_overtime')
    report_nextslip = fields.Boolean(string='Report in next payslip')
    payslip_reimburse = fields.Boolean(string='Reimburse in payslip')
    mode = fields.Selection([('by_branch','By Branch'),('by_company','By Company'),('by_department','By Department'),
                             ('by_employee','By Employee Tag')],default='by_department',string='Mode')

    @api.depends('approved_hours', 'overtime')
    def compute_overtime(self):
        for rec in self:
                rec.total_overtime = rec.approved_hours * rec.overtime_coefficient
    
    @api.onchange('overtime')
    def onchange_overtime_hours(self):
        for rec in self:
            if rec.approved_hours == 0.0:
                rec.approved_hours = rec.overtime


    @api.onchange('mode')
    def onchange_mode(self):
        for rec in self:
            rec.employee_id = False
            if rec.mode=='by_department':
                    return{'domain':{'employee_id':[('id','not in',rec.overtime_rel.overtime_line.mapped('employee_id').ids),('department_id','!=',False),('department_id','=',rec.overtime_rel.department.id)]}}
            if rec.mode == 'by_company':
                    return{'domain':{'employee_id':[('id','not in',rec.overtime_rel.overtime_line.mapped('employee_id').ids),('company_id','!=',False),('company_id','=',rec.overtime_rel.company.id)]}}
            if rec.mode == 'by_branch':
                    return {'domain': {'employee_id': [('id','not in',rec.overtime_rel.overtime_line.mapped('employee_id').ids),('branch_id', '!=',False),('branch_id', '=', rec.overtime_rel.branch.id)]}}
            if rec.mode == 'by_employee':
                    return {'domain': {'employee_id': [('id','not in',rec.overtime_rel.overtime_line.mapped('employee_id').ids),('category_ids', '!=', False),('category_ids', 'in', rec.overtime_rel.employee_tag.id)]}}            

























