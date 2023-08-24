# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    @api.model
    def create(self, values):
        """Override default Odoo write function and extend."""
        res = super(HrPayslipInput, self).create(values)
        data_dict = {}
        reference = res.name if res.name else ''
        if values.get('name'):
            data_dict['name'] = {'name': 'Name', 'new': values.get('name')}
        if values.get('code'):
            data_dict['code'] = {'name': 'Code', 'new': values.get('code')}
        if values.get('amount'):
            data_dict['amount'] = {'name': 'Amount', 'new': values.get('amount')}
        if values.get('description'):
            data_dict['description'] = {'name': 'Description', 'new': values.get('description')}
        log_body = "<p>Reference/Description : " + reference + "</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
                data_dict[val]['new']) + '</li>'
        res.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.payslip', 'res_id': res.payslip_id.id, 'subtype_id': '2'})
        return res

    #@api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'name': self.name if self.name else '', 'code': self.code if self.code else '',
                    'amount': self.amount if self.amount else '',
                    'description': self.description if self.description else ''}
        data_dict = {}
        reference = self.name if self.name else ''
        if values.get('name'):
            data_dict['name'] = {'name': 'Name', 'old': old_dict['name'], 'new': values.get('name')}
        if values.get('code'):
            data_dict['code'] = {'name': 'Code', 'old': old_dict['code'], 'new': values.get('code')}
        if values.get('amount'):
            data_dict['amount'] = {'name': 'Amount', 'old': old_dict['amount'], 'new': values.get('amount')}
        if values.get('description'):
            data_dict['description'] = {'name': 'Description', 'old': old_dict['description'],
                                        'new': values.get('description')}
        log_body = "<p>Reference/Description : " + reference + "</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.payslip', 'res_id': self.payslip_id.id, 'subtype_id': '2'})
        return super(HrPayslipInput, self).write(values)


class HrPayslipLine(models.Model):
    _name = 'hr.payslip.line'
    _inherit = ['hr.payslip.line', 'mail.thread', 'mail.activity.mixin']

    @api.model
    def create(self, values):
        """Override default Odoo write function and extend."""
        res = super(HrPayslipLine, self).create(values)
        data_dict = {}
        reference = res.name if res.name else ''
        if values.get('salary_rule_id'):
            data_dict['salary_rule_id'] = {'name': 'Salary Rule', 'new': res.salary_rule_id.name}
        if values.get('rate'):
            data_dict['rate'] = {'name': 'Rate', 'new': values.get('rate')}
        if values.get('amount'):
            data_dict['amount'] = {'name': 'Amount', 'new': values.get('amount')}
        if values.get('total'):
            data_dict['total'] = {'name': 'Total', 'new': values.get('total')}
        if values.get('quantity'):
            data_dict['quantity'] = {'name': 'Quantity',  'new': values.get('quantity')}
        if data_dict:
            log_body = "<p>Reference/Description : " + reference + "</p>"
            for val in data_dict.keys():
                log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
                    data_dict[val]['new']) + '</li>'
            res.env['mail.message'].create(
                {'body': log_body, 'model': 'hr.payslip', 'res_id': res.slip_id.id, 'subtype_id': '2'})
        return res

    #@api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'salary_rule_id': self.salary_rule_id.name if self.salary_rule_id else '',
                    'rate': self.rate if self.rate else '',
                    'amount': self.amount if self.amount else '',
                    'total': self.total if self.total else '',
                    'quantity': self.quantity if self.quantity else ''}
        data_dict = {}
        reference = self.name if self.name else ''
        if values.get('salary_rule_id'):
            data_dict['salary_rule_id'] = {'name': 'Salary Rule', 'old': old_dict['salary_rule_id'], 'new': values.get('salary_rule_id')}
        if values.get('rate'):
            data_dict['rate'] = {'name': 'Rate', 'old': old_dict['rate'], 'new': values.get('rate')}
        if values.get('amount'):
            data_dict['amount'] = {'name': 'Amount', 'old': old_dict['amount'], 'new': values.get('amount')}
        if values.get('total'):
            data_dict['total'] = {'name': 'Total', 'old': old_dict['total'], 'new': values.get('total')}
        if values.get('quantity'):
            data_dict['quantity'] = {'name': 'Quantity', 'old': old_dict['quantity'],
                                        'new': values.get('quantity')}
        if data_dict:
            log_body = "<p>Reference/Description : " + reference + "</p>"
            for val in data_dict.keys():
                log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                    data_dict[val]['new']) + '</li>'
            self.env['mail.message'].create(
                {'body': log_body, 'model': 'hr.payslip', 'res_id': self.slip_id.id, 'subtype_id': '2'})
        return super(HrPayslipLine, self).write(values)

    # slip_id = fields.Many2one(track_visibility='onchange')
    # salary_rule_id = fields.Many2one(track_visibility='onchange')
    # employee_id = fields.Many2one(track_visibility='onchange')
    # contract_id = fields.Many2one(track_visibility='onchange')
    # rate = fields.Float(track_visibility='onchange')
    # amount = fields.Float(track_visibility='onchange')
    # quantity = fields.Float(track_visibility='onchange')
    # total = fields.Float(track_visibility='onchange')


