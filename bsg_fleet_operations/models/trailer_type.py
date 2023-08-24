# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BsgTrailerType(models.Model):
	_name = 'bsg.trailer.type'
	_description = "Trailer Type"
	_inherit = ['mail.thread']
	_rec_name = "trailer_type_id"

	# Trailer Type Screen 
	trailer_type_id = fields.Char(string="Trailer Type ID")
	active = fields.Boolean(string="Active", track_visibility=True, default=True)
	trailer_ar_name = fields.Char(string="Trailer Ar Name")
	trailer_er_name = fields.Char(string="Trailer Er Name")
	trailer_status = fields.Char(string="Trailer Status")
	domain_name = fields.Selection(string="Domain Name", selection=[
	('Carrier','Carrier'),('Bx','Bx'),('Cargo','Cargo'),('Service','Service')])

	#general infomration
	triler_type_class  = fields.Selection(string="Trailer Type Class", selection=[
	('satha','Satha'),('Dawrayn','Dawrayn'),('Curtain','Curtain')])
	trailer_length = fields.Char(string="Trailer Length")
	trailer_width = fields.Char(string="Trailer Width")
	max_trailer_height = fields.Char(string="Max Trailer Height")
	gross_weight = fields.Char(string="Gross Weight")
	net_wright = fields.Char(string="Net Weight")
	gross_volume = fields.Char(string="Gross Volume")
	net_volume = fields.Char(string="Net Volume")

	#drwrayn height
	first_surface_hight = fields.Char(string="1 First Surface Height")
	second_surface_hight = fields.Char(string="2 Secong Surface Height")

	# one2many ids
	car_component_ids = fields.One2many('car.carrier.components','component_id')
	trailer_comment_ids = fields.One2many('trailer.comments.config','triler_type_id')

	trailer_services_count = fields.Integer(string="Odometer Count", compute="_compute_service_logs")


class CarCarrierComponent(models.Model):
	_name = "car.carrier.components"
	_description = "Car Carrier Component"

	component_id = fields.Many2one('bsg.trailer.type')
	floor_no = fields.Char(string="Floor No")
	car_size = fields.Char(string="Car Size")
	qty = fields.Char(string="QTY")  


class TrailerCommentsConfig(models.Model):
	_name = "trailer.comments.config"
	_description = "Tires History Config"

	triler_type_id = fields.Many2one('bsg.trailer.type',string="Trailer Type ID")
	triler_config_id = fields.Many2one('bsg_fleet_trailer_config',string="Trailer Config ID")
	comment_date = fields.Datetime(string="Comments Date",default=lambda self: fields.datetime.now())
	short_comment_des = fields.Char(string="Short Comments Des.")
	attachment_ids = fields.Many2many('ir.attachment')
	comments = fields.Text(string="Comments")