# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api
from odoo.exceptions import UserError,ValidationError


class NotificationSettings(models.Model):
    _name = 'notification_settings'

    employee_ids_iqama = fields.Many2many('hr.employee', "employee_iqamaa_company", "employee_id", "company_id",
                                          string='Employee')
    employee_ids_passport = fields.Many2many('hr.employee', "employee_passportt_company", "employee_id", "company_id",
                                             string='Employee')
    days_iqama = fields.Char(string="Before End Of Expiry Date")
    interval_type_iqama = fields.Selection([('days', 'Day(s)'),
                                            ('weeks', 'Weeks(s)'),
                                            ('months', 'Months(s)'),
                                            ('months_last_day', 'Month(s) Last Day(s)'),
                                            ('year', 'Year(s)'), ], string='Interval Unit', default='days')
    employee_id_from = fields.Many2one('hr.employee', string='Employee')



    employee_ids_license = fields.Many2many('hr.employee', "employee_licencee_company", "employee_id", "company_id",
                                            string='Employee')
    employee_license_from = fields.Many2one('hr.employee', string='Employee')

    days_license = fields.Char(string="Before End Of Expiry Date")
    interval_type_license = fields.Selection([('days', 'Day(s)'),
                                              ('weeks', 'Weeks(s)'),
                                              ('months', 'Months(s)'),
                                              ('months_last_day', 'Month(s) Last Day(s)'),
                                              ('year', 'Year(s)'), ], string='Interval Unit', default='days')




    employee_document_from = fields.Many2one('hr.employee', string='Employee')

    employee_ids_document = fields.Many2many('hr.employee', "employee_documentt_company", "employee_id", "company_id",
                                             string='Employee')
    days_document = fields.Char(string="Before End Of Expiry Date")
    interval_type_document = fields.Selection([('days', 'Day(s)'),
                                               ('weeks', 'Weeks(s)'),
                                               ('months', 'Months(s)'),
                                               ('months_last_day', 'Month(s) Last Day(s)'),
                                               ('year', 'Year(s)'), ], string='Interval Unit', default='days')

    employee_schedule = fields.Char(string="Send From")
    employee_schedule_to = fields.Char(string="Send To")
    employee_schedule_cc = fields.Char(string="Send Cc")
    days_schedule = fields.Char(string="Before End Of Expiry Date")
    interval_type_schedule = fields.Selection([('days', 'Day(s)'),
                                               ('weeks', 'Weeks(s)'),
                                               ('months', 'Months(s)'),
                                               ('months_last_day', 'Month(s) Last Day(s)'),
                                               ('year', 'Year(s)'), ], string='Interval Unit', default='days')







    # @api.multi
    def execute_settings(self):
        self.ensure_one()
        bonus_config = self.env.ref('bsg_documents_expire_reports.notification_settings_data', False)
        bonus_config.sudo().write({'employee_ids_iqama': [(6, 0, self.employee_ids_iqama.ids)],
                                   'employee_ids_passport': [(6, 0, self.employee_ids_passport.ids)],
                                   'employee_ids_license': [(6, 0, self.employee_ids_license.ids)],
                                   'employee_ids_document': [(6, 0, self.employee_ids_document.ids)],
                                   'days_iqama': self.days_iqama,
                                   'days_license': self.days_license,
                                   'days_document': self.days_document,
                                   'interval_type_iqama': self.interval_type_iqama,
                                   'interval_type_document': self.interval_type_document,
                                   'interval_type_license': self.interval_type_license,
                                   'employee_id_from': self.employee_id_from.id,
                                   'employee_license_from': self.employee_license_from.id,
                                   'employee_document_from': self.employee_document_from.id,
                                   'employee_schedule': self.employee_schedule,
                                   'employee_schedule_to': self.employee_schedule_to,
                                   'employee_schedule_cc': self.employee_schedule_cc,
                                   'days_schedule': self.days_schedule,
                                   'interval_type_schedule': self.interval_type_schedule,
                                   })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def default_get(self, fields):
        res = super(NotificationSettings, self).default_get(fields)
        notification_config = self.env.ref('bsg_documents_expire_reports.notification_settings_data', False)
        if notification_config:
            res.update({'employee_ids_iqama': notification_config.sudo().employee_ids_iqama.ids,
                        'employee_ids_passport': notification_config.sudo().employee_ids_passport.ids,
                        'employee_ids_license': notification_config.sudo().employee_ids_license.ids,
                        'employee_ids_document': notification_config.sudo().employee_ids_document.ids,
                        'days_iqama': notification_config.sudo().days_iqama,
                        'days_license': notification_config.sudo().days_license,
                        'days_document': notification_config.sudo().days_document,
                        'interval_type_iqama': notification_config.sudo().interval_type_iqama,
                        'interval_type_license': notification_config.sudo().interval_type_license,
                        'interval_type_document': notification_config.sudo().interval_type_document,
                        'employee_schedule_to': notification_config.sudo().employee_schedule_to,
                        'employee_schedule_cc': notification_config.sudo().employee_schedule_cc,
                        'days_schedule': notification_config.sudo().days_schedule,
                        'interval_type_schedule': notification_config.sudo().interval_type_schedule,
                        'employee_id_from': notification_config.sudo().employee_id_from.id,
                        'employee_license_from': notification_config.sudo().employee_license_from.id,
                        'employee_document_from': notification_config.sudo().employee_document_from.id,
                        'employee_schedule': notification_config.sudo().employee_schedule,
                        })
        return res





