# -*- coding: utf-8 -*-
import math
import re
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests


class InspectionAssign(models.TransientModel):
    _name = 'inspection.assign'

    branch_id = fields.Many2one('bsg_branches.bsg_branches')
    employee_id = fields.Many2one('hr.employee', "Inspection Employee", required=True)

    def confirm_assign(self):
        inspection_id = self.env['bassami.inspection'].browse(self._context.get('active_id'))
        inspection_id.write({
            'assigned_employee_id': self.employee_id.id,
            'user_id': self.env.uid,
            'branch_ids': [(4, self.env.user.user_branch_id.id)] 
        })
class InspectionNoteLine(models.Model):
    _name = 'inspection.note.line'

    user_name = fields.Char('User Name')
    image = fields.Binary('Image')
    note = fields.Text('Notes')
    inspection_id = fields.Many2one('bassami.inspection')

class BsgVehicleCargoSaleLine(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'

    inspection_id = fields.Many2one(
        "bassami.inspection", "Inspection", track_visibility=True)

class BassamiInspection(models.Model):
    _name = 'bassami.inspection'
    _description = "Bassami Inspection"
    _inherit = ['portal.mixin', 'mail.thread']
    
    state = fields.Selection([('draft','Draft'),('underprocess','UnderProcess'),('approved','Approved'),
                              ('cancelled','Cancelled')], string='Status', track_visibility=True, default='draft')
    name = fields.Char('Inspection Number',  readonly=True,)
    cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale', 'Cargo Sale', track_visibility=True)
    cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line', 'Cargo Sale Line', track_visibility=True)
    customer = fields.Many2one(related='cargo_sale_id.customer', string="Customer")
    plate_no = fields.Char( string="Plate Number")
    car_make = fields.Many2one(related='cargo_sale_line_id.car_make', store=True)
    car_model = fields.Many2one(related='cargo_sale_line_id.car_model', store=True)
    chassis_no = fields.Char('Chassis Number')
    branch_from = fields.Many2one('bsg_route_waypoints', string="Branch From")
    branch_to = fields.Many2one('bsg_route_waypoints', string="Branch To")
    # Same label or string in odoo12 shows warning thatsy spaces are given for Attachments string.
    attachment_top_id = fields.Many2one('ir.attachment', string='Attachments ')
    attachment_top_binary = fields.Binary(related="attachment_top_id.datas")
    attachment_bottom_id = fields.Many2one('ir.attachment',string='Attachments  ')
    attachment_bottom_id_binary = fields.Binary(related="attachment_bottom_id.datas")
    attachment_left_id = fields.Many2one('ir.attachment',string='Attachments   ')
    attachment_left_binary = fields.Binary(related="attachment_left_id.datas")
    attachment_right_id = fields.Many2one('ir.attachment',string='Attachments')
    attachment_right_binary = fields.Binary(related="attachment_right_id.datas")
    attachment_car_image_id = fields.Many2one('ir.attachment',string='Attachments     ')
    attachment_car_image_binary = fields.Binary(related="attachment_car_image_id.datas")
    attachment_ids = fields.Many2many('ir.attachment', 'inspection_attachment_rel', 'inspection_id', 'attachment_id',
        string=' Attachments')
    count = fields.Integer('Pic Number')
    notes = fields.Text(string='Comments',track_visibility=True)
    digital_signature = fields.Binary(string='Signature')
    digital_signature_date = fields.Datetime('Signature Date & Time', readonly=True)
    user_id = fields.Many2one('res.users','Assigned Branch User', track_visibility=True)
    branch_ids = fields.Many2many('bsg_branches.bsg_branches', string="Branches", track_visibility=True)
    assigned_employee_id = fields.Many2one('hr.employee', "Assigned Employee")
    inspection_source = fields.Selection([('mobile_app', 'Mobile app'), ('inspection_points', 'Inspection Points'), ('odoo_mobile', 'Odoo Mobile'), ('odoo_wed', 'Odoo Web App')], 'Document source')
    hail_scratches = fields.Boolean()
    small_scratches = fields.Boolean()
    right_mirror = fields.Boolean()
    left_mirror = fields.Boolean()
    spare_tire = fields.Boolean()
    antena = fields.Boolean()
    media_player = fields.Boolean()
    remote_control = fields.Boolean()
    plate_number = fields.Char("App Plate Number")
    note_line_ids = fields.One2many('inspection.note.line', 'inspection_id', string='Note Lines')
    odoo_id =  fields.Many2one("hr.employee", string="Carried by")
    # chassis_no_2 = fields.Char('App Chassis No', readonly=True)
    # plate_no_2 = fields.Char('App Plate No', readonly=True)

    @api.model
    def save_car_sign(self, rec_id, comments, car_images, client_signature, sign_date):
        rec = self.browse(int(rec_id))
        Attachment = rec.create_or_write_image(rec.attachment_car_image_id, car_images, 'marked_car_image')
        rec.write({'attachment_car_image_id': Attachment,'count':rec.count + 1, 'notes': comments or rec.notes, 'digital_signature': client_signature, 'digital_signature_date': sign_date})

        return rec.id

    def sign_directly(self):
        action = self.env.ref('bassami_inspection.bassami_inspection_sign_page').read()[0]
        action['target'] = 'new'
        action['context'] = {'res_id': self.id}
        return action
        

    def assign_to_me(self):
        action = self.env.ref('bassami_inspection.action_inspection_assign')
        action = action.read()[0]
        action['context'] = {'default_branch_id':self.env.user.user_branch_id.id}
        return action
        # for rec in self:
        #     rec.write({
        #         'user_id': self.env.uid,
        #         'branch_ids': [(4, self.env.user.user_branch_id.id)]     
        #     })
        #     rec.user_id = self.env.uid

        # return True

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('bassami.inspection') or _('New')
        res = super(BassamiInspection, self).create(vals)
        if res.cargo_sale_line_id:
            last_sequence = max(res.cargo_sale_line_id.inspection_lines.mapped("sequence") or [0])
            sequence = last_sequence + 1
            values = {
                "sale_line_id": res.cargo_sale_line_id.id,
                "sequence": sequence,
                "employee_id": res.odoo_id.id,
                "branch_id": res.odoo_id.branch_id.id,
                "inspection_type": 'mobile',
                "date": fields.datetime.now(),
                "user_id": res.create_uid.id,
            }
            inspection_line = res.env["sale.inspection.line"].create(values)
        return res
    

    def action_send_to_progress(self):
        for rec in self:
            if not rec.user_id:
                raise UserError(
                    _('You have not Assign user. please check and Assign first user!'),
                )
            else:
                rec.state = 'underprocess'


    def action_approved(self):
        for rec in self:
            # if rec.cargo_sale_line_id:
            #     last_sequence = max(rec.cargo_sale_line_id.inspection_lines.mapped("sequence") or [0])
            #     sequence = last_sequence + 1
            # values = {
            #     "sale_line_id": rec.cargo_sale_line_id.id,
            #     "sequence": sequence,
            #     "employee_id": rec.odoo_id.id,
            #     "branch_id": rec.odoo_id.branch_id.id,
            #     "inspection_type": 'mobile',
            #     "date": fields.datetime.now(),
            #     "user_id": rec.create_uid.id,
            # }
            #     inspection_line = self.env["sale.inspection.line"].create(values)
            rec.state = 'approved'
            

    def action_cancelled(self):
        for rec in self:
            rec.state = 'cancelled'
            

    def action_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def create_or_write_image(self, attachment_id, image_data, screen):
        Attachment = self.env['ir.attachment']
        if not attachment_id:
            return Attachment.create({
                'name': str(self.name) + '-000'+ str(self.count)+(screen or ''),
                'datas': image_data,
                'store_fname': str(self.name) + '-000'+ str(self.count)+(screen or ''),
                'res_model': 'bassami.inspection',
                'res_id': self.id,
                'compnay_id':1,
            }).id
        attachment_id.write({
            'name': str(self.name) + '-000'+ str(self.count)+(screen or ''),
            'datas': image_data,
            'store_fname': str(self.name) + '-000'+ str(self.count)+(screen or ''),
            'res_model': 'bassami.inspection',
            'res_id': self.id,
            'compnay_id':1,
        })
        return attachment_id.id


    def action_tackimage(self, image_data=None, imagePic=None):
        for rec in self:
            if str(imagePic) == 'TopScrren':
                rec.create_or_write_image(rec.attachment_top_id, image_data, str(imagePic))
                return True
            elif str(imagePic) == 'LeftScrren':
                rec.create_or_write_image(rec.attachment_left_id, image_data, str(imagePic))
                return True
            elif str(imagePic) == 'RightScrren':
                rec.create_or_write_image(rec.attachment_right_id, image_data, str(imagePic))
                return True
            elif str(imagePic) == 'BottomScrren':
                rec.create_or_write_image(rec.attachment_bottom_id, image_data, str(imagePic))
                return True
            else:
                attachment = rec.create_or_write_image(False, image_data, False)
                rec.write({'attachment_ids':[(4, attachment)],'count':rec.count + 1})
                return True