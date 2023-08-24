import xlsxwriter
from datetime import timedelta

from odoo import models,fields,api,_
from odoo.exceptions import UserError,ValidationError


class EmployeePermissionReport(models.AbstractModel):
    _name = 'report.hr_attendance_reports.employee_permission_report'

    def get_permissions(self, wizard, employee_domain):
        employees = self.env["hr.employee"].search(employee_domain)
        permission_domain = [("employee_id", "in", employees.ids)]
        if wizard.date_from:
            permission_domain += [("request_date", '>=', wizard.date_from)]
        if wizard.date_to:
            permission_domain += [("request_date", '<=', wizard.date_to)]
        permissions = self.env["hr.permission.request"].search(permission_domain)
        return permissions

    def _add_grouping_by(self, permissions, grouping_by):
        if grouping_by == 'by_branches':
            branches = permissions.mapped("employee_id.branch_id")
            permissions = [[branch.branch_ar_name, permissions.filtered(lambda x: x.employee_id.branch_id == branch)]
                           for branch in branches]
        elif grouping_by == 'by_departments':
            departments = permissions.mapped("employee_id.department_id")
            permissions = [[department.name, permissions.filtered(lambda x: x.employee_id.department_id == department)]
                           for department in departments]
        elif grouping_by == 'by_job_positions':
            jobs = permissions.mapped("employee_id.job_id")
            permissions = [[job.name, permissions.filtered(lambda x: x.employee_id.job_id == job)]
                           for job in jobs]
        else:
            permissions = [["all", permissions],]
        return permissions

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = data.get("employee_domain")
        model = self.env.context.get('active_model')
        wizard = self.env[model].browse(self.env.context.get('active_id'))
        all_permissions = self.get_permissions(wizard, domain)
        permissions = self._add_grouping_by(all_permissions, wizard.grouping_by)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'permissions': permissions,
            'dates': [wizard.date_from, wizard.date_to],
            'docs': wizard
        }