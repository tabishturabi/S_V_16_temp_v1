# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsgBranchSalesTarget(models.Model):
	_name = 'bsg_branch_sales_target'
	_description = "Branch Sales Target"
	_inherit = ['mail.thread']
	_rec_name = "bsg_br_sl_tar_seq"

	bsg_br_sl_tar_seq = fields.Char('Sequence')
	active = fields.Boolean(string="Active", tracking=True, default=True)
	financial_year = fields.Many2one(string="Fiscal Year", comodel_name="account.fiscal.year")
	br_sl_tr_line_ids = fields.One2many(string="Line Ids", comodel_name="bsg_branch_sales_target_lines", inverse_name="bsg_br_sl_tr_id")
	bsg_sl_tr_br_id = fields.Many2many(string="Branches Name", comodel_name="bsg_branches.bsg_branches")


	@api.model_create_multi
	def create(self, vals):
		SalesTarget = super(BsgBranchSalesTarget, self).create(vals)
		SalesTarget.bsg_br_sl_tar_seq = self.env['ir.sequence'].next_by_code('bsg_branch_sales_target')
		return SalesTarget


class BsgBranchSalesTargetLines(models.Model):
	_name = 'bsg_branch_sales_target_lines'
	_description = "Branch Sales Target Lines"

	service_type = fields.Many2one(string="Service Type", comodel_name="product.template")
	bsg_br_sl_tr_mon = fields.Selection(string="Month", selection=[
		('1', 'January'),('2', 'February'),('3', 'March'),
		('4', 'April'),('5', 'May'),('6', 'June'),
		('7', 'July'),('8', 'August'),('9', 'September'),
		('10', 'October'),('11', 'November'),('12', 'December')
		])

	bsg_br_sl_tr_for_tar = fields.Float(string="Forcasted Target")
	bsg_br_sl_tr_ac_tar = fields.Float(string="Actual Target")
	diff_sales_target = fields.Float(string="Difference", compute="_get_difference")
	bsg_br_sl_tr_id = fields.Many2one(string="Branch Sales Target ID", comodel_name="bsg_branch_sales_target")
	customer_type = fields.Selection(string='Customer Type',selection=[
        ('individual', 'Individual'),
        ('corporate', 'Corporate')
    ])

	#
	#@api.depends('bsg_br_sl_tr_for_tar','bsg_br_sl_tr_ac_tar')
	def _get_difference(self):
		for rec in self:
			rec.diff_sales_target = 0.0
			if rec.bsg_br_sl_tr_for_tar or rec.bsg_br_sl_tr_ac_tar:
				rec.diff_sales_target = rec.bsg_br_sl_tr_ac_tar - rec.bsg_br_sl_tr_for_tar
