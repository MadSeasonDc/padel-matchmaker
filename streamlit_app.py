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
    ["Jugadores",  "Jornadas",  "Ranking"]
)
 
# ----------------------------
# JUGADORES
# ----------------------------
if menu == "Jugadores":
    st.header("👥 Jugadores")

    for j in data["jugadores"]:
        st.write(j["nombre"])
# ----------------------------
# JORNADAS
# ----------------------------
elif menu == "Jornadas":
    st.header("📅 Jornadas")

    # Asegurar estructura
    if "jornadas" not in data:
        data["jornadas"] = []

    # Crear nueva jornada
    if st.button("➕ Nueva jornada"):
        numero = len(data["jornadas"]) + 1
        data["jornadas"].append({
            "numero": numero,
            "partidos": []
        })
        save_data(data)
        st.rerun()

    st.markdown("---")

    if not data["jornadas"]:
        st.info("No hay jornadas creadas todavía")
        st.stop()

    # Selector de jornada
    jornada_index = st.selectbox(
        "Selecciona una jornada",
        list(range(len(data["jornadas"]))),
        format_func=lambda i: f"Jornada {data['jornadas'][i]['numero']}"
    )

    jornada = data["jornadas"][jornada_index]

    st.subheader(f"🗂 Jornada {jornada['numero']}")
    st.write(f"Partidos: {len(jornada['partidos'])} / 5")

    # Añadir partido (máx. 5)
    if len(jornada["partidos"]) < 5:
        if st.button("➕ Añadir partido a esta jornada"):
            jornada["partidos"].append({
                "pareja_1": [],
                "pareja_2": [],
                "lugar": "",
                "fecha": "",
                "hora": "",
                "set1_p1": 0,
                "set1_p2": 0,
                "set2_p1": 0,
                "set2_p2": 0,
                "set3_p1": 0,
                "set3_p2": 0,
                "cerrado": False
            })
            save_data(data)
            st.rerun()
    else:
        st.warning("Esta jornada ya tiene el máximo de 5 partidos")

    st.markdown("---")

    if not jornada["partidos"]:
        st.info("La jornada aún no tiene partidos")
        st.stop()

    # Selector de partido
    partido_index = st.selectbox(
        "Selecciona un partido",
        list(range(len(jornada["partidos"]))),
        format_func=lambda i: f"Partido {i + 1}"
    )

    partido = jornada["partidos"][partido_index]
    st.subheader(f"🎾 Partido {partido_index + 1}")

    jugadores = [j["nombre"] for j in data["jugadores"]]

    # ---- PAREJAS (AQUÍ ESTABA EL ERROR ANTES) ----
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👥 Pareja 1")
        pareja1 = st.multiselect(
            label="Jugadores Pareja 1",
            options=jugadores,
            default=partido["pareja_1"],
            max_selections=2,
            key=f"p1_{jornada_index}_{partido_index}"
        )

    with col2:
        st.markdown("### 👥 Pareja 2")
        pareja2 = st.multiselect(
            label="Jugadores Pareja 2",
            options=jugadores,
            default=partido["pareja_2"],
            max_selections=2,
            key=f"p2_{jornada_index}_{partido_index}"
        )

    # Información del partido
    st.markdown("### 📍 Información")
    partido["lugar"] = st.text_input("Lugar", partido["lugar"])
    partido["fecha"] = st.text_input("Fecha", partido["fecha"])
    partido["hora"] = st.text_input("Hora", partido["hora"])

    # Resultado
    st.markdown("### 🎾 Resultado (juegos por set)")

    st.markdown("**Set 1**")
    c1, c2 = st.columns(2)
    with c1:
        partido["set1_p1"] = st.number_input(
            "Pareja 1",
            0, 7, partido["set1_p1"],
            key=f"s1p1_{jornada_index}_{partido_index}"
        )
    with c2:
        partido["set1_p2"] = st.number_input(
            "Pareja 2",
            0, 7, partido["set1_p2"],
            key=f"s1p2_{jornada_index}_{partido_index}"
        )

    st.markdown("**Set 2**")
    c1, c2 = st.columns(2)
    with c1:
        partido["set2_p1"] = st.number_input(
            "Pareja 1",
            0, 7, partido["set2_p1"],
            key=f"s2p1_{jornada_index}_{partido_index}"
        )
    with c2:
        partido["set2_p2"] = st.number_input(
            "Pareja 2",
            0, 7, partido["set2_p2"],
            key=f"s2p2_{jornada_index}_{partido_index}"
        )

    st.markdown("**Set 3 / Desempate (opcional – no cuenta)**")
    c1, c2 = st.columns(2)
    with c1:
        partido["set3_p1"] = st.number_input(
            "Pareja 1",
            0, 7, partido["set3_p1"],
            key=f"s3p1_{jornada_index}_{partido_index}"
        )
    with c2:
        partido["set3_p2"] = st.number_input(
            "Pareja 2",
            0, 7, partido["set3_p2"],
            key=f"s3p2_{jornada_index}_{partido_index}"
        )

    # Guardar partido
    if st.button("💾 Guardar partido"):
        if len(pareja1) != 2 or len(pareja2) != 2:
            st.error("Cada pareja debe tener exactamente 2 jugadores")
        elif set(pareja1) & set(pareja2):
            st.error("Un jugador no puede estar en las dos parejas")
        else:
            partido["pareja_1"] = pareja1
            partido["pareja_2"] = pareja2
            save_data(data)
            st.success("Partido guardado ✅")


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
