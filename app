<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>用戶管理系統</title>
</head>
<body>
    <h1>用戶管理系統</h1>
    <div id="signup">
        <h2>註冊</h2>
        <form id="signup-form" action="/signup" method="POST">
            <label for="signup-name">使用者名稱:</label>
            <input type="text" id="signup-name" name="name" required><br>
            <label for="signup-password">密碼:</label>
            <input type="password" id="signup-password" name="password" required><br>
            <button type="submit">註冊</button>
        </form>
    </div>
    
    <div id="signin">
        <h2>登入</h2>
        <form id="signin-form" action="/signin" method="POST">
            <label for="signin-name">使用者名稱:</label>
            <input type="text" id="signin-name" name="name" required><br>
            <label for="signin-password">密碼:</label>
            <input type="password" id="signin-password" name="password" required><br>
            <button type="submit">登入</button>
        </form>
        {% if login_alert %}
        <p>{{ login_alert }}</p>
        {% endif %}
    </div>

    <div id="changepassword">
        <h2>修改密碼</h2>
        <form id="changepassword-form" action="/changepassword" method="POST">
            <label for="changepassword-name">使用者名稱:</label>
            <input type="text" id="changepassword-name" name="name" required><br>
            <label for="changepassword-old">舊密碼:</label>
            <input type="password" id="changepassword-old" name="old_password" required><br>
            <label for="changepassword-new">新密碼:</label>
            <input type="password" id="changepassword-new" name="new_password" required><br>
            <button type="submit">修改密碼</button>
        </form>
    </div>

    <script>
        // 可以在此添加JavaScript代碼
    </script>
</body>
</html>
