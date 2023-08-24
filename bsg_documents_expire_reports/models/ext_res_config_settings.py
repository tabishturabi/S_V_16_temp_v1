from odoo import api, fields, models, _
from ast import literal_eval
import ast

# class ExtResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     employee_ids_iqama = fields.Many2many('hr.employee',
#                                           related='company_id.employee_ids_iqama',string='Employee' ,
#                                           readonly=False)
#     employee_ids_passport = fields.Many2many('hr.employee', related='company_id.employee_ids_passport',string='Employee' , readonly=False)
#     days_iqama = fields.Char(string="Before End Of Expiry Date", related='company_id.days_iqama', readonly=False)
#     interval_type_iqama = fields.Selection([('days', 'Day(s)'),
#                                                      ('weeks', 'Weeks(s)'),
#                                                      ('months', 'Months(s)'),
#                                                      ('months_last_day', 'Month(s) Last Day(s)'),
#                                                      ('year', 'Year(s)'), ], string='Interval Unit',
#                                                     related='company_id.interval_type_iqama', readonly=False)
#     employee_id_from = fields.Many2one('hr.employee', related='company_id.employee_id_from',string='Employee To' , readonly=False)
#
#
#
# class CompanyExt(models.Model):
#     _inherit = "res.company"
#
#     employee_ids_iqama = fields.Many2many('hr.employee', "employee_iqama_company", "employee_id","company_id", string='Employee')
#     employee_ids_passport = fields.Many2many('hr.employee', "employee_passport_company", "employee_id","company_id", string='Employee')
#     days_iqama = fields.Char(string="Before End Of Expiry Date")
#     interval_type_iqama = fields.Selection([('days', 'Day(s)'),
#                                                      ('weeks', 'Weeks(s)'),
#                                                      ('months', 'Months(s)'),
#                                                      ('months_last_day', 'Month(s) Last Day(s)'),
#                                                      ('year', 'Year(s)'), ], string='Interval Unit', default='days')
#     employee_id_from = fields.Many2one('hr.employee', string='Employee')

