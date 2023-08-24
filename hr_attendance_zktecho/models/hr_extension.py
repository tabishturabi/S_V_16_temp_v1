# -*- coding: utf-8 -*-
from lxml import etree
# from odoo.osv.orm import setup_modifiers
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError,UserError
#import datetime
#from pytz import timezone, UTC
from datetime import date, timedelta

class HrAttendance(models.Model):

    _name = 'hr.attendance'
    _inherit = ['hr.attendance','mail.thread']

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    name = fields.Datetime('Datetime')
    day = fields.Date("Day")
    is_missing = fields.Boolean('Missing', default=False)
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True, track_visibility='onchange')
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True, track_visibility='onchange')
    check_out = fields.Datetime(string="Check Out", track_visibility='onchange')


class hrDraftAttendance(models.Model):

    _name = 'hr.draft.attendance'
    _inherit = ['mail.thread']
    _order = 'name desc'


    name = fields.Datetime('Datetime', required=False,track_visibility='onchange')
    date = fields.Date('Date', required=False,track_visibility='onchange')
    day_name = fields.Char('Day',track_visibility='onchange')
    attendance_status = fields.Selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('sign_none', 'None')], 'Attendance State', required=True,track_visibility='onchange')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',track_visibility='onchange')
    lock_attendance = fields.Boolean('Lock Attendance',track_visibility='onchange')
    biometric_attendance_id = fields.Integer(string='Biometric Attendance ID',track_visibility='onchange')
    is_missing = fields.Boolean('Missing', default=False,track_visibility='onchange')
    moved = fields.Boolean(default=False)
    moved_to = fields.Many2one(comodel_name='hr.attendance', string='Moved to HR Attendance')
    origin_device_id = fields.Many2one("biomteric.device.info", string="Origin Device")
    authentication_type = fields.Selection([("fingerprint", "Fingerprint"), ("face", "Face"), ("card", "Card"),
                                            ("password", "Password"), ("other", "Other")])
    skipped = fields.Boolean("Skipped record")

    # @api.multi
    def unlink(self):
        for rec in self:
            if rec.moved == True:
                raise UserError(_("You can`t delete Moved Attendance"))
        return super(hrDraftAttendance, self).unlink()

    @api.model
    def _get_employee_by_attendance_id(self,biometric_attendance_id):
        if biometric_attendance_id:
            employee_attend = self.env['employee.attendance.devices'].sudo().search([('attendance_id','=',biometric_attendance_id)],limit=1)
            if employee_attend:
                return employee_attend.name.id
        return False        


    @api.model
    def create(self, vals):
        res = super(hrDraftAttendance, self).create(vals)
        if not res.employee_id and res.biometric_attendance_id:
            employee_id = self._get_employee_by_attendance_id(res.biometric_attendance_id)
            res.employee_id = employee_id
        return res

    @api.model
    def update_employee(self):
        """ Update Employee
        """
        for rec in self:
            if rec.biometric_attendance_id:
                employee_id = rec._get_employee_by_attendance_id(rec.biometric_attendance_id)
                if employee_id:
                    rec.employee_id = employee_id
            
         
    #time = fields.Float('Time', compute='_compute_time', store=True)
    #
    #@api.depends('name')
    #def _compute_time(self):
    #    for rec in self:
    #        if rec.name:
    #            user = self.env['res.users'].search([('active','=',True)], limit=1, order='id asc')
    #            tz = user.tz if user.tz else 'UTC'
    #            local_tz = timezone(tz)
    #            dt = rec.name.replace(tzinfo=UTC)
    #            dt = dt.astimezone(timezone(tz))
    #            time = dt.hour+dt.minute/60.0
    #            rec.time = time


