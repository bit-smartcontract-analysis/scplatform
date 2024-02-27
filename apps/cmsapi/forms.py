from apps.front.forms import BaseForm
from wtforms.fields import FileField, StringField, IntegerField
from flask_wtf.file import FileAllowed, FileSize
from wtforms.validators import InputRequired


class UploadImageForm(BaseForm):
    image = FileField(validators=[FileAllowed(['jpg', 'jpeg', 'png'], message="图片格式不符合要求！"),
                                  FileSize(max_size=1024 * 1024 * 5, message="图片最大不能超过5M")])


class AddBannerForm(BaseForm):
    name = StringField(validators=[InputRequired(message='请输入轮播图名称！')])
    image_url = StringField(validators=[InputRequired(message='请输入轮播图图片链接！')])
    link_url = StringField(validators=[InputRequired(message='请输入轮播图跳转链接！')])
    priority = IntegerField(validators=[InputRequired(message='请输入轮播图优先级！')])


class EditBannerForm(AddBannerForm):
    id = IntegerField(validators=[InputRequired(message="请输入轮播图的id!")])
