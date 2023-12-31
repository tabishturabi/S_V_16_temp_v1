
# -*- coding: utf-8 -*-
#################################################################################
#   Copyright (c) 2017-Present CodersFort. (<https://codersfort.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://codersfort.com/>
#################################################################################


from . import models

def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    if server_serie!='12.0':
        raise Warning('Module support Odoo series 11.0 found {}.'.format(server_serie))
    return True