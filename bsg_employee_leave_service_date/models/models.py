# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class EmployeeLeaveAndServiceDate(models.Model):
    _inherit = 'hr.employee'


    leave_start_date = fields.Date(string='Leave Start Date')
    end_service_date = fields.Date(string='Service End Date')
    # last_return_date = fields.Date(string='Effective Date')

    @api.onchange('last_return_date')
    def onchange_returndate(self):
        if self.leave_start_date and self.last_return_date:
            if self.last_return_date < self.leave_start_date:
                raise UserError('Return date must be greater than start date')



