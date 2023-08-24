odoo.define('payments_enhanced.form_widgets', function (require) {
"use strict";

var core = require('web.core');
var FieldSelection = core.form_widget_registry.get('selection');

var MySelection = FieldSelection.extend({
    // add events to base events of FieldSelection
    
    events: _.defaults({
        // we will change of visibility on focus of field
        'focus select': 'onFocus'
    }, FieldSelection.prototype.events),
    onFocus: function() {
        
        
      if (
          // check values of fields. for example I need to check many fields
          this.field_manager.fields.name_field_1.get_value() == 'value1' &&
          this.field_manager.fields.name_field_2.get_value() == 'value2' /* && etc fields...*/   
      ) {
          // for example just hide all options. You can create any kind of logic here
          this.$el.find('option').hide();
          alert(this.field_manager.fields.name_field_1.get_value());
      } 
      alert('hi');
    }
    
});

// register your widget
core.form_widget_registry.add('selectionhide', MySelection);
});