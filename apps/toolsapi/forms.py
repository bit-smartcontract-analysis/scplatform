from wtforms import Form
from wtforms.validators import length
from wtforms.fields import FileField, StringField
from flask_wtf.file import FileAllowed, FileSize


class BaseForm(Form):
    @property
    def messages(self):
        message_list = []
        if self.errors:
            for errors in self.errors.values():
                message_list.extend(errors)
        return message_list


class ToolForm(BaseForm):
    tool = StringField(validators=[length(min=1, max=200)])
    method = StringField(validators=[length(min=1, max=200)])
    target = StringField(validators=[length(min=1)])
    platform = StringField(validators=[length(min=1, max=200)])
    arguments = StringField(validators=[length(min=0)])


class UploadContractForm(BaseForm):
    file = FileField(validators=[FileAllowed(['sol', 'wasm'], message="合约格式不符合要求！"),
                                     FileSize(max_size=1024 * 1024 * 1, message="合约最大不能超过1M")])
