from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DATABASE = "monochrome.db"


# ======================================================
# ARTWORK DATA
# ======================================================

artworks = {

    "wide": {
        "title": "Wide Perspective",
        "artist": "@yourname",
        "image": "wide-perspective.jpg",
        "description":
            "A distorted wide-angle perspective inspired by the visual effect of a concave mirror.",
        "monos": 142,
        "artist_note":
            "An experiment with perspective and distortion, inspired by the way curved surfaces can completely change an ordinary view."
    },

    "mandala": {
        "title": "Mandala",
        "artist": "@yourname",
        "image": "mandala.jpg",
        "description":
            "A traditional mandala artwork built through repeated patterns, symmetry, and intricate detailing.",
        "monos": 287,
        "artist_note":
            "Inspired by traditional mandala art and the balance created through repetition and symmetry."
    },

    "dead": {
        "title": "Dead",
        "artist": "@yourname",
        "image": "dead.jpg",
        "description":
            "A monochrome composition built around contrasting sections, shapes, and textures.",
        "monos": 96,
        "artist_note":
            "An exploration of black-and-white composition, using separate sections to create contrast and visual tension."
    }

}


# ======================================================
# DATABASE
# ======================================================

def get_db():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


def init_db():

    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS stories (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            artwork_id TEXT NOT NULL,

            text TEXT NOT NULL,

            user TEXT NOT NULL,

            monos INTEGER DEFAULT 0

        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS submissions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            artist TEXT NOT NULL,

            description TEXT,

            image TEXT NOT NULL,

            monos INTEGER DEFAULT 0,

            artist_note TEXT

        )
    """)

    connection.commit()

    connection.close()


# ======================================================
# HOME
# ======================================================

@app.route("/")
def home():

    return render_template("index.html")


# ======================================================
# EXPLORE
# ======================================================

@app.route("/explore")
def explore():

    artwork_list = []

    # --------------------------------------------------
    # ORIGINAL ARTWORKS
    # --------------------------------------------------

    for artwork_id, artwork in artworks.items():

        artwork_copy = artwork.copy()

        artwork_copy["id"] = artwork_id

        artwork_list.append(
            artwork_copy
        )


    # --------------------------------------------------
    # SUBMITTED ARTWORKS
    # --------------------------------------------------

    connection = get_db()

    rows = connection.execute(
        """
        SELECT
            id,
            title,
            artist,
            description,
            image,
            monos,
            artist_note

        FROM submissions

        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()


    # --------------------------------------------------
    # ADD SUBMISSIONS TO EXPLORE
    # --------------------------------------------------

    for row in rows:

        artwork_list.append({

            "id":
                "submission_" +
                str(row["id"]),

            "title":
                row["title"],

            "artist":
                row["artist"],

            "image":
                row["image"],

            "description":
                row["description"],

            "monos":
                row["monos"],

            "artist_note":
                row["artist_note"]

        })


    return render_template(
        "explore.html",
        artworks=artwork_list
    )
# ======================================================
# ABOUT
# ======================================================

@app.route("/about")
def about():

    return render_template("about.html")


# ======================================================
# PROFILE
# ======================================================

@app.route("/profile")
def profile():

    return render_template("profile.html")


# ======================================================
# SUBMIT
# ======================================================

@app.route("/submit")
def submit():

    return render_template("submit.html")


# ======================================================
# ARTWORK
# ======================================================

