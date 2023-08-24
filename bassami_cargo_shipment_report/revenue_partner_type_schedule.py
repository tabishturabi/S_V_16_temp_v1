from odoo import api, fields, models
from datetime import date, datetime
from datetime import datetime, timedelta
import base64


class CronEmail(models.Model):
    _name = 'sale.revenue.by.partner.schedule'
    _description = 'Schedule revenue'

    # @api.multi
    def get_schedule_notification(self):
        rec = self.env['notification_settings'].search([])
        month_ar_map = {'January': 'يناير',
            'February': 'فبراير',
            'March':'مارس',
            'April':'أبريل',
            'May':'مايو',
            'June':'يونيو',
            'July':'يوليو',
            'August':'أغسطس',
            'September':'سبتمبر',
            'October':'أكتوبر',
            'November':'نوفمبر',
            'December':'ديسمبر',}
        for data in rec:
            days_schedule = data.days_schedule
            employee_schedule_to = data.employee_schedule_to
            employee_schedule_cc = data.employee_schedule_cc
            employee_schedule = data.employee_schedule
            # from_exp = datetime(datetime.now().year, (datetime.now()-timedelta(days=1)).month, 1,0,0,0)
            to_exp = datetime(datetime.today().year,datetime.today().month,datetime.today().day,23,59,59)-timedelta(days=1)
            from_exp = datetime(to_exp.year, to_exp.replace(day=1).month, 1, 0, 0, 0)
            record = self.env['sale.revenue.by.partner.type'].create({'to': to_exp,
                                                                      'form': from_exp,
                                                                      'report_type': 'cash_flow',
                                                                      })
        attachment_id = self.env.ref('bassami_cargo_shipment_report.revenue_by_partner').sudo().with_context(
            {'active_id': record.id}).render_qweb_pdf([record.id])[0]
        attachment_report = self.env['ir.attachment'].create({
            'name': 'partner type schedule',
            'type': 'binary',
            'datas': base64.encodestring(attachment_id),
            'mimetype': 'application/x-pdf',
            'store_fname': "Sales Revenue by Partner Type" + "%s %s"%(to_exp.day,to_exp.strftime("%B")) + ".pdf"
        })
        MailTemplate = self.env.ref('bassami_cargo_shipment_report.sale_revenue_notification_details_email_template',
                                    False)
        MailTemplate.attachment_ids = [(6, 0, attachment_report.ids)]

        if employee_schedule_to and employee_schedule:
            body_html = MailTemplate.body_html
            body_html = body_html.replace("{day}", str(to_exp.day)).replace("{month}", month_ar_map[to_exp.strftime("%B")]).replace("{year}", str(to_exp.year))
            data = {'email_to': employee_schedule_to, 'email_from': employee_schedule, 'subject': "تقرير المبيعات %s %s"%(to_exp.day,month_ar_map[to_exp.strftime("%B")]),
                'body_html':body_html}
            if employee_schedule_cc:
                data['email_cc'] = employee_schedule_cc
            MailTemplate.sudo().write(data)
            MailTemplate.sudo().send_mail(self.id, force_send=True)

