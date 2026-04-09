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

LOCATIONS_INICIALES = [
    {
        "club": "Factory Fit",
        "address": "Calle Santa Leonor, 52",
        "telephone": "913 040 291",
        "whatsapp": "639 556 378",
        "email": "info@factoryfit.es",
        "inout": "Outdoor",
        "wall": "Crystal",
        "price": "12 € hasta las 14:00 / 14 € a partir de las 14:00",
        "comments": "Pista más cercana a la oficina"
    },
    {
        "club": "AQA Los Prunos",
        "address": "Avda. Los Prunos 98-100",
        "telephone": "917 43 20 01",
        "whatsapp": "N/A",
        "email": "recepcion@aqalosprunos.com",
        "inout": "All",
        "wall": "Wall",
        "price": "8,90 € interior / 6,90 € exterior",
        "comments": ""
    },
    {
        "club": "Urb. Lela",
        "address": "N/A",
        "telephone": "N/A",
        "whatsapp": "N/A",
        "email": "N/A",
        "inout": "",
        "wall": "",
        "price": "(La voluntad)",
        "comments": "Solo partidos en los que participe Lela"
    }
]

def partido_vacio():
    return {
        "pareja_1": [],
        "pareja_2": [],
        "lugar": "",
        "fecha": "",
        "hora": "18:00",
        "set1_p1": 0, "set1_p2": 0,
        "set2_p1": 0, "set2_p2": 0,
        "set3_p1": 0, "set3_p2": 0
    }

def partido_con_jugadores(p1, p2):
    return {
        "pareja_1": p1,
        "pareja_2": p2,
        "lugar": "",
        "fecha": "",
        "hora": "18:00",
        "set1_p1": 0, "set1_p2": 0,
        "set2_p1": 0, "set2_p2": 0,
        "set3_p1": 0, "set3_p2": 0
    }



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
            "jornadas": [
                {"numero": i + 1, "partidos": []}
                for i in range(7)
            ],
            "partidos_borrador": [],
            "locations": LOCATIONS_INICIALES.copy()
        }
        save_data(data)
        return data

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    # Asegurar jugadores
    if "jugadores" not in data:
        data["jugadores"] = []

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
    if "jornadas" not in data:
        data["jornadas"] = [{"numero": i + 1, "partidos": []} for i in range(7)]

    # Asegurar borrador
    if "partidos_borrador" not in data:
        data["partidos_borrador"] = []

    # Asegurar locations
    if "locations" not in data or len(data["locations"]) == 0:
        data["locations"] = LOCATIONS_INICIALES.copy()

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
    ["Jornadas", "Ranking", "Locations", "Import / Export"] )





