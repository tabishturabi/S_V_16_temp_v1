# -*- coding: utf-8 -*- 
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

#for managing PettyCash
class PettyCashUserRules(models.Model):
    _name = "petty_cash_user_rules"
    _description = "Petty Cash User Rules"
    _inherit = ['mail.thread','mail.activity.mixin']

    # #for constrains method
    # 
    # @api.constrains('user_id')
    # def _check_user_id(self):
    #     search_id = self.env['petty_cash_user_rules'].search([('user_id','=',self.user_id.id),('id','!=',self.id)])
    #     if search_id:
    #         raise UserError(
    #             _('You can configuration User rules one time only..!'),
    #         )

    #for getting value from configuration and apply domain
    @api.model
    def default_get(self, fields):
        result = super(PettyCashUserRules, self).default_get(fields)
        pettyconfig = self.env.ref('advance_petty_expense_mgmt.res_petty_cash_config_data', False)
        result['res_petty_cash_config_id'] = pettyconfig.id
        return result

    @api.model
    def _default_partner(self):
        return self.env.user.partner_id.id

    name = fields.Char(string="Name",track_visibility=True)
    active = fields.Boolean(string="Active", track_visibility=True, default=True)
    user_id = fields.Many2one(string="User", comodel_name="res.users", default=lambda self: self.env.user,track_visibility=True)  
    journal_id = fields.Many2one(string="Journal", comodel_name="account.journal",track_visibility=True)
    account_id = fields.Many2one(comodel_name='account.account', string="Account",track_visibility=True)
    partner_id = fields.Many2one('res.partner', string="Partner", default=_default_partner)
    res_petty_cash_config_id = fields.Many2one('res_petty_cash_config',string="Petty Cash Config ID")

    #need to take related filed for domain use
    res_petty_product_ids = fields.Many2many('product.product','res_petty_conf','product_id','petty_id',string="Product's", related="res_petty_cash_config_id.product_ids")
    res_petty_account_ids = fields.Many2many('account.account','account_res_petty_conf','account_id','petty_id',string="Account's", related="res_petty_cash_config_id.account_ids")
    res_petty_analytic_account_ids = fields.Many2many('account.analytic.account','analytic_res_petty_conf','analytic_id','petty_id',string="Analytic Account's", related="res_petty_cash_config_id.analytic_account_ids")   
    res_petty_analytic_tag_ids = fields.Many2many('account.account.tag','analytic_tag_petty_conf','analytic_tagres_petty_id','petty_id',string="Analytic Tag's", related="res_petty_cash_config_id.analytic_tag_ids")
    res_petty_department_ids = fields.Many2many('hr.department','department_res_petty_conf','department_id','petty_id',string="Department's", related="res_petty_cash_config_id.department_ids")
    res_petty_branch_ids = fields.Many2many('bsg_branches.bsg_branches','branch_res_petty__conf','branch_id','petty_id',string="Branche's", related="res_petty_cash_config_id.branch_ids")
    # config_cash_vendor_id = fields.Many2one('res.partner', string="Cash Vendors",domain=[("is_petty_vendor",'=',True)])
    # config_partner_type_id = fields.Many2one('partner.type', string="Partner Types")
    res_cash_vendor_ids = fields.Many2many('res.partner', string="Cash Vendors",domain=[("is_petty_vendor",'=',True)], related="res_petty_cash_config_id.cash_vendor_ids")
    res_partner_type_ids = fields.Many2many('partner.type', string="Partner Types", related="res_petty_cash_config_id.partner_type_ids")

    product_ids = fields.Many2many('product.product', string="Products")
    account_ids = fields.Many2many('account.account', string="Accounts")
    analytic_account_ids = fields.Many2many('account.analytic.account', string="Analytic Accounts")   
    analytic_tag_ids = fields.Many2many('account.account.tag', string="Analytic Tags")
    department_ids = fields.Many2many('hr.department', string="Departments")
    branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branches")
    cash_vendor_ids = fields.Many2many('res.partner', string="Cash Vendors",domain=[("is_petty_vendor",'=',True)])
    partner_type_ids = fields.Many2many('partner.type', string="Partner Types")
