import streamlit as st
import plotly.graph_objects as go
import datetime
import hashlib
import time
from collections import Counter

# --- ページ設定 ---
st.set_page_config(page_title="RESONANCE - 絶対宿命律 -", page_icon="🔮", layout="centered")

# --- 1. 画数辞書 ---
alphabet_strokes = {'A': '3', 'B': '2', 'C': '1', 'D': '2', 'E': '4', 'F': '3', 'G': '1', 'H': '3', 'I': '1', 'J': '2', 'K': '3', 'L': '2', 'M': '4', 'N': '3', 'O': '1', 'P': '2', 'Q': '2', 'R': '3', 'S': '1', 'T': '2', 'U': '1', 'V': '2', 'W': '4', 'X': '2', 'Y': '3', 'Z': '3'}
hiragana_strokes = {'あ': '3', 'い': '2', 'う': '2', 'え': '2', 'お': '3', 'か': '3', 'き': '4', 'く': '1', 'け': '3', 'こ': '2', 'さ': '3', 'し': '1', 'す': '3', 'せ': '3', 'そ': '3', 'た': '4', 'ち': '2', 'つ': '1', 'て': '1', 'と': '2', 'な': '4', 'に': '3', 'ぬ': '3', 'ね': '4', 'の': '1', 'は': '4', 'ひ': '2', 'ふ': '4', 'へ': '1', 'ほ': '5', 'ま': '3', 'み': '2', 'む': '3', 'め': '2', 'も': '3', 'や': '3', 'ゆ': '2', 'よ': '2', 'ら': '2', 'り': '2', 'る': '2', 'れ': '2', 'ろ': '1', 'わ': '2', 'を': '3', 'ん': '1'}
blood_type_strokes = {"A型": "3", "B型": "2", "O型": "1", "AB型": "32"}
fortune_map = {'0': '潜在・逆転', '1': '勝負・独立', '2': '恋愛・対人', '3': '人気・表現', '4': '健康・安定', '5': '行動・変化', '6': '家庭・愛情', '7': '分析・投資', '8': '金運・成功', '9': 'カリスマ'}

