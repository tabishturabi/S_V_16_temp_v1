# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar
from dateutil.relativedelta import relativedelta
from math import copysign

from datetime import date, datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round

# Migration Note
# account.asset.category not in base
# class AccountAssetCategory(models.Model):
#     _name = "account.asset.category"
#     _inherit = ['account.asset.category', 'mail.thread']
#
#     type = fields.Selection(selection_add=[('expense', 'Deferred Expense')])
#     method_period_label = fields.Selection([('1', 'Months'), ('12', 'Years')], string='Number of Months in a Period',
#                                            default='12', help="The amount of time between two depreciations")
#
#     @api.onchange('method_period_label')
#     def onchange_method_period_label(self):
#         if self.method_period_label:
#             self.method_period = int(self.method_period_label)
#
#     @api.onchange('account_asset_id')
#     def onchange_account_asset(self):
#         if self.type in ["purchase", "expense"]:
#             self.account_depreciation_id = self.account_asset_id
#         elif self.type == "sale":
#             self.account_depreciation_expense_id = self.account_asset_id
#
#     @api.onchange('type')
#     def onchange_type(self):
#         if self.type == 'sale':
#             self.prorata = True
#             self.method_period = 1
#         else:
#             self.method_period = 12
#
#     @api.onchange('account_depreciation_id')
#     def _onchange_account_depreciation_id(self):
#         """
#         The field account_asset_id is required but invisible in the Deferred Revenue type.
#         Therefore, set it when account_depreciation_id changes.
#         """
#         if self.type == 'expense':
#             self.account_asset_id = self.account_depreciation_id
#
#     @api.model
#     def create(self, values):
#         res = super(AccountAssetCategory, self).create(values)
#         reference = res.name if res.name else ''
#         data_dict = {}
#         if 'name' in values:
#             data_dict['name'] = {'name': 'Name', 'new': res.name}
#
#         if 'open_asset' in values:
#             data_dict['open_asset'] = {'name': 'Open Assets', 'new': res.open_asset}
#
#         if 'group_entries' in values:
#             data_dict['group_entries'] = {'name': 'Group Entries', 'new': res.group_entries}
#
#         if 'method_number' in values:
#             data_dict['method_number'] = {'name': 'Method Number', 'new': res.method_number}
#
#         if 'method_period_label' in values:
#             data_dict['method_period_label'] = {'name': 'Method Period', 'new': res.method_period_label}
#
#         if 'prorata' in values:
#             data_dict['prorata'] = {'name': 'Prorata', 'new': res.prorata}
#
#         if 'date_first_depreciation' in values:
#             kay_val_dict = dict(self._fields['date_first_depreciation'].selection)  # here 'type' is field name
#             data_dict['date_first_depreciation'] = {'name': 'First Depreciation Date', 'new': kay_val_dict[res.date_first_depreciation]}
#
#         if 'journal_id' in values:
#             data_dict['journal_id'] = {'name': 'Journal ', 'new': res.journal_id.name}
#
#         if 'company_id' in values:
#             data_dict['company_id'] = {'name': 'Company', 'new': res.company_id.name}
#
#         if 'account_depreciation_id' in values:
#             data_dict['account_depreciation_id'] = {'name': 'Depreciation Account', 'new': res.account_depreciation_id.name}
#
#         if 'account_depreciation_expense_id' in values:
#             data_dict['account_depreciation_expense_id'] = {'name': 'Depreciation Expense Account ', 'new': res.account_depreciation_expense_id.name}
#
#         if 'account_analytic_id' in values:
#             data_dict['account_analytic_id'] = {'name': 'Analytic Account', 'new': res.account_analytic_id.name}
#
#         if 'analytic_tag_ids' in values:
#             data_dict['analytic_tag_ids'] = {'name': 'Analytic Tags', 'new': res.analytic_tag_ids.mapped("name")}
#
#         if data_dict:
#             log_body = "<p>Reference/Description : " + reference + "</p>"
#             for val in data_dict.keys():
#                 log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
#                     data_dict[val]['new']) + '</li>'
#             self.env['mail.message'].create(
#                 {'body': log_body, 'model': 'account.asset.category', 'res_id': res.id, 'subtype_id': '2'})
#         return res
#
#     def write(self, values):
#         """Override to log changes"""
#         old_dict = {
#             'name': self.name if self.name else '',
#             'journal_id': self.journal_id.name if self.journal_id else '',
#             'account_depreciation_id': self.account_depreciation_id.name if self.account_depreciation_id else '',
#             'account_depreciation_expense_id': self.account_depreciation_expense_id.name if self.account_depreciation_expense_id else '',
#             'account_analytic_id': self.account_analytic_id.name if self.account_analytic_id else '',
#             'company_id': self.company_id.name if self.company_id else '',
#             'open_asset': self.open_asset if self.open_asset else '',
#             'group_entries': self.group_entries if self.group_entries else '',
#             'method_number': self.method_number if self.method_number else '',
#             'date_first_depreciation': self.date_first_depreciation if self.date_first_depreciation else '',
#             'method_period_label': self.method_period_label if self.method_period_label else '',
#             'prorata': self.prorata if self.prorata else '',
#             "analytic_tag_ids": self.analytic_tag_ids.mapped("name") if self.analytic_tag_ids else '',
#         }
#         data_dict = {}
#         res = super(AccountAssetCategory, self).write(values)
#         reference = self.name if self.name else ''
#         if 'name' in values:
#             data_dict['name'] = {'name': 'Name', 'old': old_dict['name'], 'new': self.name}
#
#         if 'journal_id' in values:
#             data_dict['journal_id'] = {'name': 'Journal ', 'old': old_dict['journal_id'], 'new': self.journal_id.name}
#
#         if 'account_depreciation_id' in values:
#             data_dict['account_depreciation_id'] = {'name': 'Depreciation Account ', 'old': old_dict['account_depreciation_id'],
#                                                     'new': self.account_depreciation_id.name}
#
#         if 'account_depreciation_expense_id' in values:
#             data_dict['account_depreciation_expense_id'] = {'name': 'Depreciation Expense Account ', 'old': old_dict['account_depreciation_expense_id'],
#                                                             'new': self.account_depreciation_expense_id.name}
#
#         if 'account_analytic_id' in values:
#             data_dict['account_analytic_id'] = {'name': 'Analytic Account ', 'old': old_dict['account_analytic_id'],
#                                                     'new': self.account_analytic_id.name}
#         if 'company_id' in values:
#             data_dict['company_id'] = {'name': 'Analytic Account ', 'old': old_dict['company_id'],
#                                                     'new': self.company_id.name}
#         if 'open_asset' in values:
#             data_dict['open_asset'] = {'name': 'Open Asset', 'old': old_dict['open_asset'], 'new': self.open_asset}
#
#         if 'group_entries' in values:
#             data_dict['group_entries'] = {'name': 'Group Entries', 'old': old_dict['group_entries'], 'new': self.group_entries}
#
#         if 'method_number' in values:
#                 data_dict['method_number'] = {'name': 'Method Number', 'old': old_dict['method_number'], 'new': self.method_number}
#
#         if 'method_period_label' in values:
#             data_dict['method_period_label'] = {'name': 'Method Period', 'old': old_dict['method_period_label'], 'new': self.method_period_label}
#
#         if 'prorata' in values:
#             data_dict['prorata'] = {'name': 'Prorata', 'old': old_dict['prorata'], 'new': self.prorata}
#
#         if 'date_first_depreciation' in values:
#             kay_val_dict = dict(self._fields['date_first_depreciation'].selection)  # here 'type' is field name
#             data_dict['date_first_depreciation'] = {
#                 'name': 'First Depreciation Date', 'old':  kay_val_dict.get(old_dict['date_first_depreciation']),
#                 'new':  kay_val_dict.get(self.date_first_depreciation)}
#
#         if 'analytic_tag_ids' in values:
#             data_dict['analytic_tag_ids'] = {'name': 'Analytic Tags', 'old': old_dict['analytic_tag_ids'], 'new': self.analytic_tag_ids.mapped("name")}
#
#         if data_dict:
#             log_body = "<p>Reference/Description : " + reference + "</p>"
#             for val in data_dict.keys():
#                 log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
#                     data_dict[val]['new']) + '</li>'
#             self.env['mail.message'].create(
#                 {'body': log_body, 'model': 'account.asset.category', 'res_id': self.id, 'subtype_id': '2'})
#         return res

