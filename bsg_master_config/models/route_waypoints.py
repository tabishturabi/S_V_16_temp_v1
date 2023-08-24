# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
from lxml import etree
# from odoo.osv.orm import setup_modifiers
from odoo.exceptions import UserError

class bsg_route_waypoints(models.Model):
	_name = 'bsg_route_waypoints'
	_description = "Location"
	_inherit = ['mail.thread']
	_rec_name="waypoint_name"

	# Khalid Made this change ask him while changing
	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.browse()
		if name:
			location_name =self.search([('route_waypoint_name',operator, name)] + args, limit=limit)
			waypoint_name = self.search([('waypoint_name', operator, name)] + args, limit=limit)
			branch_name =self.search([('loc_branch_id.branch_ar_name',operator, name)] + args, limit=limit)
			branch_no =self.search([('branch_no',operator, name)] + args, limit=limit)
			if location_name:
				recs = location_name
			elif branch_no:
				recs = branch_no
			elif branch_name:
				recs = branch_name
		if not recs:
			recs = self.search([('waypoint_name', operator, name)] + args, limit=limit)
		return recs.name_get()


	# @a
	route_waypoint_seq = fields.Char('Seq #')
	waypoint_name = fields.Char('Waypoint Name', compute="_compute_waypoint_name", store=True,)
	waypoint_english_name = fields.Char('Location English Name')
	route_waypoint_name = fields.Char('Location Name')
	active = fields.Boolean(string="Active", tracking=True, default=True)
	loc_branch_id = fields.Many2one("bsg_branches.bsg_branches", string="Branch")
	branch_no = fields.Char(string="Branch No",related="loc_branch_id.branch_no",store=True)
	location_type = fields.Selection(string="Location Type", required=True, selection=[
		('albassami_loc','Albassami  Location'),
		('customer_loc','Customer Location'),
		('general_loc','General location')
	], default="")
	loc_customer_ids = fields.Many2many(comodel_name='res.partner', string='Customer')
	location_long = fields.Char(string="Longitude")
	location_lat = fields.Char(string="Latitude")
	city = fields.Char("City")
	waypoint = fields.Char("Waypoint No", store=True)
	location_url = fields.Char("Location URL")
	country_id = fields.Many2one('res.country',string="Country")
	region = fields.Many2one('region.config',string="Region")
	branch_type = fields.Selection(string="Branch Type", selection=[
		('pickup', 'Pickup'),
		('shipping', 'Shipping'),
		('both', 'Both')], default='shipping')
	is_international = fields.Boolean(string="IS International")
	is_port = fields.Boolean(string="IS Port")
	is_allow_to_release = fields.Boolean(string="Allowed To Relase Any One")
	is_internal = fields.Boolean(string="IS Internal")
	is_portal_hide_from_to = fields.Boolean(string="Portal hide from drop - To", copy=False)
	is_portal_hide_from_pickup = fields.Boolean(string=" Portal hide from pickup - From", copy=False)
	allowed_return_waypoint_ids = fields.Many2many('bsg_route_waypoints', relation='allowed_return_waypoints', column1='allowed_return_waypoint_col_1', column2='allowed_return_waypoint_col_2', string='Allowed Return Locations')
	is_close_location = fields.Boolean(string="IS Closed Location")
	visible_on_mobile_app = fields.Boolean('Visible On Mobile App')
	visible_for_subcontract_api = fields.Boolean('Visible Subcontractor API')
	has_satha_service = fields.Boolean('Has Satha Service')
	# Removing required=True from region_city_id %%%% Migration for v16
	region_city_id = fields.Many2one('region.config.line', string='Region city')
	zone_id = fields.Many2one('branches.zones', string='Zone')
	check = fields.Boolean(string="Check")
	allowed_shipment_types = fields.Many2many('bsg.car.shipment.type', string="Allowed Shipment Types")
	# Removing required=True from bayan_city_id %,bayan_region_id %%% Migration for v16
	bayan_city_id = fields.Integer(string="Bayan City ID", tracking=True)
	bayan_region_id = fields.Integer(string="Bayan Region ID", tracking=True)
	location_dedicated_area_id = fields.Many2one('trucks.dedicating.area', string="Location Dedicated Area",tracking=True)


	# _sql_constraints = [
	# ('value_route_waypoint_name_uniq', 'unique (route_waypoint_name)', 'This Location Name Must Be Unique !')
	# ]

	
	def write(self, values):
		res = super(bsg_route_waypoints, self).write(values)
		for rec in self:
			if rec:
				branch_id = rec.env['bsg_branches.bsg_branches'].search([('id', '=', rec.loc_branch_id.id)], limit=1)
				if branch_id:
					branch_id.update({
						'region': rec.region.id,
						'region_city': rec.region_city_id.id,
						'zone_id': rec.zone_id.id,
					})
		return res

	@api.model_create_multi
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		result = super(bsg_route_waypoints, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
		if view_type == 'form' and not self.env.user.has_group('bsg_master_config.group_waypoint_sale_master'):
			doc = etree.XML(result['arch'])
			method_nodes = doc.xpath("//field")
			for node in method_nodes:
				if node.get('name', False) != 'branch_type':
					node.set('readonly', "1")
					setup_modifiers(node, result['fields'][node.get('name', False)])
			result['arch'] = etree.tostring(doc)
		return result

	@api.onchange('region')
	def _get_region_city(self):
		if self.region:
			if not self.check:
				self.region_city_id = False
			if self.region.region_line:
				self.check = False
				return {'domain': {'region_city_id': [('id', 'in', self.region.region_line.ids)]}}
			if not self.region.region_line:
				self.check = False
				return {'domain': {'region_city_id': [('id', 'in', self.region.region_line.ids)]}}

		else:
			city_ids = self.env['region.config.line'].search([])
			return {'domain': {'region_city_id': [('id', 'in', city_ids.ids)]}}

	@api.onchange('is_close_location')
	def _onchange_is_close_location(self):
		if self.is_close_location:
			self.is_portal_hide_from_pickup = True
			self.is_portal_hide_from_to = True
			self.visible_on_mobile_app = False
		else:
			self.is_portal_hide_from_pickup = False
			self.is_portal_hide_from_to = False
			self.visible_on_mobile_app = False

	@api.onchange('region_city_id')
	def _get_region(self):
		if self.region_city_id:
			if not self.region:
				self.check = True
			self.region = self.region_city_id.region_id
	# _compute_waypoint_name method for geting the rec name 
	
	@api.depends('route_waypoint_name','location_type')
	def _compute_waypoint_name(self):
		if self.location_type:
			if self.location_type == 'albassami_loc':
				self.waypoint_name = self.loc_branch_id.branch_ar_name or self.route_waypoint_name
			else:
				self.waypoint_name = self.route_waypoint_name


	# Overiding Create Method
	@api.model_create_multi
	def create(self, vals):
		LocationObj = super(bsg_route_waypoints, self).create(vals)
		sequence = None
		if LocationObj.location_type == 'albassami_loc':
			sequence = self.env['ir.sequence'].next_by_code('bsg_master_config_waypoint_seq_alb_code')
		elif LocationObj.location_type == 'customer_loc':
			sequence = self.env['ir.sequence'].next_by_code('bsg_master_config_waypoint_seq_cusl_code')
		elif LocationObj.location_type == 'general_loc':
			sequence = self.env['ir.sequence'].next_by_code('bsg_master_config_waypoint_seq_gen_code')
		LocationObj.route_waypoint_seq = sequence
		branch_id = LocationObj.env['bsg_branches.bsg_branches'].search([('id', '=', LocationObj.loc_branch_id.id)],limit=1)
		if branch_id:
			branch_id.update({
				'region': LocationObj.region.id,
				'region_city': LocationObj.region_city_id.id,
				'zone_id': LocationObj.zone_id.id,
			})
		return LocationObj

	@api.onchange('loc_branch_id')
	def _onchange_branch_id(self):
		if self.loc_branch_id:
			self.region = self.loc_branch_id.region.id or False
			self.city = self.loc_branch_id.city or False
			self.country_id = self.loc_branch_id.country_id.id or False
	
	@api.onchange('branch_no','city')
	def _onchange_waypoint(self):
		if self.branch_no:
			self.waypoint = self.branch_no
		else:
			self.waypoint = self.city
		
	
	def action_getlatlan(self):
		google_maps_api_key = self.env['website'].get_current_website().google_maps_api_key
		if not google_maps_api_key:
			raise UserError(
					_('Please Check google api key is missing. Go to website and configuration...'),
				)
		URL = "https://maps.googleapis.com/maps/api/geocode/json?key="+str(google_maps_api_key)+"="
		for rec in self:
			Address = str(rec.route_waypoint_name) + ' ' +str(rec.city)+' '+str(rec.country_id.name)
			Response = requests.get(URL+Address)
			RespJson_Payload = Response.json()
			if RespJson_Payload['results']:
				location = RespJson_Payload['results'][0]['geometry']['location']
				rec.location_lat = location.get('lat')
				rec.location_long = location.get('lng') 

	
	def unlink(self):
		cargo_sale = self.env['bsg_vehicle_cargo_sale'].search(['|',('loc_to','=',self.id),('loc_from','=',self.id)])
		bsg_price_config = self.env['bsg_price_config'].search(['|',('waypoint_from','=',self.id),('waypoint_to','=',self.id)])
		bsg_route = self.env['bsg_route'].search([('waypoint_from','=',self.id)])
		bsg_route_line = self.env['bsg_route_line'].search([('waypoint','=',self.id)])
		if cargo_sale or bsg_price_config or bsg_route or bsg_route_line:
			raise UserError(
				_('Sorry you cant delete this record as it is already in used by some other records'),
				)
		result = super(bsg_route_waypoints, self).unlink()
		return result

