odoo.define('portal.cargo.sale.line.create', function (require) {
    'use strict';
    
        require('web.dom_ready');
        var core = require('web.core');
        var rpc = require("web.rpc");
        var config = require('web.config');
        var isMobile = config.device.isMobile;
        
        var _t = core._t;
        if (!$('.o_portal').length) {
            return $.Deferred().reject("DOM doesn't contain '.o_portal'");
        }
    
        if ($('#o_portal_cargo_sale_order_line_form').length) {
            var hasError = false ;
            var inStart = true;

            if (isMobile){
                $('#create_new').removeAttr('class');
                $('#create_new').removeAttr('aria-labelledby');
                $('#create_new').removeAttr('dialog');
                $('#create_line_btn').on('click', function(e){
                    $(this).removeAttr('data-toggle');
                    $('#create_new').attr('aria-hidden',false);
//                    $(this).hide();
                });
                $('#create_order_line_popup_close').on('click', function(e){
                    $('#create_new').attr('aria-hidden',true);
                    $('#create_line_btn').show();
                });

            }

            var checkCurrentRequiredField = (field)=>{
                // validation code here
                hasError = false;
                var alert_area;
                if (field.attr('required') == 'required'){
                    field.removeClass("is-invalid");

                    if(field.next("div[role='alert']").length)
                    {    
                        alert_area = field.next("div[role='alert']");
                    }
                    else if (field.parent().find("div[role='alert']").length)
                    {
                        alert_area = field.parent().find("div[role='alert']");
                    }

                    if (alert_area){
                        alert_area.hide();
                        alert_area.text('');
                        if(!field.val()){
                            alert_area.text(_t('This Field Is Required'));
                            alert_area.show();
                            hasError = true;
                        }
                    }      
                }
           };



            var required_fields = $("#o_portal_cargo_sale_order_line_form .form-control[required='required']");
            _.each(required_fields, function (field){
                
                var $elem = $(field);
                $elem.parent().parent().find('.col-form-label').append("<b style='color:red;'> * </b>");
                //$elem.closest("col-form-label").text().append("*");
            });

            var model_options = $("#o_portal_cargo_sale_order_line_form select[name='car_model']:enabled option:not(:first)");
            var first_option = $("#o_portal_cargo_sale_order_line_form select[name='car_model']:enabled option:first").val();


            $('#o_portal_cargo_sale_order_line_form').on('change', "input[name='plate_no']", function () {
                var input=$(this);
                if(input.val()){
                    var register_val = $("#o_portal_cargo_sale_order_line_form").find("select[name='plate_registration']");
                    if(register_val.val() == 'saudi' || register_val.val() == 'non-saudi'){
                        if(isNaN(input.val())){
                            input.addClass("is-invalid");
                            input.parent().find("div[role='alert']").text(_t('Plate No Number Must Be Digits.'));
                            input.parent().find("div[role='alert']").show();
                            hasError = true;
                            }
                        else if(input.val().length != 4){
                            input.addClass("is-invalid");
                            input.parent().find("div[role='alert']").text(_t('Plate No Number Must Be 4 Digits.'));
                            input.parent().find("div[role='alert']").show();
                            hasError = true;
                            }    
                        else{
                                input.removeClass("is-invalid");
                                input.parent().find("div[role='alert']").hide();
                            }

                    }
                    else{
                        input.removeClass("is-invalid");
                        input.parent().find("div[role='alert']").hide();
                    }
                }
                });
            $('#o_portal_cargo_sale_order_line_form').on('change', "input[name='chassis_no']", function () {
                var input=$(this);
                console.log(input.val());
                console.log(input.val().length);
                if(input.val()){
                    if(input.val().length < 7){
                        console.log("inside validation condition less than 7");
                        input.addClass("is-invalid");
                        input.attr("required", false);
                        input.parent().find("div[role='alert']").text(_t('Chassis Number Must Not Be Less Than 7 Digits.'));
                        input.parent().find("div[role='alert']").show();
                        hasError = true;
                        console.log("has error");
                        console.log(hasError);
                        console.log("input.parent().find");
                        console.log(input.parent().find("div[role='alert']"));
                        console.log('alert value');
                        console.log(input.parent().find("div[role='alert']").val());
                        }
                    else{
                        input.removeClass("is-invalid");
                        input.parent().find("div[role='alert']").hide();
                    }
                }
                else if (!(input.val())){
                        input.addClass("is-invalid");
                        input.parent().find("div[role='alert']").text(_t('This Field Is Required.'));
                        input.parent().find("div[role='alert']").show();
                        hasError = true;
                    }
                else{
                        input.removeClass("is-invalid");
                        input.parent().find("div[role='alert']").hide();
                    }
                });

            //To Check Required
            $('#o_portal_cargo_sale_order_line_form').on('change', "select", function () { 
                if (!inStart){
                    checkCurrentRequiredField($(this));
                }
                else{
                    inStart = false;
                } 
                
            });

            $('#o_portal_cargo_sale_order_line_form').on('change', "input", function () {  
                if (!inStart){
                    checkCurrentRequiredField($(this));
                }
                else{
                    inStart = false;
                }
            });

            //To Get Prices
            $('#o_portal_cargo_sale_order_line_form').on('change', "select[name='shipment_type']", function () {  
                var shipment_type = $(this).val();
                var car_size = $("#o_portal_cargo_sale_order_line_form select[name='car_size']");
                if (shipment_type && car_size.val()){
                    car_size.change();
                }
            });

            $('#o_portal_cargo_sale_order_line_form').on('change', "select[name='car_make']", function () {
                    var select_option = $(this.options[this.selectedIndex]);
                    var select = $("#o_portal_cargo_sale_order_line_form select[name='car_model']");
                    select.select2("val", "");
                    select.select2().val('');
                    select.val('');
                    model_options.detach();
                    var displayed_model = model_options.filter("[data-maker="+(select_option.attr('maker') || 0)+"]");
                    var nb = displayed_model.appendTo(select).show().length;
                    select.parent().toggle(nb>=1);
            });
            
            //To Get Car Size
            $('#o_portal_cargo_sale_order_line_form').on('change', "select[name='car_model']", function () {
                
                var car_model_val = $(this).val();
                var car_maker_val = $("#o_portal_cargo_sale_order_line_form select[name='car_make']").val();
                if (car_model_val){
                    var car_size = $("#o_portal_cargo_sale_order_line_form select[name='car_size']");
                    var car_classfication = $("#o_portal_cargo_sale_order_line_form input[name='car_classfication']");
                    
                    car_size.prepend('<i class="fa fa-spinner fa-spin"></i> ');

                    //this.getSession().uid
                    var def1 = rpc.query({
                        'model': 'bsg_car_line',
                        'method': 'search_read',
                        domain: [
                            ['car_model', '=', parseInt(car_model_val)],
                            ['car_config_id', '=',  parseInt(car_maker_val)],
                        ],
                        fields : ['car_size','car_classfication'],
                    }).then(function (result) {
                        car_size.removeClass('fa-spinner');
                        _.each(result, function (data) {
                            car_size.val(data.car_size[0]);
                            car_classfication.val(data.car_classfication[0]);
                        });
                        $('#o_portal_cargo_sale_order_line_form').find("select[name='car_size']").change();
                    });

                } 
            });
            
            $('#o_portal_cargo_sale_order_line_form').on('change', "select[name='car_size']", function () {
                
                var car_size_val = $(this).val();
                var loc_from = $("#o_portal_cargo_sale_order_line_form input[name='loc_from']").val();
                var loc_to = $("#o_portal_cargo_sale_order_line_form input[name='loc_to']").val();
                var shipment_date = $("#o_portal_cargo_sale_order_line_form input[name='shipment_date']").val();

                var shipment_type = $("#o_portal_cargo_sale_order_line_form select[name='shipment_type']").val();
                var car_model = $("#o_portal_cargo_sale_order_line_form select[name='car_model']").val();
                var service_type = $("#o_portal_cargo_sale_order_line_form select[name='service_type']").val();
                var service_type_input = $("#o_portal_cargo_sale_order_line_form select[name='service_type']");
                var bsg_cargo_sale_id = $("#o_portal_cargo_sale_order_line_form input[name='bsg_cargo_sale_id']").val();
                var car_classfication = $("#o_portal_cargo_sale_order_line_form input[name='car_classfication']").val();
                var discount_perc = $("#o_portal_cargo_sale_order_line_form input[name='discount']").val();
                //shipment_type,car_model,car_size,service_type,bsg_cargo_sale_id,car_classfication
                
                var tax_amount = $("#o_portal_cargo_sale_order_line_form input[name='tax_amount']");
                var amount_with_satah = $("#o_portal_cargo_sale_order_line_form input[name='amount_with_satah']");
                var total_without_tax = $("#o_portal_cargo_sale_order_line_form input[name='total_without_tax']");
                var charges = $("#o_portal_cargo_sale_order_line_form input[name='charges']");
                var unit_charges = $("#o_portal_cargo_sale_order_line_form input[name='unit_charge']");

                var warnning_area = $("#create_new #create-price-warnning");
                warnning_area.children().remove();
                //var from_date = new Date().toUTCString();
                if (car_size_val && loc_from && loc_to && loc_to && shipment_type){
                    var delivery_input = $("#o_portal_cargo_sale_order_line_form input[name='expected_delivery']");
                    var est_no_delivery_days = $("#o_portal_cargo_sale_order_line_form input[name='est_no_delivery_days']");
                    var est_no_hours = $("#o_portal_cargo_sale_order_line_form input[name='est_no_hours']");
                    var est_max_no_delivery_days = $("#o_portal_cargo_sale_order_line_form input[name='est_max_no_delivery_days']");
                    var est_max_no_hours = $("#o_portal_cargo_sale_order_line_form input[name='est_max_no_hours']");
                    var discount_percentage = $("#o_portal_cargo_sale_order_line_form input[name='discount']");
                    var discount_fixed = $("#o_portal_cargo_sale_order_line_form input[name='fixed_discount']");
                    

                    var est_no_delivery_days_sp = $("span[id='est_no_delivery_days']");
                    var est_no_hours_sp = $("span[id='est_no_hours']");
                    var est_max_no_delivery_days_sp = $("span[id='est_max_no_delivery_days']");
                    var est_max_no_hours_sp = $("span[id='est_max_no_hours']");
                    //this.getSession().uid
                    var def1 = rpc.query({
                        'model': 'bsg_vehicle_cargo_sale_line',
                        'method': 'get_portal_expected_delivery_date',
                        args: [parseInt(loc_from),
                               parseInt(loc_to),parseInt(shipment_type),
                               parseInt(car_size_val),shipment_date
                        ],
                    }).then(function (result) {
                        delivery_input.val(result.expected_delivery_date);
                        est_no_delivery_days.val(result.est_no_delivery_days);
                        est_no_hours.val(result.est_no_hours);
                        est_max_no_delivery_days.val(result.est_max_no_delivery_days);
                        est_max_no_hours.val(result.est_max_no_hours);

                        est_no_delivery_days_sp.text(result.est_no_delivery_days);
                        est_no_hours_sp.text(result.est_no_hours);
                        est_max_no_delivery_days_sp.text(result.est_max_no_delivery_days);
                        est_max_no_hours_sp.text(result.est_max_no_hours);
                    });
                    
                }      
                if(car_size_val && shipment_type && car_model && service_type && bsg_cargo_sale_id && car_classfication){
                    //Get Price
                    //shipment_type,car_model,car_size,service_type,bsg_cargo_sale_id,car_classfication
                    var def1 = rpc.query({
                        'model': 'bsg_vehicle_cargo_sale_line',
                        'method': 'get_price_for_portal',
                        args: [
                               parseInt(shipment_type),
                               parseInt(car_model),
                               parseInt(car_size_val),
                               parseInt(service_type),
                               parseInt(car_classfication),
                               parseInt(bsg_cargo_sale_id),
                               parseFloat(discount_perc)
                               
                        ],
                    }).then(function (result) {
                        if(result.error.length == 0)
                        {
                        warnning_area.children().remove();
                        tax_amount.val(result.tax_amount);
                        amount_with_satah.val(result.amount_with_satah);
                        total_without_tax.val(result.total_without_tax);
                        charges.val(result.charges);
                        unit_charges.val(result.unit_charge);
                        discount_percentage.val(result.discount);
                        discount_fixed.val(result.fixed_discount);
                        service_type_input.val(result.service_type);
                        $('#order_line_submit_btn').attr('disabled',false);
                        }
                        else{
                            warnning_area.prepend('<div class="alert alert-danger" role="alert" id="data_price_warning">' +
                            '<p>' + result.error + '</p></div>');
                            $('#order_line_submit_btn').attr('disabled',true);
                            tax_amount.val(0);
                            amount_with_satah.val(0);
                            total_without_tax.val(0);
                            charges.val(0);
                            unit_charges.val(0);
                        }
                    });
                }
            });



            $('#o_portal_cargo_sale_order_line_form').on('change', "select[name='plate_registration']", function () {
                if($(this).val()){
                    var register_val = $(this).val();
                    var palte_one = $("#o_portal_cargo_sale_order_line_form select[name='palte_one']");
                    var palte_second = $("#o_portal_cargo_sale_order_line_form select[name='palte_second']");
                    var palte_third = $("#o_portal_cargo_sale_order_line_form select[name='palte_third']");
                    var plate_no = $("#o_portal_cargo_sale_order_line_form input[name='plate_no']");

                    var non_saudi_plate_no = $("#o_portal_cargo_sale_order_line_form input[name='non_saudi_plate_no']");

                    $('o_portal_cargo_sale_order_line_form').find("input[name='plate_no']").change();

                    var chassis_no = $("#o_portal_cargo_sale_order_line_form input[name='chassis_no']");

                    var palte_type = $("#o_portal_cargo_sale_order_line_form select[name='plate_type']");

                    var saudi_div = $("#o_portal_cargo_sale_order_line_form #saudi_create");
                    var non_saudi_div = $("#o_portal_cargo_sale_order_line_form #non-saudi_create");
                    
                    if(register_val == 'saudi')
                    {
                        saudi_div.show();
                        non_saudi_div.hide();

                        palte_one.attr("required", true).show();
                        palte_second.attr("required", true).show();
                        palte_third.attr("required", true).show();
                        plate_no.attr("required", true).show();
                        palte_type.attr("required", true).show();

                        non_saudi_plate_no.attr("required", false).hide();
//                        chassis_no.attr("required", false);
                    }
                    if(register_val == 'non-saudi')
                    {
                        saudi_div.hide();
                        non_saudi_div.show();

                        palte_one.attr("required", false).hide();
                        palte_second.attr("required", false).hide();
                        palte_third.attr("required", false).hide();
                        plate_no.attr("required", false).hide();

                        palte_type.attr("required", true).show();
                        non_saudi_plate_no.attr("required", true).show(); 
//                        chassis_no.attr("required", false);

                    }
                    if (register_val == 'new_vehicle')
                    {
                        saudi_div.hide();
                        non_saudi_div.show();

                        palte_one.attr("required", false).hide();
                        palte_second.attr("required", false).hide();
                        palte_third.attr("required", false).hide();
                        plate_no.attr("required", false).hide();

                        palte_type.attr("required", false).hide();
                        non_saudi_plate_no.attr("required", false).show();
//                        chassis_no.attr("required", false);
                    }
                }  
            });
            
            $("#o_portal_cargo_sale_order_line_form").find("select[name='plate_registration']").change();
            inStart = true;
            $("#o_portal_cargo_sale_order_line_form").find("select[name='car_make']").change();
            $("#o_portal_cargo_sale_order_line_form").find("select[name='shipment_type']").select2();
            $("#o_portal_cargo_sale_order_line_form").find("select[name='car_make']").select2();
            $("#o_portal_cargo_sale_order_line_form").find("select[name='car_model']").select2();
            $("#o_portal_cargo_sale_order_line_form").find("select[name='year']").select2();
            $("#o_portal_cargo_sale_order_line_form").find("select[name='car_color']").select2();


            //Validatio>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>####################################

            $('#order_line_submit_btn').on('click', async function(e){
                // validation code here
                hasError = false;
                var warnning_area = $("#create_new #create-price-warnning");
                warnning_area.hide().text('');
                $("#o_portal_cargo_sale_order_line_form .alert[role='alert']").hide();
                var in_required_fields = $("#o_portal_cargo_sale_order_line_form .form-control[required='required']").removeClass("is-invalid");
                var in_required_fields = $("#o_portal_cargo_sale_order_line_form .form-control[required='required']");
                _.each(in_required_fields, function (field){
                    var $elem = $(field);
                    if(!$elem.val()){
                        !$elem.addClass("is-invalid");
                        if ($elem.next("div[role='alert']").length)
                        {
                            
                                !$elem.next("div[role='alert']").text(_t('This Field Is Required'));
                                !$elem.next("div[role='alert']").show();
                        }
                        else if ($elem.parent().find("div[role='alert']").length)
                        {
                                !$elem.parent().find("div[role='alert']").text(_t('This Field Is Required'));
                                !$elem.parent().find("div[role='alert']").show();
                        }
                         hasError = true;
                    }
                });

                if(!hasError){
                    $('#o_portal_cargo_sale_order_line_form').find("input[name='plate_no']").change();

                    if ($("#o_portal_cargo_sale_order_line_form input[name='unit_charge']").val() == 0){
                        warnning_area.prepend('<div class="alert alert-danger" role="alert" id="data_price_warning">' +
                                '<p> You cant have unit price -ve value or amount less then 0! </p></div>');
                        warnning_area.show();        
                        hasError = true;        
                    }
                    
                    if (!$("#o_portal_cargo_sale_order_line_form select[name='service_type']").val()){
                        warnning_area.prepend('<div class="alert alert-danger" role="alert" id="data_price_warning">' +
                                '<p> Your Cannot Proceed without Service1 ..!  </p></div>');
                        hasError = true;   
                        warnning_area.show();     
                    }
        
                    if (!$("#o_portal_cargo_sale_order_line_form select[name='service_type']").val()){
                        warnning_area.prepend('<div class="alert alert-danger" role="alert" id="data_price_warning">' +
                                '<p> Your Cannot Proceed without Service2 ..!  </p></div>');
                        hasError = true; 
                        warnning_area.show();       
                    }

                }

                if(!hasError){
                    var bsg_cargo_sale_id = $("#o_portal_cargo_sale_order_line_form input[name='bsg_cargo_sale_id']").val();
                    var chassis_no = $("#o_portal_cargo_sale_order_line_form input[name='chassis_no']").val();
                    var plate_no = $("#o_portal_cargo_sale_order_line_form input[name='plate_no']").val();
                    var palte_one = $("#o_portal_cargo_sale_order_line_form select[name='palte_one']").val();
                    var palte_second = $("#o_portal_cargo_sale_order_line_form select[name='palte_second']").val();
                    var palte_third = $("#o_portal_cargo_sale_order_line_form select[name='palte_third']").val();
                    var non_saudi_plate_no = $("#o_portal_cargo_sale_order_line_form input[name='non_saudi_plate_no']").val();

                    if(chassis_no && plate_no)
                    {
                        await rpc.query({
                            'model': 'bsg_vehicle_cargo_sale_line',
                            'method': 'search_count',
                                args: [[
                                    ['bsg_cargo_sale_id', '=', parseInt(bsg_cargo_sale_id)],
                                    ['chassis_no', '=', chassis_no ],
                                    ['plate_no', '=',  plate_no]
                                ]],
                        }).then(function (result) {
                            if(result > 0){
                                warnning_area.prepend('<div class="alert alert-danger" role="alert" id="data_price_warning">' +
                                '<p> You are Already Add Car with This  Chassis No  </p></div>');
                            hasError = true;
                            warnning_area.show();
        
                            }
                        });
                    }
                    if (plate_no && palte_one && palte_second && palte_third)
                    {
                        await rpc.query({
                            'model': 'bsg_vehicle_cargo_sale_line',
                            'method': 'search_count',
                                args: [[
                                    ['bsg_cargo_sale_id', '=', parseInt(bsg_cargo_sale_id)],
                                    ['plate_no', '=',  plate_no],
                                    ['palte_one', '=',  palte_one],
                                    ['palte_second', '=',  palte_second],
                                    ['palte_third', '=',  palte_third]
                                ]],
                        }).then(function (result) {
                            if(result > 0){
                                warnning_area.prepend('<div class="alert alert-danger" role="alert" id="data_price_warning">' +
                                '<p> You are Already Add Car with This  Plate No </p></div>');
                            hasError = true;
                            warnning_area.show();
        
                            }
                            
                        });
                    }
                    if(non_saudi_plate_no)
                    {
                        await rpc.query({
                            'model': 'bsg_vehicle_cargo_sale_line',
                            'method': 'search_count',
                                args: [
                                    [['bsg_cargo_sale_id', '=', parseInt(bsg_cargo_sale_id)],
                                    ['non_saudi_plate_no', '=',  non_saudi_plate_no]
                                ]],
                        }).then(function (result) {
                            if(result > 0){
                            warnning_area.prepend('<div class="alert alert-danger" role="alert" id="data_price_warning">' +
                                '<p> You are Already Add Car with This  Plate No </p></div>');
                            hasError = true;
                            warnning_area.show();
                            }  
                        });
                    }
                    if(!hasError){
                        $('#o_portal_cargo_sale_order_line_form').submit();
                    }
                }
            });



            $('#o_portal_cargo_sale_order_line_form').on('submit',  function(e){
            
            
            //$('.o_portal_cargo_sale_order_details').find("input[name='sender_id_card_no']").change();
            //$('.o_portal_cargo_sale_order_details').find("input[name='owner_id_card_no']").change();
            //$('.o_portal_cargo_sale_order_details').find("input[name='receiver_id_card_no']").change();
            //$('.o_portal_cargo_sale_order_details').find("input[name='sender_visa_no']").change();
            //$('.o_portal_cargo_sale_order_details').find("input[name='owner_visa_no']").change();
            //$('.o_portal_cargo_sale_order_details').find("input[name='receiver_visa_no']").change();
            $('#o_portal_cargo_sale_order_line_form').find("input[name='plate_no']").change();
                if(hasError) {
                  e.preventDefault();
                  //.closest()
                }
                else{
                    $('#o_portal_cargo_sale_order_line_form :disabled').each(function(e) {
                        $(this).removeAttr('disabled');
                    })
                    var $btn = $('#order_line_submit_btn');
                    $('#order_line_submit_btn').attr('disabled',true);
                    $btn.prepend('<i class="fa fa-refresh fa-spin"/> ');
                    //$(this).submit();
                }
              });
            //End Of Validation>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>###########################
            //$('#o_portal_cargo_sale_order_line_form').find("select[name='car_make']").change();      
        
        }        
            

if ($('#cargo_sale_order_card_details').length) {
    $('.tablinks').on('click',function(e){
        $(".tabcontent").hide();
        $(".tablinks").removeClass('active');
        var tab=$(this).attr('tab');
        $('#'+tab).show();
        $(this).addClass("active");
    });

    $('#defaultOpen').click();


    $('.show_coupon').on('click',function(e){
        $(e.currentTarget).hide();
        $('.coupon_form').show();
    });
    
}

    $("#cargo_payment_content").on('change', "input[id='cargo_term_agree']", function () {
    
        if($(this)[0].checked == true){
            $("#cargo_pay_with_content_dialog").show();
            $("#cargo_warnning_pay_with_content_dialog").hide();
        }
        else{
            $("#cargo_pay_with_content_dialog").hide();
            $("#cargo_warnning_pay_with_content_dialog").show();
        }

        if($("#tamara_required_address").length){
            $("#cargo_pay_with_content_dialog").hide();
            $("#tamara_required_address").show();
        }
    });

    $('#cargo_payment_content').find("input[id='cargo_term_agree']").change();

});                
