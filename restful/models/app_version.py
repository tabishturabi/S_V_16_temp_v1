from odoo import models, fields, api

class MobileAppVersion(models.Model):
    _name = 'andriod.app.version'
    _order = 'create_date DESC'

    name = fields.Char('Version')
    release_notes = fields.Text('Release Notes')