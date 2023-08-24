odoo.define('portal.cargo.sale.bassami.coupon', function (require) {
    'use strict';
    
        require('web.dom_ready');

        if ($('#cargo_sale_order_card_details').length) {

            $('.show_bassami_coupon').on('click',function(e){
                $(e.currentTarget).hide();
                $('.bassami_coupon_form').show();
            });
            
        }
});        