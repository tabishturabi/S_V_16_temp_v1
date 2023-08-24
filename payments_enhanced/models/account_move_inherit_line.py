# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    #override to pass the branch filed vlaue
    #@api.multi
    #def create_analytic_lines(self):
    """ Create analytic items upon validation of an account.move.line having an analytic account or an analytic distribution.
        for obj_line in self:
            if obj_line.payment_id.state == 'draft' or not obj_line.payment_id.state:
                for tag in obj_line.analytic_tag_ids.filtered('active_analytic_distribution'):
                    for distribution in tag.analytic_distribution_ids:
                        vals_line = obj_line._prepare_analytic_distribution_line(distribution)
                        if obj_line.invoice_id:
                            vals_line['branch_id'] = obj_line.invoice_id.loc_from.loc_branch_id.id
                        elif obj_line.payment_id:
                            if obj_line.payment_id.branch_ids:
                                vals_line['branch_id'] = obj_line.payment_id.branch_ids.id
                        self.env['account.analytic.line'].create(vals_line)
                if obj_line.analytic_account_id:
                    vals_line = obj_line._prepare_analytic_line()[0]
                    if obj_line.invoice_id:
                        vals_line['branch_id'] = obj_line.invoice_id.loc_from.loc_branch_id.id
                    elif obj_line.payment_id:
                        if obj_line.payment_id.branch_ids:
                            vals_line['branch_id'] = obj_line.payment_id.branch_ids.id
                    self.env['account.analytic.line'].create(vals_line)"""
    
    #For Pass Other Analysis Fields
    
    def _prepare_analytic_line(self):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            an analytic account. This method is intended to be extended in other modules.
        """
        amount = (self.credit or 0.0) - (self.debit or 0.0)
        default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
        # print('_prepare_analytic_line..........account_id.',self.account_id)
        return {
            'name': default_name,
            'date': self.date,
            'account_id': self.account_id.id,
            'tag_ids': [(6, 0, self._get_analytic_tag_ids())],
            'unit_amount': self.quantity,
            'product_id': self.product_id and self.product_id.id or False,
            'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
            'amount': amount,
            'general_account_id': self.account_id.id,
            'ref': self.ref,
            'move_id': self.id,
            'user_id': self.invoice_id.user_id.id or self._uid,
            'partner_id': self.partner_id.id,
            'company_id': self.analytic_account_id.company_id.id or self.env.user.company_id.id,
            'branch_id' : self.bsg_branches_id and self.bsg_branches_id.id or False,
            'fleet_vehicle_id' : self.fleet_vehicle_id and self.fleet_vehicle_id.id or False,
            'trailer_id' : self.trailer_id and self.trailer_id.id or False,
            'department_id': self.department_id and self.department_id.id or False,
        }


    # def _prepare_analytic_distribution_line(self, distribution, account_id, distribution_on_each_plan):
    #     """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
    #         analytic tags with analytic distribution.
    #     """
    #     self.ensure_one()
    #     print('................account_id...........',account_id)
    #     account_id = int(account_id)
    #     account = self.env['account.analytic.account'].browse(account_id)
    #     distribution_plan = distribution_on_each_plan.get(account.root_plan_id, 0) + distribution
    #     if self.env.company.currency_id.compare_amounts(distribution_plan, 100) == 0:
    #         amount = -self.balance * (100 - distribution_on_each_plan.get(account.root_plan_id, 0)) / 100.0
    #     else:
    #         amount = -self.balance * distribution / 100.0
    #     distribution_on_each_plan[account.root_plan_id] = distribution_plan
    #     default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
    #     return {
    #         'name': default_name,
    #         'date': self.date,
    #         'account_id': int(account_id) if account_id not in ['false'] else 1,
    #         'partner_id': self.partner_id.id,
    #         'unit_amount': self.quantity,
    #         'product_id': self.product_id and self.product_id.id or False,
    #         'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
    #         'amount': amount,
    #         'general_account_id': self.account_id.id,
    #         'ref': self.ref,
    #         'move_line_id': self.id,
    #         'user_id': self.move_id.invoice_user_id.id or self._uid,
    #         'company_id': account.company_id.id or self.company_id.id or self.env.company.id,
    #     }


    def _prepare_analytic_distribution_line(self, distribution,account_id, distribution_on_each_plan):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            analytic tags with analytic distribution.
        """
        self.ensure_one()
        print('...........self.............',self)
        print('...........distribution.............',distribution)
        print('...........distribution_on_each_plan.............',distribution_on_each_plan)
        print('...........account_id.............',account_id)
        print('...........account_id.............',type(account_id))
        print('...........self.account_id.............',self.account_id)
        print('...........self.analytic_distribution.............',self.analytic_distribution.items())

        # Migratio Note
        # amount = -self.balance * distribution.percentage / 100.0
        amount = -self.balance * distribution / 100.0
        default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
        # Migration Note
        # 'tag_ids': [(6, 0, [distribution.tag_id.id] + self._get_analytic_tag_ids())],
        # 'tag_ids': [(6, 0, self.tax_tag_ids.ids)],
        return {
            'name': default_name,
            'date': self.date,
            'account_id': int(account_id) if account_id not in ['false'] else 1,
            'partner_id': self.partner_id.id,
            'unit_amount': self.quantity,
            'product_id': self.product_id and self.product_id.id or False,
            'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
            'amount': amount,
            'general_account_id': self.account_id.id,
            'ref': self.ref,
            'move_line_id': self.id,
            'user_id': self.move_id.user_id.id or self._uid,
            'company_id': self.account_id.company_id.id or self.env.user.company_id.id,
            'branch_id' : self.bsg_branches_id and self.bsg_branches_id.id or False,
            'fleet_vehicle_id' : self.fleet_vehicle_id and self.fleet_vehicle_id.id or False,
            'trailer_id' : self.trailer_id and self.trailer_id.id or False,
            'department_id': self.department_id and self.department_id.id or False,
        }
    # Migration ToDo Note
    # debit = fields.Float(default=0.0, currency_field='company_currency_id', digits=dp.get_precision('Vouchers'))
    # credit = fields.Float(default=0.0, currency_field='company_currency_id', digits=dp.get_precision('Vouchers'))
    amount_currency = fields.Float(default=0.0, help="The amount expressed in an optional other currency if it is a multi-currency entry.", digits=dp.get_precision('Vouchers'))
    
    # branch_id = fields.Many2one('res.partner', string='Branch Customer')
    branch_name = fields.Char('Branch Customer ')
    bsg_branches_id = fields.Many2one('bsg_branches.bsg_branches', string="Branch ID")
    department_id = fields.Many2one('hr.department',string="Departments")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle',string="Truck")

    #override to used voucher line accont and analytic account
    @api.model
    def create(self, vals):
        # if not vals.get('account_id'):
        #     raise UserError(_("Be sure you have Defined Account in Partner or Journal"))
        payment = self.env['account.payment'].search([('id','=',vals.get('payment_id'))])
        if payment.payment_type == 'inbound':
            if vals.get('credit') != 0.0 and not vals.get('invoice_id'):
                if len(payment.voucher_line_ids) != 0:
                    vals['account_id'] = payment.voucher_line_ids[0].account_id.id
                    vals['analytic_account_id'] = payment.voucher_line_ids[0].analytic_id.id
            if vals.get('debit') != 0.0 and not vals.get('invoice_id'):
                if len(payment.voucher_line_ids) != 0:
                    vals['account_id'] = payment.journal_id.default_account_id.id
        if vals.get('payment_id'):
            payment = self.env['account.payment'].search([('id','=',vals.get('payment_id'))])
            if payment.payment_type == 'outbound':
                if vals.get('credit') != 0.0 and not vals.get('invoice_id'):
                    if len(payment.voucher_line_ids) != 0:
                        vals['account_id'] = payment.journal_id.default_account_id.id
                if vals.get('debit') != 0.0 and not vals.get('invoice_id'):
                    if len(payment.voucher_line_ids) != 0:
                        vals['account_id'] = payment.voucher_line_ids[0].account_id.id
                        vals['analytic_account_id'] = payment.voucher_line_ids[0].analytic_id.id
        res = super(AccountMoveLine, self).create(vals)        
        if res.move_id and not res.bsg_branches_id:
            res.update({'bsg_branches_id' : res.move_id.loc_from.loc_branch_id.id})
        if not res.bsg_branches_id and res.payment_id:
            res.update({'bsg_branches_id' : res.payment_id.branch_ids.id})
        return res
