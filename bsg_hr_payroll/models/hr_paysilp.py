# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero


WORK_DAY_PER_MONTH = 30

class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    description = fields.Text('Description')


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    def _get_partner_id(self, credit_account):
        """
        overridden because every employee has a partner
        """
        return self.employee_id.partner_id.id or False


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread']
    journal_id = fields.Many2one('account.journal', 'Salary Journal', readonly=True, required=True,
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['account.journal'].search([('code', '=', 'SALRY')],
                                                                                         limit=1),
                                 domain=[('code', '=', 'SALRY')])
    job_id = fields.Many2one('hr.job', string="Job Position")
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string="Branch")
    department_id = fields.Many2one('hr.department', string="Department")
    salary_payment_method = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], string="Salary Payment Method")
    # employee_state = fields.Selection([
    #     ('on_job', 'On Job'),
    #     ('on_leave', 'On leave'),
    #     ('return_from_holiday', 'Return From Holiday'),
    #     ('resignation', 'Resignation'),
    #     ('suspended', 'Suspended'),
    #     ('service_expired', 'Service Expired'),
    #     ('ending_contract_during_trial_period', 'Ending Contract During Trial Period')], string='Employee State')
    employee_state = fields.Selection([
        ('on_job', 'On Job'),
        ('on_leave', 'On leave'),
        ('return_from_holiday', 'Return From Holiday'),
        ('resignation', 'Resignation'),
        ('suspended', 'Suspended'),
        ('service_expired','Service Expired'),
        ('contract_terminated', 'Contract Terminated'),
        ('ending_contract_during_trial_period','Ending Contract During Trial Period'),
        ('deceased', 'Deceased'),
        ('suspended_case', 'Suspended for Case'),

    ], string='Employee State')
    category_ids = fields.Many2many(
        'hr.employee.category',
        string='Tags')
    category_id = fields.Many2one(
        'hr.employee.category',
        string='Tag')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* If the payslip is paid then status is set to \'Paid\'.
                \n* When user cancel payslip the status is \'Rejected\'.""", track_visibility='onchange')

    total_net = fields.Float('Total Net', compute="_compute_total_net", readonly=True, store=True)
    payment_move_id = fields.Many2one('account.move', string="Payment Entry", readonly=True)
    description = fields.Text('Description', readonly=True, states={'draft': [('readonly', False)]})
    pay_by_branch = fields.Boolean(string="Pay By Branch")
    pay_by_branch_check = fields.Boolean(string="Pay By Branch Check", compute="get_pay_branch_check")
    pay_by_branch_id = fields.Many2one('bsg_branches.bsg_branches', string="Pay By Branch ID")
    leave_request_id = fields.Many2one('hr.leave', string="Leave Request", track_visibility=True)
    details_by_salary_rule_category = fields.One2many('hr.payslip.line','slip_id',
                                                      compute='_compute_details_by_salary_rule_category',
                                                      string='Details by Salary Rule Category')

    # @api.multi
    def _compute_details_by_salary_rule_category(self):
        for payslip in self:
            payslip.details_by_salary_rule_category = payslip.mapped('line_ids').filtered(lambda line: line.category_id)

    @api.depends('leave_request_id', 'state')
    def get_pay_branch_check(self):
        for rec in self:
            rec.pay_by_branch_check = False
            if not rec.leave_request_id or rec.state != 'done':
                rec.pay_by_branch_check = True
            else:
                rec.pay_by_branch_check = False


    @api.onchange('pay_by_branch')
    def onchange_pay_by_branch(self):
        if not self.pay_by_branch:
            if self.pay_by_branch_id:
                self.pay_by_branch_id = False








    @api.model
    def create(self, vals):
        res = super(HrPayslip, self).create(vals)
        if vals.get('employee_id', False):
            res.branch_id = res.employee_id.branch_id.id
            res.job_id = res.employee_id.job_id.id
            res.department_id = res.employee_id.department_id.id
        return res

    def get_days_diff(self, joining_date, payslip_from_date):
        if not joining_date or not payslip_from_date:
            return 30
        if joining_date >= payslip_from_date:
            delta = (joining_date - payslip_from_date)
        else:
            delta = (payslip_from_date - joining_date)
        return delta.days

    
    def write(self, vals):
        res = super(HrPayslip, self).write(vals)
        if vals.get('employee_id', False):
            self.branch_id = self.employee_id.branch_id.id
            self.job_id = self.employee_id.job_id.id
            self.department_id = self.employee_id.department_id.id
        return res

    @api.onchange('employee_id')
    def onchange_employee_reset_category_ids(self):
        if self.employee_id:
            category_ids = self.employee_id.category_ids
            if category_ids:
                self.category_ids = [(6, 0, category_ids.ids)]
            self.employee_state = self.employee_id.employee_state
            self.salary_payment_method = self.employee_id.salary_payment_method
            self.branch_id = self.employee_id.branch_id.id or False
            self.job_id = self.employee_id.job_id.id or False
            self.department_id = self.employee_id.department_id.id or False
        else:
            self.category_ids = []
            self.branch_id = False
            self.job_id = False
            self.department_id = False
        return

    
    @api.depends('line_ids')
    def _compute_total_net(self):
        for rec in self:
            if rec.exists() and rec.env.context.get('eos_hr_termination') and rec.hr_termination_id and rec.type == 'eos':
                rec.update({'total_net' : rec.hr_termination_id.total_eos_amount})
            else:
                net = rec.line_ids and rec.line_ids.filtered(lambda line: line.code == 'NET').total or 0.0
                rec.total_net = net

    
    def set_to_paid(self):
        for rec in self:
            rec.write({'state': 'paid'})

    
    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        no_batch_total_update = self._context.get('no_batch_total_update', False)
        for rec in self:
            if rec.payslip_run_id and not no_batch_total_update:
                net_total = sum(rec.payslip_run_id.slip_ids.mapped('total_net'))
                rec.payslip_run_id.batch_net_total = net_total

        return res

    def get_department_parent(self, department_id):
        if not department_id.parent_id:
            return department_id
        return self.get_department_parent(department_id.parent_id)






    
    def action_payslip_done(self):
        no_compute = self._context.get('no_compute', False)
        for slip in self:
            print('.............slip...........',slip)
            analytic_account_id = False
            department_id = slip.employee_id.department_id and slip.get_department_parent(
                slip.employee_id.department_id) or False
            contract_id = slip.contract_id
            branch_id = slip.employee_id.branch_id
            fleet_vehicle_id = slip.employee_id.vehicle_sticker_no and self.env['fleet.vehicle'].search(
                [('taq_number', '=', slip.employee_id.vehicle_sticker_no), ('company_id', '=', slip.employee_id.company_id.id)]) or False
            if slip.type == 'holiday':
                allowance = slip
                allowance_lines = self.sudo().with_context({'leave_id': self.id})._get_payslip_lines_by_holiday(
                    allowance.contract_id.ids, allowance.id)
                number = allowance.number or self.env['ir.sequence'].next_by_code('salary.slip')
                if allowance_lines:
                    if allowance.line_ids:
                        allowance.line_ids.unlink()
                    lines = [(0,0, line) for line in allowance_lines]
                    allowance.write({'line_ids': lines, 'number': number})
            else:
                if not no_compute:
                    if not slip.type == 'eos':
                        slip.compute_sheet()
            slip.write({'state': 'done'})
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = slip.date or slip.date_to
            currency = slip.company_id.currency_id or slip.journal_id.company_id.currency_id

            name = _('Payslip of %s') % (slip.employee_id.name)
            move_dict = {
                'narration': name,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'date': date,
                'move_type':'entry',
            }
            for line in slip.sudo().details_by_salary_rule_category:
                amount = currency.round(slip.credit_note and -line.total or line.total)
                if currency.is_zero(amount):
                    continue
                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if debit_account_id:
                    if slip.type == 'holiday':
                        if line.salary_rule_id.is_get_from_leave:
                            debit_account_id = line.salary_rule_id.leave_debit_account_id.id
                        else:
                            debit_account_id = line.salary_rule_id.account_debit.id
                    analytic_account_id = False
                    if line.salary_rule_id.account_debit.account_type in ['income','income_other','expense','expense_direct_cost']:
                        analytic_account_id = contract_id.analytic_account_id and contract_id.analytic_account_id.id or False
                    print('............asdad.analytic_account_id.........',analytic_account_id)
                    debit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=False),
                        'account_id': debit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                        'analytic_distribution': {analytic_account_id: 100},
                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
                        'department_id': analytic_account_id and department_id and department_id.id or False,
                        'bsg_branches_id': analytic_account_id and branch_id and branch_id.id or False,
                        'fleet_vehicle_id': analytic_account_id and fleet_vehicle_id and fleet_vehicle_id.id or False,

                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                if credit_account_id:
                    if slip.type == 'holiday':
                        if line.salary_rule_id.is_get_from_leave:
                            credit_account_id = line.salary_rule_id.leave_credit_account_id.id
                        else:
                            credit_account_id = line.salary_rule_id.account_credit.id
                    analytic_account_id = False
                    if line.salary_rule_id.account_credit.account_type in ['income','income_other','expense','expense_direct_cost']:
                        analytic_account_id = contract_id.analytic_account_id and contract_id.analytic_account_id.id or False
                    print('.......dsdsdsd.....asdad.analytic_account_id.........', analytic_account_id)
                    credit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=True),
                        'account_id': credit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                        'analytic_distribution': {analytic_account_id: 100},
                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
                        'department_id': analytic_account_id and department_id and department_id.id or False,
                        'bsg_branches_id': analytic_account_id and branch_id and branch_id.id or False,
                        'fleet_vehicle_id': analytic_account_id and fleet_vehicle_id and fleet_vehicle_id.id or False,
                    })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            if currency.compare_amounts(credit_sum, debit_sum) == -1:
                acc_id = slip.journal_id.default_account_id.id
                if not acc_id:
                    raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (
                        slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': 0.0,
                    'credit': currency.round(debit_sum - credit_sum),
                })
                line_ids.append(adjust_credit)

            elif currency.compare_amounts(debit_sum, credit_sum) == -1:
                acc_id = slip.journal_id.default_account_id.id
                if not acc_id:
                    raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (
                        slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': currency.round(credit_sum - debit_sum),
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            slip.write({'move_id': move.id, 'date': date})
            move.action_post()
        return True

    @api.model
    def _get_payslip_lines_by_holiday(self, contract_ids, payslip_id):

        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)

            if category.code in localdict['categories'].dict:
                localdict['categories'].dict[category.code] += amount
            else:
                localdict['categories'].dict[category.code] = amount

            return localdict

        class BrowsableObject(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                              SELECT sum(amount) as sum
                              FROM hr_payslip as hp, hr_payslip_input as pi
                              WHERE hp.employee_id = %s AND hp.state = 'done'
                              AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                              SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                              FROM hr_payslip as hp, hr_payslip_worked_days as pi
                              WHERE hp.employee_id = %s AND hp.state = 'done'
                              AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                                      FROM hr_payslip as hp, hr_payslip_line as pl
                                      WHERE hp.employee_id = %s AND hp.state = 'done'
                                      AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        # we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules_dict = {}
        worked_days_dict = {}
        inputs_dict = {}
        blacklist = []
        payslip = self.env['hr.payslip'].browse(payslip_id)
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line
        for input_line in payslip.input_line_ids:
            inputs_dict[input_line.code] = input_line

        categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
        inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
        worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
        payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)

        baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days,
                         'inputs': inputs}
        # get the ids of the structures on the contracts and their parent id as well
        contracts = self.env['hr.contract'].browse(contract_ids)
        if len(contracts) == 1 and payslip.struct_id:
            structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
        else:
            structure_ids = contracts.get_all_structures()
        # get the rules of the structure and thier children
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        # run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

        sorted_rules = sorted_rules.filtered(lambda l: l.in_holiday)

        for contract in contracts:
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee, contract=contract)
            for rule in sorted_rules:
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                # check if the rule can be applied
                if rule._satisfy_condition(localdict) and rule.id not in blacklist:
                    # compute the amount of the rule
                    amount, qty, rate = rule._compute_rule(localdict)
                    # check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    if rule.per_day and worked_days.PAID100:
                        amount = (amount / WORK_DAY_PER_MONTH) * worked_days.PAID100.number_of_days
                    # set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    # create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    # blacklist this rule and its children
                    blacklist += [id for id, seq in rule._recursive_search_of_rules()]

        return list(result_dict.values())


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('close', 'Close'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    batch_net_total = fields.Float('Batch Total NET', readonly=True)
    description = fields.Text('Description', readonly=True, states={'draft': [('readonly', False)]})
    credit_note = fields.Boolean(
        string='Credit Note',
        states={'draft': [('readonly', False)]},
        help="Indicates this payslip has a refund of another")

    
    def _compute_attachment_number(self):
        for payslip in self:
            payslip.attachment_number = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'hr.payslip.run'), ('res_id', '=', payslip.id)])

    
    def open_attach_wizard(self):
        view_id = self.env.ref('bsg_hr_payroll.view_attachment_payslip_batch_form').id
        default_name = "مرفقات دفعة" + " " + str(self.name)

        return {
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'view_type': 'form',
            'context': "{'default_name': '%s','default_res_model': '%s','default_res_id': %d}" % (
                default_name, self._name, self.id),
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }

    
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_hr_payroll.action_attachment')
        return res

    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')

    
    def confirm_payslip_run(self):
        for rec in self:
            if rec.state != 'draft':
                ValidationError(_("You can only confirm batches in 'Draft' state!"))
            for slip in rec.slip_ids:
                if slip.state == 'draft':
                    slip.with_context({'no_compute': True}).action_payslip_done()
        return self.write({'state': 'done'})

    
    def compute_payslip_run(self):
        for rec in self:
            if not rec.slip_ids:
                ValidationError("Please generate payslips first!")
            if rec.state != 'draft':
                ValidationError(_("You may only compute batches in 'Draft' state!"))
            for slip in rec.slip_ids:
                if slip.state == 'draft':
                    slip.with_context({'no_batch_total_update': True}).compute_sheet()
            net_total = sum(rec.slip_ids.mapped('total_net'))
            rec.batch_net_total = net_total
        return True

    
    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise ValidationError(_("You can not delete confimed batches!"))
            if rec.slip_ids:
                if 'done' in rec.slip_ids.mapped('state'):
                    raise ValidationError(_("You can't delete a batch that has confirmed payslips!"))
                else:
                    rec.slip_ids.unlink()
        super(HrPayslipRun, self).unlink()
        return True

    # @api.constrains('slip_ids')
    # def _trigger_slip_ids(self):
    #     for rec in self:
    #         rec.sudo().compute_payslip_run()


class AccountMove(models.Model):
    _inherit = "account.move"

    payslip_run_id = fields.Many2one('hr.payslip', string='Payslip Batch', copy=False, help="Payslip Expense",
                                     readonly=True)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payslip_id = fields.Many2one('hr.payslip', string='Payslip', copy=False, help="Payslip Expense", readonly=True)

    def reconcile(self):
        res = super().reconcile()
        account_move_ids = [l.move_id.id for l in self]
        if account_move_ids:
            payslip = self.env['hr.payslip'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                 company_id=self.env.user.company_id.id).search([
                ('move_id', 'in', account_move_ids), ('state', '=', 'done')
            ])
            payslip.set_to_paid()
        return res
