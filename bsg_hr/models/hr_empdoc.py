# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class BsgHrEmpDoc(models.Model):
    _name = 'hr.emp.doc'
    _description = "Employee Document"
    _rec_name = "bsg_type"

    hrdoc = fields.Many2one('hr.employee', string="Insurance Ref")
    # bsg_name = fields.Char("Document Name")
    bsg_type = fields.Many2one('hr.emp.doc.type',string="Document Type")
    bsg_startdate = fields.Date("Document Start date")
    bsg_enddate = fields.Date("Document End date")
    upload_file = fields.Binary(string="Upload File")
    file_name = fields.Char(string="File Name")

class BsgHrDocType(models.Model):
    _name = 'hr.emp.doc.type'
    _description = "Employee Document"
    _rec_name = "bsg_name"

    bsg_name = fields.Char("Name")