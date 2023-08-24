# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from odoo.exceptions import UserError, ValidationError, Warning

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}


class account_cargo_line_payment_wizard(models.TransientModel):
    _name = "account.cargo.line.payment.wizard"
    _rec_name = 'account_invoice_line_id'

    cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line', string="Cargo Sale Line", required=True)
    account_invoice_line_id = fields.Many2one('account.move.line', 'Invoice Line')
    # account_payment_id = fields.Many2one('account.payment','Payment',required=True)
    # state = fields.Selection([('draft','Draft'),('posted','Posted'),('reconciled','Reconciled'),('cancelled','Cancelled'),('reversal_entry','Reversal Entry')],related='account_payment_id.state')
    total = fields.Monetary(related='account_invoice_line_id.price_total', store=True)
    currency_id = fields.Many2one('res.currency', related='account_invoice_line_id.currency_id', store=True)
    amount = fields.Float('Paid Amount')
    residual = fields.Float()
    is_other_service = fields.Boolean(related='account_invoice_line_id.is_other_service_line',
                                      string='Is Other Service', store=True)
    multi = fields.Boolean()
    payment_currency_id = fields.Many2one('res.currency')
    currency_amount = fields.Float(compute='compute_currency_amount')
    date = fields.Date()

    @api.depends('currency_id', 'payment_currency_id', 'amount', 'date')
    def compute_currency_amount(self):
        for rec in self:
            active_ids = rec.env.context.get('active_ids')
            move_id = self.env['account.move'].browse(active_ids)
            rec.currency_amount = move_id.currency_id._convert(
                rec.amount, rec.payment_currency_id, self.env.user.company_id, rec.date or fields.Date.today())

    @api.constrains('amount')
    def _constrains_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise Warning(_('Sorry! Paid Amount Must Be Greater Than 0!'))
            if rec.amount > rec.residual:
                raise Warning(_("Sorry! Paid Amount Can't Be Greater Than Residual Amount !"))


