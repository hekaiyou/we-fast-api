# WeFastAPI 简单视图

如果按照前面的教程, 我们已经在 `my_module` 模块实现了增加、删除、修改、查询和分页的接口, 现在我们可以为这些接口添加简单的视图, 需要创建两个新的模板页面, 当前 `my_module` 模块的目录结构应该如下所示：

```bash
my_module/
    views/
        static/
            css/
            image/
            js/
        templates/
            my_module/
                items.html
                drawing-prompt.html
                drawing-prompt-edit.html
        view_navigation.py
        view_url.py
    __init__.py
    api_drawing_prompt.py
    api_items.py
    models.py
    routing.py
    validate.py
```

提前在模块目录下创建好 **templates/my_module/drawing-prompt.html** 和 **templates/my_module/drawing-prompt-edit.html** 两个文件。

## 分页查询

编辑 **templates/my_module/drawing-prompt.html** 文件, 我们将通过这个文件为 *读取绘图提示 (分页)* 接口开发一个分页查询页面, 前端代码如下：

```html
{% extends 'core/navigation.html' %}

{% block title %}
绘图提示
{% endblock %}

{% block main %}
<form>
    <label>
        <select id="category" placeholder="提示类别">
            <option value="" selected>全部类别</option>
            <option value="风格">风格</option>
            <option value="反向提示">反向提示</option>
            <option value="背景">背景</option>
        </select>
    </label>
</form>
<div id="details-content">
</div>
{% endblock %}

{% block operate_bottom %}
<suspended-right>
    <button id="newItem">创建</button>
</suspended-right>
{% endblock %}

{% block javascript %}
<script>
    var loadSwitch = false;
    var loadSkip = 0;
    var loadMark = true;
    var searchCategory = '{{ category }}';
    function loadData() {
        if (!loadMark) {
            return;
        }
        loadMark = false;
        let searchData = { 'limit': 20, 'skip': loadSkip };
        if (searchCategory) {
            searchData['category'] = searchCategory
        }
        utilAjax(
            type = 'GET',
            url = '/api/my_module/drawing_prompt/',
            data = searchData,
            data_format = 'query',
            check = {},
            success = function (data, textStatus) {
                if (data['items'].length == 20) {
                    loadSwitch = true;
                } else {
                    loadSwitch = false;
                }
                loadSkip += data['items'].length;
                data['items'].forEach(function (value, index) {
                    $('#details-content').append('<details class="itemDetails" onclick="event.preventDefault()" id="' + value.id + '"><summary>' + value.describe + ' <sup>' + value.prompt + '</sup></summary></details>');
                });
                $('.itemDetails').click(function () {
                    window.location.href = '/view/my_module/drawing_prompt/update/' + $(this).attr('id') + '/?category=' + $('#category').val();
                });
            },
            complete = function (request, textStatus) {
                loadMark = true;
            },
            success_reminder = false,
            not_close = false,
        );
    }
    function searchChange() {
        loadSwitch = false;
        loadSkip = 0;
        loadMark = true;
        $('#details-content').empty();
        loadData();
    }
    $(document).ready(function () {
        $('#category').val('{{ category }}');
        loadData();
        $('#newItem').click(function () {
            window.location.href = '/view/my_module/drawing_prompt/create/?category=' + $('#category').val();
        });
        $('#category').change(function (value) {
            searchCategory = $('#category').val();
            searchChange();
        });
    });
    $(window).scroll(function () {
        if (loadSwitch) {
            var w_h = parseFloat($(window).height());
            var doc_h = $(document).height();
            totalheight = w_h + parseFloat($(window).scrollTop()) + 2;
            if (totalheight >= doc_h) {
                loadData();
            }
        }
    });
</script>
{% endblock %}
```

在模板的 `{% block main %}...{% endblock %}` 部分, 写了两个元素, 一个是 **form** 表单元素, 表单的里面有一个下拉选择框, 让用户可以根据提示词的类别来筛选数据；还有一个 `id="details-content"` 的 **div** 元素, 这个元素将用于动态加载从接口获取的每一条数据。

