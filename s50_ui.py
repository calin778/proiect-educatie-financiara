import streamlit as st

st.set_page_config(page_title="Educatie financiara", page_icon="💰", layout="wide")

pagina_lectii = st.Page("s50_pages/lectii.py", title="Lectii", icon="📚", default=True)
pagina_adauga = st.Page("s50_pages/adauga.py", title="Adauga lectie", icon="➕")
pagina_cautare = st.Page("s50_pages/cautare.py", title="Cautare", icon="🔎")
pagina_profesor = st.Page("s50_pages/profesor.py", title="Profesor AI", icon="🎓")

navigare = st.navigation([pagina_lectii, pagina_adauga, pagina_cautare, pagina_profesor])

navigare.run()
