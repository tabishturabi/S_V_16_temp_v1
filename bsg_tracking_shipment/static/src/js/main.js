odoo.define('portal.cargo.sale.shipment.track', function (require) {
    
        if($("#shipment_track_cargo_payment_content").length){
            $("#shipment_track_cargo_payment_content").on('change', "input[id='track_cargo_term_agree']", function () {
                if($(this)[0].checked == true){
                    $("#track_cargo_pay_with").find("#track_cargo_pay_with_content_dialog").show();
                    $("#track_cargo_pay_with").find("#track_cargo_warnning_pay_with_content_dialog").hide();
                }
                else{
                    $("#track_cargo_pay_with").find("#track_cargo_pay_with_content_dialog").hide();
                    $("#track_cargo_pay_with").find("#track_cargo_warnning_pay_with_content_dialog").show();
                }
            });
            $('#shipment_track_cargo_payment_content').find("input[id='track_cargo_term_agree']").change();
        }
        
        require('web.dom_ready');
    

});

function handleKeyPress(e) {
    let newValue = e.target.value + e.key;
    if (
    // It is not a number nor a control key?
    isNaN(newValue) &&
    e.which != 8 && // backspace
    e.which != 17 && // ctrl
    newValue[0] != '-' || // minus
    // It is not a negative value?
    newValue[0] == '-' &&
    isNaN(newValue.slice(1)))
        console.log('pass');

        // commented bc its generic
        // e.preventDefault(); // Then don't write it!
}