class HrPayslipWorkedDays(models.Model):
    _name = 'hr.payslip.worked_days'
    _inherit = ['hr.payslip.worked_days', 'mail.thread']

    @api.model
    def create(self, values):
        """Override default Odoo write function and extend."""
        data_dict = {}
        res = super(HrPayslipWorkedDays, self).create(values)
        reference = res.name if res.name else ''
        if values.get('name'):
            data_dict['name'] = {'name': 'Name', 'new': values.get('name')}
        if values.get('sequence'):
            data_dict['sequence'] = {'name': 'Sequence', 'new': values.get('sequence')}
        if values.get('contract_id'):
            data_dict['contract_id'] = {'name': 'Contract', 'new': res.contract_id.name}
        if values.get('code'):
            data_dict['code'] = {'name': 'Code', 'new': values.get('code')}
        if values.get('number_of_days'):
            data_dict['number_of_days'] = {'name': 'Number of Days', 'new': values.get('number_of_days')}
        if values.get('number_of_hours'):
            data_dict['number_of_hours'] = {'name': 'Number of Hours', 'new': values.get('number_of_hours')}
        if data_dict:
            log_body = "<p>Reference/Description : " + reference + "</p>"
            for val in data_dict.keys():
                log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
                    data_dict[val]['new']) + '</li>'
            res.env['mail.message'].create(
                {'body': log_body, 'model': 'hr.payslip', 'res_id': res.payslip_id.id, 'subtype_id': '2'})
        return res

    #@api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'name': self.name if self.name else '',
                    'sequence': self.sequence if self.sequence else '',
                    'code': self.code if self.code else '',
                    'contract_id': self.contract_id.name if self.contract_id else '',
                    'number_of_days': self.number_of_days if self.number_of_days else '',
                    'number_of_hours': self.number_of_hours if self.number_of_hours else ''}
        data_dict = {}
        reference = self.name if self.name else ''
        res = super(HrPayslipWorkedDays, self).write(values)
        if values.get('name'):
            data_dict['name'] = {'name': 'Name', 'old': old_dict['name'], 'new': values.get('name')}
        if values.get('sequence'):
            data_dict['sequence'] = {'name': 'Sequence', 'old': old_dict['sequence'], 'new': values.get('sequence')}
        if values.get('contract_id'):
            data_dict['contract_id'] = {'name': 'Contract', 'old': old_dict['contract_id'], 'new': self.contract_id}
        if values.get('code'):
            data_dict['code'] = {'name': 'Code', 'old': old_dict['code'], 'new': values.get('code')}
        if values.get('number_of_days'):
            data_dict['number_of_days'] = {'name': 'Number of Days', 'old': old_dict['number_of_days'], 'new': values.get('number_of_days')}
        if values.get('number_of_hours'):
            data_dict['number_of_hours'] = {'name': 'Number of Hours', 'old': old_dict['number_of_hours'],
                                        'new': values.get('number_of_hours')}
        if data_dict:
            log_body = "<p>Reference/Description : " + reference + "</p>"
            for val in data_dict.keys():
                log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                    data_dict[val]['new']) + '</li>'
            self.env['mail.message'].create(
                {'body': log_body, 'model': 'hr.payslip', 'res_id': self.payslip_id.id, 'subtype_id': '2'})
        return res


