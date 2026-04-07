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
            "partidos_borrador": [],
            "locations": []   # ✅ se crea desde el inicio
        }
        save_data(data)
        return data

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    # Asegurar jugadores
    if "jugadores" not in data:
        data["jugadores"] = []

    # Asegurar jugadores iniciales
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

    # ✅ Asegurar locations
    if "locations" not in data:
        data["locations"] = []

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
    [ "Jornadas",  "Ranking", "Locations"]
)

# ----------------------------
# JORNADAS
# ----------------------------

if menu == "Jornadas":
    import datetime

    st.header("📅 Jornadas")

    if "jornadas" not in data:
        data["jornadas"] = []

    if not data["jornadas"]:
        st.info("No hay jornadas disponibles")
        st.stop()

    # Selector de jornada
    jornada_index = st.selectbox(
        "Selecciona una jornada",
        range(len(data["jornadas"])),
        format_func=lambda i: f"Jornada {data['jornadas'][i]['numero']}"
    )

    jornada = data["jornadas"][jornada_index]

    st.subheader(f"🗂 Jornada {jornada['numero']}")
    st.write(f"Partidos: {len(jornada['partidos'])} / 5")

    # 👉 Crear automáticamente Partido 1 si no hay ninguno
    if len(jornada["partidos"]) == 0:
        jornada["partidos"].append({
            "pareja_1": [],
            "pareja_2": [],
            "lugar": "",
            "fecha": str(datetime.date.today()),
            "hora": "18:00",
            "set1_p1": 0, "set1_p2": 0,
            "set2_p1": 0, "set2_p2": 0,
            "set3_p1": 0, "set3_p2": 0
        })
        save_data(data)
        st.rerun()

    # --------- TABS ----------
    tabs_labels = []

    if len(jornada["partidos"]) < 5:
        tabs_labels.append("➕")

    tabs_labels += [f"Partido {i+1}" for i in range(len(jornada["partidos"]))]
    tabs = st.tabs(tabs_labels)

    offset = 0

    # --------- TAB ➕ (CREA PARTIDO DIRECTO) ----------
    if len(jornada["partidos"]) < 5:
        with tabs[0]:
            st.markdown("### ➕ Nuevo partido")
            st.info("Se añadirá automáticamente un nuevo partido")

            jornada["partidos"].append({
                "pareja_1": [],
                "pareja_2": [],
                "lugar": "",
                "fecha": str(datetime.date.today()),
                "hora": "18:00",
                "set1_p1": 0, "set1_p2": 0,
                "set2_p1": 0, "set2_p2": 0,
                "set3_p1": 0, "set3_p2": 0
            })
            save_data(data)
            st.rerun()

        offset = 1

    jugadores = sorted([j["nombre"] for j in data["jugadores"]])

    # --------- TABS DE PARTIDOS ----------
    for idx, partido in enumerate(jornada["partidos"]):
        with tabs[idx + offset]:
            st.subheader(f"🎾 Partido {idx + 1}")

            # Información en una línea
            c1, c2, c3 = st.columns(3)

            with c1:
                partido["lugar"] = st.text_input(
                    "📍 Lugar", partido["lugar"], key=f"lugar_{jornada_index}_{idx}"
                )

            with c2:
                fecha_val = datetime.date.fromisoformat(partido["fecha"])
                partido["fecha"] = str(
                    st.date_input("📅 Fecha", fecha_val, key=f"fecha_{jornada_index}_{idx}")
                )

            horas = [f"{h:02d}:{m:02d}" for h in range(8, 23) for m in (0, 30) if not (h == 22 and m == 30)]

            with c3:
                partido["hora"] = st.selectbox(
                    "⏰ Hora", horas,
                    index=horas.index(partido["hora"]) if partido["hora"] in horas else 0,
                    key=f"hora_{jornada_index}_{idx}"
                )

            # Parejas
            col1, col2 = st.columns(2)

            with col1:
                pareja1 = st.multiselect(
                    "👥 Pareja 1", jugadores,
                    default=partido["pareja_1"],
                    max_selections=2,
                    key=f"p1_{jornada_index}_{idx}"
                )

            disponibles_p2 = [j for j in jugadores if j not in pareja1]

            with col2:
                pareja2 = st.multiselect(
                    "👥 Pareja 2", disponibles_p2,
                    default=partido["pareja_2"],
                    max_selections=2,
                    key=f"p2_{jornada_index}_{idx}"
                )

            # ---------- RESULTADOS COMPACTOS (UNA FILA) ----------
            st.markdown("### 🎾 Resultado")

            s1, s2, s3 = st.columns(3)

            for set_num, col in zip([1, 2, 3], [s1, s2, s3]):
                with col:
                    st.markdown(f"**Set {set_num}**")
                    partido[f"set{set_num}_p1"] = st.number_input(
                        "P1", 0, 7, partido[f"set{set_num}_p1"],
                        key=f"s{set_num}p1_{jornada_index}_{idx}"
                    )
                    partido[f"set{set_num}_p2"] = st.number_input(
                        "P2", 0, 7, partido[f"set{set_num}_p2"],
                        key=f"s{set_num}p2_{jornada_index}_{idx}"
                    )

            if st.button("💾 Guardar partido", key=f"save_{jornada_index}_{idx}"):
                partido["pareja_1"] = pareja1
                partido["pareja_2"] = pareja2
                save_data(data)
                st.success("✅ Partido guardado")
