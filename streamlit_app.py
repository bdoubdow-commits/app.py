import streamlit as st
import plotly.graph_objects as go
import datetime
import json
import os
import hashlib
import random
from collections import Counter

# --- ページ設定 ---
st.set_page_config(page_title="THE DESTINY - 数字が導く宿命", page_icon="🔮", layout="centered")

# --- 1. 画数・変換データ＆解説テキスト（高低で分岐） ---
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

trait_details = {
    '0': {
        'base_high': '逆境に強く、ピンチをチャンスに変える隠された力を持っています。表舞台よりも、裏から全体を操るフィクサーとしての才能が光ります。',
        'base_low': '予期せぬ事態への耐性がやや低く、想定外のトラブルに直面すると本来の力を見失いがちです。事前準備が運命を分けます。',
        'today_high': '今日は予想外の展開が完全に味方します。一見マイナスに思えるトラブルこそが大逆転のトリガーに。焦らず好機を待ちましょう。',
        'today_low': '隠れていた問題が表面化しやすい日です。無理に状況を覆そうとせず、今日はダメージを最小限に抑える防御の姿勢が吉です。'
    },
    '1': {
        'base_high': '誰にも頼らず自らの力で道を切り開く、強い意志と勝負強さを持っています。群れを嫌い、個人の実力でトップに立つ気質です。',
        'base_low': '決断の場面で他者の意見に流されやすい傾向があります。自分の軸よりも協調性を優先するため、勝負を避けることが多いです。',
        'today_high': '直感に従い、大胆な決断を下すのに適した日です。誰かに相談するよりも、自分自身の直感を信じて即断即決することで道が開けます。',
        'today_low': '今日は勝負に出ると裏目に出やすい日。一発逆転を狙うよりも、確実な一歩を刻むこと。大きな決断は明日に回すのが無難です。'
    },
    '2': {
        'base_high': '人の心を惹きつける天性の魅力を持ち、良縁を引き寄せる才能があります。他者の感情の機微を読み取り、味方につける交渉術は一級品。',
        'base_low': '人間関係において距離感を取るのが苦手、あるいは極端に壁を作りがちです。無意識のうちに孤立を選んでしまう傾向があります。',
        'today_high': 'コミュニケーションが信じられないほど円滑に進む日。新しい出会いや、大切な人との絆が深まる予感があります。連絡は自分から積極的に。',
        'today_low': '些細な言葉のすれ違いが大きな誤解を生みやすい日。冗談のつもりでも相手を深く傷つける可能性があります。発言には細心の注意を。'
    },
    '3': {
        'base_high': '自己表現力に長け、自然と人が集まる華やかなオーラを放っています。あなたの言葉やセンスは、無意識のうちに他者に強い影響を与えます。',
        'base_low': '自分の魅力や才能を外に向かってアピールするのが苦手で、正当な評価を得にくい損な役回りになりがちです。',
        'today_high': 'あなたの発言やアイデアに注目が集まる日です。SNSでの発信や、会議での提案など、内に秘めず「外に向けてアピールする」ことが吉です。',
        'today_low': '目立つ行動が反感を買いやすい星回りです。今日は黒子に徹し、周囲のサポートに回ることで逆に信頼残高が蓄積されます。'
    },
    '4': {
        'base_high': '精神的・肉体的なバランス感覚に優れ、絶対にブレない強固な土台を築く力があります。長期戦になるほど、あなたの堅実さが勝利を生みます。',
        'base_low': '気分の浮き沈みが激しく、環境の変化によって体調やメンタルが左右されやすい脆さを秘めています。ルーティンの構築が課題です。',
        'today_high': '無理な背伸びをせず、足場を固めるのに最適な日。いつものルーティンワークを淡々とこなすことで、逆に運気が底上げされていきます。',
        'today_low': '疲労やストレスが限界に達する一歩手前です。今日は予定を詰め込まず、意識的に休息を取ることを最優先にしてください。'
    },
    '5': {
        'base_high': 'ひとつの場所に留まらず、常に新しい刺激を求めて進化し続けるフットワークの軽さが武器です。変化を恐れず、最前線を走り続けます。',
        'base_low': '未知の領域に踏み出すことに強い警戒心を抱き、現状維持を好む傾向があります。その結果、チャンスを逃してしまうことも。',
        'today_high': '「いつもと違う選択」が幸運を呼ぶ日。通ったことのない道を歩く、普段見ないジャンルの情報に触れるなど、小さな変化を起こしましょう。',
        'today_low': '今日は急な予定変更や新しい挑戦は控えるべき日。不測の事態に弱くなっているため、慣れ親しんだ安全なやり方を貫いてください。'
    },
    '6': {
        'base_high': '身近な人を深く愛し、守り抜く強さと圧倒的な包容力を持っています。あなたの周りには、深く信頼する絶対的な味方が集まります。',
        'base_low': '身内や身近な人に対してドライになりすぎたり、逆に依存しすぎたりと、愛情のバランスを取るのがやや苦手な傾向があります。',
        'today_high': 'プライベートな空間や、ごく親しい人との時間が最大のエネルギー源になる日。今日は外での勝負より、内側の人間関係を大切に。',
        'today_low': '身近な人（家族やパートナー）との間に冷たい隙間風が吹きやすい日。理詰めでの会話は避け、共感の姿勢を示すことが重要です。'
    },
    '7': {
        'base_high': '物事の本質を見抜く鋭い観察眼と、長期的な利益を緻密に計算できるロジカルな頭脳を持っています。冷徹な分析が最大の武器です。',
        'base_low': '感情や直感に流されやすく、データに基づいた客観的な判断を後回しにしがちです。思い込みで突っ走る危うさがあります。',
        'today_high': '冷静な判断が冴え渡る日。大きな買い物や、将来への投資、計画の見直しなど、頭を使う作業が最高の結果を生みます。',
        'today_low': '情報に振り回され、判断力が著しく低下しています。今日はお金が絡む決断や、重要な契約・投資は見送るのが賢明です。'
    },
    '8': {
        'base_high': '物質的な豊かさを引き寄せ、社会的成功を収める強い引力を持っています。目標を達成するための執念と、結果を出す力は群を抜いています。',
        'base_low': '利益に対する執着が薄く、せっかくのチャンスを他人に譲ってしまいがち。結果的に豊かさが手元に残りづらい傾向があります。',
        'today_high': '努力が「目に見える形（評価や利益）」になりやすい最高の日。遠慮は一切不要です。今日は貪欲に、自分の手柄や結果を求めて動いてください。',
        'today_low': '予期せぬ出費や、努力が空回りしやすい日。利益を追求するほどドツボにハマるため、今日は無償の奉仕や「与える」ことに専念しましょう。'
    },
    '9': {
        'base_high': '既存の常識に囚われず、圧倒的な存在感で他者を導く天性のカリスマ性とリーダーシップを持っています。あなたの一挙手一投足が時代の基準に。',
        'base_low': '他者の視線を過剰に気にしてしまい、自分らしさを封印しがちです。本来の個性を出すことに強い内的ブロックがかかっています。',
        'today_high': 'あなたの存在そのものが周囲の空気を支配する日。誰かの顔色を伺う必要はありません。自信を持って堂々と振る舞うだけで、全てが思い通りに。',
        'today_low': '権力や強い影響力を持つ人物と衝突しやすい日。今日はあなたが前に出るのではなく、ナンバーツーのポジションで立ち回るのが最も安全です。'
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
.once-notice { color: #d4af37; font-size: 0.9em; text-align: center; margin-top: 4px; letter-spacing: 0.05em; font-weight: bold;}
.detail-text { color: #444; font-size: 0.95em; line-height: 1.6; padding-bottom: 8px; }
.detail-label { color: #d4af37; font-weight: bold; font-size: 0.9em; border-bottom: 1px solid #eee; padding-bottom: 4px; margin-bottom: 8px; margin-top: 12px; }
.detail-label-today { color: #4a90e2; font-weight: bold; font-size: 0.9em; border-bottom: 1px solid #eee; padding-bottom: 4px; margin-bottom: 8px; margin-top: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🔮 THE DESTINY")
st.write("計算された差異が、真の宿命を炙り出す。")
st.markdown('<p class="once-notice">⚠️ 1日1度、1回目の判定が本物です。<br>2回目、3回目とズレてしまいますのでご注意ください。</p>', unsafe_allow_html=True)

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

    st.subheader("【追加情報（より深く運命を読み解く）】")
    col3, col4 = st.columns(2)
    with col3:
        time_unknown = st.checkbox("出生時間が不明")
        tob = st.time_input("出生時間", value=datetime.time(12, 0), step=60, disabled=time_unknown)
    with col4:
        blood_type = st.selectbox("血液型", ["A型", "B型", "O型", "AB型", "不明"], index=4)

    predict_button = st.button("本日の運命を解析する")

# --- 3. 解析ロジック ---
if predict_button:
    now = datetime.datetime.now()

    # --- 宿命（ベース）の計算 ---
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

    # --- クリックした「年月日時分」による変動（卜術的アプローチ） ---
    # アクセスした瞬間の「分」まで含めたシードで、毎分運勢が揺らぐように設定
    seed_str = f"{now.strftime('%Y%m%d%H%M')}_{hash_str}"
    seed_int = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    random.seed(seed_int)

    final_scores = {}
    for digit, base_s in scores.items():
        # アクセスタイミングによって -1.5 〜 +2.5 の間で運勢が変動
        buff = random.uniform(-1.5, 2.5)
        f_score = base_s + buff
        final_scores[digit] = max(0.0, min(5.0, f_score))

    # 共鳴係数の算出
    resonance = calc_resonance(dob, tob, time_unknown)
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
        <div class="resonance-title">▶ {now.strftime('%H:%M')} の星回り</div>
        <div class="resonance-value" style="color:{resonance_color}">{resonance_pct:.1f}%　<span style="font-size:0.5em">{resonance_label}</span></div>
        <div class="resonance-sub">
            あなたが扉を開いた {now.strftime('%Y/%m/%d %H:%M')} 瞬間の運命波形。<br>
            結果は刻一刻と変化します。最初の導きを大切にしてください。
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
        name='今の運勢'
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
    
    base_max_val = max(scores.values())
    final_max_val = max(final_scores.values())

    if final_max_val > 0:
        st.markdown("---")
        
        base_top_traits = [fortune_map[k] for k, v in scores.items() if v == base_max_val]
        final_top_traits = [fortune_map[k] for k, v in final_scores.items() if v == final_max_val]
        st.info(f"**👑 【生来の最大の武器】** {' / '.join(base_top_traits)} （ベース: {base_max_val:.2f}）")
        st.success(f"**🎯 【今の最強ステータス】** {' / '.join(final_top_traits)} （現在: {final_max_val:.2f} / 5.0）")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📜 全パラメータ詳細解析")
        st.write("あなたの持つすべての宿命要素と、いまこの瞬間の星回りによる状態を解説します。（現在のスコアが高い順）")

        sorted_keys = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)

        for k in sorted_keys:
            trait_name = fortune_map[k]
            b_score = scores[k]
            f_score = final_scores[k]
            
            b_text = trait_details[k]['base_high'] if b_score >= 3.0 else trait_details[k]['base_low']
            f_text = trait_details[k]['today_high'] if f_score >= 3.0 else trait_details[k]['today_low']
            
            with st.expander(f"■ {trait_name} （本来: {b_score:.2f} ➔ 現在: {f_score:.2f}）"):
                st.markdown(f"<div class='detail-label'>本来の宿命（ベーススコア: {b_score:.2f}）</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='detail-text'>{b_text}</div>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='detail-label-today'>今の運勢（最終スコア: {f_score:.2f}）</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='detail-text'>{f_text}</div>", unsafe_allow_html=True)

    else:
        st.warning("⚠️ スコアが算出できませんでした。入力情報を確認してください。")
