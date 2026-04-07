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
    [  "Jornadas",  "Ranking"]
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
    import datetime

    st.header("📅 Jornadas")

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
                "fecha": str(datetime.date.today()),
                "hora": "18:00",
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

    # ⬇️ INFORMACIÓN EN UNA SOLA LÍNEA
    col_lugar, col_fecha, col_hora = st.columns(3)

    with col_lugar:
        partido["lugar"] = st.text_input(
            "📍 Lugar",
            partido["lugar"]
        )

    with col_fecha:
        fecha_val = datetime.date.fromisoformat(partido["fecha"])
        partido["fecha"] = str(
            st.date_input(
                "📅 Fecha",
                value=fecha_val
            )
        )

    # Horas de 08:00 a 22:00 cada 30 min
    horas = [
        f"{h:02d}:{m:02d}"
        for h in range(8, 23)
        for m in (0, 30)
        if not (h == 22 and m == 30)
    ]

    with col_hora:
        partido["hora"] = st.selectbox(
            "⏰ Hora",
            horas,
            index=horas.index(partido["hora"]) if partido["hora"] in horas else 0
        )

    # ---------- Selección de jugadores ----------
    jugadores = sorted([j["nombre"] for j in data["jugadores"]])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👥 Pareja 1")
        pareja1 = st.multiselect(
            "Jugadores Pareja 1",
            jugadores,
            default=partido["pareja_1"],
            max_selections=2,
            key=f"p1_{jornada_index}_{partido_index}"
        )

    jugadores_pareja2 = [j for j in jugadores if j not in pareja1]

    with col2:
        st.markdown("### 👥 Pareja 2")
        pareja2 = st.multiselect(
            "Jugadores Pareja 2",
            jugadores_pareja2,
            default=partido["pareja_2"],
            max_selections=2,
            key=f"p2_{jornada_index}_{partido_index}"
        )

    # ---------- Resultado ----------
    st.markdown("### 🎾 Resultado (juegos por set)")

    for set_num in [1, 2, 3]:
        st.markdown(f"**Set {set_num}" + (" / Desempate**" if set_num == 3 else "**"))
        c1, c2 = st.columns(2)
        with c1:
            partido[f"set{set_num}_p1"] = st.number_input(
                "Pareja 1",
                0, 7, partido[f"set{set_num}_p1"],
                key=f"s{set_num}p1_{jornada_index}_{partido_index}"
            )
        with c2:
            partido[f"set{set_num}_p2"] = st.number_input(
                "Pareja 2",
                0, 7, partido[f"set{set_num}_p2"],
                key=f"s{set_num}p2_{jornada_index}_{partido_index}"
            )

    # Guardar
    if st.button("💾 Guardar partido"):
        if len(pareja1) != 2 or len(pareja2) != 2:
            st.error("Cada pareja debe tener exactamente 2 jugadores")
        else:
            partido["pareja_1"] = pareja1
            partido["pareja_2"] = pareja2
            save_data(data)
            st.success("Partido guardado ✅")


# ----------------------------
# RANKING
# ----------------------------
elif menu == "Ranking":
    import pandas as pd

    st.header("🏆 Ranking")

    # Inicializar estadísticas por jugador
    stats = {}
    for j in data["jugadores"]:
        stats[j["nombre"]] = {
            "PJ": 0,
            "PG": 0,
            "PP": 0,
            "Pts": 0,
            "TSW": 0,
            "TSL": 0
        }

    # Recorrer jornadas y partidos
    for jornada in data.get("jornadas", []):
        for p in jornada.get("partidos", []):

            pareja1 = p.get("pareja_1", [])
            pareja2 = p.get("pareja_2", [])

            if len(pareja1) != 2 or len(pareja2) != 2:
                continue  # partido incompleto

            # Juegos (solo set 1 y 2)
            s1_p1 = p.get("set1_p1", 0)
            s1_p2 = p.get("set1_p2", 0)
            s2_p1 = p.get("set2_p1", 0)
            s2_p2 = p.get("set2_p2", 0)

            # Sets ganados
            sets_p1 = 0
            sets_p2 = 0

            if s1_p1 > s1_p2:
                sets_p1 += 1
            elif s1_p2 > s1_p1:
                sets_p2 += 1

            if s2_p1 > s2_p2:
                sets_p1 += 1
            elif s2_p2 > s2_p1:
                sets_p2 += 1

            # Juegos totales
            juegos_p1 = s1_p1 + s2_p1
            juegos_p2 = s1_p2 + s2_p2

            # PJ y juegos
            for j in pareja1:
                stats[j]["PJ"] += 1
                stats[j]["TSW"] += juegos_p1
                stats[j]["TSL"] += juegos_p2

            for j in pareja2:
                stats[j]["PJ"] += 1
                stats[j]["TSW"] += juegos_p2
                stats[j]["TSL"] += juegos_p1

            # Resultado
            if sets_p1 > sets_p2:
                for j in pareja1:
                    stats[j]["PG"] += 1
                    stats[j]["Pts"] += 2
                for j in pareja2:
                    stats[j]["PP"] += 1

            elif sets_p2 > sets_p1:
                for j in pareja2:
                    stats[j]["PG"] += 1
                    stats[j]["Pts"] += 2
                for j in pareja1:
                    stats[j]["PP"] += 1

            else:
                for j in pareja1 + pareja2:
                    stats[j]["Pts"] += 1

    # Construir ranking
    ranking = []
    for nombre, s in stats.items():
        ranking.append({
            "Jugador": nombre,
            "PJ": s["PJ"],
            "PG": s["PG"],
            "PP": s["PP"],
            "Pts": s["Pts"],
            "TSW": s["TSW"],
            "TSL": s["TSL"],
            "Dif": s["TSW"] - s["TSL"]
        })

    # Ordenar
    ranking.sort(
        key=lambda x: (x["Pts"], x["PG"], x["Dif"]),
        reverse=True
    )

    # DataFrame
    df = pd.DataFrame(ranking)
    df.insert(0, "RK", range(1, len(df) + 1))
    df = df[["RK", "Jugador", "PJ", "PG", "PP", "Pts", "TSW", "TSL", "Dif"]]

    # Estilos TOP 3
    def style_top3(row):
        if row["RK"] == 1:
            return ["background-color: #FFD700; font-weight: bold"] * len(row)  # Oro
        elif row["RK"] == 2:
            return ["background-color: #C0C0C0"] * len(row)  # Plata
        elif row["RK"] == 3:
            return ["background-color: #CD7F32"] * len(row)  # Bronce
        else:
            return [""] * len(row)

    styled_df = df.style.apply(style_top3, axis=1)

    st.markdown("### 📊 Clasificación General")
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
