from odoo import models, fields, api,_
from odoo.exceptions import UserError


class DecisionReportComments(models.Model):
    _name='decisions.report.comments'
    _description='Decision Report Comments'
    _rec_name='decision_reference'

    decision_reference = fields.Char(string='Employees Decisions Reference')
    decision_type = fields.Selection([('appoint_employee', 'Decision to appoint an employee'),
                                      ('transfer_employee', 'Decision to transfer an employee'),
                                      ('assign_employee', 'Decision to assign an employee')],
                                     string='Decision Type')
    decision_report_layout_1 = fields.Text(string='Decisions Report Layout')
    decision_report_layout_2 = fields.Text(string='Decisions Report Layout')
    decision_report_layout_3 = fields.Text(string='Decisions Report Layout')
    decision_report_layout_4 = fields.Text(string='Decisions Report Layout')
    decision_report_layout_5 = fields.Text(string='Decisions Report Layout')
    decision_report_layout_6 = fields.Text(string='Decisions Report Layout')
    decision_report_layout_7 = fields.Text(string='Decisions Report Layout')
    decision_report_layout_8 = fields.Text(string='Decisions Report Layout')
    decision_report_layout_9 = fields.Text(string='Decisions Report Layout')
    decision_report_layout_10 = fields.Text(string='Decisions Report Layout')

