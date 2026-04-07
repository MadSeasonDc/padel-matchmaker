import streamlit as st
import json
import os

DATA_FILE = "padel_data.json"

JUGADORES_INICIALES = [
    "Antonio Seoane",
    "Carlos Ortiz",
    "Nacho Moros",
    "Nacho Urbano",
    "Adrian Gomez",
    "Alvaro Sarmiento",
    "Manuel Díaz",
    "Patricia Seoane",
    "Julio Mendez",
    "Jose Luis Pozuelo",
    "Juan Carmona",
    "Jesus Fernandez",
    "Jordi Safont",
    "Bea Jaen",
    "Cecile Autran",
    "Ester Martin",
    "Graciela Martinez",
    "Alicia Soriano",
    "Lela Bekauri",
    "Oriol Palacios"
]



def load_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "jugadores": [
                {
                    "nombre": nombre,
                    "disponible": False,
                    "puntos": 0,
                    "fijo": True
                }
                for nombre in JUGADORES_INICIALES
            ],
            "jornadas": [{"numero": i + 1, "partidos": []} for i in range(7)],
            "partidos_borrador": []
        }
        save_data(data)
        return data

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    # Asegurar estructura
    if "jugadores" not in data:
        data["jugadores"] = []

    # Asegurar que los jugadores iniciales existen y están protegidos
    nombres_existentes = {j["nombre"] for j in data["jugadores"]}

    for nombre in JUGADORES_INICIALES:
        if nombre not in nombres_existentes:
            data["jugadores"].append({
                "nombre": nombre,
                "disponible": False,
                "puntos": 0,
                "fijo": True
            })

    # Asegurar jornadas
    if "jornadas" not in data or len(data["jornadas"]) == 0:
        data["jornadas"] = [{"numero": i + 1, "partidos": []} for i in range(7)]

    # Asegurar borrador
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
    ["Jugadores",  "Partidos",  "Ranking"]
)
 
# ----------------------------
# JUGADORES
# ----------------------------
if menu == "Jugadores":
    st.header("👥 Jugadores")

    for j in data["jugadores"]:
        st.write(j["nombre"])
# ----------------------------
# PARTIDOS
# ----------------------------
elif menu == "Partidos":
    st.header("🎾 Partidos")

    # Asegurar estructura
    if "partidos" not in data:
        data["partidos"] = []

    # Crear nuevo partido
    if st.button("➕ Nuevo partido"):
        data["partidos"].append({
            "pareja_1": [],
            "pareja_2": [],
            "lugar": "",
            "fecha": "",
            "hora": "",
            "set1": "",
            "set2": "",
            "set3": "",
            "cerrado": False
        })
        save_data(data)
        st.rerun()

    st.markdown("---")

    # Si no hay partidos, salir
    if not data["partidos"]:
        st.info("No hay partidos creados todavía")
        st.stop()

    # Selector de partido
    partido_index = st.selectbox(
        "Selecciona un partido",
        range(len(data["partidos"])),
        format_func=lambda i: f"Partido {i + 1}"
    )

    partido = data["partidos"][partido_index]

    st.subheader(f"🧾 Partido {partido_index + 1}")

    jugadores = [j["nombre"] for j in data["jugadores"]]

    # Selección de parejas
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👥 Pareja 1")
        pareja1 = st.multiselect(
            "Jugadores",
            jugadores,
            default=partido["pareja_1"],
            max_selections=2,
            key=f"p1_{partido_index}"
        )

    with col2:
        st.markdown("### 👥 Pareja 2")
        pareja2 = st.multiselect(
            "Jugadores",
            jugadores,
            default=partido["pareja_2"],
            max_selections=2,
            key=f"p2_{partido_index}"
        )

    # Información del partido
    st.markdown("### 📍 Información")

    partido["lugar"] = st.text_input(
        "Lugar",
        partido["lugar"],
        key=f"lugar_{partido_index}"
    )

    partido["fecha"] = st.text_input(
        "Fecha",
        partido["fecha"],
        key=f"fecha_{partido_index}"
    )

    partido["hora"] = st.text_input(
        "Hora",
        partido["hora"],
        key=f"hora_{partido_index}"
    )

    # Resultado
    st.markdown("### 🎾 Resultado")

    partido["set1"] = st.text_input(

        
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