#####################################################################


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    EXPENSE_MODE = [
        ("employee", "Employees"),
        ("vehicles", "Vehicles"),
        ("other", "Others"),
    ]

    @api.model
    def _default_my_employee_id(self):
        user_id = self.env['res.users'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                            company_id=self.env.user.company_id.id).search(
            [('id', '=', self.env.uid)])
        return self.env['hr.employee'].search([('partner_id', '=', user_id.partner_id.id)], limit=1)

    @api.model
    def default_get(self, fields):
        res = super(AccountAsset, self).default_get(fields)
        if 'type' in fields:
            expense_type = res.get('type', False)
            if expense_type == "expense":
                res.update({'bsg_branches_id': self._default_branch()})
        return res

    @api.model
    def _default_branch(self):
        return self.env['bsg_branches.bsg_branches'].search([('branch_no', '=', '46')], limit=1).id

    employee_id = fields.Many2one('hr.employee', default=_default_my_employee_id,
                                  domain="[('company_id', '=', company_id)]")
    bsg_branches_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch Name',
                                      domain="[('company_id', '=', company_id)]")
    department_id = fields.Many2one('hr.department', string="Department",
                                    domain="[('company_id', '=', company_id)]")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Truck",
                                       domain="[('company_id', '=', company_id)]")
    expense_mode = fields.Selection(EXPENSE_MODE, string="Expense Mode", default="other")

    # # inherited to add tracking
    # category_id = fields.Many2one(track_visibility="always")
    # code = fields.Char(track_visibility="always")
    # name = fields.Char(track_visibility="always")
    # date = fields.Date(track_visibility="always")
    # currency_id = fields.Many2one(track_visibility="always")
    # company_id = fields.Many2one(track_visibility="always")
    #
    # value = fields.Float(track_visibility="always")
    # partner_id = fields.Many2one(track_visibility="always")
    # value_residual = fields.Float(track_visibility="always")
    # note = fields.Text(track_visibility="always")
    #
    # account_analytic_id = fields.Many2one(track_visibility="always")
    # analytic_tag_ids = fields.Many2many(track_visibility="always")
    #
    # method_time = fields.Selection(track_visibility="always")
    # prorata = fields.Boolean(track_visibility="always")
    # method_number = fields.Integer(track_visibility="always")
    # method_period = fields.Integer(track_visibility="always")
    # state = fields.Selection(track_visibility="always")
    # @api.model
    # def create(self, values):
    #     res = super(AccountAsset, self).create(values)
    #     reference = res.name if res.name else ''
    #     data_dict = {}
    #     if values.get('name'):
    #         data_dict['name'] = {'name': 'Name', 'new': res.name}
    #
    #     if values.get('code'):
    #         data_dict['code'] = {'name': 'Code', 'new': res.code}
    #
    #     if values.get('date'):
    #         data_dict['date'] = {'name': 'Date', 'new': res.date}
    #
    #     if values.get('value'):
    #         data_dict['value'] = {'name': 'Value', 'new': res.value}
    #
    #     if values.get('value_residual'):
    #         data_dict['value_residual'] = {'name': 'Value', 'new': res.value_residual}
    #
    #     if values.get('note'):
    #         data_dict['note'] = {'name': 'Note', 'new': res.note}
    #
    #     if values.get('expense_mode'):
    #         kay_val_dict = dict(self._fields['expense_mode'].selection)  # here 'type' is field name
    #         data_dict['expense_mode'] = {'name': 'Expense Mode', 'new': kay_val_dict[res.expense_mode]}
    #
    #     if values.get('method_time'):
    #         data_dict['method_time'] = {'name': 'Method Time', 'new': res.method_time}
    #
    #     if values.get('prorata'):
    #         data_dict['prorata'] = {'name': 'Prorata', 'new': res.prorata}
    #
    #     if values.get('method_number'):
    #         data_dict['method_number'] = {'name': 'Method Number',  'new': res.method_number}
    #
    #     if values.get('method_period'):
    #         data_dict['method_period'] = {'name': 'Method Period', 'new': res.method_period}
    #
    #     if values.get('state') and res:
    #         kay_val_dict = dict(self._fields['state'].selection)  # here 'type' is field name
    #         data_dict['state'] = {'name': 'Status', 'new': kay_val_dict[res.state]}
    #
    #     if values.get('employee_id'):
    #         data_dict['employee_id'] = {'name': 'Employee ',  'new': res.employee_id.name}
    #
    #     if values.get('partner_id'):
    #         data_dict['partner_id'] = {'name': 'Partner ', 'new': res.partner_id.name}
    #
    #     if values.get('currency_id'):
    #         data_dict['currency_id'] = {'name': 'Currency ', 'new': res.currency_id.name}
    #
    #     if values.get('company_id'):
    #         data_dict['company_id'] = {'name': 'Company ', 'new': res.company_id.name}
    #
    #     if values.get('bsg_branches_id'):
    #         data_dict['bsg_branches_id'] = {'name': 'Branch', 'new': res.bsg_branches_id.branch_ar_name}
    #
    #     if values.get('department_id'):
    #         data_dict['department_id'] = {'name': 'Department', 'new': res.department_id.name}
    #
    #     if values.get('fleet_vehicle_id'):
    #         data_dict['fleet_vehicle_id'] = {'name': 'Vehicle', 'new': res.fleet_vehicle_id.name}
    #
    #     if values.get('category_id'):
    #         data_dict['category_id'] = {'name': 'Category', 'new': res.category_id.name}
    #
    #     if values.get('account_analytic_id'):
    #         data_dict['account_analytic_id'] = {'name': 'Analytic Account', 'new': res.account_analytic_id.name}
    #
    #     if 'analytic_tag_ids' in values:
    #         data_dict['analytic_tag_ids'] = {'name': 'Analytic Tags', 'new': self.analytic_tag_ids.mapped("name")}
    #
    #     if data_dict:
    #         log_body = "<p>Reference/Description : " + reference + "</p>"
    #         for val in data_dict.keys():
    #             log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
    #                 data_dict[val]['new']) + '</li>'
    #         self.env['mail.message'].create(
    #             {'body': log_body, 'model': 'account.asset.asset', 'res_id': res.id, 'subtype_id': '2'})
    #     return res
    #
    # def write(self, values):
    #     # self = self.sudo()
    #     """Override to log changes"""
    #     for line in self:
    #         old_dict = {
    #             'name': line.name if line.name else '',
    #             'code': line.code if line.code else '',
    #             'date': line.date if line.date else '',
    #             'value': line.value if line.value else '',
    #             'value_residual': line.value_residual if line.value_residual else '',
    #             'note': line.note if line.note else '',
    #             'method_time': line.method_time if line.method_time else '',
    #             'prorata': line.prorata if line.prorata else '',
    #             'method_number': line.method_number if line.method_number else '',
    #             'method_period': line.method_period if line.method_period else '',
    #             'state': line.state if line.state else '',
    #             'expense_mode': line.expense_mode if line.expense_mode else '',
    #             'employee_id': line.employee_id.name if line.employee_id else '',
    #             'partner_id': line.partner_id.name if line.partner_id else '',
    #             'currency_id': line.currency_id.name if line.currency_id else '',
    #             'company_id': line.company_id.name if line.company_id else '',
    #             'bsg_branches_id': line.bsg_branches_id.branch_ar_name if line.bsg_branches_id else '',
    #             'department_id': line.department_id.name if line.department_id else '',
    #             'fleet_vehicle_id': line.fleet_vehicle_id.name if line.fleet_vehicle_id else '',
    #             'category_id': line.category_id.name if line.category_id else '',
    #             'account_analytic_id': line.account_analytic_id.name if line.account_analytic_id else '',
    #
    #         }
    #         data_dict = {}
    #         res = super(AccountAsset, self).write(values)
    #         reference = line.name if line.name else ''
    #         if values.get('name'):
    #             data_dict['name'] = {'name': 'Name', 'old': old_dict['name'], 'new': line.name}
    #
    #         if values.get('code'):
    #             data_dict['code'] = {'name': 'Code', 'old': old_dict['code'], 'new': line.code}
    #
    #         if values.get('date'):
    #             data_dict['date'] = {'name': 'Date', 'old': old_dict['date'], 'new': line.date}
    #
    #         if values.get('value'):
    #             data_dict['value'] = {'name': 'Value', 'old': old_dict['value'], 'new': line.value}
    #
    #         if values.get('value_residual'):
    #             data_dict['value_residual'] = {'name': 'Value', 'Value Residual': old_dict['value_residual'], 'new': line.value_residual}
    #
    #         if values.get('note'):
    #             data_dict['note'] = {'name': 'Note', 'old': old_dict['note'], 'new': line.note}
    #
    #         if values.get('expense_mode'):
    #             kay_val_dict = dict(line._fields['expense_mode'].selection)  # here 'type' is field name
    #             data_dict['expense_mode'] = {'name': 'Expense Mode', 'old': kay_val_dict[old_dict['expense_mode']], 'new': kay_val_dict[line.expense_mode]}
    #
    #         if values.get('method_time'):
    #             data_dict['method_time'] = {'name': 'Method Time', 'old': old_dict['method_time'], 'new': line.method_time}
    #
    #         if values.get('prorata'):
    #             data_dict['prorata'] = {'name': 'Prorata', 'old': old_dict['prorata'], 'new': line.prorata}
    #
    #         if values.get('method_number'):
    #             data_dict['method_number'] = {'name': 'Method Number', 'old': old_dict['method_number'], 'new': line.method_number}
    #
    #         if values.get('method_period'):
    #             data_dict['method_period'] = {'name': 'Method Period', 'old': old_dict['method_period'], 'new': line.method_period}
    #
    #         if values.get('state') and line:
    #             kay_val_dict = dict(line._fields['state'].selection)  # here 'type' is field name
    #             data_dict['state'] = {'name': 'Status', 'old': kay_val_dict.get(old_dict['state']), 'new': kay_val_dict[line.state]}
    #
    #         if values.get('employee_id'):
    #             data_dict['employee_id'] = {'name': 'Employee ', 'old': old_dict['employee_id'], 'new': line.employee_id.name}
    #
    #         if values.get('partner_id'):
    #             data_dict['partner_id'] = {'name': 'Partner ', 'old': old_dict['partner_id'], 'new': line.partner_id.name}
    #
    #         if values.get('currency_id'):
    #             data_dict['currency_id'] = {'name': 'Currency ', 'old': old_dict['currency_id'], 'new': line.currency_id.name}
    #
    #         if values.get('company_id'):
    #             data_dict['company_id'] = {'name': 'Company ', 'old': old_dict['company_id'], 'new': line.company_id.name}
    #
    #         if values.get('bsg_branches_id'):
    #             data_dict['bsg_branches_id'] = {'name': 'Branch', 'old': old_dict['bsg_branches_id'], 'new': line.bsg_branches_id.branch_ar_name}
    #
    #         if values.get('department_id'):
    #             data_dict['department_id'] = {'name': 'Department', 'old': old_dict['department_id'], 'new': line.department_id.name}
    #
    #         if values.get('fleet_vehicle_id'):
    #             data_dict['fleet_vehicle_id'] = {'name': 'Vehicle', 'old': old_dict['fleet_vehicle_id'], 'new': line.fleet_vehicle_id.name}
    #
    #         if values.get('category_id'):
    #             data_dict['category_id'] = {'name': 'Category', 'old': old_dict['category_id'], 'new': line.category_id.name}
    #
    #         if values.get('account_analytic_id'):
    #             data_dict['account_analytic_id'] = {'name': 'Analytic Account', 'old': old_dict['account_analytic_id'], 'new': line.account_analytic_id.name}
    #     if data_dict:
    #         log_body = "<p>Reference/Description : " + reference + "</p>"
    #         for val in data_dict.keys():
    #             log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
    #                 data_dict[val]['new']) + '</li>'
    #         self.env['mail.message'].create(
    #             {'body': log_body, 'model': 'account.asset.asset', 'res_id': line.id, 'subtype_id': '2'})
    #     return res

    @api.onchange("expense_mode", "employee_id", "fleet_vehicle_id")
    def onchange_expense_mode(self):
        employee = self.employee_id
        expense_mode = self.expense_mode
        vehicle = self.fleet_vehicle_id

        # self.bsg_branches_id = False
        self.department_id = False
        self.account_analytic_id = False
        self.partner_id = False
        self.code = False

        if expense_mode == "employee" and employee:
            if not vehicle:
                self.fleet_vehicle_id = employee.vehicle_sticker_no and self.env['fleet.vehicle'].search(
                [('taq_number', '=', employee.vehicle_sticker_no), ('company_id', '=', employee.company_id.id)]) or False
                    # employee.vehicle_sticker_no
            self.bsg_branches_id = employee.branch_id
            self.department_id = employee.department_id
            self.account_analytic_id = employee.contract_id.analytic_account_id
            self.partner_id = employee.partner_id
            self.code = employee.bsg_empiqama.bsg_iqama_name

        if expense_mode == "vehicles" and vehicle:
            self.bsg_branches_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', '=', '46')], limit=1)
            self.department_id = False
            self.partner_id = False
            self.account_analytic_id = vehicle.vehicle_type.analytic_account_id
            self.code = vehicle.estmaira_serial_no

        if expense_mode == "other":
            self.employee_id = False

    # override cron
    # compute_generated_entries does not exist in base
    # @api.model
    # def _cron_generate_entries(self):
    #     types = ["purchase", "sale"]
    #     for asset_type in types:
    #         self.compute_generated_entries(datetime.today(), asset_type)
    #
    # @api.model
    # def _cron_generate_expense_entries(self):
    #     self.compute_generated_entries(datetime.today(), "expense")

