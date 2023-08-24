from odoo import models,fields,api,_
from datetime import datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter


class EmployeePayslipReportPdf(models.AbstractModel):
    _name = 'report.bsg_employee_payslip_report.employee_payslip_report_pdf'

    def get_user_lang(self):
        user = self.env['res.users'].search([('id', '=', self._uid)])
        lang = 1 if user.lang != 'en_US' else 0
        return lang

    def get_employee(self, docs):
        return docs.employee_id


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        employee_id = docs.employee_id
        print("=================================", self.get_employee(docs))
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'employee_data': employee_id,
            'employee': self.get_employee(docs),
            "period_from": "%s/%s" % (docs.from_month, str(docs.from_year.name)),
            "period_to": "%s/%s" % (docs.end_month, str(docs.end_year.name)),
            "to_date": data['ids'],
            "user_lang": self.get_user_lang(),
            'docs': docs
        }




























