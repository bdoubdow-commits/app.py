import streamlit as st
import plotly.graph_objects as go
import datetime
import json
import os
from collections import Counter

# --- ページ設定 ---
st.set_page_config(page_title="THE DESTINY - 数字が導く宿命", page_icon="🔮", layout="centered")

# --- 1. 画数・変換データ＆解説テキスト ---
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

# 🌟 追加：全10項目の詳細解説辞書
trait_details = {
    '0': {
        'base': '逆境に強く、ピンチをチャンスに変える隠された力を持っています。表舞台よりも、裏から全体を操るフィクサーとしての才能が光ります。',
        'today': '今日は予想外の展開が味方する日です。一見マイナスに思えるトラブルこそが、大逆転のトリガーになります。焦らず好機を待ちましょう。'
    },
    '1': {
        'base': '誰にも頼らず自らの力で道を切り開く、強い意志と勝負強さを持っています。群れを嫌い、個人の実力でトップに立つ一匹狼の気質です。',
        'today': '直感に従い、大胆な決断を下すのに適した日です。誰かに相談するよりも、自分自身の直感を信じて即断即決することで道が開けます。'
    },
    '2': {
        'base': '人の心を惹きつける天性の魅力を持ち、良縁を引き寄せる才能があります。他者の感情の機微を読み取り、味方につける交渉術は一級品です。',
        'today': 'コミュニケーションが信じられないほど円滑に進む日。新しい出会いや、大切な人との絆が深まる予感があります。連絡は自分から積極的に。'
    },
    '3': {
        'base': '自己表現力に長け、自然と人が集まる華やかなオーラを放っています。あなたの言葉やセンスは、無意識のうちに他者に強い影響を与えます。',
        'today': 'あなたの発言やアイデアに注目が集まる日です。SNSでの発信や、会議での提案など、内に秘めず「外に向けてアピールする」ことが吉です。'
    },
    '4': {
        'base': '精神的・肉体的なバランス感覚に優れ、絶対にブレない強固な土台を築く力があります。長期戦になるほど、あなたの堅実さが勝利を生みます。',
        'today': '無理な背伸びをせず、足場を固めるのに最適な日。いつものルーティンワークを淡々とこなすことで、逆に運気が底上げされていきます。'
    },
    '5': {
        'base': 'ひとつの場所に留まらず、常に新しい刺激を求めて進化し続けるフットワークの軽さが武器です。変化を恐れず、常に最前線を走り続けます。',
        'today': '「いつもと違う選択」が幸運を呼ぶ日。通ったことのない道を歩く、普段見ないジャンルの情報に触れるなど、小さな変化を起こしましょう。'
    },
    '6': {
        'base': '身近な人を深く愛し、守り抜く強さと圧倒的な包容力を持っています。あなたの周りには、あなたを深く信頼する絶対的な味方が集まります。',
        'today': 'プライベートな空間や、ごく親しい人との時間が最大のエネルギー源になる日。今日は外での勝負より、内側の人間関係を大切にしてください。'
    },
    '7': {
        'base': '物事の本質を見抜く鋭い観察眼と、長期的な利益を緻密に計算できるロジカルな頭脳を持っています。感情に流されない冷徹な分析が最大の武器です。',
        'today': '冷静な判断が冴え渡る日。大きな買い物や、将来への投資（自己投資や学習含む）、計画の見直しなど、頭を使う作業が最高の結果を生みます。'
    },
    '8': {
        'base': '物質的な豊かさを引き寄せ、社会的成功を収めるための強い引力を持っています。目標を達成するための執念と、結果を出す力は群を抜いています。',
        'today': '努力が「目に見える形（評価や利益）」になりやすい最高の日。遠慮は一切不要です。今日は貪欲に、自分の手柄や結果を求めて動いてください。'
    },
    '9': {
        'base': '既存の常識に囚われず、圧倒的な存在感で他者を導く天性のカリスマ性とリーダーシップを持っています。あなたの一挙手一投足が時代の基準になります。',
        'today': 'あなたの存在そのものが周囲の空気を支配する日。誰かの顔色を伺う必要はありません。自信を持って堂々と振る舞うだけで、全てが思い通りに動きます。'
    }
}

def get_numeric_value(text, stroke_dict):
    s = ""
    for char in text:
        char_upper = char.upper()
        if char_upper in stroke_dict:
            s += stroke_dict[char_upper]
        else:
            s += str(ord(char))
    return int(s) if s else 0

