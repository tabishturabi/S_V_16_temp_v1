odoo.define('portal.cargo.sale.get.price', function (require) {
    'use strict';
    
        require('web.dom_ready');
        var core = require('web.core');
        var rpc = require("web.rpc");
        var config = require('web.config');
        var ajax = require('web.ajax');
        var time = require('web.time');

        var isMobile = config.device.isMobile;
        
        var _t = core._t;

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

        if ($('#o_cargo_sale_order_line').length) {

            if ($('#cargo_sale_order_line_form').length) {

            $('#get_so_line_submit_btn').on('click',  function(e){
                console.log('.................in so line submit button..................')
                    var so_line_spec_form_has_error = false;
                    if (!($("input[name='agreement_show']")[0].checked) && !($("input[name='chasis_no_show']")[0].checked) && !($("input[name='plate_info_show']")[0].checked)){
                                so_line_spec_form_has_error = true;
                                alert("You can not submit empty form please pass any data");
                            }
//                    if ($("#shipment-info").length){
//                        var all_checks_alert_area;
//                        if($("#shipment-info").next("div[role='alert']").length ){
//                                all_checks_alert_area = $("#shipment-info").next("div[role='alert']");
//                            }
//                        else if ($("#shipment-info").parent().find("div[role='alert']").length){
//                                all_checks_alert_area = $("#shipment-info").parent().find("div[role='alert']");
//                            }
//                        if (all_checks_alert_area){
//                            all_checks_alert_area.hide();
//                            all_checks_alert_area.text('');
//                            if (!($("input[name='agreement_show']")[0].checked) && !($("input[name='chasis_no_show']")[0].checked) && !($("input[name='plate_info_show']")[0].checked)){
//                                all_checks_alert_area.text('This Field Is Required');
//                                all_checks_alert_area.show();
//                                so_line_spec_form_has_error = true;
//                            }
//
//                            }
//
//                    }
                    if ($("input[name='agreement_show']")[0].checked){
                        if ($("input[name='agreement']").length){
                            var agreement_alert_area;
                            if($("input[name='agreement']").next("div[role='alert']").length ){
                                    agreement_alert_area = $("input[name='agreement']").next("div[role='alert']");
                                }
                            else if ($("input[name='agreement']").parent().find("div[role='alert']").length){
                                    agreement_alert_area = $("input[name='agreement']").parent().find("div[role='alert']");
                                }
                            if (agreement_alert_area){
                                agreement_alert_area.hide();
                                agreement_alert_area.text('');
                                if(!($("input[name='agreement']")).val()){
                                    agreement_alert_area.text('This Field Is Required');
                                    agreement_alert_area.show();
                                    so_line_spec_form_has_error = true;
                                }
                            }

                        }

                    }
                    console.log('.................in so line submit button.agreement_show.................')
                    if ($("input[name='chasis_no_show']")[0].checked){
                        if ($("input[name='chasis_no']").length){
                            var chasis_alert_area;
                            if($("input[name='chasis_no']").next("div[role='alert']").length ){
                                    chasis_alert_area = $("input[name='chasis_no']").next("div[role='alert']");
                                }
                            else if ($("input[name='chasis_no']").parent().find("div[role='alert']").length){
                                    chasis_alert_area = $("input[name='chasis_no']").parent().find("div[role='alert']");
                                }
                            if (chasis_alert_area){
                                chasis_alert_area.hide();
                                chasis_alert_area.text('');
                                if(!($("input[name='chasis_no']")).val()){
                                    chasis_alert_area.text('This Field Is Required');
                                    chasis_alert_area.show();
                                    so_line_spec_form_has_error = true;
                                }
                            }

                        }

                    }
                    console.log('.................in so line submit button.chasis_no_show.................')
                    if ($("input[name='plate_info_show']")[0].checked){
                        if ($("input[name='plate_no']").length){
                            var plate_no_alert_area;
                            if($("input[name='plate_no']").next("div[role='alert']").length ){
                                    plate_no_alert_area = $("input[name='plate_no']").next("div[role='alert']");
                                }
                            else if ($("input[name='plate_no']").parent().find("div[role='alert']").length){
                                    plate_no_alert_area = $("input[name='plate_no']").parent().find("div[role='alert']");
                                }
                            if (plate_no_alert_area){
                                plate_no_alert_area.hide();
                                plate_no_alert_area.text('');
                                if(!($("input[name='plate_no']")).val()){
                                    plate_no_alert_area.text('This Field Is Required');
                                    plate_no_alert_area.show();
                                    so_line_spec_form_has_error = true;
                                }
                            }

                        }
                        if ($("select[name='plate_one']").length){
                            var plate_one_alert_area;
                            if($("select[name='plate_one']").next("div[role='alert']").length ){
                                    plate_one_alert_area = $("select[name='plate_one']").next("div[role='alert']");
                                }
                            else if ($("select[name='plate_one']").parent().find("div[role='alert']").length){
                                    plate_one_alert_area = $("select[name='plate_one']").parent().find("div[role='alert']");
                                }
                            if (plate_one_alert_area){
                                plate_one_alert_area.hide();
                                plate_one_alert_area.text('');
                                if(!($("select[name='plate_one']")).val()){
                                    plate_one_alert_area.text('This Field Is Required');
                                    plate_one_alert_area.show();
                                    so_line_spec_form_has_error = true;
                                }
                            }

                        }
                        if ($("select[name='plate_second']").length){
                            var plate_second_alert_area;
                            if($("select[name='plate_second']").next("div[role='alert']").length ){
                                    plate_second_alert_area = $("select[name='plate_second']").next("div[role='alert']");
                                }
                            else if ($("select[name='plate_second']").parent().find("div[role='alert']").length){
                                    plate_second_alert_area = $("select[name='plate_second']").parent().find("div[role='alert']");
                                }
                            if (plate_one_alert_area){
                                plate_second_alert_area.hide();
                                plate_second_alert_area.text('');
                                if(!($("select[name='plate_second']")).val()){
                                    plate_second_alert_area.text('This Field Is Required');
                                    plate_second_alert_area.show();
                                    so_line_spec_form_has_error = true;
                                }
                            }

                        }
                        if ($("select[name='plate_third']").length){
                            var plate_third_alert_area;
                            if($("select[name='plate_third']").next("div[role='alert']").length ){
                                    plate_third_alert_area = $("select[name='plate_third']").next("div[role='alert']");
                                }
                            else if ($("select[name='plate_third']").parent().find("div[role='alert']").length){
                                    plate_third_alert_area = $("select[name='plate_third']").parent().find("div[role='alert']");
                                }
                            if (plate_third_alert_area){
                                plate_third_alert_area.hide();
                                plate_third_alert_area.text('');
                                if(!($("select[name='plate_third']")).val()){
                                    plate_third_alert_area.text('This Field Is Required');
                                    plate_third_alert_area.show();
                                    so_line_spec_form_has_error = true;
                                }
                            }

                        }
                    }
                    console.log('.................in so line submit button.plate_info_show.................')
//                    $('#cargo_sale_order_line_form').submit();
//                    checkRequiredField();
                    if(!so_line_spec_form_has_error){
                        $('#cargo_sale_order_line_form').submit();
                    }
                });

                $('#cargo_sale_order_line_form').on('change', "input[name='agreement_show']", function () {
                    console.log("on change agreement....................")
                    if($(this)[0].checked == true){
                        console.log("on change agreement checked....................")
                        $('#agreement').show();
                        }
                    else{
                        $('#agreement').hide();
                    }

                    });
                $('#cargo_sale_order_line_form').on('change', "input[name='chasis_no_show']", function () {
                    console.log("on change chasis_no....................")
                    if($(this)[0].checked == true){
                         console.log("on change chasis_no checked....................")
                        $('#chasis').show();
                        }
                    else{
                        $('#chasis').hide();
                    }
            });
             $('#cargo_sale_order_line_form').on('change', "input[name='plate_info_show']", function () {
                    if($(this)[0].checked == true){
                        $('#plate_no').show();
                        $('#plate_one').show();
                        $('#plate_second').show();
                        $('#plate_third').show();
                        }
                    else{
                        $('#plate_no').hide();
                        $('#plate_one').hide();
                        $('#plate_second').hide();
                        $('#plate_third').hide();
                    }
            });
            }



            }


    
        if ($('#o_cargo_shipment_get_price').length) {

            if ($('#cargo_sale_get_price_form').length) {
                var hasError = false ;
                var inStart = true;

                var loc_to_options = $("select[name='loc_to']:enabled option:not(:first)");
                var loc_from_options = $("select[name='loc_from']:enabled option:not(:first)");
                var model_options = $("#cargo_sale_get_price_form select[name='car_model']:enabled option:not(:first)");
                var setAstricForRequired = ()=>{
                    var required_fields = $("#cargo_sale_get_price_form .form-control[required='required']");
                    _.each(required_fields, function (field){
                        var $elem = $(field);
                        $elem.parent().parent().find('.col-form-label').append("<b style='color:red;'> * </b>");
                    });
                };
                

                setAstricForRequired();



                $('#cargo_sale_get_price_form').on('change', "select[name='loc_from']", function () {
                    if($(this).val()){
                    //Remove From To Location    
                    var select = $('#cargo_sale_get_price_form').find("select[name='loc_to']");
                    loc_to_options.detach();
                    var displayed_loc_to = loc_to_options.filter("[value !="+($(this).val() || 0)+"]");
                    var nb = displayed_loc_to.appendTo(select).show().length;
                    select.parent().toggle(nb>=1);
                    }
                    checkCurrentRequiredField($(this));
                });


                $('#cargo_sale_get_price_form').on('change', "select[name='loc_to']", function () {
                    if($(this).val()){
                    var select = $('#cargo_sale_get_price_form').find("select[name='loc_from']");
                    loc_from_options.detach();
                    var displayed_loc_from = loc_from_options.filter("[value !="+($(this).val() || 0)+"]");
                    var nb = displayed_loc_from.appendTo(select).show().length;
                    select.parent().toggle(nb>=1);
                    }  
                    checkCurrentRequiredField($(this));            
                }); 


                $('#cargo_sale_get_price_form').on('change', "select[name='car_make']", function () {
                        var select_option = $(this.options[this.selectedIndex]);
                        var select = $("#cargo_sale_get_price_form").find("select[name='car_model']");
                        select.select2("val", "");
                        select.select2().val('');
                        select.val('');
                        model_options.detach();
                        var displayed_model = model_options.filter("[data-maker="+(select_option.attr('maker') || 0)+"]");
                        var nb = displayed_model.appendTo(select).show().length;
                        select.parent().toggle(nb>=1);
                        if (!inStart){
                            checkCurrentRequiredField($(this));
                        }
                        else{
                            inStart = false;
                        } 
                });

                 //To Get Car Size
                $('#cargo_sale_get_price_form').on('change', "select[name='car_model']", function () {
                    
                    var car_model_val = $(this).val();
                    var car_maker_val = $("#cargo_sale_get_price_form select[name='car_make']").val();
                    if (car_model_val){
                        var car_size = $("#cargo_sale_get_price_form select[name='car_size']");                        
                        car_size.prepend('<i class="fa fa-spinner fa-spin"></i> ');
                        $('#get_price_next_btn').attr('disabled',true);

                        var params = {
                            'car_model': parseInt(car_model_val),
                            'car_config_id': parseInt(car_maker_val)
                        };
                        ajax.jsonRpc("/cargo_orders/get_car_size", 'call', params)
                        .then(function (data) {
                            console.log("1********",data);
                            if (data.car_size) {
                                console.log("2********",data.car_size); 
                                car_size.removeClass('fa-spinner');
                                car_size.val(data.car_size);
                            }
                            if (car_size.val()){
                                $('#get_price_next_btn').attr('disabled',false);
                            }
                            car_size.change();
                        });
                        
                        
                        /*var def1 = rpc.query({
                            'model': 'bsg_vehicle_cargo_sale_line',
                            'method': 'get_car_size',
                            args: [parseInt(car_model_val),
                                parseInt(car_maker_val)
                         ]
                        }).then(function (result) {
                            console.log("*********",result);
                            car_size.removeClass('fa-spinner');
                            _.each(result, function (data) {
                                car_size.val(data.car_size[0]);
                                
                            });
                            if (car_size.val()){
                                $('#get_price_next_btn').attr('disabled',false);
                            }
                            car_size.change();
                        });*/

                    } 
                    checkCurrentRequiredField($(this));
                    
                });
                //To Get Car Size
                $('#cargo_sale_get_price_form').on('change', "select[name='car_size']", function () {
                    checkCurrentRequiredField($(this));
                });

                



                $("#cargo_sale_get_price_form").find("select[name='loc_from']").select2();
                $("#cargo_sale_get_price_form").find("select[name='loc_to']").select2();
                $("#cargo_sale_get_price_form").find("select[name='car_make']").change();

                $("#cargo_sale_get_price_form").find("select[name='car_make']").select2();
                $("#cargo_sale_get_price_form").find("select[name='car_model']").select2();

                $('#get_price_next_btn').on('click',  function(e){
                    checkRequiredField();
                    if(!hasError){
                        $('#cargo_sale_get_price_form').find('#shipment-info').hide();
                        $('#cargo_sale_get_price_form').find('#contact-info').fadeIn();
                        $('#o_cargo_shipment_get_price').find('.box-title').text(_t('Contact Information'));
                        
                        //$('#o_cargo_shipment_get_price').find('.box-footer').find('#get_price_next_btn').replaceWith(``);
                        $('#o_cargo_shipment_get_price').find('.box-footer').find('#get_price_next_btn').hide();
                        $('#o_cargo_shipment_get_price').find('.box-footer').find('#get_price_submit_btn').show();
                        var $phone_el = $("#cargo_sale_get_price_form").find("#contact-info").find("input[name='customer_phone']");
                        $phone_el.attr('required','required');
                        $phone_el.parent().parent().find('.col-form-label').append("<b style='color:red;'> * </b>")
                        

                    }
                });

                $('#cargo_sale_get_price_form').on('change', "input[name='customer_phone']", function () {
                    checkCurrentRequiredField($(this));
                });

                $('#get_price_submit_btn').on('click',  function(e){
                    console.log("************Click");
                    checkRequiredField();
                    if(!hasError){
                        $('#cargo_sale_get_price_form').submit();
                    }
                });

                var checkRequiredField =()=>{
                     // validation code here
                     hasError = false;
                     $("#cargo_sale_get_price_form .alert[role='alert']").hide();
                     var in_required_fields = $("#cargo_sale_get_price_form .form-control[required='required']").removeClass("is-invalid");
                     var in_required_fields = $("#cargo_sale_get_price_form .form-control[required='required']");
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
                };

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

    
                

            }

        }


        if ($('#o_portal_sale_order_from_lead').length) {
        var hasError = false;

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



        $('#o_portal_sale_order_from_lead').on('change', "input[name='sender_default']", function () {
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


        $('#o_portal_sale_order_from_lead').on('change', "input[name='owner_default']", function () {
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

        $('#o_portal_sale_order_from_lead').on('change', "input[name='receiver_default']", function () {
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

        $('#o_portal_sale_order_from_lead').on('change', "select[name='sender_type']", function () {
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

        $('#o_portal_sale_order_from_lead').on('change', "select[name='owner_type']", function () {
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

        $('#o_portal_sale_order_from_lead').on('change', "select[name='receiver_type']", function () {
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


        $('#o_portal_sale_order_from_lead').find("input[name='sender_default']").change();
        $('#o_portal_sale_order_from_lead').find("input[name='owner_default']").change();
        $('#o_portal_sale_order_from_lead').find("input[name='receiver_default']").change();
        $('#o_portal_sale_order_from_lead').find("select[name='sender_nationality']").select2();
        $('#o_portal_sale_order_from_lead').find("select[name='receiver_nationality']").select2();
        $('#o_portal_sale_order_from_lead').find("select[name='owner_nationality']").select2();


        var order_required_fields = $("#o_portal_sale_order_from_lead .form-control[required='required']");
        _.each(order_required_fields, function (field){
            var $elem = $(field);
            $elem.parent().find('.col-form-label').append("<b style='color:red;'> * </b>");
            if ($elem.attr('id') == 'shipment_date'){
                $elem.parent().parent().find('.col-form-label').append("<b style='color:red;'> * </b>");
            }
        });


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





        //################SO LINE FIELDS###########################
        $('#o_portal_sale_order_from_lead').on('change', "input[name='plate_no']", function () {
            var input=$(this);
            if(input.val()){
                var register_val = $("#o_portal_sale_order_from_lead").find("select[name='plate_registration']");
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
            else{
                input.removeClass("is-invalid");
                input.parent().find("div[role='alert']").hide();
            }
            });



            $('#o_portal_sale_order_from_lead').on('change', "select[name='plate_registration']", function () {
                if($(this).val()){
                    var register_val = $(this).val();
                    var palte_one = $("#o_portal_sale_order_from_lead select[name='palte_one']");
                    var palte_second = $("#o_portal_sale_order_from_lead select[name='palte_second']");
                    var palte_third = $("#o_portal_sale_order_from_lead select[name='palte_third']");
                    var plate_no = $("#o_portal_sale_order_from_lead input[name='plate_no']");

                    var non_saudi_plate_no = $("#o_portal_sale_order_from_lead input[name='non_saudi_plate_no']");

                    $('#o_portal_sale_order_from_lead').find("input[name='plate_no']").change();

                    var chassis_no = $("#o_portal_sale_order_from_lead input[name='chassis_no']");

                    var palte_type = $("#o_portal_sale_order_from_lead select[name='plate_type']");
                    var plate_type_field = $("#o_portal_sale_order_from_lead").find('#plate_type_field');
                    

                    var saudi_div = $("#o_portal_sale_order_from_lead #saudi_create");
                    var non_saudi_div = $("#o_portal_sale_order_from_lead #non-saudi_create");
                    
                    if(register_val == 'saudi')
                    {
                        saudi_div.show();
                        non_saudi_div.hide();

                        palte_one.attr("required", true).show();
                        palte_second.attr("required", true).show();
                        palte_third.attr("required", true).show();
                        plate_no.attr("required", true).show();
                        plate_type_field.show();
                        palte_type.attr("required", true).show();
                        

                        non_saudi_plate_no.attr("required", false).hide();
                        chassis_no.attr("required", false);
                    }
                    if(register_val == 'non-saudi')
                    {
                        saudi_div.hide();
                        non_saudi_div.show();

                        palte_one.attr("required", false).hide();
                        palte_second.attr("required", false).hide();
                        palte_third.attr("required", false).hide();
                        plate_no.attr("required", false).hide();

                        plate_type_field.show();
                        palte_type.attr("required", true).show();
                        non_saudi_plate_no.attr("required", true).show(); 
                        chassis_no.attr("required", false);                

                    }
                    if (register_val == 'new_vehicle')
                    {
                        saudi_div.hide();
                        non_saudi_div.show();

                        palte_one.attr("required", false).hide();
                        palte_second.attr("required", false).hide();
                        palte_third.attr("required", false).hide();
                        plate_no.attr("required", false).hide();

                        plate_type_field.hide();
                        palte_type.attr("required", false).hide();
                        non_saudi_plate_no.attr("required", false).show();
                        chassis_no.attr("required", true);
                    }
                }  
            });


            $("#o_portal_sale_order_from_lead").find("select[name='plate_registration']").change();
            inStart = true;
            $("#o_portal_sale_order_from_lead").find("select[name='year']").select2();
            $("#o_portal_sale_order_from_lead").find("select[name='car_color']").select2();
        //################END SO LINE FIELDS#######################


        $('#o_portal_sale_order_from_lead').on('submit', function(e){
            if ($('#o_portal_sale_order_from_lead').valid()){
            
            var $elem = $(this);
            $('#o_portal_sale_order_from_lead #create_order_from_lead_submit_form').prepend('<i class="fa fa-spinner fa-spin"></i>');
            $('#o_portal_sale_order_from_lead #create_order_from_lead_submit_form').attr('disabled',true);
            // validation code here
            hasError = false;
            $('#o_portal_sale_order_from_lead').find("input[name='sender_id_card_no']").change();
            $('#o_portal_sale_order_from_lead').find("input[name='owner_id_card_no']").change();
            $('#o_portal_sale_order_from_lead').find("input[name='receiver_id_card_no']").change();
            $('#o_portal_sale_order_from_lead').find("input[name='sender_visa_no']").change();
            $('#o_portal_sale_order_from_lead').find("input[name='owner_visa_no']").change();
            $('#o_portal_sale_order_from_lead').find("input[name='receiver_visa_no']").change();
            $('#o_portal_sale_order_from_lead').find("input[name='receiver_mob_no']").change();
            $('#o_portal_sale_order_from_lead').find("input[name='shipment_date']").change();
            $('#o_portal_sale_order_from_lead').find("input[name='plate_no']").change();
           
            
            if(hasError) {
              e.preventDefault();
              $('#o_portal_sale_order_from_lead #create_order_from_lead_submit_form').children("i").remove();
              $('#o_portal_sale_order_from_lead #create_order_from_lead_submit_form').attr('disabled',false);
              //.closest()
            }
            else{
                $(':disabled').each(function(e) {
                    $(this).removeAttr('disabled');
                });
                $('#o_portal_sale_order_from_lead #create_order_from_lead_submit_form').attr('disabled',true);
                //$(this).submit();
            }
        }
          });


        //If the change event fires we want to see if the form validates.
        //But we don't want to check before the form has been submitted by the user
        //initially.
        $('#o_portal_sale_order_from_lead').on("change", ".select2-offscreen", function () {
            if (!$.isEmptyObject(validobj.submitted)) {
                validobj.form();
            }
        });

        //A select2 visually resembles a textbox and a dropdown.  A textbox when
        //unselected (or searching) and a dropdown when selecting. This code makes
        //the dropdown portion reflect an error if the textbox portion has the
        //error class. If no error then it cleans itself up.
        $('#o_portal_sale_order_from_lead').on("select2-opening", function (arg) {
            var elem = $(arg.target);
            if ($("#s2id_" + elem.attr("id") + " ul").hasClass("myErrorClass")) {
                //jquery checks if the class exists before adding.
                $(".select2-drop ul").addClass("myErrorClass");
            } else {
                $(".select2-drop ul").removeClass("myErrorClass");
            }
        });      
       
            var $registrationForm = $('#o_portal_sale_order_from_lead');
            if($registrationForm.length){
                var validobj = $registrationForm.validate({
                    
                    onkeyup: false,
                    errorClass: "my_error",
        
                   //put error message behind each form element
                    errorPlacement: function (error, element) {
                        if (['palte_one','palte_second','palte_third','plate_no'].includes(element.attr('name'))){
                            if(element.parent().find("label.my_error").length == 0 || element.parent().find("label.my_error").css('display') == 'none'){
                                error.insertAfter(element.parent().find("div[role='alert']"));
                            }
                        }
                        else if (element.attr('id') == 'shipment_date') 
                        {
                            error.insertAfter(element.parent().next("div[role='alert']"));
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

        }
});        
