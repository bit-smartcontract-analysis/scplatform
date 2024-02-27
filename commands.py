from models.post import BoardModel, PostModel
from models.auth import UserModel, RoleModel, Permission
from exts import db
import random
from flask_avatars import Identicon
from hashlib import md5
import os

def init_boards():
    board_names = ['区块链', '智能合约', '长安链']
    for index, board_name in enumerate(board_names):
        board = BoardModel(name=board_name, priority=len(board_names)-index)
        db.session.add(board)
    db.session.commit()
    print("板块初始化成功！")


def init_developer():
    role = RoleModel.query.filter_by(name="开发者").first()
    user = UserModel(username="wei", email="wwwweizhiyuan@163.com", password="000000", is_staff=True, role=role)
    db.session.add(user)
    db.session.commit()
    print("开发者角色下的用户创建成功")
    
    
def init_roles():
    # 运营
    operator_role = RoleModel(name="运营", desc="负责管理帖子和评论",
                         permissions=Permission.POST | Permission.COMMENT | Permission.USER)
    # 管理员
    admin_role = RoleModel(name="管理员", desc="负责整个网站的管理",
                      permissions=Permission.POST | Permission.COMMENT | Permission.USER | Permission.STAFF)
    # 开发者（权限是最大的）
    developer_role = RoleModel(name="开发者", desc="负责网站的开发", permissions=Permission.ALL_PERMISSION)

    db.session.add_all([operator_role, admin_role, developer_role])
    db.session.commit()
    print("角色添加成功！")


def bind_roles():
    user1 = UserModel.query.filter_by(email="wwwweizhiyuan@163.com").first()
    user2 = UserModel.query.filter_by(email="btweifar@126.com").first()
    user3 = UserModel.query.filter_by(email="475207222@qq.com").first()

    role1 = RoleModel.query.filter_by(name="开发者").first()
    role2 = RoleModel.query.filter_by(name="运营").first()
    role3 = RoleModel.query.filter_by(name="管理员").first()

    user1.role = role1
    user2.role = role2
    user3.role = role3

    db.session.commit()
    print("用户和角色绑定成功！")


def create_test_posts():
    boards = list(BoardModel.query.all())
    boards_count = len(boards)
    for x in range(99):
        title = "我是标题%d"%x
        content = "我是内容%d"%x
        author = UserModel.query.first()
        index = random.randint(0, boards_count-1)
        board = boards[index]
        post_model = PostModel(title=title, content=content, author=author, board=board)
        db.session.add(post_model)
    db.session.commit()
    print("测试帖子添加成功")


def create_test_users():
    # user1
    email1 = "111111@gmail.com"
    username1 = "Zhou"
    password1 = "111111"
    identicon = Identicon()
    filenames1 = identicon.generate(text=md5(email1.encode("utf-8")).hexdigest())
    avatar1 = filenames1[2]
    user1 = UserModel(email=email1, username=username1, password=password1, avatar=avatar1)
    db.session.add(user1)

    # user2
    email2 = "111112@gmail.com"
    username2 = "Li"
    password2 = "111111"
    filenames2 = identicon.generate(text=md5(email2.encode("utf-8")).hexdigest())
    avatar2 = filenames2[2]
    user2 = UserModel(email=email2, username=username2, password=password2, avatar=avatar2)
    db.session.add(user2)

    db.session.commit()
    print("测试人员添加成功")
