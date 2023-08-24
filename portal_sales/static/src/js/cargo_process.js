odoo.define('portal.cargo.sale.process', function (require) {
    'use strict';
    
        require('web.dom_ready');
        var rpc = require("web.rpc");
        var config = require('web.config');
        var core = require('web.core');
        var time = require('web.time');
        var _t = core._t;
        var timeout;
    
        
        if (!$('.o_portal').length) {
            return $.Deferred().reject("DOM doesn't contain '.o_portal'");
        }
        if ($('#cargo_sale_order_card_details').length) {
            const url = new URL(location);
            url.searchParams.delete('delete_error_message');
            url.searchParams.delete('error_message');
            url.searchParams.delete('success_upgrade_message');
            url.searchParams.delete('success_confirm_message');
            url.searchParams.delete('success_cancel_message');
            url.searchParams.delete('success_create_message');
            url.searchParams.delete('success_delete_message');
            url.searchParams.delete('success_edit_message');
            url.searchParams.delete('code_not_check');
            url.searchParams.delete('code_can_not_use');
            url.searchParams.delete('have_more_discount');
            url.searchParams.delete('code_not_available');
            history.replaceState(null, null, url);
        }
    
        if ($('#cargo_sale_order_card_details').length) {
            //Initial Return Process
            $('#cargo_initial_return_btn').on('click', async function(e){
                console.log($(this));
                var $elem = $(this);
                $elem.prepend('<i class="fa fa-spinner fa-spin"></i>');
                $elem.attr('disabled',true);
                var warnning_area = $("#cargo_sale_order_card_details #initial-return-warnning");
                warnning_area.children().remove();
                var return_to_type = $elem.attr('return_branch_type');
                var shipment = $elem.attr('shipment');
                console.log("Return : ",return_to_type);
                if (return_to_type == 'pickup' ||  return_to_type == 'both' ){
                    console.log("statrt rteurn",return_to_type);
                    await rpc.query({
                        'model': 'bsg_vehicle_cargo_sale',
                        'method': 'portal_start_return_process',
                            args: [parseInt(shipment),false],
                    }).then(function (result) {
                        if(result.return_id){
                            var return_url = '<a  href="' + result.return_url + '">' + result.return_id + '</a> ' + _t('Please Deliver Your Car To Our Branch');
                            warnning_area.prepend('<div class="alert alert-info" role="alert" id="initial_warning"><p> ' + _t('Return Successful Initiated : ') +
                            return_url + '</p></div>');
                            $elem.children("i").remove();
                            $elem.hide();
                        } 
                        else{
                            warnning_area.prepend('<div class="alert alert-danger" role="alert" id="initial_warning"><p> ' +
                            result.rtu_masg +'</p></div>');
                            $elem.children("i").remove();
                            $elem.attr('disabled',false);
                        } 
                    });
                    
                }
                else{
                    $elem.children("i").remove();
                    $elem.attr('disabled',false);
                    $('#show_initial_return_popup').click();
                }
            });



            $('#property_submit_cargo_initial_return_form').on('click', async function(e){
                var $elem = $(this);
                $elem.prepend('<i class="fa fa-spinner fa-spin"></i>');
                $elem.attr('disabled',true);
                var warnning_area = $("#cargo_sale_order_card_details #initial-return-warnning");
                warnning_area.children().remove();
                var close_btn = $('#cago_initial_return_dialog').find("button[data-dismiss='modal']");

                e.preventDefault();
                var input = $('#cago_initial_return_dialog').find("select[name='loc_return_to']");
                var shipment = $('#cago_initial_return_dialog').find("input[name='shipment']").val();
                var return_btn = $('#cargo_sale_order_card_details').find("cargo_initial_return_btn");
                var new_loc_to = input.val();
                if (new_loc_to){
                    input.next("div[role='alert']").hide();
                    await rpc.query({
                        'model': 'bsg_vehicle_cargo_sale',
                        'method': 'portal_start_return_process',
                            args: [parseInt(shipment),new_loc_to],
                    }).then(function (result) {
                        if(result.return_id){
                            var return_url = '<a  href="' + result.return_url + '">' + result.return_id + '</a> ' + _t('Please Deliver Your Car To Our Branch');
                            warnning_area.prepend('<div class="alert alert-info" role="alert" id="initial_warning"><p> ' + _t('Return Successful Initiated : ') +
                            return_url + '</p></div>');
                            return_btn.hide();
                            close_btn.click();
                        } 
                        else{
                            warnning_area.prepend('<div class="alert alert-danger" role="alert" id="initial_warning"><p> ' +
                            result.rtu_masg +'</p></div>');
                            close_btn.click();
                        } 
                    });

                }
                else{
                    input.addClass("is-invalid");
                    input.next("div[role='alert']").text(_t('This Field Is Required'));
                    input.next("div[role='alert']").show();
                    $elem.children("i").remove();
                    $elem.attr('disabled',false);
                }


            });

            //End Of Initial Return Process


            //Upgrade Process
            $('.line_upgrade_price_check').on('change',function(e){
                var $elem = $(this);
                var diff_price = 0.0
                var $upgrade_form = $elem.closest('form');
                var check_inputs = $upgrade_form.find("input[type='checkbox']");
                _.each(check_inputs, function (input){
                    var $input_elem = $(input);
                    var price = Number($input_elem.attr('diff-price'));
                    if (price != 'NaN' && $input_elem[0].checked == true){
                        diff_price += price;
                    }
                    //$elem.parent().find('.col-form-label').append("<b style='color:red;'> * </b>");
                    //if ($elem.attr('id') == 'shipment_date'){
                    //    $elem.parent().parent().find('.col-form-label').append("<b style='color:red;'> * </b>");
                    //}
                });
                if (diff_price == 0.0){
                    $upgrade_form.find(".alert-info").hide();
                    $upgrade_form.find(".alert-danger").show();
                    $upgrade_form.find(".order_upgrade_price_btn").attr('disabled',true);
                }
                else{
                    $upgrade_form.find(".alert-info").show();
                    $upgrade_form.find(".alert-danger").hide();
                    $upgrade_form.find(".order_upgrade_price_btn").attr('disabled',false);
                }
                $upgrade_form.find("span[class='price_total']").text(diff_price);

            });

            /*$('.upgrade-main-btn').popover({
                trigger: 'manual',
                animation: true,
                html: true,
                title: function () {
                    return _t("Features");
                },
                container: 'body',
                placement: 'auto',
                template: '<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
            });

            $('.upgrade-main-btn').on('mouseenter',function(e){
                var $elem = $(this);
                clearTimeout(timeout);
                $(this.selector).not(e.currentTarget).popover('hide');
                    $elem.popover("show");
                    $('.popover').on('mouseleave', function () {
                        $elem.trigger('mouseleave');
                    });

            });

            $('.upgrade-main-btn').on('mouseleave',function(ev){
                var $el = $(this);
                if ($('.popover:hover').length) {
                    return;
                }
                if (!$el.is(':hover')) {
                   $el.popover('hide');
                }

            });*/

           

            //End Of Upgrade Process
        }

        if ($('#cargo_sale_order_edit_operations').length) {
            var hasError = false;

            var order_required_fields = $("#cargo_sale_order_edit_operations .form-control[required='required']");
            _.each(order_required_fields, function (field){
                var $elem = $(field);
                $elem.parent().find('.col-form-label').append("<b style='color:red;'> * </b>");
                if ($elem.attr('id') == 'shipment_date'){
                    $elem.parent().parent().find('.col-form-label').append("<b style='color:red;'> * </b>");
                }
            });


            //#############################Location Edit################################
            var loc_to_options = $("select[name='loc_to']:enabled option:not(:first)");
            var loc_from_options = $("select[name='loc_from']:enabled option:not(:first)");
            var return_loc_from_options = $("select[name='return_loc_to'] option:not(:first)");

            $('#cargo_sale_order_edit_operations').on('change', "select[name='loc_from']", function () {
                if($(this).val()){
                //Remove From To Location    
                var select = $("select[name='loc_to']");
                loc_to_options.detach();
                var displayed_loc_to = loc_to_options.filter("[value !="+($(this).val() || 0)+"]");
                var nb = displayed_loc_to.appendTo(select).show().length;
                select.parent().toggle(nb>=1);
    
                //Set Return To In RoundTrip
                var agreement = $("select[name='shipment_type']").val();
                if(agreement == 'return'){
    
                    var defualt_from = $(this).val();
                    var return_select = $("select[name='return_loc_to']");
                    var current_sel_option = loc_from_options.filter("[value ="+($(this).val())+"]");
                    if (current_sel_option && current_sel_option.attr('return_branch_type') == 'shipping'){
                        return_loc_from_options.detach();
                        var availabe_options = current_sel_option.attr('allowed_return_waypoint_ids');
                        return_select.attr('disabled',false);
    
                        function checkOption(option) {
                            if (availabe_options.includes(return_loc_from_options[option].value))
                                return true;
                            else false;    
                            } 
    
                        var displayed_return_loc_from = return_loc_from_options.filter(checkOption);
                        var nb = displayed_return_loc_from.appendTo(return_select).show().length;
                        return_select.parent().toggle(nb>=1);
                        
    
                    }
    
                    else if(defualt_from){
                        return_loc_from_options.detach();
                        //var displayed_return_loc_from = return_loc_from_options.filter(checkOption);
                        var nb = return_loc_from_options.appendTo(return_select).show().length;
                        return_select.parent().toggle(nb>=1);
    
                        $("select[name='return_loc_to']").val(defualt_from);
                        return_select.attr('disabled',true);    
                    }
    
                    }
                    
    
    
    
                    if ($("select[name='loc_to']").val())
                        {
                            //Get Expected Deliver 
                            var def1 = rpc.query({
                                'model': 'bsg.estimated.delivery.days',
                                'method': 'search_read',
                                domain: [
                                    ['loc_from_id', '=', parseInt($(this).val())],
                                    ['loc_to_id', '=',  parseInt($("select[name='loc_to']").val())],
                                ],
                                fields : ['est_no_delivery_days','est_max_no_delivery_days'],
                                limit: 1,
                            }).then(function (result) {
                                if (result.length > 0 ){
                                _.each(result, function (data) {
                                    $('#cargo_sale_order_edit_operations').find("#est_no_delivery_days").text(data.est_no_delivery_days);
                                    $('#cargo_sale_order_edit_operations').find("#est_max_no_delivery_days").text(data.est_max_no_delivery_days);
                                });
                              }
                              else{
                                $('#cargo_sale_order_edit_operations').find("#est_no_delivery_days").text(0);
                                $('#cargo_sale_order_edit_operations').find("#est_max_no_delivery_days").text(0);
                              }
                            });
                        }
    
                }
            });


            $('#cargo_sale_order_edit_operations').on('change', "select[name='shipment_type']", function () {
                if($(this).val() == 'return'){
                var defualt_from = $("select[name='loc_from']").val();
                var default_to = $("select[name='loc_to']").val();
                if(default_to){
                    $("select[name='return_loc_from']").val(default_to);
                    $('.o_portal_cargo_sale_order_details').find("select[name='return_loc_from']").change();
                }
                if(defualt_from){ 
                    $('#cargo_sale_order_edit_operations').find("select[name='loc_from']").change();
                }
                $("#return_details1").show();
                $("#return_details2").show();
                $("#return_details3").show();
                $("#return_details4").show();
                $("select[name='return_loc_from']").attr("required", true);
                $("select[name='return_loc_to']").attr("required", true); 
                }
                if($(this).val() == 'oneway'){
                    $("select[name='return_loc_from']").val('');
                    $("select[name='return_loc_to']").val(''); 
                    $("#return_details1").hide();
                    $("#return_details2").hide();
                    $("#return_details3").hide();
                    $("#return_details4").hide();
                    $("select[name='return_loc_from']").attr("required", false);
                    $("select[name='return_loc_to']").attr("required", false); 
                }
            });
            $('#cargo_sale_order_edit_operations').on('change', "select[name='loc_to']", function () {
                if($(this).val()){
                var select = $("select[name='loc_from']");
                loc_from_options.detach();
                var displayed_loc_from = loc_from_options.filter("[value !="+($(this).val() || 0)+"]");
                var nb = displayed_loc_from.appendTo(select).show().length;
                select.parent().toggle(nb>=1);
    
                var agreement = $("select[name='shipment_type']").val();
                if(agreement == 'return'){
                var default_to = $(this).val();
                    if(default_to){
                        $('#cargo_sale_order_edit_operations').find("select[name='return_loc_from']").val(default_to);
                    }
                }
    
                if ($("select[name='loc_from']").val())
                {
                    //Get Expected Deliver 
                    var def1 = rpc.query({
                        'model': 'bsg.estimated.delivery.days',
                        'method': 'search_read',
                        domain: [
                            ['loc_from_id', '=', parseInt($("select[name='loc_from']").val())],
                            ['loc_to_id', '=',  parseInt($(this).val())],
                        ],
                        fields : ['est_no_delivery_days','est_max_no_delivery_days'],
                        limit: 1,
                    }).then(function (result) {
                        if (result.length > 0 ){
                            _.each(result, function (data) {
                                $('#cargo_sale_order_edit_operations').find("#est_no_delivery_days").text(data.est_no_delivery_days);
                                $('#cargo_sale_order_edit_operations').find("#est_max_no_delivery_days").text(data.est_max_no_delivery_days);
                            });
                          }
                          else{
                            $('#cargo_sale_order_edit_operations').find("#est_no_delivery_days").text(0);
                            $('#cargo_sale_order_edit_operations').find("#est_max_no_delivery_days").text(0);
                          }
                    });
                }
    
    
             }
            
            });

            $('#cargo_sale_order_edit_operations').find("select[name='shipment_type']").change();
            $('#cargo_sale_order_edit_operations').find("select[name='loc_from']").change();
            $('#cargo_sale_order_edit_operations').find("select[name='loc_to']").change();
            $('#cargo_sale_order_edit_operations').find("select[name='return_loc_from']").change();
            $('#cargo_sale_order_edit_operations').find("select[name='loc_from']").select2();
            $('#cargo_sale_order_edit_operations').find("select[name='loc_to']").select2();

            //#############################End Of Location Edit################################


            //#############################Reciever Edit#######################################
            $('#cargo_sale_order_edit_operations').on('change', "select[name='receiver_type']", function () {
                if($(this).val()){
                var default_type = $(this).val();
                var default_nationality = $("select[name='receiver_nationality']");
                var default_id_type = $("select[name='receiver_id_type']");
                var default_country = $("input[name='default_country']").val();
                if(default_type == 1){
                    default_nationality.val(default_country);
                    default_nationality.change();
                    default_id_type.val('saudi_id_card');
                }
                if(default_type == 2){
                    default_id_type.val('iqama');  
                }
                }
            });


            $("#cargo_sale_order_edit_operations").on('change',"input[name='receiver_id_card_no']", function() {
                var input=$(this);
                var re;
                var receiver_type = $("select[name='receiver_type']").val();
                var receiver_id_type = $("select[name='receiver_id_type']").val();
                //var re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
                if(input.val()){
                    if(receiver_type == 2 && receiver_id_type == 'iqama'){
                        re = /^2[0-9]{9}/;
                        if(input.val().length != 10){
                            input.addClass("is-invalid");
                            input.next("div[role='alert']").text(_t('Receiver ID Card Number Must Have 10 Digits.'));
                            input.next("div[role='alert']").show();
                            hasError = true;
                            }
    
                        else if(re && !re.test(input.val())){
                            input.addClass("is-invalid");
                            input.next("div[role='alert']").text(_t('Receiver ID Card Number Must Be Start By Number 2 And Must Be Digits.'));
                            input.next("div[role='alert']").show();
                            hasError = true;
                            }  
                        else{
                                input.removeClass("is-invalid");
                                input.next("div[role='alert']").hide();
                            } 
                    }
                    else if(receiver_type == 1 && receiver_id_type == 'saudi_id_card'){
                        re = /^1[0-9]{9}/;
                        if(input.val().length != 10){
                            input.addClass("is-invalid");
                            input.next("div[role='alert']").text(_t('Receiver ID Card Number Must Have 10 Digits.'));
                            input.next("div[role='alert']").show();
                            hasError = true;
                            }
                        else if(re && !re.test(input.val())){
                            input.addClass("is-invalid");
                            input.next("div[role='alert']").text(_t('Receiver ID Card Number Must Be Start By Number 1 And Must Be Digits.'));
                            input.next("div[role='alert']").show();
                            hasError = true;
                            }
                        else{
                                input.removeClass("is-invalid");
                                input.next("div[role='alert']").hide();
                            }
                    }
                    else{
                        input.removeClass("is-invalid");
                        input.next("div[role='alert']").hide();
                        }
                }
            });


            $("#cargo_sale_order_edit_operations").on('change',"input[name='receiver_visa_no']", function() {
                var input=$(this);
                var re = /^[a-zA-Z0-9]/;
                //var re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
                if (input.val())
                {
                    if(input.val().length > 15){
                        input.addClass("is-invalid");
                        input.next("div[role='alert']").text(_t('Receiver Visa/Passport Number Must Be Have 15 Character'));
                        input.next("div[role='alert']").show();
                        hasError = true;
                        }
                    else{
                        if(re && !re.test(input.val())){
                            input.addClass("is-invalid");
                            input.next("div[role='alert']").text(_t('Receiver Visa/Passport Number Must Contain Alphanumeric'));
                            input.next("div[role='alert']").show();
                            hasError = true;
                            }  
                        else{
                                input.removeClass("is-invalid");
                                input.next("div[role='alert']").hide();
                            } 
                        }
                }
            });
    
            $("#cargo_sale_order_edit_operations").on('change',"input[name='receiver_mob_no']", function() {
                var input=$(this);
                //var re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
                //var is_email=re.test(input.val());
                if(input.val().length < 9){
                    input.addClass("is-invalid");
                    input.next("div[role='alert']").text(_t('Reciever Mobile Number Must Be more Than 9 Digits'));
                    input.next("div[role='alert']").show();
                    hasError = true;
                    }
                else{
                    //if(!_.isNumber(input.val())){
                    //    input.addClass("is-invalid");
                    //    input.next("div[role='alert']").text('Reciever Mobile Number Must Be Digits');
                    //    input.next("div[role='alert']").show();
                    //    } 
                    //else{
                            input.removeClass("is-invalid");
                            input.next("div[role='alert']").hide();
                    //    } 
                    }
            });
            $('#cargo_sale_order_edit_operations').find("select[name='receiver_nationality']").select2();
            //#############################End Od Reciever Edit################################


            //#############################Shipment Date Edit################################

            var is_datetime_valid = function (value, type_of_date) {
                if (value === "") {
                    return true;
                } else {
                    try {
                        parse_date(value, type_of_date);
                        return true;
                    } catch (e) {
                        return false;
                    }
                }
            };
            
            // This is a stripped down version of format.js parse_value function
            var parse_date = function (value, type_of_date, value_if_empty) {
                var date_pattern = "DD/MM/YYYY";
                var time_pattern = "HH:mm:ss";
                var date_pattern_wo_zero = date_pattern.replace('MM','M').replace('DD','D'),
                    time_pattern_wo_zero = time_pattern.replace('HH','H').replace('mm','m').replace('ss','s');    
                switch (type_of_date) {
                    case 'datetime':
                        var datetime = moment(value, [date_pattern + ' ' + time_pattern, date_pattern_wo_zero + ' ' + time_pattern_wo_zero], true);
                       
                        if (datetime.isValid()) 
                            return time.datetime_to_str(datetime.toDate());
                        throw new Error(_.str.sprintf(_t("'%s' is not a correct datetime"), value));
                    case 'date':
                        var date = moment(value, [date_pattern, date_pattern_wo_zero], true);
                        if (date.isValid())
                            return time.date_to_str(date.toDate());
                        throw new Error(_.str.sprintf(_t("'%s' is not a correct date"), value));
                }
                return value;
            };

            $('#datetimepicker4').datetimepicker({
                minDate: new Date(),
                maxDate: moment({ y: 9999, M: 11, d: 31 }),
                calendarWeeks: true,
                icons : {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    next: 'fa fa-chevron-right',
                    previous: 'fa fa-chevron-left',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down',
                    },
                locale : moment.locale(),
                format : "DD/MM/YYYY",
                //defaultDate: new Date(),
            });


            $("#datetimepicker4").on("change.datetimepicker", function (e) {
                if (e.oldDate !== e.date) {
                    var input=$(this);
                    if(!is_datetime_valid(e.date,'date')){
                        input.addClass("is-invalid");
                        input.next("div[role='alert']").text(_t('Invalid Date Format'));
                        input.next("div[role='alert']").show();
                        hasError = true;
                        }  
                    else{
                        input.removeClass("is-invalid");
                        input.next("div[role='alert']").removeClass("is-invalid");
                        input.next("div[role='alert']").hide();
                        }
                }
            });

            //#############################End Of Shipment Date Edit################################



            $('#cargo_sale_order_edit_operations .cargo_edit_submit_btn').on('click', function(e){
                var $el = $(this);
                $el.parent().parent().find(".alert[role='alert']").hide();
                var required_fields = $el.parent().parent().find(".form-control[required='required']").removeClass("is-invalid");
                var required_fields = $el.parent().parent().find(".form-control[required='required']");
                _.each(required_fields, function (field){
                    var $elem = $(field);
                    if(!$elem.val()){
                        if ($elem.attr('id') == 'shipment_date'){
                            $elem.parent().next("div[role='alert']").text(_t('This Field Is Required'));
                            $elem.parent().next("div[role='alert']").show();
                        }
                        else{
                        !$elem.addClass("is-invalid");
                        !$elem.next("div[role='alert']").text(_t('This Field Is Required'));
                        !$elem.next("div[role='alert']").show();
                        }
                    }
                });
    
    
            });


            $('#cargo_sale_order_edit_operations form').on('submit', function(e){
            
                var $elem = $(this);
                $elem.find('.cargo_edit_submit_btn').prepend('<i class="fa fa-spinner fa-spin"></i>');
                $elem.find('.cargo_edit_submit_btn').attr('disabled',true);
                // validation code here
                hasError = false;
                $elem.find("input[name='receiver_id_card_no']").change();
                $elem.find("input[name='receiver_visa_no']").change();
                $elem.find("input[name='receiver_mob_no']").change();
                $elem.find("input[name='shipment_date']").change();
               
                
                if(hasError) {
                  e.preventDefault();
                  $elem.find('.cargo_edit_submit_btn').children("i").remove();
                  $elem.find('.cargo_edit_submit_btn').attr('disabled',false);
                }
                else{
                    $(':disabled').each(function(e) {
                        $(this).removeAttr('disabled');
                    })
                    $elem.find('.cargo_edit_submit_btn').attr('disabled',true);
                }
              });

        }
      
        
});    
