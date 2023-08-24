from odoo import fields, models, api, exceptions, _


class FleetVehicleTrip(models.Model):
    _inherit = 'fleet.vehicle.trip'


    bayan_config_active = fields.Boolean(string="Is Bayan Config Active", compute="_compute_baya_config_id")
    bayan_trip_id = fields.Many2one('bayan.data', track_visibility=True, string="Bayan Trip ID")
    bayan_status = fields.Selection([('draft', 'Draft'), ('success', 'Success'), ('failed', 'Failed')],
                                    string="Bayan Status", track_visibility=True, related='bayan_trip_id.state')

    def _compute_baya_config_id(self):
        bayan_config = self.env.ref('bayan_api.bayan_config_settings_data')
        for rec in self:
            rec.bayan_config_active = False
            if bayan_config and bayan_config.is_active:
                rec.bayan_config_active = True

    
    def action_get_bayan_pdf(self):
        if self.bayan_trip_id:
            return self.bayan_trip_id.action_get_bayan_pdf_v2()

    
    def action_start_trip(self):
        res = super(FleetVehicleTrip, self).action_start_trip()
        if self.bayan_config_active:
            if not self.bayan_trip_id:
                self.bayan_trip_id.action_create_api()
        return res
