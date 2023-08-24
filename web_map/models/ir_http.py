# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def webclient_rendering_context(self):
        rendering_context = super(Http, self).webclient_rendering_context()
        rendering_context['google_maps_api_key'] = request.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('google_maps_api_key')
        return rendering_context

