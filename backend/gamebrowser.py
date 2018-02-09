from socket import gethostname
from flask_graphql import GraphQLView
import website.config as config
from website.app import create_app
from website.schema import schema

# Create db connection depending on host
hostname = gethostname()
if hostname == 'helsinki':
    config.Config.SQLALCHEMY_DATABASE_URI = 'postgresql://kathrin:password@localhost:5433/gamebrowser'
if hostname == 'pori':
    config.Config.SQLALCHEMY_DATABASE_URI = 'postgresql://kathrin@localhost/gamebrowser'

app = create_app(config.DevelopmentConfig)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

# Optional, for adding batch query support (used in Apollo-Client)
# app.add_url_rule('/graphql/batch', view_func=GraphQLView.as_view('graphql', schema=schema, batch=True))

@app.route("/")
def hello():
    return "Hello !"

if __name__ == "__main__":
    app.run()