# ----------------------------
# JORNADAS (PASO 2: GRID + AUTO-CREACIÓN)
# ----------------------------
if menu == "Jornadas":
    import datetime

    st.header("📅 Jornadas")

    # Asegurar jornadas
    if not data.get("jornadas"):
        data["jornadas"] = [{"numero": i + 1, "partidos": []} for i in range(7)]
        save_data(data)

    jornada_index = st.selectbox(
        "Selecciona una jornada",
        range(len(data["jornadas"])),
        format_func=lambda i: f"Jornada {data['jornadas'][i]['numero']}"
    )

    jornada = data["jornadas"][jornada_index]
    st.subheader(f"🗂 Jornada {jornada['numero']}")
    st.write(f"Partidos: {len(jornada['partidos'])} / 5")

    jugadores = sorted(j["nombre"] for j in data["jugadores"])
    clubs = [loc["club"] for loc in data.get("locations", [])]

    # ✅ Crear 4 partidos AUTOMÁTICAMENTE solo si esta jornada está vacía
    if len(jornada["partidos"]) == 0:
        for _ in range(4):
            jornada["partidos"].append(partido_vacio())
        save_data(data)
        st.rerun()

    # ----------------------------
    # GRID 2x2
    # ----------------------------
    filas = [
        jornada["partidos"][i:i + 2]
        for i in range(0, len(jornada["partidos"]), 2)
    ]

    for fila_idx, fila in enumerate(filas):
        cols = st.columns(2)

        for col_idx, partido in enumerate(fila):
            idx = fila_idx * 2 + col_idx

            with cols[col_idx]:
                with st.container(border=True):
                    st.markdown(f"### 🎾 Partido {idx + 1}")

                    # -------- INFO BÁSICA --------
                    c1, c2, c3 = st.columns(3)

                    # Lugar
                    lugar_opciones = [""] + clubs
                    lugar_val = partido.get("lugar", "")
                    lugar_idx = lugar_opciones.index(lugar_val) if lugar_val in lugar_opciones else 0
                    partido["lugar"] = c1.selectbox(
                        "Lugar",
                        lugar_opciones,
                        index=lugar_idx,
                        key=f"lugar_{jornada_index}_{idx}"
                    )

                    # Fecha
                    try:
                        fecha_val = datetime.date.fromisoformat(partido.get("fecha", ""))
                    except Exception:
                        fecha_val = datetime.date.today()

                    partido["fecha"] = str(
                        c2.date_input("Fecha", fecha_val, key=f"fecha_{jornada_index}_{idx}")
                    )

                    # Hora
                    horas = [f"{h:02d}:{m:02d}" for h in range(8, 23) for m in (0, 30)]
                    hora_val = partido.get("hora", "18:00")
                    hora_idx = horas.index(hora_val) if hora_val in horas else 0
                    partido["hora"] = c3.selectbox(
                        "Hora",
                        horas,
                        index=hora_idx,
                        key=f"hora_{jornada_index}_{idx}"
                    )

                    # -------- PAREJAS (SIN REGLAS EXTRA) --------
                    col_p1, col_p2 = st.columns(2)

                    def get_pair_val(p, pos):
                        return p[pos] if len(p) > pos else ""

                    p1 = partido.get("pareja_1", [])
                    p2 = partido.get("pareja_2", [])

                    opciones = [""] + jugadores

                    with col_p1:
                        st.markdown("**Pareja 1**")

                        der1_val = get_pair_val(p1, 0)
                        der1_idx = opciones.index(der1_val) if der1_val in opciones else 0
                        der1 = st.selectbox("Der", opciones, index=der1_idx, key=f"p1d_{idx}")

                        rev1_val = get_pair_val(p1, 1)
                        rev1_idx = opciones.index(rev1_val) if rev1_val in opciones else 0
                        rev1 = st.selectbox("Rev", opciones, index=rev1_idx, key=f"p1r_{idx}")

                    with col_p2:
                        st.markdown("**Pareja 2**")

                        der2_val = get_pair_val(p2, 0)
                        der2_idx = opciones.index(der2_val) if der2_val in opciones else 0
                        der2 = st.selectbox("Der", opciones, index=der2_idx, key=f"p2d_{idx}")

                        rev2_val = get_pair_val(p2, 1)
                        rev2_idx = opciones.index(rev2_val) if rev2_val in opciones else 0
                        rev2 = st.selectbox("Rev", opciones, index=rev2_idx, key=f"p2r_{idx}")

                    partido["pareja_1"] = [der1, rev1]
                    partido["pareja_2"] = [der2, rev2]

                    # -------- RESULTADOS --------
                    st.markdown("**Resultado**")
                    s1, s2, s3 = st.columns(3)

                    partido["set1_p1"] = s1.number_input(
                        "Set1 P1", 0, 7, partido.get("set1_p1", 0), key=f"s1p1_{idx}"
                    )
                    partido["set1_p2"] = s1.number_input(
                        "Set1 P2", 0, 7, partido.get("set1_p2", 0), key=f"s1p2_{idx}"
                    )

                    partido["set2_p1"] = s2.number_input(
                        "Set2 P1", 0, 7, partido.get("set2_p1", 0), key=f"s2p1_{idx}"
                    )
                    partido["set2_p2"] = s2.number_input(
                        "Set2 P2", 0, 7, partido.get("set2_p2", 0), key=f"s2p2_{idx}"
                    )

                    partido["set3_p1"] = s3.number_input(
                        "Set3 P1", 0, 7, partido.get("set3_p1", 0), key=f"s3p1_{idx}"
                    )
                    partido["set3_p2"] = s3.number_input(
                        "Set3 P2", 0, 7, partido.get("set3_p2", 0), key=f"s3p2_{idx}"
                    )

                    if st.button("Guardar", key=f"save_{jornada_index}_{idx}"):
                        save_data(data)
                        st.success("✅ Guardado")


