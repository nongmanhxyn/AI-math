import streamlit as st
from groq import Groq
import wolframalpha
import matplotlib.pyplot as plt
import numpy as np
import streamlit.components.v1 as components

# --- API KEY ---
GROQ_KEY = st.secrets["GROQ_KEY"]
WOLFRAM_ID = st.secrets["WOLFRAM_ID"]

client = Groq(api_key=GROQ_KEY)
wolf_client = wolframalpha.Client(WOLFRAM_ID)

st.set_page_config(page_title="AI Toan Dien", layout="wide")
st.title("AI GIAI TOAN & VE HINH (KHONG DAU)")

# --- 1. BANG KY HIEU ---
if 'input_text' not in st.session_state: st.session_state.input_text = ""
def add_s(s): st.session_state.input_text += s

with st.expander("MO BANG KY HIEU TOAN HOC"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Phan so"): add_s("\\frac{}{}")
        if st.button("Can"): add_s("\\sqrt{}")
        if st.button("Mu 2"): add_s("**2")
    with c2:
        if st.button("Tam giac"): add_s("\\Delta ")
        if st.button("Goc"): add_s("\\angle ")
        if st.button("Vong cung"): add_s("\\widehat{}")
    with c3:
        if st.button("Song song"): add_s(" \\parallel ")
        if st.button("Vuong goc"): add_s(" \\perp ")
        if st.button("Trung"): add_s(" \\equiv ")
    with c4:
        if st.button("Sigma"): add_s("\\Sigma ")
        if st.button("Tich phan"): add_s("\\int ")
        if st.button("Vo cuc"): add_s("\\infty")

user_input = st.text_area("Nhap de bai:", value=st.session_state.input_text, height=100)
st.session_state.input_text = user_input

# --- 2. KHU VUC VE HINH ---
st.header("Khu vuc ve hinh")
loai_hinh = st.radio("Chon loai hinh muon ve:", ["Do thi ham so", "Bieu do (Cot/Quat)", "Toan hinh hoc"])

if loai_hinh == "Do thi ham so":
    ham = st.text_input("Nhap ham (VD: y=x**2, np.sin(x)):")
    if ham:
        try:
            ham_clean = ham.split('=')[-1].strip()
            x_plot = np.linspace(-20, 20, 1000)
            y_plot = eval(ham_clean.replace('^', '**'), {"np": np, "x": x_plot})
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.plot(x_plot, y_plot, color='blue', linewidth=2)
            ax.set_xlim(-10, 10); ax.set_ylim(-10, 10); ax.set_aspect('equal')
            ax.axhline(y=0, color='black', linewidth=1.2); ax.axvline(x=0, color='black', linewidth=1.2)
            ax.grid(True, linestyle=':', alpha=0.6)
            c_l, c_m, c_r = st.columns([1, 2, 1])
            with c_m: st.pyplot(fig)
        except Exception as e: st.write(f"Loi: {e}")

elif loai_hinh == "Bieu do (Cot/Quat)":
    data_raw = st.text_input("Nhap so lieu (VD: 10, 20, 30):")
    if data_raw:
        data = [float(i) for i in data_raw.split(',')]
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.bar(range(len(data)), data)
        c_l, c_m, c_r = st.columns([1, 2, 1])
        with c_m: st.pyplot(fig)

elif loai_hinh == "Toan hinh hoc":
    st.subheader("Bang ve GeoGebra Classic")
    components.iframe("https://www.geogebra.org/classic", height=500)
    st.info("💡 Copy lenh ben duoi dan vao o Input cua GeoGebra")

# --- 3. NUT GIAI ---
if st.button("GIAI NGAY"):
    if user_input:
        with st.spinner("AI dang giai..."):
            try:
                res = wolf_client.query(user_input)
                wolf_res = next(res.results).text
            except: wolf_res = "Khong co du lieu."
            try:
                chat = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": """Ban la chuyen gia toan hoc. 
                        NHIEM VU:
                        1. Giai chi tiet bang tieng Viet KHONG DAU.
                        2. BAT BUOC: Neu la bai hinh hoc, phai co muc '### LENH VE GEO' chua code GGBScript.
                        3. Trong code ve, phai co ky hieu goc vuong neu co (dung lenh 'Angle(A, B, C)'), ky hieu bang nhau (dung 'SetDecoration').
                        VD code: A=(0,0); B=(4,0); C=(0,3); Polygon(A,B,C)"""},
                        {"role": "user", "content": f"De: {user_input}. KQ: {wolf_res}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                st.success("Xong!")
                st.markdown(chat.choices[0].message.content)
            except Exception as e: st.error(f"Loi: {e}")
