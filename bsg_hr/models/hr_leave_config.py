from odoo import api, fields, models

class HrSettings(models.Model):

    _name = "hr.leave.config"

    days_to_clearance = fields.Integer("Days_To Clearance",default=15)

    # def create(self, values):
    #     if len(self.search([])) > 1:
    #         return True
    #     else:
    #         return super().write(values)

