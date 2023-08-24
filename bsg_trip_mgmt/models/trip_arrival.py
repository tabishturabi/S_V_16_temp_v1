# -*- coding: utf-8 -*-

import datetime as dt
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class ArrivingConfirmWiz(models.TransientModel):
	_name = 'arriving.confrim.wiz'

	arriving_lines = fields.Html('Arriving Cars')


	# @api.multi
	def register_arrival(self):
		return self.env['fleet.trip.arrival'].browse(self._context.get('active_id')).confirm_trip()

	# @api.multi
	def action_cancel(self):
		return self.env['fleet.trip.arrival'].browse(self._context.get('active_id')).trip_id.action_register_arrival()

class BsgFleetTripArrival(models.Model):
	_name = 'fleet.trip.arrival'
	_description = "Trip Arrval"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'waypoint_from'

	# @api.multi
	def validate_arrival_fields(self):
		# if self.odoometer == 0:
		# 	raise UserError(_("Odoo meter can not be 0"))
		# search_odoo_meter = self.env['fleet.vehicle.odometer'].search([('fleet_trip_id','=',self.trip_id.id)],limit=1)
		# if search_odoo_meter.value > self.odoometer:
			# raise UserError(_("Odoo meter should be Greter than old meter value"))
		if not self.survey_ids and not self.is_no_violation:
			raise UserError(_("Please Complete Survey First!"))
		# waypoint_line_ids = self.trip_id.trip_waypoint_ids
		lines_ids = self.arrival_line_ids.filtered(lambda l: l.state == 'shipped')
		if self.trip_id.route_id.route_type != 'port':
			rec_names = []
			for rec in lines_ids:
				# waypoint_lines = waypoint_line_ids.filtred(lambda l : rec.delivery_id.id in l.delivered_items.ids)
				# #  l.waypoint.id == rec.drop_loc.id and 
				# if waypoint_lines:
				# 	if rec.drop_loc.id in waypoint_lines.mapped('waypoint.id'):
				# 		raise ValidationError(_("SO line %s has already registered arrival at branch %s")%(rec.delivery_id.sale_line_rec_name, rec.drop_loc.waypoint_name))
				
				# field_names  = ['parking_no', 'drawer_no', 'arrived']
				field_names = ['arrived']
				res = rec.read(field_names)[0]
				arrival_fields = [res[key] for key in field_names]
				if any(arrival_fields) and not all(arrival_fields):
					rec_names.append(rec.delivery_id.sale_line_rec_name)
					# raise ValidationError(_("You must type in [drawer, parking number and mark as arrived ] to register arrival for SO %s")%rec.delivery_id.sale_line_rec_name)
					raise ValidationError(_("You must type in [mark as arrived] to register arrival for SO %s") % rec.delivery_id.sale_line_rec_name)

	@api.onchange('is_no_violation', 'survey_ids')
	def on_change_is_no_violation(self):
		for rec in self:
			if rec.is_no_violation:
				self.survey_ids = False
	
	def calculate_standard_actual_revenue(self):
		if self.trip_id.state == 'finished':
			route_id = self.trip_id.route_id
			price_line = self.env['bsg_price_line'].search([('waypoint_from', '=', route_id.waypoint_from.id), ('waypoint_to', '=', route_id.waypoint_to_ids[-1].waypoint.id), ('service_type', '=', 1), ('customer_type', '=', 'individual'), ('car_size', '=', 53), ('company_id','=', self.env.user.company_id.id)], limit=1)
			price =  price_line.price or 0
			lines = self.trip_id.mapped('stock_picking_id.picking_name')
			waypoints = [route_id.waypoint_from]+list(route_id.waypoint_to_ids.mapped('waypoint')) 
			trailer_id = self.trip_id.vehicle_id.trailer_id
			standard_revenue = price * trailer_id.trailer_capacity
			within_route_lines = [l for l in lines if l.loc_from in waypoints and l.loc_to in waypoints]
			actual_revenue = sum([l.total_without_tax for l in within_route_lines])
			not_within_route = [l for l in lines if l not in  within_route_lines]
			# total_distance = route_id.total_distance
			for so in not_within_route:
				# so_disance = sum(so.trip_history_ids.filtered(lambda t: t.fleet_trip_id == self.trip_id).mapped('trip_distance'))
				so_revenue = sum(so.trip_history_ids.filtered(lambda t: t.fleet_trip_id == self.trip_id).mapped('earned_revenue'))
				# distence_id = self.env['branch.distance'].sudo().search([('branch_from','=',so.loc_from.loc_branch_id.id),('branch_to','=',so.loc_to.loc_branch_id.id)],limit=1)
				# so_full_distance = distence_id and distence_id.distance
				# if so_disance > 0:
				# 	KM_revenue = so.total_without_tax / (so_full_distance or 1)
				actual_revenue += so_revenue
			self.trip_id.write({
				'standard_revenue': standard_revenue,
				'actual_revenue': actual_revenue
			})	

	# @api.multi
	# @api.multi
	def confirm_trip(self):
		if self.is_no_violation:
			res = self.no_violation()
			self.calculate_standard_actual_revenue()
			return res
		elif self.survey_ids:
			res =self.confirm_survey()
			self.calculate_standard_actual_revenue()
			return res

		# search_odoo_meter = self.env['fleet.vehicle.odometer'].search([('fleet_trip_id','=',self.trip_id.id)],limit=1)
		# if search_odoo_meter.value > self.odoometer:
		# 	raise UserError(_("Odoo meter should be Greter than old meter value"))
		# if not self.is_done_survey:
		# 	raise UserError(_("Please Complete Survey First!"))
		self._create_odoometer(self.trip_id.id, self.waypoint_from.id, self.waypoint_to.id, \
		 self.trip_id.vehicle_id.id, self.trip_id.driver_id.id, self.odoometer)
		is_already_finished	= self.trip_id.state == 'finished'
		self.with_context({'is_already_finished': is_already_finished})._register_arrival(self.trip_id)
		self._check_survay_done(self.trip_id, self.waypoint_from.id, self.waypoint_to.id)
		self.calculate_standard_actual_revenue()
	
	# @api.multi
	def confirm_arriving_lines(self):
		""" returns confirmation message then upon confirm register arrival"""
		self.validate_arrival_fields()
		view_id = self.env.ref('bsg_trip_mgmt.arriving_confrim_wiz_form').id
		style="border: 1px solid black;border: 1px solid #007829;"
		
		arriving_lins_html ="""<table style=\"width:100%;"""+style+"\">"+"""
			<tr>
				<th>%s</th>
				<th>%s</th>
				<th>%s</th>
				<th>%s</th>
				<th>%s</th>
			</tr>
		"""%(
			_('Sale line'),
			_('Plate Number'),
			_('Pickup Location'),
			_('Drop Location'),
			_('Location To')
		)
		lines = self.arrival_line_ids.filtered(lambda l: l.state == 'shipped' and l.arrived)
		for line in lines:
			tr = """
				<tr style="%s">
					<td style="%s">%s</td>
					<td style="%s">%s</td>
					<td style="%s">%s</td>
					<td style="%s">%s</td>
					<td style="%s">%s</td>
				</tr>
			"""%(style,
				style,
				line.delivery_id.sale_line_rec_name,
				style,
				line.plate_no,
				style,
				line.pickup_loc.route_waypoint_name,
				style,
				line.drop_loc.route_waypoint_name,
				style,
				line.delivery_id.bsg_cargo_sale_id.loc_to.route_waypoint_name
				
			)
			arriving_lins_html+=tr
		arriving_lins_html+= "</table>"
		res_id = self.env['arriving.confrim.wiz'].create({
			'arriving_lines':arriving_lins_html
		})
		return {
			'type': 'ir.actions.act_window',
			'name': 'Confrim Arrival',
			'view_mode': 'form',
			'view_type': 'form',
			'res_model': 'arriving.confrim.wiz',
			'view_id': view_id,
			'res_id':  res_id.id,
			'target': 'new',
			}

	# @api.multi
	def no_violation(self):
		# if self.odoometer == 0:
		# 	raise UserError(_("Odoo meter can not be 0"))
		self.register_done = True
		self.write({'is_done_survey': True})
		self._create_odoometer(self.trip_id.id, self.waypoint_from.id, self.waypoint_to.id, \
		 self.trip_id.vehicle_id.id, self.trip_id.driver_id.id, self.odoometer)
		is_already_finished = self.trip_id.state == 'finished'
		self.with_context({'is_already_finished': is_already_finished})._register_arrival(self.trip_id)
		self._check_survay_done(self.trip_id, self.waypoint_from.id, self.waypoint_to.id)
		# if self.finish_trip or is_already_finished:
		if is_already_finished:
			self.trip_id.state = 'finished'
		elif (self.waypoint_to.location_type != 'albassami_loc' or self.waypoint_from.location_type != 'albassami_loc') or  (self.waypoint_to.id == self.trip_id.route_id.waypoint_to_ids[-1].waypoint.id):
			self.trip_id.state = 'finished'
		else:
			self.trip_id.action_on_transit()
		diff_time =  self.est_trip_time
		if (self.trip_id.driver_id.driver_rewards == 'by_delivery') \
		or self.trip_id.driver_id.driver_rewards == 'by_delivery_a':
			reward_calculation = total_car = total_deducation = total_deducatino_pecentage = 0
			lines_ids = self.arrival_line_ids.filtered(lambda l: l.state == 'shipped')
			for car_data in lines_ids:
				total_car += car_data.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.car_size.trailer_capcity
			total_km = 0
			
			for data in self.trip_id.route_id.waypoint_to_ids:
				if data.waypoint.loc_branch_id.id == self.waypoint_to.loc_branch_id.id:
					total_km += data.distance
	
			delivery = self.env['driver_reward_per_delivery'].search([])
			if self.trip_id.driver_id.driver_rewards == 'by_delivery':
				for data in delivery:
					if data.from_km < total_km <= data.to_km:
						if (self.trip_id.driver_id.driver_rewards == 'by_delivery'):
							reward_calculation = data.amount_per_car
						# reward_calculation = data.amount_per_car_b
						elif self.trip_id.driver_id.driver_rewards == 'by_delivery_a':
							reward_calculation = data.amount_per_car_b
			self.write({'driver_reward_amount' : ((reward_calculation * total_car)) })
		else:
			reward_calculation = total_revenue = total_car = total_deducatino_pecentage = 0
			picking_id = self.env['fleet.vehicle.trip.pickings'].search([('bsg_fleet_trip_id','=',self.trip_id.id),('loc_from','=',self.waypoint_from.id),('loc_to','=',self.waypoint_to.id)],limit=1)
			total_revenue = picking_id.picking_name.total_without_tax
			lines_ids = self.arrival_line_ids.filtered(lambda l: l.state == 'shipped')
			for car_data in lines_ids:
				total_car += car_data.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.car_size.trailer_capcity

			delivery = self.env['driver_reward_by_revenue'].search([])
			for data in delivery:
				if data.from_km < total_revenue <= data.to_km:
					if total_revenue > 1:
						reward_calculation = ((total_revenue * data.amount_per_car) / 100 )
			self.write({'driver_reward_amount' : ((reward_calculation)) })

	# Confirm the survery and made payment voucher
	# @api.multi
	def confirm_survey(self):
		# survey_list = []
		# deserving_list = []
		# if self.odoometer == 0:
		# 	raise UserError(_("Odoo meter can not be 0"))
		# for data in self.arrival_survey_ids:
		# 	if data.feedback:
		# 		survey_list.append(data.feedback)
		# 	if data.deserving:
		# 		deserving_list.append(data.deserving)
		
		late_ariival_deduction = 0
		self.register_done = True
		self.write({'is_done_survey': True})
		self._create_odoometer(self.trip_id.id, self.waypoint_from.id, self.waypoint_to.id, \
		self.trip_id.vehicle_id.id, self.trip_id.driver_id.id, self.odoometer)
		is_already_finished =  self.trip_id.state == 'finished'
		self.with_context({'is_already_finished': is_already_finished})._register_arrival(self.trip_id)
		self._check_survay_done(self.trip_id, self.waypoint_from.id, self.waypoint_to.id)
		# if self.finish_trip or is_already_finished:
		if is_already_finished:
			self.trip_id.state = 'finished'
		elif self.waypoint_to.id == self.trip_id.route_id.waypoint_to_ids[-1].waypoint.id:
			self.trip_id.state = 'finished'
		else:
			self.trip_id.action_on_transit()
		diff_time =  self.est_trip_time
		est_time = self.trip_id.route_id.waypoint_to_ids.search([('waypoint','=',self.waypoint_to.id)],limit=1).estimated_time
		if diff_time > est_time:
			late_arrival = self.env['fine_for_late_arrival'].search([])
			for data in late_arrival:
				if data.from_km < diff_time <= data.to_km:
					late_ariival_deduction = data.deduction_from_reqard

		if (self.trip_id.driver_id.driver_rewards == 'by_delivery') \
		or (self.trip_id.driver_id.driver_rewards == 'by_delivery_a') :
			reward_calculation = total_car = total_deducation = total_deducatino_pecentage = 0
			lines_ids = self.arrival_line_ids.filtered(lambda l: l.state == 'shipped')
			for car_data in lines_ids:
				total_car += car_data.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.car_size.trailer_capcity
			# total_km = self.trip_id.route_id.total_distance

			total_km = 0
			
			for data in self.trip_id.route_id.waypoint_to_ids:
				if data.waypoint.loc_branch_id.id == self.waypoint_to.loc_branch_id.id:
					total_km += data.distance

			delivery = self.env['driver_reward_per_delivery'].search([])
			for data in delivery:
				if data.from_km < total_km <= data.to_km:
					if (self.trip_id.driver_id.driver_rewards == 'by_delivery'):
						reward_calculation = data.amount_per_car
					elif self.trip_id.driver_id.driver_rewards == 'by_delivery_a':
						reward_calculation = data.amount_per_car_b
				if late_ariival_deduction and late_ariival_deduction > 0:
					late_ariival_deduction = (reward_calculation * late_ariival_deduction / 100)
			for data in self.survey_ids:
				if data.dedcution_way == 'percentage':	
					total_deducatino_pecentage += data.pecentage_amount
				elif data.dedcution_way == 'fixed_amt':
					total_deducation += data.fixed_amount
			if total_deducatino_pecentage > 1:
					total_deducation += (((reward_calculation * total_car) * total_deducatino_pecentage) / 100)
			self.write({'driver_reward_amount' : ((reward_calculation * total_car) - total_deducation) , 'driver_deduction' : total_deducation})
		else:
			reward_calculation = total_revenue = total_car = total_deducation = total_deducatino_pecentage = 0
			picking_id = self.env['fleet.vehicle.trip.pickings'].search([('bsg_fleet_trip_id','=',self.trip_id.id),('loc_from','=',self.waypoint_from.id),('loc_to','=',self.waypoint_to.id)],limit=1)
			total_revenue = picking_id.picking_name.total_without_tax
			delivery = self.env['driver_reward_by_revenue'].search([])
			for data in self.survey_ids:
				if data.dedcution_way == 'percentage':	
					total_deducatino_pecentage += data.pecentage_amount
			if total_deducatino_pecentage > 1:
				total_deducation = (((reward_calculation * total_car) * total_deducatino_pecentage) / 100)
			lines_ids = self.arrival_line_ids.filtered(lambda l: l.state == 'shipped')
			for car_data in lines_ids:
				total_car += car_data.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.car_size.trailer_capcity

			for data in delivery:
				if data.from_km < total_revenue <= data.to_km:
					if total_revenue > 1:
						reward_calculation = ((total_revenue * data.amount_per_car) / 100 )
					if late_ariival_deduction and reward_calculation > 0:
						late_ariival_deduction = (reward_calculation * late_ariival_deduction / 100)
			self.write({'driver_reward_amount' : reward_calculation  , 'driver_deduction' : total_deducation})

	def _check_survay_done(self, trip_id, src, dest):
		# if self.finish_trip:
		# 	for line in trip_id.bsg_trip_arrival_ids:
		# 		if line.arrival_line_ids:
		# 			for item in line.arrival_line_ids:
		# 				if item.delivery_id.state != 'shipped':
		# 					line.is_done_survey = True
			
			trip_id.vehicle_id.daily_trip_count += 1

	# 
	def _compute_reward(self):
		for rec in self:
			rec.reward_calculation = 0.0
			total_km = rec.trip_id.route_id.total_distance
			delivery = rec.env['driver_reward_per_delivery'].search([])
			for data in delivery:
				if data.from_km < total_km <= data.to_km:
					rec.reward_calculation = total_km * data.amount_per_car

	# 
	def _computes_time(self):
		est_time = self.trip_id.route_id.waypoint_to_ids.search([('waypoint','=',self.waypoint_to.id)],limit=1).estimated_time
		self.est_trip_time = 0
		if self.actual_start_time and self.actual_end_time:
			start_time = self.actual_start_time
			end_time = self.actual_end_time
			time_delta_in_seconds = (end_time - start_time).total_seconds()
			timedelta_in_hours, second_reminder = divmod(time_delta_in_seconds, 3600)
			self.est_trip_time = timedelta_in_hours

	est_trip_time = fields.Float(string="Est. Duration", compute="_computes_time",track_visibility=True)
	waypoint_from = fields.Many2one(string="Source", comodel_name="bsg_route_waypoints",track_visibility=True,)
	waypoint_to = fields.Many2one(string="Destination", comodel_name="bsg_route_waypoints",track_visibility=True,)
	actual_start_time = fields.Datetime(string="Actual Start Time",track_visibility=True,)
	actual_end_time = fields.Datetime(string="Actual Arrival Time",track_visibility=True,)
	actual_time_duration = fields.Float(string="Actual Duration", compute="_compute_time",track_visibility=True,)
	parking_no = fields.Char(string="Park No",track_visibility=True,)
	drawer_no = fields.Char(string="Drawer No",track_visibility=True,)
	register_done = fields.Boolean(string="Registered?",track_visibility=True,)
	odoometer = fields.Float(string="Odoometer",track_visibility=True,)
	trip_id = fields.Many2one(string="Trip Id", comodel_name="fleet.vehicle.trip",track_visibility=True,)
	survey_id = fields.Many2one('survey.survey',track_visibility=True,)
	is_survey_done = fields.Boolean(string="Survey Done",default=True,track_visibility=True,)
	reg_skip_check = fields.Boolean(related="is_survey_done", string="Skip/Register Status",track_visibility=True,)
	arrival_line_ids = fields.One2many('fleet.trip.arrival.line','arrival_id',string="Arrival line",track_visibility=True,)
	arrival_survey_ids = fields.One2many('fleet.trip.survey.line','arrival_id',string="Survey line",track_visibility=True,)
	survey_ids = fields.Many2many('surver.question.config', string="Driver Assesment Surveys",track_visibility=True,)
	is_no_violation = fields.Boolean('No Violation')
	reward_calculation = fields.Float(string="Total Reward",compute="_compute_reward",track_visibility=True,)
	is_required = fields.Boolean(string="Required",track_visibility=True,)
	is_done_survey = fields.Boolean(string="Done Survet",track_visibility=True,)
	is_driver_reward_given = fields.Boolean(string="Driver Reward",track_visibility=True,)
	driver_reward_amount = fields.Float(string="Reward Amount",track_visibility=True,)
	driver_deduction = fields.Float(string="Deduction Amount",track_visibility=True,)
	finish_trip = fields.Boolean(string="Finish",track_visibility=True)

	@api.depends('actual_start_time', 'actual_end_time')
	def _compute_time(self):
		for rec in self:
			rec.est_trip_time = 0
			rec.actual_time_duration = 0
			if rec.actual_start_time and rec.actual_end_time:
				start_time = rec.actual_start_time
				end_time = rec.actual_end_time
				time_delta_in_seconds = (end_time - start_time).total_seconds()
				timedelta_in_hours, second_reminder = divmod(time_delta_in_seconds, 3600)
				rec.est_trip_time = timedelta_in_hours

	# @api.multi
	def action_update_parking(self):
		if self.parking_no:
			lines_ids = self.arrival_line_ids.filtered(lambda l: l.state == 'shipped')
			for line in lines_ids:
				if line.arrived:
					line.parking_no = self.parking_no

		view_id = self.env.ref('bsg_trip_mgmt.fleet_trip_arrival_form').id
		return {
		'type': 'ir.actions.act_window',
		'name': 'Trip Arrival',
		'view_mode': 'form',
		'view_type': 'form',
		'res_model': 'fleet.trip.arrival',
		'view_id': view_id,
		'res_id':  self.id,
		'target': 'new'}				

	# @api.multi
	def action_update_drawer(self):
		if self.drawer_no:
			lines_ids = self.arrival_line_ids.filtered(lambda l: l.state == 'shipped')
			for line in lines_ids:
				if line.arrived:
					line.drawer_no = self.drawer_no				

		view_id = self.env.ref('bsg_trip_mgmt.fleet_trip_arrival_form').id
		return {
		'type': 'ir.actions.act_window',
		'name': 'Trip Arrival',
		'view_mode': 'form',
		'view_type': 'form',
		'res_model': 'fleet.trip.arrival',
		'view_id': view_id,
		'res_id':  self.id,
		'target': 'new'}				


	# @api.multi
	def action_create_survey(self):
		# if self.arrival_line_ids:
		# 	for line in self.arrival_line_ids:
		# 		if not line.parking_check:
		# 			raise UserError(_("Please Fill Parking No first...!"))
		# 			break
		survey_id = self.env['survey.survey'].search([('is_driver','=',True)],limit=1)
		survey_id.write({'arrival_id' : self.id})
		self.ensure_one()
		self.is_survey_done = False
		return {
		'type': 'ir.actions.act_url',
		'name': "Results of the Survey",
		'target': 'self',
		'url': survey_id.with_context(relative_url=True).public_url + "/phantom"
		}

	def _create_odoometer(self, trip_id, src_loc, dest_loc, vehicle_id, driver_id, meter_value):
		odometer_obj = self.env['fleet.vehicle.odometer']
		if not odometer_obj.search([
			('fleet_trip_id', '=', trip_id),
			('src_location', '=', src_loc),
			('dest_location', '=', dest_loc),
			('vehicle_id', '=', vehicle_id)

		], limit=1):
			odometer_obj.sudo().create({
				'fleet_trip_id':trip_id,
				'src_location':src_loc,
				'dest_location':dest_loc,
				'vehicle_id':vehicle_id,
				'bsg_driver': driver_id,
				'value': meter_value,
				'unit':'kilometers',
				})


	# Get default local trip revenue
	@api.model
	def _default_local_trip_revenue(self):
		return self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('bsg_trip_mgmt.local_trip_revenue')

	def _register_arrival(self, trip_id):
		"""
		This method matching location to and location from and also drop location and retrun location 
		for delivering actual results
		"""
		self.actual_end_time = dt.datetime.now()
		destination = 0
		lines_ids = self.arrival_line_ids.filtered(lambda l: l.state == 'shipped')
		for line in lines_ids:
			branchRecord = self.env['branch.distance'].search([('branch_from','=',line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.pickup_loc.id),('branch_to','=',line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.drop_loc.id)], limit=1)
			trip_distance = branchRecord.distance
			if not trip_distance:
				trip_distance = 1
			if line.arrived:
				#  checking the location with from to pick drop and return
				if (((line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.loc_to.id or line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.return_loc_to.id) == line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.drop_loc.id)\
				and ((line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.loc_to.id or line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.drop_loc.id) == self.waypoint_to.id)) or line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.loc_to.location_type != 'albassami_loc':
					if trip_id not in line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.trip_history_ids.mapped('fleet_trip_id'):
						line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.trip_history_ids.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create({
							'fleet_trip_id':trip_id.id,
							'cargo_sale_line_id':line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.id,
							'trip_distance':trip_distance,
							'earned_revenue':0.0, # well be calculated on so_line.action_Delivered()
							})

					# if trip_id.trip_type != 'local':
					if line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.loc_to.location_type != 'albassami_loc' and line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.add_to_cc:
						line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.state = 'done'
					else:
						line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.action_Delivered()
					line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.arrival_status=True
				else:
					if line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.state != 'Delivered':
						if trip_id.trip_type != 'local':
							line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.action_on_transit()
							line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.arrival_status=True
						line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.pickup_loc = self.waypoint_to.id
						line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.drop_loc = line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.loc_to.id
						if trip_id not in line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.trip_history_ids.mapped('fleet_trip_id'):
							line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.trip_history_ids.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create({
								'fleet_trip_id':trip_id.id,
								'cargo_sale_line_id':line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.id,
								'trip_distance': trip_distance,
								'earned_revenue':0.0, # well be calculated on so_line.action_Delivered()
								})
							line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.fleet_trip_id = False
							line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.added_to_trip = False					
			else:
				if not line.arrived:
					if line.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).delivery_id.state != 'Delivered':
						continue

		destination = self.waypoint_to.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).loc_branch_id.id
		if trip_id.vehicle_id and not self._context.get('is_already_finished', False):
			trip_id.vehicle_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).current_branch_id = destination
			trip_id.vehicle_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).current_loc_id = self.waypoint_to.id

		trip_id.total_capacity = self._calculate_total_capacity(trip_id)

	def _calculate_total_capacity(self, trip_id):
		total_capacity = 0
		for line in trip_id.trip_waypoint_ids:
			if line.delivered_items:
				for saleline in line.delivered_items:
					if saleline.state == "shipped":
						total_capacity += saleline.car_size.trailer_capcity

		total_capacity = 8 - total_capacity
		return total_capacity

