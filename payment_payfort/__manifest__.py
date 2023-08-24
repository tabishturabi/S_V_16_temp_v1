# -*- coding: utf-8 -*-
#################################################################################
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
#################################################################################
{
  "name"                 :  "Payfort Payment Acquirer",
  "summary"              :  """The module allows the customers to make payment for their online orders with Payfort Payment Gateway on odoo website. The module integrates Payfort Payment Acquirer with Odoo.""",
  "category"             :  "Website",
  "version"              :  "1.1.8",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Saurabh Gupta",
  "website"              :  "https://store.webkul.com/Odoo-Payfort-Payment-Acquirer.html",
  "description"          :  """Odoo Payfort Payment Acquirer
Odoo with Payfort Payment Acquirer
Odoo Payfort Payment Gateway
Payment Gateway
Payfort Payment Gateway
Payfort integration
Payfort Integration
Payment acquirer
Payment processing
Payment processor
Website payments
Sale orders payment
Customer payment
IntegratePayfort payment acquirer in Odoo
Integrate Payfort payment gateway in Odoo""",
  "depends"              :  [
                             'payment',
      'account_payment'
                            ],
  "data"                 :  [
                             'security/groups.xml',
                             'views/payment_view.xml',
                             'views/template.xml',
                             'data/payment_payfort_data.xml',
                            ],
  "demo"                 :  [],
  "images"               :  ['static/description/banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  69.1,
  "currency"             :  "USD",
}
