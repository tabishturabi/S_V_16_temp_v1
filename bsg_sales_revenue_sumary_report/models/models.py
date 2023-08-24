# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class SalesRevenueReportWizard(models.TransientModel):
    _name = 'sales.revenue.report.wizard'

    grouping_by = fields.Selection([('all','All'),('by_branches_cls','Sales Revenue Summary Report Group By Branch Classification'),
                                    ('by_company','Sales Revenue Summary Report Group By Company'),
                                    ('by_region','Sales Revenue Summary Report Group By Region'),
                                    ('by_branch', 'Sales Revenue Summary Report Group By Branch'),
                                    ('by_create_by','Sales Revenue Summary Report Group By Create By'),
                                    ('by_partner_type','Sales Revenue Summary Report Group By Partner Type'),
                                    ('by_agreement_type','Sales Revenue Summary Report Group By Agreement Type'),
                                    ('by_car_size','Sales Revenue Summary Report Group By Car Size'),
                                    ('by_car_maker', 'Sales Revenue Summary Report Group By Car Maker'),
                                    ('by_shipment_type','Sales Revenue Summary Report Group By Shipment Type'),
                                    ('by_manufacture_year','Sales Revenue Summary Report Group By Manufacturing Year'),
                                    ('by_pricelist', 'Sales Revenue Summary Report Group By Pricelist'),
                                    ('by_order_date', 'Sales Revenue Summary Report Group By Order Date'),],required=True,string='Grouping By',default="all")
    order_date_condition = fields.Selection([('all', 'All'), ('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
                                              ('is_after', 'is after'), ('is_before', 'is before'),
                                              ('is_after_or_equal_to', 'is after or equal to'),
                                              ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
                                              ('is_set', 'is set'), ('is_not_set', 'is not set')], required=True, string='Order Date Condition',default='all')
    period_grouping_by = fields.Selection([('day', 'Day'),('weekly', 'Weekly'),('month', 'Month'),('quarterly', 'Quarterly'),('year', 'Year'),], string='Period Grouping By')
    date_from = fields.Datetime(string='From')
    date_to = fields.Datetime(string='To')
    order_date = fields.Datetime(string='Order Date')
    region_ids = fields.Many2many('region.config', string='Region')
    from_branch_ids = fields.Many2many('bsg_branches.bsg_branches','revenue_from_branch_rel','revenue_id','from_branch_id',string='From Branch')
    to_branch_ids = fields.Many2many('bsg_branches.bsg_branches','revenue_to_branch_rel', 'revenue_id','to_branch_id', string='To Branch')
    branch_cls_ids = fields.Many2many('bsg.branch.classification', string='Branch Classification')
    company_ids = fields.Many2many('res.company',string='Company')
    partner_type_ids = fields.Many2many('partner.type', string='Partner Type')
    shipment_type_ids = fields.Many2many('bsg.car.shipment.type',string='Shipment Type')
    create_user_ids = fields.Many2many('res.users',string='Create By')
    payment_method_ids = fields.Many2many('cargo_payment_method', string='Payment Method')
    sale_type = fields.Selection([('all', 'All'),('local', 'Local'),('international', 'International')],required=True,default='all' ,string='Sale Type')
    agreement_type = fields.Selection([('round_trip', 'Round Trip'), ('one_way', 'One Way')],string='Agreement Type')
    car_size_ids = fields.Many2many('bsg_car_size',string='Car Size')
    include_salath = fields.Boolean(string='Include Satha Only')
    car_maker_ids = fields.Many2many('bsg_car_config', string='Car Maker')
    shipment_status = fields.Selection([('all', 'All'),('shiped', 'Shiped'),('unshiped', 'Unshipped')],required=True,default='all' ,string='Shipment Status')
    manufacture_year_ids = fields.Many2many('bsg.car.year', string='Manufacturing Year')
    pricelist_ids = fields.Many2many('product.pricelist', string='Pricelist')



    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_sales_revenue_sumary_report.sales_revenue_report_pdf_id').report_action(self,data=data)



