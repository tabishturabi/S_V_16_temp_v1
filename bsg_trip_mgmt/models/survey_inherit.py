# -*- coding: utf-8 -*-

import datetime as dt
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class SurveySurvey(models.Model):
	_inherit = 'survey.survey'

	is_driver = fields.Boolean(string="Is Driver Survey")
	driver_ids = fields.Many2many(string="Driver", comodel_name="hr.employee")
	arrival_id = fields.Many2one('fleet.trip.arrival')

	@api.constrains('is_driver')
	def _code_constrains(self):
		if self.is_driver:
			search_id = self.env['survey.survey'].search([('is_driver','=',True)])
			if len(search_id) > 1:
				raise UserError('Driver Survey Must Be one..!')

class SurveyUserInput(models.Model):
	_inherit = 'survey.user_input'

	waypoint_from = fields.Many2one(string="Source", comodel_name="bsg_route_waypoints")
	waypoint_to = fields.Many2one(string="Destination", comodel_name="bsg_route_waypoints")
	trip_id = fields.Many2one(string="Trip Id", comodel_name="fleet.vehicle.trip")
	driver_id = fields.Many2one(string="Driver", comodel_name="hr.employee")

	@api.model
	def create(self, vals):
		if vals.get('survey_id'):
			survey_id = self.env['survey.survey'].search([('id','=',vals.get('survey_id'))])
			arrival_search = self.env['fleet.trip.arrival'].search([('id','=',survey_id.arrival_id.id)])
			arrival_search.write({'survey_id' : survey_id.id ,'is_survey_done' : False})
			vals['waypoint_from'] = survey_id.arrival_id.waypoint_from.id
			vals['waypoint_to'] = survey_id.arrival_id.waypoint_to.id
			vals['trip_id'] = survey_id.arrival_id.trip_id.id
			vals['driver_id'] = survey_id.arrival_id.trip_id.driver_id.id
		return super(SurveyUserInput, self).create(vals)