# ----------------------------
# RANKING
# ----------------------------
elif menu == "Ranking":
    import pandas as pd

    st.header("🏆 Ranking")

    # -------- Selector de jornada para congelar ranking --------
    jornadas = data.get("jornadas", [])
    opciones_jornada = ["Todas"] + [f"Jornada {j['numero']}" for j in jornadas]

    seleccion = st.selectbox("Ranking hasta:", opciones_jornada)

    if seleccion == "Todas":
        jornadas_usar = jornadas
    else:
        nro = int(seleccion.split()[-1])
        jornadas_usar = [j for j in jornadas if j["numero"] <= nro]

    # -------- Inicializar estadísticas --------
    stats = {
        j["nombre"]: {
            "PJ": 0,
            "PG": 0,
            "PP": 0,
            "Pts": 0,
            "TSW": 0,
            "TSL": 0
        }
        for j in data["jugadores"]
    }

    # -------- Calcular estadísticas --------
    for jornada in jornadas_usar:
        for p in jornada.get("partidos", []):
            pareja1 = p.get("pareja_1", [])
            pareja2 = p.get("pareja_2", [])

            if len(pareja1) != 2 or len(pareja2) != 2:
                continue

            s1_p1, s1_p2 = p["set1_p1"], p["set1_p2"]
            s2_p1, s2_p2 = p["set2_p1"], p["set2_p2"]

            sets_p1 = (s1_p1 > s1_p2) + (s2_p1 > s2_p2)
            sets_p2 = (s1_p2 > s1_p1) + (s2_p2 > s2_p1)

            juegos_p1 = s1_p1 + s2_p1
            juegos_p2 = s1_p2 + s2_p2

            for j in pareja1:
                stats[j]["PJ"] += 1
                stats[j]["TSW"] += juegos_p1
                stats[j]["TSL"] += juegos_p2

            for j in pareja2:
                stats[j]["PJ"] += 1
                stats[j]["TSW"] += juegos_p2
                stats[j]["TSL"] += juegos_p1

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

    # -------- Crear DataFrame --------
    filas = []
    for nombre, s in stats.items():
        filas.append({
            "Jugador": nombre,
            "PJ": s["PJ"],
            "PG": s["PG"],
            "PP": s["PP"],
            "Pts": s["Pts"],
            "TSW": s["TSW"],
            "TSL": s["TSL"],
            "Dif": s["TSW"] - s["TSL"]
        })

    filas.sort(key=lambda x: (x["Pts"], x["PG"], x["Dif"]), reverse=True)

    df = pd.DataFrame(filas)
    df.insert(0, "RK", range(1, len(df) + 1))

    # -------- Iconos TOP 3 --------
    def nombre_con_icono(row):
        if row["RK"] == 1:
            return f"🥇 {row['Jugador']}"
        elif row["RK"] == 2:
            return f"🥈 {row['Jugador']}"
        elif row["RK"] == 3:
            return f"🥉 {row['Jugador']}"
        return row["Jugador"]

    df["Jugador"] = df.apply(nombre_con_icono, axis=1)

    # -------- Estilo solo en nombre --------
    def style_row(row):
        estilos = ["" for _ in row.index]
        idx = row.index.get_loc("Jugador")
        if row["RK"] == 1:
            estilos[idx] = "background-color:#FFD700;font-weight:bold"
        elif row["RK"] == 2:
            estilos[idx] = "background-color:#C0C0C0"
        elif row["RK"] == 3:
            estilos[idx] = "background-color:#CD7F32"
        return estilos

    st.dataframe(
        df.style.apply(style_row, axis=1),
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------
    # RESUMEN POR JUGADOR
    # ----------------------------
    st.markdown("---")
    st.markdown("## 👤 Resumen por jugador")

    nombres_limpios = sorted(
        df["Jugador"]
        .str.replace("🥇 ", "", regex=False)
        .str.replace("🥈 ", "", regex=False)
        .str.replace("🥉 ", "", regex=False)
    )

    jugador_sel = st.selectbox(
        "Selecciona un jugador",
        nombres_limpios
    )

    fila = df[df["Jugador"].str.contains(jugador_sel, regex=False)].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Puntos", fila["Pts"])
    c2.metric("Partidos Jugados", fila["PJ"])
    c3.metric("Dif. Juegos", fila["Dif"])

    st.write(
        f"""
**📊 Estadísticas**
- ✅ Partidos ganados: {fila['PG']}
- ❌ Partidos perdidos: {fila['PP']}
- 🎾 Juegos a favor: {fila['TSW']}
- 🚫 Juegos en contra: {fila['TSL']}
"""
    )
# ----------------------------
# LOCATIONS
# ----------------------------
elif menu == "Locations":
    st.header("📍 Locations / Clubs")

    if "locations" not in data:
        data["locations"] = []

    st.markdown("### ➕ Añadir nuevo club")

    with st.expander("Añadir nuevo club"):
        club = st.text_input("Club")
        address = st.text_input("Dirección")
        telephone = st.text_input("Teléfono")
        whatsapp = st.text_input("Whatsapp")
        email = st.text_input("E-mail")
        inout = st.selectbox("In / Out", ["Indoor", "Outdoor", "All"])
        wall = st.selectbox("Crystal / Wall", ["Crystal", "Wall"])
        price = st.text_input("Precio aproximado")
        comments = st.text_input("Comentarios adicionales")

        if st.button("Guardar club"):
            if club:
                data["locations"].append({
                    "club": club,
                    "address": address,
                    "telephone": telephone,
                    "whatsapp": whatsapp,
                    "email": email,
                    "inout": inout,
                    "wall": wall,
                    "price": price,
                    "comments": comments
                })
                save_data(data)
                st.success("✅ Club añadido correctamente")
                st.rerun()
            else:
                st.error("El nombre del club es obligatorio")

    st.markdown("---")
    st.markdown("### 📋 Clubs guardados")

    if not data["locations"]:
        st.info("No hay clubs añadidos todavía")
    else:
        import pandas as pd

        df_locations = pd.DataFrame(data["locations"])
        st.dataframe(df_locations, use_container_width=True)
