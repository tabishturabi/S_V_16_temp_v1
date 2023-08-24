# -*- coding: utf-8 -*-

from odoo import fields,api,models,_

    
class CarSize(models.Model):
    _inherit = 'bsg_car_size'
    _description = 'Car Sizes'
    _rec_name = 'car_size_name'
     
    car_size_name = fields.Char('Car Size Name',required=True)
    length = fields.Integer('Length')
    width = fields.Integer('Width')
    car_old_id = fields.Integer('Car Old Id')
    height = fields.Integer('Height')
    trailer_capcity = fields.Integer('Aquiring Capacity',default=1,required=True)
    active = fields.Boolean('Active',default=True)
    
    
class CarMaker(models.Model):
    _name='bsg_car_make'
    _description = 'Car Maker'
    _rec_name = 'car_maker_name'
    
    car_make_name = fields.Char('Car Maker Name',required=True)
    car_make_ar_name = fields.Char('Arabic Name')
    car_make_old_id = fields.Integer('Maker Old Sys Id')
    active = fields.Boolean('Active',default=True)
    
class CarColor(models.Model):
    _name = 'bsg_vehicle_color'
    _description = 'Car Colors'
    _rec_name = 'car_color'
    
    vehicle_color_name = fields.Char('Car Color Arabic Name',required=True)
    active = fields.Boolean('Active',default=True)
    
class CarYear(models.Model):
    _name = 'bsg.car.year'
    _description = 'Car Years'
    _rec_name = 'car_year'
    
    car_year = fields.Char('Car Year',required=True)
    active = fields.Boolean('Active',default=True)
    
    
class CarModel(models.Model):
    _name = 'bsg_car_config'
    _description = 'Car Models'
    _rec_name = 'car_model'
    
    car_model = fields.Char('Car Model',required=True)
    car_maker = fields.Many2one('bsg_car_make',string ='Car Maker',required=True)
    active = fields.Boolean('Active',default=True)
    
class CarPlatno(models.Model):
    _name='bsg_plate_config'
    _description = 'car Plate no'
    _rec_name = 'plate_config'
    
    plate_config = fields.Char('Plate Config', required=True)
    active = fields.Boolean('Active',default=True)
    
    
    