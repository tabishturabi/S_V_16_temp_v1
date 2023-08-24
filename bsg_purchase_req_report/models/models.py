# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class PurchaseRequestReportWizard(models.TransientModel):
    _name = 'purchase.req.report.wizard'

    product_ids = fields.Many2many('product.product',string="Product")
    category_ids = fields.Many2many('product.category',string="Category")
    branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branch")
    department_ids = fields.Many2many('hr.department', string="Department")
    request_type = fields.Selection([('stock', 'For Stock'), ('workshop', 'For Workshop'),('branch', 'For Branch')], string='Request Type')
    start_date = fields.Datetime(string='Start Date',required=True)
    end_date = fields.Datetime(string='End Date',required=True)

    has_rfq = fields.Boolean('With RFQ')
    has_po = fields.Boolean('With PO')
    has_iss = fields.Boolean('With ISS')
    has_recieved = fields.Boolean('with Received')

    has_no_rfq = fields.Boolean('Without RFQ')
    has_no_po = fields.Boolean('Without PO')
    has_no_iss = fields.Boolean('Without ISS')
    has_no_recieved = fields.Boolean('Without Received')

    state_filter = fields.Selection([('all', 'All'), ('tsub', 'To Submit'),
        ('tapprove', 'To Approve'),('approve', 'Approved'),
        ('open', 'Open'), ('close', 'Close'),('cancel', 'Cancel'),
        ('reject', 'Reject'),('done', 'Done'),('done_close', 'Done And Close')],string='PR State',required=True,default='all')
    
    pr_groub_by = fields.Selection([('without', 'Without'),('group_by_product', 'Group By Product'),
                                     ('group_by_category', 'Group By Category')],string='PR Group By',required=True,default='without')    
    print_date = fields.Date(string='Today Date', default=fields.date.today())
    is_with_details = fields.Boolean(string="With Details", default=False)

    @api.onchange('has_rfq')
    def _onchange_has_rfq(self):
        if self.has_rfq:
            self.has_no_rfq = False
    @api.onchange('has_po')
    def _onchange_has_po(self):
        if self.has_po:
            self.has_no_po = False
    @api.onchange('has_iss')
    def _onchange_has_iss(self):
        if self.has_iss:
            self.has_no_iss = False
    @api.onchange('has_recieved')
    def _onchange_has_recieved(self):
        if self.has_recieved:
            self.has_no_recieved = False                               


    @api.onchange('has_no_rfq')
    def _onchange_has_no_rfq(self):
        if self.has_no_rfq:
            self.has_rfq = False
    @api.onchange('has_no_po')
    def _onchange_has_no_po(self):
        if self.has_no_po:
            self.has_po = False
    @api.onchange('has_no_iss')
    def _onchange_has_no_iss(self):
        if self.has_no_iss:
            self.has_iss = False
    @api.onchange('has_no_recieved')
    def _onchange_has_no_recieved(self):
        if self.has_no_recieved:
            self.has_recieved = False




    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_purchase_req_report.purchase_req_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_purchase_req_report.purchase_req_report_pdf_id').report_action(self,data=data)









