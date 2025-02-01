import streamlit as st

st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.logo("https://www.streamlit.io/images/brand/streamlit-mark-color.png")
pages = {
    "Home": [
        st.Page("Welcome.py", title="Welcome",icon="🏠"),
    ],
    "Your account": [
        st.Page("create_account.py", title="Create your account"),
        st.Page("manage_account.py", title="Manage your account"),
        st.Page("EldoGaming.py", title="EldoGaming"),
    ]
}

pg = st.navigation(pages)
pg.run()