###############################################################################


# class AccountAssetDepreciationLine(models.Model):
#     _inherit = 'account.asset.depreciation.line'
#
#     @api.multi
#     def create_move(self, post_move=True):
#         move_ids = super(AccountAssetDepreciationLine, self).create_move(post_move)
#         for line in self:
#             if line.asset_id.type == "expense":
#                 line.move_id.sudo().post()
#         return move_ids
#
#     # override to pass value as needed
#     def _prepare_move(self, line):
#         category_id = line.asset_id.category_id
#         account_analytic_id = line.asset_id.account_analytic_id
#         analytic_tag_ids = line.asset_id.analytic_tag_ids
#         depreciation_date = self.env.context.get(
#             'depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
#         company_currency = line.asset_id.company_id.currency_id
#         current_currency = line.asset_id.currency_id
#         prec = company_currency.decimal_places
#         amount = current_currency._convert(
#             line.amount, company_currency, line.asset_id.company_id, depreciation_date)
#         asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
#         move_line_1 = {
#             'name': asset_name,
#             'account_id': category_id.account_depreciation_id.id,
#             'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
#             'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
#             'partner_id': line.asset_id.partner_id.id,
#             'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
#             'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
#             'bsg_branches_id': line.asset_id.bsg_branches_id.id if category_id.type == 'sale' else False,
#             'department_id': line.asset_id.department_id.id if category_id.type == 'sale' else False,
#             'fleet_vehicle_id': line.asset_id.fleet_vehicle_id.id if category_id.type == 'sale' else False,
#             'currency_id': company_currency != current_currency and current_currency.id or False,
#             'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
#         }
#         move_line_2 = {
#             'name': asset_name,
#             'account_id': category_id.account_depreciation_expense_id.id,
#             'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
#             'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
#             'partner_id': line.asset_id.partner_id.id,
#             ##########
#             'analytic_account_id': account_analytic_id.id if category_id.type in ('purchase', 'expense') else False,
#             'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type in ('purchase', 'expense') else False,
#             'bsg_branches_id': line.asset_id.bsg_branches_id.id if category_id.type in ('purchase', 'expense') else False,
#             'department_id': line.asset_id.department_id.id if category_id.type in ('purchase', 'expense') else False,
#             'fleet_vehicle_id': line.asset_id.fleet_vehicle_id.id if category_id.type in ('purchase', 'expense') else False,
#             ##########
#             'currency_id': company_currency != current_currency and current_currency.id or False,
#             'amount_currency': company_currency != current_currency and line.amount or 0.0,
#         }
#         move_vals = {
#             'ref': line.asset_id.code,
#             'date': depreciation_date or False,
#             'journal_id': category_id.journal_id.id,
#             'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
#         }
#         return move_vals
#
#     def write(self, values):
#         """Override to log changes"""
#         old_dict = {'name': self.name if self.name else '',
#                     'move_id': self.move_id if self.move_id else '',
#                     'amount': self.amount if self.amount else '',
#                     'sequence': self.sequence if self.sequence else '',
#                     'remaining_value': self.remaining_value if self.remaining_value else '',
#                     'depreciated_value': self.depreciated_value if self.depreciated_value else '',
#                     'depreciation_date': self.depreciation_date if self.depreciation_date else '',}
#         data_dict = {}
#         reference = self.name if self.name else ''
#         if values.get('name'):
#             data_dict['name'] = {'name': 'Name', 'old': old_dict['name'], 'new': values.get('name')}
#         if values.get('move_id'):
#             data_dict['move_id'] = {'name': 'Move ', 'old': old_dict['move_id'], 'new': values.get('move_id')}
#         if values.get('amount'):
#             data_dict['amount'] = {'name': 'Amount', 'old': old_dict['amount'], 'new': values.get('amount')}
#         if values.get('sequence'):
#             data_dict['sequence'] = {'name': 'Sequence', 'old': old_dict['sequence'], 'new': values.get('sequence')}
#         if values.get('remaining_value'):
#             data_dict['remaining_value'] = {'name': 'Remaining Value', 'old': old_dict['remaining_value'], 'new': values.get('remaining_value')}
#         if values.get('depreciated_value'):
#             data_dict['depreciated_value'] = {'name': 'Depreciated Value', 'old': old_dict['depreciated_value'], 'new': values.get('depreciated_value')}
#         if values.get('depreciation_date'):
#             data_dict['depreciation_date'] = {'name': 'Date', 'old': old_dict['depreciation_date'], 'new': values.get('depreciation_date')}
#         if data_dict:
#             log_body = "<p>Reference/Description : " + reference + "</p>"
#             for val in data_dict.keys():
#                 log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
#                     data_dict[val]['new']) + '</li>'
#             self.env['mail.message'].create(
#                 {'body': log_body, 'model': 'account.asset.asset', 'res_id': self.asset_id.id, 'subtype_id': '2'})
#         return super(AccountAssetDepreciationLine, self).write(values)
