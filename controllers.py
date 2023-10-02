import db
import hashlib
import re

from models import User, Task
from mycalendar import MyCalendar

from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

app = FastAPI(
    tilte='FastAPIでつくるtoDoアプリケーション',
    description='FastAPIチュートリアル：FastAPI(とstarlette)でシンプルなtoDoアプリを作りましょう．',
    version='0.9 beta'
)

templates = Jinja2Templates(directory="templates")
jinja_env = templates.env

def index(request: Request):
    return templates.TemplateResponse(
        'index.html',
        {'request': request}
    )

sequrity = HTTPBasic()

def admin(request: Request, credentials: HTTPBasicCredentials = Depends(sequrity)):
    # Basic認証で受け取った情報
    username = credentials.username
    password = hashlib.md5(credentials.password.encode()).hexdigest()

    # 今日の日付と来週の日付
    today = datetime.now()
    next_w = today + timedelta(days=7)

    # データベースからユーザ名が一致するデータを取得
    user = db.session.query(User).filter(User.username == username).first()
    db.session.close()

    # 該当ユーザがいない場合
    if user is None or user.password != password:
        error = 'ユーザ名かパスワードが間違っています'
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Basic"},
        )

    task = db.session.query(Task).filter(Task.user_id == user.id).all() if user is not None else []
    db.session.close()

    # カレンダーをHTML形式で取得
    cal = MyCalendar(
        username,
        {t.deadline.strftime('%Y%m%d'): t.done for t in task}
    )

    cal = cal.formatyear(today.year, 4)

    # 直近のタスクだけでいいので、リストを書き換える
    task = [t for t in task if today <= t.deadline <= next_w]
    links = [t.deadline.strftime('/todo/'+username+'/%Y/%m/%d') for t in task]

    # 特に問題がなければ管理者ページへ
    return templates.TemplateResponse(
        'admin.html',
        {'request': request,
         'user': user,
         'task': task,
         'links': links,
         'calender': cal}
    )

# 任意の4~20の英数字を示す正規表現
pattern = re.compile(r'\w{4,20}')
# 任意の6~20の英数字を示す正規表現
pattern_pw = re.compile(r'\w{6,20}')
# 任意のメールアドレスを示す正規表現
pattern_mail = re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')

async def register(request: Request):
    if request.method == 'GET':
        return templates.TemplateResponse(
            'register.html',
            {'request': request,
             'username': '',
             'error': []}
        )

    if request.method == 'POST':
        data = await request.form()
        username = data.get('username')
        password = data.get('password')
        password_tmp = data.get('password_tmp')
        mail = data.get('mail')

        # エラーを格納するリスト
        error = []

        # ユーザ名のバリデーション
        tmp_user = db.session.query(User).filter(User.username == username).first()

        # エラー処理
        if tmp_user is not None:
            error.append('同じユーザ名のユーザが存在します。')
        if password != password_tmp:
            error.append('入力したパスワードが一致しません。')
        if pattern.match(username) is None:
            error.append('ユーザ名は4~20文字の半角英数字にしてください。')
        if pattern_pw.match(password) is None:
            error.append('パスワードは6~20文字の半角英数字にしてください。')
        if pattern_mail.match(mail) is None:
            error.append('正しくメールアドレスを入力してください。')
        
        # エラーがあれば登録ページへ戻す
        if error:
            return templates.TemplateResponse(
                'register.html',
                {'request': request,
                 'username': username,
                 'error': error}
            )
        
        # エラーがなければ登録
        user = User(username, password, mail)
        db.session.add(user)
        db.session.commit()
        db.session.close()

        return templates.TemplateResponse(
            'complete.html',
            {'request': request,
             'username': username}
        )
    
def detail(request: Request, username, year, month, day):
    return templates.TemplateResponse(
        'detail.html',
        {'request': request,
         'username': username,
         'year': year,
         'month': month,
         'day': day}
    )