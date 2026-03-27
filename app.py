import streamlit as st
import simpy
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Simulación Profesional de Sistemas", layout="wide")

class SistemaProduccion:
    def __init__(self, env, num_maquinas, tiempo_proceso, variabilidad):
        self.env = env
        self.maquina = simpy.Resource(env, num_maquinas)
        self.tiempo_proceso = tiempo_proceso
        self.variabilidad = variabilidad
        self.datos = []

    def procesar(self, pieza_id):
        llegada = self.env.now
        
        with self.maquina.request() as requerimiento:
            yield requerimiento
            espera = self.env.now - llegada
            
            # Tiempo de procesamiento con distribución normal (evitando negativos)
            duracion = max(0.1, random.normalvariate(self.tiempo_proceso, self.variabilidad))
            yield self.env.timeout(duracion)
            
            self.datos.append({
                'Pieza': pieza_id,
                'Llegada': llegada,
                'Espera': espera,
                'Salida': self.env.now,
                'Utilizacion': (duracion / self.env.now) * 100
            })

def generador_piezas(env, sistema, intervalo_llegada):
    pieza_id = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / intervalo_llegada))
        pieza_id += 1
        env.process(sistema.procesar(pieza_id))

# --- INTERFAZ STREAMLIT ---
st.title("🏭 Simulación Avanzada de Planta Industrial")
st.markdown("### Optimización de Procesos y Análisis de Cuellos de Botella")

with st.sidebar:
    st.header("Parámetros del Sistema")
    n_maquinas = st.slider("Número de Estaciones (Servidores)", 1, 10, 2)
    t_llegada = st.number_input("Intervalo medio de llegada (min)", value=5.0)
    t_proceso = st.number_input("Tiempo de proceso medio (min)", value=8.0)
    sigma = st.number_input("Desviación estándar (Variabilidad)", value=2.0)
    tiempo_sim = st.number_input("Tiempo total de simulación (min)", value=480)

if st.button("Ejecutar Simulación"):
    # Configuración del entorno SimPy
    env = simpy.Environment()
    sistema = SistemaProduccion(env, n_maquinas, t_proceso, sigma)
    env.process(generador_piezas(env, sistema, t_llegada))
    env.run(until=tiempo_sim)

    # Procesamiento de resultados
    df = pd.DataFrame(sistema.datos)

    # --- MÉTRICAS CLAVE ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Procesado", f"{len(df)} piezas")
    col2.metric("Espera Promedio", f"{round(df['Espera'].mean(), 2)} min")
    col3.metric("Eficiencia del Sistema", f"{round((df['Salida'].max() / tiempo_sim)*100, 1)}%")

    # --- GRÁFICOS PROFESIONALES ---
    st.subheader("📊 Análisis de Rendimiento")
    
    # Histograma de Tiempos de Espera
    fig_hist = px.histogram(df, x="Espera", title="Distribución de Tiempos de Espera (Cola)",
                           labels={'Espera': 'Minutos en espera'}, color_discrete_sequence=['#00CC96'])
    st.plotly_chart(fig_hist, use_container_width=True)

    # Gráfico de Dispersión: Tiempo en el sistema
    fig_scatter = px.scatter(df, x="Llegada", y="Espera", size="Espera", 
                            title="Evolución de la Cola en el Tiempo",
                            color="Espera", color_continuous_scale="Viridis")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.success("Simulación completada con éxito. Listo para despliegue.")
