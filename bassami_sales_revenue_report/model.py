#-*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    OpenERP, Open Source Management Solution                                        ##
##    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved       ##
##                                                                                    ##
##    This program is free software: you can redistribute it and/or modify            ##
##    it under the terms of the GNU Affero General Public License as published by     ##
##    the Free Software Foundation, either version 3 of the License, or               ##
##    (at your option) any later version.                                             ##
##                                                                                    ##
##    This program is distributed in the hope that it will be useful,                 ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of                  ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   ##
##    GNU Affero General Public License for more details.                             ##
##                                                                                    ##
##    You should have received a copy of the GNU Affero General Public License        ##
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.           ##
##                                                                                    ##
########################################################################################
########################################################################################

from odoo import api, models, fields
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning

class BranchesLedgerReportSalesRevenue(models.AbstractModel):
	_name = 'report.bassami_sales_revenue_report.sales_revenue_id'

	@api.model
	def _get_report_values(self, docids, data=None):
		model = self.env.context.get('active_model')
		record_wizard = self.env[model].browse(self.env.context.get('active_id'))

		
		form = record_wizard.form
		to = record_wizard.to
		partner_types = record_wizard.partner_types
		service_type = record_wizard.service_type
		branch_from = record_wizard.branch_from
		user_branch = record_wizard.user_branch
		service_filter = record_wizard.service_filter
		branch_filter = record_wizard.branch_filter
		user_filter = record_wizard.user_filter


		if service_filter == 'all':
			service_data = self.env['product.template'].search([])
		else:
			service_data = []
			for ser in service_type:
				service_data.append(ser)

		if user_filter == 'all':
			user_data = self.env['bsg_branches.bsg_branches'].search([])
		else:
			user_data = []
			for us in user_branch:
				user_data.append(us)

		if branch_filter == 'all':
			branches_data = self.env['bsg_branches.bsg_branches'].search([])
		else:
			branches_data = []
			for b in branch_from:
				branches_data.append(b)



		main_data = []
		for x in branches_data:
			branch_data = []
			for y in service_data:
				so = []
				so_line = []
				# trans = self.env['bsg_vehicle_cargo_sale_line'].search([('bsg_cargo_sale_id.order_date','>=',form),('bsg_cargo_sale_id.order_date','<=',to),('loc_from_branch_id.id','=',x.id),('service_type.id','=',y.id),('bsg_cargo_sale_id.state','!=','draft'),('bsg_cargo_sale_id.partner_types.id','=',partner_types.id)])
				trans = self.env['bsg_vehicle_cargo_sale_line'].search([])
				for line in trans:
					if user_filter == 'specific':
						if user_branch.id in line.bsg_cargo_sale_id.user_id.user_branch_ids:
							if line.bsg_cargo_sale_id.payment_method.payment_type in ['cash']:
								for data in line.bsg_cargo_sale_id.invoice_ids:
									if data.state == 'paid':
										if line not in so_line:
											so_line.append(line)
										if line.bsg_cargo_sale_id not in so:
											so.append(line.bsg_cargo_sale_id)
							else:
								if line not in so_line:
									so_line.append(line)
								if line.bsg_cargo_sale_id not in so:
									so.append(line.bsg_cargo_sale_id)

					else:
						for rec in line.bsg_cargo_sale_id.user_id.user_branch_ids:
							if rec in user_data:
								if line.bsg_cargo_sale_id.payment_method.payment_type in ['cash']:
									for data in line.bsg_cargo_sale_id.invoice_ids:
										if data.state == 'paid':
											if line not in so_line:
												so_line.append(line)
											if line.bsg_cargo_sale_id not in so:
												so.append(line.bsg_cargo_sale_id)
								else:
									if line not in so_line:
										so_line.append(line)
									if line.bsg_cargo_sale_id not in so:
										so.append(line.bsg_cargo_sale_id)


				if len(so_line) > 0 or len(so) > 0:
					tot_amt = 0
					tot_amt_tax = 0
					tot_amt_paid = 0
					for s in so:
						tot_amt = tot_amt + (s.total_amount - s.tax_amount_total)
						tot_amt_tax = tot_amt_tax + s.total_amount
						for i in s.invoice_ids:
							tot_amt_paid = tot_amt_paid + (i.amount_total - i.amount_residual)


					branch_data.append({
						'name': y.name,
						'so': len(so),
						'so_line':len(so_line),
						'partner_type':partner_types.name,
						'tot_amt_paid':tot_amt_paid,
						'tot_amt_tax':tot_amt_tax,
						'tot_amt_paid':tot_amt_paid,

						})

			if len(branch_data) > 0:
				main_data.append({
                    'name': x.branch_ar_name,
                    'number': x.branch_no,
					'branch_data':branch_data,
                    })

		revenue_report = self.env['ir.actions.report']._get_report_from_name('bassami_sales_revenue_report.sales_revenue_id')
		holidays = self.env['hr.leave'].browse(self.ids)
		return {
			'doc_ids': self.ids,
			'doc_model': revenue_report.model,
			'form': form,
			'to': to,
			'main_data': main_data,
			'docs':record_wizard
		}

		# return report_obj.render('partner_ledger_sugar.partner_ledger_report', docargs)