在模板的 `{% block operate_bottom %}...{% endblock %}` 部分, 用了框架中定义的 **suspended-right** 元素, 这个元素里的内容会悬浮显示在窗口的右下角区域, 然后在里面创建一个 `id="newItem"` 的 **button** 按钮元素, 这个按钮给用户提供了一个创建新数据的入口。

在模板的 `{% block javascript %}...{% endblock %}` 部分, 开头定义的三个变量 `loadSwitch` *(拖到到窗口底部时是否触发分页查询)* 、`loadSkip` *(分页查询时从第几条数据开始拉)* 和 `loadMark` *(控制分页请求同时只能发起一条)* 。 接下来是 `searchCategory` 参数, 这个是分页查询的筛选条件, 一般以 **searchXXX** 的规则命名, 其数据来源有两个, 一是模板加载时服务端给的值, 二是表单元素变更时动态设置的值, 并在 `loadData()` 函数中将值添加到 `searchData` 里一并发送给服务端, 最后是在 `data['items'].forEach` 和 `$('.itemDetails').click` 两个代码段中定义每条数据的显示效果和点击事件。

### 添加分页查询路由

编辑 **view_url.py** 文件, 添加一个路由函数 `page_my_module_drawing_prompt()` 用于返回 **my_module/drawing-prompt.html** 模板文件：

```python
from fastapi.responses import HTMLResponse
from core.dependencies import get_view_request
from fastapi import APIRouter, Depends
from apis.templating import templates
from ..validate import DrawingPromptObjIdParams

router = APIRouter(prefix='/my_module', )

......

@router.get(
    '/drawing_prompt/',
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def page_my_module_drawing_prompt(
        category: str = '',
        request: dict = Depends(get_view_request),
):
    return templates.TemplateResponse(
        'my_module/drawing-prompt.html',
        {
            'category': category,
            **request
        },
    )
```

上面为 **my_module/drawing-prompt.html** 这个分页查询模版添加了一个路由 `page_my_module_drawing_prompt()` 函数, 并接收 **url** 中的 `category` 参数, 然后传到模版内, 替换模版中 `{{ category }}` 的内容。如果还有其他筛选参数, 应该按同样的方式传到前端模版中。

## 增删改操作

编辑 **templates/my_module/drawing-prompt-edit.html** 文件, 我们将通过这个文件为 *创建绘图提示*、*删除绘图提示*、*更新绘图提示* 和 *读取绘图提示* 接口开发一个增删改操作页面, 前端代码如下：

