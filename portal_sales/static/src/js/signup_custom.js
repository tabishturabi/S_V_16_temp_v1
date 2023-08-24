odoo.define('portal_sales.auth_signup_custom', function (require) {
    'use strict';
    
    var base = require('web_editor.base');
    var singup = require('auth_signup.signup');

    base.ready().then(function() {
        // Disable 'Sign Up' button to prevent user form continuous clicking
        if ($('.oe_signup_form').length > 0) {
            var order_required_fields = $(".oe_signup_form .form-control[required='required']");
            _.each(order_required_fields, function (field){
                var $elem = $(field);
                if ($elem.attr('id') != 'nationality_id')
                    $elem.parent().find('label').append("<b style='color:red;'> * </b>");
            });      
        
            $('.oe_signup_form').on('change', "select[name='customer_type']", function () {
                if($(this).val()){
                    var customer_type = $(this).val();
                    if (customer_type == '1'){
                        var default_country = $("input[name='default_country']").val();
                        $("select[name='customer_id_type']").val('saudi_id_card');
                        $("select[name='country_id']").val(default_country);

                        $("select[name='customer_id_type']").attr("disabled", true);
                        $("select[name='country_id']").attr("disabled", true);

                    }
                    if (customer_type == '2'){
                        $("select[name='customer_id_type']").val('iqama');
                        $("select[name='country_id']").val('');

                        $("select[name='customer_id_type']").attr("disabled", false);
                        $("select[name='country_id']").attr("disabled", false);
                    }
                }
            
            });       
            $('.oe_signup_form').on('submit', function (ev) {
                var $form = $(ev.currentTarget);
                $form.find(':disabled').each(function(e) {
                    $(this).removeAttr('disabled');
                });
            });
        
        }
    });
    
    
    });
