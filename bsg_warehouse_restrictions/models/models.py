# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.osv import expression
import re
from odoo.tools import pycompat,float_is_zero
from odoo.tools.float_utils import float_round
from datetime import datetime
import operator as py_operator

class ResUsers(models.Model):
    _inherit = 'res.users'

    stock_warehouse_ids = fields.Many2many('stock.warehouse', 'res_user_stock_warehouse_rest', 'user_id',
                                           'warehouse_id', string='Allowed Warehouses')
    stock_warehouse_id = fields.Many2one('stock.warehouse', string='Current warehouse')

    stock_location_ids = fields.Many2many('stock.location', 'res_user_stock_location_rest', 'user_id', 'location_id',
                                          string='Allowed Warehouse Locations')
    default_location_ids = fields.Many2many('stock.location', 'res_user_stock_locations_rest_com', 'user_id',
                                            'location_id', compute='_compute_allow_locations', store=True,
                                            string='Computed Locations')
    current_location_ids = fields.Many2many('stock.location', 'res_user_stock_locations_rest_current', 'user_id',
                                            'location_id', compute='_compute_current_locations', store=True,
                                            string='Computed Current Locations')

    picking_type_ids = fields.Many2many('stock.picking.type', 'res_user_picking_type_rest', 'user_id',
                                        'picking_type_id', string='Allowed Warehouse Operations')
    default_picking_type_ids = fields.Many2many('stock.picking.type', 'res_user_picking_type_rest_com', 'user_id',
                                                'picking_type_id', compute='_compute_allow_pickings', store=True,
                                                string='Allowed Warehouse Operations')

    product_ids = fields.Many2many('product.product', 'res_user_products_rest', 'user_id', 'product_id',
                                   string='Allowed Products')
    #default_product_ids = fields.Many2many('product.product', 'res_user_products_rest_com', 'user_id', 'product_id',
    #                                       compute='_compute_allow_products', store=True, string='Computed Products')
    # domain_product_ids = fields.Many2many('product.product','res_user_products_rest_com_domain','user_id','product_id',compute='_compute_domain_products',store=True,string='Domain Products')

    product_category_ids = fields.Many2many('product.category', 'res_user_products_category_rest', 'user_id',
                                            'product_categ_id', string='Allowed Product Category')

    #default_product_template_ids = fields.Many2many('product.template', 'res_user_products_template_rest_com',
    #                                                'user_id', 'product_tmp_id',
    #                                                compute='_compute_allow_products_template', store=True,
    #                                                string='Computed Products Template')
    partner_location_ids = fields.Many2many('stock.location', 'res_user_stock_partner_location_rest', 'user_id',
                                            'location_id', string='Allowed Partner Locations',
                                            domain=[('usage', 'in', ['customer', 'supplier'])])
    '''@api.onchange('stock_warehouse_ids')
    def _onchange_stock_warehouse_ids(self):
        self.view_warehouse_location_id = False
        if self.stock_warehouse_ids:
            for rec in self.stock_warehouse_ids:
                self.view_warehouse_location_id += rec.view_location_id
                #self.default_picking_type_ids += self.default_picking_type_ids.search([('warehouse_id','=',rec.id)])
                #self.stock_location_ids += self.stock_location_ids.search([('id','child_of',rec.view_location_id.id)])'''

    @api.depends('stock_warehouse_ids', 'stock_warehouse_ids.view_location_id.child_ids', 'stock_location_ids',
                 'default_picking_type_ids', 'partner_location_ids')
    def _compute_allow_locations(self):
        for rec in self:
            rec.default_location_ids.unlink()
            if rec.stock_location_ids:
                rec.default_location_ids += rec.stock_location_ids
            elif rec.stock_warehouse_ids:
                rec.default_location_ids += rec.stock_location_ids.search(
                    [('id', 'child_of', rec.stock_warehouse_ids.mapped('view_location_id.id'))])
            if rec.partner_location_ids:
                rec.default_location_ids += rec.partner_location_ids
            if rec.default_picking_type_ids:
                rec.default_location_ids += rec.default_picking_type_ids.mapped(
                    'default_location_src_id') + rec.default_picking_type_ids.mapped('default_location_dest_id')
            rec.clear_caches()

    @api.depends('stock_warehouse_ids', 'picking_type_ids')
    def _compute_allow_pickings(self):
        for rec in self:
            rec.default_picking_type_ids.unlink()
            if rec.picking_type_ids:
                rec.default_picking_type_ids += rec.picking_type_ids
            elif rec.stock_warehouse_ids:
                rec.default_picking_type_ids += rec.picking_type_ids.search(
                    [('warehouse_id', 'in', rec.stock_warehouse_ids.ids)])
            rec.clear_caches()

    '''@api.depends('default_location_ids')
    def _compute_domain_products(self):
        for rec in self:
            if rec.default_location_ids:
                rec.domain_product_ids += rec.default_location_ids.mapped('quant_ids.product_id')'''

    '''@api.onchange('product_ids','default_location_ids')
    def _onchange_default_location_ids(self):
        return {'domain':{'product_ids':[('id','in',self.default_location_ids.mapped('quant_ids.product_id').ids)]}}'''

    '''@api.depends('product_category_ids','product_ids')
    def _compute_allow_products(self):
        for rec in self:
            rec.default_product_ids.unlink()
            if rec.product_ids:
                rec.default_product_ids += rec.product_ids
            elif rec.product_category_ids:
                rec.default_product_ids += rec.product_ids.search(
                    [('categ_id', 'child_of', rec.product_category_ids.ids)])
            rec.clear_caches()'''

    '''@api.depends('default_product_ids')
    def _compute_allow_products_template(self):
        for rec in self:
            rec.default_product_template_ids.unlink()
            rec.default_product_template_ids += rec.default_product_ids.mapped('product_tmpl_id')
            rec.clear_caches()'''

    @api.depends('stock_warehouse_id', 'default_location_ids')
    def _compute_current_locations(self):
        for rec in self:
            rec.current_location_ids.unlink()
            if rec.stock_warehouse_id:
                rec.current_location_ids += rec.default_location_ids.search(
                    [('id', 'child_of', rec.stock_warehouse_id.view_location_id.id)
                        , ('id', 'in', rec.default_location_ids.ids)])
            rec.clear_caches()

    # @api.multi
    def write(self, vals):
        if vals.get('warehouse-id'):
            self.env.user.update({'stock_warehouse_id': vals.get('warehouse-id')})
            self.env['ir.rule'].clear_cache()
        res = super(ResUsers, self).write(vals)
        return res


