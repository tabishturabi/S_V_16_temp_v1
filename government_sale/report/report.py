# -*- coding:utf-8 -*-

from odoo import api, models
from datetime import timedelta, datetime, date


class ReportSaleGovAgreement(models.AbstractModel):
    _name = 'report.government_sale.sale_gov_agreement_report_id'
    _description = "Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['transport.management'].browse(docids)

        user_data = self.env['hr.employee'].search([('user_id.id', '=', docs.create_uid.id)], limit=1)
        user_code = user_data.driver_code

        voucher_amt = 0
        voucher_num = ""
        for vouc in docs.invoice_id.payment_ids:
            voucher_amt = voucher_amt + vouc.amount
            voucher_num = voucher_num + ' ' + str(vouc.number)

        actual_time = datetime.now() + timedelta(hours=3)
        am_pm = str(actual_time)[11:13]
        actual_time = str(actual_time)[:16]
        actual_time = datetime.strptime(actual_time, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %I:%M')
        if int(am_pm) > 12:
            actual_time = actual_time + ' ' + 'PM'
        if int(am_pm) <= 12:
            actual_time = actual_time + ' ' + 'AM'

        return {
            'doc_ids': docids,
            'doc_model': 'transport.management',
            'data': data,
            'docs': docs,
            'user_code': user_code,
            'voucher_amt': voucher_amt,
            'voucher_num': voucher_num,
            'actual_time': actual_time,

        }


