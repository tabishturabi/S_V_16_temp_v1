# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import Warning


class BsgRoute(models.Model):
    _name = 'bsg_route'
    _description = "Route"
    _inherit = ['mail.thread']
    _rec_name = "route_name"

    route_name = fields.Char()
    route_id = fields.Char(string="Route ID")
    active = fields.Boolean(string="Active", tracking=True, default=True)
    waypoint_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints")
    waypoint_to_ids = fields.One2many(comodel_name="bsg_route_line", inverse_name="route_id", string="route_line_ids")
    total_distance = fields.Float(string="Total Distance (KM)", compute="_compute_cites_and_distance")
    estimated_time = fields.Float(string="ETA (Hours)", compute="_compute_time")
    waypoint_to = fields.Char(compute="_compute_cites_and_distance", string="To")
    distance_adj = fields.Integer(string='Distance Adjustment', default=0)
    reason = fields.Text(string='Reason')
    waypoint_hide = fields.Many2one(string="From Hidden", comodel_name="bsg_route_waypoints", store=True)
    # route_type this field must have same options as fuel_expense_type in bsg_fleet_operations/models/fuel_expense_method.py
    route_type = fields.Selection([
        ('km', 'Domestic'),
        ('local', 'خدمي'),
        ('route', 'International'),
        ('port', 'Port'),
        ('hybrid', 'Hybrid Route')], string="Route Type",
        help='This is to determine if the route is international/domestic or between ports'
    )

    _sql_constraints = [
        ('code_route_id', 'Check(1=1)', 'The Route ID must be unique !')
    ]

    @api.depends('waypoint_to_ids')
    def _compute_cites_and_distance(self):
        for rec in self:
            distance = sum(line.distance for line in rec.waypoint_to_ids)
            rec.total_distance = distance + rec.distance_adj
            rec.waypoint_to = [i['waypoint']['route_waypoint_name'] for i in self.waypoint_to_ids]

    @api.depends('waypoint_to_ids')
    def _compute_time(self):
        self.estimated_time = 0.0
        if self.waypoint_to_ids:
            self.estimated_time = sum(line.estimated_time for line in self.waypoint_to_ids)

    def unlink(self):
        search_id = self.env['bsg_vehicle_cargo_sale'].search([('route', '=', self.id)])
        if search_id:
            raise Warning(_('You cannot Delete these Record is still Refrence'))
        result = super(BsgRoute, self).unlink()
        return result

    @api.onchange('waypoint_to_ids', 'waypoint_from')
    def _get_routeid_routename(self):
        self.route_id = None
        self.route_name = None
        if self.waypoint_from and self.waypoint_from.location_type == 'albassami_loc':
            self.route_id = self.waypoint_from.loc_branch_id.branch_no
            self.route_name = self.waypoint_from.loc_branch_id.branch_ar_name
        elif self.waypoint_from and self.waypoint_from.location_type != 'albassami_loc':
            self.route_id = str(self.waypoint_from.waypoint)
            self.route_name = str(self.waypoint_from.route_waypoint_name)
        else:
            self.route_id = None
            self.route_name = None

        if self.waypoint_to_ids:
            for x in self.waypoint_to_ids:
                if x.waypoint and x.waypoint.location_type == 'albassami_loc':
                    self.route_id = self.route_id or '' + '-' + str(x.waypoint.loc_branch_id.branch_no)
                    self.route_name = self.route_name or '' + '-' + str(x.waypoint.loc_branch_id.branch_ar_name)
                elif x.waypoint and x.waypoint.location_type != 'albassami_loc':
                    self.route_id = self.route_id or '' + '-' + str(x.waypoint.waypoint)
                    self.route_name = self.route_name or '' + '-' + str(x.waypoint.route_waypoint_name)
                else:
                    self.route_id = None
                    self.route_name = None

    def copy(self, default=None):
        """
            Create a new record in BsgRoute model from existing one 
            with line ids.
        """
        res = super(BsgRoute, self).copy(default)
        for line in self.waypoint_to_ids:
            self.env['bsg_route_line'].create({
                'waypoint': line.waypoint.id or False,
                'distance': line.distance or 0,
                'avg_speed': line.avg_speed or 0,
                'estimated_time': line.estimated_time or False,
                'currency_id': line.currency_id.id or False,
                'route_id': res.id
            })
        return res

    @api.onchange('waypoint_to_ids')
    def _waypoint_hide(self):
        for res in self:
            res.waypoint_hide = False
            for res_line in res.waypoint_to_ids:
                res.waypoint_hide = res_line.waypoint

    def write(self, vals):
        msg = _(
            """<div class="o_thread_message_content">
            <p>Route Old Value</p>
            <ul class="o_mail_thread_message_tracking">
            <li>To : <span>{waypoint_to}</span></li>
            <li>Route Name : <span>{route_name}</span></li>
            <li>Route ID : <span>{route_id}</span></li>
            <li>Waypoint From : <span>{waypoint_from}</span></li>
            <li>Route Type : <span>{route_type}</span></li>
            <li>Distance Adj : <span>{distance_adj}</span></li>
            <li>Reason : <span>{reason}</span></li>
            <li>Total Distance (KM) : <span>{total_distance}</span></li>
            <li>ETA (Hours) : <span>{estimated_time}</span></li>
            </ul>
            </div>
            """.format(
                waypoint_to=self.waypoint_to,
                route_name=self.route_name,
                route_id=self.route_id,
                waypoint_from=self.waypoint_from.route_waypoint_name,
                route_type=self.route_type,
                distance_adj=self.distance_adj,
                total_distance=self.total_distance,
                reason=self.reason,
                estimated_time=self.estimated_time
            )
        )
        self.message_post(body=msg)
        res = super(BsgRoute, self).write(vals)
        msg = _(
            """<div class="o_thread_message_content">
            <p>Route Modified Value</p>
            <ul class="o_mail_thread_message_tracking">
            <li>To : <span>{waypoint_to}</span></li>
            <li>Route Name : <span>{route_name}</span></li>
            <li>Route ID : <span>{route_id}</span></li>
            <li>Waypoint From : <span>{waypoint_from}</span></li>
            <li>Route Type : <span>{route_type}</span></li>
            <li>Distance Adj : <span>{distance_adj}</span></li>
            <li>Reason : <span>{reason}</span></li>
            <li>Total Distance (KM) : <span>{total_distance}</span></li>
            <li>ETA (Hours) : <span>{estimated_time}</span></li>
            </ul>
            </div>
            """.format(
                waypoint_to=self.waypoint_to,
                route_name=self.route_name,
                route_id=self.route_id,
                waypoint_from=self.waypoint_from.route_waypoint_name,
                route_type=self.route_type,
                distance_adj=self.distance_adj,
                total_distance=self.total_distance,
                reason=self.reason,
                estimated_time=self.estimated_time
            )
        )
        self.message_post(body=msg)
        return res


