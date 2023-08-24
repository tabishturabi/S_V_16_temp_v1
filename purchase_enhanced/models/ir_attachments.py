from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    purchase_req_id = fields.Many2one('purchase.req', string="Purchase Request")

    # @api.multi
    def save_and_new2(self):
        view_id = self.env.ref('purchase_enhanced.view_attachment_form_purchase_req').id
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
    def action_save2(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}