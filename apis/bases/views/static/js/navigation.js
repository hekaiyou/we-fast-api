var c_username = Cookies.get('username');
if (c_username) {  // 检测用户名称的 Cookie 值
    $('#nav-username').append(Cookies.get('username'));
    $('#nav-avata').append('<img decoding="async" src="/api/bases/me/avata/free/" alt="Me Avata" width="40" height="40">');
    $('#right-hand-nav-off').hide();
    $('#right-hand-nav-on').show();
}
var c_permissions = Cookies.get('permissions');
if (c_permissions) {  // 检测用户权限的 Cookie 值
    var permissions = c_permissions.split(',');  // 用户权限列表
    navigationBar.forEach(function (value, index) {
        let permission = value['permission'];  // 菜单项需要的权限列表
        if (permission.every(v => permissions.includes(v))) {  // 匹配时显示菜单项
            $('#nav-content').append('<li><a href="' + value['path'] + '">' + value['text'] + '</a></li>');
        }
    })
}
$('#signout').click(function () {
    Cookies.remove('username');
    Cookies.remove('full_name');
    Cookies.remove('token_s');
    Cookies.remove('role');
    Cookies.remove('permissions');
    window.location.href = '/view/bases/token/';
});