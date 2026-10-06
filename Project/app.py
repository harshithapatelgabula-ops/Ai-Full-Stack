import streamlit as st
import pandas as pd
import requests
import json
import re

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AI Cricket Team Selector",
    page_icon="🏏",
    layout="wide"
)

# ==========================================================
# MAIN TITLE
# ==========================================================

st.title("🏏 AI Cricket Team Selector")

st.write(
    "Upload a player list and use AI to select the Best Playing XI."
)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("📁 Team Selection")

    # ------------------------------------------------------
    # UPLOAD PLAYER LIST
    # ------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload Player List",
        type=["csv", "xlsx"]
    )

    # ------------------------------------------------------
    # UPLOAD SUCCESS MESSAGE
    # ------------------------------------------------------

    if uploaded_file is not None:

        st.success(
            f"✅ File uploaded successfully:\n"
            f"{uploaded_file.name}"
        )

    st.markdown("---")

    # ------------------------------------------------------
    # CREATE TEAM BUTTON
    # ------------------------------------------------------

    create_team = st.button(
        "🏏 Create Team",
        use_container_width=True
    )


# ==========================================================
# CREATE TEAM WITHOUT FILE
# ==========================================================

if create_team and uploaded_file is None:

    st.error(
        "❌ Please upload a player list file first."
    )

    # Try Again button
    if st.button(
        "🔄 Try Again",
        use_container_width=True
    ):

        st.rerun()


# ==========================================================
# FILE UPLOADED
# ==========================================================

