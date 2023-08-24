# -*- coding: utf-8 -*-

from odoo import models, fields, api,tools,exceptions, _, SUPERUSER_ID
from odoo import _

class InheritHrEmployee(models.Model):
    _inherit = "hr.employee"

    emp_code_id = fields.Integer(string='Machine Employee ID')
    employee_code = fields.Char("Employee Code")
    
    #@api.multi
    def action_attend_log(self):
        res = self.env['ir.actions.act_window']._for_xml_id('hr_attendance_extender.log_attendance_action')
        view = self.env.ref('hr_attendance_extender.attend_log_tree', False)
        res['views'] = [(view and view.id or False, 'tree')]
        res['domain'] = [('employee_id','=',self.id)]
        return res

    #@api.multi
    def action_attendance(self):
        xes = self.env['ir.actions.act_window'].for_xml_id('hr_attendance', 'hr_attendance_action')
        view = self.env.ref('hr_attendance.view_attendance_tree', False)
        vfrom = self.env.ref('hr_attendance.hr_attendance_view_form', False)
        xes['views'] = [(view and view.id or False, 'tree'),(vfrom and vfrom.id or False,'form')]
        xes['domain'] = [('employee_id', '=', self.id)]
        return xes

    #@api.multi
    def action_attendance_sheet(self):
        sxes = self.env['ir.actions.act_window'].for_xml_id('hr_attendance_extender', 'open_view_attendance_sheet')
        view = self.env.ref('hr_attendance_extender.view_hr_attendance_sheet_tree', False)
        sfrom = self.env.ref('hr_attendance.view_hr_attendance_sheet_form', False)
        sxes['views'] = [(view and view.id or False, 'tree'), (sfrom and sfrom.id or False, 'form')]
        sxes['domain'] = [('employee_id', '=', self.id)]
        return sxes
