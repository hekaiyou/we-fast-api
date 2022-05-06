$('#nav-username').append(Cookies.get('username'));
navigationBar.forEach(function (value, index) {
    let permission = value['permission'];
    let permissions = Cookies.get('permissions').split(',');
    if (permission.every(v => permissions.includes(v))) {
        $('#nav-content').append('<li><a href="' + value['path'] + '">' + value['text'] + '</a></li>');
    }
})