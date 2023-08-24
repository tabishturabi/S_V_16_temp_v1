# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CheckDuplicate(models.TransientModel):

    _name = "calculate.value.wizard"
    _description = "Calcualte Value"

    yes_no = fields.Char()

    # @api.multi
    def check_value(self):
        search_id = self.env['fleet.vehicle.trip'].search([('id','=',self._context.get('default_id'))])
        if search_id:
            if search_id.trip_type == 'local' and len(search_id.stock_picking_id)>0:
                cargo_sale_lines_ids = search_id.stock_picking_id.mapped('picking_name')
                for rec in cargo_sale_lines_ids.ids:
                    line = self.env['bsg_vehicle_cargo_sale_line'].browse(rec)
                    if search_id.route_id.waypoint_from.id == line.loc_from.id:
                        line.write({'added_to_local_to_shipment_branch':True})
                    elif search_id.route_id.waypoint_from.id == line.loc_to.id:
                        line.write({'added_to_local_from_arriavl_branch': True})
        search_id.confim_data()