$(document).ready(function(){
	var url = location.pathname;
	if (url == '/my/leave'){
		$(".time_period").hide();
		var date = new Date();
		$("#date_from, #date_to").val(date.toISOString().substr(0, 10));
		$("#half-days").on('change',function(){
			var status = $(this).prop("checked");
			if (status){
				$(".time_period").show();
				$(".date_to").hide();
			}
			else {
				$(".time_period").hide();
				$(".date_to").show();
			}
		});
		$(".form-process").on('submit',function(){
			var from=$("#date_from").val();
			var to=$("#date_to").val();
			if (from <= to){
				return true;
			}
			else {
				return false;
			}
		})
	}
})