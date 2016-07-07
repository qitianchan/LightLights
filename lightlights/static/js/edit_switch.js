/**
 * Created by admin on 2016/7/7 0007.
 */
$(document).ready(function(){
    var form = $('#switch-update');
    form.submit(function(ev){
        var lights = [];
        $('input:checked').each(function(){
           lights.push($(this).val());
        });

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function(res){
                toastr.success('更新成功')
            },
            error: function(res){
                toastr.error('更新失败')
            }
        });
         ev.preventDefault();
    })
});