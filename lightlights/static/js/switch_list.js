/**
 * Created by admin on 2016/7/5 0005.
 */
$(document).ready(function(){
    function restoreRow(oTable, nRow) {
        var aData = oTable.fnGetData(nRow);
        var jqTds = $('>td', nRow);

        for (var i = 0, iLen = jqTds.length; i < iLen; i++) {
            oTable.fnUpdate(aData[i], nRow, i, false);
        }

        oTable.fnDraw();
    }

    function editRow(oTable, nRow) {
        var aData = oTable.fnGetData(nRow);
        var jqTds = $('>td', nRow);
        jqTds[0].innerHTML = '<input type="text" class="form-control small" value="' + aData[0] + '">';
        jqTds[1].innerHTML = '<input type="text" class="form-control small" value="' + aData[1] + '">';
        jqTds[2].innerHTML = '<input type="text" class="form-control small" value="' + aData[2] + '">';
        jqTds[3].innerHTML = '<a class=" btn btn-sm btn-primary edit" href="" style="margin-right: 0.5em;">保存</a>' + '<a class=" btn btn-sm btn-danger cancel" href="">放弃</a>';
    }

    function saveRow(oTable, nRow) {

        var data = {};
        var jqInputs = $('input', nRow);
        data.name = jqInputs[0].value;
        data.eui = jqInputs[1].value;
        data.group_eui = jqInputs[2].value;
        var url = window.location.href;

        // update row
        if($(nRow).data('switch-id') !== undefined) {
            data.switch_id = $(nRow).data('switch-id');
            url = url.substr(0, url.lastIndexOf('/')) + '/switch/update';
        }else {
            url = url.substr(0, url.lastIndexOf('/'))+ '/switch/add';
        }

        $.ajax({
            url: url,
            type: 'post',
            data: data,
            success: function(res){
                toastr.success(res.message);
                $(nRow).data('switch-id', res.data.switch.id);
                var jqInputs = $('input', nRow);
                oTable.fnUpdate(res.data.switch.name, nRow, 0, false);
                oTable.fnUpdate(res.data.switch.eui, nRow, 1, false);
                oTable.fnUpdate(res.data.switch.group_eui, nRow, 2, false);
                oTable.fnUpdate('<a class="edit" href="">编辑</a>', nRow, 3, false);
                oTable.fnUpdate('<a class="delete" href="">删除</a>', nRow, 4, false);
                oTable.fnDraw();
                nEditing = null;

            },
            error: function(res){
                toastr.error(res.responseJSON.message);
                restoreRow(oTable, nEditing);
                nEditing = null;
            }
        });
    }

    var oTable = $('#switchs').dataTable({
        "aLengthMenu": [
            [5, 15, 20, -1],
            [5, 15, 20, "All"] // change per page values here
        ],
        // set the initial value
        "iDisplayLength": 15,
        "oLanguage": {
            "sLengthMenu": "_MENU_ 条记录每页",
            "oPaginate": {
                "sPrevious": "上一页",
                "sNext": "下一页"
            },
        },
        "aoColumnDefs": [{
                'bSortable': false,
                'aTargets': [0]
            }
        ]
    });

    var nEditing = null;

    $('#switch_new').click(function (e) {
        e.preventDefault();
        var aiNew = oTable.fnAddData(['', '', '',
            '<a class="edit" href="">编辑</a>','<a class="cancel" data-mode="new" href="">删除</a>'
        ]);
        var nRow = oTable.fnGetNodes(aiNew[0]);
        editRow(oTable, nRow);
        nEditing = nRow;
    });

    $('#switchs').on('click', 'a.delete', function (e) {
        e.preventDefault();

        if (confirm("确定要删除吗?") == false) {
            return;
        }
        var nRow = $(this).parents('tr')[0];
         if($(nRow).data('switch-id') !== undefined) {
                var switch_id = $(nRow).data('switch-id');
         }

        var url = window.location.href;
        url = url.substr(0, url.lastIndexOf('/')) + '/switch/delete';

        $.ajax({
            url: url,
            type: 'post',
            data: {switch_id: switch_id},
            success: function(res){
                toastr.success(res.message);
                oTable.fnDeleteRow(nRow);
            },
            error: function(res){
                toastr.error(res.responseJSON.message);
            }
        });
    });

    $('#switchs').on('click','a.cancel', function (e) {
        e.preventDefault();
        if ($(this).attr("data-mode") == "new") {
            var nRow = $(this).parents('tr')[0];
            oTable.fnDeleteRow(nRow);
        } else {
            restoreRow(oTable, nEditing);
            nEditing = null;
        }
    });

    $('#switchs').on('click', 'a.edit', function (e) {
        e.preventDefault();

        /* Get the row as a parent of the link that was clicked ` */
        var nRow = $(this).parents('tr')[0];

        if (nEditing !== null && nEditing != nRow) {
            /* Currently editing - but not this row - restore the old before continuing to edit mode */
            restoreRow(oTable, nEditing);
            editRow(oTable, nRow);
            nEditing = nRow;
        } else if (nEditing == nRow && this.innerHTML == "保存") {
            /* Editing this row and want to save it */
            saveRow(oTable, nEditing);
            nEditing = null;
        } else {
            /* No edit in progress - let's start one */
            editRow(oTable, nRow);
            nEditing = nRow;
        }
    });

    $('#switchs').on('click', 'a.reset', function(e){
        e.preventDefault();
        var nRow = $(this).parents('tr')[0];
        if($(nRow).data('switch-id') !== undefined) {
            var switch_id = $(nRow).data('switch-id');
            var url = window.location.href.substr(0, window.location.href.lastIndexOf('/')) + '/switch/reset';
            $.ajax({
            url: url,
            type: 'post',
            data: {switch_id: switch_id},
            success: function(res){
                toastr.success(res.message);
                oTable.fnUpdate(res.data.switch.status + '(' + res.data.switch.on_count +')', nRow, 2, false);
            },
            error: function(res){
                toastr.success(res.responseJSON.message);
            }
        })
        }

    })

});