from models import *
import db
import os

if __name__ == "__main__":
    path = SQLITE3_NAME
    if not os.path.isfile(path):
        # テーブル作成
        Base.metadata.create_all(db.engine)
    
    # サンプルユーザ(admin)作成
    admin = User(
        username='admin',
        password='fastapi',
        mail='hoge@example.com',
    )
    # 追加
    db.session.add(admin)
    # データベースに反映
    db.session.commit()

    # サンプルタスク作成
    task = Task(
        user_id=admin.id,
        content='〇〇の締め切り',
        deadline=datetime(2019, 12, 25, 12, 00, 00),
    )
    print(task)
    # 追加
    db.session.add(task)
    # データベースに反映
    db.session.commit()

    # セッションを閉じる
    db.session.close()
    