if uploaded_file is not None:

    try:

        # --------------------------------------------------
        # READ CSV
        # --------------------------------------------------

        if uploaded_file.name.lower().endswith(".csv"):

            df = pd.read_csv(uploaded_file)

        # --------------------------------------------------
        # READ EXCEL
        # --------------------------------------------------

        else:

            df = pd.read_excel(uploaded_file)

        # --------------------------------------------------
        # CLEAN COLUMN NAMES
        # --------------------------------------------------

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        # --------------------------------------------------
        # DISPLAY PLAYER LIST
        # --------------------------------------------------

        st.subheader("📊 Uploaded Player List")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.write(
            f"👥 **Total Players:** {len(df)}"
        )

        # ==================================================
        # CREATE TEAM
        # ==================================================

        if create_team:

            # ------------------------------------------------
            # REQUIRED COLUMNS
            # ------------------------------------------------

            required_columns = [
                "Player",
                "Role",
                "Runs",
                "Average",
                "Strike Rate",
                "Wickets"
            ]

            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            # ------------------------------------------------
            # CHECK REQUIRED COLUMNS
            # ------------------------------------------------

            if missing_columns:

                st.error(
                    "❌ Some required columns are missing."
                )

                st.write("Missing columns:")

                for column in missing_columns:

                    st.write(
                        f"- {column}"
                    )

                st.info(
                    "Your file should contain: "
                    "Player, Role, Runs, Average, "
                    "Strike Rate, Wickets"
                )

            else:

                # ==========================================
                # CHECK KL RAHUL
                # ==========================================

                player_names = (
                    df["Player"]
                    .astype(str)
                    .str.strip()
                    .tolist()
                )

                kl_rahul = None

                for name in player_names:

                    if name.lower() == "kl rahul":

                        kl_rahul = name
                        break

                # ------------------------------------------------
                # KL RAHUL NOT FOUND
                # ------------------------------------------------

                if kl_rahul is None:

                    st.error(
                        "❌ KL Rahul is not present "
                        "in the uploaded player list."
                    )

                else:

                    # ==========================================
                    # PREPARE PLAYER DATA
                    # ==========================================

                    player_data = df.to_string(
                        index=False
                    )

                    # ==========================================
                    # AI PROMPT
                    # ==========================================

                    prompt = f"""
You are an expert cricket team selector.

Select the BEST Playing XI from the following
uploaded player list.

PLAYER LIST:

{player_data}

SELECTION RULES:

1. Select EXACTLY 11 players.
2. Consider ALL players in the list.
3. Select players based on their statistics.
4. Consider Runs.
5. Consider Batting Average.
6. Consider Strike Rate.
7. Consider Wickets.
8. Build a balanced cricket team.
9. Include strong batsmen.
10. Include useful all-rounders.
11. Include at least 4 bowling options.
12. Include at least one wicketkeeper.
13. Consider KL Rahul along with all other players.
14. KL Rahul should be selected in the Best Playing XI.
15. If KL Rahul is selected, display him at Position 1.
16. Do not select duplicate players.
17. Select ONLY players from the uploaded player list.

Return ONLY valid JSON.

Use exactly this format:

{{
    "playing_xi": [
        "Player Name 1",
        "Player Name 2",
        "Player Name 3",
        "Player Name 4",
        "Player Name 5",
        "Player Name 6",
        "Player Name 7",
        "Player Name 8",
        "Player Name 9",
        "Player Name 10",
        "Player Name 11"
    ],
    "captain": "Player Name",
    "vice_captain": "Player Name",
    "reason": "Short explanation of why this team was selected."
}}
"""

                    # ==========================================
                    # CALL OLLAMA
                    # ==========================================

                    with st.spinner(
                        "🤖 AI is selecting the best team..."
                    ):

                        try:

                            response = requests.post(
                                "http://localhost:11434/api/generate",
                                json={
                                    "model": "llama3.2",
                                    "prompt": prompt,
                                    "stream": False,
                                    "format": "json"
                                },
                                timeout=180
                            )

                            # ==================================
                            # OLLAMA ERROR
                            # ==================================

                            if response.status_code != 200:

                                st.error(
                                    "❌ Ollama returned an error."
                                )

                                st.code(
                                    response.text
                                )

                            else:

                                result = response.json()

                                ai_response = result.get(
                                    "response",
                                    ""
                                )

                                # ==================================
                                # CONVERT RESPONSE TO JSON
                                # ==================================

                                try:

                                    team_data = json.loads(
                                        ai_response
                                    )

                                except json.JSONDecodeError:

                                    match = re.search(
                                        r"\{.*\}",
                                        ai_response,
                                        re.DOTALL
                                    )

                                    if match:

                                        team_data = json.loads(
                                            match.group()
                                        )

                                    else:

                                        raise ValueError(
                                            "Ollama returned "
                                            "an invalid response."
                                        )

                                # ==================================
                                # GET AI RESULTS
                                # ==================================

                                selected_players = (
                                    team_data.get(
                                        "playing_xi",
                                        []
                                    )
                                )

                                captain = team_data.get(
                                    "captain",
                                    ""
                                )

                                vice_captain = team_data.get(
                                    "vice_captain",
                                    ""
                                )

                                reason = team_data.get(
                                    "reason",
                                    ""
                                )

                                # ==================================
                                # MATCH PLAYER NAMES
                                # ==================================

                                valid_players = (
                                    df["Player"]
                                    .astype(str)
                                    .str.strip()
                                    .tolist()
                                )

                                final_players = []

                                for selected_player in selected_players:

                                    selected_player = (
                                        str(selected_player)
                                        .strip()
                                    )

                                    for valid_player in valid_players:

                                        if (
                                            selected_player.lower()
                                            == valid_player.lower()
                                        ):

                                            if (
                                                valid_player
                                                not in final_players
                                            ):

                                                final_players.append(
                                                    valid_player
                                                )

                                # ==================================
                                # PUT KL RAHUL AT POSITION 1
                                # ==================================

                                if kl_rahul in final_players:

                                    final_players.remove(
                                        kl_rahul
                                    )

                                    final_players.insert(
                                        0,
                                        kl_rahul
                                    )

                                # ==================================
                                # CHECK TEAM SIZE
                                # ==================================

                                if len(final_players) < 11:

                                    st.warning(
                                        f"⚠️ AI returned "
                                        f"{len(final_players)} "
                                        f"valid players instead of 11."
                                    )

                                # ==================================
                                # DISPLAY FINAL TEAM
                                # ==================================

                                st.success(
                                    "🏆 Best Playing XI Selected!"
                                )

                                st.subheader(
                                    "🏏 Best Playing XI"
                                )

                                for i, player in enumerate(
                                    final_players,
                                    start=1
                                ):

                                    player_row = df[
                                        df["Player"]
                                        .astype(str)
                                        .str.strip()
                                        == player
                                    ]

                                    role = player_row[
                                        "Role"
                                    ].iloc[0]

                                    # KL Rahul appears first
                                    if player.lower() == "kl rahul":

                                        st.markdown(
                                            f"### ⭐ {i}. "
                                            f"{player} — {role}"
                                        )

                                    else:

                                        st.write(
                                            f"**{i}. {player}** "
                                            f"— {role}"
                                        )

                                # ==================================
                                # CAPTAIN & VICE CAPTAIN
                                # ==================================

                                st.markdown("---")

                                col1, col2 = st.columns(2)

                                with col1:

                                    st.info(
                                        f"🧢 **Captain:** "
                                        f"{captain}"
                                    )

                                with col2:

                                    st.info(
                                        f"⭐ **Vice-Captain:** "
                                        f"{vice_captain}"
                                    )

                                # ==================================
                                # AI REASON
                                # ==================================

                                st.subheader(
                                    "💡 AI Selection Reason"
                                )

                                st.write(
                                    reason
                                )

                                # ==================================
                                # TEAM STATISTICS
                                # ==================================

                                final_df = df[
                                    df["Player"]
                                    .astype(str)
                                    .str.strip()
                                    .isin(final_players)
                                ]

                                st.subheader(
                                    "📊 Team Statistics"
                                )

                                col1, col2, col3, col4 = (
                                    st.columns(4)
                                )

                                with col1:

                                    st.metric(
                                        "Total Runs",
                                        int(
                                            final_df[
                                                "Runs"
                                            ].sum()
                                        )
                                    )

                                with col2:

                                    st.metric(
                                        "Average",
                                        round(
                                            final_df[
                                                "Average"
                                            ].mean(),
                                            2
                                        )
                                    )

                                with col3:

                                    st.metric(
                                        "Strike Rate",
                                        round(
                                            final_df[
                                                "Strike Rate"
                                            ].mean(),
                                            2
                                        )
                                    )

                                with col4:

                                    st.metric(
                                        "Total Wickets",
                                        int(
                                            final_df[
                                                "Wickets"
                                            ].sum()
                                        )
                                    )

                        # ======================================
                        # OLLAMA CONNECTION ERROR
                        # ======================================

                        except requests.exceptions.ConnectionError:

                            st.error(
                                "❌ Cannot connect to Ollama."
                            )

                            st.info(
                                "Please open Ollama and "
                                "make sure it is running."
                            )

                        # ======================================
                        # OLLAMA TIMEOUT
                        # ======================================

                        except requests.exceptions.Timeout:

                            st.error(
                                "⏳ Ollama took too long "
                                "to respond."
                            )

                        # ======================================
                        # OTHER ERROR
                        # ======================================

                        except Exception as e:

                            st.error(
                                "❌ Something went wrong."
                            )

                            st.code(
                                str(e)
                            )

    # ======================================================
    # FILE READING ERROR
    # ======================================================

    except Exception as e:

        st.error(
            "❌ Could not read the uploaded file."
        )

        st.code(
            str(e)
        )
