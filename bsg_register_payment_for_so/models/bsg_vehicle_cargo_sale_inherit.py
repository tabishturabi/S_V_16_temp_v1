# -*- coding: utf-8 -*-
import re
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BsgVehicleCargoSale(models.Model):
	_inherit = 'bsg_vehicle_cargo_sale'

	#for getting related information
	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []
		if name:
			args = ['|','|','|','|',('loc_to.loc_branch_id.branch_ar_name',operator, name),('loc_from_branch_id.branch_ar_name',operator, name),('customer.name',operator, name),('name',operator, name),('receiver_name', operator, name)]
		bsg_vehicle_cargo_sale_ids = self._search(args, limit=limit, access_rights_uid=None)
		return super(BsgVehicleCargoSale, self).name_search(name=name, args=args, operator=operator, limit=limit)