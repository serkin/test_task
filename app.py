from functools import wraps

from flask import Flask
from flask_restful import Api, Resource, fields, marshal_with, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import HTTPException, Forbidden
from werkzeug.security import check_password_hash

app = Flask(__name__)


class ResourceAlreadyExistsError(HTTPException):
    pass


class ElementNotFoundError(HTTPException):
    pass


errors = {
    'ResourceAlreadyExistsError': {
        'message': "Resource already exists.",
        'status': 409,
    },
    'ElementNotFoundError': {
        'message': "Resource not found.",
        'status': 404,
    }
}

api = Api(app, errors=errors)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mysecretpassword@localhost:5432/postgres_5302'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String)
    password = db.Column(db.String)
    token = db.Column(db.String)

    @staticmethod
    def is_user_authorized(token):
        return bool(User.query.filter_by(token=token).first())


class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    regions = db.relationship('Region', backref='countries', cascade="all,delete", lazy=True)


class Region(db.Model):
    __tablename__ = 'regions'
    __table_args__ = (db.UniqueConstraint('name', 'country_id'),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id', ondelete="CASCADE"), index=True, nullable=False)


_fields = {
    'id': fields.Integer,
    'name': fields.String

}


def _non_empty_string(s):
    if not s:
        raise ValueError("Must not be empty string")
    return s


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('token', type=_non_empty_string, required=True, help='token required')
        _args = parser.parse_args()

        if User.is_user_authorized(_args['token']):
            return func(*args, **kwargs)

        abort(401)

    return wrapper


class CountryListController(Resource):
    method_decorators = {'post': [authenticate]}

    @marshal_with(_fields)
    def get(self):
        return Country.query.all()

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=_non_empty_string, required=True, help='name required')
        args = parser.parse_args()
        record = Country(name=args['name'])
        try:
            db.session.add(record)
            db.session.commit()
            return {"name": args['name']}
        except IntegrityError:
            raise ResourceAlreadyExistsError


class CountryController(Resource):
    method_decorators = {'put': [authenticate], 'delete': [authenticate]}

    @marshal_with(_fields)
    def get(self, country_id):

        try:
            return Country.query.filter_by(id=country_id).one()
        except NoResultFound:
            raise ElementNotFoundError

    @marshal_with(_fields)
    def put(self, country_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=_non_empty_string, required=True, help='name required')
        args = parser.parse_args()
        record = Country.query.filter_by(id=country_id).first()
        if not record:
            raise ElementNotFoundError
        record.name = args['name']
        try:
            db.session.commit()
            return record, 201
        except IntegrityError:
            raise ResourceAlreadyExistsError()

    def delete(self, country_id):
        Country.query.filter_by(id=country_id).delete()
        db.session.commit()
        return '{}', 204


class RegionListController(Resource):
    method_decorators = {'post': [authenticate]}

    @marshal_with(_fields)
    def get(self, country_id):
        return Region.query.filter_by(country_id=country_id).all()

    def post(self, country_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=_non_empty_string, required=True, help='name required')
        args = parser.parse_args()
        record = Region(name=args['name'], country_id=country_id)
        try:
            db.session.add(record)
            db.session.commit()
            return {"name": args['name']}
        except IntegrityError:
            raise ResourceAlreadyExistsError()


class RegionController(Resource):
    method_decorators = {'put': [authenticate], 'delete': [authenticate]}

    @marshal_with(_fields)
    def get(self, country_id, region_id):
        try:
            return Region.query.filter_by(country_id=country_id, id=region_id).one()
        except NoResultFound:
            raise ElementNotFoundError

    def post(self, country_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=_non_empty_string, required=True, help='name required')
        args = parser.parse_args()

        record = Region(name=args['name'], country_id=country_id)
        try:
            db.session.add(record)
            db.session.commit()
            return {"name": args['name']}

        except IntegrityError:
            raise ResourceAlreadyExistsError

    @marshal_with(_fields)
    def put(self, country_id, region_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=_non_empty_string, required=True, help='name required')
        args = parser.parse_args()
        record = Region.query.filter_by(id=region_id, country_id=country_id).first()
        if not record:
            raise ElementNotFoundError()
        record.name = args['name']
        try:
            db.session.commit()
            return record, 201
        except IntegrityError:
            raise ResourceAlreadyExistsError()

    def delete(self, country_id, region_id):
        Region.query.filter_by(id=country_id).delete()
        db.session.commit()
        return '{}', 204


"""
Controller gets user token
"""


class UserAuth(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, required=True, help='login required')
        parser.add_argument('password', type=str, required=True, help='password required')
        args = parser.parse_args()
        user = User.query.filter_by(login=args["login"]).first()
        if user and check_password_hash(user.password, args["password"]):
            return {"token": user.token}
        else:
            raise Forbidden


api.add_resource(CountryListController, '/countries')
api.add_resource(CountryController, '/countries/<country_id>')
api.add_resource(RegionListController, '/countries/<country_id>/regions')
api.add_resource(RegionController, '/countries/<country_id>/regions/<region_id>')

api.add_resource(UserAuth, '/auth')


def seed():
    db.session.add(Country(name="Russian Federation"))
    db.session.add(Country(name="Germany"))

    db.session.add(Region(name="Moscow", country_id=1))
    db.session.add(Region(name="Korolev", country_id=1))
    db.session.add(Region(name="Berlin", country_id=2))

    db.session.add(User(login="university",
                        password="pbkdf2:sha256:150000$75xC98vG$fc51835c7707c340a1524078960a5a8b58d87338b84e0076e7fa95534fe09bd8",
                        token="wc45vcws4rc5sc67657t9ynt4v545"))

    db.session.commit()


def recreate_db():
    db.drop_all()
    db.create_all()
    seed()


if __name__ == '__main__':
    recreate_db()

    app.run(host="0.0.0.0")
