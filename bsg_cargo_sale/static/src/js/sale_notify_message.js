odoo.define('bsg_cargo_sale.warnning_message',function(require){
	"use strict";

var ListController = require('web.ListController')
var core = require('web.core');
var session = require('web.session');
var _t = core._t;
 
ListController.include({	
		renderButtons: function() {
			this._super.apply(this, arguments)
			var $message = this.$buttons.find('.o_sale_warnning_message');
			$message.hide();

			if (this.modelName == 'bsg_vehicle_cargo_sale')
			{
				
				var def_config = this._rpc({
					model: 'cargo_sale_order_config',
					method: 'search_read',
					fields: ['name','ar_message','en_message','show'],
				})
				.then(function (config) {
					_.each(config, function(conf){
						if (conf.show == true)
						{ 
							var msg = " ";
							if (session.user_context.lang.indexOf("en") !== -1)
								msg = _t(conf.en_message) +" "+ conf.name + _t(" Hours");
							if (session.user_context.lang.indexOf("ar") !== -1)
								msg = _t(conf.ar_message) +" "+ conf.name + _t(" سـاعة ");
							$message[0].textContent = msg
							$message.show();
						}
					})
					
				});
			}	
		},

			
		
	});
});
