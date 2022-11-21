# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()


class DirectionSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


api = Api(app)

movie_ns = api.namespace("movies")
direction_ns = api.namespace("directions")
genre_ns = api.namespace("genre")

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

direction_schema = DirectionSchema()
directions_schema = DirectionSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        movies_query = db.session.query(Movie)
        direction_id = request.args.get("direction_id")
        if direction_id is not None:
            movies_query = movies_query.filter(Movie.director_id == direction_id)
        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            movies_query = movies_query.filter(Movie.genre_id == genre_id)
        return movies_schema.dump(movies_query.all()), 200

    def post(self):
        request_json = request.json
        new_movie = Movie(**request_json)

        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movie_ns.route("/<int:uid>")
class MovieView(Resource):
    def get(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "", 404
        return movies_schema.dump(movie), 200

    def put(self, uid: int):
        update_movie = db.session.query(Movie).filter(Movie.id == uid).update(request.json)
        if update_movie != 1:
            return "", 400
        return "", 204

    def delete(self, uid: int):
        delete_movie = db.session.query(Movie).get(uid)
        if delete_movie != 1:
            return "", 400
        db.session.delete()
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