# car lines

class bsg_route_line(models.Model):
    _name = 'bsg_route_line'
    _description = "Route Lines"
    _inherit = ['mail.thread']
    _order = 'sequence asc'

    route_id = fields.Many2one(string="Route ID ", comodel_name="bsg_route", store=True)
    active = fields.Boolean(string="Active", tracking=True, default=True)
    sequence = fields.Integer(string="Sr No")
    waypoint = fields.Many2one(string="Cites",
                               comodel_name="bsg_route_waypoints")  # domain="[('id','!=', parent.waypoint_from)]"
    distance = fields.Float(string="Distance K.M")
    avg_speed = fields.Float(string="Ave Speed", default='40')
    estimated_time = fields.Float(string="EST Time", compute="_compute_time", store=True)
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    check_vals = fields.Char()

    @api.onchange('waypoint')
    def onchange_distance(self):
        if self.waypoint and self.route_id.waypoint_from and not self.route_id.waypoint_hide:
            distence_id = self.env['branch.distance'].search(
                [('branch_from', '=', self.route_id.waypoint_from.id), ('branch_to', '=', self.waypoint.id)], limit=1)
            self.distance = distence_id.distance
        elif self.waypoint and self.route_id.waypoint_hide:
            distence = self.env['branch.distance'].search(
                [('branch_from', '=', self.route_id.waypoint_hide.id), ('branch_to', '=', self.waypoint.id)], limit=1)
            self.distance = distence.distance
        else:
            self.distance = False

    @api.depends('distance', 'avg_speed')
    def _compute_time(self):
        self.estimated_time = 0.0
        if self.distance != 0 and self.avg_speed != 0:
            self.estimated_time = self.distance / self.avg_speed

    # 
    # @api.depends('distance','avg_speed')
    @api.onchange('distance', 'avg_speed')
    def _onchange_negative_vals(self):
        if self.distance:
            if float_compare(self.distance, 0.0, precision_rounding=self.currency_id.rounding) == -1:
                raise Warning(_('You cannot assign negative value in distance'))
        if self.avg_speed:
            if float_compare(self.avg_speed, 0.0, precision_rounding=self.currency_id.rounding) == -1:
                raise Warning(_('You cannot assign negative value in Ave Speed'))

    _sql_constraints = [
        ('value_bsg_route_line_uniq', 'Check(1=1)', 'This record already exists !')
    ]

    @api.model_create_multi
    def create(self, vals):
        res = super(bsg_route_line, self).create(vals)
        if res.distance:
            if float_compare(res.distance, 0.0, precision_rounding=res.currency_id.rounding) == -1:
                raise Warning(_('You cannot assign negative value in distance'))
        if res.avg_speed:
            if float_compare(res.avg_speed, 0.0, precision_rounding=res.currency_id.rounding) == -1:
                raise Warning(_('You cannot assign negative value in Ave Speed'))
        msg = _(
            """<div class="o_thread_message_content">
            <p>Route line Created</p>
            <ul class="o_mail_thread_message_tracking">
            <li>Sr No : <span>{sequence}</span></li>
            <li>Cites : <span>{waypoint}</span></li>
            <li>Distance K.M : <span>{distance}</span></li>
            <li>Ave Speed : <span>{avg_speed}</span></li>
            <li>EST Time : <span>{estimated_time}</span></li>
            </ul>
            </div>
            """.format(
                sequence=res.sequence,
                waypoint=res.waypoint.route_waypoint_name,
                distance=res.distance,
                avg_speed=res.avg_speed,
                estimated_time=res.estimated_time
            )
        )
        res.route_id.message_post(body=msg)
        return res

    def write(self, vals):
        msg = _(
            """<div class="o_thread_message_content">
            <p>Route line Old Value</p>
            <ul class="o_mail_thread_message_tracking">
            <li>Cites : <span>{waypoint}</span></li>
            <li>Distance K.M : <span>{distance}</span></li>
            <li>Ave Speed : <span>{avg_speed}</span></li>
            <li>EST Time : <span>{estimated_time}</span></li>
            </ul>
            </div>
            """.format(
                waypoint=self.waypoint.route_waypoint_name,
                distance=self.distance,
                avg_speed=self.avg_speed,
                estimated_time=self.estimated_time
            )
        )
        self.route_id.message_post(body=msg)
        res = super(bsg_route_line, self).write(vals)
        if self.distance:
            if float_compare(self.distance, 0.0, precision_rounding=self.currency_id.rounding) == -1:
                raise Warning(_('You cannot assign negative value in distance'))
        if self.avg_speed:
            if float_compare(self.avg_speed, 0.0, precision_rounding=self.currency_id.rounding) == -1:
                raise Warning(_('You cannot assign negative value in Ave Speed'))
        msg = _(
            """<div class="o_thread_message_content">
            <p>Route line Modified Value</p>
            <ul class="o_mail_thread_message_tracking">
            <li>Cites : <span>{waypoint}</span></li>
            <li>Distance K.M : <span>{distance}</span></li>
            <li>Ave Speed : <span>{avg_speed}</span></li>
            <li>EST Time : <span>{estimated_time}</span></li>
            </ul>
            </div>
            """.format(
                waypoint=self.waypoint.route_waypoint_name,
                distance=self.distance,
                avg_speed=self.avg_speed,
                estimated_time=self.estimated_time
            )
        )
        self.route_id.message_post(body=msg)
        return res

    def unlink(self):
        for rec in self:
            msg = _(
                """<div class="o_thread_message_content">
                <p>Route line Deleted</p>
                <ul class="o_mail_thread_message_tracking">
                <li>Sr No : <span>{sequence}</span></li>
                <li>Cites : <span>{waypoint}</span></li>
                <li>Distance K.M : <span>{distance}</span></li>
                <li>Ave Speed : <span>{avg_speed}</span></li>
                <li>EST Time : <span>{estimated_time}</span></li>
                </ul>
                </div>
                """.format(
                    sequence=rec.sequence,
                    waypoint=rec.waypoint.route_waypoint_name,
                    distance=rec.distance,
                    avg_speed=rec.avg_speed,
                    estimated_time=rec.estimated_time
                )
            )
            rec.route_id.message_post(body=msg)
        return super(bsg_route_line, self).unlink()
    #     search_id = self.env['bsg_vehicle_cargo_sale'].search(['|',('loc_from','=',self.waypoint.id),('loc_from','=',self.waypoint.id)])
    #     if search_id:
    #         raise Warning(_('You cannot Delete these Record is still Refrence'))
    #     result = super(bsg_route_line, self).unlink()
    #     return result
