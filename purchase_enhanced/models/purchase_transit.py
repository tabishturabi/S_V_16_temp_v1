from odoo import api, fields, models, _


class purchasetransit(models.Model):
    _name = 'purchase.transit'
    _description = "Purchase Transit"

    partner = fields.Many2one('res.partner',string="Partner")
    picking_type_id = fields.Many2one('stock.picking',string="Operation type")
    location_id = fields.Many2one('stock.location',string="Source Location")
    location_dest_id = fields.Many2one('stock.location',string="Destination")
    datetime = fields.Datetime('Scheduled Date',default=fields.Date.context_today)
    origin = fields.Char("Source Document")
    purchase_transit = fields.One2many('purchase.transit.line','purtran',string="Purchase Request Line")
    
class purchasetransitline(models.Model):
    _name = 'purchase.transit.line'
    _description = "Purchase Transit Line"

    preq = fields.Many2one('purchase.transit',string="Purchase Transit")
    product_id = fields.Many2one('product.product', string='Requested Product')
    intial = fields.Float("Initial Demand")
    reserved = fields.Float("Reserved",readonly =True)
    done = fields.Float("Done")

    