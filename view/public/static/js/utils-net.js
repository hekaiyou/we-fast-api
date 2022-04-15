if (!Cookies.get('token_s')) {
    if (window.location.href.indexOf('/view/users/token') == -1) {
        window.location.href = '/view/users/token/';
    }
} else {
    if (window.location.href.indexOf('/view/users/token') != -1) {
        window.location.href = '/view/users/dashboard/';
    }
}

function utilAjax(type, url, data, check, success) {
    var checkResult = true;
    $.each(check, function (key, value) {
        if (!value[0].test(data[key])) {
            swal({
                icon: 'info',
                title: '校验异常',
                text: value[1],
                button: false,
            });
            checkResult = false;
            return false;
        }
    });
    if (!checkResult) {
        return;
    }
    var headers = { 'Accept': 'application/json;charset=utf-8' }
    if (type == 'PUT') {
        data = JSON.stringify(data);
        headers['Content-Type'] = 'application/json;charset=utf-8';
    }
    $.ajax({
        type: type,
        url: url,
        data: data,
        dataType: 'json',
        headers: headers,
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
            } else if (request.status == 422) {
                var errText = '请求格式或内容错误';
                var errIcon = 'error';
            } else if (request.status == 405) {
                var errText = '请求方法不被允许';
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