def calc_resonance(dob, tob, time_unknown):
    now = datetime.datetime.now()
    today = now.date()
    days_diff = abs((today - dob).days) % 365
    date_resonance = 1.0 - (days_diff / 365.0)

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
h1 { color: #d4af37; text-align: center; font-family: 'serif'; }
.resonance-box {
    background: linear-gradient(135deg, rgba(212,175,55,0.1), rgba(212,175,55,0.02));
    border: 1px solid rgba(212,175,55,0.3);
    border-radius: 8px;
    padding: 16px 20px;
    margin: 12px 0;
    font-family: 'serif';
}
.resonance-title { color: #d4af37; font-size: 0.85em; letter-spacing: 0.15em; margin-bottom: 6px; }
.resonance-value { color: #333; font-size: 2em; font-weight: bold; }
.resonance-sub { color: #666; font-size: 0.8em; margin-top: 6px; line-height: 1.6; }
.once-notice { color: #d4af37; font-size: 0.8em; text-align: center; margin-top: 4px; letter-spacing: 0.05em; font-weight: bold;}
.detail-box {
    background-color: #f8f9fa;
    border-left: 5px solid #d4af37;
    padding: 15px;
    margin-top: 10px;
    margin-bottom: 20px;
    border-radius: 4px;
    color: #333;
}
.detail-box-today {
    background-color: #f0f7ff;
    border-left: 5px solid #4a90e2;
    padding: 15px;
    margin-top: 10px;
    margin-bottom: 20px;
    border-radius: 4px;
    color: #333;
}
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
        tob = st.time_input("出生時間", value=datetime.time(12, 0), step=60, disabled=time_unknown)
    with col4:
        blood_type = st.selectbox("血液型", ["A型", "B型", "O型", "AB型", "不明（ペナルティ）"], index=4)

    predict_button = st.button("運命を解析する")

# --- 3. 解析ロジック ---
if predict_button:
    now = datetime.datetime.now()

    year = dob.year
    month_day = int(dob.strftime('%m%d'))
    val_dob = abs(year - month_day)
    val_kanji = abs(get_numeric_value(last_name, hiragana_strokes) - get_numeric_value(first_name, hiragana_strokes))
    val_alpha = abs(get_numeric_value(first_name_alpha, alphabet_strokes) - get_numeric_value(last_name_alpha, alphabet_strokes))

    hash_str = f"{val_dob}{val_kanji}{val_alpha}"
    counts = Counter(hash_str)

    raw_scores = {str(i): float(counts.get(str(i), 0)) for i in range(10)}
    max_raw = max(raw_scores.values()) if max(raw_scores.values()) > 0 else 1.0

    info_scale = min(max_raw / 3.0, 1.0)
    scores = {k: (v / max_raw) * 5.0 * info_scale for k, v in raw_scores.items()}

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

    resonance = calc_resonance(dob, tob, time_unknown)
    final_scores = {digit: (s * 0.5 + s * resonance * 0.5) for digit, s in scores.items()}

    resonance_pct = resonance * 100
    if resonance_pct >= 75:
        resonance_label, resonance_color = "極めて強い共鳴 ✨", "#d4af37"
    elif resonance_pct >= 50:
        resonance_label, resonance_color = "良好な共鳴 🌙", "#4a90e2"
    elif resonance_pct >= 25:
        resonance_label, resonance_color = "微弱な共鳴 🌫️", "#666666"
    else:
        resonance_label, resonance_color = "宿命との乖離 🌑", "#d0021b"

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

    labels = [fortune_map[str(i)] for i in range(10)]
    base_values = [scores[str(i)] for i in range(10)]
    final_values = [final_scores[str(i)] for i in range(10)]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=base_values + [base_values[0]],
        theta=labels + [labels[0]],
        fill='none',
        line=dict(color='#888888', width=1.5, dash='dot'),
        name='本来の宿命'
    ))

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
            radialaxis=dict(visible=True, range=[0, 5], tickvals=[1, 2, 3, 4, 5], tickcolor="#cccccc", gridcolor="#e0e0e0"),
            angularaxis=dict(gridcolor="#e0e0e0", tickfont=dict(size=12, color="#333333"))
        ),
        showlegend=True,
        legend=dict(font=dict(color="#333333"), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=20)
    )

    st.subheader("🌟 あなたの真の運命チャート")
    st.plotly_chart(fig, use_container_width=True)
    
    # --- Step 7: テキスト出力 ＆ 詳細解説表示 ---
    base_max_val = max(scores.values())
    final_max_val = max(final_scores.values())

    if final_max_val > 0:
        st.markdown("---")
        st.subheader("📜 宿命と運勢の深淵解説")
        
        # 本来の宿命（ベース）の解説
        st.markdown(f"#### 🔘 【本来の宿命】最大の武器（スコア: {base_max_val:.2f}）")
        for k, v in scores.items():
            if v == base_max_val:
                st.markdown(f"**■ {fortune_map[k]}**")
                st.markdown(f"<div class='detail-box'>{trait_details[k]['base']}</div>", unsafe_allow_html=True)
        
        # 今日の波形の解説
        st.markdown(f"#### 🌟 【今日の波形】星からのメッセージ（スコア: {final_max_val:.2f}）")
        for k, v in final_scores.items():
            if v == final_max_val:
                st.markdown(f"**■ {fortune_map[k]}**")
                st.markdown(f"<div class='detail-box-today'>{trait_details[k]['today']}</div>", unsafe_allow_html=True)

        # 総合評価メッセージ
        st.markdown("---")
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
