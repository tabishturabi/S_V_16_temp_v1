#-*- coding:utf-8 -*-
 
# Part of Odoo. See LICENSE file for full copyright and licensing details.
 
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from odoo import api, fields, models
from odoo import exceptions, _
# from pkg_resources.extern import names
 
 
class LcReport(models.AbstractModel):
	_name = 'report.payments_enhanced.report_collection' #report.modulename.your_modelname of report
	_description = "report_payments_enhanced_report_collection"
  
	def _get_report_values(self, docids, data=None):
		
		report = self.env['ir.actions.report']._get_report_from_name('payments_enhanced.report_collection')
		return {
				'doc_ids': docids,
				'doc_model': report.model,
				'docs': self.env[report.model].browse(docids),
				'report_type': data.get('report_type') if data else '',
			}
	   

#     def render_html(self, docids, data=None):
#        
#                           
#               
#           
# #         docargs = {
# #                 'encash_ids':encash_rec,
# #                 'emp_id':emp_list,
# #                 'dept':depart_list,
# #                                  
# #             }
#         return self.env['ir.actions.report']._get_report_from_name('payments_enhanced.report_collection','docargs')
	   

