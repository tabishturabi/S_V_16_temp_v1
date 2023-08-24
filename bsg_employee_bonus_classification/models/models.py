# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime
import time
from odoo.exceptions import UserError,ValidationError

class EmployeeBonusClassification(models.Model):
    _name = 'employee.bonus.classification'
    _inherit = 'mail.thread'
    _description = 'Employee Bonus Classification'

    name = fields.Char(string='Employee Bonus Classification',required=True,translate=True,track_visibility='always')
    activation_date = fields.Date(string='Activation Date',default=fields.date.today(),required=True,track_visibility='always')
    deactivation_date = fields.Date(string='Deactivation Date',track_visibility='always')
    internal_notes = fields.Char(string='Internal Notes',translate=True,track_visibility='always')
    branch_classification_line_id = fields.One2many('branch.classification.line','bonus_classification_id' ,string='Branch Classification Line')
    bonus_percentage = fields.Float(string='Bonus Percentage %')
    bonus_depending_on = fields.Selection([('branch', 'Branches'), ('company', 'Company')], string='Bonus Depending On',
                                          default='branch', required=True)
    active = fields.Boolean(string='Active',default=True)
    employee_ids = fields.Many2many('hr.employee',string='Employee')
    check = fields.Boolean(string='Check', compute='compute_check')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'This Employee Bonus Classification name already exists!')
    ]

    @api.depends('deactivation_date')
    def compute_check(self):
        for rec in self:
            rec.check =False
            if not rec.deactivation_date:
                rec.check=True

    @api.onchange('bonus_percentage')
    def _onchange_percentage(self):
        if self.bonus_percentage < 0.0 or self.bonus_percentage > 100:
            raise ValidationError(_('The percentage must be greater than 0 and less than 100.'))
    @api.constrains('deactivation_date')
    def _onchange_deactivation_date(self):
        if self.deactivation_date and self.deactivation_date < self.activation_date:
            raise ValidationError(_('Deactivation date must be greater than activation date.'))

    @api.onchange('branch_classification_line_id')
    def _onchange_branch(self):
        line_list=[]
        if len(self.branch_classification_line_id)>1:
            for rec in self.branch_classification_line_id:
                if rec.branch_classification_id.bsg_branch_cls_name not in line_list:
                    line_list.append(rec.branch_classification_id.bsg_branch_cls_name)
                else:
                    raise ValidationError(_('This Branch Classification already exists!'))

    def add_members(self):
        return {
            'name': 'Employees',
            'res_model': 'hr.employee',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }

class BranchClassificationLine(models.Model):
    _name = 'branch.classification.line'
    _description = 'Branch Classification Line'

    bonus_classification_id = fields.Many2one('employee.bonus.classification',string='Bonus Classification ID')
    branch_classification_id = fields.Many2one('bsg.branch.classification',string='Branch Classification')
    percentage = fields.Float(string='Percentage %')

    @api.onchange('percentage')
    def _onchange_percentage(self):
        print('percentage called')
        if self.percentage < 0.0 or self.percentage > 100:
            raise ValidationError(_('The percentage must be greater than 0 and less than 100.'))




class EmployeeInherit(models.Model):
    _inherit='hr.employee'

    # activation_current_date=fields.Date(string='Activation Current Date',compute='get_today', default=fields.date.today())
    bonus_classification_ids = fields.Many2many('employee.bonus.classification',string='Bonus Classification')


    # def get_today(self):
    #     for rec in self:
    #         rec.activation_current_date = fields.date.today()







