# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class BsgEducation(models.Model):
    _name = 'hr.education'
    _description = "Education"
    _rec_name = "bsg_name"

    bsg_edu_type = fields.Many2one('hr.education.type',string="Education Type")
    bsg_name = fields.Char(related="bsg_edu_type.bsg_type")
    bsg_inst = fields.Char("Institute Name ")
    # bsg_relation = fields.Char("Relation")
    education_emp = fields.Many2one('hr.employee', string="Education Ref")
    upload_file = fields.Binary(string="Upload File")
    file_name = fields.Char(string="File Name")

class BsgEducationType(models.Model):
    _name = 'hr.education.type'
    _description = "Education Type"
    _rec_name = "bsg_type"

    bsg_type = fields.Char("Education Type")
