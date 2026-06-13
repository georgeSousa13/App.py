import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import hashlib
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configuração da página
st.set_page_config(page_title="Correndo Com o Rei", page_icon="👑", layout="wide")

# Função simples para criptografar senhas
def gerar_hash(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

# Banco de dados na memória do sistema
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "rei": {"nome": "O Rei (Treinador)", "senha": gerar_hash("rei123"), "tipo": "treinador"},
        "carlos": {"nome": "Carlos Silva", "senha": gerar_hash("carlos123"), "tipo": "atleta", "idade": 30},
        "ana": {"nome": "Ana Costa", "senha": gerar_hash("ana123"), "tipo": "atleta", "idade": 25}
    }

if "treinos" not in st.session_state:
    st.session_state.treinos = [
        {
            "id": 1, "usuario": "carlos", "atleta": "Carlos Silva", "idade": 30, "data": "2026-06-10", 
            "distancia": 8.0, "tempo": "00:44:00", "fc_media": 155, "copos_agua": 6, "status": "Respondido",
            "feedback": "Excelente controle de FC na zona 3. Ajuste para 8 copos de água nos dias mais quentes."
        }
    ]

if "planilhas" not in st.session_state:
    st.session_state.planilhas = {
        "carlos": "Segunda: 5km Leve | Quarta: Tiros de 400m (6x) | Sexta: 8km Ritmo de Prova",
        "ana": "Terça: Trote 6km | Quinta: 10km Ritmo Confortável | Sábado: Longo de 14km"
    }

# Funções esportivas auxiliares
def calcular_pace(tempo_str, distancia):
    try:
        h, m, s = map(int, tempo_str.split(':'))
        total_minutos = (h * 60) + m + (s / 60)
        pace_decimal = total_minutos / distancia
        pace_min = int(pace_decimal)
        pace_seg = int((pace_decimal - pace_min) * 60)
        return pace_decimal, f"{pace_min}:{pace_seg:02d}"
    except:
        return 0, "0:00"

def classificar_fc(fc_media, idade):
    fc_max = 220 - idade
    pct = (fc_media / fc_max) * 100
    if pct < 60: return "Z1 - Recuperação (Leve)", "🔵", pct
    elif pct < 70: return "Z2 - Resistência (Gordura)", "🟢", pct
    elif pct < 80: return "Z3 - Cardio (Aeróbico)", "🟡", pct
    elif pct < 90: return "Z4 - Limiar Limite (Intenso)", "🟠", pct
    else: return "Z5 - Esforço Máximo (Anaeróbico)", "🔴", pct

def classificar_pace(pace_decimal):
    if pace_decimal < 4.0: return "Ritmo de Velocidade / Tiro 🏎️"
    elif pace_decimal < 5.0: return "Tempo Run / Ritmo de Prova ⚡"
    elif pace_decimal < 6.0: return "Rodagem Confortável 🏃"
    else: return "Regenerativo / Trote Lento 🐢"

def obter_status_agua(copos):
    if copos < 5: return "Desidratado", "🔴"
    elif copos < 8: return "Hidratação Moderada", "🟡"
    else: return "Meta de Hidratação Batida!", "🟢"

# Função para Gerar PDF
def gerar_pdf_feedback(atleta, data, distancia, pace, fc, feedback):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 22)
    p.drawString(100, 750, "👑 CORRENDO COM O REI 👑")
    p.setFont("Helvetica", 14)
    p.drawString(100, 720, f"Relatório de Performance - {data}")
    p.line(100, 705, 500, 705)
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 670, f"Atleta: {atleta}")
    p.setFont("Helvetica", 12)
    p.drawString(100, 650, f"Distância: {distancia} km")
    p.drawString(100, 630, f"Ritmo Médio (Pace): {pace} /km")
    p.drawString(100, 610, f"Frequência Cardíaca: {fc} BPM")
    
    p.line(100, 590, 500, 590)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 560, "💬 Feedback Real:")
    p.setFont("Helvetica", 12)
    
    textobject = p.beginText(100, 530)
    textobject.setWordSpace(1)
    textobject.textLines(feedback)
    p.drawText(textobject)
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- SISTEMA DE LOGOUT ---
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_atual = None

if st.session_state.logado:
    st.sidebar.write(f"Conectado como: **{st.session_state.usuarios[st.session_state.usuario_atual]['nome']}**")
    if st.sidebar.button("Sair / Logout 🚪"):
        st.session_state.logado = False
        st.session_state.usuario_atual = None
        st.rerun()

