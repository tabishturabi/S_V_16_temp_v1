from odoo import models, fields, api, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    # @api.multi
    def _compute_work_order_count(self):
        for fleet in self:
            fleet.work_order_count = self.env['maintenance.request.enhance'].search_count(
                [('vehicle_id', '=', fleet.id)])

    # @api.multi
    def action_get_work_order_count(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('maintenance_enhance.maintenance_req_enh_action')
        res['domain'] = [('vehicle_id', 'in', self.ids)]
        return res

    work_order_count = fields.Integer('Number of Work Orders', compute='_compute_work_order_count')