##############################################################


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread']

    @api.model
    def create(self, values):
        # overridden to automatically invite user to sign up
        payslip = super(HrPayslip, self).create(values)
        old_values = {
            'name': '',
            'number': '',
            'date_from': '',
            'date_to': '',
            'struct_id': '',
            'employee_id': '',
            'company_id': '',
            'state': '',
            'note': '',
            'contract_id': '',
            'credit_note': '',
            'payslip_run_id': '',
            'payslip_count': '',
            'total_net': '',
            'journal_id': '',
            'job_id': '',
            'branch_id': '',
            'department_id': '',
            'salary_payment_method': '',
            'employee_state': '',
            'category_ids': '',
            'category_id': '',
            'payment_move_id': '',
            'description': '',
        }
        tracked_fields = self.env['hr.payslip'].fields_get(
            ['name', 'number', 'date_from', 'date_to', 'struct_id', 'employee_id', 'company_id', 'state', 'note',
             'contract_id', 'credit_note', 'payslip_run_id', 'payslip_count', 'total_net', 'journal_id', 'job_id'
                                                                                                         'branch_id',
             'department_id', 'salary_payment_method', 'employee_state', 'category_ids', 'category_id'
                                                                                         'payment_move_id',
             'description'])

        changes, tracking_value_ids = payslip._message_track(tracked_fields, old_values)
        if changes:
            payslip.message_post(tracking_value_ids=tracking_value_ids)
        return payslip

    #@api.multi
    def write(self, vals):
        old_values = {
            'name': self.name,
            'number': self.number,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'struct_id': self.struct_id,
            'employee_id': self.employee_id,
            'company_id': self.company_id,
            'state': self.state,
            'note': self.note,
            'contract_id': self.contract_id,
            'credit_note': self.credit_note,
            'payslip_run_id': self.payslip_run_id,
            'payslip_count': self.payslip_count,
            'total_net': self.total_net,
            'journal_id': self.journal_id,
            'job_id': self.job_id,
            'branch_id': self.branch_id,
            'department_id': self.department_id,
            'salary_payment_method': self.salary_payment_method,
            'employee_state': self.employee_state,
            'category_ids': self.category_ids,
            'category_id': self.category_id,
            'payment_move_id': self.payment_move_id,
            'description': self.description,
        }
        res = super(HrPayslip, self).write(vals)
        tracked_fields = self.env['hr.payslip'].fields_get(
            ['name', 'number', 'date_from', 'date_to', 'struct_id', 'employee_id', 'company_id', 'state', 'note',
             'contract_id', 'credit_note', 'payslip_run_id', 'payslip_count', 'total_net', 'journal_id', 'job_id'
             'branch_id', 'department_id', 'salary_payment_method', 'employee_state', 'category_ids', 'category_id'
             'payment_move_id', 'description'])

        changes, tracking_value_ids = self._message_track(tracked_fields, old_values)
        if changes:
            self.message_post(tracking_value_ids=tracking_value_ids)
            return res

    name = fields.Char(tracking=True)
    # number = fields.Char(tracking=True)
    # employee_id = fields.Many2one(tracking=True)
    # date_from = fields.Date(string='Date From', readonly=True, required=True,
    #     default=lambda self: fields.Date.to_string(date.today().replace(day=1)), states={'draft': [('readonly', False)]})
    # date_to = fields.Date(string='Date To', readonly=True, required=True,
    #     default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
    #     states={'draft': [('readonly', False)]})

