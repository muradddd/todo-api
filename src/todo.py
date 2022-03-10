from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import Todo, db
from flasgger import swag_from

todos = Blueprint("todos", __name__, url_prefix="/api/v1/todos")


@todos.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_todos():
    current_user = get_jwt_identity()

    if request.method == 'POST':

        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                'error': 'Enter a valid url'
            }), HTTP_400_BAD_REQUEST

        if Todo.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL already exists'
            }), HTTP_409_CONFLICT

        todo = Todo(url=url, body=body, user_id=current_user)
        db.session.add(todo)
        db.session.commit()

        return jsonify({
            'id': todo.id,
            'url': todo.url,
            'short_url': todo.short_url,
            'visit': todo.visits,
            'body': todo.body,
            'created_at': todo.created_at,
            'updated_at': todo.updated_at,
        }), HTTP_201_CREATED

    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        todos = Todo.query.filter_by(
            user_id=current_user).paginate(page=page, per_page=per_page)

        data = []

        for todo in todos.items:
            data.append({
                'id': todo.id,
                'url': todo.url,
                'short_url': todo.short_url,
                'visit': todo.visits,
                'body': todo.body,
                'created_at': todo.created_at,
                'updated_at': todo.updated_at,
            })

        meta = {
            "page": todos.page,
            'pages': todos.pages,
            'total_count': todos.total,
            'prev_page': todos.prev_num,
            'next_page': todos.next_num,
            'has_next': todos.has_next,
            'has_prev': todos.has_prev,

        }

        return jsonify({'data': data, "meta": meta}), HTTP_200_OK


@todos.get("/<int:id>")
@jwt_required()
def get_todo(id):
    current_user = get_jwt_identity()

    todo = Todo.query.filter_by(user_id=current_user, id=id).first()

    if not todo:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify({
        'id': todo.id,
        'url': todo.url,
        'short_url': todo.short_url,
        'visit': todo.visits,
        'body': todo.body,
        'created_at': todo.created_at,
        'updated_at': todo.updated_at,
    }), HTTP_200_OK


@todos.delete("/<int:id>")
@jwt_required()
def delete_todo(id):
    current_user = get_jwt_identity()

    todo = Todo.query.filter_by(user_id=current_user, id=id).first()

    if not todo:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    db.session.delete(todo)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


@todos.put('/<int:id>')
@todos.patch('/<int:id>')
@jwt_required()
def edittodo(id):
    current_user = get_jwt_identity()

    todo = Todo.query.filter_by(user_id=current_user, id=id).first()

    if not todo:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({
            'error': 'Enter a valid url'
        }), HTTP_400_BAD_REQUEST

    todo.url = url
    todo.body = body

    db.session.commit()

    return jsonify({
        'id': todo.id,
        'url': todo.url,
        'short_url': todo.short_url,
        'visit': todo.visits,
        'body': todo.body,
        'created_at': todo.created_at,
        'updated_at': todo.updated_at,
    }), HTTP_200_OK


@todos.get("/stats")
@jwt_required()
@swag_from("./docs/todos/stats.yaml")
def get_stats():
    current_user = get_jwt_identity()

    data = []

    items = Todo.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link = {
            'visits': item.visits,
            'url': item.url,
            'id': item.id,
            'short_url': item.short_url,
        }

        data.append(new_link)

    return jsonify({'data': data}), HTTP_200_OK
