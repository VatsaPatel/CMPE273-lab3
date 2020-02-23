from ariadne import QueryType, graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, MutationType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify

id = 1001
c_id = 112200
students = {}
classes = {}

type_defs = load_schema_from_path('schema.graphql')
query = QueryType()
mutation = MutationType()


@query.field("hello")
def resolve_hello(_, info):
    request = info.context
    user_agent = request.headers.get("User-Agent", "Guest")
    return "Hello, %s!" % user_agent

@mutation.field("insertStudent")
def insertStudent(_, info, name):
    global id
    id += 1
    students[id] = name
    print(students)
    return {'id': id, 'name': name}

@query.field("viewStudent")
def viewStudent(_, info, id):
    return {'id': id, 'name': students.get(int(id))}

@mutation.field("createClass")
def createClass(_, info, name):
    global c_id
    c_id += 1
    classes[c_id] = { 'name': name, 'students': [] }
    return {'id': c_id, 'name': name, 'students': []}

@query.field("viewClass")
def viewClass(_, info, id):
    t=classes.get(int(id))
    return {'id': id, 'name': t['name'], 'students': t['students']}

@mutation.field("addStudent")
def addStudent(_, info, id, classId):
    s_name = students.get(id)
    classes[int(classId)]['students'].append( {'id' : id, 'name': s_name} )
    c_metadata = classes.get(int(classId))
    return {'id': classId, 'name': c_metadata['name'], 'students': c_metadata['students']}

schema = make_executable_schema(type_defs, [query, mutation])

app = Flask(__name__)


@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True)
