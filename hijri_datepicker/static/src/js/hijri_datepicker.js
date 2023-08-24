odoo.define('hijri_datepicker', function (require) {
"use strict";
var core = require('web.core');
var datepicker = require('web.datepicker');
var datetimefield = require('web.basic_fields');
var time = require('web.time');
var field_utils = require('web.field_utils');
var session = require('web.session');

var _t = core._t;
var qweb = core.qweb;
var lang = '';
var date_format = 'dd/mm/Y';

    datepicker.DateWidget.include({
        
        start: function() {
            
            var def = new $.Deferred();;
            this.$input = this.$('input.oe_datepicker_master');
            this.$input_picker = this.$('input.oe_datepicker_container');
            this.$input_hijri = this.$el.find('input.oe_hijri');
            this.$input_hijri.hide();
            if (this.getParent().attrs){
                if(this.getParent().attrs.class == 'with_hijri'){
                    this.$input_hijri.show();
                    
                }
            }
            $(this.$input_hijri).val('');
            this._super();
            this.$input = this.$('input.oe_datepicker_master');
            var self = this;
            function convert_to_hijri(date) {
            	if (date.length == 0) {
            		return false
            	}
            	var jd = $.calendars.instance('islamic').toJD(parseInt(date[0].year()),parseInt(date[0].month()),parseInt(date[0].day()));
            	var date = $.calendars.instance('gregorian').fromJD(jd);
            	var date_value = new Date(parseInt(date.year()),parseInt(date.month())-1,parseInt(date.day()));
            	self.$el.find('input.oe_simple_date').val(self.formatClient(date_value, self.type_of_date));
            	self.change_datetime();
            }
            var custom_hijri_locale = moment.locale();
            if (custom_hijri_locale.indexOf("ar") !== -1) {
                $(self.$input_hijri).calendarsPicker({
                	calendar: $.calendars.instance('islamic','ar'),
                	dateFormat: date_format,
                	onSelect: convert_to_hijri,
                });
            }
            if (custom_hijri_locale.indexOf("fa") !== -1) {
                $(self.$input_hijri).calendarsPicker({
                	calendar: $.calendars.instance('islamic','fa'),
                	dateFormat: date_format,
                	onSelect: convert_to_hijri,
                });
            }
            else {
                $(self.$input_hijri).calendarsPicker({
                	calendar: $.calendars.instance('islamic'),
                	dateFormat: date_format,
                	onSelect: convert_to_hijri,
                });
            }
            
        },
        formatClient: function (value, type) {
            if (type == 'datetime'){
                var date_format = time.getLangDatetimeFormat();
            }
            if (type == 'date'){
                var date_format = time.getLangDateFormat();
            }
            return moment(value).format(date_format);
        },
        convert_greg_to_hijri: function(text) {
            if (text) {
            	var cal_greg = $.calendars.instance('gregorian');
            	var cal_hijri = $.calendars.instance('islamic');
            	var text = text._i;
            	if (text.indexOf('-')!= -1){
            		var text_split = text.split('-');
            		var year = parseInt(text_split[0]);
            		var month = parseInt(text_split[1]);
            		var day = parseInt(text_split[2]);

            		var jd = cal_greg.toJD(year,month,day);
                    var date = cal_hijri.fromJD(jd);
                    if (date)
                    {
                        var m = (date.month() >=10 ? date.month():"0"+date.month());
                        var d = (date.day() >=10 ? date.day():"0"+date.day());
                        $(this.$input_hijri).val(cal_hijri.formatDate(date_format, date));
                    }
                    else{
                        $(this.$input_hijri).val('');
                    }
            	}

            	if(text.indexOf('/')!= -1){
                   
                    var text_split = text.split('/');
            		var year = parseInt(text_split[2]);
            		var day = parseInt(text_split[0]);
            		var month = parseInt(text_split[1]);
                    var jd = cal_greg.toJD(year,month,day);
                    var date = cal_hijri.fromJD(jd);
                    if (date)
                    {
                        var m = (date.month() >=10 ? date.month():"0"+date.month());
                        var d = (date.day() >=10 ? date.day():"0"+date.day());
                        $(this.$input_hijri).val(cal_hijri.formatDate(date_format, date));
                    }
                    else{
                        $(this.$input_hijri).val('');
                    }    
                    
            	}
            }
        },
        set_value_from_ui: function() {
            
            var value = this.$input.val() || false;
            this.value = this._parseClient(value);
            if (this.oldValue){
            this.newValue = this.value;
            }
            this.setValue(this.value);
            this.convert_greg_to_hijri(this.value);
            
        },
        set_readonly: function(readonly) {
            this._super(readonly);
            this.$input_hijri.prop('readonly', this.readonly);
        },
        change_datetime: function(e) {
        	this._setValueFromUi();
        	this.trigger("datetime_changed");
        },
        changeDatetime: function () {
            
            if (this.isValid()) {
                var oldValue = this.getValue();
                if (!this.oldValue){
                this.oldValue = this.getValue();
                }
                
                
                if(this.oldValue !== this.newValue){
                this.set_value_from_ui();
                }
                var newValue = this.getValue();
                
                var hasChanged = !oldValue !== !newValue;
                if (oldValue && newValue) {
                var formattedOldValue = oldValue.format(time.getLangDatetimeFormat());
                var formattedNewValue = newValue.format(time.getLangDatetimeFormat())
                if (formattedNewValue !== formattedOldValue) {
                    hasChanged = true;
                }
                }
                if (hasChanged) {
                    
                // The condition is strangely written; this is because the
                // values can be false/undefined
                this.trigger("datetime_changed");
                }
            }
        },
    });

    datetimefield.FieldDate.include({
        start: function () {
            var self = this;
            this._super();
            if (this.mode === 'readonly') {
                var date_value = $(this.$el).text();
                var hij_date = self.convert_greg_to_hijri(this.value);
                if(this.attrs.class == 'with_hijri'){
                    this.$el.append("<div><span class='oe_hijri'>"+hij_date+"</span></div>");
                }
                
            }
            //return $.when(def, this._super.apply(this, arguments));
            return true;
        },
        

        convert_greg_to_hijri: function(text) {
            if (text) {
            	var cal_greg = $.calendars.instance('gregorian');
                var cal_hijri = $.calendars.instance('islamic');
                var text = text._i;
            	if (text.indexOf('-')!= -1){
            		var text_split = text.split('-');
            		var year = parseInt(text_split[0]);
            		var month  = parseInt(text_split[1]);
                    var day = parseInt(text_split[2]);

            		var jd = cal_greg.toJD(year,month,day);
                    var date = cal_hijri.fromJD(jd);
                    if(date)
                    {
                	var m = (date.month() >=10 ? date.month():"0"+date.month());
                    var d = (date.day() >=10 ? date.day():"0"+date.day());
                    
                    return cal_hijri.formatDate(date_format, date);
                    }
                    else{
                        return '';
                    }
            	}

            	if(text.indexOf('/')!= -1){
            		var text_split = text.split('/');
            		var year = parseInt(text_split[2]);
            		var day = parseInt(text_split[0]);
                    var month = parseInt(text_split[1]);
            		var jd = cal_greg.toJD(year,month,day);
                    var date = cal_hijri.fromJD(jd);
                    if(date){
                	var m = (date.month() >=10 ? date.month():"0"+date.month());
                    var d = (date.day() >=10 ? date.day():"0"+date.day());
                    return cal_hijri.formatDate(date_format, date);
                    }
                    else{
                        return '';
                    }
            	}
            }
        },
    });

});
