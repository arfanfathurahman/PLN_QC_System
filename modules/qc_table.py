import streamlit as st
import pandas as pd


def qc_table(title, items):

    st.subheader(title)

    rows = []

    for i, item in enumerate(items, start=1):

        col1, col2, col3, col4, col5 = st.columns([0.5,4,2,2,3])

        with col1:
            st.write(i)

        with col2:
            st.write(item["item"])

        with col3:
            st.write(item["standar"])

        with col4:
            hasil = st.selectbox(
                "",
                ["✅ Sesuai", "❌ Tidak Sesuai"],
                key=f"{title}_{i}"
            )

        with col5:
            ket = st.text_input(
                "",
                key=f"{title}_ket_{i}"
            )

        rows.append({
            "No": i,
            "Item": item["item"],
            "Standar": item["standar"],
            "Hasil": hasil,
            "Keterangan": ket
        })

    return pd.DataFrame(rows)