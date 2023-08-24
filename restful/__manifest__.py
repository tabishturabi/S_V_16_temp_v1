{
    "name": "Odoo RESTFUL API",
    "version": "1.5.8",
    "category": "API",
    "author": "Babatope Ajepe",
    "website": "https://ajepe.github.io/blog/restful-api-for-odoo",
    "summary": "Odoo RESTFUL API",
    "support": "ajepebabatope@gmail.com",
    "description": """ RESTFUL API For Odoo
====================
With use of this module user can enable REST API in any Odoo applications/modules

For detailed example of REST API refer https://ajepe.github.io/restful-api-for-odoo
""",
    "depends": ["base","web", "bsg_cargo_sale"],
    "data": [
        "data/sequence.xml",
        "data/ir_config_param.xml",
        "views/ir_model.xml",
        "views/res_users.xml", 
        "security/ir.model.access.csv",
        "views/product.xml",
        "views/cash_credit_collection.xml",
        "views/other_service.xml",
        "views/res_country.xml",
        'views/account_payment.xml'
        ],
    "images": ["static/description/main_screenshot.png"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
