# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _

class HRTicketRequest(models.Model):
    """"""
    _name = 'hr.ticket.request'
    _inherit = 'mail.thread'

    TICKET_DEGREE = [
        ('first', 'First'),
        ('first_reduced', 'First Reduced'),
        ('economic', 'Economic'),
        ('business', 'Business'),
        ('other', 'Other')]

    @api.model
    def default_get(self, fields):
        result = super(HRTicketRequest, self).default_get(fields)
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1).id
        if employee_id:
            result['employee_id'] = employee_id
        return result

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Ticket Request")
    name = fields.Char(string='Name')
    state = fields.Selection(string='State', selection=[('draft', 'Draft'),
                                                        ('hr_manager', 'HR Manager'), ('done', 'Done'),
                                                        ('paid', 'Paid'),
                                                        ('cancel', 'Cancelled')], track_visibility='always',
                             default='draft')

    leave_request_id = fields.Many2one('hr.leave', store=True, string="Leave Request", track_visibility='always')
    vacation_start_date = fields.Datetime(string="Vacation Start Date", related='leave_request_id.date_from',
                                          readonly=True)
    vacation_end_date = fields.Datetime(string="Vacation End Date", related='leave_request_id.date_to', readonly=True)
    new_vacation_end_date = fields.Date(string="Unpaid Vacation End Date", related='leave_request_id.leave_date_to', readonly=True)
    request_more_than_balance = fields.Boolean("Request More Than Balance",related='leave_request_id.request_more_than_balance')

    vacation_duration = fields.Float(string="Vacation Duration", related='leave_request_id.number_of_days',
                                     readonly=True)
    payslip_id = fields.Many2one('hr.payslip', store=True, string="Payslip", track_visibility='always')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, store=True,
                                 string="Company", track_visibility='always')
    request_date = fields.Date(string='Request Date', default=fields.Date.today(), track_visibility='always')
    from_hr = fields.Boolean(string='Another Employee', default=False, track_visibility='always')
    employee_id = fields.Many2one('hr.employee', string='Employee', track_visibility='always')
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Job', track_visibility='always')
    # TODO
    nationality_id = fields.Many2one('res.country', related='employee_id.country_id', string='Nationality',
                                     track_visibility='always')
    bsg_passport = fields.Many2one('hr.passport', related='employee_id.bsg_passport', string='Passport Number',
                                   track_visibility='always')
    # passport_expiry_date = fields.Date(related='employee_id.bsg_passport.bsg_passport_expiry_date', string='Passport Expiration')
    request_for = fields.Selection([('employee', 'Employee'), ('family', 'Family'), ('all', 'All')], default='employee',
                                   string='Request For', track_visibility='always')
    request_type = fields.Many2one('hr.ticket.request.type', string='Request Type', track_visibility='always')
    ticket_check = fields.Boolean(string='Ticket Checking', related='request_type.ticket_check',
                                  track_visibility='always')
    mission_check = fields.Boolean(string='Mission/Training Not Holiday', track_visibility='always', default=True)
    air_line = fields.Many2one('hr.airline', string='Air Line', track_visibility='always')
    ticket_degree = fields.Selection(TICKET_DEGREE, default='first', string='Ticket Degree', track_visibility='always')
    travel_agent = fields.Many2one('res.partner', string='Travel Agent', track_visibility='always')
    ticket_cost = fields.Float(string='Ticket Cost', track_visibility='always')
    destination_id = fields.Many2one('hr.destination', string='Destination', track_visibility='always')
    ticket_date = fields.Date(string='Ticket Date', default=fields.Date.today(), track_visibility='always')
    attach_ids = fields.One2many('hr.ticket.attachment', 'ticket_request_id', string='Attachments',
                                 track_visibility='always')
    note = fields.Text(string='Notes', track_visibility='always')
    termination_id = fields.Many2one('hr.termination',string="Termination")
    deputation_id = fields.Many2one('hr.deputation')

    # override create method to passing sequnce on that
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.ticket.seq')
        return super(HRTicketRequest, self).create(vals)

    
    def action_cancel(self):
        self.write({'state': 'cancel'})

    
    def unlink(self):
        for rec in self:
            if rec.state not in 'draft':
                raise UserError(
                    'You cannot delete a ticket which is not in draft state')
        return super(HRTicketRequest, self).unlink()

    
    def action_submit(self):
        if self.ticket_cost <= 0:
            raise ValidationError(_("Pls make sure ticket cost should be more than zero"))
        self.write({'state': 'hr_manager'})

    
    def action_hr_manager_approve(self):
        if self.ticket_cost <= 0:
            raise ValidationError(_("Pls make sure ticket cost should be more than zero"))
        if self.leave_request_id.issue_ticket_by_company:
            if not self.request_type.account_debit_id:
                raise ValidationError(_("Pls make sure to set Debit Account on request type"))
            if not self.request_type.journal_id:
                raise ValidationError(_("Pls make sure to set Journal ID on request type"))
            move_id = self.env['account.move'].create({
                'ref': self.employee_id.name,
                'date': datetime.today(),
                'journal_id': self.request_type.journal_id.id,
                'state': 'draft',
                'line_ids': [(0, 6, {'name': self.employee_id.name + _('Ticket Amount'),
                                     'due_date': datetime.today(),
                                     'bsg_branches_id': self.employee_id.branch_id.id,
                                     'department_id': self.employee_id.department_id.id,
                                     'account_id': self.request_type.account_debit_id.id,
                                     'debit': self.ticket_cost,
                                     'credit': 0.0,
                                     }),
                             (0, 6, {'name': self.employee_id.name + _('Ticket Amount'),
                                     'due_date': datetime.today(),
                                     'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,
                                     'bsg_branches_id': self.employee_id.branch_id.id,
                                     'department_id': self.employee_id.department_id.id,
                                     'account_id': self.request_type.journal_id.default_account_id.id,
                                     'debit': 0.0,
                                     'credit': self.ticket_cost,
                                     })]})
            move_id.post()
            self.write({'state': 'paid'})

        else:
            self.write({'state': 'done'})


