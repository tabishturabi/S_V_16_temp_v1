# -*- coding: utf-8 -*-
import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

# class AccountAssetDepreciationLine(models.Model):
#     _inherit = 'account.asset.depreciation.line'
#
#     #override to pass value as needed
#     def _prepare_move(self, line):
#         category_id = line.asset_id.category_id
#         account_analytic_id = line.asset_id.account_analytic_id
#         analytic_tag_ids = line.asset_id.analytic_tag_ids
#         depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
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
#             'bsg_branches_id' : line.asset_id.bsg_branches_id.id if category_id.type == 'sale' else False,
#             'department_id' : line.asset_id.department_id.id if category_id.type == 'sale' else False,
#             'fleet_vehicle_id' : line.asset_id.fleet_vehicle_id.id if category_id.type == 'sale' else False,
#             'currency_id': company_currency != current_currency and current_currency.id or False,
#             'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
#         }
#         move_line_2 = {
#             'name': asset_name,
#             'account_id': category_id.account_depreciation_expense_id.id,
#             'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
#             'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
#             'partner_id': line.asset_id.partner_id.id,
#             'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
#             'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
#             'bsg_branches_id' : line.asset_id.bsg_branches_id.id if category_id.type == 'purchase' else False,
#             'department_id' : line.asset_id.department_id.id if category_id.type == 'purchase' else False,
#             'fleet_vehicle_id' : line.asset_id.fleet_vehicle_id.id if category_id.type == 'purchase' else False,
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

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset'

    #override to perfect calculation as need
    # @api.multi
    # def compute_depreciation_board(self):
    #     self.ensure_one()
    #
    #     posted_depreciation_line_ids = self.depreciation_move_ids.filtered(lambda x: x.move_check).sorted(key=lambda l: l.depreciation_date)
    #     unposted_depreciation_line_ids = self.depreciation_move_ids.filtered(lambda x: not x.move_check)
    #
    #     # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
    #     commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]
    #
    #     if self.value_residual != 0.0:
    #         amount_to_depr = residual_amount = self.value_residual
    #
    #         # if we already have some previous validated entries, starting date is last entry + method period
    #         if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
    #             last_depreciation_date = fields.Date.from_string(posted_depreciation_line_ids[-1].depreciation_date)
    #             depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)
    #         else:
    #             # depreciation_date computed from the purchase date
    #             depreciation_date = self.date
    #             if self.date_first_depreciation == 'last_day_period':
    #                 # depreciation_date = the last day of the month
    #                 depreciation_date = depreciation_date + relativedelta(day=31)
    #                 # ... or fiscalyear depending the number of period
    #                 if self.method_period == 12:
    #                     depreciation_date = depreciation_date + relativedelta(month=self.company_id.fiscalyear_last_month)
    #                     depreciation_date = depreciation_date + relativedelta(day=self.company_id.fiscalyear_last_day)
    #                     if depreciation_date < self.date:
    #                         depreciation_date = depreciation_date + relativedelta(years=1)
    #             elif self.first_depreciation_manual_date and self.first_depreciation_manual_date != self.date:
    #                 # depreciation_date set manually from the 'first_depreciation_manual_date' field
    #                 depreciation_date = self.first_depreciation_manual_date
    #
    #         total_days = (depreciation_date.year % 4) and 365 or 366
    #         month_day = depreciation_date.day
    #         undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)
    #
    #         for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
    #             sequence = x + 1
    #             amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date)
    #             amount = self.currency_id.round(amount)
    #             if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
    #                 continue
    #             residual_amount -= amount
    #             vals = {
    #                 'amount': amount,
    #                 'asset_id': self.id,
    #                 'sequence': sequence,
    #                 'name': (self.code or '') + '/' + str(sequence),
    #                 'remaining_value': residual_amount,
    #                 'depreciated_value': self.value - (self.salvage_value + residual_amount) - self.accumulated_depreciation,
    #                 'depreciation_date': depreciation_date,
    #             }
    #             commands.append((0, False, vals))
    #
    #             depreciation_date = depreciation_date + relativedelta(months=+self.method_period)
    #
    #             if month_day > 28 and self.date_first_depreciation == 'manual':
    #                 max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
    #                 depreciation_date = depreciation_date.replace(day=min(max_day_in_month, month_day))
    #
    #             # datetime doesn't take into account that the number of days is not the same for each month
    #             if not self.prorata and self.method_period % 12 != 0 and self.date_first_depreciation == 'last_day_period':
    #                 max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
    #                 depreciation_date = depreciation_date.replace(day=max_day_in_month)
    #
    #     self.write({'depreciation_move_ids': commands})
    #
    #     return True

    #oveeride to pass true value on that
    def _get_disposal_moves(self):
        move_ids = []
        for asset in self:
            unposted_depreciation_line_ids = asset.depreciation_move_ids.filtered(lambda x: not x.move_check)
            if unposted_depreciation_line_ids:
                old_values = {
                    'method_end': asset.method_end,
                    'method_number': asset.method_number,
                }

                # Remove all unposted depr. lines
                commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

                # Create a new depr. line with the residual amount and post it
                sequence = len(asset.depreciation_move_ids) - len(unposted_depreciation_line_ids) + 1
                today = fields.Datetime.today()
                vals = {
                    'amount': asset.value_residual,
                    'asset_id': asset.id,
                    'sequence': sequence,
                    'name': (asset.code or '') + '/' + str(sequence),
                    'remaining_value': 0,
                    'depreciated_value': asset.value - asset.salvage_value - asset.accumulated_depreciation,  # the asset is completely depreciated
                    'depreciation_date': today,
                }
                commands.append((0, False, vals))
                asset.write({'depreciation_move_ids': commands, 'method_end': today, 'method_number': sequence})
                tracked_fields = self.env['account.asset'].fields_get(['method_number', 'method_end'])
                changes, tracking_value_ids = asset._message_track(tracked_fields, old_values)
                if changes:
                    asset.message_post(subject=_('Asset sold or disposed. Accounting entry awaiting for validation.'), tracking_value_ids=tracking_value_ids)
                move_ids += asset.depreciation_move_ids[-1].create_move(post_move=False)

        return move_ids

    #override to pass branch, truck and department field
    def onchange_category_id_values_on_create(self, vals):
        if vals:
            if vals['category_id']:
                category = self.env['account.asset.category'].browse(vals['category_id'])
                return {
                    'value': {
                        'method': category.method,
                        'method_number': category.method_number,
                        'method_time': category.method_time,
                        'method_period': category.method_period,
                        'method_progress_factor': category.method_progress_factor,
                        'method_end': category.method_end,
                        'prorata': category.prorata,
                        #'bsg_branches_id' : category.bsg_branches_id.id,
                        #'department_id' : category.department_id.id,
                        #'fleet_vehicle_id' : category.fleet_vehicle_id.id,
                        'date_first_depreciation': category.date_first_depreciation,
                        'account_analytic_id': not vals['account_analytic_id'] and category.account_analytic_id.id  or vals['account_analytic_id'],
                        'analytic_tag_ids':  not vals['analytic_tag_ids'] and [(6, 0, category.analytic_tag_ids.ids)] or [(6, 0, vals['analytic_tag_ids'])],
                    }
                }

    #override to add new filed deduction on that\
    # @api.one
    @api.depends('value', 'accumulated_depreciation', 'salvage_value', 'depreciation_move_ids.move_check', 'depreciation_move_ids.amount')
    def _amount_residual(self):
        total_amount = 0.0
        for line in self.depreciation_move_ids:
            if line.move_check:
                total_amount += line.amount
        self.value_residual = self.value - total_amount - self.salvage_value - self.accumulated_depreciation


    bsg_branches_id = fields.Many2one('bsg_branches.bsg_branches', string="Branch")
    department_id = fields.Many2one('hr.department',string="Department")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle',string="Truck")
    accumulated_depreciation = fields.Float(string="Accumulated Depreciation")
    is_sold = fields.Boolean()
    sale_date = fields.Date()
