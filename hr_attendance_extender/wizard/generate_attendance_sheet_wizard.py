# -*- coding: utf-8 -*-
import time
from datetime import datetime , timedelta
from dateutil import relativedelta as re

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class GenerateAttendanceSheet(models.TransientModel):
    _name = 'generate.attendance.sheet'
    _descripition = 'To Generate Attendance Sheet'

    employee_ids = fields.Many2many('hr.employee',string='Employees Name')
    date_start = fields.Date(string='Date From', required=True, default=time.strftime('%Y-%m-01'))
    date_end = fields.Date(string='Date To', required=True, default=str(datetime.now() + re.relativedelta(months=+1, day=1, days=-1))[:10])

    #@api.multi
    def generate_attendance_record(self):
        all_attendance_recs = self.env['hr.attendance'].search([])
        all_attendance_sheets = self.env['hr.attendance.sheet'].search([])
        if self.employee_ids:
            for employee in self.employee_ids:
                if employee.contract_id and not employee.contract_id.is_not_required_attendance:
                    date_start = datetime.strptime(str(self.date_start), '%Y-%m-%d').date()
                    date_end = datetime.strptime(str(self.date_end), '%Y-%m-%d').date()

                    attendances = all_attendance_recs.filtered(lambda r:
                            (datetime.strptime(r.expected_check_out_max, DEFAULT_SERVER_DATETIME_FORMAT).date()) <= date_end
                                and
                            (datetime.strptime(r.expected_check_in_min, DEFAULT_SERVER_DATETIME_FORMAT).date()) >= date_start
                                 and r.append_in_sheet is False and not r.sheet_id and r.state == 'validate'

                                 and r.employee_id.id == employee.id)
                    if attendances:
                        sheet = all_attendance_sheets.filtered(
                            lambda x: (datetime.strptime(str(x.date_from), '%Y-%m-%d').date())
                                     >=
                                     (datetime.strptime(str(self.date_start), '%Y-%m-%d').date())
                                     and
                                     (datetime.strptime(str(x.date_to), '%Y-%m-%d').date())
                                     <=
                                     (datetime.strptime(str(self.date_end), '%Y-%m-%d').date())
                                     and
                                     x.employee_id.id == employee.id
                                                                      )
                        if sheet:
                            raise UserError(_('Kindly Employee %s already has an existing a Attendance Sheet will be generated!') %
                                            (employee.name))
                        if not sheet:
                            sheet_id = sheet.create({'employee_id':employee.id,
                                                                     'date_from': self.date_start,
                                                                     'date_to': self.date_end,
                                                                     'state': 'draft',
                                                                     })

                            if sheet_id:
                                for record in attendances:
                                    record.write({'sheet_id': sheet_id.id, 'append_in_sheet':True})
                                sheet_id.action_compute_sheet()
        else:
            raise UserError(_('Kindly Specify a Employee Records because a Attendance Sheet will be generated!'))

