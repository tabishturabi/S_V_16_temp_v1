# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class BranchOwner(models.Model):
    _inherit = 'bsg_branches.bsg_branches'


    contract_type = fields.Selection([('rent','Rent'),('owned','Owned')],string='Contract Type',track_visibility='always')
    lessor_name = fields.Many2one('res.partner',string='Lessor Name',track_visibility='always')
    contract_no = fields.Integer(string='Contract Number',track_visibility='always')
    contract_amount = fields.Float(string='Contract Amount',track_visibility='always')
    tenancy_start_date = fields.Date(string='Tenancy Start Date',track_visibility='always')
    tenancy_end_date = fields.Date(string='Tenancy End Date',track_visibility='always')
    electricity_meter_number = fields.Integer(string='Electricity Meter Number',track_visibility='always')
    water_meter_number = fields.Integer(string='Water Meter Number',track_visibility='always')
    attachment_ids  = fields.Many2many('ir.attachment',string='Attachment',track_visibility='always')
    description = fields.Char(string='Description',track_visibility='always')




