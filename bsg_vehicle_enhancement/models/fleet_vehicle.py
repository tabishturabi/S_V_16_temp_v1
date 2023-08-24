from odoo import _, api, fields, models


class FleetVehicleExt(models.Model):
    _inherit = 'fleet.vehicle'

    # @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'fleet.vehicle'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for fleet in self:
            fleet.attachment_number = attachment.get(fleet.id, 0)

    # @api.multi
    def open_attach_wizard(self):
        view_id = self.env.ref('bsg_vehicle_enhancement.view_attachment_fleet_form').id
        return {
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'view_type': 'form',
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id),
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }

    # @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        if self.env.user.has_group(
                'bsg_vehicle_enhancement.group_fleet_attachment_delete') or self.env.user._is_admin():
            res = self.env['ir.actions.act_window'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).for_xml_id('bsg_vehicle_enhancement', 'action_attachment_fleet_all_access')
        else:
            res = self.env['ir.actions.act_window']._for_xml_id('bsg_vehicle_enhancement.action_attachment_fleet_less_access')
        res['domain'] = [('res_model', '=', 'fleet.vehicle'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'fleet.vehicle', 'default_res_id': self.id, }
        return res

    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')

    # @api.multi
    def _compute_trips_number(self):
        for fleet in self:
            fleet.trips_number = self.env['fleet.vehicle.trip'].search_count([('vehicle_id', '=', fleet.id)])

    # @api.multi
    def action_get_trips_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_trip_mgmt.action_fleet_vehicle_trip_all')
        res['domain'] = [('vehicle_id', 'in', self.ids)]
        return res

    trips_number = fields.Integer('Number of Trips', compute='_compute_trips_number')

    # @api.multi
    def _compute_assign_number(self):
        for fleet in self:
            fleet.driver_assign_count = self.env['driver.assign'].search_count([('fleet_vehicle_id', '=', fleet.id)])

    # @api.multi
    def action_get_assigned_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_fleet_operations.bsg_driver_assign_action')
        res['domain'] = [('fleet_vehicle_id', 'in', self.ids)]
        return res

    driver_assign_count = fields.Integer('Number of Driver Assign', compute='_compute_assign_number')

    # @api.multi
    def _compute_unassigned_number(self):
        for fleet in self:
            fleet.driver_unassigned_count = self.env['driver.unassign'].search_count([('fleet_vehicle_id', '=', fleet.id)])

    # @api.multi
    def action_get_unassigned_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_fleet_operations.bsg_driver_unassign_action')
        res['domain'] = [('fleet_vehicle_id', 'in', self.ids)]
        return res

    driver_unassigned_count = fields.Integer('Number of Driver Assign', compute='_compute_unassigned_number')


    # @api.multi
    def _compute_bx_trip(self):
        for fleet in self:
            fleet.bx_trip_count = self.env['transport.management'].search_count([('transportation_vehicle', '=', fleet.id)])

    # @api.multi
    def action_get_bx_trip(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('transport_management.transport_management_action')
        res['domain'] = [('transportation_vehicle', 'in', self.ids)]
        return res

    bx_trip_count = fields.Integer('Number of Bx Trips', compute='_compute_bx_trip')
