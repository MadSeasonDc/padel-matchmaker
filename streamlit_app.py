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
    [ "Jornadas",  "Ranking", "Locations"]
)


# ----------------------------
# JORNADAS
# ----------------------------
if menu == "Jornadas":
    import datetime

    st.header("📅 Jornadas")

    # Crear jornadas base si no existen
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

    # ✅ Crear 4 partidos por defecto
    if len(jornada["partidos"]) == 0:
        for _ in range(4):
            jornada["partidos"].append({
                "pareja_1": [],
                "pareja_2": [],
                "lugar": "",
                "fecha": "",
                "hora": "18:00",
                "set1_p1": 0, "set1_p2": 0,
                "set2_p1": 0, "set2_p2": 0,
                "set3_p1": 0, "set3_p2": 0
            })
        save_data(data)
        st.rerun()

    # Construir grid 2x2
    filas = [
        jornada["partidos"][i:i+2]
        for i in range(0, len(jornada["partidos"]), 2)
    ]

    for fila_idx, fila in enumerate(filas):
        st.markdown("")  # separación visual
        cols = st.columns(2)

        for col_idx, partido in enumerate(fila):
            idx = fila_idx * 2 + col_idx

            with cols[col_idx]:
                # Marco del partido
                st.markdown(
                    """
                    <div style="
                        border: 2px solid #3a3a3a;
                        border-radius: 12px;
                        padding: 16px;
                        margin-bottom: 20px;
                    ">
                    """,
                    unsafe_allow_html=True
                )

                # Título centrado
                st.markdown(
                    f"<h3 style='text-align:center; margin-top:0;'>🎾 Partido {idx + 1}</h3>",
                    unsafe_allow_html=True
                )

                # Jugadores ya usados en partidos anteriores
                jugadores_usados = set()
                for i in range(idx):
                    jugadores_usados.update(jornada["partidos"][i].get("pareja_1", []))
                    jugadores_usados.update(jornada["partidos"][i].get("pareja_2", []))

                jugadores_disponibles = [j for j in jugadores if j not in jugadores_usados]
                opciones = [""] + jugadores_disponibles

                # Información básica
                c1, c2, c3 = st.columns(3)

                with c1:
                    partido["lugar"] = st.selectbox(
                        "Lugar",
                        [""] + clubs,
                        index=0,
                        key=f"lugar_{jornada_index}_{idx}"
                    )

                with c2:
                    try:
                        fecha_val = datetime.date.fromisoformat(partido.get("fecha", ""))
                    except Exception:
                        fecha_val = datetime.date.today()

                    partido["fecha"] = str(
                        st.date_input(
                            "Fecha",
                            fecha_val,
                            key=f"fecha_{jornada_index}_{idx}"
                        )
                    )

                with c3:
                    horas = [
                        f"{h:02d}:{m:02d}"
                        for h in range(8, 23)
                        for m in (0, 30)
                        if not (h == 22 and m == 30)
                    ]
                    partido["hora"] = st.selectbox(
                        "Hora",
                        horas,
                        index=horas.index(partido.get("hora", "18:00")) if partido.get("hora") in horas else 0,
                        key=f"hora_{jornada_index}_{idx}"
                    )

                # Parejas Der / Rev
                col_p1, col_p2 = st.columns(2)

                with col_p1:
                    st.markdown("**Pareja 1**")
                    der_p1 = st.selectbox("Der", opciones, key=f"p1_der_{idx}")
                    rev_p1 = st.selectbox(
                        "Rev",
                        [""] + [j for j in jugadores_disponibles if j != der_p1],
                        key=f"p1_rev_{idx}"
                    )

                with col_p2:
                    st.markdown("**Pareja 2**")
                    der_p2 = st.selectbox("Der", opciones, key=f"p2_der_{idx}")
                    rev_p2 = st.selectbox(
                        "Rev",
                        [""] + [j for j in jugadores_disponibles if j != der_p2],
                        key=f"p2_rev_{idx}"
                    )

                partido["pareja_1"] = [der_p1, rev_p1]
                partido["pareja_2"] = [der_p2, rev_p2]

                # Resultado compacto
                st.markdown("**Resultado**")
                r1, r2, r3 = st.columns(3)

                with r1:
                    partido["set1_p1"] = st.number_input("P1", 0, 7, key=f"s1p1_{idx}")
                    partido["set1_p2"] = st.number_input("P2", 0, 7, key=f"s1p2_{idx}")
                with r2:
                    partido["set2_p1"] = st.number_input("P1", 0, 7, key=f"s2p1_{idx}")
                    partido["set2_p2"] = st.number_input("P2", 0, 7, key=f"s2p2_{idx}")
                with r3:
                    partido["set3_p1"] = st.number_input("P1", 0, 7, key=f"s3p1_{idx}")
                    partido["set3_p2"] = st.number_input("P2", 0, 7, key=f"s3p2_{idx}")

                if st.button("Guardar", key=f"save_{idx}"):
                    save_data(data)
                    st.success("✅ Guardado")

                st.markdown("</div>", unsafe_allow_html=True)

    # Botón + centrado SOLO para el 5º partido
    if len(jornada["partidos"]) == 4:
        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("➕ Añadir Partido 5"):
                jornada["partidos"].append({
                    "pareja_1": [],
                    "pareja_2": [],
                    "lugar": "",
                    "fecha": "",
                    "hora": "18:00",
                    "set1_p1": 0, "set1_p2": 0,
                    "set2_p1": 0, "set2_p2": 0,
                    "set3_p1": 0, "set3_p2": 0
                })
                save_data(data)
                st.rerun()

 

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

    # Recorremos jornadas y partidos
    for jornada in jornadas:
        for p in jornada.get("partidos", []):

            p1 = p.get("pareja_1", [])
            p2 = p.get("pareja_2", [])

            if len(p1) != 2 or len(p2) != 2:
                continue

            # Sets
            s1_p1, s1_p2 = p["set1_p1"], p["set1_p2"]
            s2_p1, s2_p2 = p["set2_p1"], p["set2_p2"]
            s3_p1, s3_p2 = p["set3_p1"], p["set3_p2"]

            # ¿Hay set jugado?
            set1_jugado = (s1_p1 + s1_p2) > 0
            set2_jugado = (s2_p1 + s2_p2) > 0
            set3_jugado = (s3_p1 + s3_p2) > 0

            if not set1_jugado:
                continue  # partido no jugado

            # Sets ganados
            sets_p1 = (s1_p1 > s1_p2) + (s2_p1 > s2_p2)
            sets_p2 = (s1_p2 > s1_p1) + (s2_p2 > s2_p1)

            # Juegos totales
            juegos_p1 = s1_p1 + s2_p1 + s3_p1
            juegos_p2 = s1_p2 + s2_p2 + s3_p2

            # Actualizar partidos jugados y juegos
            for j in p1:
                stats[j]["PJ"] += 1
                stats[j]["TSW"] += juegos_p1
                stats[j]["TSL"] += juegos_p2

            for j in p2:
                stats[j]["PJ"] += 1
                stats[j]["TSW"] += juegos_p2
                stats[j]["TSL"] += juegos_p1

            # ----------------------------
            # LÓGICA DE PUNTOS
            # ----------------------------

            if set3_jugado:
                # Partido decidido en 3er set
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
                # NO hay set 3
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
                    # Empate real (1–1 sin set 3)
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

    st.dataframe(df, use_container_width=True, hide_index=True)


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