class StockLocation(models.Model):
    _inherit = 'stock.location'

    complete_name = fields.Char("Full Location Name", compute='_compute_complete_name', compute_sudo=True, store=True)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self._context.get('is_user_search') and self._context.get('stock_warehouse_ids'):
            stock_warehouse_ids = self.env['stock.warehouse'].browse(self._context.get('stock_warehouse_ids')[0][2])
            search_id = self.env['stock.location'].search(
                [('id', 'child_of', stock_warehouse_ids.mapped('view_location_id.id'))])
            domain = args or []
            domain += [
                ('id', 'in', search_id.ids)]
            rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
            return self.browse(rec).name_get()
        res = super(StockLocation, self)._name_search(name, args, operator, limit, name_get_uid=name_get_uid)
        return res

    '''@api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        res = super(StockLocation, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
        return res'''

    def name_get(self):
        ret_list = []
        for location in self:
            orig_location = location
            name = location.name
            while location.sudo().with_context(force_company=self.env.user.company_id.id,
                                               company_id=self.env.user.company_id.id).location_id and location.usage != 'view':
                location = location.sudo().with_context(force_company=self.env.user.company_id.id,
                                                        company_id=self.env.user.company_id.id).location_id
                if not name:
                    raise UserError(_('You have to set a name for this location.'))
                name = location.name + "/" + name
            ret_list.append((orig_location.id, name))
        return ret_list

    def get_putaway_strategy(self, product):
        ''' Returns the location where the product has to be put, if any compliant putaway strategy is found. Otherwise returns None.'''
        current_location = self
        putaway_location = self.env['stock.location']
        while current_location and not putaway_location:
            if current_location.putaway_strategy_id:
                putaway_location = current_location.putaway_strategy_id.putaway_apply(product)
            current_location = current_location.sudo().with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).location_id
        return putaway_location


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_out_of_restruction = fields.Boolean('Out Of Restruction')
    is_for_branch = fields.Boolean('Is For Branch')
    without_approve = fields.Boolean('Without P.R Approve')
    part_number = fields.Char('Part Number')
    
    @api.onchange('is_for_branch')
    def _onchange_product_is_for_branch(self):
        if self.is_for_branch:
            self.is_out_of_restruction = True
        if not self.is_for_branch:
            self.is_out_of_restruction = False


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_out_of_restruction = fields.Boolean('Out Of Restruction', related='product_tmpl_id.is_out_of_restruction',
                                           store=True)
    is_for_branch = fields.Boolean('Is For Branch', related='product_tmpl_id.is_for_branch', store=True)
    part_number = fields.Char('Part Number', related='product_tmpl_id.part_number', store=True)
    without_approve = fields.Boolean('Without P.R Approve',related='product_tmpl_id.without_approve', store=True)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            if operator in positive_operators:
                product_ids = self._search(['|',('default_code', '=', name),('part_number', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
                if not product_ids:
                    product_ids = self._search([('barcode', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
            if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                product_ids = self._search(args + ['|',('default_code', operator, name),('part_number', operator, name)], limit=limit)
                if not limit or len(product_ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(product_ids)) if limit else False
                    product2_ids = self._search(args + [('name', operator, name), ('id', 'not in', product_ids)], limit=limit2, access_rights_uid=name_get_uid)
                    print('..............product2_ids................',product2_ids)
                    print('..............product_ids................',product_ids)
                    # product_ids.extend(product2_ids)
            elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('name', operator, name),'|',('default_code', operator, name),('part_number', operator, name)],
                    ['&', ('name', operator, name),'|', ('default_code', '=', False),('part_number', '=', False)],
                ])
                domain = expression.AND([args, domain])
                product_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
            if not product_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    product_ids = self._search(['|',('default_code', '=', res.group(2)),('part_number', '=', res.group(2))] + args, limit=limit, access_rights_uid=name_get_uid)
            # still no results, partner in context: search on supplier info as last hope to find something
            if not product_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('name', '=', self._context.get('partner_id')),
                    '|','|',
                    ('product_code', operator, name),
                    ('part_number', operator, name),
                    ('product_name', operator, name)], access_rights_uid=name_get_uid)
                if suppliers_ids:
                    product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit, access_rights_uid=name_get_uid)
        else:
            product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        # return self.browse(product_ids).name_get()
        return product_ids

    def _get_domain_locations_new(self, location_ids, company_id=False, compute_child=True):
        operator = compute_child and 'child_of' or 'in'
        domain = company_id and ['&', ('company_id', '=', company_id)] or []
        locations = self.env['stock.location'].sudo().with_context(force_company=self.env.user.company_id.id,
                                                                   company_id=self.env.user.company_id.id).browse(
            location_ids)
        # TDE FIXME: should move the support of child_of + auto_join directly in expression
        hierarchical_locations = locations if operator == 'child_of' else locations.browse()
        other_locations = locations - hierarchical_locations
        loc_domain = []
        dest_loc_domain = []
        # this optimizes [('location_id', 'child_of', hierarchical_locations.ids)]
        # by avoiding the ORM to search for children locations and injecting a
        # lot of location ids into the main query
        for location in hierarchical_locations:
            loc_domain = loc_domain and ['|'] + loc_domain or loc_domain
            loc_domain.append(('location_id.parent_path', '=like', location.parent_path + '%'))
            dest_loc_domain = dest_loc_domain and ['|'] + dest_loc_domain or dest_loc_domain
            dest_loc_domain.append(('location_dest_id.parent_path', '=like', location.parent_path + '%'))
        if other_locations:
            loc_domain = loc_domain and ['|'] + loc_domain or loc_domain
            loc_domain = loc_domain + [('location_id', operator, other_locations.ids)]
            dest_loc_domain = dest_loc_domain and ['|'] + dest_loc_domain or dest_loc_domain
            dest_loc_domain = dest_loc_domain + [('location_dest_id', operator, other_locations.ids)]
        return (
            domain + loc_domain,
            domain + dest_loc_domain + ['!'] + loc_domain if loc_domain else domain + dest_loc_domain,
            domain + loc_domain + ['!'] + dest_loc_domain if dest_loc_domain else domain + loc_domain
        )

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        #Inherit For Stop Compute On-hand For Customer Location
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        to_date = fields.Datetime.to_datetime(to_date)
        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            domain_move_in += [('date', '>=', from_date)]
            domain_move_out += [('date', '>=', from_date)]
        if to_date:
            domain_move_in += [('date', '<=', to_date)]
            domain_move_out += [('date', '<=', to_date)]

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
        domain_move_out_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        quants_res = dict((item['product_id'][0], item['quantity']) for item in Quant.read_group([('location_id.usage', 'in', ['internal', 'transit','inventory', 'production'])]+domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            product_id = product.id
            rounding = product.uom_id.rounding
            res[product_id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(product_id, 0.0) - moves_in_res_past.get(product_id, 0.0) + moves_out_res_past.get(product_id, 0.0)
            else:
                qty_available = quants_res.get(product_id, 0.0)
            res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
            res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['virtual_available'] = float_round(
                qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                precision_rounding=rounding)

        return res

class ProductCategory(models.Model):
    _inherit = "product.category"

    product_ids = fields.One2many('product.product', 'categ_id', string='Products')
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True, compute_sudo=True)
    not_use_in_pr = fields.Boolean("Not Use In P.R")


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _get_removal_strategy(self, product_id, location_id):
        if product_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).categ_id.removal_strategy_id:
            return product_id.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).categ_id.removal_strategy_id.method
        loc = location_id
        while loc:
            if loc.removal_strategy_id:
                return loc.removal_strategy_id.method
            loc = loc.sudo().with_context(force_company=self.env.user.company_id.id,
                                          company_id=self.env.user.company_id.id).location_id
        return 'fifo'
