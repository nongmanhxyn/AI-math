import streamlit as st
from groq import Groq
import wolframalpha
import matplotlib.pyplot as plt
import numpy as np
import streamlit.components.v1 as components

# --- 0. CAU HINH API KEY ---
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    WOLFRAM_ID = st.secrets["WOLFRAM_ID"]
except:
    st.error("Thieu API Key trong Secrets!")
    st.stop()

client = Groq(api_key=GROQ_KEY)
wolf_client = wolframalpha.Client(WOLFRAM_ID)

st.set_page_config(page_title="AI Toan Dien", layout="wide")
st.title("🚀 AI GIAI TOAN & VE HINH CHUAN")

# --- 1. BANG KY HIEU ---
if 'input_text' not in st.session_state: st.session_state.input_text = ""
def add_s(s): st.session_state.input_text += s

with st.expander("⌨️ MO BANG KY HIEU TOAN HOC"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Phan so"): add_s("\\frac{}{}")
        if st.button("Can"): add_s("\\sqrt{}")
        if st.button("Mu 2"): add_s("**2")
    with c2:
        if st.button("Tam giac"): add_s("\\Delta ")
        if st.button("Goc"): add_s("\\angle ")
    with c3:
        if st.button("Song song"): add_s(" \\parallel ")
        if st.button("Vuong goc"): add_s(" \\perp ")
    with c4:
        if st.button("Sigma"): add_s("\\Sigma ")
        if st.button("Tich phan"): add_s("\\int ")

user_input = st.text_area("📝 Nhap de bai:", value=st.session_state.input_text, height=100)
st.session_state.input_text = user_input

# --- 2. KHU VUC VE HINH ---
st.header("🎨 Khu vuc ve hinh")
loai_hinh = st.radio("Chon loai hinh:", ["Do thi ham so", "Toan hinh hoc"])

if loai_hinh == "Do thi ham so":
    ham = st.text_input("Nhap ham (VD: y=x**2):")
    if ham:
        try:
            ham_clean = ham.split('=')[-1].strip()
            x_plot = np.linspace(-10, 10, 400)
            y_plot = eval(ham_clean.replace('^', '**'), {"np": np, "x": x_plot})
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.plot(x_plot, y_plot)
            ax.axhline(0, color='black'); ax.axvline(0, color='black')
            st.pyplot(fig)
        except: st.write("Loi cu phap!")

elif loai_hinh == "Toan hinh hoc":
    st.subheader("📐 Bang ve GeoGebra Classic")
    components.iframe("https://www.geogebra.org/classic", height=600)
    st.info("💡 Copy code trong o mau xam phia duoi dan vao o Input (+) cua GeoGebra.")

# --- 3. NUT GIAI ---
if st.button("🔥 GIAI NGAY"):
    if user_input:
        with st.spinner("AI dang tinh..."):
            try:
                res = wolf_client.query(user_input)
                wolf_res = next(res.results).text
            except: wolf_res = "Khong co so lieu."
            
            try:
                chat = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": """Ban la chuyen gia hinh hoc Geogebra. 
                        NHIEM VU:
                        1. Giai chi tiet bang tieng Viet khong dau.
                        2. BAT BUOC: Cuoi cung phai co muc '### LENH VE GEO'.
                        3. TRONG MUC NAY, CHI DUOC VIET CODE, KHONG VIET CHU. 
                        4. QUY TAC VE:
                           - Luon dat A=(0,5); B=(-3,0); C=(4,0) de tam giac khong bi dac biet (neu de ko yeu cau).
                           - Dung lenh quan he: PerpendicularLine, Midpoint, Circle, Intersect.
                           - VD: A=(0,5); B=(-3,0); C=(4,0); Polygon(A,B,C); h=PerpendicularLine(A, Line(B,C))"""},
                        {"role": "user", "content": f"De: {user_input}. KQ: {wolf_res}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                st.success("Xong!")
                st.markdown(chat.choices[0].message.content)
            except Exception as e: st.error(f"Loi: {e}")
