view_navigation_bar = [
    {
        'path': '/view/bases/statistics/',
        'permission': [
            'read_statistics',
            'read_statistics_all',
        ],
        'text': '访问统计',
        'weight': 0,
    },
    {
        'path': '/view/bases/logs/',
        'permission': [
            'read_logs_all',
            'read_logs_file',
        ],
        'text': '服务日志',
        'weight': 0,
    },
    {
        'path':
        '/view/bases/user/',
        'permission': [
            'read_user_page',
            'read_user',
            'create_user',
            'update_user',
            'delete_user',
        ],
        'text':
        '用户管理',
        'weight':
        0,
    },
    {
        'path':
        '/view/bases/role/',
        'permission': [
            'read_permission_all',
            'create_role',
            'delete_role',
            'update_role',
            'read_role',
            'read_role_all',
        ],
        'text':
        '角色与权限',
        'weight':
        0,
    },
    {
        'path': '/view/bases/setup/',
        'permission': [
            'read_setup_module_all',
            'read_setup',
            'update_setup',
        ],
        'text': '参数设置',
        'weight': 0,
    },
]