# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from calendar import monthrange

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'



    
    def set_loan_to_done(self):
        for rec in self:
            rec.loan_paymet_ids.write({'state': 'paid', 'payslip_id': rec.id})

    
    def set_loan_to_draft(self):
        for rec in self:
            rec.loan_paymet_ids.write({'state': 'draft'})   

    
    def action_payslip_done(self):
        res = super(hr_payslip, self).action_payslip_done()
        self.set_loan_to_done()
        return res

    
    def refund_sheet(self):
        for payslip in self:
            if payslip.type == 'holiday':
                copied_payslip = payslip.with_context({'default_type':'holiday'}).copy({'credit_note': True, 'name': _('Refund: ') + payslip.name})
            else:
                copied_payslip = payslip.copy({'credit_note': True, 'name': _('Refund: ') + payslip.name})
            copied_payslip.action_payslip_done()
            copied_payslip.state = 'cancel'
            loans_emis = self.env['loan.payment'].search([('employee_id', '=', payslip.employee_id.id),
                                                      ('due_date', '>=', payslip.date_from),
                                                      ('due_date', '<=', payslip.date_to),
                                                      ('payslip_id', '=', payslip.id),
                                                      ('state', '=', 'paid'),
                                                      ('loan_app_id.state', '=', 'paid')])
        for loan in loans_emis:
             loan.write({'state': 'draft',
                         'payslip_id': False})
        self.state = 'cancel'
        formview_ref = self.env.ref('hr_payroll.view_hr_payslip_form', False)
        treeview_ref = self.env.ref('hr_payroll.view_hr_payslip_tree', False)
        return {
            'name': ("Refund Payslip"),
            'view_mode': 'tree, form',
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % copied_payslip.ids,
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'), (formview_ref and formview_ref.id or False, 'form')],
            'context': {}
        }

    
    def compute_sheet(self):
        # for rec in self:
        #     rec._compute_loan()
        return super(hr_payslip, self).compute_sheet()

    def _compute_loan(self):
        for rec in self:
            loans_emis = self.env['loan.payment'].search([('employee_id', '=', rec.employee_id.id),
                                                        ('due_date', '>=', rec.date_from),
                                                        ('due_date', '<=', rec.date_to),
                                                        ('state', '=', 'draft'),
                                                        ('loan_app_id.state', '=', 'paid')])
            rec.loan_paymet_ids = loans_emis


    loan_paymet_ids = fields.One2many('loan.payment', 'payslip_id',
                                      string='Loan EMI')


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'


    
    def close_payslip_run(self):
        res = super(HrPayslipRun, self).close_payslip_run()
        for run in self:
            run.slip_ids.set_loan_to_done() 
        return res      
        