# ----------------------------
# RANKING
# ----------------------------
elif menu == "Ranking":
    import pandas as pd

    st.header("🏆 Ranking")

    jornadas = data.get("jornadas", [])

    # Inicializar estadísticas
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

    # Recorrer jornadas y partidos
    for jornada in jornadas:
        for p in jornada.get("partidos", []):

            p1 = p.get("pareja_1", [])
            p2 = p.get("pareja_2", [])

            if len(p1) != 2 or len(p2) != 2:
                continue

            s1_p1, s1_p2 = p["set1_p1"], p["set1_p2"]
            s2_p1, s2_p2 = p["set2_p1"], p["set2_p2"]
            s3_p1, s3_p2 = p["set3_p1"], p["set3_p2"]

            set1_jugado = (s1_p1 + s1_p2) > 0
            set2_jugado = (s2_p1 + s2_p2) > 0
            set3_jugado = (s3_p1 + s3_p2) > 0

            if not set1_jugado:
                continue

            sets_p1 = (s1_p1 > s1_p2) + (s2_p1 > s2_p2)
            sets_p2 = (s1_p2 > s1_p1) + (s2_p2 > s2_p1)

            juegos_p1 = s1_p1 + s2_p1 + s3_p1
            juegos_p2 = s1_p2 + s2_p2 + s3_p2

            for j in p1:
                stats[j]["PJ"] += 1
                stats[j]["TSW"] += juegos_p1
                stats[j]["TSL"] += juegos_p2

            for j in p2:
                stats[j]["PJ"] += 1
                stats[j]["TSW"] += juegos_p2
                stats[j]["TSL"] += juegos_p1

            # Puntuación
            if set3_jugado:
                if s3_p1 > s3_p2:
                    ganadores, perdedores = p1, p2
                else:
                    ganadores, perdedores = p2, p1

                for j in ganadores:
                    stats[j]["PG"] += 1
                    stats[j]["Pts"] += 3
                for j in perdedores:
                    stats[j]["PP"] += 1
                    stats[j]["Pts"] += 1

            else:
                if sets_p1 > sets_p2:
                    for j in p1:
                        stats[j]["PG"] += 1
                        stats[j]["Pts"] += 3
                    for j in p2:
                        stats[j]["PP"] += 1
                elif sets_p2 > sets_p1:
                    for j in p2:
                        stats[j]["PG"] += 1
                        stats[j]["Pts"] += 3
                    for j in p1:
                        stats[j]["PP"] += 1
                else:
                    for j in p1 + p2:
                        stats[j]["Pts"] += 1

    # Construir DataFrame
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

    # Iconos TOP 3
    def nombre_con_icono(row):
        if row["RK"] == 1:
            return f"🥇 {row['Jugador']}"
        elif row["RK"] == 2:
            return f"🥈 {row['Jugador']}"
        elif row["RK"] == 3:
            return f"🥉 {row['Jugador']}"
        return row["Jugador"]

    df["Jugador"] = df.apply(nombre_con_icono, axis=1)

    # Estilo solo en el nombre
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

    jugador_sel = st.selectbox("Selecciona un jugador", nombres_limpios)
    fila = df[df["Jugador"].str.contains(jugador_sel, regex=False)].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Puntos", fila["Pts"])
    c2.metric("Partidos jugados", fila["PJ"])
    c3.metric("Diferencia juegos", fila["Dif"])

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


# ----------------------------
# IMPORT / EXPORT
# ----------------------------
elif menu == "Import / Export":
    st.header("🔄 Importar / Exportar Jornadas")

    st.markdown(
        """
        Este apartado sirve para **guardar una copia de seguridad** de las jornadas
        o **restaurarlas más adelante**.

        ✅ Incluye solo **jornadas y partidos**  
        ❌ No modifica jugadores ni locations
        """
    )

    # ----------------------------
    # EXPORTAR JORNADAS
    # ----------------------------
    st.markdown("### 📤 Exportar jornadas")

    export_data = {
        "jornadas": data.get("jornadas", [])
    }

    export_json = json.dumps(export_data, indent=4, ensure_ascii=False)

    st.download_button(
        label="⬇️ Descargar backup de jornadas",
        data=export_json,
        file_name="padel_jornadas_backup.json",
        mime="application/json"
    )

    st.markdown("---")

    # ----------------------------
    # IMPORTAR JORNADAS
    # ----------------------------
    st.markdown("### 📥 Importar jornadas")

    uploaded_file = st.file_uploader(
        "Selecciona un archivo de backup (.json)",
        type="json"
    )

    if uploaded_file is not None:
        try:
            imported_data = json.load(uploaded_file)

            if "jornadas" not in imported_data:
                st.error("❌ El archivo no contiene jornadas válidas")
            else:
                st.warning(
                    "⚠️ Esta acción sobrescribirá las jornadas actuales."
                )

                if st.button("✅ Importar y reemplazar jornadas"):
                    data["jornadas"] = imported_data["jornadas"]
                    save_data(data)
                    st.success("✅ Jornadas importadas correctamente")
                    st.rerun()

        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")


