import streamlit as st
from groq import Groq
import wolframalpha
import matplotlib.pyplot as plt
import numpy as np

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
            # Tu dong lay phan sau dau "=" neu b nhap y=...
            ham_clean = ham.split('=')[-1].strip()
            
            x = np.linspace(-10, 10, 400)
            y = eval(ham_clean.replace('^', '**'), {"np": np, "x": x})
            
            # Tao khung hinh vuong de ty le x, y khong bi lech
            fig, ax = plt.subplots(figsize=(7, 7))
            ax.plot(x, y, label=f"y = {ham_clean}", color='blue', linewidth=2)
            
            # Thiet lap truc Oxy chuan
            ax.set_aspect('equal', adjustable='datalim')
            ax.axhline(y=0, color='black', linewidth=1.5) # Truc Ox
            ax.axvline(x=0, color='black', linewidth=1.5) # Truc Oy
            
            # Gioi han khung nhin de b thay duoc vach chia
            ax.set_xlim(-11, 11)
            
            # Them ten truc
            ax.set_xlabel('x', loc='right')
            ax.set_ylabel('y', loc='top', rotation=0)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend()
            
            st.pyplot(fig)
        except Exception as e: 
            st.write(f"Check lai cu phap nhe! Loi: {e}")

elif loai_hinh == "Bieu do (Cot/Quat)":
    kieu = st.selectbox("Chon kieu bieu do:", ["Cot", "Quat (Tron)", "Tranh (Diem)"])
    data_raw = st.text_input("Nhap so lieu (VD: 10, 20, 30):")
    if data_raw:
        data = [float(x) for x in data_raw.split(',')]
        fig, ax = plt.subplots()
        if kieu == "Cot": ax.bar(range(len(data)), data)
        elif kieu == "Quat (Tron)": ax.pie(data, labels=[f"Phan {i+1}" for i in range(len(data))])
        else: ax.scatter(range(len(data)), data)
        st.pyplot(fig)

elif loai_hinh == "Toan hinh hoc":
    st.info("B vao GeoGebra ve cho chuan nhe, hoac xem AI mo ta cach ve o duoi!")

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
                        {"role": "system", "content": "Ban la chuyen gia toan. Giai chi tiet bang tieng Viet KHONG DAU. Neu la hinh hoc hay mo ta chi tiet cach ve va ky hieu. Dung Latex $...$"},
                        {"role": "user", "content": f"De: {user_input}. KQ: {wolf_res}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                st.success("Xong!")
                st.markdown(chat.choices[0].message.content)
            except Exception as e: st.error(f"Loi: {e}")
