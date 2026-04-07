import streamlit as st
import json
import os

DATA_FILE = "padel_data.json"

def load_data():

    # Si el archivo no existe, crear estructura completa
    if not os.path.exists(DATA_FILE):
        data = {
            "jugadores": [],
            "jornadas": [{"numero": i + 1, "partidos": []} for i in range(7)],
            "partidos_borrador": []
        }
        save_data(data)
        return data

    # Si existe, cargarlo
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    # Asegurar claves necesarias
    if "jugadores" not in data:
        data["jugadores"] = []

    if "jornadas" not in data or len(data["jornadas"]) == 0:
        data["jornadas"] = [{"numero": i + 1, "partidos": []} for i in range(7)]

    if "partidos_borrador" not in data:
        data["partidos_borrador"] = []

    save_data(data)
    return data


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

st.set_page_config(page_title="Pádel Matchmaker", layout="wide")
st.title("🏓 Pádel Matchmaker")

menu = st.sidebar.radio(
    "Menú",
    ["Jugadores", "Disponibilidad", "Generar Partidos", "Jornadas", "Ranking"]
)

# ----------------------------
# DISPONIBILIDAD
# ----------------------------
# ----------------------------
# JUGADORES
# ----------------------------
if menu == "Jugadores":
    st.header("👥 Gestión de jugadores")

    nuevo = st.text_input("Nombre del jugador")

    if st.button("Añadir jugador"):
        if nuevo and nuevo not in [j["nombre"] for j in data["jugadores"]]:
            data["jugadores"].append({
                "nombre": nuevo,
                "disponible": False,
                "puntos": 0
            })
            save_data(data)
            st.success(f"Jugador '{nuevo}' añadido")
        else:
            st.error("Nombre vacío o jugador ya existe")

    st.markdown("### Lista de jugadores")

    for i, j in enumerate(data["jugadores"]):
        col1, col2 = st.columns([4, 1])
        col1.write(j["nombre"])

        if col2.button("🗑️", key=f"del_{i}"):
            data["jugadores"].pop(i)
            save_data(data)
            st.experimental_rerun()
            
if menu == "Disponibilidad":
    st.header("✅ Disponibilidad de jugadores")

    for j in data["jugadores"]:
        j["disponible"] = st.checkbox(j["nombre"], j["disponible"])

    if st.button("Guardar"):
        save_data(data)
        st.success("Disponibilidad guardada")

# ----------------------------
# GENERAR PARTIDOS
# ----------------------------
elif menu == "Generar Partidos":
    st.header("🎾 Partidos automáticos")

    disponibles = [j for j in data["jugadores"] if j["disponible"]]
    st.info(f"Jugadores disponibles: {len(disponibles)}")

    jugadores = disponibles.copy()

    partido_num = 1
    while len(jugadores) >= 4:
        p = jugadores[:4]
        jugadores = jugadores[4:]

        st.write(
            f"**Partido {partido_num}:** "
            f"{p[0]['nombre']} & {p[1]['nombre']} vs "
            f"{p[2]['nombre']} & {p[3]['nombre']}"
        )
        partido_num += 1

    if jugadores:
        st.warning(
            "Reservas: " + ", ".join(j["nombre"] for j in jugadores)
        )

# ----------------------------
# JORNADAS
# ----------------------------
elif menu == "Jornadas":
    st.header("📅 Jornadas")

    jornada_sel = st.selectbox(
        "Selecciona jornada",
        [j["numero"] for j in data["jornadas"]]
    )

    jornada = data["jornadas"][jornada_sel - 1]

    jugadores_nombres = [j["nombre"] for j in data["jugadores"]]

    st.subheader("➕ Añadir partido")
    pareja1 = st.multiselect("Pareja 1", jugadores_nombres, max_selections=2)
    pareja2 = st.multiselect("Pareja 2", jugadores_nombres, max_selections=2)

    pista = st.text_input("Pista")
    lugar = st.text_input("Lugar")

    if st.button("Añadir partido"):
        if len(pareja1) == 2 and len(pareja2) == 2:
            jornada["partidos"].append({
                "jugadores": pareja1 + pareja2,
                "pista": pista,
                "lugar": lugar,
                "set1": "",
                "set2": "",
                "desempate": ""
            })
            save_data(data)
            st.success("Partido añadido")
        else:
            st.error("Debes seleccionar 2 jugadores por pareja")

    st.markdown("---")

    for i, p in enumerate(jornada["partidos"]):
        st.markdown(f"### Partido {i + 1}")
        st.write("Jugadores:", ", ".join(p["jugadores"]))
        st.write(f"📍 {p['lugar']} · Pista {p['pista']}")

# ----------------------------
# RANKING
# ----------------------------
elif menu == "Ranking":
    st.header("🏆 Ranking")

    ranking = sorted(
        data["jugadores"],
        key=lambda x: x["puntos"],
        reverse=True
    )

    for i, j in enumerate(ranking, start=1):
        st.write(f"{i}. {j['nombre']} – {j['puntos']} puntos")
