odoo.define('open_many2many_tags.many_two_many', function (require) {
"use strict";

var Fields = require('web.relational_fields');
var AbstractField = require('web.AbstractField');

var core = require('web.core');

var _t = core._t;
var qweb = core.qweb;
	
	Fields.FieldMany2ManyTags.include({
		events: _.extend({}, Fields.FieldMany2ManyTags.prototype.events, {
			'click .badge-pill': '_onOpenRecord',
		}),
		_onOpenRecord: function(event){
			var self = this;
			var context = this.record.getContext(this.recordParams)
			this.do_action({
				name: 'Open Record',
				res_model: this.value.model,
				res_id: $(event.target).parent().data('id'),
				views: [[false, 'form']],
				type: 'ir.actions.act_window',
				view_type: 'form',
				view_mode: 'form',
			});
		},
	})

})