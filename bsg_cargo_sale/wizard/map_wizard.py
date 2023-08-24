# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

class MapWizard(models.TransientModel):
    _name = 'map.wizard'
    _description = 'Wizard Map'
    
    @api.model
    def default_get(self, fields):
        result = super(MapWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_id = self.env['satah.vehicale.list'].browse(int(active_id))
        result['satah_vehicale_id'] = active_id.id
        if active_id.loc_src and active_id.loc_dest:
            result['origin'] = str(active_id.loc_src.location_lat)+','+str(active_id.loc_src.location_long)
            result['destination'] = str(active_id.loc_dest.location_lat)+','+str(active_id.loc_dest.location_long)
        return result
    
    origin = fields.Text('origin')
    destination = fields.Text('destination')
    map = fields.Text('Map')
    satah_vehicale_id = fields.Many2one('satah.vehicale.list', 'Satah Vehicale')