@app.route("/artwork")
def artwork():

    artwork_id = request.args.get(
        "art",
        "wide"
    )


    # ==================================================
    # ORIGINAL ARTWORK
    # ==================================================

    if artwork_id in artworks:

        artwork_data = artworks[artwork_id]

        connection = get_db()

        rows = connection.execute(
            """
            SELECT text, user, monos

            FROM stories

            WHERE artwork_id = ?

            ORDER BY id ASC
            """,
            (artwork_id,)
        ).fetchall()

        connection.close()


        return render_template(

            "artwork.html",

            artwork=artwork_data,

            artwork_id=artwork_id,

            stories=rows

        )


    # ==================================================
    # SUBMITTED ARTWORK
    # ==================================================

    if artwork_id.startswith(
        "submission_"
    ):

        try:

            submission_id = int(
                artwork_id.split("_")[1]
            )

        except (
            ValueError,
            IndexError
        ):

            return "Artwork not found", 404


        connection = get_db()


        submission = connection.execute(
            """
            SELECT
                title,
                artist,
                description,
                image,
                monos,
                artist_note

            FROM submissions

            WHERE id = ?
            """,
            (submission_id,)
        ).fetchone()


        stories = connection.execute(
            """
            SELECT
                text,
                user,
                monos

            FROM stories

            WHERE artwork_id = ?

            ORDER BY id ASC
            """,
            (artwork_id,)
        ).fetchall()


        connection.close()


        if not submission:

            return "Artwork not found", 404


        artwork_data = {

            "title":
                submission["title"],

            "artist":
                submission["artist"],

            "image":
                submission["image"],

            "description":
                submission["description"],

            "monos":
                submission["monos"],

            "artist_note":
                submission["artist_note"] or ""

        }


        return render_template(

            "artwork.html",

            artwork=artwork_data,

            artwork_id=artwork_id,

            stories=stories

        )


    return "Artwork not found", 404
# ======================================================
# GET STORIES
# ======================================================

@app.route(
    "/api/stories/<artwork_id>",
    methods=["GET"]
)
def get_stories(artwork_id):

    connection = get_db()


    rows = connection.execute(
        """
        SELECT text, user, monos

        FROM stories

        WHERE artwork_id = ?

        ORDER BY id ASC
        """,
        (artwork_id,)
    ).fetchall()


    connection.close()


    stories = []


    for row in rows:

        stories.append({

            "text": row["text"],

            "user": row["user"],

            "monos": row["monos"]

        })


    return jsonify(stories)


# ======================================================
# ADD STORY
# ======================================================

@app.route(
    "/api/stories/<artwork_id>",
    methods=["POST"]
)
def add_story(artwork_id):

    data = request.get_json()


    if not data:

        return jsonify({
            "error": "No data received"
        }), 400


    story_text = data.get(
        "text",
        ""
    ).strip()


    if not story_text:

        return jsonify({
            "error": "Story is empty"
        }), 400


    if artwork_id not in artworks:

        return jsonify({
            "error": "Artwork not found"
        }), 404


    connection = get_db()


    connection.execute(
        """
        INSERT INTO stories
        (
            artwork_id,
            text,
            user,
            monos
        )

        VALUES (?, ?, ?, ?)
        """,

        (
            artwork_id,
            story_text,
            "@you",
            0
        )
    )


    connection.commit()

    connection.close()


    return jsonify({

        "text": story_text,

        "user": "@you",

        "monos": 0

    })

# ======================================================
# SUBMIT ARTWORK API
# ======================================================

@app.route(
    "/api/submit",
    methods=["POST"]
)
def submit_artwork():

    title = request.form.get(
        "title",
        ""
    ).strip()

    artist = request.form.get(
        "artist",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    image = request.files.get(
        "image"
    )


    if not title or not artist:

        return jsonify({
            "error": "Title and artist are required."
        }), 400


    if not image:

        return jsonify({
            "error": "Please select an image."
        }), 400


    # --------------------------------------------------
    # SAVE IMAGE
    # --------------------------------------------------

    images_folder = os.path.join(
        app.static_folder,
        "images"
    )


    os.makedirs(
        images_folder,
        exist_ok=True
    )


    filename = image.filename


    # Keep only the filename
    filename = os.path.basename(
        filename
    )


    image_path = os.path.join(
        images_folder,
        filename
    )


    image.save(
        image_path
    )


    # --------------------------------------------------
    # SAVE SUBMISSION TO DATABASE
    # --------------------------------------------------

    connection = get_db()


    connection.execute(
        """
        INSERT INTO submissions
        (
            title,
            artist,
            description,
            image,
            monos,
            artist_note
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,

        (
            title,
            artist,
            description,
            filename,
            0,
            ""
        )
    )


    connection.commit()

    connection.close()


    return jsonify({

        "success": True,

        "message":
            "Artwork submitted successfully."

    })
# ======================================================
# START
# ======================================================

# Initialize database
init_db()


if __name__ == "__main__":

    app.run(
        debug=True
    )