class Employee(models.Model):

    _inherit = 'hr.employee'

    is_shift = fields.Boolean("Shifted Employee")
    attendance_devices = fields.One2many(comodel_name='employee.attendance.devices', inverse_name='name', string='Attendance')
    draft_attendances = fields.One2many(comodel_name='hr.draft.attendance', inverse_name='employee_id', string='Draft Attendances')
    draft_attendances_not_moved = fields.One2many(comodel_name='hr.draft.attendance', compute='_get_draft_attendance', string='Draft Attendances', store=False)
    last_draft_attendance_id = fields.Many2one('hr.draft.attendance', compute='_compute_last_draft_attendance_id')
    active_on_reports = fields.Boolean(string='Active On Reports')
    count_overtime = fields.Boolean(string='Count Overtime')
    holiday_overtime = fields.Boolean(string='Holiday Overtime')
    check_in = fields.Selection([('by_time_zone', 'By Time Zone'), ('must_clock_in', 'Must Clock In'),('donot_check', 'Do Not Check')],
                                default='must_clock_in', string="Check In")
    check_out = fields.Selection([('by_time_zone', 'By Time Zone'), ('must_clock_out', 'Must Clock Out'), ('donot_check', 'Do Not Check')],
                                 default='must_clock_out', string="Check Out")
    calender_lines = fields.One2many("employee.calendar.line", "employee_id", string="Calender Lines")

    @api.depends('draft_attendances')
    def _compute_last_draft_attendance_id(self):
        for employee in self:
            employee.last_draft_attendance_id = employee.draft_attendances and employee.draft_attendances[0] or False

    @api.depends('last_draft_attendance_id.attendance_status', 'last_draft_attendance_id', 'last_attendance_id.check_in', 'last_attendance_id.check_out', 'last_attendance_id')
    def _compute_attendance_state(self):
        for employee in self:
            if employee.last_attendance_id and not employee.last_attendance_id.zkteco_device_attendance:
                employee.attendance_state = employee.last_attendance_id and not employee.last_attendance_id.check_out and 'checked_in' or 'checked_out'
            else:
                _logger.info('Computing attendance state for employee ' + str(employee))
                attendance_state = 'checked_out'
                if employee.last_draft_attendance_id and employee.last_draft_attendance_id.attendance_status == 'sign_in':
                    _logger.info('    check in found for employee ' + str(employee) + ' -- ' + str(employee.last_draft_attendance_id))
                    attendance_state = 'checked_in'
                employee.attendance_state = attendance_state

    # @api.one
    def _get_draft_attendance(self):
        #_logger.info(self._context)
        draft_start_date = self._context.get('draft_start_date', False)
        draft_end_date = self._context.get('draft_end_date', False)
        search_domain = [('employee_id', '=', self.id), ('moved', '=', False)]
        if draft_start_date:
            search_domain.append(('name', '>=', draft_start_date))
        if draft_end_date:
            search_domain.append(('name', '<=', draft_end_date))
        #_logger.info(search_domain)
        self.draft_attendances_not_moved = self.env['hr.draft.attendance'].search(search_domain)

    def action_view_emp_rules(self):
        emp_rule = self.env["hr.attendance.rule.emp"].search([("employee_id", "=", self.id)], limit =1)
        data = {'default_employee_id' : self.id}
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.attendance.rule.emp',
            'view_id':  self.env.ref('hr_attendance_zktecho.hr_attendance_rule_emp_form').id,
            'view_mode': 'form',
            'view_type': 'form',
            'context': data,
            'res_id': emp_rule.id if emp_rule else False,
            'target': 'new',
        }

###############################


