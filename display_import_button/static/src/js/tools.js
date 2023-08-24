odoo.define('display_import_button.Tools', function(require) {
"use strict";

var AbstractView = require('web.AbstractView');
var session = require('web.session');

var Tools = AbstractView.include({
    init: function (viewInfo, params) {
        this._super(viewInfo, params);
        //this.controllerParams.activeActions['import'] = false;
        

        // Importation option on views
        if (session.can_import){
            var importation = this.arch.attrs.import ? JSON.parse(this.arch.attrs.import) : true;
            this.controllerParams.activeActions['import'] = importation;
        }
        else{
            this.controllerParams.activeActions['import'] = session.can_import;
        }
        
    },
    });

return Tools;

});
