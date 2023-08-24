# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BsgMasterConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	est_delivery_selection = fields.Selection(string='Estimation Delivery Structure',
         selection=[('trips', 'Trips Planning'), ('edd', 'Delivery Days')])
	capacity_threshold = fields.Float(string='Capacity Threshold')
	satha_capacity_threshold = fields.Float(string='Capacity Threshold')
	car_year_id = fields.Many2one('bsg.car.year',string="Credit SO For > Car Year Manufacture : ",config_parameter='bsg_master_config.car_year_id')

	# @api.model_create_multi
	def get_values(self):
		res = super(BsgMasterConfigSettings, self).get_values()
		est_delivery_selection = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('bsg_master_config.est_delivery_selection')
		capacity_threshold = float(self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('bsg_master_config.capacity_threshold'))
		satha_capacity_threshold = float(self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('bsg_master_config.satha_capacity_threshold'))
		res.update({
					'est_delivery_selection' : est_delivery_selection,
					'capacity_threshold' : capacity_threshold,
					'satha_capacity_threshold' : satha_capacity_threshold,
					})
		return res

	
	def set_values(self):
		super(BsgMasterConfigSettings, self).set_values()
		self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).set_param('bsg_master_config.est_delivery_selection', self.est_delivery_selection)
		self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).set_param('bsg_master_config.capacity_threshold', self.capacity_threshold)
		self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).set_param('bsg_master_config.satha_capacity_threshold', self.satha_capacity_threshold)


