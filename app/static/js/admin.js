/* Copyright (c) 2026 新疆幻城网安科技有限责任公司
 * All rights reserved.
 * 官方网站：https://www.hcnsec.cn/
 */

// 本代码由新疆幻城网安公益大模型API中转站提供API支持
// 访问地址：https://api.iamhc.cn/

// 左侧菜单切换
document.addEventListener('DOMContentLoaded', function() {
    const menuToggles = document.querySelectorAll('.menu-toggle');
    
    menuToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const submenu = this.nextElementSibling;
            if (submenu && submenu.classList.contains('submenu')) {
                submenu.classList.toggle('show');
                this.classList.toggle('active');
            }
        });
    });
});

// AJAX工具函数
function ajaxPost(url, data, callback) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    callback(response);
                } catch(e) {
                    callback({code: 1, msg: '服务器响应错误'});
                }
            } else {
                callback({code: 1, msg: '请求失败'});
            }
        }
    };
    
    xhr.send(data);
}

// 提示消息
function showMessage(msg, type) {
    alert(msg);
}
