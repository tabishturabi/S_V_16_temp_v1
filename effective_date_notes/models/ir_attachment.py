from odoo import api, fields, models


class IrAttachmentExt(models.Model):
    _inherit = "ir.attachment"

    effective_id = fields.Selection(string="Doucment Type",
                                          selection=[('effect',
                                                      'Effective Date Request'),
                                                     ('vacation',
                                                      'Return From Vacation')],
                                          track_visibility=True)