```html
{% extends 'core/navigation.html' %}

{% block title %}
{% if id %}
更新绘图提示
{% else %}
创建绘图提示
{% endif %}
{% endblock %}

{% block operate_left %}
<a href="/view/my_module/drawing_prompt/?category={{ category }}">
    <img src="/static/bases/material-icons/arrow_back_ios_new_fill.svg" />
</a>
{% endblock %}

{% block operate_right_top %}
{% if id %}
<a id="updateAndCreateItem" role="button" href="javascript:void(0);">更新</a>
{% else %}
<a id="updateAndCreateItem" role="button" href="javascript:void(0);">创建</a>
{% endif %}
{% endblock %}

{% block main %}
<form id="form-content">
    <label>
        提示类别
        <select id="category" placeholder="提示类别">
            <option value="风格">风格</option>
            <option value="反向提示">反向提示</option>
            <option value="背景">背景</option>
        </select>
    </label>
    <div class="grid">
        <label>
            提示
            <input type="text" id="prompt" placeholder="提示" required>
        </label>
        <label>
            描述
            <input type="text" id="describe" placeholder="描述" required>
        </label>
    </div>
</form>
{% endblock %}

{% block operate_bottom %}
{% if id %}
<suspended-right>
    <button id="deleteItem" class="contrast">删除</button>
</suspended-right>
{% endif %}
{% endblock %}

{% block javascript %}
<script>
    //{% if id %}
    $(document).ready(function () {
        utilAjax(
            type = 'GET',
            url = '/api/my_module/drawing_prompt/{{ id }}/',
            data = {},
            data_format = 'query',
            check = {},
            success = function (data, textStatus) {
                $('#category').val(data.category);
                $('#prompt').val(data.prompt);
                $('#describe').val(data.describe);
            },
            complete = function (request, textStatus) { },
            success_reminder = false,
            not_close = false,
        );
        $('#updateAndCreateItem').click(function () {
            utilAjax(
                type = 'PUT',
                url = '/api/my_module/drawing_prompt/{{ id }}/',
                data = {
                    'category': $('#category').val(),
                    'prompt': $('#prompt').val(),
                    'describe': $('#describe').val(),
                },
                data_format = 'json',
                check = {
                    'prompt': [/^[^\s]+(\s+[^\s]+)*$/, '提示不能为空'],
                    'describe': [/^[^\s]+(\s+[^\s]+)*$/, '描述不能为空'],
                },
                success = function (data, textStatus) {
                    $('#category').val(data.category);
                    $('#prompt').val(data.prompt);
                    $('#describe').val(data.describe);
                },
                complete = function (request, textStatus) { },
                success_reminder = true,
                not_close = false,
            );
        });
        $('#deleteItem').click(function () {
            swal({
                title: '你正在删除绘图提示',
                icon: 'warning',
                buttons: ['取消', '确认删除'],
                dangerMode: true,
            }).then((willDelete) => {
                if (willDelete) {
                    utilAjax(
                        type = 'DELETE',
                        url = '/api/my_module/drawing_prompt/{{ id }}/',
                        data = {},
                        data_format = 'json',
                        check = {},
                        success = function (data, textStatus) {
                            window.location.href = '/view/my_module/drawing_prompt/?category={{ category }}';
                        },
                        complete = function (request, textStatus) { },
                        success_reminder = false,
                        not_close = false,
                    );
                }
            });
        });
    });
    //{% else %}
    $(document).ready(function () {
        $('#updateAndCreateItem').click(function () {
            utilAjax(
                type = 'POST',
                url = '/api/my_module/drawing_prompt/',
                data = {
                    'category': $('#category').val(),
                    'prompt': $('#prompt').val(),
                    'describe': $('#describe').val(),
                },
                data_format = 'json',
                check = {
                    'prompt': [/^[^\s]+(\s+[^\s]+)*$/, '提示不能为空'],
                    'describe': [/^[^\s]+(\s+[^\s]+)*$/, '描述不能为空'],
                },
                success = function (data, textStatus) {
                    window.location.href = '/view/my_module/drawing_prompt/update/' + data._id + '/?category={{ category }}';
                },
                complete = function (request, textStatus) { },
                success_reminder = false,
                not_close = false,
            );
        });
    });
    //{% endif %}
</script>
{% endblock %}
```

在模板的 `{% block title %}...{% endblock %}` 部分, 根据服务端是否将 `id` 传输给了模版, 来显示不同的页面标题。

在模板的 `{% block operate_left %}...{% endblock %}` 部分, 这是页面左上角区域, 实现了一个返回图标按钮, 用于返回到上一级页面, 而且返回的链接中包含了上级页面需要请求参数, 这样可以同时兼顾用户体验和数据一致性。

在模板的 `{% block operate_right_top %}...{% endblock %}` 部分, 这是页面右上角区域, 根据服务端是否将 `id` 传输给了模版, 控制显示 *更新* 还是 *创建* 按钮, 就当前的页面来说, 两个按钮只是名称不同, 都是 `id="updateAndCreateItem"` 的元素。

在模板的 `{% block main %}...{% endblock %}` 部分, 主要是个 **form** 表单元素, 表单的里面有一个下拉选择框, 让用户选择提示词的类别, 还有两个文本输入框, 让用户输入提示及其描述信息, 注意 `id` 属性的命名, 尽量与后端接口的参数名称一致, 这样代码会比较好维护。

