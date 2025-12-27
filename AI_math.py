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
    with c2:
        if st.button("Tam giac"): add_s("\\Delta ")
        if st.button("Goc"): add_s("\\angle ")
    with c3:
        if st.button("Song song"): add_s(" \\parallel ")
        if st.button("Vuong goc"): add_s(" \\perp ")
    with c4:
        if st.button("Sigma"): add_s("\\Sigma ")
        if st.button("Vo cuc"): add_s("\\infty")

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
            ax.plot(x_plot, y_plot, color='blue')
            ax.axhline(0, color='black', lw=1); ax.axvline(0, color='black', lw=1)
            st.pyplot(fig)
        except: st.write("Loi cu phap!")

elif loai_hinh == "Toan hinh hoc":
    st.subheader("📐 Bang ve GeoGebra Classic")
    # Nhung iframe tuong tac
    components.iframe("https://www.geogebra.org/classic", height=600)
    st.info("💡 Copy lenh trong o xam o duoi cung roi dan vao Input (+) cua GeoGebra.")

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
                        1. Giai chi tiet (Viet khong dau).
                        2. BAT BUOC: Cuoi loi giai phai co muc '### LENH VE GEO'.
                        3. QUY TAC LENH (Dung tieng Anh cho Geogebra):
                           - Diem: A=(0,5); B=(-3,0); C=(4,0)
                           - Tam giac: Polygon(A,B,C)
                           - Duong cao AH: h=PerpendicularLine(A, Line(B,C)); H=Intersect(h, Line(B,C))
                           - Duong tron noi tiep: Incircle(A,B,C)
                           - Duong tron ngoai tiep: Circle(A,B,C)
                           - Trung diem: Midpoint(A,B)
                        4. NEU DE KHONG NOI GI: Luon ve tam giac thuong (A=(0,5); B=(-3,0); C=(4,0))."""},
                        {"role": "user", "content": f"De: {user_input}. KQ: {wolf_res}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                st.success("Xong!")
                # Tách phần lệnh vẽ ra để b dễ nhìn
                full_res = chat.choices[0].message.content
                if "### LENH VE GEO" in full_res:
                    loi_giai, lenh_ve = full_res.split("### LENH VE GEO")
                    st.markdown(loi_giai)
                    st.code(lenh_ve.strip(), language="javascript")
                else:
                    st.markdown(full_res)
            except Exception as e: st.error(f"Loi: {e}")
