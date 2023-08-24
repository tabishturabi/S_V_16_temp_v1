

odoo.define('portal.cargo.sale', function (require) {
'use strict';





    require('web.dom_ready');
    require('web.Session');
    
    var core = require('web.core');
    var time = require('web.time');
    var rpc = require("web.rpc");

    var _t = core._t;
    var l10n = _t.database.parameters;


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

    if (!$('.o_portal').length) {
        return $.Deferred().reject("DOM doesn't contain '.o_portal'");
    }

    if ($('.o_portal_cargo_sale_order_details').length) {



        var order_required_fields = $(".o_portal_cargo_sale_order_details .form-control[required='required']");
            _.each(order_required_fields, function (field){
                var $elem = $(field);
                $elem.parent().find('.col-form-label').append("<b style='color:red;'> * </b>");
                if ($elem.attr('id') == 'shipment_date'){
                    $elem.parent().parent().find('.col-form-label').append("<b style='color:red;'> * </b>");
                }
            });

        var hasError = false;
        var loc_to_options = $("select[name='loc_to']:enabled option:not(:first)");
        var loc_from_options = $("select[name='loc_from']:enabled option:not(:first)");
        var return_loc_from_options = $("select[name='return_loc_to'] option:not(:first)");
        
        // DD/MM/YYYY HH:mm:ss
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
            if (e.date && e.oldDate !== e.date) {
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



        $('.o_portal_cargo_sale_order_details').on('change', "select[name='loc_from']", function () {
            if($(this).val()){
            //Remove From To Location    
            var select = $("select[name='loc_to']");
            loc_to_options.detach();
            var displayed_loc_to = loc_to_options.filter("[value !="+($(this).val() || 0)+"]");
            var nb = displayed_loc_to.appendTo(select).show().length;
            select.parent().toggle(nb>=1);

            //Set Return To In RoundTrip
            var agreement = $("select[name='agreement_type']").val();
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
                                $('#o_portal_cargo_sale_order_form').find("#est_no_delivery_days").text(data.est_no_delivery_days);
                                $('#o_portal_cargo_sale_order_form').find("#est_max_no_delivery_days").text(data.est_max_no_delivery_days);
                            });
                          }
                          else{
                            $('#o_portal_cargo_sale_order_form').find("#est_no_delivery_days").text(0);
                            $('#o_portal_cargo_sale_order_form').find("#est_max_no_delivery_days").text(0);
                          }
                        });
                    }

            }
        });

        $('.o_portal_cargo_sale_order_details').on('change', "select[name='agreement_type']", function () {
            if($(this).val() == 'return'){
            var defualt_from = $("select[name='loc_from']").val();
            var default_to = $("select[name='loc_to']").val();
            if(default_to){
                $("select[name='return_loc_from']").val(default_to);
                $('.o_portal_cargo_sale_order_details').find("select[name='return_loc_from']").change();
            }
            if(defualt_from){
                //$("select[name='return_loc_to']").val(defualt_from);    
                $('.o_portal_cargo_sale_order_details').find("select[name='loc_from']").change();
            }
            //var default_payment_method_id = $("input[name='default_payment_method_id']").val();
            //$("select[name='payment_method']").val(default_payment_method_id);
            //$("select[name='payment_method']").attr("disabled", true);
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
                //$("select[name='payment_method']").attr("disabled", false);
                $("select[name='return_loc_from']").attr("required", false);
                $("select[name='return_loc_to']").attr("required", false); 
            }
        });

        $('.o_portal_cargo_sale_order_details').on('change', "select[name='loc_to']", function () {
            if($(this).val()){
            var select = $("select[name='loc_from']");
            loc_from_options.detach();
            var displayed_loc_from = loc_from_options.filter("[value !="+($(this).val() || 0)+"]");
            var nb = displayed_loc_from.appendTo(select).show().length;
            select.parent().toggle(nb>=1);

            var agreement = $("select[name='agreement_type']").val();
            if(agreement == 'return'){
            var default_to = $(this).val();
                if(default_to){
                    $("select[name='return_loc_from']").val(default_to);
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
                            $('#o_portal_cargo_sale_order_form').find("#est_no_delivery_days").text(data.est_no_delivery_days);
                            $('#o_portal_cargo_sale_order_form').find("#est_max_no_delivery_days").text(data.est_max_no_delivery_days);
                        });
                      }
                      else{
                        $('#o_portal_cargo_sale_order_form').find("#est_no_delivery_days").text(0);
                        $('#o_portal_cargo_sale_order_form').find("#est_max_no_delivery_days").text(0);
                      }
                });
            }


         }
        
        });



        /*$('.o_portal_cargo_sale_order_details').on('change', "select[name='return_loc_from']", function () {
            
            if($(this).val()){
            var select = $("select[name='return_loc_to']");
            return_loc_to_options.detach();
            var displayed_loc_to = return_loc_to_options.filter("[value !="+($(this).val() || 0)+"]");
            var nb = displayed_loc_to.appendTo(select).show().length;
            select.parent().toggle(nb>=1);
            }
        });*/
        //==#################################################################==========


        $('.o_portal_cargo_sale_order_details').on('change', "input[name='sender_default']", function () {
            if($(this)[0].checked == true){
            var defualt_sender_name = $("input[name='defualt_sender_name']").val();
            var default_sender_type = $("input[name='default_sender_type']").val();
            var default_sender_nationality = $("input[name='default_sender_nationality']").val();
            var default_sender_id_type = $("input[name='default_sender_id_type']").val();
            var default_sender_id_card_no = $("input[name='default_sender_id_card_no']").val();
            var defualt_sender_visa_no = $("input[name='defualt_sender_visa_no']").val();
            if(defualt_sender_name){
                $("input[name='sender_name']").val(defualt_sender_name);
                $("input[name='sender_name']").change();
            }
            if(default_sender_type){
                $("select[name='sender_type']").val(default_sender_type); 
                $("select[name='sender_type']").change();  
            }
            if(default_sender_nationality){
                $("select[name='sender_nationality']").val(default_sender_nationality);
                $("select[name='sender_nationality']").change();
            }
            if(default_sender_id_type){
                $("select[name='sender_id_type']").val(default_sender_id_type);
                $("select[name='sender_id_type']").change();
            }
            if(default_sender_id_card_no){
                $("input[name='sender_id_card_no']").val(default_sender_id_card_no);
                $("input[name='sender_id_card_no']").change();
            }
            if(defualt_sender_visa_no){
                $("input[name='sender_visa_no']").val(defualt_sender_visa_no);
                $("input[name='sender_visa_no']").change();
            }
            }
        });


        $('.o_portal_cargo_sale_order_details').on('change', "input[name='owner_default']", function () {
            if($(this)[0].checked == true){
            var defualt_owner_name = $("input[name='sender_name']").val();
            var default_owner_type = $("select[name='sender_type']").val();
            var default_owner_nationality = $("select[name='sender_nationality']").val();
            var default_owner_id_type = $("select[name='sender_id_type']").val();
            var default_owner_id_card_no = $("input[name='sender_id_card_no']").val();
            var defualt_owner_visa_no = $("input[name='sender_visa_no']").val();
            if(defualt_owner_name){
                $("input[name='owner_name']").val(defualt_owner_name);
                $("input[name='owner_name']").change();
            }
            if(default_owner_type){
                $("select[name='owner_type']").val(default_owner_type); 
                $("select[name='owner_type']").change();
            }
            if(default_owner_nationality){
                $("select[name='owner_nationality']").val(default_owner_nationality);
                $("select[name='owner_nationality']").change();
            }
            if(default_owner_id_type){
                $("select[name='owner_id_type']").val(default_owner_id_type);
                $("select[name='owner_id_type']").change();
            }
            if(default_owner_id_card_no){
                $("input[name='owner_id_card_no']").val(default_owner_id_card_no);
                $("input[name='owner_id_card_no']").change();
            }
            if(defualt_owner_visa_no){
                $("input[name='owner_visa_no']").val(defualt_owner_visa_no);
                $("input[name='owner_visa_no']").change();
            }
            }
        });

        $('.o_portal_cargo_sale_order_details').on('change', "input[name='receiver_default']", function () {
            if($(this)[0].checked == true){
            var defualt_receiver_name = $("input[name='owner_name']").val();
            var default_receiver_type = $("select[name='owner_type']").val();
            var default_receiver_nationality = $("select[name='owner_nationality']").val();
            var default_receiver_id_type = $("select[name='owner_id_type']").val();
            var default_receiver_id_card_no = $("input[name='owner_id_card_no']").val();
            var defualt_receiver_visa_no = $("input[name='owner_visa_no']").val();
            if(defualt_receiver_name){
                $("input[name='receiver_name']").val(defualt_receiver_name);
                $("input[name='receiver_nationality']").change();
                

            }
            if(default_receiver_type){
                $("select[name='receiver_type']").val(default_receiver_type); 
                $("select[name='receiver_type']").change();
            }
            if(default_receiver_nationality){
                $("select[name='receiver_nationality']").val(default_receiver_nationality);
                $("select[name='receiver_nationality']").change();
            }
            if(default_receiver_id_type){
                $("select[name='receiver_id_type']").val(default_receiver_id_type);
                $("select[name='receiver_id_type']").change();
            }
            if(default_receiver_id_card_no){
                $("input[name='receiver_id_card_no']").val(default_receiver_id_card_no);
                $("input[name='receiver_id_card_no']").change();
            }
            if(defualt_receiver_visa_no){
                $("input[name='receiver_visa_no']").val(defualt_receiver_visa_no);
                $("input[name='receiver_visa_no']").change();
            }
            }
        });


        //=======================Type Change===============================================//

        $('.o_portal_cargo_sale_order_details').on('change', "select[name='sender_type']", function () {
            if($(this).val()){
            var default_type = $(this).val();
            var default_nationality = $("select[name='sender_nationality']");
            var default_id_type = $("select[name='sender_id_type']");
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

        $('.o_portal_cargo_sale_order_details').on('change', "select[name='owner_type']", function () {
            if($(this).val()){
            var default_type = $(this).val();
            var default_nationality = $("select[name='owner_nationality']");
            var default_id_type = $("select[name='owner_id_type']");
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

        $('.o_portal_cargo_sale_order_details').on('change', "select[name='receiver_type']", function () {
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



        
        
        
        $('.o_portal_cargo_sale_order_details').find("input[name='sender_default']").change();
        $('.o_portal_cargo_sale_order_details').find("input[name='owner_default']").change();
        $('.o_portal_cargo_sale_order_details').find("input[name='receiver_default']").change();
        $('.o_portal_cargo_sale_order_details').find("select[name='agreement_type']").change();
        $('.o_portal_cargo_sale_order_details').find("select[name='loc_from']").change();
        $('.o_portal_cargo_sale_order_details').find("select[name='loc_to']").change();
        $('.o_portal_cargo_sale_order_details').find("select[name='return_loc_from']").change();
        $('.o_portal_cargo_sale_order_details').find("select[name='loc_from']").select2();
        $('.o_portal_cargo_sale_order_details').find("select[name='loc_to']").select2();
        $('.o_portal_cargo_sale_order_details').find("select[name='sender_nationality']").select2();
        $('.o_portal_cargo_sale_order_details').find("select[name='receiver_nationality']").select2();
        $('.o_portal_cargo_sale_order_details').find("select[name='owner_nationality']").select2();
        //$('.o_portal_cargo_sale_order_details').find("div[class='input-group-append']").click().click();
        

        //Validation Check#################################
        //1==> Check Card Number==============================
        $("input[name='sender_id_card_no']").on('change', function() {
            var input=$(this);
            var re;
            var sender_type = $("select[name='sender_type']").val();
            var sender_id_type = $("select[name='sender_id_type']").val();
            
            //var re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;  
            if(input.val()){
            if(sender_type == 2 && sender_id_type == 'iqama'){
                re = /^2[0-9]{9}/;

                if(input.val().length != 10){
                    input.addClass("is-invalid");
                    input.next("div[role='alert']").text(_t('Sender ID Card No Must Have 10 Digits.'));
                    input.next("div[role='alert']").show();
                    hasError = true;
                    }

                else if(re && !re.test(input.val())){
                    input.addClass("is-invalid");
                    input.next("div[role='alert']").text(_t('Sender ID Card No Must Be Start By Number 2 And Must Be Digits.'));
                    input.next("div[role='alert']").show();
                    hasError = true;
                    }  

                else{
                        input.removeClass("is-invalid");
                        input.next("div[role='alert']").hide();
                    } 
            }

            else if(sender_type == 1 && sender_id_type == 'saudi_id_card'){
                re = /^1[0-9]{9}/;
                if(input.val().length != 10){
                    input.addClass("is-invalid");
                    input.next("div[role='alert']").text(_t('Sender ID Card No Must Have 10 Digits.'));
                    input.next("div[role='alert']").show();
                    hasError = true;
                    }

                else if(re && !re.test(input.val())){
                    input.addClass("is-invalid");
                    input.next("div[role='alert']").text(_t('Sender ID Card No Must  Be Start By Number 1 And Must Be Digits.'));
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

        $("input[name='owner_id_card_no']").on('change', function() {
            var input=$(this);
            var re;
            var owner_type = $("select[name='owner_type']").val();
            var owner_id_type = $("select[name='owner_id_type']").val();
            
            //var re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
            if(input.val()){
                if(owner_type == 2 && owner_id_type == 'iqama'){
                    re = /^2[0-9]{9}/;
                    if(input.val().length != 10){
                        input.addClass("is-invalid");
                        input.next("div[role='alert']").text(_t('Owner ID Card Number Must Have 10 Digits.'));
                        input.next("div[role='alert']").show();
                        hasError = true;
                        }
                    else if(re && !re.test(input.val())){
                        input.addClass("is-invalid");
                        input.next("div[role='alert']").text(_t('Owner ID Card Number Must Be Start By Number 2 And Must Be Digits.'));
                        input.next("div[role='alert']").show();
                        hasError = true;
                        }  
                    else{
                            input.removeClass("is-invalid");
                            input.next("div[role='alert']").hide();
                        } 
                }
                else if(owner_type == 1 && owner_id_type == 'saudi_id_card'){
                    re = /^1[0-9]{9}/;
                    if(input.val().length != 10){
                        input.addClass("is-invalid");
                        input.next("div[role='alert']").text(_t('Owner ID Card Number Must Have 10 Digits.'));
                        input.next("div[role='alert']").show();
                        hasError = true;
                        }
                    else if(re && !re.test(input.val())){
                        input.addClass("is-invalid");
                        input.next("div[role='alert']").text(_t('Owner ID Card Number Must Be Start By Number 1 And Must Be Digits.'));
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

        $("input[name='receiver_id_card_no']").on('change', function() {
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

        $("input[name='sender_visa_no']").on('change', function() {
            var input=$(this);
            var re = /^[a-zA-Z0-9]/;
            //var re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
            if (input.val())
            {
                if(input.val().length > 15){
                    input.addClass("is-invalid");
                    input.next("div[role='alert']").text(_t('Sender Visa/Passport Number Must Be Have 15 Character'));
                    input.next("div[role='alert']").show();
                    hasError = true;
                    }
                    
                else{
                    if(re && !re.test(input.val())){
                        input.addClass("is-invalid");
                        input.next("div[role='alert']").text(_t('Sender Visa/Passport Number Must Contain Alphanumeric'));
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

        $("input[name='owner_visa_no']").on('change', function() {
            var input=$(this);
            var re = /^[a-zA-Z0-9]/;
            //var re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
            if (input.val())
            {
                if(input.val().length > 15){
                    input.addClass("is-invalid");
                    input.next("div[role='alert']").text(_t('Owner Visa/Passport Number Must Be Have 15 Character'));
                    input.next("div[role='alert']").show();
                    hasError = true;
                    }
                    
                else{
                    if(re && !re.test(input.val())){
                        input.addClass("is-invalid");
                        input.next("div[role='alert']").text(_t('Owner Visa/Passport Number Must Contain Alphanumeric'));
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

        $("input[name='receiver_visa_no']").on('change', function() {
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

        $("input[name='receiver_mob_no']").on('change', function() {
            var input=$(this);
            //var re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
            //var is_email=re.test(input.val());
            if(input.val()){
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
            }
        });

        /*$('#o_portal_cargo_sale_order_form #property_submit_form').on('click', function(e){
            $(".o_portal_cargo_sale_order_details .alert[role='alert']").hide();
            var required_fields = $(".o_portal_cargo_sale_order_details .form-control[required='required']").removeClass("is-invalid");
            var required_fields = $(".o_portal_cargo_sale_order_details .form-control[required='required']");
            _.each(required_fields, function (field){
                var $elem = $(field);
                if(!$elem.val()){
                    if ($elem.attr('id') == 'shipment_date'){
                        $elem.parent().next("div[role='alert']").text(_t('This Field Is Required'));
                        $elem.parent().next("div[role='alert']").show();
                    }
                    else{
                        $elem.addClass("is-invalid");
                        $elem.next("div[role='alert']").text(_t('This Field Is Required'));
                        $elem.next("div[role='alert']").show();
                    }
                }
            });


        });*/
       
        $('#o_portal_cargo_sale_order_form').on('submit', function(e){
            if ($('#o_portal_cargo_sale_order_form').valid()){
            
            var $elem = $(this);
            $('#o_portal_cargo_sale_order_form #property_submit_form').prepend('<i class="fa fa-spinner fa-spin"></i>');
            $('#o_portal_cargo_sale_order_form #property_submit_form').attr('disabled',true);
            // validation code here
            hasError = false;
            $('.o_portal_cargo_sale_order_details').find("input[name='sender_id_card_no']").change();
            $('.o_portal_cargo_sale_order_details').find("input[name='owner_id_card_no']").change();
            $('.o_portal_cargo_sale_order_details').find("input[name='receiver_id_card_no']").change();
            $('.o_portal_cargo_sale_order_details').find("input[name='sender_visa_no']").change();
            $('.o_portal_cargo_sale_order_details').find("input[name='owner_visa_no']").change();
            $('.o_portal_cargo_sale_order_details').find("input[name='receiver_visa_no']").change();
            $('.o_portal_cargo_sale_order_details').find("input[name='receiver_mob_no']").change();
            $('.o_portal_cargo_sale_order_details').find("input[name='shipment_date']").change();
           
            
            if(hasError) {
              e.preventDefault();
              $('#o_portal_cargo_sale_order_form #property_submit_form').children("i").remove();
              $('#o_portal_cargo_sale_order_form #property_submit_form').attr('disabled',false);
              //.closest()
            }
            else{
                $(':disabled').each(function(e) {
                    $(this).removeAttr('disabled');
                });
                $('#o_portal_cargo_sale_order_form #property_submit_form').attr('disabled',true);
                $(this).submit();
            }
        }
          });



        //If the change event fires we want to see if the form validates.
        //But we don't want to check before the form has been submitted by the user
        //initially.
        $('#o_portal_cargo_sale_order_form').on("change", ".select2-offscreen", function () {
            if (!$.isEmptyObject(validobj.submitted)) {
                validobj.form();
            }
        });

        //A select2 visually resembles a textbox and a dropdown.  A textbox when
        //unselected (or searching) and a dropdown when selecting. This code makes
        //the dropdown portion reflect an error if the textbox portion has the
        //error class. If no error then it cleans itself up.
        $('#o_portal_cargo_sale_order_form').on("select2-opening", function (arg) {
            var elem = $(arg.target);
            if ($("#s2id_" + elem.attr("id") + " ul").hasClass("myErrorClass")) {
                //jquery checks if the class exists before adding.
                $(".select2-drop ul").addClass("myErrorClass");
            } else {
                $(".select2-drop ul").removeClass("myErrorClass");
            }
        });      
       
    }

    var $registrationForm = $('#o_portal_cargo_sale_order_form');
    if($registrationForm.length){
        var validobj = $registrationForm.validate({
            
            onkeyup: false,
            errorClass: "my_error",

           //put error message behind each form element
            errorPlacement: function (error, element) {
                
                if (element.attr('id') == 'shipment_date') 
                {
                    error.insertAfter(element.parents().next("div[role='alert']"));
                }
                else{
                    if(element.next("div[role='alert']").length > 0){
                        error.insertAfter(element.next("div[role='alert']"));
                    }
                    else{
                        error.insertAfter(element);
                    }
                }
                
            },

            //When there is an error normally you just add the class to the element.
            // But in the case of select2s you must add it to a UL to make it visible.
            // The select element, which would otherwise get the class, is hidden from
            // view.
            highlight: function (element, errorClass, validClass) {
                var elem = $(element);
                if (elem.hasClass("select2-offscreen")) {
                    $("#s2id_" + elem.attr("id") + " ul").addClass(errorClass);
                } else {
                    elem.addClass(errorClass);
                }
            },


            //When removing make the same adjustments as when adding
            unhighlight: function (element, errorClass, validClass) {
                var elem = $(element);
                if (elem.hasClass("select2-offscreen")) {
                    $("#s2id_" + elem.attr("id") + " ul").removeClass(errorClass);
                } else {
                    elem.removeClass(errorClass);
                }
            },

        });


        
    }

});
