$(document).ready(function(){
    let portal_user_form = $("form[action='/my/account']").length
    if (portal_user_form)
    {
        $(".checkbox_2fa").on("change", function(){
            $("#is_2fa_change").val("yes");
            if(this.checked) {
            }
            else{
                    $(".qrcode_div").remove();
            }
        });
    }
});
