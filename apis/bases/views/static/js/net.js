if (!Cookies.get('token_s')) {
    if (window.location.href.indexOf('/view/bases/token') == -1) {
        window.location.href = '/view/bases/token/';
    }
} else {
    if (window.location.href.indexOf('/view/bases/token') != -1) {
        window.location.href = '/view/bases/home/';
    }
}

function generalErrorHandling(request) {
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
}

function utilAjax(type, url, data, data_format, check, success, complete, success_reminder, not_close) {
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
    var headers = { 'Accept': 'application/json' }
    // data_format: query, json
    if (data_format == 'json') {
        data = JSON.stringify(data);
        headers['Content-Type'] = 'application/json';
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
            success(data, textStatus);
            if (success_reminder) {
                swal('请求成功', { icon: 'success', buttons: false, timer: 1500, });
            } else {
                if (!not_close) {
                    swal.close();
                }
            }
        },
        error: function (request, textStatus, errorThrown) {
            generalErrorHandling(request);
        },
        complete: function (request, textStatus) {
            complete(request, textStatus);
        },
    });
}

function utilAjaxFile(type, url, file, success, success_reminder) {
    var formData = new FormData();
    formData.append('file', file[0].files[0]);
    var progress_html = document.createElement('progress');
    progress_html.value = 0.0;
    progress_html.max = 100.0;
    $.ajax({
        type: type,
        url: url,
        data: formData,
        headers: {
            'Accept': 'application/json',
        },
        async: true,
        dataType: 'json',
        processData: false,
        contentType: false,
        beforeSend: function (request) {
            swal({
                text: '文件上传中……',
                content: progress_html,
                button: false,
                closeOnEsc: false,
                closeOnClickOutside: false,
            });
        },
        xhr: function () {
            var myXhr = $.ajaxSettings.xhr();
            if (myXhr.upload) {
                myXhr.upload.addEventListener('progress', function (e) {
                    var loaded = e.loaded;
                    var total = e.total;
                    progress_html.value = Math.floor(100 * loaded / total);
                }, false);
            }
            return myXhr;
        },
        success: function (data, textStatus) {
            success(data, textStatus);
            if (success_reminder) {
                swal('上传成功', { icon: 'success', buttons: false, timer: 1500, });
            } else {
                swal.close();
            }
        },
        error: function (request, textStatus, errorThrown) {
            generalErrorHandling(request);
        },
    });
}