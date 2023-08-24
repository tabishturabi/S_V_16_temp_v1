# -*- coding: utf-8 -*-
{
    "name": "Google Drive Odoo Integration",
    "version": "12.0.1.2.0",
    "category": "Document Management",
    "author": "faOtools",
    "website": "https://faotools.com/apps/12.0/google-drive-odoo-integration-278",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "cloud_base"
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {
        "python": []
},
    "summary": "The tool to automatically synchronize Odoo attachments with Google Drive files in both ways",
    "description": """
For the full details look at static/description/index.html

* Features * 
- Automatic integration
- Bilateral sync
- Sync any documents you like
- Easy accessible files
- Individual and team drives
- Sync logs in Odoo
- Default folders for documents
- Applicable to all Odoo apps
- Compatible with Odoo Enterprise Documents

* Extra Notes *
- How files and folders are synced from Odoo to Google Drive
- How items are retrieved from Google Drive to Odoo
- Typical use cases
- A few important peculiarities to take into account
- How Odoo Enterprise Documents are synced


#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "264.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=80&ticket_version=12.0&url_type_id=3",
}