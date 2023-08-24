from datetime import date, datetime, time
from pytz import timezone
import babel

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from odoo.tools.mail import html2plaintext, is_html_empty



class HrPayslipLine(models.Model):

    _inherit = "hr.payslip.line"

    hr_leave_request_id = fields.Many2one("hr.leave")
    register_id = fields.Many2one('hr.contribution.register', string='Contribution Register')
    condition_select = fields.Selection([
        ('none', 'Always True'),
        ('range', 'Range'),
        ('python', 'Python Expression')
    ], string="Condition Based on", default='none')


WORK_DAY_PER_MONTH = 30

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_contract(self, employee, date_from, date_to):
        """
        @param employee: recordset of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
        """
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open'), '|',
                        '|'] + clause_1 + clause_2 + clause_3
        return self.env['hr.contract'].search(clause_final).ids

    # @api.multi
    def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):
        # defaults
        res = {
            'value': {
                'line_ids': [],
                # delete old input lines
                'input_line_ids': [(2, x,) for x in self.input_line_ids.ids],
                # delete old worked days lines
                'worked_days_line_ids': [(2, x,) for x in self.worked_days_line_ids.ids],
                # 'details_by_salary_head':[], TODO put me back
                'name': '',
                'contract_id': False,
                'struct_id': False,
            }
        }
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        employee = self.env['hr.employee'].browse(employee_id)
        locale = self.env.context.get('lang') or 'en_US'
        res['value'].update({
            'name': _('Salary Slip of %s for %s') % (
            employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))),
            'company_id': employee.company_id.id,
        })

        if not self.env.context.get('contract'):
            # fill with the first contract of the employee
            contract_ids = self.get_contract(employee, date_from, date_to)
        else:
            if contract_id:
                # set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                # if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(employee, date_from, date_to)

        if not contract_ids:
            return res
        contract = self.env['hr.contract'].browse(contract_ids[0])
        res['value'].update({
            'contract_id': contract.id
        })
        struct = contract.struct_id
        if not struct:
            return res
        res['value'].update({
            'struct_id': struct.id,
        })
        # computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        res['value'].update({
            'worked_days_line_ids': worked_days_line_ids,
            'input_line_ids': input_line_ids,
        })
        return res

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        res = []

        structure_ids = contracts.get_all_structures()
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
        inputs = self.env['hr.salary.rule'].browse(sorted_rule_ids).mapped('input_ids')

        for contract in contracts:
            for input in inputs:
                input_data = {
                    'name': input.name,
                    'code': input.code,
                    'contract_id': contract.id,
                }
                res += [input_data]
        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee_hr_leave(self):

        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []

        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id

        #computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines
        return

    bonus_ids = fields.Many2many('hr.salary.rule', string='Rules')
    eos_rule_ids = fields.Many2many('hr.salary.rule','payslip_id','salary_rule_id', string='EOS Rules')
    type = fields.Selection([
        ('salary', 'Salary'), ('holiday', 'Holiday'), ('eos', 'EOS')
    ], string='Type', index=True, copy=False,default='salary')
    leave_request_id = fields.Many2one('hr.leave', string="Leave Request", track_visibility=True)

    # 
    # def copy(self):
    #     return 1/0

    
    def compute_sheet(self):
        for payslip in self:
            if payslip.type == 'holiday' and payslip.bonus_ids:
                number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
                # delete old payslip lines
                payslip.line_ids.unlink()
                rules = [(rule.id, rule.sequence) for rule in payslip.bonus_ids]
                # set the list of contract for which the rules have to be applied
                # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
                contract_ids = payslip.contract_id.ids or \
                               self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
                lines = [(0, 0, line) for line in self._get_holiday_payslip_lines(contract_ids, payslip.id)]
                payslip.write({'line_ids': lines, 'number': number})
                return True
            else:
                self = self.with_context(tracking_disable=True)
                return super(HrPayslip, self).compute_sheet()

    def _get_holiday_payslip_lines(self, contract_ids, payslip_id):
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

        sorted_rules = sorted_rules.filtered(lambda l:l.in_holiday)

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


    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), time.max)

            # compute leave days
            leaves = {}
            calendar = contract.resource_calendar_id
            tz = timezone(calendar.tz)
            day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to, calendar=contract.resource_calendar_id)
            for day, hours, leave in day_leave_intervals:
                holiday = leave[:1].holiday_id
                current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                    'name': holiday.holiday_status_id.name or _('Global Leaves'),
                    'sequence': 5,
                    'code': holiday.holiday_status_id.unpaid or 'GLOBAL',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract.id,
                    'holiday_id':holiday,
                })
                current_leave_struct['number_of_hours'] += hours
                work_hours = calendar.get_work_hours_count(
                    tz.localize(datetime.combine(day, time.min)),
                    tz.localize(datetime.combine(day, time.max)),
                    compute_leaves=False,
                )
                if work_hours:
                    current_leave_struct['number_of_days'] += hours / work_hours

            # compute worked days
            work_data = contract.employee_id.get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
            print('............work_data...........',work_data)
            attendance_work_entry =  self.env.ref('hr_work_entry.work_entry_type_attendance')
            paid_work_entry =  self.env.ref('bsg_hr.work_entry_type_paid')
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_data['days'] if work_data else 0.0,
                'number_of_hours': work_data['hours'] if work_data else 0.0,
                'contract_id': contract.id,
                'work_entry_type_id':attendance_work_entry.id
            }
            paid_days_dict = contract.employee_id.get_paid_days_data(day_from, day_to, leaves,self)
            print('............paid_days_dict...........', paid_days_dict)
            paid_days = {
                'name': _("Normal Paid Days at 100%"),
                'sequence': 3,
                'code': 'PAID100',
                'number_of_days': paid_days_dict['days'],
                'number_of_hours': paid_days_dict['hours'],
                'contract_id': contract.id,
                'work_entry_type_id':paid_work_entry.id
            }

            res.append(attendances)
            res.extend(leaves.values())
            res.append(paid_days)
        return res

    def _get_payslip_lines(self):
        line_vals = []
        for payslip in self:
            if not payslip.contract_id:
                raise UserError(_("There's no contract set on payslip %s for %s. Check that there is at least a contract set on the employee form.", payslip.name, payslip.employee_id.name))

            localdict = self.env.context.get('force_payslip_localdict', None)
            if localdict is None:
                localdict = payslip._get_localdict()

            rules_dict = localdict['rules'].dict
            result_rules_dict = localdict['result_rules'].dict

            blacklisted_rule_ids = self.env.context.get('prevent_payslip_computation_line_ids', [])

            result = {}
            for rule in sorted(payslip.struct_id.rule_ids, key=lambda x: x.sequence):
                if rule.id in blacklisted_rule_ids:
                    continue
                localdict.update({
                    'result': None,
                    'result_qty': 1.0,
                    'result_rate': 100,
                    'result_name': False
                })
                if rule._satisfy_condition(localdict):
                    amount, qty, rate = rule._compute_rule(localdict)
                    #check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    #set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    result_rules_dict[rule.code] = {'total': tot_rule, 'amount': amount, 'quantity': qty}
                    rules_dict[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = rule.category_id._sum_salary_rule_category(localdict, tot_rule - previous_amount)
                    # Retrieve the line name in the employee's lang
                    employee_lang = payslip.employee_id.sudo().address_home_id.lang
                    # This actually has an impact, don't remove this line
                    context = {'lang': employee_lang}
                    if localdict['result_name']:
                        rule_name = localdict['result_name']
                    elif rule.code in ['BASIC', 'GROSS', 'NET', 'DEDUCTION', 'REIMBURSEMENT']:  # Generated by default_get (no xmlid)
                        if rule.code == 'BASIC':  # Note: Crappy way to code this, but _(foo) is forbidden. Make a method in master to be overridden, using the structure code
                            if rule.name == "Double Holiday Pay":
                                rule_name = _("Double Holiday Pay")
                            if rule.struct_id.name == "CP200: Employees 13th Month":
                                rule_name = _("Prorated end-of-year bonus")
                            else:
                                rule_name = _('Basic Salary')
                        elif rule.code == "GROSS":
                            rule_name = _('Gross')
                        elif rule.code == "DEDUCTION":
                            rule_name = _('Deduction')
                        elif rule.code == "REIMBURSEMENT":
                            rule_name = _('Reimbursement')
                        elif rule.code == 'NET':
                            rule_name = _('Net Salary')
                    else:
                        rule_name = rule.with_context(lang=employee_lang).name
                    # create/overwrite the rule in the temporary results
                    result[rule.code] = {
                        'sequence': rule.sequence,
                        'code': rule.code,
                        'name': rule_name,
                        'note': html2plaintext(rule.note) if not is_html_empty(rule.note) else '',
                        'salary_rule_id': rule.id,
                        'contract_id': localdict['contract'].id,
                        'employee_id': localdict['employee'].id,
                        'amount': amount,
                        'quantity': qty,
                        'rate': rate,
                        'slip_id': payslip.id,
                    }
            line_vals += list(result.values())
        return line_vals


    # @api.model
    # def _get_payslip_lines(self, contract_ids, payslip_id):
    #     # return 1/0
    #     def _sum_salary_rule_category(localdict, category, amount):
    #         if category.parent_id:
    #             localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
    #         localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
    #         return localdict
    #
    #     class BrowsableObject(object):
    #         def __init__(self, employee_id, dict, env):
    #             self.employee_id = employee_id
    #             self.dict = dict
    #             self.env = env
    #
    #         def __getattr__(self, attr):
    #             return attr in self.dict and self.dict.__getitem__(attr) or 0.0
    #
    #     class InputLine(BrowsableObject):
    #         """a class that will be used into the python code, mainly for usability purposes"""
    #         def sum(self, code, from_date, to_date=None):
    #             if to_date is None:
    #                 to_date = fields.Date.today()
    #             self.env.cr.execute("""
    #                 SELECT sum(amount) as sum
    #                 FROM hr_payslip as hp, hr_payslip_input as pi
    #                 WHERE hp.employee_id = %s AND hp.state = 'done'
    #                 AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
    #                 (self.employee_id, from_date, to_date, code))
    #             return self.env.cr.fetchone()[0] or 0.0
    #
    #     class WorkedDays(BrowsableObject):
    #         """a class that will be used into the python code, mainly for usability purposes"""
    #         def _sum(self, code, from_date, to_date=None):
    #             if to_date is None:
    #                 to_date = fields.Date.today()
    #             self.env.cr.execute("""
    #                 SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
    #                 FROM hr_payslip as hp, hr_payslip_worked_days as pi
    #                 WHERE hp.employee_id = %s AND hp.state = 'done'
    #                 AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
    #                 (self.employee_id, from_date, to_date, code))
    #             return self.env.cr.fetchone()
    #
    #         def sum(self, code, from_date, to_date=None):
    #             res = self._sum(code, from_date, to_date)
    #             return res and res[0] or 0.0
    #
    #         def sum_hours(self, code, from_date, to_date=None):
    #             res = self._sum(code, from_date, to_date)
    #             return res and res[1] or 0.0
    #
    #     class Payslips(BrowsableObject):
    #         """a class that will be used into the python code, mainly for usability purposes"""
    #
    #         def sum(self, code, from_date, to_date=None):
    #             if to_date is None:
    #                 to_date = fields.Date.today()
    #             self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
    #                         FROM hr_payslip as hp, hr_payslip_line as pl
    #                         WHERE hp.employee_id = %s AND hp.state = 'done'
    #                         AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
    #                         (self.employee_id, from_date, to_date, code))
    #             res = self.env.cr.fetchone()
    #             return res and res[0] or 0.0
    #
    #     #we keep a dict with the result because a value can be overwritten by another rule with the same code
    #     result_dict = {}
    #     rules_dict = {}
    #     worked_days_dict = {}
    #     inputs_dict = {}
    #     blacklist = []
    #     payslip = self.env['hr.payslip'].browse(payslip_id)
    #     for worked_days_line in payslip.worked_days_line_ids:
    #         worked_days_dict[worked_days_line.code] = worked_days_line
    #     for input_line in payslip.input_line_ids:
    #         inputs_dict[input_line.code] = input_line
    #
    #     categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
    #     inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
    #     worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
    #     payslips = Payslips(payslip.employee_id.id, payslip, self.env)
    #     rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)
    #
    #     baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days, 'inputs': inputs}
    #     #get the ids of the structures on the contracts and their parent id as well
    #     contracts = self.env['hr.contract'].browse(contract_ids)
    #     if len(contracts) == 1 and payslip.struct_id:
    #         structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
    #     else:
    #         structure_ids = contracts.get_all_structures()
    #     #get the rules of the structure and thier children
    #     if payslip.type == 'holiday' and payslip.bonus_ids:
    #         rules = [(rule.id, rule.sequence) for rule in payslip.bonus_ids]
    #         rule_ids = self.env['hr.payroll.structure'].with_context({'rules': rules}).browse(structure_ids).get_all_rules()
    #     else:
    #         rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
    #     #run the rules by sequence
    #     sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
    #     sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)
    #
    #     for contract in contracts:
    #         employee = contract.employee_id
    #         localdict = dict(baselocaldict, employee=employee, contract=contract)
    #         for rule in sorted_rules:
    #             key = rule.code + '-' + str(contract.id)
    #             localdict['result'] = None
    #             localdict['result_qty'] = 1.0
    #             localdict['result_rate'] = 100
    #             #check if the rule can be applied
    #             if rule._satisfy_condition(localdict) and rule.id not in blacklist:
    #                 #compute the amount of the rule
    #                 amount, qty, rate = rule._compute_rule(localdict)
    #                 #check if there is already a rule computed with that code
    #                 previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
    #                 if rule.per_day and worked_days.PAID100:
    #                    amount = (amount / WORK_DAY_PER_MONTH) * worked_days.PAID100.number_of_days
    #                 #set/overwrite the amount computed for this rule in the localdict
    #                 tot_rule = amount * qty * rate / 100.0
    #                 localdict[rule.code] = tot_rule
    #                 rules_dict[rule.code] = rule
    #                 #sum the amount for its salary category
    #                 localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
    #                 #create/overwrite the rule in the temporary results
    #                 result_dict[key] = {
    #                     'salary_rule_id': rule.id,
    #                     'contract_id': contract.id,
    #                     'name': rule.name,
    #                     'code': rule.code,
    #                     'category_id': rule.category_id.id,
    #                     'sequence': rule.sequence,
    #                     'appears_on_payslip': rule.appears_on_payslip,
    #                     'condition_select': rule.condition_select,
    #                     'condition_python': rule.condition_python,
    #                     'condition_range': rule.condition_range,
    #                     'condition_range_min': rule.condition_range_min,
    #                     'condition_range_max': rule.condition_range_max,
    #                     'amount_select': rule.amount_select,
    #                     'amount_fix': rule.amount_fix,
    #                     'amount_python_compute': rule.amount_python_compute,
    #                     'amount_percentage': rule.amount_percentage,
    #                     'amount_percentage_base': rule.amount_percentage_base,
    #                     'register_id': rule.register_id.id,
    #                     'amount': amount,
    #                     'employee_id': contract.employee_id.id,
    #                     'quantity': qty,
    #                     'rate': rate,
    #                 }
    #             else:
    #                 #blacklist this rule and its children
    #                 blacklist += [id for id, seq in rule._recursive_search_of_rules()]
    #
    #     return list(result_dict.values())
class PayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'


    parent_id = fields.Many2one('hr.payroll.structure', string='Parent')


    # @api.multi
    def _get_parent_structure(self):
        parent = self.mapped('parent_id')
        if parent:
            parent = parent._get_parent_structure()
        return parent + self




    
    def get_all_rules(self):
        """
        @return: returns a list of tuple (id, sequence) of rules that are maybe to apply
        """
        all_rules = []
        if self.env.context.get('rules'):
            all_rules = self.env.context.get('rules')
        else:
            for struct in self:
                all_rules += struct.rule_ids._recursive_search_of_rules()

        return all_rules



class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    per_day = fields.Boolean('Per Working Day')
    in_holiday = fields.Boolean('In Holiday',default=False)
    move_per_employee = fields.Boolean('Move Per Employee',default=False)
    leave_debit_account_id = fields.Many2one('account.account', string="Leave Debit Account")
    leave_credit_account_id = fields.Many2one('account.account', string="Leave Credit Account")
    is_get_from_leave = fields.Boolean('Is get from leave', default=False)
    input_ids = fields.One2many('hr.rule.input', 'input_id', string='Inputs', copy=True)


class HrRuleInput(models.Model):
    _name = 'hr.rule.input'
    _description = 'Salary Rule Input'

    name = fields.Char(string='Description', required=True)
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
    input_id = fields.Many2one('hr.salary.rule', string='Salary Rule Input', required=True)
