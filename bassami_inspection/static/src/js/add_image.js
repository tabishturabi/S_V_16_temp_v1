odoo.define('bassami_inspection.sign_page', function (require) {
	"use strict";
	
	var core = require('web.core');
	var Widget = require('web.Widget');
	var Dialog = require('web.Dialog');
	var Session = require('web.session');
	require('web_editor.ready');
	var ajax = require('web.ajax');
	var base = require('web_editor.base');
	var rpc = require("web.rpc");
	var AbstractAction = require('web.AbstractAction');
	
	var qweb = core.qweb;
	var _t = core._t;
	
	
	var SignPage = AbstractAction.extend({
		template: 'sign_page',
	
		events: {
			"click .button_back": function(){
				this.destroy();
				$('.o_technical_modal').hide()
				$('.modal-backdrop').hide();
			},
			"click .button_submit": function(){
				// this.create_car_info();
				/*this.clear_session_data();*/
				// this.do_action('bassami_inspection.my_dev_action_sign_page');
				var self = this;
				var ca_damage = self.$("#signature1").jSignature("getData",'image')[1]
				var client_signature = self.$("#client_signature").jSignature("getData",'image')[1]
				var comments = self.$('#comment').val();
				var sign_date = moment().format("MM/DD/YYYY HH:MM:SS");
				this._rpc({
					model: 'bassami.inspection',
					method: 'save_car_sign',
					args: [Session.given_context_active_id,comments, ca_damage, client_signature, sign_date],
				}).then(function (record) {
					// self.destroy();
					$('.o_technical_modal').hide()
					$('.modal-backdrop').hide();
					return self.do_action({
						res_model: 'bassami.inspection',
						res_id: record,
						views: [[false, 'form']],
						type: 'ir.actions.act_window',
						view_type: 'form',
						view_mode: 'form',
					});
					// return self.do_action('bassami_inspection.action_bassami_inspection_needs_action');
				});

			},
		},
		create_car_info: function() {
			var self = this;
			var parts = [];
			$.each($("input[type='checkbox']"), function(){      
				if($(this).prop("checked") == true){
					parts.push(parseInt($(this).prop('id')));
				}      
			});
			var data = {
				'make': Session.make || this.$el.find('#make').val(),
				'vin_no': Session.vin_no || this.$el.find('#vin_no').val(),
				'contract_no': Session.contract_no,
				'description': Session.comment || this.$el.find('#comment').val(),
				'parts_ids': [[6, 0, parts]]
			}
			this._rpc({
				model: 'car.service.details',
				method: 'create',
				args: [data],
			}).then(function (record) {
				var capture_images = Session.capture_images;
				var sign = self.$("#signature1").jSignature("getData",'image')[1]
				self._rpc({
					model: 'car.service.details',
					method: 'store_data_on_local_pc',
					args: [Session.contract_no, capture_images, sign, record],
				});
				/*self._rpc({
					model: 'car.service.details',
					method: 'store_data_on_local_pc',
					args: [Session.contract_no, sign, record],
				});*/
				self.clear_session_data();
			});
		},
		clear_session_data: function() {
			this.$el.find('#make').val(''),
			this.$el.find('#vin_no').val(''),
			this.$el.find('#contract_no').val(''),
			this.$el.find('#comment').val(''),
			Session.default_parts_checked =  []
			Session.comment = '';
			Session.signature = '';
			Session.make = '';
			Session.vin_no = '';
			Session.parts = '';
			Session.selected_parts = [];
			Session.capture_images = [];
			Session.contract_no = '';
			this.do_action('my_dev.my_dev_action_main_menu_a');
		},
		store_in_session: function() {
			// Implement store all details in session.
	
			// store all checked items 
			// store description
			// store make, vin no
			// So when we next from first page we can use it to set defaults 
			Session.comment = this.$el.find('#comment').val();
			Session.signature = this.$el.find('#signature').val();
			Session.make = this.$el.find('#make').val();
			Session.vin_no = this.$el.find('#vin_no').val();
			var parts = [];
			$.each($("input[type='checkbox']"), function(){      
				if($(this).prop("checked") == true){
					parts.push($(this).prop('id'));
				}      
			});
			Session.selected_parts = parts;
		},
	
		init: function(parent, action) {
			// set all store details here ...
			Session.default_parts_checked = Session.default_parts_checked || []
			Session.comment = Session.comment || '';
			Session.signature = Session.signature || '';
			Session.make = Session.make || '';
			Session.vin_no = Session.vin_no || '';
			Session.parts = Session.parts || '';
			Session.selected_parts = Session.selected_parts || [];
			console.log(action);
			Session.given_context_active_id =  action.context.active_id;
			Session.active_action = action.context.params;
			// Yet, "_super" must be present in a function for the class mechanism to replace it with the actual parent method.
			this._super.apply(this, arguments);
			this.message_demo_barcodes = action.params.message_demo_barcodes;
		},
	
		start: function() {
			var self = this;
			this._super.apply(this, arguments);
			// self.$('#make').val(Session.make);
			// self.$('#vin_no').val(Session.vin_no);
			
		},
		// Signature
		initSign: function () {
				var self = this;
				self.$("#signature1").jSignature({
					'decor-color': '#FF0000',
					'color': '#000',
					'background-color': '#fff',
					'width':'100%',
					'height': '450px',
				});

				var image  = document.getElementsByClassName('car_image')[0];
				var canvas = document.getElementsByClassName('jSignature')[0];	
				var ctx = canvas.getContext('2d');
				ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
		},
	
		clearSign: function () {
			var self = this;
			self.$("#signature1").jSignature('reset');
		},
	
	
		destroy: function () {
			// clear all the session items 
			this._super();
		},
	
		render_options: function () {
			var self = this;
			var domain = []
			var default_parts_checked = Session.default_parts_checked
			self.initSign();
		}
	});
	
	core.action_registry.add('bassami_inspection_sign_page', SignPage);
	
	// return {
	//     MainMenu: MainMenu,
	// };
	return SignPage;
	
	});
	