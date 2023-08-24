from odoo import api, fields, models
from datetime import date, datetime
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta


class CronEmailLicense(models.Model):
    _name = 'bsg.license.reports'
    _description = 'Bsg License Reports'

    # @api.multi
    def get_license_notification(self):
        rec = self.env['notification_settings'].search([], limit=1)
        for data in rec:
            days = 0
            check_type = data.interval_type_license
            if check_type == "days":
                days = data.days_license
            if check_type == "weeks":
                days = int(data.days_license) * 7
            if check_type == "months":
                days = int(data.days_license)
                today_date = fields.Date.today()
                next_date = today_date + relativedelta(months=days)
                total_days = next_date - today_date
                get_days = str(total_days).rpartition(' days,')[0]
                days = int(get_days)
            if check_type == "months_last_day":
                days = int(data.days_license) * 31
            if check_type == "year":
                days = int(data.days_license) * 365
            employee_ids = data.employee_ids_license
            employee_id = data.employee_license_from
            exp = datetime.today() + timedelta(int(days))
            exp.date()
            record = self.env['bsg.license.report'].create({'date': exp.date(),
                                                            'filter_type': 'By Expiry Date',
                                                            'date_type': 'is before or equal to',
                                                            'report_mode': 'Document Type',
            })
        attachment_id = record.get_notification()
        MailTemplate = self.env.ref('bsg_license_report.bsg_license_reports_notification_details_email_template', False)
        MailTemplate.attachment_ids = [(6, 0, attachment_id.ids)]
        for rec in employee_ids:
            if rec.partner_id.email:
                MailTemplate.sudo().write(
                    {'email_to': str(rec.partner_id.email), 'email_from': str(employee_id.partner_id.email)})
                MailTemplate.sudo().send_mail(self.id, force_send=True)
