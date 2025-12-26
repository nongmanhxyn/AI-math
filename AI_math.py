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
    ham = st.text_input("Nhap ham (VD: x**2, np.sin(x)):")
    if ham:
        try:
            x = np.linspace(-10, 10, 400)
            y = eval(ham.replace('^', '**'), {"np": np, "x": x})
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.grid(True)
            st.pyplot(fig)
        except: st.write("Check lai cu phap np.sin(x) hoac x**2 nhe!")

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
    st.write("AI se mo ta cach ve hinh hoc (Tam giac, Duong tron) o phan loi giai nhe!")

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
                        {"role": "system", "content": "Ban la chuyen gia toan. Giai chi tiet bang tieng Viet KHONG DAU. Dung Latex $...$"},
                        {"role": "user", "content": f"De: {user_input}. KQ: {wolf_res}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                st.success("Xong!")
                st.markdown(chat.choices[0].message.content)
            except Exception as e: st.error(f"Loi: {e}")
