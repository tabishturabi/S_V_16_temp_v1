odoo.define('web_map.FieldMap', function (require) {
	"use strict";

	var field_registry = require('web.field_registry');
	var AbstractField = require('web.AbstractField');

	var FormController = require('web.FormController');
	//var Model = require('web.Model');

	
	FormController.include({
		_update: function () {
			var _super_update = this._super.apply(this, arguments);
			this.trigger('view_updated');
			return _super_update;
		},
	});

	var FieldMap = AbstractField.extend({
		template: 'FieldMap',
		start: function () {
			var self = this;
			console.log("thissssssssssssssssssssssss", this)
			this.getParent().getParent().on('view_updated', self, function () {
				console.log("23 Inside")
				self.update_map();
				self.getParent().$('a[data-toggle="tab"]').on('shown.bs.tab', function () {
					console.log("26 Inside")
					self.update_map();
				});
			});
			return this._super();
		},
		update_mode: function () {
			if (this.isMap) {
				console.log("this.mode", this, this.mode)
				if (this.mode === 'readonly') {
					console.log("AAAAAAAAAAAA")
					this.map.setOptions({
						disableDoubleClickZoom: true,
						draggable: false,
						scrollwheel: false,
					});
					this.marker.setOptions({
						draggable: false,
						cursor: 'default',
					});
				} else {
					console.log("BBBBBB")
					this.map.setOptions({
						disableDoubleClickZoom: false,
						draggable: true,
						scrollwheel: true,
					});
					this.marker.setOptions({
						draggable: true,
						cursor: 'pointer',
					});
				}
			}
		},
		update_map: function () {
			console.log(">>>>>>offsetWidth>>>>>>>>", this, this.el.offsetWidth)
			if (!this.isMap && this.el.offsetWidth > 0) {
				console.log(">>>>>>>>>>>>>Inside lenght>")
				this.init_map();
				this.isMap = true;
			}
			this.init_map();
			this.isMap = true;
			console.log(">>>>>>>>>>>>>>>>>this Mpa", this.isMap)
			this.update_mode();
		},
		init_map: function () {
			var self = this;
			console.log("this.el", this.el)
			this.el.append("<div class='dircet'/>") //Append Value For Direction // Bug Not Working 
			this.directionsService = new google.maps.DirectionsService(); // Get Direction 
			this.directionsDisplay = new google.maps.DirectionsRenderer({ // Get Direction Display 
				draggable: true,
				suppressInfoWindows: true
			});
			this.geocoder = new google.maps.Geocoder(); // Get For Address
			this.map = new google.maps.Map(this.el, { // Load Map
				center: {
					lat: 0,
					lng: 0
				},
				zoom: 2,
				disableDefaultUI: true,
			});
			this.marker = new google.maps.Marker({ // Load Marker
				position: {
					lat: 0,
					lng: 0
				},
			});
			console.log("this.$('#directionsPanel')",this.$('#directionsPanel'))
			this.directionsDisplay.setMap(this.map); // Load Direction
			if (this.value) {
				this.marker.setPosition(JSON.parse(this.value).position);
				this.map.setCenter(JSON.parse(this.value).position);
				this.map.setZoom(JSON.parse(this.value).zoom);
				this.marker.setMap(this.map);
			}

			this.map.addListener('click', function (e) {
				// if(self.mode === 'edit' && self.marker.getMap() == null) {
				self.marker.setPosition(e.latLng);
				self.marker.setMap(self.map);
				self._setValue(JSON.stringify({
					position: self.marker.getPosition(),
					zoom: self.map.getZoom()
				}));
				//  }
			});
			this.map.addListener('zoom_changed', function () {
				//if(self.mode === 'edit' && self.marker.getMap()) {
				self._setValue(JSON.stringify({
					position: self.marker.getPosition(),
					zoom: self.map.getZoom()
				}));
				//}
			});
			this.marker.addListener('click', function () {
				// if(self.mode === 'edit') {
				self.marker.setMap(null);
				self._setValue(false);
				//}
			});
			this.marker.addListener('dragend', function () {
				self._setValue(JSON.stringify({
					position: self.marker.getPosition(),
					zoom: self.map.getZoom()
				}));
			});
			this.marker.addListener('click', function() {
		         // infowindow.open(self.map, self.marker);
		     });
			this.infowindow = new google.maps.InfoWindow()
			// if((this.recordData.origin) && this.recordData.destination){
			// 	this.calcRoute(); // Direction With Distion 
			// }
			this.getLatLan()
		},

		calcRoute: function () {
			console.log(">>>>>>>>>", this)
			var self = this;
			var request = {
				origin: this.recordData.origin, //' 23.033863, 72.585022',
				destination: this.recordData.destination, //"19.076090	72.877426",
				travelMode: google.maps.DirectionsTravelMode.DRIVING
			};
			this.directionsService.route(request, function (response, status) {
				if (status == google.maps.DirectionsStatus.OK) {
					self.directionsDisplay.setDirections(response);
				}
			});
		},
		
		getLatLan: function(){
			var self = this;
			google.maps.event.addListener(this.map, 'click', function( event ){
				console.log( "Latitude: "+event.latLng.lat()+" "+", longitude: "+event.latLng.lng() ); 
				console.log("self.recordData.satah_vehicale_id.data.id",self.recordData.satah_vehicale_id.data.id)
				self._rpc({
	                model: 'satah.vehicale.list',
	                method: 'write',
	                args: [self.recordData.satah_vehicale_id.data.id, {'location_lat':event.latLng.lat(),'location_long':event.latLng.lng()}],
	            }).then(function(re){
	            	self.do_notify('Your Location Update Sucessfully....')
	            });
//				var args = [self.recordData.satah_vehicale_id.data.id, 'location_lat', 'location_long'];
//				self._rpc({
//	                model: 'satah.vehicale.list',
//	                method: 'action_getLatLan',
//	                args: args,
//	                context: self.context,
//	            })
				self.geocoder.geocode({
				    'latLng': event.latLng
				  }, function(results, status) {
				    if (status == google.maps.GeocoderStatus.OK) {
				      if (results[0]) {
				          self.infowindow.setContent(results[0].formatted_address);
				    	  self.infowindow.open(self.map, self.marker);
				      }
				    }
				  });
			});
		}
	});

	field_registry.add('map', FieldMap);

	return {
		FieldMap: FieldMap,
	};

});