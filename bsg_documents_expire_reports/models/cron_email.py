from odoo import api, fields, models
from datetime import date, datetime
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta




class CronEmail(models.Model):
    _name = 'employee.iqama.report'
    _description = 'iqama documents report'

    # @api.multi
    def get_iqama_notification(self):
        rec = self.env['notification_settings'].search([], limit=1)
        for data in rec:
            days = 0
            check_type = data.interval_type_iqama
            if check_type == "days":
                days = data.days_iqama
            if check_type == "weeks":
                days = int(data.days_iqama) * 7
            if check_type == "months":
                days = int(data.days_iqama)
                today_date = fields.Date.today()
                next_date = today_date + relativedelta(months=days)
                total_days = next_date - today_date
                get_days = str(total_days).rpartition(' days,')[0]
                days = int(get_days)
            if check_type == "months_last_day":
                days = int(data.days_iqama) * 31
                print("monthes last day", days)
            if check_type == "year":
                days = int(data.days_iqama) * 365
            employee_ids = data.employee_ids_iqama
            employee_id = data.employee_id_from
            exp = datetime.today() + timedelta(int(days))
            exp.date()
            record = self.env['employee.iqama.report.wizard'].create({'expiry_date': exp.date(),
                                                            'grouping_by': 'all',
                                                            'mode': 'all',
                                                            'expire_date_condition': 'is_before_or_equal_to',
                                                            'employee_state': 'all',
                                                            })
        attachment_id = record.get_notification()
        MailTemplate = self.env.ref('bsg_documents_expire_reports.iqama_report_notification_details_email_template', False)
        MailTemplate.attachment_ids = [(6, 0, attachment_id.ids)]
        for rec in employee_ids:
            if rec.partner_id.email:
                MailTemplate.sudo().write(
                    {'email_to': str(rec.partner_id.email), 'email_from': str(employee_id.partner_id.email)})
                MailTemplate.sudo().send_mail(self.id, force_send=True)


class CronEmailPassport(models.Model):
    _name = 'employee.passport.report'
    _description = 'passport documents report'

    # @api.multi
    def get_passport_notification(self):
        rec = self.env['notification_settings'].search([], limit=1)
        for data in rec:
            days = 0
            check_type = data.interval_type_iqama
            if check_type == "days":
                days = data.days_iqama
            if check_type == "weeks":
                days = int(data.days_iqama) * 7
            if check_type == "months":
                days = int(data.days_iqama)
                today_date = fields.Date.today()
                next_date = today_date + relativedelta(months=days)
                total_days = next_date - today_date
                get_days = str(total_days).rpartition(' days,')[0]
                days = int(get_days)
            if check_type == "months_last_day":
                days = int(data.days_iqama) * 31
            if check_type == "year":
                days = int(data.days_iqama) * 365

            employee_ids = data.employee_ids_passport
            employee_id = data.employee_id_from
            exp = datetime.today() + timedelta(int(days))
            exp.date()
            record = self.env['employee.passport.report.wizard'].create({'expiry_date': exp.date(),
                                                                      'grouping_by': 'all',
                                                                      'mode': 'all',
                                                                      'expire_date_condition': 'is_before_or_equal_to',
                                                                      'employee_state': 'all',
                                                                      })
        attachment_id = record.get_notification()
        MailTemplate = self.env.ref('bsg_documents_expire_reports.passport_notification_details_email_template',
                                    False)
        MailTemplate.attachment_ids = [(6, 0, attachment_id.ids)]
        for rec in employee_ids:
            if rec.partner_id.email:
                MailTemplate.sudo().write(
                    {'email_to': str(rec.partner_id.email), 'email_from': str(employee_id.partner_id.email)})
                MailTemplate.sudo().send_mail(self.id, force_send=True)

class CronEmailReports(models.Model):
    _name = 'cron.email.reports'
    _description = 'Cron Email Reports'

    # @api.multi
    def get_email_notification(self):
        self.env['employee.passport.report'].search([]).get_passport_notification()
        self.env['employee.iqama.report'].search([]).get_iqama_notification()
        self.env['bsg.license.reports'].search([]).get_license_notification()
        self.env['vehicle.documents.report'].search([]).get_documents_notification()
