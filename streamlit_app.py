import streamlit as st
import plotly.graph_objects as go
import datetime
import json
import os
from collections import Counter

# --- ページ設定 ---
st.set_page_config(page_title="THE DESTINY - 数字が導く宿命", page_icon="🔮", layout="centered")

# --- 1. 画数・数値変換データ ---
alphabet_strokes = {
    'A': '3', 'B': '2', 'C': '1', 'D': '2', 'E': '4', 'F': '3', 'G': '1', 'H': '3', 'I': '1',
    'J': '2', 'K': '3', 'L': '2', 'M': '4', 'N': '3', 'O': '1', 'P': '2', 'Q': '2', 'R': '3',
    'S': '1', 'T': '2', 'U': '1', 'V': '2', 'W': '4', 'X': '2', 'Y': '3', 'Z': '3'
}

hiragana_strokes = {
    'あ': '3', 'い': '2', 'う': '2', 'え': '2', 'お': '3', 'か': '3', 'き': '4', 'く': '1', 'け': '3', 'こ': '2',
    'さ': '3', 'し': '1', 'す': '3', 'せ': '3', 'そ': '3', 'た': '4', 'ち': '2', 'つ': '1', 'て': '1', 'と': '2',
    'な': '4', 'に': '3', 'ぬ': '3', 'ね': '4', 'の': '1', 'は': '4', 'ひ': '2', 'ふ': '4', 'へ': '1', 'ほ': '5',
    'ま': '3', 'み': '2', 'む': '3', 'め': '2', 'も': '3', 'や': '3', 'ゆ': '2', 'よ': '2', 'ら': '2', 'り': '2',
    'る': '2', 'れ': '2', 'ろ': '1', 'わ': '2', 'を': '3', 'ん': '1'
}

blood_type_strokes = {"A型": "3", "B型": "2", "O型": "1", "AB型": "32"}

fortune_map = {
    '0': '潜在・逆転', '1': '勝負・独立', '2': '恋愛・対人', '3': '人気・表現', '4': '健康・安定',
    '5': '行動・変化', '6': '家庭・愛情', '7': '分析・投資', '8': '金運・成功', '9': 'カリスマ'
}

def get_numeric_value(text, stroke_dict):
    """文字列を数値化。辞書にある文字は画数、ない文字（漢字等）はUnicodeで数値化。"""
    s = ""
    for char in text:
        char_upper = char.upper()
        if char_upper in stroke_dict:
            s += stroke_dict[char_upper]
        else:
            s += str(ord(char))
    return int(s) if s else 0

def calc_resonance(dob, tob, time_unknown):
    """今日の日時とユーザー情報から共鳴係数（0.0〜1.0）を算出する。"""
    now = datetime.datetime.now()
    today = now.date()

    # 日付軸：誕生日に近いほど高い
    days_diff = abs((today - dob).days) % 365
    date_resonance = 1.0 - (days_diff / 365.0)

    # 時刻軸：出生時刻に近いほど高い
    if time_unknown:
        time_resonance = 0.5
    else:
        now_minutes = now.hour * 60 + now.minute
        birth_minutes = tob.hour * 60 + tob.minute
        minutes_diff = abs(now_minutes - birth_minutes) % 1440
        time_resonance = 1.0 - (min(minutes_diff, 1440 - minutes_diff) / 720.0)

    return (date_resonance + time_resonance) / 2.0

# --- 2. UI構築 ---
st.markdown("""
<style>
.main { background-color: #0e1117; color: #ffffff; }
h1 { color: #d4af37; text-align: center; font-family: 'serif'; }
.resonance-box {
    background: linear-gradient(135deg, rgba(212,175,55,0.15), rgba(212,175,55,0.05));
    border: 1px solid rgba(212,175,55,0.4);
    border-radius: 8px;
    padding: 16px 20px;
    margin: 12px 0;
    font-family: 'serif';
}
.resonance-title { color: #d4af37; font-size: 0.85em; letter-spacing: 0.15em; margin-bottom: 6px; }
.resonance-value { color: #fff; font-size: 2em; font-weight: bold; }
.resonance-sub { color: #aaa; font-size: 0.8em; margin-top: 6px; line-height: 1.6; }
.once-notice { color: #d4af37; font-size: 0.8em; opacity: 0.8; text-align: center; margin-top: 4px; letter-spacing: 0.05em; }
</style>
""", unsafe_allow_html=True)

st.title("🔮 THE DESTINY")
st.write("計算された差異が、真の宿命を炙り出す。")
st.markdown('<p class="once-notice">⚠️ 扉は今日一度だけ開かれる——最初の結果が、あなたの本当の声。</p>', unsafe_allow_html=True)

with st.container():
    st.subheader("【基本情報】")
    col1, col2 = st.columns(2)
    with col1:
        last_name = st.text_input("姓（漢字・ひらがな）", placeholder="例：山田")
        first_name = st.text_input("名（漢字・ひらがな）", placeholder="例：太郎")
    with col2:
        last_name_alpha = st.text_input("姓（ローマ字）", placeholder="例：YAMADA")
        first_name_alpha = st.text_input("名（ローマ字）", placeholder="例：TARO")

    dob = st.date_input("生年月日", min_value=datetime.date(1900, 1, 1), value=datetime.date(2000, 1, 1))

    st.subheader("【追加情報（デバフ判定用）】")
    col3, col4 = st.columns(2)
    with col3:
        time_unknown = st.checkbox("出生時間が不明")
        # step=60で1分刻みに修正
        tob = st.time_input("出生時間", value=datetime.time(12, 0), step=60, disabled=time_unknown)
    with col4:
        blood_type = st.selectbox("血液型", ["A型", "B型", "O型", "AB型", "不明（ペナルティ）"], index=4)

    predict_button = st.button("運命を解析する")