# --- 預言者テキスト（重要ワードを<span>で強調可能に） ---
trait_details = {
    '0': {
        'base_high': '【本質】あなたは逆境を喰らい、運命を反転させる<span style="color:#d4af37">特異点</span>の星の元に生まれました。<br>【深掘り】光の当たる表舞台よりも、深淵からすべてを操るフィクサーとしての才脈が脈打っています。絶望的な状況に陥るほど、あなたの真の力は覚醒するでしょう。',
        'base_low': '【本質】予期せぬ運命の揺らぎに対し、やや脆弱な星の配置にあります。<br>【深掘り】想定外のトラブルに直面すると、本来の力を見失い、波に飲まれがちです。あなたの運命を分けるのは、常に<span style="color:#d4af37">最悪を想定した事前準備</span>です。',
        'today_high': '【波動解析】星の配列が特異点に達しています。<br>【深掘り】今日あなたの身に降りかかる『不測の事態』は、運命を強制的に好転させるための<span style="color:#d4af37">宇宙の布石</span>に過ぎません。<br>【本日の指針】表面的なトラブルに動揺せず、ただ静観してください。全てはあなたの手の中に収まります。',
        'today_low': '【波動解析】見えない死角から、運命のノイズが侵入しやすい危険な波形です。<br>【深掘り】隠れていた問題が突然表面化し、あなたを激しく揺さぶるでしょう。無理に状況を覆そうとすれば、さらなる深みにハマります。<br>【本日の指針】今日はダメージを最小限に抑える<span style="color:#ff4b4b">防御の姿勢</span>を貫きなさい。'
    },
    '1': {
        'base_high': '【本質】誰にも依存せず、自らの力で荒野を切り開く<span style="color:#d4af37">孤高の王</span>の気質です。<br>【深掘り】他者のルールに従うのではなく、あなたがルールとなるのです。圧倒的な実力で頂点に立つ運命を与えられています。',
        'base_low': '【本質】決断の淵に立たされた時、他者の波動に共鳴しすぎる傾向があります。<br>【深掘り】自らの真なる声よりも、周囲との調和を優先してしまうため、勝負所で身を引いてしまうことが多いでしょう。それは優しさでもあり、弱さでもあります。',
        'today_high': '【波動解析】直感の刃が極限まで研ぎ澄まされた絶対的な波形です。<br>【深掘り】誰かに意見を求める行為は、かえって運気を濁らせます。内なる直感こそが、今日最も正確なコンパスとなります。<br>【本日の指針】他者の声を聞く必要はありません。<span style="color:#d4af37">即断即決</span>で道を開きなさい。',
        'today_low': '【波動解析】勝負の波が乱れ、行動が裏目に出やすい星回りです。<br>【深掘り】一発逆転を狙うような野心的な行動は、運命の歪みを引き起こします。今は刃を隠し、力を蓄えるべき時。<br>【本日の指針】大きな決断は絶対に避け、<span style="color:#ff4b4b">確実な一歩</span>だけを刻みなさい。'
    },
    '2': {
        'base_high': '【本質】人の魂を魅了し、運命の糸を自在に操る天性の<span style="color:#d4af37">引力</span>を持っています。<br>【深掘り】他者の感情を無意識に読み取り、絶対的な味方へと変える交渉術はまさに魔力。あなたは存在そのものが、周囲にとっての引力圏なのです。',
        'base_low': '【本質】魂の交信において、距離感のチューニングに不協和音を抱えています。<br>【深掘り】他者と深く交わることを恐れ、見えない壁を築いてしまう傾向があります。無意識のうちに孤立を選び、孤独のループに陥る危うさがあります。',
        'today_high': '【波動解析】対人運の波形が黄金比を描き、完璧な共鳴を果たしています。<br>【深掘り】今日、あなたの言葉は相手の魂の奥深くまで届きます。停滞していた関係が<span style="color:#d4af37">劇的に動き出す</span>予感。<br>【本日の指針】自ら運命の糸をたぐり寄せなさい。積極的な連絡が吉です。',
        'today_low': '【波動解析】言葉の波長が歪み、ノイズが発生しやすい危険な星回りです。<br>【深掘り】ほんの些細な一言が、取り返しのつかない誤解と亀裂を生み出します。あなたの意図とは無関係に、悪意として受け取られかねません。<br>【本日の指針】今日は徹底して<span style="color:#ff4b4b">言葉を慎み</span>、聞き手に回りなさい。'
    },
    '3': {
        'base_high': '【本質】魂の輝きを外へ放ち、世界を魅了する表現者の星を宿しています。<br>【深掘り】あなたの放つ言葉やセンスは、他者の無意識に強烈な楔を打ち込みます。自然と人が集い、あなたを中心に世界が回るでしょう。',
        'base_low': '【本質】自らの放つべき光を、内側の闇に閉じ込めてしまう傾向があります。<br>【深掘り】他者の評価を恐れるあまり、才能の片鱗を見せることを無意識に拒絶しています。本来受けるべき賞賛を得られない損な役回りに甘んじています。',
        'today_high': '【波動解析】表現のオーラが最大化し、周囲の視線を独占する波形です。<br>【深掘り】あなたの存在そのものが強いメッセージとなり、世界を揺るがします。内に秘めたアイデアは、今日<span style="color:#d4af37">解き放たれるため</span>にありました。<br>【本日の指針】決して隠れてはいけません。舞台の中央に立ちなさい。',
        'today_low': '【波動解析】自己主張の波が周囲と衝突し、反発を生む危険な兆候です。<br>【深掘り】良かれと思った行動が「自己中心的」と誤認され、無用な嫉妬や反感を買うでしょう。今日はあなたの光が強すぎるのです。<br>【本日の指針】黒子に徹し、他者を輝かせることにのみ力を注ぎなさい。'
    },
    '4': {
        'base_high': '【本質】大地の如き不動の精神と、肉体の完全な均衡を保つ星の元にあります。<br>【深掘り】どれほど激しい嵐の中でも、あなたの根は決してブレません。<span style="color:#d4af37">長期的な視点</span>こそが、最終的な勝利と絶対の安定をもたらします。',
        'base_low': '【本質】魂の基盤が揺らぎやすく、環境のノイズに深く共鳴してしまう脆さがあります。<br>【深掘り】気分の浮き沈みが激しく、些細な変化が肉体や精神にダイレクトにダメージを与えます。強固なルーティンを持たぬ限り、運命に翻弄されるでしょう。',
        'today_high': '【波動解析】安定のバイオリズムが完璧な調和を見せる、盤石の星回りです。<br>【深掘り】今日、無理な背伸びは不要です。日常を淡々とこなすことで、その反復が強大な運気となって蓄積されます。<br>【本日の指針】足元を見つめ、<span style="color:#d4af37">いつもの歩幅</span>で確実に前進しなさい。',
        'today_low': '【波動解析】生命力の波形が底を打ち、限界のレッドゾーンに突入しつつあります。<br>【深掘り】見えない疲労とストレスが魂を侵食しています。このまま進めば、取り返しのつかない崩壊を招く恐れがあります。<br>【本日の指針】すべての予定を一旦停止し、<span style="color:#ff4b4b">絶対的な休息</span>を求めなさい。'
    },
    '5': {
        'base_high': '【本質】常に進化を渇望し、停滞を死とする流浪の星を宿しています。<br>【深掘り】ひとつの場所に縛られることなく、新たな刺激を求めて最前線を駆け抜けます。フットワークの軽さは、運命を切り開く最強の剣です。',
        'base_low': '【本質】未知の領域に対する本能的な恐怖が、あなたの足を鎖で繋いでいます。<br>【深掘り】変化を極端に恐れ、苦痛を伴ってでも現状維持に固執する傾向があります。その警戒心が、チャンスを殺しているのです。',
        'today_high': '【波動解析】変化の波が押し寄せ、新たな次元への扉が開く特異日です。<br>【深掘り】日常の延長線上には何の手がかりもありません。<span style="color:#d4af37">「いつもと違う選択」</span>こそが、奇跡を呼ぶ唯一のパスワードです。<br>【本日の指針】通ったことのない道へ、迷わず飛び込みなさい。',
        'today_low': '【波動解析】運命のベクトルが乱れ、行動が裏目に出やすい不安定な波形です。<br>【深掘り】不測の事態に対する耐性が著しく低下しています。今日、急な予定変更を行うことは、自ら罠に飛び込むようなもの。<br>【本日の指針】慣れ親しんだ<span style="color:#ff4b4b">安全圏</span>に留まり、絶対に冒険を避けなさい。'
    },
    '6': {
        'base_high': '【本質】深い慈愛で他者を包み込み、絶対的な安全圏を構築する守護の星です。<br>【深掘り】身近な者を守り抜く強さと、海のような包容力を持っています。あなたの波動に引き寄せられ、周囲には強固な信頼が築かれます。',
        'base_low': '【本質】愛のエネルギーの出力調整に、深刻な揺らぎを抱えています。<br>【深掘り】身近な者に対して氷のように冷酷になったかと思えば、逆に依存してしまう。この両極端な揺らぎが、関係を破壊する火種となります。',
        'today_high': '【波動解析】愛と調和のエネルギーが満ち溢れ、結びつきが最強となる日です。<br>【深掘り】外の世界での闘争は今日はいったん忘れなさい。魂を許し合える者との時間が、あなたに<span style="color:#d4af37">無尽蔵の力</span>を与えます。<br>【本日の指針】大切な者との対話に時間を使いなさい。',
        'today_low': '【波動解析】身近な関係線にノイズが走り、断絶の危機が迫る星回りです。<br>【深掘り】家族やパートナーとの間に、冷たく刺さるような隙間風が吹くでしょう。正論は、相手の心に致命的な傷を負わせます。<br>【本日の指針】今日は論破を禁じます。ただ黙って<span style="color:#ff4b4b">共感</span>を示しなさい。'
    },
    '7': {
        'base_high': '【本質】世界のあらゆる事象を数式化し、本質を見抜く冷徹な知性の星です。<br>【深掘り】感情というノイズを排除し、長期利益を計算し尽くすロジカルな頭脳。その鋭利な観察眼は、未来を予測する最高の武器となります。',
        'base_low': '【本質】論理的思考の回路が感情によってショートしやすい傾向があります。<br>【深掘り】客観データよりも、その瞬間の気分に流されてしまいます。思い込みで突っ走り、後戻りできない失敗を招く危うさがあります。',
        'today_high': '【波動解析】思考のクロック数が跳ね上がり、冷徹な判断力が冴え渡る波形です。<br>【深掘り】今日、あなたの脳髄は正確無比な答えを導き出します。将来への投資や、複雑な計画の立案には最高の日。<br>【本日の指針】感情を排し、<span style="color:#d4af37">論理のみ</span>を信じて決断を下しなさい。',
        'today_low': '【波動解析】情報処理の回路に深刻なバグが発生し、判断力が混濁しています。<br>【深掘り】溢れるノイズに振り回され、真実を見失うでしょう。今日、金銭が絡む決断を行うことは、<span style="color:#ff4b4b">破滅へのトリガー</span>となります。<br>【本日の指針】すべての重要な判断を明日に先送りしなさい。'
    },
    '8': {
        'base_high': '【本質】この世界における物質的な豊かさを根こそぎ引き寄せる、強烈な引力の星です。<br>【深掘り】目標達成への執念と、結果をもぎ取る実行力。あなたは社会的成功を宿命づけられた、<span style="color:#d4af37">選ばれし覇者</span>の一人です。',
        'base_low': '【本質】豊かさを受け取ることに対する、無意識のブロックが存在します。<br>【深掘り】利益への執着が薄く、チャンスを他人に譲ってしまうお人好し。結果として、あなたの手元には何も残らないという運命を繰り返しています。',
        'today_high': '【波動解析】成功へのベクトルが一直線に揃い、物質的豊かさが具現化する波形です。<br>【深掘り】努力が今日ついに『利益』となって還元されます。遠慮は一切不要です。<br>【本日の指針】<span style="color:#d4af37">貪欲</span>になりなさい。すべてを刈り取りなさい。',
        'today_low': '【波動解析】金運の波が完全に逆流し、富が逃げていく危険な星回りです。<br>【深掘り】利益を追求すればするほど、底なし沼にハマる日。予期せぬ出費があなたを嘲笑うでしょう。<br>【本日の指針】利益を手放し、他者への<span style="color:#ff4b4b">奉仕</span>にのみ専念しなさい。'
    },
    '9': {
        'base_high': '【本質】既存の常識を破壊し、新たな世界の基準を創り出す支配者の星です。<br>【深掘り】圧倒的なオーラを放ち、無意識のうちに他者をひれ伏させます。群衆を導く<span style="color:#d4af37">天性のカリスマ</span>、それがあなたの真の姿です。',
        'base_low': '【本質】自らに宿る強大な力を恐れ、自意識の檻に閉じこもる傾向があります。<br>【深掘り】他者の視線を恐れ、周囲に合わせて自分らしさを去勢しています。本来の規格外の個性を封印しているため、魂が窒息状態にあります。',
        'today_high': '【波動解析】カリスマの波動が限界突破し、周囲の空間を完全に支配する日です。<br>【深掘り】誰の顔色を窺う必要もありません。あなたの意志が法となり、一挙手一投足が時代の基準となります。<br>【本日の指針】圧倒的な自信を纏い、<span style="color:#d4af37">王として</span>世界に君臨しなさい。',
        'today_low': '【波動解析】あなたの放つ強い波動が、既存の権力と激しく衝突する警告波形です。<br>【深掘り】今日、あなたが前に出れば、より強大な力を持つ人物の逆鱗に触れ、徹底的に叩き潰される危険があります。<br>【本日の指針】気配を消し、<span style="color:#ff4b4b">ナンバーツー</span>として狡猾に立ち回りなさい。'
    }
}

