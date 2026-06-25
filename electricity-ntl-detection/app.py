import streamlit as st
import pandas as pd
import joblib

# ---------------- LOGIN SESSION ---------------- #

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN PAGE ---------------- #

def login():

    st.title("🔐 Electricity Board Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login Successful")
            st.rerun()

        elif username == "officer" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login Successful")
            st.rerun()

        else:
            st.error("Invalid Username or Password")


# ---------------- MAIN APP ---------------- #

def main_app():

    # Load model files
    model = joblib.load("model/model.pkl")
    scaler = joblib.load("model/scaler.pkl")
    metrics = joblib.load("model/metrics.pkl")

    df = pd.read_csv("dataset/electricity_data.csv")

    st.set_page_config(page_title="Electricity Theft Detection", layout="wide")

    st.title("⚡ Electricity Theft Detection System")

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # -------- VELLORE DATA -------- #

    vellore_data = {

    "Vellore":[
    "Poigai","Seduvalai","Ariyur","Munjurpattu",
    "Genganallore","Adukkamparai","Edayansathu"
    ],

    "Katpadi":[
    "Ammundi","Alanganeri","Angarankuppam","Annangudi",
    "Arumbakkam","Balekuppam","Dharapadavedu"
    ],

    "Anaicut":[
    "Odugathur","Pallikonda","Ussoor","Pennathur",
    "Veppankuppam","Sevoor","Agaram"
    ],

    "Gudiyatham":[
    "Valathur","Paradarami","Melmuttukur","Kallapadi",
    "Mordhana","Perumbadi","Erthangal"
    ],

    "Pernambut":[
    "Melpatti","Aravatla","Devalapuram","Erukkampattu",
    "Kollapalli","Sathambakkam","Morappanthangal"
    ],

    "K. V. Kuppam":[
    "Vaduganthangal","Kilvaithinankuppam","Kothamangalam",
    "Kavanur","Serpadi","Melalathur","Kilalathur"
    ]
    }

    # Sidebar menu
    page = st.sidebar.selectbox(
        "Menu",
        ["Model Analysis","District Detection"]
    )

    # ================= MODEL ANALYSIS ================= #

    if page == "Model Analysis":

        st.header("📊 Model Performance")

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("Accuracy", round(metrics["accuracy"],2))
        col2.metric("Precision", round(metrics["precision"],2))
        col3.metric("Recall", round(metrics["recall"],2))
        col4.metric("F1 Score", round(metrics["f1"],2))

        st.subheader("Confusion Matrix")

        cm = pd.DataFrame(
            metrics["confusion_matrix"],
            columns=["Predicted Normal","Predicted Fraud"],
            index=["Actual Normal","Actual Fraud"]
        )

        st.dataframe(cm)

    # ================= DISTRICT DETECTION ================= #

    if page == "District Detection":

        st.header("🔎 Electricity Theft Detection")

        # Session state
        if "district_checked" not in st.session_state:
            st.session_state.district_checked = False
        if "town_checked" not in st.session_state:
            st.session_state.town_checked = False
        if "area_checked" not in st.session_state:
            st.session_state.area_checked = False
        if "fraud_data" not in st.session_state:
            st.session_state.fraud_data = pd.DataFrame()

        # -------- DISTRICT -------- #

        district = st.selectbox("Select District", ["Vellore"])
        district_data = df[df["District"] == district]

        if st.button("Check District"):

            fraud_count = district_data["NTL_Label"].sum()
            st.session_state.district_checked = True

            if fraud_count == 0:
                st.success("✅ No Fraud Detected in District")
            else:
                st.error(f"⚠ Fraud Detected: {fraud_count} consumers")

        # -------- TOWN -------- #

        if st.session_state.district_checked:

            town = st.selectbox("Select Town", list(vellore_data.keys()))
            areas = vellore_data[town]

            town_data = df[df["Area"].isin(areas)]

            if st.button("Check Town"):

                town_fraud = town_data["NTL_Label"].sum()
                st.session_state.town_checked = True

                if town_fraud == 0:
                    st.success("✅ No Fraud in Town")
                else:
                    st.error(f"⚠ Fraud Found: {town_fraud}")

        # -------- AREA -------- #

        if st.session_state.town_checked:

            area = st.selectbox("Select Area", areas)
            area_data = df[df["Area"] == area]

            if st.button("Check Area"):

                fraud_data = area_data[area_data["NTL_Label"] == 1]
                st.session_state.area_checked = True
                st.session_state.fraud_data = fraud_data

                if fraud_data.empty:
                    st.success("✅ No Fraud in this Area")

                else:
                    st.error(f"⚠ Fraud Found: {len(fraud_data)} consumers")

                    st.markdown("### 🚨 Fraud Customers")

                    # ✅ SHOW ONLY CONSUMER IDs (IMAGE 1)
                    st.dataframe(fraud_data[["Consumer_ID"]])

                    csv = fraud_data.to_csv(index=False)
                    st.download_button(
                        "⬇ Download Fraud List",
                        csv,
                        "fraud_customers.csv",
                        "text/csv"
                    )

        # -------- CHECK CONSUMER DETAILS -------- #

        if st.session_state.area_checked:

            fraud_data = st.session_state.fraud_data

            if not fraud_data.empty:

                st.markdown("---")
                st.subheader("🔍 Check Fraud Consumer Details")

                selected_consumer = st.selectbox(
                    "Select Consumer ID",
                    fraud_data["Consumer_ID"]
                )

                if selected_consumer:

                    consumer_details = fraud_data[
                        fraud_data["Consumer_ID"] == selected_consumer
                    ]

                    # ✅ FULL DETAILS (IMAGE 2)
                    st.dataframe(consumer_details[[
                        "Consumer_ID",
                        "Monthly_Consumption",
                        "Deviation",
                        "Sudden_Drop",
                        "Area_Mismatch",
                        "Feeder_Mismatch"
                    ]])

        # -------- OPTIONAL MODEL PREDICTION -------- #

        if st.session_state.area_checked:

            st.markdown("---")
            st.subheader("🤖 Model Prediction (Optional)")

            consumer = st.selectbox("Select Any Consumer", df["Consumer_ID"])

            data = df[df["Consumer_ID"] == consumer]

            features = data[[
                "Monthly_Consumption",
                "Avg_6_Months",
                "Area_Avg",
                "Feeder_Avg",
                "Deviation",
                "Sudden_Drop",
                "Area_Mismatch",
                "Feeder_Mismatch"
            ]]

            features = features.replace({"YES":1,"NO":0})

            scaled = scaler.transform(features)

            prediction = model.predict(scaled)

            if prediction[0] == 1:
                st.error("⚠ Theft Detected")
            else:
                st.success("✔ Normal Consumer")


# ---------------- RUN APP ---------------- #

if st.session_state.logged_in:
    main_app()
else:
    login()