class account_register_payments(models.TransientModel):
    # Migration Note
    # _inherit = "account.register.payments"
    _inherit = "account.payment.register"

    @api.model
    def default_get(self, fields):
        result = super(account_register_payments, self).default_get(fields)
        if self.env.user.has_group('payments_enhanced.group_allowed_pay_with_fc'):
            result.update({
                'is_allow_pay_with_fc': True,
            })
        else:
            result.update({
                'is_allow_pay_with_fc': False,
            })
        if self.env.user.has_group('account.group_account_manager') or self.env.user.has_group(
                'account.group_account_user'):
            result.update({
                'allow_edit_in_wiz': True,
            })
        else:
            result.update({
                'allow_edit_in_wiz': False,
            })
        return result

    is_more_amount = fields.Boolean(string="Is More Amount")
    bsg_vehicle_cargo_sale_line_ids = fields.Many2many('account.cargo.line.payment.wizard',
                                                       string='So Line Wizard Payment')
    cargo_sale_line_order_ids = fields.Many2many(string="Cargo Sale Lines", comodel_name="bsg_vehicle_cargo_sale_line",
                                                 compute='_compute_so_line', copy=False)
    is_new_order = fields.Boolean()
    cargo_sale_order_id = fields.Many2one(string="Cargo Sale ID", comodel_name="bsg_vehicle_cargo_sale", copy=False)
    multi_invoice = fields.Boolean(compute='compute_multi_ivn', store=True)
    is_allow_pay_with_fc = fields.Boolean(string="Is Allowed Payment With FC", default='get_is_allow_pay_with_fc')
    operation_number = fields.Char(string="Operation Number")
    attachment_id = fields.Binary(string="Attachment")
    allow_edit_in_wiz = fields.Boolean(default='get_allow_edit_in_wiz')
    show_invoice_amount = fields.Boolean("Show Invoices Amount")
    is_for_refund = fields.Boolean()
    is_cancel = fields.Boolean(string="Is Cancel")
    is_for_old_order = fields.Boolean('Is Old Order', related='cargo_sale_order_id.is_old_order', store=True)
    cancel_amt = fields.Float(string='Cancel Amount')
    show_communication_field = fields.Boolean()
    # MIgration NOte
    is_patrtially_payment = fields.Boolean(string="Is Partially Payment")
    collectionre = fields.Char("Collection Voucher ref")
    branch_id = fields.Many2one('res.partner', string='Branch Customer')

    def _compute_journal_id(self):
        res = super(account_register_payments, self)._compute_journal_id()
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        # if active_model == 'account.collection':
        #     collectionss = self.env['account.collection'].browse(active_ids)
        #     invoices = self.env['account.move'].browse(collectionss.account_invoice.ids)
        #     self.amount = abs(self._compute_payment_amount(invoices))
        return res

    def action_validate_invoice_payment(self):
        """ Posts a payment used to pay an invoice. This function only posts the
        payment by default but can be overridden to apply specific post or pre-processing.
        payment by default but can be overridden to apply specific post or pre-processing.
        It is called by the "validate" button of the popup window
        triggered on invoice form by the "Register Payment" button.
        """
        if self._context.get('pass_sale_order_id'):
            cargo_id = self.env['bsg_vehicle_cargo_sale'].search([('id', '=', self._context.get('pass_sale_order_id'))])
            if cargo_id:
                if self.amount >= sum(self.env['account.move'].search(
                            [('id', '=', self._context.get('default_invoice_ids')[0][1])]).mapped('amount_residual')):
                    self.action_create_payments()
                    cargo_id.write({'state': 'done'})

        '''if self.amount == self.due_invoice_amount :
            cargo_id = self.env['bsg_vehicle_cargo_sale'].search([('id','=',self._context.get('pass_sale_order_id'))])
            cargo_id.write({'state' : 'done'})

        cargo_id = self.env['bsg_vehicle_cargo_sale'].search([('id','=',self._context.get('active_id'))])        
        if not cargo_id:
            if self.cargo_sale_order_id.payment_method.payment_type != 'pod':
                self.cargo_sale_order_id.write({'state' : 'done'})
        if cargo_id.payment_method.payment_type != 'pod': 
            if not self.is_patrtially_payment:
                cargo_id.write({'state' : 'done'})
            if self.is_patrtially_payment:
                if self.amount == self.cargo_sale_order_id.invoice_ids.residual:
                    cargo_id.write({'state' : 'done'})'''
        # if self.amount > self.due_invoice_amount and self.show_invoice_amount:
        #     raise Warning(_("You cannot Pay More than Amount "))

        total_amount1 = 0.0
        if self.bsg_vehicle_cargo_sale_line_ids:
            for so_line in self.bsg_vehicle_cargo_sale_line_ids.mapped('cargo_sale_line_id').filtered(
                    lambda x: x.is_paid and x.state == 'draft'):
                so_line.write({'state': 'confirm'})
        return

        # Migration Note invoice_ids does not exist in this model

    # @api.depends('invoice_ids')
    # def compute_multi_ivn(self):
    #     for rec in self:
    #         if len(rec.invoice_ids) > 1:
    #             rec.multi_invoice = True
    #         else:
    #             rec.multi_invoice = False

    # Migration Note
    # @api.depends('invoice_ids.invoice_line_ids')
    @api.depends('line_ids')
    def _compute_so_line(self):
        for rec in self:
            active_ids = self._context.get('active_ids')
            invoice_ids = self.env['account.move'].browse(active_ids)
            if invoice_ids.invoice_line_ids.mapped('cargo_sale_line_id'):
                rec.cargo_sale_line_order_ids = self.bsg_vehicle_cargo_sale_line_ids.mapped('cargo_sale_line_id')
            elif invoice_ids:
                rec.cargo_sale_line_order_ids = invoice_ids.mapped('invoice_line_ids').filtered(
                    lambda s: not s.is_paid).mapped('cargo_sale_line_id')

    @api.onchange('cargo_sale_line_order_ids')
    def _compute_so_line_payment(self):
        payment_line = []
        self.bsg_vehicle_cargo_sale_line_ids = False
        active_ids = self._context.get('active_ids')
        invoice_ids = self.env['account.move'].browse(active_ids)
        if self.cargo_sale_line_order_ids:
            for line in self.cargo_sale_line_order_ids:
                for inv_line in invoice_ids.mapped('invoice_line_ids'):
                    payment_line.append({
                        'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                        'total': inv_line.price_total,
                        'account_invoice_line_id': inv_line.id,
                        'amount': inv_line.price_total - inv_line.paid_amount,
                        'residual': inv_line.price_total - inv_line.paid_amount,
                        # 'multi': self.multi,
                        'payment_currency_id': self.currency_id.id,
                        'date': self.payment_date
                    })
            self.bsg_vehicle_cargo_sale_line_ids = [(0, 0, pay_line) for pay_line in payment_line]
            if self._context.get('active_model') == 'bsg_vehicle_cargo_sale_line':
                self.amount = sum(self.bsg_vehicle_cargo_sale_line_ids.mapped('currency_amount'))

    def _compute_journal_id(self):
        res = super(account_register_payments, self)._compute_journal_id()
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        if active_model == 'bsg_vehicle_cargo_sale_line':
            self.amount = sum(self.bsg_vehicle_cargo_sale_line_ids.mapped('currency_amount'))
        return res

    @api.onchange('currency_id')
    def _onchange_currency(self):
        self._compute_amount()
        self.amount = abs(self.amount)
        if self.bsg_vehicle_cargo_sale_line_ids:
            self.bsg_vehicle_cargo_sale_line_ids.update({
                'payment_currency_id': self.currency_id.id,
                'date': self.payment_date
            })
            self.bsg_vehicle_cargo_sale_line_ids.compute_currency_amount()
            self.amount = sum(self.bsg_vehicle_cargo_sale_line_ids.mapped('currency_amount'))

        # Set by default the first liquidity journal having this currency if exists.
        if self.journal_id:
            return
        journal = self.env['account.journal'].search(
            [('type', 'in', ('bank', 'cash')), ('currency_id', '=', self.currency_id.id)], limit=1)
        if journal:
            return {'value': {'journal_id': journal.id}}

    # @api.multie
    def _prepare_payment_vals(self, invoices):
        '''Create the payment values.

        :param invoices: The invoices that should have the same commercial partner and the same type.
        :return: The payment values as a dictionary.
        '''
        values = super(account_register_payments, self)._prepare_payment_vals(invoices)
        if self.cargo_sale_line_order_ids:
            values['cargo_sale_line_order_ids'] = [(6, 0, self.cargo_sale_line_order_ids.ids)]
        values['operation_number'] = self.operation_number
        values['attachment_id'] = self.attachment_id
        return values

    # def _create_payment_vals_from_wizard(self, batch_result):
    #     res = super()._create_payments(batch_result)
    #     print("")
    #     return res


    def _create_payments(self):
        # self._compute_amount()
        res = super()._create_payments()
        self.btn_create_payments(res)
        return res

    def btn_create_payments(self,payment):
        '''Create payments according to the invoices.
        Having invoices with different commercial_partner_id or different type (Vendor bills with customer invoices)
        leads to multiple payments.
        In case of all the invoices are related to the same commercial_partner_id and have the same type,
        only one payment will be created.

        :return: The ir.actions.act_window to show created payments.
        '''
        # Payment = self.env['account.payment']
        # payments = Payment
        # for payment_vals in self.get_payments_vals():
        #     payments += Payment.create(payment_vals)
        cargo_line_pay = self.env['account.cargo.line.payment']
        payments = self.env['account.payment'].browse(payment.id)
        if self.cargo_sale_line_order_ids:
            for pay in payments:
                for so_line in self.cargo_sale_line_order_ids:
                    if True:
                        for inv_line in pay.invoice_ids.mapped('invoice_line_ids').filtered(
                                lambda s: s.cargo_sale_line_id.id == so_line.id and not s.is_paid):
                            amount = pay.currency_id._convert(
                                pay.amount_total, inv_line.move_id.currency_id, self.env.user.company_id,
                                pay.date or fields.Date.today())
                            cargo_line_pay.with_context({'without_check_amount': True}).create({
                                'cargo_sale_line_id': inv_line.cargo_sale_line_id.id,
                                'account_invoice_line_id': inv_line.id,
                                'amount': amount <= (inv_line.price_total - inv_line.paid_amount) and amount or (
                                        inv_line.price_total - inv_line.paid_amount),
                                'residual': inv_line.price_total - inv_line.paid_amount,
                                'account_payment_id': pay.id,
                            })
        # payments.state = 'posted'
        payments.post_state()
        # payments.action_post()

        action_vals = {
            'name': _('Payments'),
            'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(payments) == 1:
            action_vals.update({'res_id': payments[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals

    @api.onchange('amount', 'currency_id')
    def _onchange_amount(self):
        # jrnl_filters = self._compute_journal_domain_and_types()
        # journal_types = jrnl_filters['journal_types']
        # domain_on_types = [('type', 'in', list(journal_types))]
        brnch_list = []
        # if self.amount <= 0 and self.show_invoice_amount:
        #    self.is_more_amount = True
        # if self.amount > self.due_invoice_amount and self.show_invoice_amount:
        #     self.is_more_amount = True
        # if self.is_more_amount:
        #     raise Warning(_("You cannot Pay More than Amount "))  
        # return {'type': 'ir.actions.act_window_close'}
        # raise Warning(_("You cannot Pay More than Amount "))
        # for data in self.env['bsg_branches.bsg_branches'].search([('member_ids.user_id','=',self.env.user.id)]):
        #     brnch_list.append(data.id)
        # if self.journal_id.type not in journal_types:
        #     self.journal_id = self.env['account.journal'].search(domain_on_types, limit=1)
        # if self.is_more_amount:
        #    raise Warning(_("You cannot Pay More than Amount "))  
        if self.partner_type == 'customer':
            if self._context.get('active_model') == 'transport.management':
                self.journal_id = False
                if self.payment_type == 'inbound':
                    return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id)]}}
                else:
                    return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id)]}}
            else:
                if self._context.get('context_sequnce_cash'):
                    if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                        if self.payment_type == 'inbound':
                            return {'domain': {
                                'journal_id': [('type', 'in', ['cash', 'bank']), ('sub_type', 'in', ['Receipt', 'All'])]}}
                        else:
                            return {'domain': {
                                'journal_id': [('type', 'in', ['cash', 'bank']), ('sub_type', 'in', ['Payment', 'All'])]}}
                    else:
                        cargo_search_id = self.env['bsg_vehicle_cargo_sale'].browse(self._context.get('active_id'))
                        if self.payment_type == 'inbound':
                            cargo_sale_journal = self.env['account.journal'].search(
                                [('branches', 'in', cargo_search_id.loc_from.loc_branch_id.id),
                                 ('type', 'in', ['cash']), ('sub_type', 'in', ['Receipt', 'All'])], limit=1)
                            if cargo_sale_journal:
                                self.journal_id = cargo_sale_journal.id
                            else:
                                self.journal_id = False
                            # return {'domain': {'journal_id': ['|',('branches','in',brnch_list),('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('type','in',['cash','bank']),('sub_type','in',['Receipt','All'])]}}
                            return {'domain': {
                                'journal_id': [('branches', 'in', cargo_search_id.loc_from.loc_branch_id.id),
                                               ('type', 'in', ['cash', 'bank']), ('sub_type', 'in', ['Receipt', 'All'])]}}
                        else:
                            cargo_sale_journal = self.env['account.journal'].search(
                                [('branches', 'in', cargo_search_id.loc_from.loc_branch_id.id),
                                 ('type', 'in', ['cash']), ('sub_type', 'in', ['Payment', 'All'])], limit=1)
                            if cargo_sale_journal:
                                self.journal_id = cargo_sale_journal.id
                            else:
                                self.journal_id = False
                            # return {'domain': {'journal_id': ['|',('branches','in',brnch_list),('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('type','in',['cash','bank']),('sub_type','in',['Receipt','All'])]}}
                            return {'domain': {
                                'journal_id': [('branches', 'in', cargo_search_id.loc_from.loc_branch_id.id),
                                               ('type', 'in', ['cash', 'bank']), ('sub_type', 'in', ['Payment', 'All'])]}}
                elif self._context.get('default_show_invoice_amount'):
                    if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                        if self.payment_type == 'inbound':
                            return {'domain': {
                                'journal_id': [('type', 'in', ['cash', 'bank']), ('sub_type', 'in', ['Receipt', 'All'])]}}
                        else:
                            return {'domain': {
                                'journal_id': [('type', 'in', ['cash', 'bank']), ('sub_type', 'in', ['Payment', 'All'])]}}
                    else:
                        cargo_sale_journal = False
                        cargo_search_id = self.env['bsg_vehicle_cargo_sale'].browse(self._context.get('active_id'))
                        user_id = self.env['res.users'].search([('id', '=', self._context.get('uid'))])
                        if self.payment_type == 'inbound':
                            if user_id.user_branch_id.id == cargo_search_id.loc_from.loc_branch_id.id or user_id.user_branch_id.id == cargo_search_id.loc_to.loc_branch_id.id:
                                # cargo_sale_journal = self.env['account.journal'].search(['|',('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('branches','in',cargo_search_id.loc_to.loc_branch_id.id),('type','in',['cash']),('sub_type','in',['Receipt'])],limit=1)
                                cargo_sale_journal = self.env['account.journal'].search(
                                    [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash']),
                                     ('sub_type', 'in', ['Receipt'])], limit=1)
                            if cargo_sale_journal:
                                self.journal_id = cargo_sale_journal.id
                            else:
                                self.journal_id = False
                            # return {'domain': {'journal_id': ['|','|',('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('branches','in',cargo_search_id.loc_to.loc_branch_id.id),('branches','in',brnch_list),('type','in',['cash','bank']),('sub_type','in',['Receipt','All'])]}}    

                            return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id),
                                                              ('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Receipt', 'All']),
                                                              ('at_least_one_inbound', '=', True)]}}
                        else:
                            if user_id.user_branch_id.id == cargo_search_id.loc_from.loc_branch_id.id or user_id.user_branch_id.id == cargo_search_id.loc_to.loc_branch_id.id:
                                # cargo_sale_journal = self.env['account.journal'].search(['|',('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('branches','in',cargo_search_id.loc_to.loc_branch_id.id),('type','in',['cash']),('sub_type','in',['Receipt'])],limit=1)
                                cargo_sale_journal = self.env['account.journal'].search(
                                    [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash']),
                                     ('sub_type', 'in', ['Payment'])], limit=1)
                            if cargo_sale_journal:
                                self.journal_id = cargo_sale_journal.id
                            else:
                                self.journal_id = False
                            # return {'domain': {'journal_id': ['|','|',('branches','in',cargo_search_id.loc_from.loc_branch_id.id),('branches','in',cargo_search_id.loc_to.loc_branch_id.id),('branches','in',brnch_list),('type','in',['cash','bank']),('sub_type','in',['Receipt','All'])]}}    

                            return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id),
                                                              ('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Payment', 'All'])]}}
                else:
                    if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                        if self.payment_type == 'inbound':
                            return {'domain': {
                                'journal_id': [('type', 'in', ['cash', 'bank']), ('sub_type', 'in', ['Receipt', 'All'])]}}
                        else:
                            return {'domain': {
                                'journal_id': [('type', 'in', ['cash', 'bank']), ('sub_type', 'in', ['Payment', 'All'])]}}
                    else:
                        if self.payment_type == 'inbound':
                            jounal_id = self.env['account.journal'].search(
                                [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash', 'bank']),
                                 ('sub_type', 'in', ['Receipt', 'All'])], limit=1)
                            if jounal_id:
                                self.journal_id = jounal_id.id
                            else:
                                self.journal_id = False
                            return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id),
                                                              ('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Receipt', 'All'])]}}
                        else:
                            jounal_id = self.env['account.journal'].search(
                                [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash', 'bank']),
                                 ('sub_type', 'in', ['Payment', 'All'])], limit=1)
                            if jounal_id:
                                self.journal_id = jounal_id.id
                            else:
                                self.journal_id = False
                            return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id),
                                                              ('type', 'in', ['cash', 'bank']),
                                                              ('sub_type', 'in', ['Payment', 'All'])]}}

        elif self.partner_type == 'supplier':
            if self._context.get('active_model') == 'transport.management':
                self.journal_id = False
                if self.payment_type == 'inbound':
                    return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id)]}}
                else:
                    return {'domain': {'journal_id': [('branches', 'in', self.env.user.user_branch_id.id)]}}
            else:
                if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                    if self.payment_type == 'inbound':
                        return {'domain': {'journal_id': [('sub_type', 'in', ['Receipt', 'All'])]}}
                    else:
                        return {'domain': {'journal_id': [('sub_type', 'in', ['Payment', 'All'])]}}
                else:
                    if self.payment_type == 'inbound':
                        jounal_id = self.env['account.journal'].search(
                            [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash', 'bank']),
                             ('sub_type', 'in', ['Receipt', 'All'])], limit=1)
                        if jounal_id:
                            self.journal_id = jounal_id.id
                        else:
                            self.journal_id = False
                        return {'domain': {'journal_id': [('sub_type', 'in', ['Receipt', 'All']),
                                                          ('branches', 'in', self.env.user.user_branch_id.id)]}}
                    else:
                        jounal_id = self.env['account.journal'].search(
                            [('branches', 'in', self.env.user.user_branch_id.id), ('type', 'in', ['cash', 'bank']),
                             ('sub_type', 'in', ['Payment', 'All'])], limit=1)
                        if jounal_id:
                            self.journal_id = jounal_id.id
                        else:
                            self.journal_id = False
                        return {'domain': {'journal_id': [('sub_type', 'in', ['Payment', 'All']),
                                                          ('branches', 'in', self.env.user.user_branch_id.id)]}}
        else:
            if self.env.user.has_group('payments_enhanced.all_branch_access_group'):
                if self.payment_type == 'inbound':
                    return {'domain': {
                        'journal_id': [('type', 'in', ['cash', 'bank'])]}}
                if self.payment_type == 'outbound':
                    return {'domain': {
                        'journal_id': [('type', 'in', ['cash', 'bank'])]}}
                if self.is_internal_transfer:
                    return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank'])]}}
            else:
                if self.payment_type == 'inbound':
                    return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank']),
                                                      ('branches', 'in', self.env.user.user_branch_id.id)]}}
                if self.payment_type == 'outbound':
                    return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank']),
                                                      ('branches', 'in', self.env.user.user_branch_id.id)]}}
                if self.is_internal_transfer:
                    return {'domain': {'journal_id': [('type', 'in', ['cash', 'bank'])]}}


class AccountPayment(models.TransientModel):
    _inherit = "account.payment.register"

    cargo_sale_order_id = fields.Many2one(string="Cargo Sale ID", comodel_name="bsg_vehicle_cargo_sale", copy=False)
    bsg_vehicle_cargo_sale_line_ids = fields.Many2many('account.cargo.line.payment.wizard',
                                                       string='So Line Wizard Payment')
    is_new_order = fields.Boolean()
