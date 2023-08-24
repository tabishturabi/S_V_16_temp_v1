# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Projects(models.Model):
    _name = 'bsg.mrp.project'
    _description = 'BSG MRP Projects'

    name = fields.Char('Project name')
    project_type = fields.Many2one('bsg.mrp.project.type','Project Type Name')
    project_amount = fields.Float('Project Amount')
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)


class ProjectType(models.Model):
    _name = 'bsg.mrp.project.type'
    _description = 'BSG MRP Project Type'

    name = fields.Char('Project Type Name')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

