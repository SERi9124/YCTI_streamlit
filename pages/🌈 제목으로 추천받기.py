import streamlit as st
import pandas as pd
import numpy as np
import requests
import io


st.set_page_config(
    layout="wide",
    page_icon="π§ββοΈ",
    page_title="μ λͺ©μΌλ‘ μΆμ²λ°κΈ°"
)

# νμ΄μ§ μ λͺ©
st.title(":revolving_hearts: μ λͺ©μΌλ‘ νμΈνλ λ΄ μ·¨ν₯")


web_title = pd.read_csv('data/toon_list.csv')

info_area = st.empty()
i1 = info_area.container()
with i1:
    st.markdown("β» __λͺ¨λΈ λ‘λμ μ½ 30μ΄ μμ__ λ©λλ€.")
    st.write("")
    st.write("")


    st.markdown("π§ μ λͺ©μ **:green[μ ν(μλ ₯)]** ν΄μ£ΌμΈμ π§ββοΈπ§ββοΈ")
    options = st.multiselect("β» μ΅λ **:red[3κ°μ μΉν°μ μ ν]** ν  μ μμ΅λλ€. ", web_title, max_selections=3)

    select_title = []

    for x in options:
        select_title.append(x)
        title_re = x.replace("\\", "/")
    
    st.text('''π§ 22.12.28 κΈ°μ€ μ°μ¬ μ€μΈ μΉν°μΌλ‘ κ²μ λ° μΆμ²λκ³  μμ΅λλ€.''')
    
    ac_button = st.button('μΉν° μΆμ²λ°κΈ°!')
@st.cache
def load_thumb(url):
    rep_thumb = requests.get(url)
    rep_thumb.raise_for_status()
    rep_thumb = np.load(io.BytesIO(rep_thumb.content))
    
    return rep_thumb

thumb_url = 'https://github.com/SERi9124/YCTI_streamlit/blob/4dcccfd048e6971afb4878906456dd3528a3b719/data/cropped_img.npy?raw=true'
rep_thumb = load_thumb(thumb_url)

data_name = 'https://github.com/SERi9124/YCTI_streamlit/blob/4dcccfd048e6971afb4878906456dd3528a3b719/data/np_embeddings_efficientnet_v2.npy?raw=true'
label_name = 'https://github.com/SERi9124/YCTI_streamlit/blob/4dcccfd048e6971afb4878906456dd3528a3b719/data/np_labels_efficientnet_v2.npy?raw=true'

@st.cache(show_spinner = True)
def load_data(data_name, label_name):    
    # data = np.load(data_name, allow_pickle = True)
    data = requests.get(data_name)
    data.raise_for_status()
    data = np.load(io.BytesIO(data.content))
    
    # np_label = np.load(label_name)
    np_label = requests.get(label_name)
    np_label.raise_for_status()
    np_label = np.load(io.BytesIO(np_label.content))
    
    # df = pd.DataFrame(pd.Series(data.tolist()),
    #                         columns=['embedding'])
    # df['embedding'] = df['embedding'].map(np.asarray)
    # df['label'] = np_label
    return data, np_label

# df = load_data(data_name, label_name)
embedding, labels = load_data(data_name, label_name)

