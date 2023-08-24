# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
import math, time, babel
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from datetime import datetime, timedelta
from pytz import timezone, UTC


class EmployeeOvertime(models.Model):
    _name = 'hr.overtime'
    _description = 'To Manage Employee Overtime Requests'
    _inherit = 'mail.thread'
    _rec_name = 'sequence_number'

    @api.model
    def _default_my_employee_id(self):
        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        return self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)])

    sequence_number = fields.Char(string='Request NO', readonly=True, track_visibility='always')
    name = fields.Char(string='Request Name', required=True, track_visibility='always')
    employee_name = fields.Many2one('hr.employee', string='Employee', default=_default_my_employee_id, required=True,
                                    track_visibility='always')
    employee_id = fields.Char(string='Employee Code')
    emp_department = fields.Many2one('hr.department', string='Department')
    branch_name = fields.Many2one('bsg_branches.bsg_branches', string='Branch Name')
    job_position = fields.Many2one('hr.job', string='Job Position')
    resource_calendar_id = fields.Many2one('resource.calendar', 'Working Schedule')
    employee_tag_ids = fields.Many2many('hr.employee.category', string='Employee Tag')
    manager = fields.Many2one('hr.employee', string='Manager')
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'),
                              ('hr_salary_approve', 'HR Sallary Approved'),
                              ('hr_manager_approved', 'HR Manager Approved'), ('account_approved', 'Account Approved'),
                              ('audit_approved', 'Audit Approved'), ('fin_approved', 'Fin Approved'),
                              ('in_payroll', 'Payslip'),
                              ('posted', 'Posted'), ('paid', 'Paid'), ('cancel', 'Canceld')], default='draft',
                             track_visibility='always')
    company = fields.Many2one('res.company', string='Company')
    date_from = fields.Datetime(string='From', required=True, track_visibility='always')
    date_to = fields.Datetime(string='To', required=True, track_visibility='always')
    description = fields.Char(string='Description', track_visibility='always')
    manager_comment = fields.Text(string='Comment By Manager', track_visibility='always')
    refusal_reason = fields.Text(string='Reason To Refuse', track_visibility='always')
    priority = fields.Selection(
        [('low', 'Low Priority'), ('low_priority', 'Low Priority'), ('medium', 'Medium Priority'),
         ('high', 'High Priority')], track_visibility='always', default='low')
    wage_sallary = fields.Integer(string='Wage Sallary')
    per_hour = fields.Float(string='Salary Per Hour')
    overtime_coefficient = fields.Float(string='Overtime Coefficient', default=1.0)
    report_nextslip = fields.Boolean(string='Report in next payslip')
    generate_from_attendance = fields.Boolean(string='Generate From Attendance')
    allow_overtime_per_employee = fields.Boolean(string='Allow Total Overtme Hours')
    overtime_line = fields.One2many('hr.overtime.line', 'overtime_rel')
    subtotal = fields.Float(string='Hours', readonly=True, compute='_overtime_total')
    approved_hours = fields.Float(string='Approved Hours', readonly=True, compute='_overtime_total')
    total_overtime = fields.Float(string='Total Overtime', readonly=True, compute='_overtime_total')
    total_overtime_amount = fields.Float(string='Total Overtime Amount', readonly=True, compute='_overtime_total')

    posted_date = fields.Date('Posted Date')
    paid_date = fields.Date('Paid Date')
    journal_id = fields.Many2one('account.journal', 'Overtime Journal')
    payment_move_id = fields.Many2one('account.payment', string="Payment Entry", readonly=True)
    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)
    payslip_reimburse = fields.Boolean(string='Reimburse in payslip')
    emp_overtime_batch = fields.Many2one('hr.employee.overtime', string='Batch ID', readonly=True)
    emp_overtime_batch_by_hours = fields.Many2one('hr.employee.overtime.by.hours', string='Batch By Total Hours ID',
                                                  readonly=True)
    employee_readonly = fields.Boolean(default=False)
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    payslip_input_ids = fields.Many2many('hr.payslip.input', string="input")
    payslip_ids = fields.Many2one('hr.payslip', related='payslip_input_ids.payslip_id', string='Payslip', readonly=True,
                                  store=True)
    overtime_compute_salary_rule_id = fields.Many2one('hr.salary.rule',
                                                      related='company.overtime_compute_salary_rule_id',
                                                      string='Overtime Compute Rule', store=True)

    def get_month(self, date_from):
        locale = self.env.context.get('lang') or 'en_US'
        new_dates = tools.ustr(babel.dates.format_date(date=date_from, format='MMMM y', locale=locale))
        return new_dates

    def get_line_by_data_range(self, overtime_rel, date_condition, date_from, date_to):
        date_domain = [('overtime_rel', '=', overtime_rel.id)]
        if date_condition == 'equal':
            date_domain += [('from_date', '=', date_from), ('to_date', '=', date_to)]
        if date_condition == 'not_equal':
            date_domain += [('from_date', '!=', date_from), ('to_date', '!=', date_to)]
        if date_condition == 'after':
            date_domain += [('from_date', '>', date_from), ('to_date', '>', date_to)]
        if date_condition == 'before':
            date_domain += [('from_date', '<', date_from), ('to_date', '<', date_to)]
        if date_condition == 'after_equal':
            date_domain += [('from_date', '>=', date_from), ('to_date', '>=', date_to)]
        if date_condition == 'before_equal':
            date_domain += [('from_date', '<=', date_from), ('to_date', '<=', date_to)]
        if date_condition == 'between':
            date_domain += [('from_date', '>=', date_from), ('to_date', '<=', date_to)]
        overtime_line_ids = self.env['hr.overtime.line'].search(date_domain)
        return overtime_line_ids

    @api.onchange('overtime_coefficient')
    def _onchange_overtime_coefficient(self):
        self.overtime_line.write({'overtime_coefficient': self.overtime_coefficient})

    @api.onchange('employee_name')
    def _onchange_employee_name(self):
        if self.employee_name:
            self.employee_id = self.employee_name.employee_code
            self.emp_department = self.employee_name.department_id
            self.branch_name = self.employee_name.branch_id
            self.job_position = self.employee_name.job_id
            self.employee_tag_ids = self.employee_name.category_ids
            self.manager = self.employee_name.parent_id
            self.company = self.employee_name.company_id
            self.resource_calendar_id = self.employee_name.resource_calendar_id
            contract_id = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_name.id), ('state', '=', 'open')], limit=1)
            if contract_id and self.overtime_compute_salary_rule_id:
                rules = [(rule.id, rule.sequence) for rule in self.overtime_compute_salary_rule_id]
                data = self.employee_name.with_context({'rules': rules})._get_payslip_lines(contract_id,
                                                                                            payslip_id=None)
                # lines = [line['amount'] for line in self.employee_name.with_context({'rules':rules})._get_payslip_lines(contract_id, payslip_id=None)
                # if line['salary_rule_id'] ==  self.overtime_compute_salary_rule_id.id]
                if self.employee_name:
                    emp_gross = self.employee_name.line_ids.filtered(lambda i: i.code == 'GROSS').amount
                    emp_basic = self.employee_name.line_ids.filtered(lambda i: i.code == 'BASIC').amount
                    self.per_hour = ((emp_gross / 240) + (emp_basic / 240) * 0.5)
                else:
                    self.per_hour = 0

    #             else:
    #                 raise UserError(_('%s does not has contract in running state'%self.employee_name.name))

    @api.onchange('date_from', 'date_to')
    def onchange_default_time(self):
        tz = timezone(self.env.context.get('tz') or self.env.user.tz)

        if self.date_from:
            from_date_tz = UTC.localize(self.date_from).astimezone(tz).replace(hour=00, minute=00, second=00).replace(
                tzinfo=None)
            self.date_from = tz.localize(from_date_tz).astimezone(UTC).replace(tzinfo=None)

        if self.date_to:
            to_date_tz = UTC.localize(self.date_to).astimezone(tz).replace(hour=23, minute=59, second=59).replace(
                tzinfo=None)
            self.date_to = tz.localize(to_date_tz).astimezone(UTC).replace(tzinfo=None)

    #@api.multi
    def write(self, vals):
        super(EmployeeOvertime, self).write(vals)
        return True

    #@api.multi
    @api.depends('overtime_line.approved_hours', 'overtime_line.overtime', 'overtime_line.total_overtime',
                 'overtime_line.total_overtime_amount')
    def _overtime_total(self):
        for rec in self:
            if rec.overtime_line:
                rec.subtotal = sum(rec.overtime_line.mapped('overtime'))
                rec.approved_hours = sum(rec.overtime_line.mapped('approved_hours'))
                rec.total_overtime = sum(rec.overtime_line.mapped('total_overtime'))
                rec.total_overtime_amount = sum(rec.overtime_line.mapped('total_overtime_amount'))

            else:
                rec.subtotal = 0.0
                rec.approved_hours = 0.0
                rec.total_overtime = 0.0
                rec.total_overtime_amount = 0.0

    #@api.multi
    def generate_ovt_from_attendance(self):
        for rec in self:
            rec.overtime_line.unlink()
            attendance_records = self.env['hr.attendance'].search(
                [('check_in', '>=', rec.date_from), ('check_in', '<=', rec.date_to),
                 ('check_out', '<=', rec.date_to), ('check_out', '>=', rec.date_from),
                 ('employee_id', '=', rec.employee_name.id)])

            for attend in attendance_records:
                overtime_hours = 0.0
                date_from = attend.check_in.replace(hour=00, minute=00, second=00)
                date_to = attend.check_out.replace(hour=23, minute=59, second=59)
                results = rec.employee_name.get_work_days_data(date_from, date_to)
                if results['hours'] != 0:
                    if attend.worked_hours > results['hours']:
                        overtime_hours = attend.worked_hours - results['hours']
                    else:
                        continue
                else:
                    overtime_hours = attend.worked_hours
                if overtime_hours > 0:
                    ovt_date_from = fields.Datetime.from_string(attend.check_out)
                    ovt_date_from -= timedelta(hours=overtime_hours)
                    rec.overtime_line.create({'overtime_rel': rec.id,
                                              'from_date': ovt_date_from,
                                              'to_date': fields.Datetime.from_string(attend.check_out),
                                              'description': _('Generated From Attendance'),
                                              'per_hour_sallary': rec.per_hour,
                                              'overtime_coefficient': rec.overtime_coefficient,
                                              'approved_hours': overtime_hours,
                                              'overtime_duration': str(timedelta(hours=overtime_hours))
                                              })

    #@api.multi
    def attachment_tree_view(self):
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_hr_overtime.action_attachment')
        return res

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for overtime in self:
            overtime.doc_count = Attachment.search_count([
                ('res_model', '=', 'hr.overtime'), ('res_id', '=', overtime.id)
            ])

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('orsequencecode')
        user = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                         company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.user.id)])
        branch_number = user.user_branch_id.branch_no

        if branch_number:
            vals['sequence_number'] = "OTR%s%s" % (branch_number, seq)
        else:
            vals['sequence_number'] = "OTR%s" % (seq)

        return super(EmployeeOvertime, self).create(vals)

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for overtime in self:
            if overtime.date_to < overtime.date_from:
                raise ValidationError(_('Date from can not be greater than date to'))
            domain = [
                ('date_from', '<=', overtime.date_to),
                ('date_to', '>', overtime.date_from),
                ('employee_name', '=', overtime.employee_name.id),
                ('id', '!=', overtime.id),
            ]
            nrequests = self.env['hr.overtime'].search_count(domain)
            if nrequests:
                raise ValidationError(_('You can not have 2 requests that overlaps on the same day.'))
            if overtime.overtime_line:
                for rec in overtime.overtime_line:
                    rec._check_date()

    @api.constrains('employee_name')
    def _check_employee_contracr(self):
        if self.employee_name:
            emp_id = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_name.id), ('state', '=', 'open')])
            if not emp_id:
                raise ValidationError(_('%s does not has contract in running state' % self.employee_name.name))

    def action_submit(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'submitted'

    def action_approve(self):
        for rec in self:
            if rec.state == 'submitted':
                rec.state = 'approved'

    def action_reject(self):
        for rec in self:
            rec.state = 'draft'

    def action_hr_sallary_approve(self):
        for rec in self:
            if rec.state == 'approved':
                rec.state = 'hr_salary_approve'

    def action_hr_sallary_reject(self):
        for rec in self:
            if rec.state == 'approved':
                rec.state = 'submitted'

    def action_hr_manager_approve(self):
        for rec in self:
            if rec.state == 'hr_salary_approve':
                rec.state = 'hr_manager_approved'

    def action_hr_manager_reject(self):
        for rec in self:
            if rec.state == 'hr_salary_approve':
                rec.state = 'approved'

    def action_account_approve(self):
        for rec in self:
            if rec.state == 'hr_manager_approved':
                rec.state = 'account_approved'

    def action_account_reject(self):
        for rec in self:
            if rec.state == 'hr_manager_approved':
                rec.state = 'hr_salary_approve'

    def action_audit_approve(self):
        for rec in self:
            if rec.state == 'hr_manager_approved':
                rec.state = 'audit_approved'

    def action_audit_reject(self):
        for rec in self:
            if rec.state == 'hr_manager_approved':
                rec.state = 'hr_salary_approve'

    def action_fin_approve(self):
        for rec in self:
            if rec.state == 'audit_approved':
                rec.state = 'fin_approved'

    def action_fin_reject(self):
        for rec in self:
            if rec.state == 'audit_approved':
                rec.state = 'hr_manager_approved'

    def action_post(self):
        for rec in self:
            if rec.state == 'fin_approved':
                rec.state = 'posted'

    def action_pay(self):
        for rec in self:
            if rec.state == 'posted':
                rec.state = 'paid'

    def payroll_approve(self):
        for rec in self:
            rec.write({'state': 'in_payroll'})

    def payroll_reject(self):
        for rec in self:
            rec.write({'state': 'audit_approved'})


class OvertimeLine(models.Model):
    _name = 'hr.overtime.line'
    _description = 'Manage Employee Overtime Requests Line'

    overtime_rel = fields.Many2one('hr.overtime', string='Overtime Line', required=True, ondelete='cascade')
    from_date = fields.Datetime(string='From Date')
    to_date = fields.Datetime(string='To Date')
    description = fields.Char(string='Description')
    overtime = fields.Float(string='Overtime Hours', compute='compute_overtime_hours', store=True)
    overtime_duration = fields.Char('Duration')
    ovt_hours = fields.Float(string='Hours')
    approved_hours = fields.Float(string='Approved Hours')
    overtime_coefficient = fields.Float(string='Overtime Coefficient')
    total_overtime = fields.Float(string='Total Overtime Hours', compute='compute_overtime_amount')
    per_hour_sallary = fields.Float(string='Sallary Per Hour')
    total_overtime_amount = fields.Float(string='Total Overtime Amount', compute='compute_overtime_amount')
    payslip_reimburse = fields.Boolean(string='Reimburse in payslip')
    report_nextslip = fields.Boolean(string='Report in next payslip')

    @api.depends('from_date', 'to_date', 'ovt_hours')
    def compute_overtime_hours(self):
        for rec in self:
            if rec.overtime_rel.allow_overtime_per_employee:
                rec.overtime = rec.ovt_hours
                rec.approved_hours = rec.ovt_hours
            elif rec.from_date and rec.to_date:
                delta = rec.to_date - rec.from_date
                rec.overtime = delta.total_seconds() / 3600.0
                rec.overtime_duration = str(delta)
            else:
                rec.overtime = 0.0
                rec.approved_hours = 0.0
                rec.overtime_duration = '0.0'

    @api.onchange('overtime')
    def _onchange_overtime_hours(self):
        self.approved_hours = self.overtime

    @api.depends('approved_hours', 'overtime_coefficient')
    def compute_overtime_amount(self):
        for rec in self:
            total_overtime = rec.approved_hours * rec.overtime_coefficient
            total_overtime_amount = total_overtime * rec.per_hour_sallary
            rec.update({
                'total_overtime': total_overtime,
                'total_overtime_amount': total_overtime_amount
            })

    @api.constrains('from_date', 'to_date')
    def _check_date(self):
        for rec in self:

            if rec.from_date and rec.to_date:
                if rec.to_date < rec.from_date:
                    raise ValidationError(_('Date from can not be greater than date to'))
                if (rec.from_date < rec.overtime_rel.date_from or rec.from_date > rec.overtime_rel.date_to) or (
                        rec.to_date > rec.overtime_rel.date_to or rec.to_date < rec.overtime_rel.date_from):
                    raise ValidationError(_('You can not have dates out of the range of dates above.'))

            domain = [
                ('from_date', '<', rec.to_date),
                ('to_date', '>', rec.from_date),
                ('overtime_rel', '=', rec.overtime_rel.id),
                ('id', '!=', rec.id),
            ]
            no_vertime = self.search_count(domain)
            if no_vertime:
                raise ValidationError(_('You can not have 2 overtimes that overlaps on the same periods.'))
