# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import Warning
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class bsg_price_config(models.Model):
    _name = 'bsg_price_config'
    _description = "Price Configuratioin"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "price_config_name"

    price_config_name = fields.Char(compute="_get_name", store=True)
    active = fields.Boolean(string="Active", tracking=True, default=True)
    waypoint_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints")
    waypoint_to = fields.Many2one(string="To", comodel_name="bsg_route_waypoints")
    customer_type = fields.Selection(string="Customer Type", selection=[
        ('individual', 'Individual'),
        ('corporate', 'Corporate'),
    ])
    price_line_ids = fields.One2many(string="price_line_ids",ondelete="cascade", comodel_name="bsg_price_line", inverse_name="price_config_id")
    is_update_price = fields.Boolean(string="Is Price Updated")
    
    _sql_constraints = [
    ('value_bsg_price_config_uniq', 'unique (waypoint_from,waypoint_to,customer_type)', 'This record already exists !')
    ]

    @api.model_create_multi
    def _run_price_update_cron(self):
        for data in self.search([('is_update_price','=',False)], limit=500):
            price = min_price = round_trip_price = 0
            for line_data in data.price_line_ids:
                if line_data.car_size.car_size_name == 'سيارة صغيرة':
                    price = round(line_data.price * 1.63)
                    min_price = round(line_data.min_price * 1.63)
                    round_trip_price = round(line_data.addtional_price * 1.63)
                elif line_data.car_size.car_size_name == 'نقل مميز صغيرة':
                    line_data.write({'price' : price,'min_price' : min_price , 'addtional_price' : round_trip_price})
            data.write({'is_update_price' : True})

    
    def unlink(self):
        for rec in self:
            search_id = self.env['bsg_vehicle_cargo_sale'].search([('loc_from','=',rec.waypoint_from.id),('loc_to','=',rec.waypoint_to.id)])
            if search_id:
                raise Warning(_('You cannot Delete these Record is still Refrence'))
        result = super(bsg_price_config, self).unlink()
        return result

    
    def toggle_active(self):
        _logger.info(">>>>>>>>>>>>>>>>>bsg_price_config, toggle_active ", str(self))
        for rec in self:
            if rec.price_line_ids:
                for line_id in rec.price_line_ids:
                    if line_id:
                        line_id.toggle_active()
            else:

                price_line_ids = self.env['bsg_price_line'].search(
                    [('price_config_id', '=', self.id), ('active', '=', False)])
                for line_id in price_line_ids:
                    if not line_id.active:
                        line_id.toggle_active()
        return super(bsg_price_config, self).toggle_active()


    
    def copy(self, default=None):
        """
            Create a new record in bsg_price_config model from existing one 
            with line ids.
        """
        default={
        'waypoint_from':False,
        'waypoint_to':False,
        'customer_type':False,
        }
        res =  super(bsg_price_config, self).copy(default)
        for line in self.price_line_ids:
            self.env['bsg_price_line'].create({'price_config_id' : res.id or False,
                                                       'car_size' : line.car_size.id or False,													   
                                                       'car_classfication' : line.car_classfication.id or False,
                                                       'service_type' : line.service_type.id or False,
                                                       'price' : line.price or 0.0,
                                                       'min_price' : line.min_price or 0.0,
                                                       'addtional_price': line.addtional_price or 0.0
                                                       })
        return res

    @api.onchange('waypoint_from')
    def _oncahnge_waypoint_from(self):
        if self.waypoint_from:
            domain = [('id', '!=', self.waypoint_from.id)]
            return {'domain': {'waypoint_to': domain}}

    @api.onchange('waypoint_to')
    def _oncahnge_waypoint_to(self):
        if self.waypoint_to:
            domain = [('id', '!=', self.waypoint_to.id)]
            return {'domain': {'waypoint_from': domain}}

    
    @api.depends('waypoint_from','waypoint_from')
    def _get_name(self):
        for rec in self:
            if rec.waypoint_from and rec.waypoint_to:
                rec.price_config_name = str(rec.waypoint_from.route_waypoint_name) +" to "+ str(rec.waypoint_to.route_waypoint_name)