class EmployeeWorkLines(models.Model):
    _name = 'employee.calendar.line'
    _description = 'Employee Calendar'

    # resource.calendar

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(EmployeeWorkLines, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)

        doc = etree.XML(result['arch'])
        for node in doc.xpath("//field[@name='employee_id']"):
            departments = self.env.user.employee_ids.mapped("department_id")
            node.set('domain', "[('department_id', 'in', %s)]"%str(departments.ids))
        result['arch'] = etree.tostring(doc, encoding='unicode')
        return result

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',
                                 )
    calender_id = fields.Many2one(comodel_name='resource.calendar', string='Work Schedule')
    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
    is_current = fields.Boolean(string="Currently Active", compute="compute_is_current", store=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
                                    store=True, readonly=True)
    allowed_departments = fields.Many2many("hr.department", string="Allowed Departments",
                                           compute="compute_allowed_departments")
    is_multi_shift = fields.Boolean("Is multi Shift")
    # allowed_employees = fields.Many2many("hr.employee", string="Allowed Employees",
    #                                      compute="compute_allowed_departments")

    def compute_allowed_departments(self):
        for rec in self:
            departments = self.env.user.employee_ids.mapped("department_id")
            rec.allowed_departments = departments
            # rec.allowed_employees = departments.member_ids

    @api.depends("date_from", "date_to", "is_multi_shift")
    def compute_is_current(self):
        for rec in self:
            if rec.is_multi_shift:
                """ always true in case of multi shift"""
                rec.is_current = True
            else:
                if rec.date_from and rec.date_to and not rec.is_multi_shift:
                    if not isinstance(rec.id, models.NewId):
                        multi_shift_exist = self.search([("employee_id", "=", rec.employee_id.id), ("id", "!=", rec.id),
                                                 ("is_multi_shift", "=", True)], limit=1)
                    else:
                        multi_shift_exist = self.search([("employee_id", "=", rec.employee_id.id),
                                                         ("is_multi_shift", "=", True)], limit=1)
                    if not multi_shift_exist:
                        today = fields.Date.today()
                        if rec.date_from <= today <= rec.date_to:
                            rec.is_current = True

    @api.constrains('is_multi_shift')
    def _check_is_multi_shift(self):
        for calender in self:
            is_multi_shift = calender.is_multi_shift
            if is_multi_shift:
                domain = [('is_multi_shift', '=', True),
                          ('employee_id', '=', calender.employee_id.id), ('id', '!=', calender.id)]
                ncalender = self.search_count(domain)
                if ncalender:
                    raise ValidationError(_('You can not have 2 calender lines as multi-shift for same employee.'))

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for calender in self:
            date_from = calender.date_from
            date_to = calender.date_to
            if date_from and date_to and not calender.is_multi_shift:
                domain = [
                    ('date_from', '<=', fields.Date.from_string(date_to)),
                    ('date_to', '>=', fields.Date.from_string(date_from)),
                    ('employee_id', '=', calender.employee_id.id),
                    ('id', '!=', calender.id), ('is_multi_shift', '=', False)]
                ncalender = self.search_count(domain)
                if ncalender:
                    raise ValidationError(_('You can not have 2 calender lines that overlaps on the same day.'))
                if date_to < date_from:   # Starting date must be prior to the ending date
                    raise ValidationError(_('The ending date must not be prior to the starting date.'))

    @api.model
    def create(self, vals):
        new_line = super(EmployeeWorkLines, self).create(vals)
        if new_line.date_from and new_line.date_to and not new_line.is_multi_shift:
            employee_id = new_line.employee_id
            last_line = self.search([("employee_id", "=", employee_id.id), ("id", "!=", new_line.id),
                                     ("is_multi_shift", "=", False)], limit=1, order="date_to desc")
            new_date = new_line.date_from - timedelta(days=1)
            if last_line:
                last_line.date_to = new_date
        return new_line

################################################################


class EmployeeAttendanceDevices(models.Model):

    _name = 'employee.attendance.devices'

    name = fields.Many2one(comodel_name='hr.employee', string='Employee', readonly=True)
    attendance_id = fields.Char("Attendance ID", required=True)
    branch_id = fields.Many2one('bsg_branches.bsg_branches', required=True, string='Branch')
    device_ids = fields.Many2many('biomteric.device.info', 'employee_devices_rel', 'emp_dev_id', 'att_dev_id',
                                  string='Branch Device', ondelete='restrict')

    @api.onchange('branch_id')
    def get_branch_devices(self):
        for rec in self:
            if rec.branch_id:
                device_ids = rec.env['biomteric.device.info'].search([('branch_id', '=', rec.branch_id.id)])
                rec.device_ids = [(6, 0, device_ids.ids)]

    # @api.multi
    @api.constrains('attendance_id','device_ids','name')
    def _check_unique_constraint(self):
        self.ensure_one()
        record = self.search([('attendance_id', '=', self.attendance_id), ('device_ids', 'in', self.device_ids.ids)])
        if len(record) > 1:
            vals_list = self.device_ids.mapped('name')
            vals = ",".join(vals_list)
            raise ValidationError('Employee with Id ('+ str(self.attendance_id)+') exists on Devices ('+vals+') !')
        record = self.search([('name', '=', self.name.id), ('device_ids', 'in', self.device_ids.ids)])
        if len(record) > 1:
            vals_list = self.device_ids.mapped('name')
            vals = ",".join(vals_list)
            raise ValidationError('Configuration for Devices ('+ vals+') of Employee  ('+ str(self.name.name)+') already exists!')

###########################################################


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    day_period = fields.Selection([('morning', 'Morning'), ('afternoon', 'Afternoon'),('fullday', 'Full Day')], required=True,
                                  default='morning')