class BranchClassificationInherit(models.Model):
    _inherit = 'bsg.branch.classification'

    bonus_percentage = fields.Float(string='Bonus Percentage %')
    agreements_rule_line = fields.One2many('agreements.rule.line','branch_cls_id',string='Agreement Rule Line')
    internal_notes = fields.Char(string='Internal Notes',translate=True)
    condition_rule = fields.Selection([('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
                                       ('is_after', 'is after'), ('is_before', 'is before'),
                                       ('is_after_or_equal_to', 'is after or equal to'),
                                       ('is_before_or_equal_to', 'is before or equal to'),
                                       ('is_between', 'is between')],
                                      required=True, string='Condition Rule', default='is_after_or_equal_to')
    con_rule_amt_1 = fields.Float(string='Amount 1')
    con_rule_amt_2 = fields.Float(string='Amount 2')
    sales_cls_ids = fields.Many2many('bsg_branches.bsg_branches','branches_classification_rel','branch_cls_id','branch_id',string='Sales Classification',compute="_get_sales_cls_branches",readonly=True)
    # sales_cls_ids = fields.Many2many('bsg_branches.bsg_branches', 'hr_branches_classification_rel', 'hr_branch_cls_id',
    #                                  'hr_branch_id', string='HR Classification', compute="_get_hr_cls_branches",
    #                                  readonly=True)

    # @api.multi
    def _get_sales_cls_branches(self):
        branch_ids = self.env['bsg_branches.bsg_branches'].search([('branch_classifcation','=',self.id)])
        if branch_ids:
            self.sales_cls_ids = [(6,0,branch_ids.ids)]


    _sql_constraints = [
        ('bsg_branch_cls_name_uniq', 'unique (bsg_branch_cls_name)', 'This Branch Classification name already exists!')
    ]


    @api.onchange('bonus_percentage')
    def _onchange_percentage(self):
        if self.bonus_percentage < 0.0 or self.bonus_percentage > 100:
            raise ValidationError(_('The percentage must be greater than 0 and less than 100.'))


    @api.onchange('con_rule_amt_1')
    def _onchange_amount_1(self):
        if self.con_rule_amt_1 < 0.0:
            raise ValidationError(_('The value must be greater than 0.'))


    @api.onchange('con_rule_amt_2')
    def _onchange_amount_2(self):
        if self.con_rule_amt_2 < 0.0:
            raise ValidationError(_('The value must be greater than 0.'))





class AgreementsRuleLine(models.Model):
    _name = 'agreements.rule.line'
    _description = 'Agreements Rule Line'

    branch_cls_id = fields.Many2one('bsg.branch.classification',string='Branch Classification ID')
    payment_method_ids = fields.Many2many('cargo_payment_method',string='Payment Method')
    shipment_type_ids = fields.Many2many('bsg.car.shipment.type',string='Shipment Type')
    service_type_ids = fields.Many2many('product.template',string='Service Type')
    amount_type = fields.Selection([('fixed','Fixed Amount'),('percentage','Percentage (%)')],string='Amount Type',required=True,default='fixed')
    value = fields.Float(string='Value')

    @api.onchange('value')
    def _onchange_value(self):
        if self.amount_type == 'fixed':
            if self.value < 0.0:
                raise ValidationError(_('The value must be greater than 0.'))
        if self.amount_type == 'percentage':
            if self.value < 0.0 or self.value > 100:
                raise ValidationError(_('The value must be greater than 0 and less than 100.'))

class CargoSaleLineInherit(models.Model):
    _inherit='bsg_vehicle_cargo_sale_line'


    bonus_state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid'),
                                       ('cancel', 'Cancelled')],string='Bonus State',readonly=True)
    bonus_agreement_amount = fields.Float(string='Bonus Agreement Amount',readonly=True)
    bonus_agreement_paid_amount = fields.Float(string='Bonus Agreement Paid Amount',readonly=True)
    release_car_no = fields.Char(string='Release Car No')
    release_car_date = fields.Datetime(string='Release Date')


    # @api.multi
    # def calculated_no_of_days(self):
    #     branch_cls_id = self.env['bsg.branch.classification'].search([('id','=',self.loc_from.loc_branch_id.id)],limit=1)
    #     if branch_cls_id:
    #         if branch_cls_id.agreements_rule_line:
    #             for agreement_id in branch_cls_id.agreements_rule_line:
    #                 if self.payment_method in agreement_id.payment_method_ids.ids and self.shipment_type in agreement_id.shipment_type_ids.ids and self.service_type in agreement_id.service_type_ids.ids :
    #                     self.bonus_agreement_amount = agreement_id.value
    #                     self.bonus_state='draft'
    #     res = super(CargoSaleLineInherit,self).calculated_no_of_days()
    #     return res

    # @api.multi
    def write(self, vals):
        if vals.get('state'):
            if vals.get('state') == 'done':
                self.bonus_state = 'draft'
                branch_cls_id = self.env['bsg.branch.classification'].search(
                    [('id', '=', self.loc_from.loc_branch_id.branch_classifcation.id)], limit=1)
                if branch_cls_id:
                    if branch_cls_id.agreements_rule_line:
                        for agreement_id in branch_cls_id.agreements_rule_line:
                            if self.payment_method.id in agreement_id.payment_method_ids.ids and self.shipment_type.id in agreement_id.shipment_type_ids.ids and self.service_type.id in agreement_id.service_type_ids.ids:
                                self.bonus_agreement_amount = agreement_id.value
        res = super(CargoSaleLineInherit, self).write(vals)
        return res

    # @api.multi
    def print_delivery_report(self):
        res = super(CargoSaleLineInherit, self).print_delivery_report()
        self.release_car_no = self.delivery_note_no
        self.release_car_date = self.release_date
        return res

    # @api.multi
    def print_delivery_report_done_sate(self):
        self.release_car_no = self.delivery_note_no
        self.release_car_date = self.release_date
        res = super(CargoSaleLineInherit, self).print_delivery_report_done_sate()
        return res