class AirLine(models.Model):
    _name = 'hr.airline'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name')
    code = fields.Char('Code')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, sgtore=True,
                                 string="Company")


class HRTicketAttachment(models.Model):
    _name = 'hr.ticket.attachment'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name')
    file = fields.Binary(string='File Content')
    ticket_request_id = fields.Many2one('hr.ticket.request', string='Ticket Request')


class HRTicketRequestType(models.Model):
    """"""
    _name = 'hr.ticket.request.type'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name')
    ticket_check = fields.Boolean(string='Ticket Checking', default=False)
    deputation_check = fields.Boolean(string='Deputation Checking', default=False)
    allowance_name = fields.Many2one('hr.salary.rule', string='Allowance Name')
    account_debit_id = fields.Many2one('account.account', string='Account Debit')
    journal_id = fields.Many2one('account.journal', string='Journal', track_visibility=True)


class HRDestination(models.Model):
    """"""
    _name = 'hr.destination'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name')
    code = fields.Char('Code')
    country_id = fields.Many2one('res.country', string='Counter')
    destination_line_ids = fields.One2many('hr.destination.line', 'destination_id', string='Destination Line')


class HRDestinationLine(models.Model):
    """"""
    _name = 'hr.destination.line'
    _inherit = 'mail.thread'

    destination_id = fields.Many2one('hr.destination', string='Destination')
    class_id = fields.Many2one('hr.destination.class', string='Ticket Class')
    price = fields.Float(string='Price')


class HRDestinationClass(models.Model):
    _name = 'hr.destination.class'
    _inherit = 'mail.thread'

    name = fields.Char(string='Class Name')