# --- 2. CSSリッチ化ハック ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;700&display=swap" rel="stylesheet">
<style>
/* 全体背景：深淵へのグラデーション */
.stApp {
    background: linear-gradient(180deg, #050505 0%, #0a0a15 100%) !important;
    color: #e0e0e0 !important;
    font-family: 'Shippori Mincho', serif !important;
}

/* 高級フォントの適用 */
h1, h2, h3, h4, p, span, div, .stButton {
    font-family: 'Shippori Mincho', serif !important;
}

/* タイトル周辺の発光 */
h1 { 
    color: #d4af37 !important; 
    text-align: center; 
    font-size: 3em !important; 
    text-shadow: 0 0 20px rgba(212,175,55,0.5); 
    margin-bottom: 0px !important;
}
.sub-title { 
    text-align: center; 
    color: #a0a0a0; 
    font-size: 1.2em; 
    margin-bottom: 35px; 
    letter-spacing: 0.2em; 
}

/* 警告文のリッチ化 */
.once-notice { 
    color: #ff4b4b; 
    text-align: center; 
    padding: 15px; 
    border: 1px solid #441111; 
    background: rgba(40, 5, 5, 0.5); 
    border-radius: 8px;
    box-shadow: inset 0 0 10px rgba(255,75,75,0.1);
    margin-bottom: 30px;
}

/* 入力セクションの装飾 */
.stTextInput input, .stDateInput input, .stSelectbox div {
    background-color: #111 !important;
    border: 1px solid #d4af3744 !important;
    color: #d4af37 !important;
}

/* 黄金のボタン */
.stButton>button {
    background: linear-gradient(135deg, #8a6d3b 0%, #d4af37 50%, #8a6d3b 100%) !important;
    color: #000 !important;
    font-weight: bold !important;
    border: none !important;
    padding: 12px 0 !important;
    box-shadow: 0 0 20px rgba(212,175,55,0.3) !important;
    transition: 0.4s !important;
}
.stButton>button:hover {
    box-shadow: 0 0 40px rgba(212,175,55,0.6) !important;
    letter-spacing: 0.2em;
}

/* プログレスバーの装飾 */
.stProgress > div > div > div > div {
    background-color: #d4af37 !important;
}

/* 解析結果のカード */
.stExpander {
    background: rgba(20, 20, 25, 0.5) !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
}
.detail-label { color: #d4af37; font-weight: bold; border-left: 3px solid #d4af37; padding-left: 12px; margin-bottom: 8px; margin-top: 15px;}
.detail-label-today { color: #a0c4ff; font-weight: bold; border-left: 3px solid #a0c4ff; padding-left: 12px; margin-bottom: 8px; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

# --- 3. UI構築 ---
st.markdown("<h1>🔮 RESONANCE</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>絶対宿命律が、隠されたあなたの本質を炙り出す</p>", unsafe_allow_html=True)
st.markdown('<div class="once-notice">⚠️ 1日1度、1回目の判定のみが真実です。<br>2回目以降の波形は宇宙のノイズにより歪みます。</div>', unsafe_allow_html=True)

with st.container():
    st.subheader("【魂の基本情報】")
    col1, col2 = st.columns(2)
    with col1:
        last_name = st.text_input("姓", placeholder="例：山田")
        first_name = st.text_input("名", placeholder="例：太郎")
    with col2:
        last_name_alpha = st.text_input("姓（ローマ字）", placeholder="例：YAMADA")
        first_name_alpha = st.text_input("名（ローマ字）", placeholder="例：TARO")

    dob = st.date_input("生誕の日", min_value=datetime.date(1900, 1, 1), value=datetime.date(2000, 1, 1))

    st.subheader("【運命の深淵パラメータ】")
    col3, col4 = st.columns(2)
    with col3:
        time_unknown = st.checkbox("生誕の時刻が不明")
        tob = st.time_input("生誕の時刻", value=datetime.time(12, 0), step=60, disabled=time_unknown)
    with col4:
        blood_type = st.selectbox("血の盟約（血液型）", ["A型", "B型", "O型", "AB型", "不明"], index=4)

    predict_button = st.button("運命波動を解析する")

def get_numeric_value(text, stroke_dict):
    s = ""
    for char in text:
        char_upper = char.upper()
        if char_upper in stroke_dict:
            s += stroke_dict[char_upper]
        else:
            s += str(ord(char))
    return int(s) if s else 0

# --- 4. 解析・演出ロジック ---
if predict_button:
    # --- 演出：「溜め」のプログレスバー ---
    status_text = st.empty()
    progress_bar = st.progress(0)
    messages = ["深淵の記憶を照合中...", "星の配置を再構成中...", "運命の糸を紡いでいます...", "絶対宿命律と同期完了。"]
    
    for i in range(100):
        time.sleep(0.03) # 合計約3秒の溜め
        progress_bar.progress(i + 1)
        if i < 30: status_text.markdown(f"<p style='text-align:center;'>{messages[0]}</p>", unsafe_allow_html=True)
        elif i < 60: status_text.markdown(f"<p style='text-align:center;'>{messages[1]}</p>", unsafe_allow_html=True)
        elif i < 90: status_text.markdown(f"<p style='text-align:center;'>{messages[2]}</p>", unsafe_allow_html=True)
        else: status_text.markdown(f"<p style='text-align:center;'>{messages[3]}</p>", unsafe_allow_html=True)
    
    time.sleep(0.5)
    status_text.empty()
    progress_bar.empty()

    # --- コアロジック ---
    JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
    now = datetime.datetime.now(JST)

    # 1. ベース計算
    year = dob.year
    month_day = int(dob.strftime('%m%d'))
    val_dob = abs(year - month_day)
    val_kanji = abs(get_numeric_value(last_name, hiragana_strokes) - get_numeric_value(first_name, hiragana_strokes))
    val_alpha = abs(get_numeric_value(first_name_alpha, alphabet_strokes) - get_numeric_value(last_name_alpha, alphabet_strokes))
    hash_base = f"{val_dob}{val_kanji}{val_alpha}"
    counts_base = Counter(hash_base)

    raw_scores_base = {}
    for i in range(10):
        digit = str(i)
        seed = f"{hash_base}_base_{i}"
        noise = (int(hashlib.md5(seed.encode()).hexdigest()[:8], 16) % 100) / 100.0
        raw_scores_base[digit] = counts_base.get(digit, 0) + noise
    max_raw_base = max(raw_scores_base.values()) if max(raw_scores_base.values()) > 0 else 1.0
    scores_base = {k: (v / max_raw_base) * 5.0 * min(max_raw_base / 3.0, 1.0) for k, v in raw_scores_base.items()}

    # 2. 現在計算
    hash_now = hash_base + now.strftime('%Y%m%d%H%M')
    counts_now = Counter(hash_now)
    raw_scores_now = {}
    for i in range(10):
        digit = str(i)
        seed = f"{hash_now}_now_{i}"
        noise = (int(hashlib.md5(seed.encode()).hexdigest()[:8], 16) % 100) / 100.0
        raw_scores_now[digit] = counts_now.get(digit, 0) + noise
    max_raw_now = max(raw_scores_now.values()) if max(raw_scores_now.values()) > 0 else 1.0
    scores_now = {k: (v / max_raw_now) * 5.0 * min(max_raw_now / 4.0, 1.0) for k, v in raw_scores_now.items()}

    # 3. デバフ
    time_str = "" if time_unknown else tob.strftime('%H%M')
    blood_str = "" if blood_type.startswith("不明") else blood_type_strokes.get(blood_type, "")
    for i in range(10):
        d = str(i)
        p = 0.5 if (time_unknown or d in time_str) else 0.0
        p += 0.5 if (blood_type.startswith("不明") or d in blood_str) else 0.0
        scores_base[d] = max(0.0, scores_base[d] - p)
        scores_now[d] = max(0.0, scores_now[d] - p)

    # --- グラフ表示 ---
    labels = [fortune_map[str(i)] for i in range(10)]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[scores_base[str(i)] for i in range(10)] + [scores_base['0']], theta=labels + [labels[0]], fill='none', line=dict(color='#444', width=1.5, dash='dot'), name='本来の宿命'))
    fig.add_trace(go.Scatterpolar(r=[scores_now[str(i)] for i in range(10)] + [scores_now['0']], theta=labels + [labels[0]], fill='toself', fillcolor='rgba(212, 175, 55, 0.2)', line=dict(color='#d4af37', width=2.5), marker=dict(color='#d4af37', size=10), name='今の運勢'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5], tickvals=[1,2,3,4,5], tickcolor="#333", gridcolor="#222"), angularaxis=dict(gridcolor="#222", tickfont=dict(size=14, color="#d4af37"))), showlegend=True, legend=dict(font=dict(color="#eee")), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=60, r=60, t=40, b=40))
    
    st.plotly_chart(fig, use_container_width=True)

    # --- 詳細解析表示 ---
    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    base_max = max(scores_base.values())
    final_max = max(scores_now.values())
    b_tops = [fortune_map[k] for k, v in scores_base.items() if v == base_max]
    f_tops = [fortune_map[k] for k, v in scores_now.items() if v == final_max]
    
    st.markdown(f"<h4 style='color: #888; text-align:center;'>👁️ 生来の最大の武器：{' / '.join(b_tops)} ({base_max:.2f})</h4>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color: #d4af37; text-align:center; text-shadow: 0 0 10px #d4af3744;'>👑 現在の最強ステータス：{' / '.join(f_tops)} ({final_max:.2f})</h2>", unsafe_allow_html=True)

    sorted_keys = sorted(scores_now.keys(), key=lambda x: scores_now[x], reverse=True)
    for k in sorted_keys:
        b_s, f_s = scores_base[k], scores_now[k]
        b_t = trait_details[k]['base_high'] if b_s >= 3.0 else trait_details[k]['base_low']
        f_t = trait_details[k]['today_high'] if f_s >= 3.0 else trait_details[k]['today_low']
        with st.expander(f"■ {fortune_map[k]} （本来: {b_s:.2f} ➔ 現在: {f_s:.2f}）"):
            st.markdown(f"<div class='detail-label'>本来の宿命</div><div class='detail-text'>{b_t}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='detail-label-today'>現在の運勢</div><div class='detail-text'>{f_t}</div>", unsafe_allow_html=True)
