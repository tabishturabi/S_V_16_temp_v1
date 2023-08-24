# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class BsgBranchClassification(models.Model):
	_name = 'bsg.branch.classification'
	_description = "Branch Classfication"
	_inherit = ['mail.thread']
	_rec_name = "bsg_branch_cls_name"

	bsg_branch_cls_name = fields.Char('Branch Type')
	active = fields.Boolean(string="Active", tracking=True, default=True)

	_sql_constraints = [
	    ('bsg_branch_cls_name_uniq', 'unique (bsg_branch_cls_name)', _('The branch name must be unique !')),
	]
