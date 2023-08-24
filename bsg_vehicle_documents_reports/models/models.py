# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict
from werkzeug.urls import url_encode
import uuid
import base64





class VehicleDocumentReportWizard(models.TransientModel):
    _name = 'vehicle.documents.report.wizard'

    grouping_by = fields.Selection([('all','All'),('document_type','Document Type'), ('vehicle_make','Vehicle Make'), ('vehicle_type', 'Vehicle Type'),
                                    ('vehicle_domain_name', 'Vehicle Domain Name'), ('vehicle_status', 'Vehicle Status'),
                                    ('document_expiry_date', 'Document Expiry Date'),('created_by', 'Created By')], required=True,string='Grouping By')
    expire_date_condition = fields.Selection([('all', 'All'), ('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
                                              ('is_after', 'is after'), ('is_before', 'is before'),
                                              ('is_after_or_equal_to', 'is after or equal to'),
                                              ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
                                              ('is_set', 'is set'), ('is_not_set', 'is not set')], required=True, string='Expire Date Condition',default='all')
    renewal_license_date_condition = fields.Selection(
        [('all', 'All'), ('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
         ('is_after', 'is after'), ('is_before', 'is before'),
         ('is_after_or_equal_to', 'is after or equal to'),
         ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
         ('is_set', 'is set'), ('is_not_set', 'is not set')], required=True, string='Renewel License Date Condition',
        default='all')
    last_update_date_condition = fields.Selection(
        [('all', 'All'), ('is_equal_to', 'is equal to '), ('is_not_equal_to', 'is not equal to'),
         ('is_after', 'is after'), ('is_before', 'is before'),
         ('is_after_or_equal_to', 'is after or equal to'),
         ('is_before_or_equal_to', 'is before or equal to'), ('is_between', 'is between'),
         ('is_set', 'is set'), ('is_not_set', 'is not set')], required=True, string='Last Update Date Condition',
        default='all')
    date_filter_by = fields.Selection(
        [('expire_date', 'Expire Date'), ('renewel_license_date', 'Renewel License Date'),
         ('last_update_date', 'Last Update Date')],
        string='Date Filter By')
    period_grouping_by = fields.Selection([('day', 'Day'),('weekly', 'Weekly'),('month', 'Month'),('quarterly', 'Quarterly'),('year', 'Year'),], string='Period Grouping By')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    date_from_last_update = fields.Date(string='From')
    date_to_last_update = fields.Date(string='To')
    date_from_renewel_license = fields.Date(string='From')
    date_to_renewel_license = fields.Date(string='To')
    expiry_date = fields.Date(string='Expiry Date')
    renewal_license_date = fields.Date(string='Renewel License Date')
    last_update_date = fields.Date(string='Last Update Date')
    last_update_by = fields.Many2many('res.users','last_update_user_id','wiz_id', string='Last Update By')
    create_by = fields.Many2many('res.users','create_user_id','wiz_id', string='Create By')
    vehicle_make = fields.Many2many('fleet.vehicle.model.brand',string='Vehicle Make')
    document_type = fields.Many2many('documents.type',string='Document Type')
    vehicle_sticker_no = fields.Many2many('fleet.vehicle',string='Vehicle Sticker NO')
    driver_link = fields.Selection([('linked','Linked'),('unlinked','Un_Linked')],string="Driver Link")
    driver_name = fields.Many2many('hr.employee',string='Driver Name')
    model_year =  fields.Many2many('bsg.car.year',string='Model Year')
    vehicle_state = fields.Many2many('fleet.vehicle.state',string='Vehicle State')
    vehicle_status = fields.Many2many('bsg.vehicle.status' ,string='Vehicle Status')
    vehicle_type = fields.Many2many('bsg.vehicle.type.table',string='Vehicle Type')
    domain_name = fields.Many2many('vehicle.type.domain',string='Domain Name')
    print_date = fields.Date(string='Today Date', default=fields.date.today())
    report_file = fields.Binary('report file')

    # @api.multi
    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_action(self,data=data)

    # @api.multi
    def click_print_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        print(data,999999999999888888)
        return self.env.ref('bsg_vehicle_documents_reports.vehicle_document_report_pdf_id').report_action(self,data=data)

    # @api.multi
    def get_notification(self):
        data = self.read()
        report = self.env['ir.actions.report']. \
            _get_report_from_name('bsg_vehicle_documents_reports.vehicle_doc_report_xlsx')
        xlsx_ = report.with_context({'active_id': self.id}).render_xlsx(self.ids, data)

        excel_file = base64.encodestring(xlsx_[0])

        attachment_id = self.env['ir.attachment'].create({
            'name': 'document.xlsx',
            'datas': excel_file,
            'store_fname': 'document.xlsx',
            'type': 'binary'
        })
        print("attachmenttttttttttt", attachment_id)
        return attachment_id




