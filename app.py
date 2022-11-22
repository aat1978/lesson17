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


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


api = Api(app)

movie_ns = api.namespace("movies")
director_ns = api.namespace("directors")
genre_ns = api.namespace("genres")

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route("/")
class MoviesView(Resource):
    def get(self, page=1):
        movies_query = db.session.query(Movie)
        director_id = request.args.get("director_id")
        if director_id is not None:
            movies_query = movies_query.filter(Movie.director_id == director_id)
        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            movies_query = movies_query.filter(Movie.genre_id == genre_id)
        movies = movies_query.paginate(page, per_page=5)
        return movies_schema.dump(movies.items), 200

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
        return movie_schema.dump(movie), 200

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


@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director)
        return directors_schema.dump(all_directors), 200

    def post(self):
        request_json = request.json
        new_director = Director(**request_json)

        with db.session.begin():
            db.session.add(new_director)

        return "", 201


@director_ns.route("/<int:uid>")
class DirectorView(Resource):
    def get(self, uid: int):
        director = db.session.query(Director).get(uid)
        if not director:
            return "", 404
        return director_schema.dump(director), 200

    def put(self, uid: int):
        update_director = db.session.query(Director).filter(Director.id == uid).update(request.json)
        if update_director != 1:
            return "", 400
        return "", 204

    def delete(self, uid: int):
        delete_director = db.session.query(Director).get(uid)
        if delete_director != 1:
            return "", 400
        db.session.delete()
        db.session.commit()
        return "", 204


@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre)
        return genres_schema.dump(all_genres), 200

    def post(self):
        request_json = request.json
        new_genre = Genre(**request_json)

        with db.session.begin():
            db.session.add(new_genre)

        return "", 201


@genre_ns.route("/<int:uid>")
class GenreView(Resource):
    def get(self, uid: int):
        genre = db.session.query(Genre).get(uid)
        if not genre:
            return "", 404
        return genre_schema.dump(genre), 200

    def put(self, uid: int):
        update_genre = db.session.query(Genre).filter(Genre.id == uid).update(request.json)
        if update_genre != 1:
            return "", 400
        return "", 204

    def delete(self, uid: int):
        delete_genre = db.session.query(Genre).get(uid)
        if delete_genre != 1:
            return "", 400
        db.session.delete()
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
