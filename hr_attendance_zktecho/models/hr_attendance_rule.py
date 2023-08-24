# -*- coding: utf-8 -*-

from __future__ import division
from datetime import *
import pytz
from odoo import api, fields, models, exceptions, _


class hr_attendance_rule(models.Model):

    _name = "hr.attendance.rule"
    _inherit = ['mail.thread']
    _description = "Attendance Rule"
    # _rec_name = 'branch_id'

    APPLY_ON_SEL = [
        ("work", "Work Schedule"),
        ("branch", "Branch"),
        ("dep", "Department"),
        ("company", "Company"),
    ]

    name = fields.Char(string="Name")
    description = fields.Char(string='Description')

    work_schedule_id = fields.Many2many(comodel_name='resource.calendar', string='Work Schedule')
    branch_id = fields.Many2many('bsg_branches.bsg_branches', string="Branch")
    department_id = fields.Many2many('hr.department', string="Department")
    company_id = fields.Many2many('res.company', string="Company")

    apply_on = fields.Selection(APPLY_ON_SEL, string="Apply On", default="work")

    # no check-in/out
    no_checkin_options = fields.Selection([("absent", "Absent"), ("late", "Late Arrival")], default="absent")
    no_checkin_late_min = fields.Integer(string="No Checking in late Min")
    no_checkout_options = fields.Selection([("absent", "Absent"), ("early", "Leave Early")], default="absent")
    no_checkout_leave_min = fields.Integer(string="No Checkout early Min")

    # absent
    checkin_late_as_abs = fields.Integer("If late exceed, Count as absent")
    checkout_early_as_abs = fields.Integer("If early exceed, Count as absent")

    # overtime
    is_allowed_before_ot = fields.Boolean("Allowed Before OT")
    is_allowed_after_ot = fields.Boolean("Allowed After OT")
    min_before_ot = fields.Integer("Minimum Time before Start Count OT")
    min_before_ot_period = fields.Integer("Interval before Start Count OT")
    min_after_ot = fields.Integer("Minimum Time After End Count OT")
    min_after_ot_period = fields.Integer("Interval After End Count OT")

    max_before_ot = fields.Integer("Limit Max Before OT")
    max_after_ot = fields.Integer("Limit Max After OT")
    max_total_ot = fields.Integer("Max OT", compute="compute_max_total_ot", store=True)

    @api.depends('max_before_ot', 'max_after_ot')
    def compute_max_total_ot(self):
        for rec in self:
            rec.max_total_ot = rec.max_before_ot + rec.max_after_ot

    # working_hours = fields.Integer(string="Working Hours")
    # one_workday_as = fields.Integer(string="One Workday as")
    # clock_in_over = fields.Integer(string="Clock-in Over")
    # clock_out_over = fields.Integer(string="Clock-out Over")
    # no_clock_in = fields.Boolean(string='If no clock in')
    # no_clock_in_count_as = fields.Selection([('late','Late'),('early_leave','Early Leave')],string='Count as')
    # no_clock_in_mins = fields.Integer(string="Mins")
    # no_clock_out = fields.Boolean(string='If no clock out')
    # no_clock_out_count_as = fields.Selection([('late', 'Late'), ('early_leave', 'Early Leave')], string='Count as')
    # no_clock_out_mins = fields.Integer(string="Mins")
    # as_late_exceed = fields.Boolean(string="As Late Exceed")
    # as_late_exceed_mins = fields.Integer(string='Count as absent')
    # as_early_leave_exceed = fields.Boolean(string="As Early Leave Exceed")
    # as_early_leave_exceed_mins = fields.Integer(string='Count as absent ')
    # min_time_to_start_after_ot = fields.Boolean(string='Min time to start after OT')
    # min_time_to_start_after_ot_min = fields.Integer(string='Minutes')
    # calculate_above_interval_as_ot_after_ot = fields.Integer(string='Calculate above interval as OT')
    # limit_max_after_ot = fields.Boolean(string='Limit max after OT')
    # limit_max_after_ot_as_minutes = fields.Integer(string='As Minutes')
    # min_time_to_start_before_ot = fields.Boolean(string='Min time to start before OT')
    # min_time_to_start_before_ot_min = fields.Integer(string='Minutes')
    # calculate_above_interval_as_ot_before_ot = fields.Integer(string='Calculate above interval as OT')
    # limit_max_early_ot = fields.Boolean(string='Limit max early OT')
    # limit_max_early_ot_as_minutes = fields.Integer(string='As Minutes')
    # limit_max_total_ot = fields.Boolean(string='Limit max total OT')
    # limit_max_total_ot_as_minutes = fields.Integer(string='As Minutes')


#####################################################


class EmployeeAttendanceRule(models.Model):

    _name = "hr.attendance.rule.emp"

    # @api.multi
    def name_get(self):
        result = []
        for rule in self:
            result.append((rule.id, "%s" % (rule.employee_id.name or '')))
        return result

    employee_id = fields.Many2one("hr.employee")

    # general day

    # workday_min = fields.Integer("Workday in Min")
    # late_checkin_min = fields.Integer("Check-in Over Minutes counts Late")
    # early_checkout_min = fields.Integer("Check-out Over Minutes counts Early")

    # no check-in/out
    no_checkin_options = fields.Selection([("absent", "Absent"), ("late", "Late Arrival")], default="absent")
    no_checkin_late_min = fields.Integer(string="No Checking in late Min")
    no_checkout_options = fields.Selection([("absent", "Absent"), ("early", "Leave Early")],  default="absent")
    no_checkout_leave_min = fields.Integer(string="No Checkout early Min")

    # absent
    checkin_late_as_abs = fields.Integer("If late exceed, Count as absent")
    checkout_early_as_abs = fields.Integer("If early exceed, Count as absent")

    # overtime
    is_allowed_before_ot = fields.Boolean("Allowed Before OT")
    is_allowed_after_ot = fields.Boolean("Allowed After OT")
    min_before_ot = fields.Integer("Minimum Time before Start Count OT")
    min_before_ot_period = fields.Integer("Interval before Start Count OT")
    min_after_ot = fields.Integer("Minimum Time After End Count OT")
    min_after_ot_period = fields.Integer("Interval After End Count OT")

    max_before_ot = fields.Integer("Limit Max Before OT")
    max_after_ot = fields.Integer("Limit Max After OT")
    max_total_ot = fields.Integer("Max OT", compute="compute_max_total_ot", store=True)

    @api.depends('max_before_ot', 'max_after_ot')
    def compute_max_total_ot(self):
        for rec in self:
            rec.max_total_ot = rec.max_before_ot + rec.max_after_ot
