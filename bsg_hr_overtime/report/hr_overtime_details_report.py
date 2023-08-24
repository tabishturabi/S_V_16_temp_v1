# -*- coding: utf-8 -*-

import time
from odoo import  api, fields, models,_
from odoo.exceptions import ValidationError



class OvertimeDetailedReport(models.AbstractModel):
    _name = 'report.bsg_hr_overtime.overtime_details_report_template'
   
    def get_month(self, date_from):
      return fields.Datetime.from_string(date_from).strftime('%B %Y')

  

    @api.model
    def _get_report_values(self, docids, data=None):
        mode = data['form']['mode']
        department_ids = data['form']['department_ids']
        branch_ids = data['form']['branch_ids']
        company_ids = data['form']['company_ids']
        employee_tag_ids = data['form']['employee_tag_ids']
        employee_ids = data['form']['employee_ids']
        group_by_mode = data['form']['group_by_mode']
        state = data['form']['state']
        date_from = data['form']['date_from']
        date_to  = data['form']['date_to']
        date_condition = data['form']['date_condition']
        create_by = data['form']['create_by']
        emp_overtime_batch_ids = data['form']['emp_overtime_batch_ids']
        emp_overtime_batch_by_hours_ids = data['form']['emp_overtime_batch_by_hours_ids']
        emp_overtime = data['form']['emp_overtime']


        domain = []
        date_domain = []
        if emp_overtime_batch_ids:
            domain +=[('emp_overtime_batch','in',emp_overtime_batch_ids)]
        if emp_overtime_batch_by_hours_ids:
            domain +=[('emp_overtime_batch_by_hours','in',emp_overtime_batch_by_hours_ids)]     
        if emp_overtime:
            domain +=[('id','in',emp_overtime)]        
        if department_ids:
               domain +=[('emp_department','in',department_ids)]
        if branch_ids:
               domain +=[('branch_name','in',branch_ids)]
        if employee_tag_ids:
               domain +=[('employee_tag_ids','in',employee_tag_ids)]
        if employee_ids:
               domain +=[('employee_name','in',employee_ids)]
        if state:
               domain +=[('state','in',self.env['overt.report.wizard.state'].sudo().browse(state).mapped('value'))]   
        if data['form']['report_type'] == 'total':                
            if date_condition == 'equal':
                domain += [('date_from','=',date_from),('date_to','=',date_to)] 
            if date_condition == 'not_equal': 
                domain += [('date_from','!=',date_from),('date_to','!=',date_to)] 
            if date_condition == 'after':
                domain += [('date_from','>',date_from),('date_to','>',date_to)]
            if date_condition == 'before':
                domain += [('date_from','<',date_from),('date_to','<',date_to)]
            if date_condition == 'after_equal':
                domain += [('date_from','>=',date_from),('date_to','>=',date_to)]
            if date_condition == 'before_equal': 
                domain += [('date_from','<=',date_from),('date_to','<=',date_to)] 
            if date_condition == 'between':
                domain += [('date_from','>=',date_from),('date_to','<=',date_to)] 
        if data['form']['report_type'] == 'detail': 
            if date_condition == 'equal':
                date_domain += [('from_date','=',date_from),('to_date','=',date_to)] 
            if date_condition == 'not_equal': 
                date_domain += [('from_date','!=',date_from),('to_date','!=',date_to)] 
            if date_condition == 'after':
                date_domain += [('from_date','>',date_from),('to_date','>',date_to)]
            if date_condition == 'before':
                date_domain += [('from_date','<',date_from),('to_date','<',date_to)]
            if date_condition == 'after_equal':
                date_domain += [('from_date','>=',date_from),('to_date','>=',date_to)]
            if date_condition == 'before_equal': 
                domain += [('from_date','<=',date_from),('to_date','<=',date_to)] 
            if date_condition == 'between':
                date_domain += [('from_date','>=',date_from),('to_date','<=',date_to)]  
            if(len(date_domain) > 0):
                overtime_line_ids = self.env['hr.overtime.line'].search(date_domain)
                domain += [('overtime_line','in',overtime_line_ids.ids)]
                         
        if create_by:
            domain +=[('create_uid','=',create_by)]
        records = self.env['hr.overtime'].search(domain)
        if not records:
           raise ValidationError(_('There Is No Match Overtime Data'))        
        domain = []    
        if  group_by_mode == 'by_employee':
            if  employee_ids:
                domain = [('id','in',employee_ids)] 
            grouping = self.env['hr.employee'].search(domain) 
        if  group_by_mode == 'by_branch': 
            if branch_ids:
               domain = [('id','in',branch_ids)]
            grouping = self.env['bsg_branches.bsg_branches'].search(domain)
        if  group_by_mode == 'by_department':   
            if department_ids:
               domain = [('id','in',department_ids)] 
            grouping =  self.env['hr.department'].search(domain)    
        overtime_date = {}
        for group in grouping:
            if group_by_mode == 'by_branch':
                group_name = group.branch_name
                overtime_ids = records.filtered(lambda rec: rec.branch_name.id == group.id)
            if  group_by_mode == 'by_employee':
                group_name = group.name
                overtime_ids = records.filtered(lambda rec: rec.employee_name.id == group.id)
            if  group_by_mode == 'by_department': 
                group_name = group.name
                overtime_ids = records.filtered(lambda rec: rec.emp_department.id == group.id ) 
            if overtime_ids:
                overtime_date[group_name] = overtime_ids      

        docargs = {}
        docargs['employee_data'] = overtime_date
        docargs['doc_ids'] = self.ids
        docargs['doc_model'] = self
        docargs['data'] = data
        docargs ['date_from'] =date_from
        docargs ['date_to'] = date_to
        docargs['date_condition'] = date_condition
        docargs['user'] = self.env.user
        
        
        return docargs
