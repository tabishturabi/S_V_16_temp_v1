# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigCashRouding(models.Model):
    _name = 'res.config.cash.rounding'
    _description = "Res Config Tax "

    cash_rounding_id = fields.Many2one('account.cash.rounding', string="Cash Rounding Method")


class TripManagementConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    local_trip_revenue = fields.Float(string='Local Trip Revenue', default=0, related='company_id.local_trip_revenue',readonly=False)
    cash_rounding_id = fields.Many2one('account.cash.rounding', string="Cash Rounding Method",
                                       related='company_id.cash_rounding_id',readonly=False)
    rented_vehicle_service = fields.Many2one('product.template',string='Default Rented Vehicle Service Product',readonly=False,related="company_id.rented_vehicle_service",store=True)								   

	# @api.model
	# def get_values(self):
	# 	res = super(TripManagementConfig, self).get_values()
	# 	local_trip_revenue = float(self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('bsg_trip_mgmt.local_trip_revenue'))
	# 	Config = self.env.ref('bsg_trip_mgmt.res_config_cash_rounding_data', False)
	# 	res.update({'local_trip_revenue' : local_trip_revenue,
	# 				'cash_rounding_id' : Config.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).cash_rounding_id.id})
	# 	return res
	#
	# @api.multi
	# def set_values(self):
	# 	super(TripManagementConfig, self).set_values()
	# 	self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).set_param('bsg_trip_mgmt.local_trip_revenue', self.local_trip_revenue)
	# 	Config = self.env.ref('bsg_trip_mgmt.res_config_cash_rounding_data', False)
	# 	if self.cash_rounding_id:
	# 		Config.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).write({'cash_rounding_id' : self.cash_rounding_id.id})
	# 	else:
	# 		Config.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).write({'cash_rounding_id' : False})
	# 	return True