@st.cache(show_spinner = False)
def rank_similarity(embedding, labels, webtoon_ids, top = 10):    
    
    # df_temp = μ΄λ―Έμ§ λ³ label μ λ³΄μ μ μ¬λ κ³μ° κ²°κ³Όκ° λ΄κΈΈ λ°μ΄ν°νλ μ μ μΈ
    df_temp = pd.DataFrame(labels, columns = ['label'])
    
    # chosen_index: μ νν μΉν°λ€μ λν΄ μ΄λ―Έμ§λ₯Ό 3μ₯μ© κ³¨λΌμ€ ν μΈλ±μ€λ₯Ό λ΄μμ€λ€.
    # μΆν μ μ¬λ κ³μ° κΈ°μ€ λ²‘ν°μ μΈλ±μ€κ° λ  κ²
    chosen_index = []
    for webtoon in webtoon_ids:
        where_label = np.where(labels == webtoon)[0]
        chosen_index.extend(np.random.choice(where_label, 3, replace = False))
    
    # μ μ¬λ κ³μ° κ²°κ³Όμ ν©μ λ΄μ array μμ±
    result = np.zeros_like(labels, dtype=float)
    
    # μ μ¬λ κ³μ°
    for b in chosen_index:

        # 0μΌλ‘ λλμ΄μ§λ κ²½μ° λ°©μ§
        np.seterr(invalid='ignore')

        # cosine similarity κ³μ°, ν΄μλ‘ μ’λ€ => μμλ₯Ό λΆμλ€.
        # λ¬Έμ  : λ°°μ΄μ΄ μ΄μ°¨μ λ°°μ΄μ => κ³μ° μ μ΄μ°¨μ λ°°μ΄μμ νΉ νλμ©μ μ¬μ©ν΄μΌνλ€λ λ».
        # μλ¬΄λ¦¬ μ°Ύμλ΄λ λ°λ³΅λ¬Έλ°μ λ΅μ΄ μλ€.
        # μλλ μ’ λλ¦¬κ² μ§λ§!

        cosine_sim = lambda a : np.divide(
                -np.dot(a, embedding[b]),
                np.linalg.norm(a) * np.linalg.norm(embedding[b]))

        sim = np.zeros_like(labels, dtype=float)
        for i in range(len(embedding)):
            sim[i] = cosine_sim(embedding[i])

        result += sim
    
    df_temp['order'] = result
    df_temp = df_temp.sort_values(by='order')\
                    .drop_duplicates('label')
    #                     .drop('order', axis=1)\
    df_temp = df_temp[~df_temp['label'].isin(webtoon_ids)]
    
    return df_temp.iloc[:10]


