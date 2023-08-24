# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

class GetImage(models.TransientModel):
    _name = 'get.image'
    
    @api.model
    def default_get(self, fields):
        result = super(GetImage, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_id = self.env['bassami.inspection'].browse(int(active_id))
        result['is_other'] = self._context.get('is_other', False)
        if not result.get('is_other', False):
            result['images_top'] = active_id.attachment_top_id and active_id.attachment_top_id.datas or False
            result['images_left'] = active_id.attachment_left_id and active_id.attachment_left_id.datas or False
            result['images_bottom'] = active_id.attachment_bottom_id and active_id.attachment_bottom_id.datas or False
            result['images_right'] = active_id.attachment_right_id and active_id.attachment_right_id.datas or False
        return result

    images_top = fields.Binary('Top Pic')
    images_left = fields.Binary('Left Pic')
    images_bottom = fields.Binary('Bottom Pic')
    images_right = fields.Binary('Right Pic')
    images_other = fields.Binary('Addtional Pic')
    is_other = fields.Boolean()

    def action_confirm(self):
        for rec in self:
            active_id = self._context.get('active_id')
            active_id = self.env['bassami.inspection'].browse(int(active_id))
            if not rec.is_other:
                attachment_top_id = active_id.create_or_write_image(active_id.attachment_top_id, rec.images_top, 'TopScrren')
                attachment_left_id = active_id.create_or_write_image(active_id.attachment_left_id, rec.images_left, 'LeftScrren')
                attachment_right_id = active_id.create_or_write_image(active_id.attachment_right_id, rec.images_right, 'RightScrren')
                attachment_bottom_id = active_id.create_or_write_image(active_id.attachment_bottom_id, rec.images_bottom, 'BottomScrren')
                active_id.write({
                    'attachment_top_id' : attachment_top_id,
                    'attachment_left_id': attachment_left_id,
                    'attachment_right_id': attachment_right_id,
                    'attachment_bottom_id': attachment_bottom_id
                })
            else:
                attachment = active_id.create_or_write_image(False, rec.images_other, False)
                active_id.write({'attachment_ids':[(4, attachment)],'count':active_id.count + 1})
