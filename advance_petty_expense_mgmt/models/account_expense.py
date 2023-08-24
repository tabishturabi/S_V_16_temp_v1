# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta



class MailActivity(models.Model):
    _inherit = 'mail.activity'
    
    
    def action_close_dialog(self):
        if self.env.context.get('reset_to_auditor'):
            self.env['expense.accounting.petty'].reset_to_auditor(self.res_id)
        elif self.env.context.get('reset_to_requester'): 
            self.env['expense.accounting.petty'].reset_to_requester(self.res_id)
        return super(MailActivity, self).action_close_dialog()    

class ExpenseAccounting(models.Model):
    _name = "expense.accounting.petty"
    _description = "Expenses Accounting"
    _inherit = ['mail.thread','mail.activity.mixin','portal.mixin']

    #for passing default value based on hide column as need ...!
    @api.model
    def default_get(self, fields):
        result = super(ExpenseAccounting, self).default_get(fields)
        is_with_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('advance_petty_expense_mgmt.is_with_product')
        is_without_product = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('advance_petty_expense_mgmt.is_without_product')
        if is_with_product:
            result['is_with_product'] = True
            # result['is_without_product'] = False
        if is_without_product:
            # result['is_with_product'] = False
            result['is_without_product'] = True

        return result

    # @api.model
    # def _default_balance(self):
    #     return self.env.user.partner_id.balance_payment
    

    @api.model
    def _get_default_request_partner(self):
        return self.env.user.partner_id.id

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id
  
    # @api.model
    # def _get_default_journal(self):
    #     search_cash_user_rule_id = self.env['petty_cash_user_rules'].search([('user_id','=',self.env.user.id)],limit=1)
    #     if search_cash_user_rule_id:
    #         return search_cash_user_rule_id.journal_id.id


    @api.depends('expense_treeview.amount')
    def _get_net_balance(self):
        for rec in self:
            rec.balnce_of_requester = 0
            if rec.expense_treeview:
                total_expense_amount =  sum([data.total_amount if data.total_amount else 0 for data in rec.expense_treeview])
                rec.balnce_of_requester = rec.opening_balacne - total_expense_amount
        # else:
        #     self.balnce_of_requester = self.opening_balacne

    #for getting lenght of move line
    
    def _get_move_length(self):
        self.len_move_id = len(self.move_ids)

    petty_cash_user_rule_id = fields.Many2one('petty_cash_user_rules',string="Petty Cash User Rule",track_visibility='always')
    petty_cash_journal_id = fields.Many2one(related="petty_cash_user_rule_id.journal_id")
    template_id = fields.Many2one('expense.accounting.template',string='Petty Cash Template',track_visibility='always')
    # employee_id = fields.Many2one('hr.employee',string="Employee ID")
    user_id = fields.Many2one('res.users',string="Requested User", default=lambda self: self.env.user,track_visibility='always')
    requested_partner_id = fields.Many2one('res.partner',string="Requested Partner", default=_get_default_request_partner)    
    opening_balacne = fields.Float(string="Opening Balance", copy=False,track_visibility='always')#default=_default_balance, 
    # department_id = fields.Many2one('hr.department',string="Department")
    balnce_of_requester = fields.Float(string="Net Balance",compute="_get_net_balance")#related="requested_partner_id.balance_payment",
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today,track_visibility='always')
    journal_id = fields.Many2one('account.journal', copy=False)#, default=_get_default_journal
    name = fields.Char(string="Sequence", required=False, default='/')
    expense_treeview = fields.One2many('expense.accounting.petty.tree', 'expense_accounting_id',track_visibility='always')
    total = fields.Float(string="Total Expense",  required=False,  compute='_compute_amount',track_visibility='always')
    state = fields.Selection(string="State", selection=[('draft', 'Draft'),('auditing', 'Auditing'),('open', 'Open'), ('done', 'Done'), ], default='draft', track_visibility='always')
    analytical_id = fields.Many2one('account.analytic.account', string="Analytic Accounts",track_visibility='always')    
    move_ids = fields.One2many('account.move', 'expense_id', readonly=True, copy=False,
                               ondelete='restrict',track_visibility='always')
    len_move_id = fields.Integer(string="Move ID Length",compute="_get_move_length",track_visibility='always')
    tax_amount = fields.Float(string="Total Vat",compute='_compute_amount',track_visibility='always')
    total_without_vat = fields.Float(string="Total Without Vat",compute='_compute_amount',track_visibility='always')
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_currency, track_visibility='always')
    petty_user_id = fields.Many2one('res.users',string="Confirm Request User")
    is_with_product = fields.Boolean(string="With Product", default=False)
    is_without_product = fields.Boolean(string="Without Product", default=False)
    account_id = fields.Many2one('account.account', string="Account",track_visibility='always')
    sequence = fields.Integer(help="need to use on journal reating purpose",default=1)
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Documents",track_visibility='always')
    in_auditor = fields.Boolean('In Auditor',default=False)

    def _compute_attached_docs_count(self):
        for petty in self:
            petty.doc_count = self.env['ir.attachment'].search_count([
            '|',
            '&',
            ('res_model', '=', 'expense.accounting.petty'),
            ('res_id', '=', petty.id),
            '&',
            ('res_model', '=', 'expense.accounting.petty.tree'),
            ('res_id', 'in', petty.expense_treeview.ids)
        ])

    
    def attachment_tree_view(self):
        res = self.env['ir.actions.act_window']._for_xml_id('advance_petty_expense_mgmt.action_attachment')
        return res

    
    def _set_attachment(self,attachment_ids):
        if len(attachment_ids)>0:
            for line in self.expense_treeview:
                attach_list = []
                for attach in attachment_ids:
                    new_attach = self.env['ir.attachment'].browse(attach).copy()
                    #line.attachment_id = new_attach.id
                    new_attach.write({'res_model':'expense.accounting.petty.tree','res_id':line.id}) 
                    attach_list.append(new_attach.id)
                line.attachment_id = attach_list
                                 
    @api.onchange('template_id')
    def onchange_template_id(self):
        final_list = []
        if self.template_id and not self.petty_cash_user_rule_id:
            raise UserError(_("Please Choose Petty Cash User Rule First"))
        if self.template_id and self.petty_cash_user_rule_id:
            for line in self.template_id.template_line_ids:
                final_list.append((0, 0,
                            {
                            'description': line.name,
                            'amount': line.amount,'product_id':line.product_id.id,
                            'account_id':line.account_id.id,
                            'is_petty_vendor_id':line.partner_id.id,
                            'petty_cash_user_rules_id':self.petty_cash_user_rule_id.id,
                            'is_with_product' : self.is_with_product,
                            'is_without_product':self.is_without_product,
                            'tax_ids':line.tax_ids.ids,
                            'analytical_id':self.template_id.analytic_account_id.id,
                            'analytic_tag_ids':self.template_id.analytic_tag_ids.ids,
                            'department_id':self.template_id.department_id.id,
                            'branches_id':self.template_id.branch_id.id}))
        if final_list: 
            #self.expense_treeview = False       
            self.expense_treeview = final_list

    #for onchange to pass user journal to expense cash journal and getting default value of balance from journal
    @api.onchange('petty_cash_user_rule_id')
    def _onchange_petty_cash_user_rule_id(self):
        if not self.petty_cash_user_rule_id.journal_id.default_account_id and not self.petty_cash_user_rule_id.journal_id.default_account_id and self.petty_cash_user_rule_id.account_id:
            self.account_id = self.petty_cash_user_rule_id.account_id.id
 
        if self.petty_cash_user_rule_id:
            self.journal_id = self.petty_cash_user_rule_id.journal_id.id
            # if self.petty_cash_user_rule_id.journal_id.default_account_id:
            if self.petty_cash_user_rule_id.journal_id.default_account_id:
                # self.opening_balacne = self.journal_id.default_account_id.balance
                # self.account_id = self.petty_cash_user_rule_id.journal_id.default_account_id.id
                self.account_id = self.petty_cash_user_rule_id.journal_id.default_account_id.id

    #getting default balance from account if not select any journal
    @api.onchange('account_id')
    def _onchange_account_id(self):
        if self.account_id:
            # self.opening_balacne = self.account_id.balance
            balance = 0.0  
            if self.petty_cash_user_rule_id.account_id:          
                for aml in self.env['account.move.line'].search([('account_id','=',self.account_id.id),('move_id.state','=','posted'),('partner_id','=',self.petty_cash_user_rule_id.partner_id.id)]):
                    balance += aml.debit - aml.credit
            else:
                for aml in self.env['account.move.line'].search([('account_id','=',self.account_id.id),('move_id.state','=','posted')]):
                    balance += aml.debit - aml.credit                
            self.opening_balacne = balance

    #for calculating total amount
    
    @api.depends('expense_treeview.amount')
    def _compute_amount(self):
        for rec in self:
            rec.total_without_vat = (sum(x.total_amount for x in rec.expense_treeview) - sum(x.line_tax_amount for x in rec.expense_treeview))
            rec.tax_amount = sum(x.line_tax_amount for x in rec.expense_treeview)
            rec.total = rec.total_without_vat + rec.tax_amount
            rec.line_tax_amount = rec.total_without_vat + rec.tax_amount

    # not need as per last updation of MR Nabeel
    #for constrints used
    @api.constrains('expense_treeview')
    def _check_attachment_id(self):
        if not self._context.get('without_attachment',False):
            for rec in self:
                for line in rec.expense_treeview:
                    if not line.attachment_id:
                        raise UserError(_("Attachment Must be required per each line."))

    # View Journal
    
    def button_journal_entries(self, context):
        move_id = self.env['account.move'].search([('expense_id', '=', self.id)])
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if len(move_id) > 1:
            action['domain'] = [('id', 'in', move_id.ids)]
        elif len(move_id) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = move_id.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    #for moving state draft to auditing
    
    def action_send(self):
        if self.balnce_of_requester < 0:
            raise Warning(_("You Are Not Allowed to Do More Expenses than Balance"))

        code = 'PC' + self.env.user.user_branch_id.branch_no
        seq = self.env['ir.sequence'].next_by_code(code)
        if not bool(seq):
            self.sudo().env['ir.sequence'].create({
                'name': code,
                'code': code,
                'prefix': 'PC' + self.env.user.user_branch_id.branch_no +  '%(y)s' + '%(month)s',
                'padding': 4,
            })
            self.name = self.env['ir.sequence'].next_by_code(code)
        else:
            self.name = seq
        self.in_auditor = True
        self.state = 'auditing'
        self.ensure_one()
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_res_model_id': self.env['ir.model'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('model', '=', 'expense.accounting.petty')], limit=1).id,
            'default_res_id': self.ids[0],
        })
        return {
                'name': _('Schedule an Activity'),
                'context': ctx,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.activity',
                'views': [(False, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
            }


    #for validate_all_lines
    
    def action_validate_all_lines(self):
        for data in self:
            if data.state in ['auditing','open']:
                if data.in_auditor != True:
                    raise Warning(_("You Can Not Validate Record, This Record In User"))
                data.validate()
                data.state = 'done'
                data.sequence += 1
            else:
                raise Warning(_("You can only validate Open or Auditing state record"))

    #for validate_all_lines
    
    def action_validate_post_lines(self):
        list_data = []
        for data in self:
            if data.state in ['auditing','open']:
                data.validate_open_record()
                data.sequence += 1
            else:
                raise Warning(_("You can only validate Open or Auditing state record"))

            for line_date in data.expense_treeview:
                list_data.append(line_date.is_post)
            if False in list_data:
                self.state = 'open'
            else:
                self.state = 'done'

    # press on validate button
    
    def validate_open_record(self):
        self.petty_user_id = self.env.user.id
        for data in self.expense_treeview:
            if not data.done and data.is_post:
                if not data.account_id:
                    raise Warning(_("Not Define account on Line Number"+" - " + str(data.sequence)))

        expense_lines =  self.expense_treeview.filtered(lambda s: not s.done and s.is_post)   
        if  expense_lines:  
            move_line = self._get_account_move_line_values(expense_lines)    
            move = self.env['account.move'].create(self._prepare_move_values())
            move.with_context(dont_create_taxes=True,from_petty=True).write({
                'line_ids': [(0, 0, line) for line in move_line]
            })
            
            expense_lines.write({'done':True})
            move.with_context(from_petty=True).action_post()
        else:
            raise Warning(_("You can not create move line without post line record"))

    
    def _prepare_move_values(self):
        """
        This function prepares move values related to an expense
        """
        self.ensure_one()
        move_values = {
            'journal_id': self.journal_id.id,
            'company_id': self.env.user.company_id.id,
            'date': self.date,
            'ref' : self.name,
            'is_petty_expense' : True,
            'expense_id': self.id,
        }
        return move_values

    # press on validate button
    
    def validate(self):
        self.petty_user_id = self.env.user.id
        for data in self.expense_treeview:
            if data.review and not data.is_post:
               raise Warning(_("Sorry ,Please You Must Post All Lines Has Review, Check This Line %s")%(data.description)) 
            if not data.done:
                if not data.account_id:
                    raise Warning(_("Not Define account on Line Number"+" - " + str(data.sequence)))
                
        expense_lines =  self.expense_treeview.filtered(lambda s: not s.done)   
        if  expense_lines:  
            move_line = self._get_account_move_line_values(expense_lines)    
            move = self.env['account.move'].create(self._prepare_move_values())
            move.with_context(dont_create_taxes=True,from_petty=True).write({
                'line_ids': [(0, 0, line) for line in move_line]
            })
            
            expense_lines.write({'done':True})
            move.with_context(from_petty=True).action_post()
        else:
            raise Warning(_("You can not create move line without post line record"))    

    # override create method for sequnace
    @api.model
    def create(self, vals):
        if 'expense_treeview' not in vals and not self._context.get('without_attachment',False):
            raise Warning(_("Please at least add one line to save record"))
        res = super(ExpenseAccounting, self).create(vals)
        res.name = '*' + str(res.id)
        return res

    # override write method
    
    def write(self, line_values):
        res = super(ExpenseAccounting, self).write(line_values)
        if not self.expense_treeview and not self._context.get('without_attachment',False):
            raise Warning(_("Please at least add one line to save record"))
        self._reset_sequence()
        return res

    # for sequnce method
    
    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.expense_treeview:
                line.name = current_sequence
                current_sequence += 1

    
    def action_audit_resend(self):
        '''
        This function opens a window to assign Activity
        '''
        self.ensure_one()
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_res_model_id': self.env['ir.model'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('model', '=', 'expense.accounting.petty')], limit=1).id,
            'default_res_id': self.ids[0],
            'default_user_id': self.user_id.id,
            'reset_to_requester' : True,
        })
        return {
                'name': _('Schedule an Activity'),
                'context': ctx,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.activity',
                'views': [(False, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
                

    def reset_to_requester(self,id):
        if id:
            self.browse(id).write({'in_auditor':False})
    def reset_to_auditor(self,id):
        if id:
            self.browse(id).write({'in_auditor':True})    

    
    def action_user_resend(self):
        '''
        This function opens a window to compose an email
        '''
        self.ensure_one()
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_res_model_id': self.env['ir.model'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('model', '=', 'expense.accounting.petty')], limit=1).id,
            'default_res_id': self.ids[0],
            'reset_to_auditor' : True,
        })
        return {
                'name': _('Schedule an Activity'),
                'context': ctx,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.activity',
                'views': [(False, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
            }


    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('reset_to_audit'):
            self.write({'state': 'auditing'})
        elif self.env.context.get('reset_to_draft'): 
            self.write({'state':'draft'})   
        return super(ExpenseAccounting, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
    
    
    def petty_cash_get_form_view(self):
        if self.env.user.id == self.user_id.id:
            petty_action = self.env.ref('advance_petty_expense_mgmt.expense_account_form_view_action')
            action = petty_action.read()[0]
            action['views'] = [(self.env.ref('advance_petty_expense_mgmt.expenses_bcube_form_view').id, 'form')]

        elif self.env.user.id != self.user_id.id and self.env.user.has_group('advance_petty_expense_mgmt.petty_cash_internal_editor'): 
            petty_action = self.env.ref('advance_petty_expense_mgmt.expense_auditing_account_form_view_action')
            action = petty_action.read()[0]
            action['views'] = [(self.env.ref('advance_petty_expense_mgmt.expenses_bcube_form_auditing_view').id, 'form')]  
        else:
            petty_action = self.env.ref('advance_petty_expense_mgmt.expense_account_all_form_view_action')
            action = petty_action.read()[0]
            action['views'] = [(self.env.ref('advance_petty_expense_mgmt.expenses_all_bcube_form_view').id, 'form')]     
        action['view_mode'] = 'form'
        action['res_id'] = self.id
        return action




    
    def _get_account_move_line_values(self,lines):
        account_dst = self.account_id.id if self.account_id else self.journal_id.default_account_id.id
        account_date = self.date
        company_currency = self.env.user.company_id.currency_id
        different_currency = self.currency_id and self.currency_id != company_currency
        total_amount = 0.0
        total_amount_currency = 0.0
        move_line_values = []
        for expense in lines:
            move_line_name = expense.description
            account_src = expense.account_id
            currency = expense.currency_id or None
            quantity = 1
            product = expense.product_id or None
            if not expense.is_new_order:
                taxes = expense.tax_id.with_context(round=True).compute_all(expense.amount, currency, quantity, product)
            else:    
                taxes = expense.tax_ids.with_context(round=True).compute_all(expense.amount, currency, quantity, product)
            partner_id = expense.is_petty_vendor_id.id

            # source move line
            amount = taxes['total_excluded']
            amount_currency = False
            if different_currency:
                amount = expense.currency_id._convert(amount, company_currency, self.env.user.company_id, account_date)
                amount_currency = taxes['total_excluded']

            move_line_src = {
                'name': move_line_name,
                'quantity': 1,
                'debit': amount if amount > 0 else 0,
                'credit': -amount if amount < 0 else 0,
                'amount_currency': amount_currency if different_currency else 0.0,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                #'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytical_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_accouting_petty_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'currency_id': expense.currency_id.id if different_currency else False,
                'bsg_branches_id' : expense.branches_id.id,
                'department_id' : expense.department_id.id,
                'fleet_vehicle_id' : expense.fleet_vehicle_id.id,
                'expense_accouting_petty_id' : expense.id,
            }
            move_line_values.append(move_line_src)
            total_amount += -move_line_src['debit'] or move_line_src['credit']
            total_amount_currency += -move_line_src['amount_currency'] if move_line_src['currency_id'] else (-move_line_src['debit'] or move_line_src['credit'])

            # taxes move lines
            for tax in taxes['taxes']:
                amount = tax['amount']
                amount_currency = False
                if different_currency:
                    amount = expense.currency_id._convert(amount, company_currency, self.env.user.company_id, account_date)
                    amount_currency = tax['amount']
                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': amount if amount > 0 else 0,
                    'credit': -amount if amount < 0 else 0,
                    'amount_currency': amount_currency if different_currency else 0.0,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_line_id': tax['id'],
                    'expense_accouting_petty_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id if different_currency else False,
                    'analytic_account_id': expense.analytical_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= amount
                total_amount_currency -= move_line_tax_values['amount_currency'] or amount
                move_line_values.append(move_line_tax_values)

        credit_name = " , ".join((data.description for data in lines))
        # destination move line
        move_line_dst = {
            'name': credit_name,
            'debit': total_amount > 0 and total_amount,
            'credit': total_amount < 0 and -total_amount,
            'account_id': account_dst,
            'date_maturity': account_date,
            'amount_currency': total_amount_currency if different_currency else 0.0,
            'currency_id': self.currency_id.id if different_currency else False,
            'partner_id': self.sudo().petty_cash_user_rule_id.partner_id.id,
        }
        move_line_values.append(move_line_dst)
        return move_line_values


class ExpenseAccountingTree(models.Model):
    _name = "expense.accounting.petty.tree"
    _description = "Expenses Accounting Line"
                
    #for don't allow user to cahnged it :)
    
    def _get_user_access(self):
        if self.env.user.has_group('advance_petty_expense_mgmt.petty_cash_manager') or self.env.user.has_group('advance_petty_expense_mgmt.petty_accounting_manager') or self.env.user.has_group('advance_petty_expense_mgmt.petty_cash_internal_editor'):
            self.is_allow_to_change_review = True
        else:
            self.is_allow_to_change_review = False
        if self.expense_accounting_id.in_auditor == False and  self.env.user.has_group('advance_petty_expense_mgmt.petty_cash_user') and self.is_post != True:
            self.allow_to_change = True    
        elif (self.expense_accounting_id.state == 'auditing' and self.expense_accounting_id.in_auditor == False and  self.env.user.has_group('advance_petty_expense_mgmt.petty_cash_internal_editor')) or self.is_post == True:
            self.allow_to_change = False  
        else:self.allow_to_change = True                  

    #for passing default value based on hide column as need ...!
    @api.model
    def default_get(self, fields):
        result = super(ExpenseAccountingTree, self).default_get(fields)
        petty_cash_user_rule_id = self.env.context.get('petty_cash_user_rule_id') 
        result['is_new_order'] = True   
        if petty_cash_user_rule_id:
            result['petty_cash_user_rules_id'] = petty_cash_user_rule_id
        return result

    
    @api.depends('amount','tax_id','tax_ids')
    def _compute_amount(self):
        for rec in self:
            rec.line_tax_amount = 0.0
            rec.total_amount = 0.0
            rec.total_exclude_amount = 0.0
            if rec.amount:
                currency = rec.currency_id or None
                quantity = 1
                product = rec.product_id or None
                if not rec.is_new_order:
                    taxes = rec.tax_id.compute_all((rec.amount), currency, quantity,
                                                        product, partner=rec.expense_accounting_id.requested_partner_id)
                else:
                    taxes = rec.tax_ids.compute_all((rec.amount), currency, quantity,
                                                        product, partner=rec.expense_accounting_id.requested_partner_id)
                rec.line_tax_amount  = (taxes['total_included']-taxes['total_excluded'])
                rec.total_amount = taxes['total_included']
                rec.total_exclude_amount = taxes['total_excluded']

    # @api.model
    # def _get_default_user_rules(self):
    #     parent = self.expense_accounting_id
    #     return self.expense_accounting_id.petty_cash_user_rule_id.id

    description = fields.Char(string="Label")
    amount = fields.Float(string="Amount")
    product_id = fields.Many2one('product.product',string="Product",domain=[('is_expense_product','=',True)])
    account_id = fields.Many2one('account.account', string="Account")
    expense_accounting_id = fields.Many2one('expense.accounting.petty')

    is_with_product = fields.Boolean(string="With Product")
    is_without_product = fields.Boolean(string="Without Product")

    date = fields.Date(string="Date", default=fields.Date.context_today)
    done = fields.Boolean()
    tax_id = fields.Many2one('account.tax',string="Taxes")
    vat_no = fields.Char(string="Vat No",related="is_petty_vendor_id.vat", store=True)
    invoice_ref_no = fields.Char(string="Ref")
    line_tax_amount = fields.Float(string="Amount Tax",compute='_compute_amount')
    name = fields.Char(string="SEQ")
    attachment_id = fields.Many2many('ir.attachment',string='Attachments',required=True)
    is_petty_vendor_id = fields.Many2one('res.partner','Partner')#,
    branches_id = fields.Many2one('bsg_branches.bsg_branches', string="Branch")
    department_id = fields.Many2one('hr.department',string="Department")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle',string="Truck")
    analytical_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    analytic_tag_ids = fields.Many2many('account.account.tag', string="Analytic Tags")
    review = fields.Text(string="Note")
    is_post = fields.Boolean(string="Post")
    total_amount = fields.Float(string="Total",compute='_compute_amount')
    total_exclude_amount = fields.Float(string="Total Without Tax",compute='_compute_amount')
    currency_id = fields.Many2one('res.currency', string='Currency', related="expense_accounting_id.currency_id")

    petty_cash_user_rules_id = fields.Many2one('petty_cash_user_rules',string="Petty cash User rules")
    user_product_ids = fields.Many2many('product.product', string="Products", related="petty_cash_user_rules_id.product_ids")
    user_account_ids = fields.Many2many('account.account', string="Accounts", related="petty_cash_user_rules_id.account_ids")
    user_analytic_account_ids = fields.Many2many('account.analytic.account', string="Analytic Accounts", related="petty_cash_user_rules_id.analytic_account_ids")   
    user_analytic_tag_ids = fields.Many2many('account.account.tag', string="Analytic Tags", related="petty_cash_user_rules_id.analytic_tag_ids")
    user_department_ids = fields.Many2many('hr.department', string="User Department", related="petty_cash_user_rules_id.department_ids")
    user_branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="User Branche", related="petty_cash_user_rules_id.branch_ids")
    cash_vendor_ids = fields.Many2many('res.partner', string="Cash Vendor", related="petty_cash_user_rules_id.cash_vendor_ids")
    partner_type_ids = fields.Many2many('partner.type', string="Partner Types", related="petty_cash_user_rules_id.partner_type_ids")
    is_allow_to_change_review = fields.Boolean(string="Allow to change Review",compute="_get_user_access")
    allow_to_change = fields.Boolean(string="Allow to Change",compute="_get_user_access",default=True)
    is_attach_added = fields.Selection([('yes','Yes')],'Please Add Attachment',default='yes')
    is_new_order = fields.Boolean('Is New Order')
    tax_ids = fields.Many2many('account.tax', 'petty_cash_expense_tax', 'petty_expense_id', 'tax_id', string='Taxes')
    tax_len =fields.Integer('Taxes',compute='_compute_tax_len',store=True)

    @api.onchange('attachment_id')
    def _onchange_attachment_id(self):
        for rec in self:
            if rec.attachment_id:
                rec.is_attach_added = 'yes'
            elif rec.is_attach_added == 'yes':
                 rec.is_attach_added = ''  
                  
    @api.depends('tax_ids','tax_id')
    def _compute_tax_len(self):
        for rec in self:
            rec.tax_len = len(rec.tax_ids) + len(rec.tax_id) 


    @api.onchange('tax_id')
    def _onchange_tax_id(self):
        if self.tax_id:
            self.tax_ids = self.tax_id
    # onchange to pass vat from vendor
    @api.onchange('is_petty_vendor_id')
    def _onchange_vendor_id(self):
        # if self.is_petty_vendor_id:
        #     self.vat_no = self.is_petty_vendor_id.vat
        pettyconfig = self.env.ref('advance_petty_expense_mgmt.res_petty_cash_config_data', False)
        vendor_list = []
        config_vendor_list = []
        if self.is_petty_vendor_id:
            if self.is_petty_vendor_id not in self.expense_accounting_id.petty_cash_user_rule_id.cash_vendor_ids:
                self.expense_accounting_id.petty_cash_user_rule_id.write({'cash_vendor_ids' : [(4, self.is_petty_vendor_id.id)]})
        if self.is_petty_vendor_id:
            if self.is_petty_vendor_id not in pettyconfig.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).cash_vendor_ids:
               pettyconfig.write({'cash_vendor_ids' : [(4, self.is_petty_vendor_id.id)]})
  
    #for constrint user
    
    @api.constrains('vat_no')
    def check_vat_no(self):
        if self.vat_no:
            search_id = self.search([('vat_no','=',self.vat_no),('is_petty_vendor_id','!=',self.is_petty_vendor_id.id),('expense_accounting_id','=',self.expense_accounting_id.id)])
            if len(search_id) >= 1:
                raise Warning(_("Vat No Should be Unique...!"))

    #for constrint user
    
    @api.constrains('date')
    def check_date(self):
        if self.date:
            expense_date = datetime.strptime(str(self.expense_accounting_id.date), DEFAULT_SERVER_DATE_FORMAT)
            expense_month = expense_date.month
            line_date = datetime.strptime(str(self.date), DEFAULT_SERVER_DATE_FORMAT)
            line_month = line_date.month
            if expense_month != line_month:
                raise Warning(_("You Are Not Allowed to Enter Expense line with different month..!"))

    #for constrint user
    
    @api.constrains('amount')
    def check_amount(self):
        if not self._context.get('without_attachment',False):
            if self.amount:
                if self.expense_accounting_id.balnce_of_requester < 0:
                    raise Warning(_("You Are Not Allowed to Do More Expenses than Balance"))

    # # onchange for validation not allow to enter more amount
    # @api.onchange('amount')
    # def _onchange_amont(self):
    #     if self.amount:
    #         if self.amount > self.expense_accounting_id.balnce_of_requester:
    #             raise Warning(_("You Are Not Allowed to Do More Expenses than Balance"))

    # onchange for passing account from product id 
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.account_id = self.product_id.property_account_expense_id.id
            return {'domain': {'account_id': [('id', '=', self.product_id.property_account_expense_id.id)]}}
        else:    
            return {'domain': {'account_id': [('id','in',self.user_account_ids.ids)]}}

    # override to create method
    @api.model
    def create(self, vals):
        res = super(ExpenseAccountingTree, self).create(vals)
        res.expense_accounting_id._reset_sequence()
        if res.attachment_id:
            res.attachment_id.write({'res_id':self.id})
        return res

    # override write method
    
    def write(self, values):
        res = super(ExpenseAccountingTree, self).write(values)
        for rec in self:
            if rec.attachment_id:
                rec.attachment_id.write({'res_id':rec.id})
        return res


    @api.constrains('attachment_id')
    def _check_attachment_id(self):
        if not self._context.get('without_attachment',False):
            for rec in self:
                if not rec.attachment_id:
                        raise UserError(_("Please Add Attachment."))  

    # override to unlink to allow or not do delete item if posted
    
    def unlink(self):
        """
            Delete all record(s) from table heaving record id in ids
            return True on success, False otherwise

            @return: True on success, False otherwise
        """
        for rec in self:
            if rec.is_post or rec.done:
                raise UserError(_('You can delete record If move line Created or it has Posted'))
        return super(ExpenseAccountingTree, self).unlink()


class ExpenseAccountingTemplate(models.Model):
    _name = "expense.accounting.template"
    _description = "Expenses Accounting Template"
    _inherit = ['mail.thread','mail.activity.mixin','portal.mixin']

    #for getting value from configuration and apply domain
    @api.model
    def default_get(self, fields):
        result = super(ExpenseAccountingTemplate, self).default_get(fields)
        pettyconfig = self.env.ref('advance_petty_expense_mgmt.res_petty_cash_config_data', False)
        result['res_petty_cash_config_id'] = pettyconfig.id
        return result

    name = fields.Char(required=True,track_visibility='always')
    template_line_ids = fields.One2many('expense.accounting.template.line','template_id',track_visibility='always')
    analytic_tag_ids = fields.Many2many('account.account.tag', string="Analytic Tag's",track_visibility='always')
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account",track_visibility='always')
    department_id = fields.Many2one('hr.department', string="Department",track_visibility='always')
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string="Branche",track_visibility='always')
    res_petty_cash_config_id = fields.Many2one('res_petty_cash_config',string="Petty Cash Config")
    

    #need to take related filed for domain use
    res_petty_product_ids = fields.Many2many('product.product','product_template_petty_conf','template_id','product_id',string="Product's", related="res_petty_cash_config_id.product_ids")
    res_petty_account_ids = fields.Many2many('account.account','account_template_petty_conf','template_id','account_id',string="Account's", related="res_petty_cash_config_id.account_ids")
    res_petty_analytic_tag_ids = fields.Many2many('account.account.tag','account_tags_template_petty_conf','template_id','tag_id',string="tag's", related="res_petty_cash_config_id.analytic_tag_ids")
    res_petty_analytic_account_ids = fields.Many2many('account.analytic.account','account_analytic_template_petty_conf','template_id','analytic_id',string="analytic's", related="res_petty_cash_config_id.analytic_account_ids")
    res_petty_department_ids = fields.Many2many('hr.department','department_template_petty_conf','template_id','department_id',string="Departments", related="res_petty_cash_config_id.department_ids")
    res_petty_branch_ids = fields.Many2many('bsg_branches.bsg_branches','branch_template_petty_conf','template_id','branch_id',string="Branche's", related="res_petty_cash_config_id.branch_ids")


class ExpenseAccountingTemplateLine(models.Model):
    _name = "expense.accounting.template.line"
    _description = "Expenses Accounting Template Line"



    name = fields.Char(string="Label")
    template_id = fields.Many2one('expense.accounting.template')
    amount = fields.Float(string="Amount")
    product_id = fields.Many2one('product.product',string="Product")
    account_id = fields.Many2one('account.account', string="Account")
    tax_ids = fields.Many2many('account.tax',string="Taxes",domain=[('type_tax_use','=','purchase')])
    partner_id = fields.Many2one('res.partner','Partner')



    # onchange for passing account from product id 
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.account_id = self.product_id.property_account_expense_id.id
            self.name = self.product_id.description_purchase
            self.tax_ids = self.product_id.supplier_taxes_id.ids
            self.amount = self.product_id.standard_price
            return {'domain': {'account_id': [('id', '=', self.product_id.property_account_expense_id.id)]}}
        else:    
            return {'domain': {'account_id': [('id','in',self.template_id.res_petty_account_ids.ids)]}}

