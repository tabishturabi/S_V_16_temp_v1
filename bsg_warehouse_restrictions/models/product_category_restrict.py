# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression

class PutAwayStrategy(models.Model):
    # Migration Note
    # _inherit = 'product.putaway'
    _inherit = 'stock.putaway.rule'

    def _get_putaway_rule(self, product):
        if self.product_location_ids:
            put_away = self.product_location_ids.filtered(lambda x: x.product_id == product)
            if put_away:
                return put_away[0]
        if self.fixed_location_ids:
            categ = product.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).categ_id
            while categ:
                put_away = self.fixed_location_ids.filtered(lambda x: x.category_id == categ)
                if put_away:
                    return put_away[0]
                categ = categ.parent_id
        return self.env['stock.location']

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _search_rule(self, route_ids,packaging_id, product_id, warehouse_id, domain):
        """ First find a rule among the ones defined on the procurement
        group, then try on the routes defined for the product, finally fallback
        on the default behavior
        """
        if warehouse_id:
            domain = expression.AND([['|', ('warehouse_id', '=', warehouse_id.id), ('warehouse_id', '=', False)], domain])
        Rule = self.env['stock.rule']
        res = self.env['stock.rule']
        if route_ids:
            res = Rule.search(expression.AND([[('route_id', 'in', route_ids.ids)], domain]), order='route_sequence, sequence', limit=1)
        if not res:
            product_routes = product_id.route_ids | product_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).categ_id.total_route_ids
            if product_routes:
                res = Rule.search(expression.AND([[('route_id', 'in', product_routes.ids)], domain]), order='route_sequence, sequence', limit=1)
        if not res and warehouse_id:
            warehouse_routes = warehouse_id.route_ids
            if warehouse_routes:
                res = Rule.search(expression.AND([[('route_id', 'in', warehouse_routes.ids)], domain]), order='route_sequence, sequence', limit=1)
        return res