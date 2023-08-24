import xlsxwriter
from datetime import timedelta

from odoo import models,fields,api,_
from odoo.exceptions import UserError,ValidationError


class AttendanceDailyReport(models.AbstractModel):
    _name = 'report.hr_attendance_reports.attendance_daily_report'

    def get_attendances(self, wizard, employee_domain):
        employees = self.env["hr.employee"].search(employee_domain)
        attendance_domain = [("employee_id", "in", employees.ids)]
        if wizard.date_from:
            attendance_domain += [("day", '>=', wizard.date_from)]
        if wizard.date_to:
            attendance_domain += [("day", '<=', wizard.date_to)]
        attendances = self.env["hr.attendance"].search(attendance_domain)
        return attendances

    def _add_grouping_by(self, attendances, grouping_by):
        if grouping_by == 'by_branches':
            branches = attendances.mapped("employee_id.branch_id")
            attendances = [[branch.branch_ar_name, attendances.filtered(lambda x: x.employee_id.branch_id == branch)]
                           for branch in branches]
        elif grouping_by == 'by_departments':
            departments = attendances.mapped("employee_id.department_id")
            attendances = [[department.name, attendances.filtered(lambda x: x.employee_id.department_id == department)]
                           for department in departments]
        elif grouping_by == 'by_job_positions':
            jobs = attendances.mapped("employee_id.job_id")
            attendances = [[job.name, attendances.filtered(lambda x: x.employee_id.job_id == job)]
                           for job in jobs]
        else:
            attendances = [["all", attendances],]
        return attendances

    def get_employee_calendar(self, employee):
        active_calendar_line = employee.calender_lines and employee.calender_lines.filtered(lambda x: x.is_current)
        current_calendar = active_calendar_line.calender_id
        if not current_calendar:
            current_calendar = employee.resource_calendar_id
        return current_calendar

    def is_weekday(self, employee, date):
        work_schedule = self.get_employee_calendar(employee)
        work_schedule.ensure_one()
        date_weekday = date.weekday()
        days_of_week = [line.dayofweek for line in work_schedule.attendance_ids]
        if str(date_weekday) in days_of_week:
            return True
        else:
            return False

    def _add_missig_days(self, attendances, date_from, date_to, employee_domain):
        print("here")
        print("attendances", attendances)
        employees = self.env["hr.employee"].search(employee_domain)

        for grouping_by in attendances:
            print("grouping_by", grouping_by)
            recs = grouping_by[1]
            start_date = date_from
            all_days = []
            while start_date < date_to:
                for employee in employees:
                    atts = recs.filtered(lambda x: x.day == start_date and x.employee_id == employee)
                    if atts:
                        for att in atts:
                            all_days.append((employee, start_date, att))
                    else:
                        # check for weekend here
                        if self.is_weekday(employee, start_date):
                            all_days.append((employee, start_date, False))

                start_date = start_date + timedelta(days=1)

            print("recs", recs)
            print("all_days", all_days)
            grouping_by[1] = all_days
        return attendances

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = data.get("employee_domain")
        model = self.env.context.get('active_model')
        wizard = self.env[model].browse(self.env.context.get('active_id'))
        all_attendances = self.get_attendances(wizard, domain)
        attendances = self._add_grouping_by(all_attendances, wizard.grouping_by)
        attendances = self._add_missig_days(attendances, wizard.date_from, wizard.date_to, domain)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'attendances': attendances,
            # 'grouping_by': False if wizard.grouping_by == 'all' else True,
            'docs': wizard
        }




