def show_recommendations(df, webtoon_ids, rep_thumb):
    
    toon_list = pd.read_csv("data/toon_list.csv").T
    webtoon = pd.read_csv("data/webtoon.csv")

    wt_name = []
    wt_titleId = []
    url = []
    
    for label in df['label']:
        # labelμ μ μ₯ labelμ μ μ¬λμΉν° indexλ²νΈ
        wt_name.append(label)
        # st.write(label)
        # μΆμ²νλμΉν°μ titleId
        wt_titleId.append(webtoon[webtoon["title"].isin(toon_list[label])]["titleId"].values[0])
        # st.write(webtoon[webtoon["title"].isin(toon_list[label])]["titleId"].values)
        url.append(webtoon[webtoon["title"].isin(toon_list[label])]["url"].values[0])
    
    st.balloons()
    
    st.markdown('---')
    col1, col2 = st.columns([9, 1])
    with col1:
        st.header("ππ μΆμ²νλ μΉν° ππ")
    with col2:
        re_button = st.button("λ€μ μΆμ²λ°κΈ°")
    st.write("")

    col1, col2, col3, col4, col5 = st.columns([1, 3, 0.5, 3, 1])

    # col1, col2 = st.columns(2)

    with col2:
        # st.header("1οΈβ£ μΆμ²μΉν° ")
        st.subheader("1οΈβ£" + webtoon.loc[webtoon["titleId"] == wt_titleId[0]]["title"].values[0])
        st.image(rep_thumb[wt_name[0]])
        # st.write('μ λͺ© : ',webtoon.loc[webtoon["titleId"] == wt_titleId[0]]["title"].values[0])
        st.write(':pencil2: μκ° : ',webtoon.loc[webtoon["titleId"] == wt_titleId[0]]["writer"].values[0])
        st.write(':face_with_monocle: μ₯λ₯΄ : ',webtoon.loc[webtoon["titleId"] == wt_titleId[0]]["genre"].values[0])
        st.write(':calendar: μ°μ¬μμΌ : ',webtoon.loc[webtoon["titleId"] == wt_titleId[0]]["serial_day"].values[0])  
        st.markdown(f'[λ³΄λ¬κ°κΈ° :dash::dash:]({url[0]})')
        st.write("")      
    with col4:
        # st.header("2οΈβ£μΆμ²μΉν°")
        st.subheader("2οΈβ£" + webtoon.loc[webtoon["titleId"] == wt_titleId[1]]["title"].values[0])
        st.image(rep_thumb[wt_name[1]]) # μΆμ²
        # st.write('μ λͺ© : ',webtoon.loc[webtoon["titleId"] == wt_titleId[1]]["title"].values[0])
        st.write(':pencil2: μκ° : ',webtoon.loc[webtoon["titleId"] == wt_titleId[1]]["writer"].values[0])
        st.write(':face_with_monocle: μ₯λ₯΄ : ',webtoon.loc[webtoon["titleId"] == wt_titleId[1]]["genre"].values[0])
        st.write(':calendar: μ°μ¬μμΌ : ',webtoon.loc[webtoon["titleId"] == wt_titleId[1]]["serial_day"].values[0])
        st.markdown(f'[λ³΄λ¬κ°κΈ° :dash::dash:]({url[1]})')
        st.write("")

    col3, col4, col5 = st.columns(3)
    st.write("")
    st.write("")

    with col3:
        # st.header("3οΈβ£ μΆμ²μΉν° ")
        st.subheader("3οΈβ£" + webtoon.loc[webtoon["titleId"] == wt_titleId[2]]["title"].values[0])
        st.image(rep_thumb[wt_name[2]]) # μΆμ²
        # st.write('μ λͺ© : ',webtoon.loc[webtoon["titleId"] == wt_titleId[2]]["title"].values[0])
        st.write(':pencil2: μκ° : ',webtoon.loc[webtoon["titleId"] == wt_titleId[2]]["writer"].values[0])
        st.write(':face_with_monocle: μ₯λ₯΄ : ',webtoon.loc[webtoon["titleId"] == wt_titleId[2]]["genre"].values[0])
        st.write(':calendar: μ°μ¬μμΌ : ',webtoon.loc[webtoon["titleId"] == wt_titleId[2]]["serial_day"].values[0]) 
        st.markdown(f'[λ³΄λ¬κ°κΈ° :dash::dash:]({url[2]})')
        # st.write("")       
    with col4:
        # st.header("4οΈβ£μΆμ²μΉν°")
        st.subheader("4οΈβ£" + webtoon.loc[webtoon["titleId"] == wt_titleId[3]]["title"].values[0])
        st.image(rep_thumb[wt_name[3]]) # μΆμ²
        # st.write('μ λͺ© : ',webtoon.loc[webtoon["titleId"] == wt_titleId[3]]["title"].values[0])
        st.write(':pencil2: μκ° : ',webtoon.loc[webtoon["titleId"] == wt_titleId[3]]["writer"].values[0])
        st.write(':face_with_monocle: μ₯λ₯΄ : ',webtoon.loc[webtoon["titleId"] == wt_titleId[3]]["genre"].values[0])
        st.write(':calendar: μ°μ¬μμΌ : ',webtoon.loc[webtoon["titleId"] == wt_titleId[3]]["serial_day"].values[0])
        st.markdown(f'[λ³΄λ¬κ°κΈ° :dash::dash:]({url[3]})')
        # st.write("")
    with col5:
        # st.header("5οΈβ£μΆμ²μΉν°")
        st.subheader("5οΈβ£" + webtoon.loc[webtoon["titleId"] == wt_titleId[4]]["title"].values[0])
        st.image(rep_thumb[wt_name[4]]) # μΆμ²
        # st.write('μ λͺ© : ',webtoon.loc[webtoon["titleId"] == wt_titleId[4]]["title"].values[0])
        st.write(':pencil2: μκ° : ',webtoon.loc[webtoon["titleId"] == wt_titleId[4]]["writer"].values[0])
        st.write(':face_with_monocle: μ₯λ₯΄ : ',webtoon.loc[webtoon["titleId"] == wt_titleId[4]]["genre"].values[0])
        st.write(':calendar: μ°μ¬μμΌ : ',webtoon.loc[webtoon["titleId"] == wt_titleId[4]]["serial_day"].values[0])
        st.markdown(f'[λ³΄λ¬κ°κΈ° :dash::dash:]({url[4]})')
        # st.write("")

    if re_button:
        info_area.empty()
        st.experimental_memo.clear()
        st.experimental_rerun()

@st.experimental_memo(show_spinner = False)
def title_id(select_title):
    user_pick = []
    for i in select_title:
        user_pick.append(web_title[web_title['0'] == i].index.item())
    return user_pick

# st.markdown('---')

if ac_button:
    info_area.empty()
    user_pick = title_id(select_title)
    # df_rec = rank_similarity(df,user_pick,mode='l2-norm',top=10)

    with st.spinner(f'**{", ".join(select_title)}** μ κ·Έλ¦Όμ²΄κ° μ μ¬ν μΉν°μ κ²μμ€μλλ€.'):
        wait_area = st.empty()
        p1 = wait_area.container()
        with p1:
            st.image("img/plz_wait.jpg")
        df_rec = rank_similarity(embedding, labels, user_pick)
        wait_area.empty()
        show_recommendations(df_rec, user_pick, rep_thumb)
        st.markdown('---')