# --- 3. 解析ロジック ---
if predict_button:
    now = datetime.datetime.now()

    # --- Step 1: ハッシュ文字列の生成 ---
    year = dob.year
    month_day = int(dob.strftime('%m%d'))
    val_dob = abs(year - month_day)
    val_kanji = abs(get_numeric_value(last_name, hiragana_strokes) - get_numeric_value(first_name, hiragana_strokes))
    val_alpha = abs(get_numeric_value(first_name_alpha, alphabet_strokes) - get_numeric_value(last_name_alpha, alphabet_strokes))

    hash_str = f"{val_dob}{val_kanji}{val_alpha}"
    counts = Counter(hash_str)

    # --- Step 2: 正規化スコアの算出 ---
    raw_scores = {str(i): float(counts.get(str(i), 0)) for i in range(10)}
    max_raw = max(raw_scores.values()) if max(raw_scores.values()) > 0 else 1.0

    info_scale = min(max_raw / 3.0, 1.0)
    scores = {k: (v / max_raw) * 5.0 * info_scale for k, v in raw_scores.items()}

    # --- Step 3: デバフ判定（生来の宿命） ---
    time_str = "" if time_unknown else tob.strftime('%H%M')
    blood_str = "" if blood_type.startswith("不明") else blood_type_strokes.get(blood_type, "")

    for i in range(10):
        digit = str(i)
        debuff = 0.0
        if time_unknown or digit in time_str:
            debuff += 0.5
        if blood_type.startswith("不明") or digit in blood_str:
            debuff += 0.5
        scores[digit] = max(0.0, scores[digit] - debuff)

    # --- Step 4: 共鳴係数の算出と適用（今日の波形） ---
    resonance = calc_resonance(dob, tob, time_unknown)
    final_scores = {digit: (s * 0.5 + s * resonance * 0.5) for digit, s in scores.items()}

    # --- Step 5: 共鳴演出 ---
    resonance_pct = resonance * 100
    if resonance_pct >= 75:
        resonance_label, resonance_color = "極めて強い共鳴 ✨", "#d4af37"
    elif resonance_pct >= 50:
        resonance_label, resonance_color = "良好な共鳴 🌙", "#a0c4ff"
    elif resonance_pct >= 25:
        resonance_label, resonance_color = "微弱な共鳴 🌫️", "#888"
    else:
        resonance_label, resonance_color = "宿命との乖離 🌑", "#c04040"

    st.markdown(f"""
    <div class="resonance-box">
        <div class="resonance-title">▶ 今日の宿命共鳴</div>
        <div class="resonance-value" style="color:{resonance_color}">{resonance_pct:.1f}%　<span style="font-size:0.5em">{resonance_label}</span></div>
        <div class="resonance-sub">
            {now.strftime('%Y/%m/%d %H:%M')} に扉を開いた。<br>
            この数値は今日限り。最初の結果だけが、宿命の本当の声。
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Step 6: グラフ表示（二重波形） ---
    labels = [fortune_map[str(i)] for i in range(10)]
    
    # ベースの波形（生来の宿命）
    base_values = [scores[str(i)] for i in range(10)]
    # 今日の波形（共鳴後）
    final_values = [final_scores[str(i)] for i in range(10)]

    fig = go.Figure()

    # ベース波形を追加（グレーの点線）
    fig.add_trace(go.Scatterpolar(
        r=base_values + [base_values[0]],
        theta=labels + [labels[0]],
        fill='none',
        line=dict(color='#888888', width=1.5, dash='dot'),
        name='本来の宿命'
    ))

    # 今日の波形を追加（ゴールド）
    fig.add_trace(go.Scatterpolar(
        r=final_values + [final_values[0]],
        theta=labels + [labels[0]],
        fill='toself',
        fillcolor='rgba(212, 175, 55, 0.4)',
        line=dict(color='#d4af37', width=2),
        marker=dict(color='#d4af37', size=8),
        name='今日の波形'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickvals=[1, 2, 3, 4, 5], tickcolor="#444", gridcolor="#444"),
            angularaxis=dict(gridcolor="#444", tickfont=dict(size=12, color="#eee"))
        ),
        showlegend=True,
        legend=dict(font=dict(color="#eee"), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=20)
    )

    st.subheader("🌟 あなたの真の運命チャート")
    st.plotly_chart(fig, use_container_width=True)

    # --- Step 7: テキスト出力 ---
    
    # 最大値の算出
    base_max_val = max(scores.values())
    base_top_traits = [fortune_map[k] for k, v in scores.items() if v == base_max_val]
    
    final_max_val = max(final_scores.values())
    final_top_traits = [fortune_map[k] for k, v in final_scores.items() if v == final_max_val]

    if final_max_val > 0:
        st.markdown(f"**【生来の宿命】** あなたが本来持つ最大の武器は **「{' / '.join(base_top_traits)}」** です。（ベーススコア: {base_max_val:.2f}）")
        st.info(f"**【今日の波形】** 星との共鳴を経た今日の武器は **「{' / '.join(final_top_traits)}」** です。（最終スコア: {final_max_val:.2f} / 5.0）")

        if resonance_pct >= 75:
            st.success("✨ 今日は星との共鳴が極めて強い。この結果を信じよ。")
        elif resonance_pct >= 50:
            st.info("🌙 良好な共鳴。今日の結果は概ね信頼できる。")
        elif resonance_pct >= 25:
            st.warning("🌫️ 共鳴はやや弱い。今日は本来の力が出し切れていないかもしれない。")
        else:
            st.error("🌑 宿命との乖離が大きい日。逆らわず、流れに身を任せよ。")
    else:
        st.warning("⚠️ スコアが算出できませんでした。入力情報を確認してください。")
