from odoo import api, fields, models, _
from ast import literal_eval
import ast


# class ExtResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     employee_ids_document = fields.Many2many('hr.employee', related='company_id.employee_ids_document',string='Employee' , readonly=False)
#     days_document = fields.Char(string="Before End Of Expiry Date", related='company_id.days_document', readonly=False)
#     interval_type_document = fields.Selection([('days', 'Day(s)'),
#                                                      ('weeks', 'Weeks(s)'),
#                                                      ('months', 'Months(s)'),
#                                                      ('months_last_day', 'Month(s) Last Day(s)'),
#                                                      ('year', 'Year(s)'), ], string='Interval Unit',
#                                                     related='company_id.interval_type_document', readonly=False)
#
#
# class CompanyExt(models.Model):
#     _inherit = "res.company"
#
#     employee_ids_document = fields.Many2many('hr.employee', "employee_document_company", "employee_id","company_id", string='Employee')
#     days_document = fields.Char(string="Before End Of Expiry Date")
#     interval_type_document = fields.Selection([('days', 'Day(s)'),
#                                                      ('weeks', 'Weeks(s)'),
#                                                      ('months', 'Months(s)'),
#                                                      ('months_last_day', 'Month(s) Last Day(s)'),
#                                                      ('year', 'Year(s)'), ], string='Interval Unit', default='days')
