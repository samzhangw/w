const express = require('express');
const bodyParser = require('body-parser');
const bcrypt = require('bcrypt');

const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({ extended: true }));

const users = {};

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

app.post('/signup', async (req, res) => {
    const { name, password } = req.body;
    if (users[name]) {
        return res.json({ status: 'error', message: '使用者已存在，請嘗試其他名稱。' });
    }
    const hashedPassword = await bcrypt.hash(password, 10);
    users[name] = hashedPassword;
    res.json({ status: 'success', message: `使用者 ${name} 註冊成功！請登入。` });
});

app.post('/signin', async (req, res) => {
    const { name, password } = req.body;
    const hashedPassword = users[name];
    if (!hashedPassword) {
        return res.render('index.html', { login_alert: '該使用者尚未註冊。' });
    }
    const match = await bcrypt.compare(password, hashedPassword);
    if (match) {
        return res.redirect(`/success/${name}`);
    } else {
        return res.render('index.html', { login_alert: '無效的名稱或密碼。請重試。' });
    }
});

app.listen(port, () => {
    console.log(`App listening at http://localhost:${port}`);
});
