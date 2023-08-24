# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BsgBranchDocType(models.Model):
    _name = 'bsg.branch.doc.type'
    _description = 'Branch Document Type'
    _rec_name = 'branch_doc_type'

    branch_doc_type = fields.Char(string='Branch Document Type', translate=True)
