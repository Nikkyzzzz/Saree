import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# ─── Google Sheets Setup ──────────────────────────────────────────────────────
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gspread"], scope)
client = gspread.authorize(creds)

# ─── Load Google Sheet ────────────────────────────────────────────────────────
SPREADSHEET_ID = "1EaN3GaYgg-Z3-WwFe6qh1sZ2nA8sUzMq2Hqs8q2Lvhw"
sheet = client.open_by_key(SPREADSHEET_ID).sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ─── Convert Google Drive Link to Direct Image URL ────────────────────────────
import re

def convert_drive_url(url):
    match = re.search(r'(?:id=|file/d/|/d/)([a-zA-Z0-9_-]+)', str(url))
    if match:
        return f"https://drive.google.com/uc?export=view&id={match.group(1)}"
    return None

# ─── Ensure "Status" Column Exists ────────────────────────────────────────────
if "Status" not in df.columns:
    df["Status"] = ["Available"] * len(df)

# ─── UI ────────────────────────────────────────────────────────────────────────
st.title("👗 Saree Store Inventory")

updated_status = []

for i, row in df.iterrows():
    st.markdown("---")
    cols = st.columns([1.5, 3])

    # Left Column: Photo
    with cols[0]:
        img_url = convert_drive_url(row["Photo"])
        if img_url:
            import requests
            from PIL import Image
            from io import BytesIO

            try:
                response = requests.get(img_url)
                image = Image.open(BytesIO(response.content))
                st.image(image, width=300)
            except Exception as e:
                st.warning("📷 Could not load image")
                st.text(f"{e}")

        else:
            st.warning("No image")

    # Right Column: Info + Checkbox
    with cols[1]:
        st.subheader(f"Saree No: {row['Number']}")
        st.write(f"**Cost Price**: ₹{row['Cost Price']}")
        st.write(f"**Color**: {row['Color']}")
        st.write(f"**Fabric**: {row['Fabric']}")
        sold = st.checkbox("Mark as Sold", key=f"checkbox_{i}", value=(row.get("Status", "") == "Sold"))
        updated_status.append("Sold" if sold else "Available")
        st.write(f"📝 Status: {'Sold' if sold else 'Available'}")

# ─── Update Sheet ─────────────────────────────────────────────────────────────
if st.button("✅ Update Sheet"):
    for idx, status in enumerate(updated_status):
        sheet.update_cell(idx + 2, df.columns.get_loc("Status") + 1 + 1, status)
    st.success("✅ Google Sheet updated! Please refresh the app to see updates.")
