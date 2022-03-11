from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import Todo, db
from flasgger import swag_from

todos = Blueprint("todos", __name__, url_prefix="/api/v1/todos")


@todos.get("/<int:id>")
@jwt_required()
def get_todo(id):
    current_user = get_jwt_identity()

    todo = Todo.query.filter_by(user_id=current_user, id=id).first()

    if not todo:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify({
        'id': todo.id,
        'title': todo.title,
        'is_complete': todo.is_complete,
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
@jwt_required()
def edit_todo(id):
    current_user = get_jwt_identity()

    todo = Todo.query.filter_by(user_id=current_user, id=id).first()

    if not todo:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    title = request.get_json().get('title', '')
    is_complete = request.get_json().get('is_complete', '')

    todo.title = title
    todo.is_complete = is_complete

    db.session.commit()

    return jsonify({
        'id': todo.id,
        'title': todo.title,
        'is_complete': todo.is_complete,
        'created_at': todo.created_at,
        'updated_at': todo.updated_at,
    }), HTTP_200_OK


@todos.get("/")
@jwt_required()
@swag_from("./docs/todos.yaml")
def todo_list():
    current_user = get_jwt_identity()

    data = []

    todos = Todo.query.filter_by(user_id=current_user).all()

    for todo in todos:
        new_todo = {
            'id': todo.id,
            'title': todo.title,
            'is_complete': todo.is_complete,
            'updated_at': todo.updated_at,
        }

        data.append(new_todo)

    return jsonify({'data': data}), HTTP_200_OK


@todos.post("/")
@jwt_required()
def create_todo():
    current_user = get_jwt_identity()
    
    title = request.get_json().get('title', '')

    todo = Todo(title=title, user_id=current_user)
    todo.save()
    
    data = {
        'id': todo.id,
        'title': todo.title,
        'is_complete': todo.is_complete,
        'created_at': todo.created_at,
        'updated_at': todo.updated_at
    }

    return jsonify({'data': data}), HTTP_200_OK