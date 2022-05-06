$('#nav-username').append(Cookies.get('username'));
$('#signout').click(function () {
    Cookies.remove('username');
    Cookies.remove('token_s');
    Cookies.remove('role');
    Cookies.remove('permissions');
    window.location.href = '/view/bases/token/';
});
navigationBar.forEach(function (value, index) {
    let permission = value['permission'];
    let permissions = Cookies.get('permissions').split(',');
    if (permission.every(v => permissions.includes(v))) {
        $('#nav-content').append('<li><a href="' + value['path'] + '">' + value['text'] + '</a></li>');
    }
})