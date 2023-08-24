# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools ,  _
from odoo.exceptions import ValidationError
import base64 ,babel
import os
from datetime import datetime
from datetime import *
from io import BytesIO

import xlsxwriter
from PIL import Image as Image
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from xlsxwriter.utility import xl_rowcol_to_cell

class OvertimeDetailedReportWizardState(models.Model):
    _name = 'overt.report.wizard.state'
    _description = "Overtime Report Wizard State"

    name = fields.Char(string='State')
    value = fields.Char(required=True)

class OvertimeDetailedReportWizard(models.TransientModel):

    _name = 'overtime.detailed.report.wizard'
    _description = "Overtime Report Wizard"


    mode = fields.Selection([('by_employee','Specific Employee'),('by_branch','By Branch'),('by_department','By Department'),
    ('by_company','By Company'),('by_employee_tag','By Employee Tag')],default='by_branch',string='Mode')
    department_ids = fields.Many2many('hr.department',string='Department')
    branch_ids = fields.Many2many('bsg_branches.bsg_branches',string='Branch')
    company_ids = fields.Many2many('res.company',string='Company')
    employee_tag_ids = fields.Many2many('hr.employee.category',string='Employee Tag')
    employee_ids = fields.Many2many('hr.employee')
    group_by_mode = fields.Selection([('by_employee','by Employee'),('by_branch','By Branch'),('by_department','By Department')],default='by_branch',string='Grouping By')
    state = fields.Many2many('overt.report.wizard.state')
    date_from = fields.Datetime('From')
    date_to = fields.Datetime('To')
    date_condition = fields.Selection([('equal','is equal to'),('not_equal','is not equal'),('after','is after'),
    ('before','is before'),('after_equal','is after or equal to'),('before_equal','is after or equal to'),
    ('between','is between'),('set','is set')],default='set',srting='Overtime Date Condition') 
    create_by = fields.Many2many('res.users') 
    report_type = fields.Selection([('detail', 'Detail Report'),('total','Total')], string='Report Type',default='total')
    emp_overtime_batch_ids = fields.Many2many('hr.employee.overtime',string='Overtime Batch Req. No')
    emp_overtime_batch_by_hours_ids = fields.Many2many('hr.employee.overtime.by.hours','wizard_hour_batch_rel','wiz_id','batch_id',string='Overtime Total Hours Batch Req. No')
    emp_overtime = fields.Many2many('hr.overtime',string='Overtime Req. No')

    
    @api.constrains('date_from','date_to')
    def _constrains_dates(self):
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValidationError(_('Sorry, To Date Must Be After From Date'))


    @api.onchange('emp_overtime_batch_ids')
    def _onchange_emp_overtime_batch_ids(self):
        if self.emp_overtime_batch_ids:
            return{'domain':{'emp_overtime':[('emp_overtime_batch','in',self.emp_overtime_batch_ids.ids)]}}
        else:return{'domain':{'emp_overtime':[]}}    

    @api.onchange('emp_overtime_batch_by_hours_ids')
    def _onchange_emp_overtime_batch_by_hours_ids(self):
        if self.emp_overtime_batch_by_hours_ids:
            return{'domain':{'emp_overtime':[('emp_overtime_batch_by_hours','in',self.emp_overtime_batch_by_hours_ids.ids)]}}            
        else:return{'domain':{'emp_overtime':[]}}
        
    def print_report_pdf(self, data):
        
        data['form']=self.read([])[0]
        return self.env.ref('bsg_hr_overtime.overtime_details_action_report').report_action(
            self, data=data)     


    def _get_data_by_domain(self):
        domain = []
        date_domain = []
        if self.emp_overtime_batch_ids:
            domain +=[('emp_overtime_batch','in',self.emp_overtime_batch_ids.ids)]
        if self.emp_overtime_batch_by_hours_ids:
            domain +=[('emp_overtime_batch_by_hours','in',self.emp_overtime_batch_by_hours_ids.ids)]     
        if self.emp_overtime:
            domain +=[('id','in',self.emp_overtime.ids)]
        if self.department_ids:
               domain +=[('emp_department','in',(self.department_ids.ids))]
        if self.branch_ids:
               domain +=[('branch_name','in',(self.branch_ids.ids))]
        if self.employee_tag_ids:
               domain +=[('employee_tag_ids','in',(self.employee_tag_ids.ids))]
        if self.employee_ids:
               domain +=[('employee_name','in',(self.employee_ids.ids))]
        if self.state:
               domain +=[('state','in',self.state.mapped('value'))] 
        if self.report_type == 'total':                  
            if self.date_condition == 'equal':
                domain += [('date_from','=',fields.Datetime.to_string(self.date_from)),('date_to','=',fields.Datetime.to_string(self.date_to))] 
            if self.date_condition == 'not_equal': 
                domain += [('date_from','!=',fields.Datetime.to_string(self.date_from)),('date_to','!=',fields.Datetime.to_string(self.date_to))] 
            if self.date_condition == 'after':
                domain += [('date_from','>',fields.Datetime.to_string(self.date_from)),('date_to','>',fields.Datetime.to_string(self.date_to))]
            if self.date_condition == 'before':
                domain += [('date_from','<',fields.Datetime.to_string(self.date_from)),('date_to','<',fields.Datetime.to_string(self.date_to))]
            if self.date_condition == 'after_equal':
                domain += [('date_from','>=',fields.Datetime.to_string(self.date_from)),('date_to','>=',fields.Datetime.to_string(self.date_to))]
            if self.date_condition == 'before_equal': 
                domain += [('date_from','<=',fields.Datetime.to_string(self.date_from)),('date_to','<=',fields.Datetime.to_string(self.date_to))] 
            if self.date_condition == 'between':
                domain += [('date_from','>=',fields.Datetime.to_string(self.date_from)),('date_to','<=',fields.Datetime.to_string(self.date_to))]     
        if self.report_type == 'detail':
            if self.date_condition == 'equal':
                date_domain += [('from_date','=',fields.Datetime.to_string(self.date_from)),('to_date','=',fields.Datetime.to_string(self.date_to))] 
            if self.date_condition == 'not_equal': 
                date_domain += [('from_date','!=',fields.Datetime.to_string(self.date_from)),('to_date','!=',fields.Datetime.to_string(self.date_to))] 
            if self.date_condition == 'after':
                date_domain += [('from_date','>',fields.Datetime.to_string(self.date_from)),('to_date','>',fields.Datetime.to_string(self.date_to))]
            if self.date_condition == 'before':
                date_domain += [('from_date','<',fields.Datetime.to_string(self.date_from)),('to_date','<',fields.Datetime.to_string(self.date_to))]
            if self.date_condition == 'after_equal':
                date_domain += [('from_date','>=',fields.Datetime.to_string(self.date_from)),('to_date','>=',fields.Datetime.to_string(self.date_to))]
            if self.date_condition == 'before_equal': 
                date_domain += [('from_date','<=',fields.Datetime.to_string(self.date_from)),('to_date','<=',fields.Datetime.to_string(self.date_to))] 
            if self.date_condition == 'between':
                date_domain += [('from_date','>=',fields.Datetime.to_string(self.date_from)),('to_date','<=',fields.Datetime.to_string(self.date_to))]     
            if self.create_by:
                domain +=[('create_uid','=',self.create_by.id)]
            if(len(date_domain) > 0):
                overtime_line_ids = self.env['hr.overtime.line'].search(date_domain)
                domain += [('overtime_line','in',overtime_line_ids.ids)]
        if self.create_by:
            domain +=[('create_uid','=',self.create_by.id)]
            
        overtime_ids = self.env['hr.overtime'].search(domain) 
        return overtime_ids

    def get_line_by_data_range(self,overtime_rel):
            date_domain = [('overtime_rel','=',overtime_rel.id)]
            if self.date_condition == 'equal':
                date_domain += [('from_date','=',fields.Datetime.to_string(self.date_from)),('to_date','=',fields.Datetime.to_string(self.date_to))] 
            if self.date_condition == 'not_equal': 
                date_domain += [('from_date','!=',fields.Datetime.to_string(self.date_from)),('to_date','!=',fields.Datetime.to_string(self.date_to))] 
            if self.date_condition == 'after':
                date_domain += [('from_date','>',fields.Datetime.to_string(self.date_from)),('to_date','>',fields.Datetime.to_string(self.date_to))]
            if self.date_condition == 'before':
                date_domain += [('from_date','<',fields.Datetime.to_string(self.date_from)),('to_date','<',fields.Datetime.to_string(self.date_to))]
            if self.date_condition == 'after_equal':
                date_domain += [('from_date','>=',fields.Datetime.to_string(self.date_from)),('to_date','>=',fields.Datetime.to_string(self.date_to))]
            if self.date_condition == 'before_equal': 
                date_domain += [('from_date','<=',fields.Datetime.to_string(self.date_from)),('to_date','<=',fields.Datetime.to_string(self.date_to))] 
            if self.date_condition == 'between':
                date_domain += [('from_date','>=',fields.Datetime.to_string(self.date_from)),('to_date','<=',fields.Datetime.to_string(self.date_to))]
            overtime_line_ids = self.env['hr.overtime.line'].search(date_domain)
            return overtime_line_ids

    def print_report_excel(self, data):
        records = self._get_data_by_domain()
        locale = data['lang'] or 'en_US'
        if not records:
           raise ValidationError(_('There Is No Match Overtime Data'))
        domain = []    
        if  self.group_by_mode == 'by_employee':
            if  self.employee_ids:
                domain = [('id','in',(self.employee_ids.ids))] 
            grouping = self.env['hr.employee'].search(domain) 
            return self.get_employee_item_data(grouping,records,locale)
        if  self.group_by_mode == 'by_branch': 
            if self.branch_ids:
               domain = [('id','in',(self.branch_ids.ids))]
            grouping = self.env['bsg_branches.bsg_branches'].search(domain) 
            return self.get_branch_item_data(grouping,records,locale)
        if  self.group_by_mode == 'by_department':   
            if self.department_ids:
               domain = [('id','in',(self.department_ids.ids))] 
            grouping =  self.env['hr.department'].search(domain)    
            return self.get_department_item_data(grouping,records,locale)   


    def get_department_item_data(self,grouping,records,locale):
        file_name = _('overtime_report.xlsx')
        fp = BytesIO()

        workbook = xlsxwriter.Workbook(fp)
        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 14,
                                              'bg_color':'gray','font_color':'white'})
        cell_text_format_n = workbook.add_format({'align': 'center',
                                                  'bold': True, 'size': 9,
                                                  'bg_color': '#F1F1F1','font_color':'#454748'
                                                  })
        cell_text_format = workbook.add_format({'align': 'center',
                                                'bold': True, 'size': 9,
                                                'bg_color': '#F1F1F1','font_color':'#454748'
                                                })
        heading_format.set_border()
        cell_text_format_n.set_border()
        heading_format.set_align('center')

        cell_text_format.set_border()
        cell_text_format_new = workbook.add_format({'align': 'left',
                                                    'size': 9,
                                                    })
        cell_text_format_new.set_border()
        cell_number_format = workbook.add_format({'align': 'right',
                                                  'bold': False, 'size': 9,
                                                  'num_format': '#,###0.00',
                                                  'bg_color': '#F1F1F1','font_color':'#454748'})
        cell_number_format.set_border()
        worksheet = workbook.add_worksheet('overtime_report.xlsx')
        normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,###0.00', 'size': 9,'bg_color': '#F1F1F1','font_color':'#454748' })
        normal_num_bold.set_border()
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:M', 20)
        worksheet.set_column('N:N', 20)
        row = 4
        column = 0
        worksheet.merge_range('A1:F2',self.env.user.company_id.name, heading_format)
        worksheet.merge_range('B4:D4',_('Department of Human Ressources'), cell_text_format_n)
        worksheet.merge_range('B5:D5',_('Overtime statement'), cell_text_format_n)
        worksheet.merge_range('B6:D6',_('Printing Date %s')%(fields.Date.today()), cell_text_format_n)
                     
        for dept in grouping:
            overtime_ids = records.filtered(lambda rec: rec.emp_department.id == dept.id )
            if overtime_ids:
                row += 3
                #worksheet.write(row, 4, 'Department', heading_format)
                worksheet.write(row, 3, dept.name or '',heading_format)
                row += 2
                worksheet.write(row, 0, _('Sequence'), cell_text_format)
                worksheet.write(row, 1, _('Employee'), cell_text_format)
                worksheet.write(row, 2, _('Month'), cell_text_format)
                worksheet.write(row, 3, _('Type'), cell_text_format)
                worksheet.write(row, 4, _('Total Salary'), cell_text_format)
                worksheet.write(row, 5, _('Hours'), cell_text_format)
                worksheet.write(row, 6, _('Total Overtime Amount'), cell_text_format)
                worksheet.write(row, 7, _('Notes'), cell_text_format)
                row_set = row
                row += 1
                col = 0
                ro = row
                 
                if self.report_type == 'detail':
                    for overtime in overtime_ids:
                        for line in self.get_line_by_data_range(overtime):
                            sequence =overtime.sequence_number
                            employee = overtime.employee_name.name
                            hours = line.total_overtime
                            overtime_month = tools.ustr(babel.dates.format_date(date=overtime.date_from, format='MMMM y', locale=locale))
                            ovt_name = overtime.name
                            line_description = line.description
                            wage_sallary = overtime.wage_sallary
                            total_overtime = line.total_overtime_amount



                            worksheet.write(ro, col, sequence or '', cell_text_format_new)
                            worksheet.write(ro, col + 1, employee or '', cell_text_format_new)
                            worksheet.write(ro, col + 2, overtime_month or '', cell_text_format_new)
                            worksheet.write(ro, col + 3, ovt_name or '', cell_text_format_new)
                            worksheet.write(ro, col + 4, wage_sallary or '', cell_text_format_new)
                            worksheet.write(ro, col + 5, hours or '', cell_text_format_new)
                            worksheet.write(ro, col + 6, total_overtime or '', cell_text_format_new)
                            worksheet.write(ro, col + 7, line_description or '', cell_text_format_new)
                            ro = ro + 1
                elif self.report_type == 'total':
                    for overtime in overtime_ids:
                        sequence = overtime.sequence_number
                        employee = overtime.employee_name.name
                        hours = sum(overtime.overtime_line.mapped('total_overtime'))
                        overtime_month = tools.ustr(babel.dates.format_date(date=overtime.date_from, format='MMMM y', locale=locale))
                        ovt_name = overtime.name
                        description = overtime.description
                        wage_sallary = overtime.wage_sallary
                        total_overtime = sum(overtime.overtime_line.mapped('total_overtime_amount'))



                        worksheet.write(ro, col, sequence or '', cell_text_format_new)
                        worksheet.write(ro, col + 1, employee or '', cell_text_format_new)
                        worksheet.write(ro, col + 2, overtime_month or '', cell_text_format_new)
                        worksheet.write(ro, col + 3, ovt_name or '', cell_text_format_new)
                        worksheet.write(ro, col + 4, wage_sallary or '', cell_text_format_new)
                        worksheet.write(ro, col + 5, hours or '', cell_text_format_new)
                        worksheet.write(ro, col + 6, total_overtime or '', cell_text_format_new)
                        worksheet.write(ro, col + 7, description or '', cell_text_format_new)
                        ro = ro + 1            
                #col = col + 3
                #colm = col
                row = ro
                worksheet.write(row, 0, _('Grand Total'), cell_text_format)
                #calculating sum of columnn
                roww = row
                #Sum Of wage_sallary
                cell1 = xl_rowcol_to_cell(row_set + 1, 4)
                cell2 = xl_rowcol_to_cell(row - 1, 4)
                worksheet.write_formula(row, 4, '{=SUM(%s:%s)}' % (cell1, cell2), normal_num_bold)
                
                #Sum Of hours
                cell1 = xl_rowcol_to_cell(row_set + 1, 5)
                cell2 = xl_rowcol_to_cell(row - 1, 5)
                worksheet.write_formula(row, 5, '{=SUM(%s:%s)}' % (cell1, cell2), normal_num_bold)
                #Sum Of Total Overtime
                cell1 = xl_rowcol_to_cell(row_set + 1, 6)
                cell2 = xl_rowcol_to_cell(row - 1, 6)
                worksheet.write_formula(row, 6, '{=SUM(%s:%s)}' % (cell1, cell2), normal_num_bold)
                #Set Empty Value For Colum
                worksheet.write(row, 1, '', cell_text_format)
                worksheet.write(row, 2, '', cell_text_format)
                worksheet.write(row, 3, '', cell_text_format)
                worksheet.write(row, 7, '', cell_text_format)

        workbook.close()
        file_download = base64.b64encode(fp.getvalue())
        fp.close()
        self = self.with_context(default_name=file_name, default_file_download=file_download)

        return {
            'name': 'Overtime report Download',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'overtime.detail.report.excel',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
        }


    def get_branch_item_data(self,grouping,records,locale):
        file_name = _('overtime_report.xlsx')
        fp = BytesIO()

        workbook = xlsxwriter.Workbook(fp)
        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 14,
                                              'bg_color':'gray','font_color':'white'})
        cell_text_format_n = workbook.add_format({'align': 'center',
                                                  'bold': True, 'size': 9,
                                                  'bg_color': '#F1F1F1','font_color':'#454748'
                                                  })
        cell_text_format = workbook.add_format({'align': 'center',
                                                'bold': True, 'size': 9,
                                                'bg_color': '#F1F1F1','font_color':'#454748'
                                                })
        heading_format.set_border()
        cell_text_format_n.set_border()
        heading_format.set_align('center')

        cell_text_format.set_border()
        cell_text_format_new = workbook.add_format({'align': 'left',
                                                    'size': 9,
                                                    })
        cell_text_format_new.set_border()
        cell_number_format = workbook.add_format({'align': 'right',
                                                  'bold': False, 'size': 9,
                                                  'num_format': '#,###0.00',
                                                  'bg_color': '#F1F1F1','font_color':'#454748'})
        cell_number_format.set_border()
        worksheet = workbook.add_worksheet('overtime_report.xlsx')
        normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,###0.00', 'size': 9,'bg_color': '#F1F1F1','font_color':'#454748' })
        normal_num_bold.set_border()
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:M', 20)
        worksheet.set_column('N:N', 20)
        row = 4
        column = 0
        worksheet.merge_range('A1:F2',self.env.user.company_id.name, heading_format)
        worksheet.merge_range('B4:D4',_('Department of Human Ressources'), cell_text_format_n)
        worksheet.merge_range('B5:D5',_('Overtime statement'), cell_text_format_n)
        worksheet.merge_range('B6:D6',_('Printing Date %s')%(fields.Date.today()), cell_text_format_n)
        for branch in grouping:
            overtime_ids = records.filtered(lambda rec: rec.branch_name.id == branch.id)
            if overtime_ids:    
                row += 3
                #worksheet.write(row, 4, 'Branch', heading_format)
                worksheet.write(row, 3, branch.branch_name or '',heading_format)
                row += 2



                worksheet.write(row, 0, _('Sequence'), cell_text_format)
                worksheet.write(row, 1, _('Employee'), cell_text_format)
                worksheet.write(row, 2, _('Month'), cell_text_format)
                worksheet.write(row, 3, _('Type'), cell_text_format)
                worksheet.write(row, 4, _('Total Salary'), cell_text_format)
                worksheet.write(row, 5, _('Hours'), cell_text_format)
                worksheet.write(row, 6, _('Total Overtime Amount'), cell_text_format)
                worksheet.write(row, 7, _('Notes'), cell_text_format)


                row_set = row
                row += 1
                col = 0
                ro = row

                if self.report_type == 'detail':
                    for overtime in overtime_ids:
                        for line in self.get_line_by_data_range(overtime):
                            sequence = overtime.sequence_number
                            employee = overtime.employee_name.name
                            hours = line.total_overtime
                            overtime_month = tools.ustr(babel.dates.format_date(date=overtime.date_from, format='MMMM y', locale=locale))
                            ovt_name = overtime.name
                            line_description = line.description
                            wage_sallary = overtime.wage_sallary
                            total_overtime = line.total_overtime_amount



                            worksheet.write(ro, col, sequence or '', cell_text_format_new)
                            worksheet.write(ro, col + 1, employee or '', cell_text_format_new)
                            worksheet.write(ro, col + 2, overtime_month or '', cell_text_format_new)
                            worksheet.write(ro, col + 3, ovt_name or '', cell_text_format_new)
                            worksheet.write(ro, col + 4, wage_sallary or '', cell_text_format_new)
                            worksheet.write(ro, col + 5, hours or '', cell_text_format_new)
                            worksheet.write(ro, col + 6, total_overtime or '', cell_text_format_new)
                            worksheet.write(ro, col + 7, line_description or '', cell_text_format_new)
                            ro = ro + 1
                elif self.report_type == 'total':
                    for overtime in overtime_ids:
                        sequence = overtime.sequence_number
                        employee = overtime.employee_name.name
                        hours = sum(overtime.overtime_line.mapped('total_overtime'))
                        overtime_month = tools.ustr(babel.dates.format_date(date=overtime.date_from, format='MMMM y', locale=locale))
                        ovt_name = overtime.name
                        description = overtime.description
                        wage_sallary = overtime.wage_sallary
                        total_overtime = sum(overtime.overtime_line.mapped('total_overtime_amount'))



                        worksheet.write(ro, col, sequence or '', cell_text_format_new)
                        worksheet.write(ro, col + 1, employee or '', cell_text_format_new)
                        worksheet.write(ro, col + 2, overtime_month or '', cell_text_format_new)
                        worksheet.write(ro, col + 3, ovt_name or '', cell_text_format_new)
                        worksheet.write(ro, col + 4, wage_sallary or '', cell_text_format_new)
                        worksheet.write(ro, col + 5, hours or '', cell_text_format_new)
                        worksheet.write(ro, col + 6, total_overtime or '', cell_text_format_new)
                        worksheet.write(ro, col + 7, description or '', cell_text_format_new)
                        ro = ro + 1            
                #col = col + 3
                #colm = col
                row = ro
                worksheet.write(row, 0, _('Grand Total'), cell_text_format)
                #calculating sum of columnn
                roww = row
                #Sum Of wage_sallary
                cell1 = xl_rowcol_to_cell(row_set + 1, 4)
                cell2 = xl_rowcol_to_cell(row - 1, 4)
                worksheet.write_formula(row, 4, '{=SUM(%s:%s)}' % (cell1, cell2), normal_num_bold)
                
                #Sum Of hours
                cell1 = xl_rowcol_to_cell(row_set + 1, 5)
                cell2 = xl_rowcol_to_cell(row - 1, 5)
                worksheet.write_formula(row, 5, '{=SUM(%s:%s)}' % (cell1, cell2), normal_num_bold)
                #Sum Of Total Overtime
                cell1 = xl_rowcol_to_cell(row_set + 1, 6)
                cell2 = xl_rowcol_to_cell(row - 1, 6)
                worksheet.write_formula(row, 6, '{=SUM(%s:%s)}' % (cell1, cell2), normal_num_bold)
                #Set Empty Value For Colum
                worksheet.write(row, 1, '', cell_text_format)
                worksheet.write(row, 2, '', cell_text_format)
                worksheet.write(row, 3, '', cell_text_format)
                worksheet.write(row, 7, '', cell_text_format)

        workbook.close()
        file_download = base64.b64encode(fp.getvalue())
        fp.close()
        self = self.with_context(default_name=file_name, default_file_download=file_download)

        return {
            'name': 'Overtime report Download',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'overtime.detail.report.excel',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
        }

    def get_employee_item_data(self,grouping,records,locale):
        file_name = _('overtime_report.xlsx')
        fp = BytesIO()

        workbook = xlsxwriter.Workbook(fp)
        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 14,
                                              'bg_color':'gray','font_color':'white'})
        cell_text_format_n = workbook.add_format({'align': 'center',
                                                  'bold': True, 'size': 9,
                                                  'bg_color': '#F1F1F1','font_color':'#454748'
                                                  })
        cell_text_format = workbook.add_format({'align': 'center',
                                                'bold': True, 'size': 9,
                                                'bg_color': '#F1F1F1','font_color':'#454748'
                                                })
        heading_format.set_border()
        cell_text_format_n.set_border()
        heading_format.set_align('center')

        cell_text_format.set_border()
        cell_text_format_new = workbook.add_format({'align': 'left',
                                                    'size': 9,
                                                    })
        cell_text_format_new.set_border()
        cell_number_format = workbook.add_format({'align': 'right',
                                                  'bold': False, 'size': 9,
                                                  'num_format': '#,###0.00',
                                                  'bg_color': '#F1F1F1','font_color':'#454748'})
        cell_number_format.set_border()
        worksheet = workbook.add_worksheet('overtime_report.xlsx')
        normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,###0.00', 'size': 9,'bg_color': '#F1F1F1','font_color':'#454748' })
        normal_num_bold.set_border()
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:M', 20)
        worksheet.set_column('N:N', 20)
        row = 4
        column = 0
        worksheet.merge_range('A1:F2',self.env.user.company_id.name, heading_format)
        worksheet.merge_range('B4:D4',_('Department of Human Ressources'), cell_text_format_n)
        worksheet.merge_range('B5:D5',_('Overtime statement'), cell_text_format_n)
        worksheet.merge_range('B6:D6',_('Printing Date %s')%(fields.Date.today()), cell_text_format_n)
                     
        for employee in grouping:
            overtime_ids = records.filtered(lambda rec: rec.employee_name.id == employee.id)
            if overtime_ids:
                row += 3
                #worksheet.write(row, 4, 'Employee', heading_format)
                
                worksheet.write(row, 3, employee.name or '',heading_format)
                row += 2



                worksheet.write(row, 0, _('Sequence'), cell_text_format)
                #worksheet.write(row, 1, _('Employee'), cell_text_format)
                worksheet.write(row, 1, _('Month'), cell_text_format)
                worksheet.write(row, 2, _('Type'), cell_text_format)
                worksheet.write(row, 3, _('Total Salary'), cell_text_format)
                worksheet.write(row, 4, _('Hours'), cell_text_format)
                worksheet.write(row, 5, _('Total Overtime Amount'), cell_text_format)
                worksheet.write(row, 6, _('Notes'), cell_text_format)


                row_set = row
                row += 1
                col = 0
                ro = row
                if self.report_type == 'detail':
                    for overtime in overtime_ids:
                        for line in self.get_line_by_data_range(overtime):
                            sequence = overtime.sequence_number
                            employee = overtime.employee_name.name
                            hours = line.total_overtime
                            overtime_month = tools.ustr(babel.dates.format_date(date=overtime.date_from, format='MMMM y', locale=locale))
                            ovt_name = overtime.name
                            line_description = line.description
                            wage_sallary = overtime.wage_sallary
                            total_overtime = line.total_overtime_amount



                            worksheet.write(ro, col, sequence or '', cell_text_format_new)
                            #worksheet.write(ro, col + 1, employee or '', cell_text_format_new)
                            worksheet.write(ro, col + 1, overtime_month or '', cell_text_format_new)
                            worksheet.write(ro, col + 2, ovt_name or '', cell_text_format_new)
                            worksheet.write(ro, col + 3, wage_sallary or '', cell_text_format_new)
                            worksheet.write(ro, col + 4, hours or '', cell_text_format_new)
                            worksheet.write(ro, col + 5, total_overtime or '', cell_text_format_new)
                            worksheet.write(ro, col + 6, line_description or '', cell_text_format_new)
                            ro = ro + 1
                elif self.report_type == 'total':
                    for overtime in overtime_ids:
                        sequence = overtime.sequence_number
                        employee = overtime.employee_name.name
                        hours = sum(overtime.overtime_line.mapped('total_overtime'))
                        overtime_month = tools.ustr(babel.dates.format_date(date=overtime.date_from, format='MMMM y', locale=locale))
                        ovt_name = overtime.name
                        description = overtime.description
                        wage_sallary = overtime.wage_sallary
                        total_overtime = sum(overtime.overtime_line.mapped('total_overtime_amount'))



                        worksheet.write(ro, col, sequence or '', cell_text_format_new)
                        #worksheet.write(ro, col + 1, employee or '', cell_text_format_new)
                        worksheet.write(ro, col + 1, overtime_month or '', cell_text_format_new)
                        worksheet.write(ro, col + 2, ovt_name or '', cell_text_format_new)
                        worksheet.write(ro, col + 3, wage_sallary or '', cell_text_format_new)
                        worksheet.write(ro, col + 4, hours or '', cell_text_format_new)
                        worksheet.write(ro, col + 5, total_overtime or '', cell_text_format_new)
                        worksheet.write(ro, col + 6, description or '', cell_text_format_new)
                        ro = ro + 1            
                #col = col + 3
                #colm = col
                row = ro
                worksheet.write(row, 0, _('Grand Total'), cell_text_format)
                #calculating sum of columnn
                roww = row
                #Sum Of wage_sallary
                cell1 = xl_rowcol_to_cell(row_set + 1, 3)
                cell2 = xl_rowcol_to_cell(row - 1, 3)
                worksheet.write_formula(row, 3, '{=SUM(%s:%s)}' % (cell1, cell2), normal_num_bold)
                
                #Sum Of hours
                cell1 = xl_rowcol_to_cell(row_set + 1, 4)
                cell2 = xl_rowcol_to_cell(row - 1, 4)
                worksheet.write_formula(row, 4, '{=SUM(%s:%s)}' % (cell1, cell2), normal_num_bold)
                #Sum Of Total Overtime
                cell1 = xl_rowcol_to_cell(row_set + 1, 5)
                cell2 = xl_rowcol_to_cell(row - 1, 5)
                worksheet.write_formula(row, 5, '{=SUM(%s:%s)}' % (cell1, cell2), normal_num_bold)
                #Set Empty Value For Colum
                worksheet.write(row, 1, '', cell_text_format)
                worksheet.write(row, 2, '', cell_text_format)
                worksheet.write(row, 6, '', cell_text_format)

        workbook.close()
        file_download = base64.b64encode(fp.getvalue())
        fp.close()
        self = self.with_context(default_name=file_name, default_file_download=file_download)

        return {
            'name': 'Overtime report Download',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'overtime.detail.report.excel',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
        }

class overtime_report_excel(models.TransientModel):
    _name = 'overtime.detail.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('Download overtime', readonly=True)
                           
