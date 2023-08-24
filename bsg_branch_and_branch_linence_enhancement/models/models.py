# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError
from ummalqura.hijri_date import HijriDate

class LicenseInfoInherit(models.Model):
    _inherit = "bsg.license.info"

    comment = fields.Char(string='Comment',translate=True)
    hijri_issue_date = fields.Char(string='Hijri Issue Date' ,readonly=True)
    hijri_expiry_date = fields.Char(string='Hijri Expiry Date',readonly=True)

    @api.onchange('expiry_date')
    def get_arabic_expiry_dates(self):
        if self.expiry_date:
            self.hijri_expiry_date = HijriDate.get_hijri_date(self.expiry_date)

    @api.onchange('issue_date')
    def get_arabic_issue_dates(self):
        if self.issue_date:
            self.hijri_issue_date = HijriDate.get_hijri_date(self.issue_date)




