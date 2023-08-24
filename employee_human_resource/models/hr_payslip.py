from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    hr_termination_id = fields.Many2one(comodel_name="hr.termination", string="Hr Termination")
    hr_termination_duration_id = fields.Many2one(comodel_name="hr.termination.duration", string="Hr Termination Duration")
