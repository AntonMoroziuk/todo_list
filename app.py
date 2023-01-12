import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from todo_list_pb2 import ListItem as ProtobufItem
from todo_list_pb2 import ToDoList

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1024), nullable=False)
    done = db.Column(db.Boolean, default=False)


def item_to_proto(item, protobuf_item):
    protobuf_item.id = item.id
    protobuf_item.done = item.done
    protobuf_item.text = item.text


@app.route("/", methods=["GET"])
def get_items():
    use_protobuf = request.args.get("use_protobuf", False)
    items = Item.query.all()

    if use_protobuf:
        todo_list = ToDoList()
        for item in items:
            protobuf_item = todo_list.items.add()
            item_to_proto(item, protobuf_item)
        return todo_list.SerializeToString()
    else:
        return [{"id": item.id, "done": item.done, "text": item.text} for item in items]


@app.route("/<item_id>", methods=["GET"])
def get_item(item_id):
    use_protobuf = request.args.get("use_protobuf", False)
    item = Item.query.filter_by(id=item_id).first_or_404()

    if use_protobuf:
        protobuf_item = ProtobufItem()
        item_to_proto(item, protobuf_item)
        return protobuf_item.SerializeToString()
    else:
        return {"id": item.id, "done": item.done, "text": item.text}


@app.route("/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.filter_by(id=item_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return "", 204


@app.route("/", methods=["POST"])
def add_item():
    use_protobuf = request.args.get("use_protobuf", False)

    if use_protobuf:
        protobuf_item = ProtobufItem()
        protobuf_item.ParseFromString(request.data)
        item = Item(text=protobuf_item.text)

        db.session.add(item)
        db.session.commit()
        protobuf_item.id = item.id
        return protobuf_item.SerializeToString(), 201
    else:
        data = request.json
        if "text" not in data:
            return "You should provide a text for todo list item", 400
        item = Item(text=data["text"])

        db.session.add(item)
        db.session.commit()
        return {"id": item.id, "done": item.done, "text": item.text}, 201


@app.route("/<item_id>", methods=["PUT"])
def update_item(item_id):
    use_protobuf = request.args.get("use_protobuf", False)
    item = Item.query.filter_by(id=item_id).first_or_404()

    if use_protobuf:
        protobuf_item = ProtobufItem()
        protobuf_item.ParseFromString(request.data)
        item.text = protobuf_item.text
        item.done = protobuf_item.done

        db.session.commit()
        return protobuf_item.SerializeToString()
    else:
        data = request.json
        if "text" not in data:
            return "You should provide a text to update todo list item", 400

        item.text = data["text"]
        item.done = data.get("done", item.done)

        db.session.commit()
        return {"id": item.id, "done": item.done, "text": item.text}, 200


if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run()
