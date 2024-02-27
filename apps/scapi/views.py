from flask import (
    Blueprint,
    render_template,
    session,
    g,
    request,
    current_app
)

from flask_jwt_extended import jwt_required, get_jwt_identity
from models.auth import UserModel
from .forms import UploadContractForm
import os
from hashlib import md5
import time
from utils import restful


bp = Blueprint("scAnalysis", __name__, url_prefix="/scAnalysis")


@bp.before_request
def front_before_request():
    if 'user_id' in session:
        user_id = session.get("user_id")
        user = UserModel.query.get(user_id)
        setattr(g, "user", user)


@bp.context_processor
def front_context_processor():
    if hasattr(g, "user"):
        return {"user": g.user}
    else:
        return {}


@bp.get("/")
def index():
    return render_template("sc/scAnalysis.html")


@bp.post("/contracts/file/upload")
def upload_contracts_file():
    form = UploadContractForm(request.files)
    if form.validate():
        file = form.file.data
        filename = file.filename
        contract_path = os.path.join(current_app.config['CONTRACT_IMAGE_SAVE_PATH'], filename)
        file.save(contract_path)
        return restful.ok(data={"contract_url": filename})
    else:
        message = form.messages[0]
        print(message)
        return restful.params_error(message=message)


