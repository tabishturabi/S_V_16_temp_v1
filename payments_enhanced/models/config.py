# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigTax(models.Model):
    _name = 'res.config.sequnce'
    _description = "Res Config Tax "

    sequnce_id = fields.Many2one('ir.sequence', string="Internal Sequence")


class ResSaleConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    sequnce_id = fields.Many2one('ir.sequence', string="Internal Sequence", related='company_id.sequnce_id',readonly=False)

	# @api.model
	# def get_values(self):
	# 	tax_list = []
	# 	res = super(ResSaleConfig, self).get_values()
	# 	Config = self.env.ref('payments_enhanced.res_config_sequnce_data', False)
	# 	res.update({'sequnce_id' : Config.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).sequnce_id.id})
	# 	return res
	#
	# @api.multi
	# def set_values(self):
	# 	super(ResSaleConfig, self).set_values()
	# 	ir_config = self.env['ir.config_parameter']
	# 	self.ensure_one()
	# 	Config = self.env.ref('payments_enhanced.res_config_sequnce_data', False)
	# 	if self.sequnce_id:
	# 		Config.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).write({'sequnce_id' : self.sequnce_id.id})
	# 	else:
	# 		Config.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).write({'sequnce_id' : False})
	# 	return True
	#
	#
