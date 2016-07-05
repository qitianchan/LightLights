/**
 * Created by admin on 2016/7/5 0005.
 */
$(document).ready(function(){
    //var table = $('#lights').DataTable();
    //$('#lights tbody').on('click', 'a.edit', function(){
    //    var data = table.row(this.parent).data();
    //    alert( 'You clicked on '+data[0]+'\'s row' );
    //    oTable = $('#lighhts').dataTable()
    //    oTable
    //});
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
        //jqTds[2].innerHTML = '<input type="text" class="form-control small" value="' + aData[2] + '">';
        jqTds[3].innerHTML = '<a class=" btn btn-sm btn-primary edit" href="" style="margin-right: 0.5em;">保存</a>' + '<a class=" btn btn-sm btn-danger cancel" href="">放弃</a>';
    }

    function saveRow(oTable, nRow) {

        var data = {};
        var jqInputs = $('input', nRow);
        data.identifier = jqInputs[0].value;
        data.eui = jqInputs[1].value;
        var url = window.location.href;

        // update row
        if($(nRow).data('light-id') !== undefined) {
            data.light_id = $(nRow).data('light-id');
            url = url.substr(0, url.lastIndexOf('/')) + '/light/update';
        }else {
            url = url.substr(0, url.lastIndexOf('/'))+ '/light/add';
        }

        $.ajax({
            url: url,
            type: 'post',
            data: data,
            success: function(res){
                toastr.success('添加成功');
                $(nRow).data('light-id', res.data.light.id);
                var jqInputs = $('input', nRow);
                oTable.fnUpdate(res.data.light.identifier, nRow, 0, false);
                oTable.fnUpdate(res.data.light.eui, nRow, 1, false);
                oTable.fnUpdate(res.data.light.status + '(' + res.data.light.on_count +')', nRow, 2, false);
                oTable.fnUpdate('<a class="edit" href="">编辑</a>', nRow, 3, false);
                oTable.fnUpdate('<a class="delete" href="">删除</a>', nRow, 4, false);
                oTable.fnUpdate('<a class="reset" href="">重置</a>', nRow, 5, false);
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

    var oTable = $('#lights').dataTable({
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

    $('#light_new').click(function (e) {
        e.preventDefault();
        var aiNew = oTable.fnAddData(['', '', '',
            '<a class="edit" href="">编辑</a>','<a class="cancel" data-mode="new" href="">删除</a>', '<a class="reset" href="">重置</a>'
        ]);
        var nRow = oTable.fnGetNodes(aiNew[0]);
        editRow(oTable, nRow);
        nEditing = nRow;
    });

    $('#lights').on('click', 'a.delete', function (e) {
        e.preventDefault();

        if (confirm("确定要删除吗?") == false) {
            return;
        }
        var nRow = $(this).parents('tr')[0];
         if($(nRow).data('light-id') !== undefined) {
                var light_id = $(nRow).data('light-id');
         }

        var url = window.location.href;
        url = url.substr(0, url.lastIndexOf('/')) + '/light/delete';

        $.ajax({
            url: url,
            type: 'post',
            data: {light_id: light_id},
            success: function(res){
                toastr.success(res.message);
                oTable.fnDeleteRow(nRow);
            },
            error: function(res){
                toastr.error(res.responseJSON.message);
            }
        });
    });

    $('#lights').on('click','a.cancel', function (e) {
        e.preventDefault();
        if ($(this).attr("data-mode") == "new") {
            var nRow = $(this).parents('tr')[0];
            oTable.fnDeleteRow(nRow);
        } else {
            restoreRow(oTable, nEditing);
            nEditing = null;
        }
    });

    $('#lights').on('click', 'a.edit', function (e) {
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

    $('#lights').on('click', 'a.reset', function(e){
        e.preventDefault();
        var nRow = $(this).parents('tr')[0];
        if($(nRow).data('light-id') !== undefined) {
            var light_id = $(nRow).data('light-id');
            var url = window.location.href.substr(0, window.location.href.lastIndexOf('/')) + '/light/reset';
            $.ajax({
            url: url,
            type: 'post',
            data: {light_id: light_id},
            success: function(res){
                toastr.success(res.message);
                oTable.fnUpdate(res.data.light.status + '(' + res.data.light.on_count +')', nRow, 2, false);
            },
            error: function(res){
                toastr.success(res.responseJSON.message);
            }
        })
        }

    })

});