# --- TELA DE LOGIN / CADASTRO ---
if not st.session_state.logado:
    st.title("👑 Correndo Com o Rei")
    st.subheader("Faça login para acessar suas planilhas e treinos")
    
    aba_login, aba_cadastro = st.tabs(["🔒 Entrar na Conta", "📝 Criar Nova Conta Atleta"])
    
    with aba_login:
        usuario_input = st.text_input("Nome de Usuário (Login):", key="login_user").strip().lower()
        senha_input = st.text_input("Senha:", type="password", key="login_pass")
        
        if st.button("Acessar Painel 🚀"):
            if usuario_input in st.session_state.usuarios:
                if st.session_state.usuarios[usuario_input]["senha"] == gerar_hash(senha_input):
                    st.session_state.logado = True
                    st.session_state.usuario_atual = usuario_input
                    st.success("Acesso autorizado!")
                    st.rerun()
                else: st.error("Senha incorreta.")
            else: st.error("Usuário não encontrado.")
                
    with aba_cadastro:
        novo_user = st.text_input("Crie um Usuário (Sem espaços):").strip().lower()
        novo_nome = st.text_input("Seu Nome Completo:")
        nova_idade = st.number_input("Sua Idade:", min_value=10, max_value=99, value=30)
        nova_senha = st.text_input("Crie uma Senha:", type="password")
        
        if st.button("Cadastrar Novo Perfil"):
            if novo_user and novo_nome and nova_senha:
                if novo_user in st.session_state.usuarios: st.error("Este usuário já existe.")
                else:
                    st.session_state.usuarios[novo_user] = {"nome": novo_nome, "senha": gerar_hash(nova_senha), "tipo": "atleta", "idade": nova_idade}
                    st.session_state.planilhas[novo_user] = "Nenhuma planilha cadastrada pelo Rei ainda."
                    st.success(f"Conta criada! Faça o login.")
            else: st.error("Preencha todos os campos.")

# --- CONTEÚDO DO APLICATIVO LOGADO ---
else:
    user_info = st.session_state.usuarios[st.session_state.usuario_atual]
    
    # ----------------- VISÃO DO ATLETA -----------------
    if user_info["tipo"] == "atleta":
        st.title(f"🏃‍♂️ Painel do Atleta: {user_info['nome']}")
        
        menu_atleta = st.tabs(["📅 Minha Planilha Semanal", "📩 Enviar Corrida", "📊 Meu Histórico & Feedbacks"])
        
        with menu_atleta:
            st.markdown("### 📋 Treinos Prescritos Pelo Rei")
            planilha_atual = st.session_state.planilhas.get(st.session_state.usuario_atual, "Sem planilha ativa.")
            st.info(planilha_atual)
            
        with menu_atleta:
            st.markdown("### Registrar Treino de Hoje")
            with st.form("form_treino_atleta", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    distancia = st.number_input("Distância (km):", min_value=0.1, step=0.1, value=5.0)
                    tempo = st.text_input("Tempo total (HH:MM:SS):", value="00:30:00")
                with col2:
                    fc_media = st.number_input("Frequência Cardíaca Média (BPM):", min_value=40, value=140)
                    copos_agua = st.slider("Copos de Água hoje:", 0, 15, 6)
                    
                if st.form_submit_button("Enviar para Análise do Rei 👑"):
                    novo_treino = {
                        "id": len(st.session_state.treinos) + 1, "usuario": st.session_state.usuario_atual,
                        "atleta": user_info["nome"], "idade": user_info["idade"], "data": str(datetime.date.today()),
                        "distancia": distancia, "tempo": tempo, "fc_media": fc_media, "copos_agua": copos_agua,
                        "status": "Pendente", "feedback": ""
                    }
                    st.session_state.treinos.append(novo_treino)
                    st.success("Corrida enviada com sucesso!")
                    
        with menu_atleta:
            st.markdown("### Seus Registros & Ajustes")
            meus_treinos = [t for t in st.session_state.treinos if t["usuario"] == st.session_state.usuario_atual]
            
            if meus_treinos:
                for t in meus_treinos:
                    pace_dec, pace_f = calcular_pace(t["tempo"], t["distancia"])
                    zona_fc, emoji_fc, pct_fc = classificar_fc(t["fc_media"], t["idade"])
                    zona_p = classificar_pace(pace_dec)
                    txt_agua, emoji_agua = obter_status_agua(t["copos_agua"])
                    
                    with st.expander(f"Corrida de {t['distancia']}km em {t['data']} — Status: {t['status']}"):
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Ritmo (Pace)", f"{pace_f} /km", zona_p)
                        c2.metric("Frequência Cardíaca", f"{t['fc_media']} BPM", f"{pct_fc:.1f}% da Max")
                        c3.metric("Copos de Água", f"{t['copos_agua']} copos", f"{emoji_agua} {txt_agua}")
                        
                        if t["status"] == "Respondido":
                            st.info(f"💬 **Feedback do Rei:** {t['feedback']}")
                            
                            # Botão do PDF
                            pdf_data = gerar_pdf_feedback(t['atleta'], t['data'], t['distancia'], pace_f, t['fc_media'], t['feedback'])
                            st.download_button(label="📥 Baixar Feedback em PDF", data=pdf_data, file_name=f"Feedback_Rei_{t['data']}.pdf", mime="application/pdf")
                            
                            # Link Pronto para Instagram Stories
