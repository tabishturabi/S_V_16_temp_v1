odoo.define('bassami_inspection.web_came_screen', function (require) {
"use strict";
	
	var AbstractAction = require('web.AbstractAction');
	var core = require('web.core');
	var Session = require('web.session');
	var QWeb = core.qweb;
	var _t = core._t;
	var Dialog = require("web.Dialog");
	
	var WebCameScreen = AbstractAction.extend({
		events: {
			'click .back-to-record': '_onBackRecord',
			'click .confirm': '_onConfirm',
			'click .cancel': '_onCancel',
			
		},
	
		start: function () {
			var self = this;
			if (Session.car_data){
				self.data = Session.car_data.data
				self.$el.html(QWeb.render("DialogForWebCam", {widget: self}));
				self.Webcam_capture(self.$el)
				
			}else{
				var content = $('<div>').html(_t('<p>Plase Select Car Inspection Record:<p/>'));
				new Dialog(self, {
					title: _t('Warning!'),
					size: 'medium',
					$content: content,
					buttons: [
					{text: _t('Cancel'), close: true}]
				}).open();
				
			}
			return this._super.apply(this, arguments);
		},
	
		Webcam_capture: function (html_el) {
			var self = this;
			var camera_el = $(html_el).find('.web_cam');
//			var cameras = new Array(); //create empty array to later insert available devices
//			navigator.mediaDevices.enumerateDevices() // get the available devices found in the machine
//				.then(function(devices) {
//					devices.forEach(function(device) {
//						var i = 0;
//						if(device.kind=== "videoinput"){ //filter video devices only
//							cameras[i]= device.deviceId; // save the camera id's in the camera array
//							i++;
//						}
//				});
//			})
			if (camera_el.length == 1){
				Webcam.set({
					width: 380,
					height: 440,
					image_format: 'jpeg',
					jpeg_quality: 90,
					//sourceId: cameras[0],
//				     force_flash: true,
//				     flip_horiz: true,
//				     fps: 45,
					swfURL: '/bassami_inspection/static/src/js/webcam.swf',
				});
				Webcam.attach(camera_el[0]);
			}
			console.log("Webcam",Webcam)
//			if (Webcam.cameraIDs.length > 1) {
//				Webcam.cameraID = 1;
//				}
		},
		
		_onBackRecord: function (event) {
			var self = this;
			self.do_action({
				name: 'Car Inspection',
				res_model: 'bassami.inspection',
				res_id: parseInt(event.target.id),
				views: [[false, 'form']],
				type: 'ir.actions.act_window',
				view_type: 'form',
				view_mode: 'form',
			});
		},
		
		_onConfirm: function (event) {
			var self = this;
			Webcam.snap( function(data_uri) {
				if (data_uri){
					var image_data = data_uri.split(',')[1];
					console.log("data_uri",image_data)
					self._rpc({
						model: 'bassami.inspection',
						method: 'action_tackimage',
						args: [[parseInt(Session.car_data.data.id)] ,image_data, Session.imagePic],
					})
					.then(function(result) {
						Webcam.reset();
						self.do_action({
							name: 'Car Inspection',
							res_model: 'bassami.inspection',
							res_id: parseInt(Session.car_data.data.id),
							views: [[false, 'form']],
							type: 'ir.actions.act_window',
							view_type: 'form',
							view_mode: 'form',
						});
					});
				}
				
				
			});
		},
		
		_onCancel: function () {
			this.do_action('bassami_inspection.action_bassami_inspection', {})
		}
		
	});
	
	core.action_registry.add('web_came_screen', WebCameScreen);
	
	return WebCameScreen;

});
