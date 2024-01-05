from pymongo import MongoClient
from config import MONGODB_IP, MONGODB_PORT, MYSQL_IP, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, NEO4J_IP, NEO4J_PORT, NEO4J_USER, NEO4J_PASSWORD
from neo4j import GraphDatabase
import mysql.connector

client = MongoClient(f'mongodb://{MONGODB_IP}:{MONGODB_PORT}/')

uri = f"bolt://{NEO4J_IP}:{NEO4J_PORT}" 
username = NEO4J_USER
password = NEO4J_PASSWORD

movies_to_add = [
        {
            "title": "Big Buck Bunny",
            "length": "10 minutes",
            "genre": "Action",
            "thumbnail": "/static/images/bbb.jpg",
            "mp4File": "bbb.mp4",
        },
        {
            "title": "Valkaama",
            "length": "8 minutes",
            "genre": "Drama",
            "thumbnail": "/static/images/Valkaama.jpg",
            "mp4File": "Valkaama.mp4",
        },
        {
            "title": "Elephants Dream",
            "length": "10 minutes",
            "genre": "Comedy",
            "thumbnail": "/static/images/ed.jpg",
            "mp4File": "ed.mp4",
        },
        {
            "title": "La chute d’une plume",
            "length": "10 minutes",
            "genre": "Sci-Fi",
            "thumbnail": "/static/images/plume.png",
            "mp4File": "plume.mp4",
        },
    ]

#NEO4j
def clear_neo4j():
    # Connect to the Neo4j database
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        # Create a session
        with driver.session() as session:
            # Run a Cypher query to delete all nodes and relationships
            session.run("MATCH (n) DETACH DELETE n")

def create_graph(tx):
    for movie in movies_to_add:
        tx.run("CREATE (:Movie {id: $id})", id=movie['title'])

def is_neo4j_empty():
    query_nodes = "MATCH (n) RETURN COUNT(n) AS nodeCount"
    query_relationships = "MATCH ()-->() RETURN COUNT(*) AS relationshipCount"

    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            result_nodes = session.run(query_nodes)
            result_relationships = session.run(query_relationships)

            node_count = result_nodes.single()["nodeCount"]
            relationship_count = result_relationships.single()["relationshipCount"]

            return node_count == 0 and relationship_count == 0

def start_neo4j():
    if is_neo4j_empty():
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                session.write_transaction(create_graph)   

def create_user_node(tx, email):
    # Cypher query to create a user node
    query = (
        "CREATE (u:User {email: $email}) "
        "RETURN u"
    )
    result = tx.run(query, email=email)
    return result.single()

def add_user_to_neo4j(email):
    # Connect to Neo4j
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            # Execute the Cypher query to create a user node
            result = session.write_transaction(create_user_node, email)
            print(f"User node created: {result['u']['email']}")

def create_connection(user_email, movie_id):
    query = (
        "MERGE (u:User {email: $email}) "
        "MERGE (m:Movie {id: $movie_id}) "
        "MERGE (u)-[:WATCHED]->(m)"
    )
    
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            session.run(query, email=user_email, movie_id=movie_id)

def recommend_movies(user_email, limit=10):
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {email: $userEmail})-[:WATCHED]->(watchedMovie:Movie)
                WITH COLLECT(watchedMovie) AS watchedMovies

                MATCH (m:Movie)
                WHERE NOT m IN watchedMovies
                WITH m, SIZE([(user)-[:WATCHED]->(m) | user]) AS watchCount
                RETURN m.id AS movieId, watchCount
                ORDER BY watchCount DESC
                """,
                userEmail=user_email,
                limit=limit
            )

            recommendations = [{"movieId": record["movieId"], "watchCount": record["watchCount"]} for record in result]

    return recommendations

# MYSQL
def initialize_mysql_database():
    try: 
        # Establish a connection to the MySQL server
        conn = mysql.connector.connect(host=MYSQL_IP, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)

        # Create a cursor object
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255),
                password VARCHAR(255),
                admin BOOLEAN DEFAULT FALSE
            )
        ''')

        conn.commit()
        return cursor, conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None

def user_exists(cursor, email):
    query = "SELECT COUNT(*) FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    return result[0] > 0

#MongoDB
def populate_movies():
    # Connect to MongoDB
    db = client["movies"]
    collection = db["movies"]

    # Check if the 'movies' collection is empty
    if collection.count_documents({}) == 0:
        # Insert movies into the collection
        result = collection.insert_many(movies_to_add)
        print(f"{result.inserted_ids} movies inserted successfully.")
    else:
        print("Movies collection is not empty. Skipping population.")

def get_movies():
    db = client["movies"]
    movies = db.movies.find()
    return movies