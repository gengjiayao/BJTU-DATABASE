const btn = document.getElementById("send-code-btn");
const _phone = document.getElementById("phone");

// 获取 csrf_token cookie 的值
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function generateCode() {
    const chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    let code = '';
    for (let i = 0; i < 6; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
}

btn.addEventListener('mouseover', function () {
    if (!btn.disabled) {
        btn.style.backgroundColor = "#3e8e41";
    }
});
btn.addEventListener('mouseout', function () {
    if (!btn.disabled) {
        btn.style.backgroundColor = "#4CAF50";
    }
});
btn.addEventListener('click', function () {
    if (!_phone.value) {
        alert("手机号码不能为空");
        return;
    }
    const xhr = new XMLHttpRequest();
    const csrfToken = getCookie('csrftoken'); // 获取 CSRF 令牌
    xhr.open("POST", "/send_code/", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-CSRFToken", csrfToken); // 将 CSRF 令牌添加到请求头中
    let Code = generateCode();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                console.log(xhr.responseText);
                console.log("6位验证码：" + Code);
            } else {
                console.error(xhr.statusText);
            }
        }
    }
    let data = {
        Code: Code,
    };
    xhr.send(JSON.stringify(data));

    let time = 59;
    btn.disabled = true;
    btn.style.backgroundColor = "#808080";
    btn.style.cursor = "default";
    const timer = setInterval(function () {
        if (time === 0) {
            clearInterval(timer);
            btn.disabled = false;
            btn.innerHTML = '获取验证码';
            btn.style.backgroundColor = "#4CAF50";
        } else {
            btn.innerHTML = `${time}s重新发送`;
            time--;
        }
    }, 1000);
});