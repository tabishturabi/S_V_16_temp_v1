from odoo import api, fields, models
from datetime import date, datetime
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta




class CronEmail(models.Model):
    _name = 'house.movement.report'
    _description = 'House documents report'

    
    def get_house_notification(self):
        rec = self.env['permission_settings'].search([], limit=1)
        for data in rec:
            days = 0
            check_type = data.interval_type
            if check_type == "days":
                days = data.days_schedule
            if check_type == "weeks":
                days = int(data.days_schedule) * 7
            if check_type == "months":
                days = int(data.days_schedule)
                today_date = fields.Date.today()
                next_date = today_date + relativedelta(months=days)
                total_days = next_date - today_date
                get_days = str(total_days).rpartition(' days,')[0]
                days = int(get_days)
            if check_type == "months_last_day":
                days = int(data.days_schedule) * 31
                print("monthes last day", days)
            if check_type == "year":
                days = int(data.days_schedule) * 365
            employee_to = data.employee_to
            employee_cc = data.employee_cc
            employee_sending = data.employee_sending
            exp = datetime.today() + timedelta(int(days))
            exp.date()
            record = self.env['house.movement'].create({'date_from': exp.date(),
                                                            'report_mode': 'house_movement_transaction_type',
                                                            'transaction_type': 'entry_housing',
                                                            'day_condition': 'is before or equal to',
                                                            })
        attachment_id = record.get_notification()
        MailTemplate = self.env.ref('housing.house_report_notification_details_email_template', False)
        MailTemplate.attachment_ids = [(6, 0, attachment_id.ids)]

        if employee_to:
            to = employee_to.split(", ")
            if to:
                for rec in to:
                    MailTemplate.sudo().write(
                        {'email_to': str(employee_to), 'email_from': str(employee_sending)})
                    MailTemplate.sudo().send_mail(self.id, force_send=True)

        if employee_cc:
            cc = employee_cc.split(", ")
            if cc:
                for rec in cc:
                    MailTemplate.sudo().write(
                        {'email_to': str(employee_cc), 'email_from': str(employee_sending)})
                    MailTemplate.sudo().send_mail(self.id, force_send=True)




