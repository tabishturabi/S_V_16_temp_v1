# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

{
    "name":  "Tamara Payment Connect",
    "summary":  "Tamara Payment Connect",
    "category":  "Accounting",
    "version":  "12.77.27",
    "sequence":  1,
    "author":  "Webkul Software Pvt. Ltd.",
    "license":  "Other proprietary",
    "website":  "https://store.webkul.com/",
    "description":  """Tamara Payment Connect""",
    "depends":  [
        'payment','bsg_cargo_sale','portal','payment_payfort'
    ],
    "data":  [
        # 'security/ir.model.access.csv',
        'wizard/cargo_sale_tamara_wiz.xml',
        'views/payment_acquirer.xml',
        'views/payment_tamara_templates.xml',
        # 'views/account_invoice.xml',
        'data/tamara_payment_data.xml',
        'views/bsg_cargo_sale.xml',
        'views/account_payment.xml',
    ],
    "images":  ['static/description/Banner.gif'],
    "application":  True,
    "installable":  True,
    "price":  149,
    "currency":  "USD",
    "pre_init_hook":  "pre_init_check",
}
