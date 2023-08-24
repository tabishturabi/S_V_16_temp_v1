# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class ResCompany(models.Model):
    _inherit = "res.company"

    overtime_sallary_rule_id = fields.Many2one('hr.salary.rule',string='Overtime Sallary Rule')
    overtime_debit_account_id = fields.Many2one('account.account',string='Overtime Debit Account')
    overtime_credit_account_id = fields.Many2one('account.account', string='Overtime Credit Account')
    overtime_analytic_account_id = fields.Many2one('account.analytic.account', string='Overtime Analytic Account')
    overtime_tax_id = fields.Many2one('account.tax')
    overtime_journal_id = fields.Many2one('account.journal',string='Overtime Journal')
    overtime_payment_method_id = fields.Many2one('account.journal',string='Overtime Payment Journal')
    overtime_compute_salary_rule_id = fields.Many2one('hr.salary.rule',string='Overtime Compute Rule')    

class OvertimeResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    incomming_emails = fields.Boolean(string='Overtime Incomming Emails')
    default_payslip_reimburse = fields.Boolean(string='Reimburse in Payslip',default=False,default_model='hr.overtime')
    default_generate_from_attendance = fields.Boolean(string='Pull Data From Attendance App',default=False,default_model='hr.overtime')
    default_allow_overtime_per_employee = fields.Boolean(string='Allow To Enter Total Overtime Per Employee',default=False,default_model='hr.overtime')
    default_multi_payslip_reimburse = fields.Boolean(string='Reimburse in Payslip For Multi Requests',default=False,default_model='hr.employee.overtime')
    default_total_hours_payslip_reimburse = fields.Boolean(string='Reimburse in Payslip For Total Hours Requests',default=False,default_model='hr.employee.overtime.by.hours')
    #company
    overtime_sallary_rule_id = fields.Many2one('hr.salary.rule',related='company_id.overtime_sallary_rule_id',readonly=False,string='Sallary Rule')
    overtime_debit_account_id = fields.Many2one('account.account',related='company_id.overtime_debit_account_id',readonly=False,string='Debit Account')
    overtime_credit_account_id = fields.Many2one('account.account',related='company_id.overtime_credit_account_id',readonly=False,string='Credit Account')
    overtime_analytic_account_id = fields.Many2one('account.analytic.account',related='company_id.overtime_analytic_account_id',readonly=False,string='Analytic Account')
    overtime_tax_id = fields.Many2one('account.tax',related='company_id.overtime_tax_id',readonly=False,string='Tax')
    overtime_journal_id = fields.Many2one('account.journal',related='company_id.overtime_journal_id',readonly=False,string='Overtime Journal')
    overtime_payment_method_id = fields.Many2one('account.journal',related='company_id.overtime_payment_method_id',string='Payment Journal',readonly=False)
    overtime_compute_salary_rule_id = fields.Many2one('hr.salary.rule',related='company_id.overtime_compute_salary_rule_id',readonly=False,string='Overtime Compute Rule')
    
    def set_values(self):
        res = super(OvertimeResConfigSettings,self).set_values()
        self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).set_param('bsg_hr_overtime.incomming_emails',self.incomming_emails)
        return res

    @api.model
    def get_values(self):
        res = super(OvertimeResConfigSettings, self).get_values()
        overtime_param = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id)
        mails = overtime_param.get_param('bsg_hr_overtime.incomming_emails')
        res.update({
            'incomming_emails' : mails,
        })
        return res
    @api.onchange('default_payslip_reimburse')
    def onchange_payslip_reimburse(self):
        self.default_multi_payslip_reimburse = self.default_payslip_reimburse 
        self.default_total_hours_payslip_reimburse = self.default_payslip_reimburse

