# -*- coding: utf-8 -*-

from odoo import models, fields, api,_,tools
from odoo.exceptions import UserError

class TrailerVehicleConnectView(models.Model):
    _name = 'trailer.vehicle.connect.view'
    _auto = False

    name = fields.Char()
    taq_number = fields.Char(string="Taq No", track_visibility=True)
    chassis_number = fields.Char("Chassis Number")
    res_id = fields.Char()
    res_model = fields.Char()
    state = fields.Char()
    type = fields.Selection([('vehicle','Vehicle'),('trailer','Trailer')])

    # @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'trailer_vehicle_connect_view')
        self._cr.execute('''
            Create View trailer_vehicle_connect_view as ( 
                SELECT row_number() OVER (ORDER BY 1) AS id,
                T.res_id,T.name,T.taq_number,T.chassis_number,T.res_model,T.state,T.type from(
                    select id as res_id,trailer_config_name as name,
                    trailer_taq_no as taq_number,chassis_number as chassis_number,
                    state as state ,'bsg_fleet_trailer_config' as res_model , 'trailer' as type
                    from bsg_fleet_trailer_config
                    
                    UNION ALL
                    select  fleet_vehicle.id as res_id,fleet_vehicle.name,fleet_vehicle.taq_number as taq_number,
                    fleet_vehicle.vin_sn as chassis_number,fleet_vehicle_state.name::jsonb->>'en US' as state,
                    'fleet.vehicle' as res_model,'vehicle' as type
                    from fleet_vehicle ,fleet_vehicle_state
                    WHERE fleet_vehicle.state_id = fleet_vehicle_state.id
                 ) as T)''')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|',('name', operator, name), ('taq_number', operator, name)]
        fleet = self.search(domain + args, limit=limit)
        return fleet.name_get()

    '''@api.multi
    def name_get(self):
        res = []
        for vehicle in self:
            name = vehicle.taq_number
            print("%%%%%%%%%%%%%%%%%%%5",name,"#",vehicle)
            res.append((vehicle.id, name))
        return res'''
                   