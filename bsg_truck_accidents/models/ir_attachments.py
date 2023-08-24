from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class BsgTruckAccident(models.Model):
    _inherit = 'ir.attachment'

    truck_accident_attach = fields.Many2one('truck.accident.attachment', string="Truck Accident Type")

    # @api.multi
    @api.onchange('truck_accident_attach')
    def get_name_truck_accident_attach(self):
        if self.truck_accident_attach:
            self.name = self.truck_accident_attach.name

    @api.constrains('datas')
    def _check_truck_accident_attachment(self):
        if self.truck_accident_attach:
            if 'pdf' not in self.mimetype and 'png' not in self.mimetype and 'jpeg' not in self.mimetype:
                raise ValidationError("Cannot upload file different from .pdf,png,jpeg file")

    # @api.multi
    def save_and_new(self):
        view_id = self.env.ref('bsg_truck_accidents.view_attachment_form_for_truck_accident').id
        default_res_model = self.env.context.get('default_res_model')
        default_res_id = self.env.context.get('default_res_id')
        return {
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'view_type': 'form',
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (default_res_model, default_res_id),
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }

    # @api.multi
    def action_save(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}