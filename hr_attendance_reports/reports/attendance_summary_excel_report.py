from odoo import models,fields,api,_
from datetime import datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
from datetime import datetime, time, timedelta
from odoo.tools.float_utils import float_round


class EmployeePayslipReportExcel(models.AbstractModel):
    _name = 'report.hr_attendance_reports.attendance_summary_excel_report'
    _inherit ='report.report_xlsx.abstract'

    def get_employee_calendar(self, employee):
        active_calendar_line = employee.calender_lines and employee.calender_lines.filtered(lambda x: x.is_current)
        current_calendar = active_calendar_line.calender_id
        if not current_calendar:
            current_calendar = employee.resource_calendar_id
        return current_calendar

    def get_normal_days(self, employee, date_from, date_to):
        work_schedule = self.get_employee_calendar(employee)
        work_schedule.ensure_one()
        days_of_week = [(line.dayofweek, line.day_period) for line in work_schedule.attendance_ids]
        start_date = date_from
        normal_days = 0
        while start_date <= date_to:
            for day in days_of_week:
                if str(start_date.weekday()) in day[0]:
                    if day[1] == "fullday":
                        normal_days += 1
                    else:
                        normal_days += .5
            delta = timedelta(days=1)
            start_date += delta
        return normal_days

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

    def add_leave_types(self):
        leave_types = self.env["hr.leave.type"].search([])
        hour_leaves = [(leave.name, "Hour", "leave_hour") for leave in leave_types.filtered(lambda x: x.request_unit == "hour")]
        day_leaves = [(leave.name, "Day", "leave_day") for leave in leave_types.filtered(lambda x: x.request_unit == "day")]
        return hour_leaves + day_leaves

    def add_permissions_types(self, date_from, date_to):
        start_month = date_from.month
        end_month = date_to.month
        month_range = [x for x in range(start_month, end_month+1)]
        permissions = self.env["hr.permission.type"].search([("validity_start", ">=", date_from)])
        permissions = permissions.filtered(
            lambda x: x.validity_start.month in month_range or x.validity_stop.month in month_range)
        return [(permission.name, "Hour", "permission") for permission in permissions]

    def get_header(self, date_from, date_to):
        workday = "WDay"
        min = "Min."
        hour = "Hour"
        times = "Times"
        table_header_list = [("Name", "", "field"), ("Acc No", "", "field"), ("Normal", workday, "calc"),
                             ("Actual", workday, "calc"), ("Absent", workday, "calc"), ("Late", min, "calc"),
                             ("Early", min, "calc"), ("OT", hour, "calc"), ("AFL", hour, "calc"),
                             ("B Leaves", workday, "calc"), ("N/IN", times, "calc"), ("N/OUT", times, "calc"),
                             ("Normal Hours", times, "calc")] + self.add_leave_types() + \
                            self.add_permissions_types(date_from, date_to) +\
                            [("Working Time", hour, "calc"), ("ATT Rate", "%", "calc")]

        table_header = [{"name": item[0], "unit": item[1], "type": item[2]} for item in table_header_list]
        return table_header

    def get_AFL(self, employee, date_from, date_to, leave_name=None, permission_name=None):
        leaves_domain = [("employee_id", "=", employee.id),
            ("state", "=", "validate"), ("request_unit_half", "=", True),
            "|", ("request_date_from", ">=", date_from), ("request_date_to", "<=", date_to)]
        if leave_name:

            hour_leave_types = self.env["hr.leave.type"].search([("name", "=", leave_name)])
            leaves_domain.append(("holiday_status_id", "in", hour_leave_types.ids))

        leaves = self.env["hr.leave"].search(leaves_domain)
        leaves_days = sum(leaves.mapped("number_of_days"))
        day_length = self.get_employee_calendar(employee).hours_per_day
        total_leave_hours = leaves_days * (day_length /2)
        if leave_name:
            return total_leave_hours

        permission_domain = [
            ("employee_id", "=", employee.id), ("request_date", ">=", date_from), ("request_date", "<=", date_to),
            ("state", "=", "validate")]
        if permission_name:
            permission_type = self.env["hr.permission.type"].search([("name", "=", permission_name)], limit=1)
            permission_domain.append(("permission_type_id", "=", permission_type.id))
        permissions = self.env["hr.permission.request"].search(permission_domain)
        permission_total = sum(permissions.mapped("duration"))
        permission_hours = float_round(permission_total/60, precision_digits=2)
        if permission_name:
            return permission_hours

        return total_leave_hours + permission_hours

    def get_b_leaves(self, employee, date_from, date_to, leave_name=None):
        if not leave_name:
            day_leave_types = self.env["hr.leave.type"].search([("request_unit", "=", "day")])
        else:
            day_leave_types = self.env["hr.leave.type"].search([("name", "=", leave_name)])
        leaves = self.env["hr.leave"].search(
            [("employee_id", "=", employee.id), ("holiday_status_id", "in", day_leave_types.ids),
             "|", ("request_date_from", ">=", date_from), ("request_date_to", "<=", date_to),
             ("request_unit_half", "=", False)])
        total_leave_days = sum(leaves.mapped("number_of_days"))
        return total_leave_days

    def get_actual_days(self, employee_attendances):
        full_day = employee_attendances.filtered(lambda x: not x.is_absent and not x.is_leave and x.calendar_line.day_period == "fullday")
        half_day = employee_attendances.filtered(
            lambda x: not x.is_absent and not x.is_leave and x.calendar_line.day_period in ("morning", "afternoon"))
        return len(full_day) + (len(half_day) * 2)

    def get_absent_days(self, employee_attendances):
        full_day = employee_attendances.filtered(lambda x: x.is_absent and x.calendar_line.day_period == "fullday")
        half_day = employee_attendances.filtered(
            lambda x:  x.is_absent and x.calendar_line.day_period in ("morning", "afternoon"))
        return len(full_day) + (len(half_day) * 2)

    def get_normal_times(self, actual_attendances):
        total_worked_hours = sum(actual_attendances.mapped("worked_hours"))
        total_worked_hours = float_round(total_worked_hours,  precision_digits=1)
        return total_worked_hours

    def get_expected_hours(self, employee, normal_days):
        total_expected_days = normal_days
        day_length = self.get_employee_calendar(employee).hours_per_day
        total_expected_work_hours = total_expected_days * day_length
        # total_expected_work_hours = sum(actual_attendances.mapped("expected_work_hours"))
        # total_expected_work_hours = float_round(total_expected_work_hours,  precision_digits=2)
        return total_expected_work_hours

    def get_att_rate(self, actual, expected):
        rate = (actual / expected) * 100
        rate = float_round(rate,  precision_digits=1)
        rate = "{0:.2f}".format(rate)
        return rate

    def get_summary_line(self, table_header, attendances, date_from, date_to):
        # "Att Rate %": {("Actual hours" / "Schedule Hours") * 100}
        my_list = []
        employees = attendances.mapped("employee_id")
        for employee in employees:
            employee_attendances = attendances.filtered(lambda x: x.employee_id == employee)
            employee_list = []
            actual_days = self.get_actual_days(employee_attendances)
            absent_days = self.get_absent_days(employee_attendances)
            actual_attendances = employee_attendances.filtered(lambda x: not x.is_absent and not x.is_leave)
            normal_days = self.get_normal_days(employee, date_from, date_to)
            expected_hours = self.get_expected_hours(employee, normal_days)
            actual_hours = self.get_normal_times(actual_attendances)
            att_rate = self.get_att_rate(actual_hours, expected_hours)
            for header_item in table_header:
                title = header_item.get("name")
                type = header_item.get("type")
                if title == "Name":
                    employee_list.append(employee.name)
                    continue
                if title == "Acc No":
                    employee_list.append(employee.employee_code)
                    continue
                if title == "Normal":
                    employee_list.append(normal_days)
                    continue
                if title == "Actual":
                    employee_list.append(actual_days)
                    continue
                if title == "Absent":
                    employee_list.append(absent_days)
                    continue
                if title == "Late":
                    employee_list.append(round(sum(actual_attendances.mapped("late_penalty_min"))))
                    continue
                if title == "Early":
                    employee_list.append(round(sum(actual_attendances.mapped("early_penalty_min"))))
                    continue
                if title == "OT":
                    ot_hours = float_round(
                        sum(actual_attendances.mapped("total_ot"))/60, precision_digits=2)
                    employee_list.append(ot_hours)
                    continue
                if title == "AFL":
                    employee_list.append(self.get_AFL(employee, date_from, date_to))
                    continue
                if title == "B Leaves":
                    employee_list.append(self.get_b_leaves(employee, date_from, date_to))
                    continue
                if title == "N/IN":
                    employee_list.append((len(actual_attendances.filtered(lambda x: x.check_in))))
                    continue
                if title == "N/OUT":
                    employee_list.append((len(actual_attendances.filtered(lambda x: x.check_out))))
                    continue
                if title == "Normal Hours":
                    actual_hours = "{0:.2f}".format(actual_hours)
                    employee_list.append(actual_hours)
                    continue
                if type == "leave_hour":
                    leave_name = title
                    employee_list.append(self.get_AFL(employee, date_from, date_to, leave_name=leave_name))
                    continue
                if type == "leave_day":
                    leave_name = title
                    employee_list.append(self.get_b_leaves(employee, date_from, date_to, leave_name=leave_name))
                    continue
                if type == "permission":
                    permission_name = title
                    employee_list.append(self.get_AFL(employee, date_from, date_to, permission_name=permission_name))
                    continue
                if title == "Working Time":
                    employee_list.append(expected_hours)
                    continue
                if title == "ATT Rate":
                    employee_list.append(att_rate)
                    continue
            my_list.append(employee_list)
        return my_list

    def generate_xlsx_report(self, workbook, lines, data=None):

        domain = lines.get("employee_domain")
        model = self.env.context.get('active_model')
        wizard = data
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_from = wizard.date_from
        date_to = wizard.date_to

        table_headers = self.get_header(date_from, date_to)
        has_grouping = False if wizard.grouping_by == "all" else True
        all_attendances = self.get_attendances(wizard, domain)
        attendances = self._add_grouping_by(all_attendances, wizard.grouping_by)

        main_heading = workbook.add_format({
            "bold": 0,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": 'white',
            'font_size': '10',
        })
        main_heading2 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#acadb2',
            'font_size': '12',
        })
        main_heading3 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#ffffff',
            'font_size': '13',
        })
        sheet = workbook.add_worksheet('Employees Payslips')
        sheet.set_column('A2:A2',30)
        sheet.set_column('B:M', 15)
        row = 1
        col = 0
        sheet.merge_range('A1:W1', 'تقرير حضور الموظفين العام', main_heading3)
        row += 1
        sheet.merge_range('A2:W2', 'Employee Attendance General Report', main_heading3)
        row += 2
        # report parameter data
        sheet.write(row, col, 'Date From', main_heading2)
        sheet.write_string(row, col + 1, str(date_from), main_heading)
        sheet.write(row, col + 2, 'Date To', main_heading2)
        sheet.write_string(row, col + 3, str(date_to), main_heading)
        sheet.write(row, col + 4, 'Print Date', main_heading2)
        sheet.write_string(row, col + 5, str(docs.print_date_time.strftime('%Y-%m-%d %H:%M:%S')), main_heading)
        sheet.write(row, col + 6, 'Grouping', main_heading2)
        sheet.write_string(row, col + 7, str(wizard.grouping_by), main_heading)
        row += 3
        # ### report body

        if attendances:
            for header_item in table_headers:
                # rule_name = key.split('+')
                sheet.write_string(row, col, header_item['name'], main_heading2)
                col += 1
            row += 1
            col = 0
            for attendance_list in attendances:
                if has_grouping:
                    sheet.write_string(row, col, attendance_list[0], main_heading2)
                    row += 1
                    col = 0
                summary_lines = self.get_summary_line(table_headers, attendance_list[1], date_from, date_to)
                for line in summary_lines:
                    for summary_value in line:
                        sheet.write_string(row, col, str(summary_value), main_heading)
                        col += 1

                    col = 0
                    row += 1