在模板的 `{% block operate_bottom %}...{% endblock %}` 部分, 这是悬浮显示在窗口的右下角区域, 先判断服务端是否将 `id` 传输给了模版, 只有 `id` 存在时才需要在里面创建一个 `id="deleteItem"` 的 **button** 按钮元素, 这个按钮给用户提供了删除数据的功能入口。

在模板的 `{% block javascript %}...{% endblock %}` 部分, 这里同样是根据服务端是否将 `id` 传输给了模版。当有 `id` 时, 先通过 `utilAjax` 函数调用 *读取绘图提示* 接口加载页面需要显示的信息, 再实现 `id="updateAndCreateItem"` 的 *更新* 按钮点击事件 (调用 *更新绘图提示* 接口), 再实现 `id="deleteItem"` 的 *删除* 按钮点击事件 (调用 *删除绘图提示* 接口); 当没有 `id` 时, 则只需要实现 `id="updateAndCreateItem"` 的 *创建* 按钮点击事件 (调用 *创建绘图提示* 接口)。

### 添加增删改操作路由

编辑 **view_url.py** 文件, 添加两个路由函数 `page_my_module_drawing_prompt_create()` 和 `page_my_module_drawing_prompt_update()` 用于返回 **my_module/drawing-prompt-edit.html** 模板文件的创建和更新部分：

```python
from fastapi.responses import HTMLResponse
from core.dependencies import get_view_request
from fastapi import APIRouter, Depends
from apis.templating import templates
from ..validate import DrawingPromptObjIdParams

router = APIRouter(prefix='/my_module', )

......

@router.get(
    '/drawing_prompt/create/',
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def page_my_module_drawing_prompt_create(
        category: str = '',
        request: dict = Depends(get_view_request),
):
    return templates.TemplateResponse(
        'my_module/drawing-prompt-edit.html',
        {
            'category': category,
            **request
        },
    )

@router.get(
    '/drawing_prompt/update/{id}/',
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def page_my_module_drawing_prompt_update(
        id: DrawingPromptObjIdParams,
        category: str = '',
        request: dict = Depends(get_view_request),
):
    return templates.TemplateResponse(
        'my_module/drawing-prompt-edit.html',
        {
            'id': str(id),
            'category': category,
            **request
        },
    )
```

上面为 **my_module/drawing-prompt-edit.html** 这个增删改操作模版添加了两个路由 `page_my_module_drawing_prompt_create()` 函数和 `page_my_module_drawing_prompt_update()` 函数。为了与分页查询模版保持一致, 这两个函数同样接收 **url** 中的 `category` 参数, 替换模版中 `{{ category }}` 的内容。另外一个路由 `page_my_module_drawing_prompt_update()` 函数因为是数据更新页面, 所以需要接收 **url** 中的 `id` 参数, 替换模版中 `{{ id }}` 项, 这就和前面模板代码中的 `{% if id %}...{% else %}...{% endif %}` 逻辑片段匹配上了。

## 导航和权限

编辑 **view_navigation.py** 文件, 将分页查询页面添加到导航栏的菜单项中, 并设置分页查询页面的菜单项显示条件, 即用户必须的权限列表：

```python
view_navigation_bar = [
    {
        'path': '/view/my_module/items/',
        'permission': [],
        'text': '第一个页面',
        'weight': 1,
    },
    {
        'path': '/view/my_module/drawing_prompt/',
        'permission': [
            'create_drawing_prompt',
            'delete_drawing_prompt',
            'update_drawing_prompt',
            'read_drawing_prompt',
            'read_drawing_prompt_page',
        ],
        'text': '绘图提示',
        'weight': 1,
    },
]
```

上面的配置控制了用户必须同时拥有 *读取绘图提示 (分页)*、*创建绘图提示*、*删除绘图提示*、*更新绘图提示* 和 *读取绘图提示* 接口的权限, 才会为用户显示 **绘图提示** 这个菜单项, 同时设置点击后打开 `/view/my_module/drawing_prompt/` 路径的页面。