class BsgFleetTripArrival(models.Model):
	_name = 'fleet.trip.arrival.line'
	_description = "Trip Arrval Info"

	arrival_id = fields.Many2one('fleet.trip.arrival',string="Arrival ID")
	delivery_id = fields.Many2one("bsg_vehicle_cargo_sale_line",string="Delivery")
	state = fields.Selection(related="delivery_id.state", string="State")
	pickup_loc = fields.Many2one('bsg_route_waypoints', related="delivery_id.pickup_loc", store=True ,string="Pickup Location")
	drop_loc = 	fields.Many2one('bsg_route_waypoints', store=True, string="Drop")
	loc_to = 	fields.Many2one(comodel_name="bsg_route_waypoints", related="delivery_id.bsg_cargo_sale_id.loc_to",  string="Location To", readonly=True)
	parking_no = fields.Char(string="Park No")
	drawer_no = fields.Char(string="Drawer No")
	parking_check = fields.Boolean(string="Parking Check", compute='_compute_parking_no')
	car_maker_id = fields.Many2one('bsg_car_config',string='Car Maker',related="delivery_id.car_make",store=True)
	car_model_id = fields.Many2one('bsg_car_model',string='Car Model',related="delivery_id.car_model",store=True)
	chassis_no = fields.Char(string='Chassis No',related="delivery_id.chassis_no",store=True)
	plate_no = fields.Char(string='Plate No',related="delivery_id.general_plate_no",store=True)
	arrived = fields.Boolean(string='Arrival Check')
	actual_start_time = fields.Datetime(string="Actual Start Time",related="arrival_id.actual_start_time", store=True)
	route_waypoint_ids = fields.Many2many('bsg_route_waypoints', string='trip route waypoints')

	# 
	@api.depends('parking_no')
	def _compute_parking_no(self):
		for rec in self:
			rec.parking_check = True
			if rec.parking_no:
				rec.parking_check = True


class BsgFleetTripArrival(models.Model):
	_name = 'fleet.trip.survey.line'
	_description = "Trip Arrival Survey  Info"

	name = fields.Char(string="Question")
	arrival_id = fields.Many2one('fleet.trip.arrival',string="Arrival ID")
	category_id = fields.Many2one("survey.question.category",string="Category")
	dedcution_way = fields.Selection([('percentage','Percentage'),('fixed_amt','Fixed Amt'),('not_apply','Not Apply')],string="Deduction Way")
	deducation_amount = fields.Float(string="Deduction Amt")
	deserving = fields.Selection([('yes','Yes'),('no','No'),('stop_deserving','Stop Deserving'),('not_apply','Not Apply')],string="DeservIng")
	feedback = fields.Boolean(string="Feedback")
