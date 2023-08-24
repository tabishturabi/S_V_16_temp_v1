from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning as UserError
from datetime import datetime
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class HrDeputations(models.Model):
    _name = 'hr.deputations'
    _description = 'Employee Business Trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"
    _order = 'id desc'

    @api.model
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee_rec.id

    refusal_reason = fields.Text(string='Reason To Refuse',tracking=True, track_visibility='onchange')
    name = fields.Char(string='Name', default='New')
    employee_no = fields.Char(related='employee_id.driver_code', string='Employee No')

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True,
                                  default=_get_employee_id,
                                  states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id',
                                    store=True)
    job_id = fields.Many2one('hr.job', string='Job Position', related='employee_id.job_id', store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.user.company_id)
    country_id = fields.Many2one('res.country', string='Country', readonly=True,
                                 states={'draft': [('readonly', False)]})
    destination_country = fields.Many2one('res.country', string='Destination Country', readonly=True,
                                          states={'draft': [('readonly', False)]})
    from_city = fields.Many2one('res.city', string='From City', readonly=True, states={'draft': [('readonly', False)]})
    to_city = fields.Many2one('res.city', string='To City', readonly=True, states={'draft': [('readonly', False)]})
    deputation_type = fields.Selection([('internal', 'Internal'), ('external', 'External')], string='Deputation Type',
                                       default='internal', readonly=True,
                                       states={'draft': [('readonly', False)]})
    request_date = fields.Date('Request Date', default=fields.date.today(), readonly=True,
                               states={'draft': [('readonly', False)]})
    end_date = fields.Date('End Date', readonly=True,
                           states={'draft': [('readonly', False)]})
    from_date = fields.Date('From Date', readonly=True,
                            states={'draft': [('readonly', False)]})
    to_date = fields.Date('To Date', readonly=True, states={'draft': [('readonly', False)]})
    duration = fields.Integer(string='Duration', compute='_compute_duration')
    days_before = fields.Integer(string='Days Before', readonly=True, states={'draft': [('readonly', False)]})
    days_after = fields.Integer(string='Days after', readonly=True, states={'draft': [('readonly', False)]})
    travel_by = fields.Selection([('land', 'By Land'), ('air', 'By Air')], string='Travel By', readonly=True,
                                 states={'draft': [('readonly', False)]}, required=True)
    housing_by = fields.Selection(
        [('company', 'By Company'), ('employee', 'By Employee')], string='Hotel Reservation',
        readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    tansp_cost = fields.Selection([('company', 'By Company'), ('employee', 'By Employee Car')],
                                  string='Transportation', readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string='Description')
    end_report = fields.Text(string='Task Report')
    basic_allownce = fields.Float('Basic Allowance', compute="_compute_allownces", store=True)
    other_allownce = fields.Float('Other Allowance', compute="_compute_allownce_amount")
    total_amount = fields.Float('Total Amount', compute="_compute_allownce_amount")
    state = fields.Selection([('draft', 'Draft'), ('direct_manager', 'Direct Manager'),
                              ('hr_salary_accountant', 'HR Salary Accountant'),
                              ('hr_manager', 'HR Manager'), ('internal_audit', 'Internal Audit'),
                              ('finance_manager', 'Finance Manager'), ('accountant', 'Accountant'), ('done', 'Done')],
                             string='Status', required=True, default='draft', track_visibility='onchange')
    deputation_account = fields.Many2one('account.analytic.account', string="Analytic Account")
    line_ids = fields.One2many('hr.deputations.allownce.lines', 'deputation_id',
                               string='Deputation Lines', tracking=True, track_visibility='onchange', readonly=True,
                               states={'draft': [('readonly', False)]})
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')
    payment_ids = fields.One2many('account.payment', 'deputation_id')
    payment_count = fields.Integer(string='Payment count', default=0, compute='count_payments')
    ticket_count = fields.Integer(string='Tickets count', default=0, compute='count_tickets')
    move_id = fields.Many2one('account.move', string='Deputation Receipt', copy=False)
    receipt_count = fields.Integer(string="Receipts", default=1)
    # ticketing = fields.Selection([('company', 'By Company'), ('employee', 'Cash On Hand')], readonly=True,
    #                              string='Ticketing', states={'draft': [('readonly', False)]})
    distance = fields.Float(string="Distance")
    tranp_amount = fields.Float(string="Transportation Amount", compute="get_tranp_amount")
    ticket_cost = fields.Float(string="Company Tickets Cost")
    employee_ticket_cost = fields.Float(string="Employee Tickets Cost")
    book_ticket_check = fields.Boolean(compute="get_book_ticket_check", string="Book Ticket")
    is_by_hr = fields.Boolean(string="Is By HR")
    # is_ticket_created = fields.Boolean(string="Is Ticket Created ", default=False)


    @api.onchange('tansp_cost', 'travel_by')
    def change_distance(self):
        for rec in self:
            rec.distance = 0.00

    @api.onchange('travel_by')
    def change_travel_by(self):
        for rec in self:
            rec.employee_ticket_cost = 0.00
            rec.ticket_cost = 0.00

    def get_book_ticket_check(self):
        for rec in self:
            ticket_id = self.env['hr.ticket.request'].search([('deputation_id', '=', self.id)], limit=1)
            if ticket_id:
                rec.book_ticket_check = True
            else:
                rec.book_ticket_check = False

    @api.constrains('employee_id', 'from_date', 'to_date')
    def employee_deputation_repeat_valid(self):
        # for rec in self:
        #     deputation_ids = self.env['hr.deputations'].search([('employee_id','=',rec.employee_id.id)])
        #     if len(deputation_ids.filtered(lambda line: line.from_date <= rec.from_date or line.to_date >= rec.from_date)) > 1:
        #         raise ValidationError("Employee can not take more than one deputation in same period")
        #     if len(deputation_ids.filtered(lambda line: line.from_date <= rec.from_date or line.to_date <= rec.to_date)) > 1:
        #         raise ValidationError("Employee can not take more than one deputation in same period")
        #     # if deputation_ids > 1:
        #     #     raise ValidationError("Employee can not take more than one deputation in same period")
        #
        for rec in self:
            if self.env['hr.deputations'].search_count(
                    [('employee_id', '=', rec.employee_id.id), ('from_date', '<=', rec.from_date),
                     ('to_date', '>=', rec.from_date)]) > 1:
                raise ValidationError("Employee can not take more than one deputation in same period")
            elif self.env['hr.deputations'].search_count(
                    [('employee_id', '=', rec.employee_id.id), ('from_date', '<=', rec.to_date),
                     ('to_date', '>=', rec.to_date)]) > 1:
                raise ValidationError("Employee can not take more than one deputation in same period")
            elif self.env['hr.deputations'].search_count(
                    [('employee_id', '=', rec.employee_id.id), ('from_date', '>=', rec.from_date),
                     ('to_date', '<=', rec.to_date)]) > 1:
                raise ValidationError("Employee can not take more than one deputation in same period")

    @api.constrains('ticket_cost','employee_ticket_cost')
    def validate_travel_by(self):
        if self.travel_by == 'air' and (self.ticket_cost+self.employee_ticket_cost) <= 0:
            raise ValidationError("Employee ticket cost or company ticket cost should be more than zero")

    @api.constrains('distance')
    def validate_distance(self):
        if self.travel_by == 'land' and self.tansp_cost == 'employee':
            if self.distance <= 0:
                raise ValidationError("Distance must be more than zero in this case.")

    @api.depends('distance')
    def get_tranp_amount(self):
        for rec in self:
            kilometer_rate = self.env['ir.config_parameter'].sudo().get_param('hr_deputation.kilometer_rate')
            _logger.info('...kilometer_rate ' + str(kilometer_rate) + '  \\\\  ' + str(type(kilometer_rate)))
            rec.tranp_amount = float(kilometer_rate) * rec.distance

    @api.depends('payment_ids')
    def count_payments(self):
        for rec in self:
            rec.payment_count = len(rec.payment_ids)

    def count_tickets(self):
        for rec in self:
            rec.ticket_count = self.env['hr.ticket.request'].search_count([('deputation_id', '=', self.id)])

    def action_tickets_requests(self):
        return {
            'name': 'Tickets Booked',
            'domain': [('deputation_id', '=', self.id)],
            'res_model': 'hr.ticket.request',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    @api.onchange('duration')
    def onchange_duration(self):
        self._compute_allownce_amount()
        self._onchange_to_city()

    @api.onchange('to_city','housing_by')
    def _onchange_to_city(self):
        for rec in self:
            rec.line_ids = None
            lines = []
            basic_allow = self.env['hr.deputations.allownce'].search([('id', '>=', 0)])
            for basic in basic_allow:
                if rec.to_city.country_id in basic.counter_group.country_ids:
                    if rec.employee_id.job_id.id in basic.line_ids[0].job_ids.ids:
                        for allownce_type in basic.other_allownce_ids:
                            amount = 0.0
                            if allownce_type.amount_type == 'amount':
                                amount = allownce_type.amount
                            if allownce_type.amount_type == 'percentage':
                                if allownce_type.percentage_type == 'basic':
                                    amount = (self.employee_id.contract_id.wage * allownce_type.percentage) / 100
                                if allownce_type.percentage_type == 'allownce':
                                    amount = (self.basic_allownce * allownce_type.percentage) / 100
                            if allownce_type.name.housing:
                                if rec.housing_by == 'employee':
                                    amount = amount * (rec.duration - 1)
                                else:
                                    amount = 0
                            else:
                                amount = amount * rec.duration
                            line_vals = {'allownce_type': allownce_type.id,
                                         'amount': amount,
                                         }

                            lines.append((0, 0, line_vals))
            rec.line_ids = lines

    @api.depends('employee_id.job_id', 'deputation_type', 'duration', 'to_city.country_id', 'days_after', 'days_before','housing_by','employee_ticket_cost')
    def _compute_allownces(self):
        for rec in self:
            total = 0.0
            for line in rec.line_ids:
                total += line.amount
            rec.basic_allownce = total
            rec._onchange_to_city()

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("You can delete record in draft state only!"))
        return super(HrDeputations, self).unlink()

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id and not self.employee_id.job_id:
            raise ValidationError(_("Please Set job Position for this employee!!"))

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'hr.deputations'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for dept in self:
            dept.attachment_number = attachment.get(dept.id, 0)

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'hr.deputations'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'hr.deputations', 'default_res_id': self.id}
        return res

    def attach_document(self, **kwargs):
        pass

    @api.depends('line_ids', 'basic_allownce', 'tranp_amount','employee_ticket_cost')
    def _compute_allownce_amount(self):
        for rec in self:
            if rec.tranp_amount > 0 or rec.employee_ticket_cost > 0:
                rec.other_allownce = rec.tranp_amount + rec.employee_ticket_cost
            total_amount = rec.other_allownce + rec.basic_allownce
            rec.total_amount = total_amount

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id.partner_id.country_id:
            self.country_id = self.company_id.partner_id.country_id
            self.destination_country = self.company_id.partner_id.country_id
        if self.company_id.partner_id.city_id:
            self.from_city = self.company_id.partner_id.city_id
        deputation_account = self.env['ir.config_parameter'].sudo().get_param('hr_deputation.hr_deputation_account')
        acc = int(deputation_account)
        self.deputation_account = acc
        if self.employee_id and self.employee_id.contract_id.analytic_account_id:
            self.deputation_account = self.employee_id.contract_id.analytic_account_id.id

    #
    @api.onchange('deputation_type')
    def onchange_deputation_type(self):
        if self.deputation_type == 'external':
            self.destination_country = False
            self.to_city = False
        if self.deputation_type == 'internal':
            self.onchange_company_id()

    def action_confirm(self):
        seq = self.env['ir.sequence'].next_by_code('hr.deputations')
        self.state = 'direct_manager'
        self.name = seq

    def action_direct_manager_approve(self):
        self.state = 'hr_salary_accountant'

    def action_hr_salary_accountant_approve(self):
        # if self.travel_by == 'air' and self.ticketing == 'company' and self.ticket_count == 0:
        #     raise ValidationError("Ticket must be booked before salary accountant approval.")
        if self.employee_id.employee_type == 'foreign' and self.deputation_type == 'external':
            vals = {
                'request_for': 'employee',
                'travel_before_date': fields.date.today(),
                'exit_return_type': 'final',
                'employee_id': self.employee_id.id,
                'deputation_id': self.id,
            }
            hr_exit_return = self.env['hr.exit.return'].create(vals)
        if not self.book_ticket_check:
            if self.state == 'hr_salary_accountant' and self.travel_by == 'air':
                if self.ticket_cost > 0:
                    hr_ticket_request_type = self.env['hr.ticket.request.type'].search([('deputation_check', '=', True)], limit=1)
                    vals = {
                        'request_date': fields.date.today(),
                        'employee_id': self.employee_id.id,
                        'deputation_id': self.id,
                        'request_type': hr_ticket_request_type.id,
                        'ticket_cost': self.ticket_cost,
                        'ticket_date': fields.date.today(),
                        'mission_check': True,
                    }
                    self.env['hr.ticket.request'].create(vals)
                    # self.write({'is_ticket_created': True})
        self.state = 'hr_manager'

    def action_hr_manager_approve(self):
        self.state = 'internal_audit'

    def action_internal_audit_approve(self):
        self.state = 'finance_manager'

    def action_finance_manager_approve(self):
        self.state = 'accountant'

    # def action_finance_manager_approve(self):
    #     if not self.employee_id.address_id:
    #         raise ValidationError(_("Please add partner to selected employee firstly and try again."))
    #     elif not self.company_id.account_id:
    #         raise ValidationError(_("Please add deputation account in settings and try again."))
    # move_id = self.env['account.move'].sudo().create([
    #     {
    #         'invoice_date': self.request_date,
    #         'partner_id': self.employee_id.address_id.id,
    #         'date': self.request_date,
    #         'move_type': 'in_receipt',
    #         'ref': _('Deputation Cost For: {}').format(self.employee_id.name),
    #
    #         'line_ids': [
    #             (0, 0, {
    #                 'name': _('Deputation Cost For: {} - Period {} - {}').format(self.employee_id.name, self.from_date, self.to_date),
    #                 'partner_id': self.employee_id.address_id.id,
    #                 'account_id': self.employee_id.address_id.property_account_payable_id.id,
    #                 'analytic_account_id': self.deputation_account.id,
    #                 'price_unit': self.total_amount,
    #                 'credit': self.total_amount,
    #                 'exclude_from_invoice_tab': True,
    #             }
    #              ),
    #             (0, 0, {
    #                 'name': _('Deputation Cost For: {} - Period {} - {}').format(self.employee_id.name, self.from_date, self.to_date),
    #                 'partner_id': self.employee_id.address_id.id,
    #                 'account_id': self.company_id.account_id.id,
    #                 'analytic_account_id': self.deputation_account.id,
    #                 'price_unit': self.total_amount,
    #                 'debit': self.total_amount,
    #                 'account_internal_type': 'payable',
    #             }
    #              ),
    #         ],
    #     }
    # ])
    # payment_method = self.env.ref('account.account_payment_method_manual_in')
    # payment_id = self.env['account.payment'].create({
    #     'name': self.name,
    #     'payment_type': 'outbound',
    #     'partner_type': 'supplier',
    #     'partner_id': self.employee_id.address_id.id,
    #     'amount': self.total_amount,
    #     'petty_cash_id': self.id,
    #     'communication': self.description,
    #     'journal_id': self.company_id.journal_id.id,
    #     'payment_date': str(datetime.now()),
    #     'payment_method_id': payment_method.id})
    # # self.move_id = move_id.id
    # self.state = 'done'

    def action_view_receipt(self):
        move_obj = self.env.ref('account.view_move_form')
        return {'name': _("Deputation Cost Receipt"),
                'view_mode': 'form',
                'res_model': 'account.move',
                'view_id': move_obj.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': self.move_id.id,
                'context': {}}

    def action_draft(self):
        self.state = 'draft'

    # def action_cancel(self):
    #     self.write({'state': 'cancel'})

    @api.depends('from_date', 'to_date')
    def _compute_duration(self):
        for record in self:
            if record.from_date and record.to_date:
                record.duration = ((record.to_date + relativedelta(days=1)) - record.from_date).days
            else:
                record.duration = 0

    # def action_register_payment(self):
    #     action = self.env.ref('account.action_account_payments').read()[0]
    #     view_id = self.env.ref('account.view_account_payment_form').id
    #     action.update({'views': [(view_id, 'form')], })
    #     action['context'] = {
    #         'default_partner_id': self.employee_id.address_home_id.id,
    #         'default_payment_type': 'outbound',
    #         'default_amount': self.total_amount,
    #         'default_deputation_id': self.id,
    #         'default_journal_id': 11, 'default_ref': 'Business Trip %s' % self.name
    #     }
    #     return action

    # def action_create_ticket(self):
    #
    #     return {
    #         'name': _('Book Ticket'),
    #         'res_model': 'hr.ticket.request',
    #         'view_mode': 'form',
    #         'context': {
    #             'default_employee_id': self.employee_id.id,
    #             'default_deputation_id': self.id
    #
    #         },
    #         'target': 'new',
    #         'type': 'ir.actions.act_window',
    #     }

    def action_payment_view(self):
        pay_obj = self.env.ref('account.view_account_payment_form')
        paymemt = self.env['account.payment'].search_count([('deputation_id', '=', self.id)])
        payment_id = self.env['account.payment'].search([('deputation_id', '=', self.id)])
        if paymemt == 1:
            return {'name': _("Deputation Payment"),
                    'view_mode': 'form',
                    'res_model': 'account.payment',
                    'view_id': pay_obj.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'res_id': payment_id.id,
                    'context': {}}

    # def action_ticket_view(self):
    #     ticket_obj = self.env.ref('hr_deputation.hr_ticketing_form')
    #     ticket = self.env['hr.ticketing'].search_count([('deputation_id', '=', self.id)])
    #     ticket_id = self.env['hr.ticketing'].search([('deputation_id', '=', self.id)])
    #     if ticket == 1:
    #         return {'name': _("Deputation Ticket"),
    #                 'view_mode': 'form',
    #                 'res_model': 'hr.ticketing',
    #                 'view_id': ticket_obj.id,
    #                 'type': 'ir.actions.act_window',
    #                 'nodestroy': True,
    #                 'target': 'current',
    #                 'res_id': ticket_id.id,
    #                 'context': {}}


class AccountPayment(models.Model):
    _inherit = "account.payment"

    deputation_id = fields.Many2one('hr.deputations',
                                    string="Deputation", store=True)


class HrDeputationLines(models.Model):
    _name = 'hr.deputations.allownce.lines'

    _inherit = ['mail.thread']

    allownce_type = fields.Many2one('hr.deput.other.allownce')

    deputation_id = fields.Many2one('hr.deputations', 'Deputation')

    amount = fields.Float('Amount')

    @api.onchange('allownce_type')
    def onchange_allownce_type(self):

        if self.allownce_type.amount_type == 'amount':
            self.amount = self.allownce_type.amount
        if self.allownce_type.amount_type == 'percentage':
            if self.allownce_type.percentage_type == 'basic':
                amount = (self.deputation_id.employee_id.contract_id.wage * self.allownce_type.percentage) / 100
                self.amount = amount
            if self.allownce_type.percentage_type == 'allownce':
                amount = (self.deputation_id.basic_allownce * self.allownce_type.percentage) / 100