# Price lines
class bsg_price_line(models.Model):
    _name = 'bsg_price_line'
    _description = "Price Lines"
    _inherit = ['mail.thread']
    _order = "car_size"	

    price_config_id = fields.Many2one(string="Price Config ID ",ondelete="cascade", comodel_name="bsg_price_config")
    active = fields.Boolean(string="Active",tracking=True, default=True)
    car_size = fields.Many2one(string="Car Size", comodel_name="bsg_car_size", required=True, on_delete="cascade")
    car_classfication = fields.Many2one(string="Car Classification", comodel_name="bsg_car_classfication", required=True, on_delete="cascade")
    service_type = fields.Many2one(string="Service Type", comodel_name="product.template", required=True, on_delete="cascade")
    price = fields.Float(string="Price", tracking=True)
    min_price = fields.Float(string="Min Price", tracking=True)	
    addtional_price = fields.Float(string="Round Trip Price")
    waypoint_from = fields.Many2one('bsg_route_waypoints',related="price_config_id.waypoint_from",string='From', store=True)
    waypoint_to = fields.Many2one('bsg_route_waypoints',related="price_config_id.waypoint_to",string='To',store=True)
    customer_type = fields.Selection(related="price_config_id.customer_type",string="Customer Type",store=True)

    _sql_constraints = [
    ('value_price_line_uniq', 'unique (price_config_id, car_size, car_classfication, service_type)', 'This record already exists !')
    ]

    
    @api.constrains('price','min_price','addtional_price')
    def _check_negative_values(self):
        if self.price <= 0:
            raise UserError(_('Price must be non-negative or zero.'))
        
        if self.min_price <= 0:
            raise UserError(_('Min Price must be non-negative or zero.'))
        
        if self.addtional_price <= 0:
            raise UserError(_('Round Trip Price must be non-negative or zero.'))

        if self.min_price > self.price:
            raise UserError(_('Min price can not be greater then Price.'))

    
    def toggle_active(self):
        for rec in self:
            _logger.info(">>>>>>>>>>>>>>>>>bsg_price_line, toggle_active ", str(self))
            msg = _(
                """<div class="o_thread_message_content">
                    <p>Price Config Line Data</p>
                    <ul class="o_mail_thread_message_tracking">
                    <li>Car Size : <span>{car_size}</span></li>
                    <li>Service Type : <span>{service_type}</span></li>
                    <li>Car Classification : <span>{car_classfication}</span></li>
                    <li>Price : <span>{price}</span></li>
                    <li>Min Price : <span>{min_price}</span></li>
                    <li>Round Trip Price : <span>{addtional_price}</span></li>
                    </ul>
                    </div>
                    """.format(
                    car_size=rec.car_size.car_size_name,
                    service_type=rec.service_type.name,
                    car_classfication=rec.car_classfication.car_class_name,
                    price=rec.price,
                    min_price=rec.min_price,
                    addtional_price=rec.addtional_price
                )
            )
            rec.price_config_id.message_post(body=msg)
        return super(bsg_price_line, self).toggle_active()

    #for tracking value on change on lie
    
    def write(self, vals):
        for rec in self:
            old_values = {
                'active': rec.active,
                'car_size': rec.car_size,
                'car_classfication': rec.car_classfication,
                'service_type': rec.service_type,
                'price': rec.price,
                'min_price': rec.min_price,
                'addtional_price': rec.addtional_price,
                'waypoint_from': rec.waypoint_from,
                'waypoint_to': rec.waypoint_to,
                'customer_type': rec.customer_type,
            }
            res = super(bsg_price_line, rec).write(vals)
            tracked_fields = rec.env['bsg_price_line'].fields_get(vals)
            changes, tracking_value_ids = rec._message_track(tracked_fields, old_values)
            if changes:
                rec.price_config_id.message_post(tracking_value_ids=tracking_value_ids)
            return res

    # 
    # def unlink(self):
    # 	search_id = self.env['bsg_vehicle_cargo_sale_line'].search([('car_size','=',self.car_size.id)])
    # 	print(search_id)
    # 	print(self.car_size.id)
    # 	print("search_id-------------------------")
    # 	if search_id:
    # 		raise Warning(_('You cannot Delete these Record is still Refrence'))
    # 	result = super(bsg_price_line, self).unlink()
    # 	return result

    
    def unlink(self):
        for rec in self:
            search_id = rec.env['bsg_vehicle_cargo_sale_line'].search([('price_line_id', '=', rec.id)])
            if search_id:
                raise Warning(_('You cannot Delete these Record is still Reference'))
            result = super(bsg_price_line, rec).unlink()
            return result

