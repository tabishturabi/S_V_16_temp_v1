from odoo import api, SUPERUSER_ID
from datetime import datetime, timedelta, timezone


def post_init_hook(cr, registry):
    pass
    # env = api.Environment(cr, SUPERUSER_ID, {})
    # model_id = env['vehicle.model.year']
    # for rec in model_id:
    #     if rec:
    #         rec.name = '2000'
    #         print('..........model_id',model_id.id)
    # model_id.create({
    #     'name': '1950'
    # })
    # for num in range(1900,(datetime.now().year) + 1):
    #     if num:
    #         print('.........model year........',model_id.id)
    #         model_id.create({
    #             'name':str(num)
    #         })

