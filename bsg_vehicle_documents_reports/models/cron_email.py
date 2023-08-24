from odoo import api, fields, models
from datetime import date, datetime
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta


class CronEmail(models.Model):
    _name = 'vehicle.documents.report'
    _description = 'vehicle documents report'

    # @api.multi
    def get_documents_notification(self):
        rec = self.env['notification_settings'].search([], limit=1)
        for data in rec:
            days = 0
            check_type = data.interval_type_document
            if check_type == "days":
                days = data.days_document
            if check_type == "weeks":
                days = int(data.days_document) * 7
            if check_type == "months":
                days = int(data.days_document)
                today_date = fields.Date.today()
                next_date = today_date + relativedelta(months=days)
                total_days = next_date - today_date
                get_days = str(total_days).rpartition(' days,')[0]
                days = int(get_days)
            if check_type == "months_last_day":
                days = int(data.days_document) * 31
            if check_type == "year":
                days = int(data.days_document) * 365
            employee_ids = data.employee_ids_document
            employee_id = data.employee_document_from
            exp = datetime.today() + timedelta(int(days))
            exp.date()
            record = self.env['vehicle.documents.report.wizard'].create({'expiry_date': exp.date(),
                                                            'grouping_by': 'document_type',
                                                            'expire_date_condition': 'is_before_or_equal_to',
                                                            })
        attachment_id = record.get_notification()
        MailTemplate = self.env.ref('bsg_vehicle_documents_reports.notification_details_email_template', False)
        MailTemplate.attachment_ids = [(6, 0, attachment_id.ids)]
        for rec in employee_ids:
            if rec.partner_id.email:
                MailTemplate.sudo().write(
                    {'email_to': str(rec.partner_id.email), 'email_from': str(employee_id.partner_id.email)})
                MailTemplate.sudo().send_mail(self.id, force_send=True)
