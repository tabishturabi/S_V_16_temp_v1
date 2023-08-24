# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BsgEstimatedDeliveryDays(models.Model):
	_name = 'bsg.estimated.delivery.days'
	_description = "Estimated Delivery Day's"
	_inherit = ['mail.thread']

	#Fields Declaration 
	name = fields.Char(string='Name')
	active = fields.Boolean(string="Active", tracking=True, default=True)
	loc_from_id = fields.Many2one('bsg_route_waypoints',string='Est DD From')
	loc_to_id = fields.Many2one('bsg_route_waypoints',string='Est DD To')
	shipemnt_type = fields.Many2one('bsg.car.shipment.type',string='Shipment Type')
	est_no_delivery_days = fields.Integer(string='Est No of Days')
	est_no_hours = fields.Float(string='Est No of Hours')
	est_max_no_delivery_days = fields.Integer(string='Est Max No of Days')
	est_max_no_hours = fields.Float(string='Est Max No of Hours')
	# Constraints....
	_sql_constraints = [
						('loc_to_id_loc_from_id_uniq', 
	    				'unique (loc_to_id,loc_from_id,shipemnt_type)', 
	    				_('The From,To and shipment type must be unique !')),
	    				]

	
	@api.constrains('est_no_delivery_days', 'est_no_hours', 'est_max_no_delivery_days', 'est_max_no_hours')
	def _check_negative_values(self):
		if self.est_no_delivery_days < 0 or self.est_max_no_delivery_days < 0:
			raise UserError(_('Days must be non-negative.'))

		if self.est_no_hours < 0 or self.est_max_no_hours < 0:
			raise UserError(_('Hours must be non-negative.'))


	# Overiding default odoo create method 
	@api.model_create_multi
	def create(self, values):
		"""
		Create a new record for a model BsgEstimatedDeliveryDays
		@param values: provides a data for new record

		@return: returns a id of new record
		"""
		EstmatedObj = super(BsgEstimatedDeliveryDays, self).create(values)
		EstmatedObj.name = self.env['ir.sequence'].next_by_code('bsg_master_config_estimated_delivery_day_code')
		return EstmatedObj