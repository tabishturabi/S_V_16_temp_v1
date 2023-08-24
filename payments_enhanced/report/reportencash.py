#-*- coding:utf-8 -*-
 
# Part of Odoo. See LICENSE file for full copyright and licensing details.
 
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from odoo import api, fields, models
from odoo import exceptions, _
from pkg_resources.extern import names
 
 
class LcReport(models.AbstractModel):
    _name = 'report.out_leave_form.report_encash' #report.modulename.your_modelname of report
 
  
    def render_html(self, docids, data=None):
        encash_rec = self.env['employee.encash'].search([('id','in',docids)])
        
        
    
        emp_list=[]
        list_sum = {} #{['dep':'somvallue','emp_count':1].[.......]}
        depart_list=[]
        dep_name = ''
        salary=0
        amount=0
        amt_sum = 0
        count_emp =0
        perce =0
        if(len(encash_rec) >= 1):
            for e in encash_rec:
                for e_dep in e.dep:
                    dep_name = ''
                    count_emp =0
                    amt_sum = 0
                    count_emp =0
                    salary=0
                    for d in e_dep:
                        names = self.env['hr.employee'].search([('department_id','in',[d.id])])
                        if(len(names) >=1):
                            for ne in names:
                                count_emp = count_emp+1
                                salary = salary + ne.contract_id.wage
                                emp_list.append((ne))
                                if(dep_name == ''): #dep shd come on once
                                    dep_name = d.name
                                    
                                for ech in e.encash_line:
                                    if(ech.emp_name == ne.name):
                                        amount = round((ne.contract_id.wage/30.42)*ech.cash)
                                        amt_sum = amt_sum + amount
                        else:
                            emp_list.append((names))
                            salary = salary + names.contract_id.wage
                            if(dep_name == ''):
                                dep_name = d.name
                                count_emp = count_emp+1
                            
                            for ech in e.encash_line:
                                    if(ech.emp_name == names.name):
                                        amount = round((names.contract_id.wage/30.42)*ech.cash)
                                        amt_sum = amt_sum + amount
                    if(amt_sum != 0):
                        perce = (amt_sum/salary)*100
                    depart_list.append({'Department':dep_name,'Empcount':count_emp,'Salary':salary,'Amount':amt_sum,'Percentage':str(perce)+'%'})

        else:
            names = self.env['hr.employee'].search([('department_id','in',[encash_rec.dep.id])])
            for e in names:
                emp_list.append((e))  
                
                    
           
        
#         for e in encash_rec:
#                 for ed in names:
#                     for edp in e.dep:
#                         if(ed.department_id.id==edp.dep.id):
#                             depart_list.append(ed)
                 
                          
              
          
        docargs = {
                'encash_ids':encash_rec,
                'emp_id':emp_list,
                'dept':depart_list,
                                 
            }
        return self.env['report'].render('out_leave_form.report_encash',docargs)
       


