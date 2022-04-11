function utilAjax(type, url, data, success) {
    $.ajax({
        type: type,
        url: url,
        data: data,
        dataType: 'json',
        beforeSend: function (request) {
            swal({
                text: '网络请求中……',
                button: false,
                closeOnEsc: false,
                closeOnClickOutside: false,
            });
        },
        success: function (data, textStatus) {
            swal.close();
            success(data, textStatus);
        },
        error: function (request, textStatus, errorThrown) {
            console.log(request, textStatus, errorThrown);
            if (request.status == 0) {
                var errText = '服务器无法连接';
                var errIcon = 'error';
            } else {
                var errText = request.responseJSON.detail;
                var errIcon = 'warning';
            }
            swal({
                icon: errIcon,
                title: request.status.toString(),
                text: errText,
                button: false,
            });
        },
    });
}