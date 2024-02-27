from flask import Blueprint, request, current_app, g
import os
import time
from hashlib import md5
from utils import restful
from flask_jwt_extended import jwt_required, get_jwt_identity
from .forms import UploadImageForm, AddBannerForm, EditBannerForm
from models.auth import UserModel, Permission
from models.post import BannerModel, PostModel, CommentModel, BoardModel
from exts import db
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from .decorators import permission_required

bp = Blueprint("cmsapi", __name__, url_prefix="/cmsapi")


@bp.before_request
@jwt_required()
def cmsapi_before_request():
    if request.method == 'OPTIONS':
        return
    identity = get_jwt_identity()
    user = UserModel.query.filter_by(id=identity).first()
    if user:
        setattr(g, "user", user)


@bp.get("/")
@jwt_required()
def mytest():
    # Access the identity of the current user with get_jwt_identity
    identity = get_jwt_identity()
    return restful.ok(message="success!", data={"identity": identity})


@bp.post("/banner/image/upload")
@permission_required(Permission.BANNER)
def upload_banner_image():
    print(request.files)
    form = UploadImageForm(request.files)
    if form.validate():
        image = form.image.data
        # 不要使用用户上传上来的文件名，否则容易被黑客攻击
        filename = image.filename
        # xxx.png,xx.jpeg
        _, ext = os.path.splitext(filename)
        filename = md5((g.user.email + str(time.time())).encode("utf-8")).hexdigest() + ext
        image_path = os.path.join(current_app.config['BANNER_IMAGE_SAVE_PATH'], filename)
        image.save(image_path)
        return restful.ok(data={"image_url": filename})
    else:
        message = form.messages[0]
        return restful.params_error(message=message)


@bp.post("/banner/add")
@permission_required(Permission.BANNER)
def add_banner():
    form = AddBannerForm(request.form)
    if form.validate():
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        banner_model = BannerModel(name=name, image_url=image_url, link_url=link_url, priority=priority)
        db.session.add(banner_model)
        db.session.commit()
        return restful.ok(data=banner_model.to_dict())
    else:
        return restful.params_error(message=form.messages[0])


@bp.get("/banner/list")
@permission_required(Permission.BANNER)
def banner_list():
    banners = BannerModel.query.order_by(BannerModel.create_time.desc()).all()
    # BannerModel
    banner_dicts = [banner.to_dict() for banner in banners]
    return restful.ok(data=banner_dicts)


@bp.post("/banner/delete")
@permission_required(Permission.BANNER)
def delete_banner():
    banner_id = request.form.get("id")
    if not banner_id:
        return restful.params_error(message="没有传入id！")
    try:
        banner_model = BannerModel.query.get(banner_id)
    except Exception as e:
        return restful.params_error(message="此轮播图不存在！")
    db.session.delete(banner_model)
    db.session.commit()
    return restful.ok()


@bp.post("/banner/edit")
@permission_required(Permission.BANNER)
def edit_banner():
    form = EditBannerForm(request.form)
    if form.validate():
        banner_id = form.id.data
        try:
            banner_model = BannerModel.query.get(banner_id)
        except Exception as e:
            return restful.params_error(message="轮播图不存在！")
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data

        banner_model.name = name
        banner_model.image_url = image_url
        banner_model.link_url = link_url
        banner_model.priority = priority
        db.session.commit()
        return restful.ok(data=banner_model.to_dict())
    else:
        return restful.params_error(message=form.messages[0])


@bp.get("/post/list")
@permission_required(Permission.POST)
def post_list():
    page = request.args.get('page', default=1, type=int)
    per_page_count = current_app.config['PER_PAGE_COUNT']
    start = (page-1)*per_page_count
    end = start + per_page_count
    query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    total_count = query_obj.count()
    posts = query_obj.slice(start, end)
    # [PostMode(1), PostModel(2)]
    post_list = [post.to_dict() for post in posts]
    return restful.ok(data={
        'total_count': total_count,
        'post_list': post_list,
        'page': page
    })


@bp.post("/post/delete")
@permission_required(Permission.POST)
def delete_post():
    post_id = request.form.get("id")
    try:
        post_model = PostModel.query.get(post_id)
    except Exception as e:
        return restful.params_error(message="帖子不存在")
    db.session.delete(post_model)
    db.session.commit()
    return restful.ok()


@bp.get("/comment/list")
@permission_required(Permission.COMMENT)
def comment_list():
    comments = CommentModel.query.order_by(CommentModel.create_time.desc()).all()
    comment_list = []
    for comment in comments:
        comment_dict = comment.to_dict()
        comment_list.append(comment_dict)
    return restful.ok(data=comment_list)


@bp.post("/comment/delete")
@permission_required(Permission.COMMENT)
def delete_comment():
    comment_id = request.form.get("id")
    CommentModel.query.filter_by(id=comment_id).delete()
    return restful.ok()


@bp.get("/user/list")
@permission_required(Permission.USER)
def user_list():
    users = UserModel.query.order_by(UserModel.join_time.desc()).all()
    user_list = [user.to_dict() for user in users]
    return restful.ok(data=user_list)


@bp.post("/user/active")
@permission_required(Permission.USER)
def active_user():
    is_active = request.form.get('is_active', type=int)
    user_id = request.form.get("id")
    user = UserModel.query.get(user_id)
    user.is_active = bool(is_active)
    db.session.commit()
    return restful.ok(data=user.to_dict())


@bp.get("/board/post/count")
def board_post_count():
    board_post_count_list = db.session.query(BoardModel.name, func.count(BoardModel.name)).join(PostModel).group_by(BoardModel.name).all()
    board_names = []
    post_counts = []
    for bord_post_count in board_post_count_list:
        board_names.append(bord_post_count[0])
        post_counts.append(bord_post_count[1])
    return restful.ok(data={"board_names": board_names, "post_counts": post_counts})


@bp.get("/day7/post/count")
def day7_post_count():
    # MySQL数据库，用的是date_format函数
    # SQlite数据库，用的是strfformat函数
    now = datetime.now()
    # 一定要把时分秒减为0，不然只能获取7天前当前时间的帖子
    seven_day_ago = now - timedelta(days=6, hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    day7_post_count_list = db.session.query(func.date_format(PostModel.create_time, "%Y-%m-%d"), func.count(PostModel.id)).group_by(func.date_format(PostModel.create_time, "%Y-%m-%d")).filter(PostModel.create_time >= seven_day_ago).all()
    day7_post_count_dict = dict(day7_post_count_list)
    for x in range(7):
        date = seven_day_ago + timedelta(days=x)
        date_str = date.strftime("%Y-%m-%d")
        if date_str not in day7_post_count_dict:
            day7_post_count_dict[date_str] = 0
    dates = sorted(list(day7_post_count_dict.keys()))
    counts = []
    for date in dates:
        counts.append(day7_post_count_dict[date])
    # print({"dates": dates, "counts": counts})
    return restful.ok(data={"dates": dates, "counts": counts})


