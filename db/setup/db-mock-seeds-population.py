import uuid
import db.queries.queries as queries


# Connect to your PostgreSQL database with the DB URL
conn = queries.createConnection()
# Create a cursor object
cur = queries.createCursor(conn)

brassicaNapus = (str(uuid.uuid4()), "Brassica napus")
brassicaJunsea = (str(uuid.uuid4()), "Brassica juncea")
cirsiumArvense = (str(uuid.uuid4()), "Cirsium arvense")
cirsiumVulgare = (str(uuid.uuid4()), "Cirsium vulgare")
carduusNutans = (str(uuid.uuid4()), "Carduus nutans")
bromusSecalinus = (str(uuid.uuid4()), "Bromus secalinus")
bromusHordeaceus = (str(uuid.uuid4()), "Bromus hordeaceus")
bromusJaponicus = (str(uuid.uuid4()), "Bromus japonicus")
loliumTemulentum = (str(uuid.uuid4()), "Lolium temulentum")
solanumCarolinense = (str(uuid.uuid4()), "Solanum carolinense")
solanumNigrum = (str(uuid.uuid4()), "Solanum nigrum")
solanumRostratum = (str(uuid.uuid4()), "Solanum rostratum")
ambrosiaArtemisiifolia = (str(uuid.uuid4()), "Ambrosia artemisiifolia")
ambrosiaTrifida = (str(uuid.uuid4()), "Ambrosia trifida")
Ambrosiapsilostachya = (str(uuid.uuid4()), "Ambrosia psilostachya")

queries.createSearchPath(conn, cur)

# Query to insert a seed
query = "INSERT INTO seeds (id,name) VALUES (%s,%s),(%s,%s),(%s,%s),(%s,%s),(%s,%s),(%s,%s),(%s,%s),(%s,%s),(%s,%s),(%s,%s),(%s,%s),(%s,%s),(%s,%s),(%s,%s),(%s,%s)"
data = (
    brassicaNapus[0],
    brassicaNapus[1],
    brassicaJunsea[0],
    brassicaJunsea[1],
    cirsiumArvense[0],
    cirsiumArvense[1],
    cirsiumVulgare[0],
    cirsiumVulgare[1],
    carduusNutans[0],
    carduusNutans[1],
    bromusSecalinus[0],
    bromusSecalinus[1],
    bromusHordeaceus[0],
    bromusHordeaceus[1],
    bromusJaponicus[0],
    bromusJaponicus[1],
    loliumTemulentum[0],
    loliumTemulentum[1],
    solanumCarolinense[0],
    solanumCarolinense[1],
    solanumNigrum[0],
    solanumNigrum[1],
    solanumRostratum[0],
    solanumRostratum[1],
    ambrosiaArtemisiifolia[0],
    ambrosiaArtemisiifolia[1],
    ambrosiaTrifida[0],
    ambrosiaTrifida[1],
    Ambrosiapsilostachya[0],
    Ambrosiapsilostachya[1],
)

# queries.queryParameterizedDB(conn,cur,query,data)

queries.queryDB(conn, cur, "select id,name from seeds")
queries.printResults(cur)
