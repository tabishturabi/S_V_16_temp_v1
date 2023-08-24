# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PartnerType(models.Model):
    _inherit = 'partner.type'

    is_default_in_portal = fields.Boolean('Default In Portal')
    
class BsgCarShipmentType(models.Model):
    _inherit = 'bsg.car.shipment.type'

    is_public = fields.Boolean()    

class resPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def signup_retrieve_info(self, token):
        """ retrieve the user info about the token
            :return: a dictionary with the user information:
                - 'db': the name of the database
                - 'token': the token, if token is valid
                - 'name': the name of the partner, if token is valid
                - 'login': the user login, if the user already exists
                - 'email': the partner email, if the user does not exist
                -customer_type
                -nationality_id
                -customer_id_type
                -identity_number
                -phone
        """
        partner = self._signup_retrieve_partner(token, raise_exception=True)
        res = {'db': self.env.cr.dbname}
        if partner.signup_valid:
            res['token'] = token
            res['name'] = partner.name
            res['phone'] = partner.phone
            
            res['customer_id_type'] = partner.customer_id_type

            if partner.customer_id_type == 'saudi_id_card':
                res['identity_number'] = partner.customer_id_card_no
                res['customer_type'] = '1'
            else: 
                res['identity_number'] = partner.iqama_no
                res['customer_type'] = '2'

            nationality_ids = self.env['res.country'].sudo().search([('visible_on_mobile_app','=',True)])
            #default_country = self.env['res.country'].sudo().search([('code', '=', 'SA'), ('phone_code', '=', '966')],limit=1).id

            res['nationality_ids'] = nationality_ids
            res['default_country'] = partner.country_id.id
        if partner.user_ids:
            res['login'] = partner.user_ids[0].login
        else:
            res['email'] = res['login'] = partner.email or ''
        return res 
