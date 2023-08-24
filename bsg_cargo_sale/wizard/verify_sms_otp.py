# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class VerifySMS_OTP(models.TransientModel):
    _name = "verify_sms_otp"

    line_id = fields.Many2one('bsg_vehicle_cargo_sale_line',string='Cargo Sale Line ID')
    sms_otp = fields.Char("SMS Verfication Code")


    def verify(self):
        if self.line_id.sms_otp == self.sms_otp:
            self.line_id.sms_otp = "verified"
        return self.line_id.calculated_no_of_days()
