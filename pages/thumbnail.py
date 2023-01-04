import streamlit as st
import pandas as pd
import numpy as np
import random
from glob import glob
from PIL import Image
import requests
import io

st.set_page_config(
    layout="wide")



# 페이지 제목
st.title("💘 썸네일로 확인하는 내 취향")

st.write("")
st.write("")


web_title = pd.read_csv('https://raw.githubusercontent.com/SERi9124/YCTI_streamlit/main/data/toon_list.csv')
# rep_thumb = np.load('https://github.com/SERi9124/YCTI_streamlit/blob/4dcccfd048e6971afb4878906456dd3528a3b719/data/cropped_img.npy?raw=true', allow_pickle=True)          
@st.cache
def load_thumb(url):
    rep_thumb = requests.get(url)
    rep_thumb.raise_for_status()
    rep_thumb = np.load(io.BytesIO(rep_thumb.content))
    
    return rep_thumb

# st.write(web_title.iloc[0].values[0])

data_name = 'https://github.com/SERi9124/YCTI_streamlit/blob/4dcccfd048e6971afb4878906456dd3528a3b719/data/np_embeddings_efficientnet_v2.npy?raw=true'
# data_name = requests.get('https://github.com/SERi9124/YCTI_streamlit/blob/4dcccfd048e6971afb4878906456dd3528a3b719/data/np_embeddings_efficientnet_v2.npy?raw=true')
# data_name.raise_for_status()
# data_name = np.load(io.BytesIO(data_name.content))

label_name = 'https://github.com/SERi9124/YCTI_streamlit/blob/4dcccfd048e6971afb4878906456dd3528a3b719/data/np_labels_efficientnet_v2.npy?raw=true'
# label_name = requests.get('https://github.com/SERi9124/YCTI_streamlit/blob/4dcccfd048e6971afb4878906456dd3528a3b719/data/np_labels_efficientnet_v2.npy?raw=true')
# label_name.raise_for_status()
# label_name = np.load(io.BytesIO(label_name.content))
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
    
    # df_temp = 이미지 별 label 정보와 유사도 계산 결과가 담길 데이터프레임 선언
    df_temp = pd.DataFrame(labels, columns = ['label'])
    
    # chosen_index: 선택한 웹툰들에 대해 이미지를 3장씩 골라준 후 인덱스를 담아준다.
    # 추후 유사도 계산 기준 벡터의 인덱스가 될 것
    chosen_index = []
    for webtoon in webtoon_ids:
        where_label = np.where(labels == webtoon)[0]
        chosen_index.extend(np.random.choice(where_label, 3, replace = False))
    
    # 유사도 계산 결과의 합을 담을 array 생성
    result = np.zeros_like(labels, dtype=float)
    
    # 유사도 계산
    for b in chosen_index:

        # 0으로 나누어지는 경우 방지
        np.seterr(invalid='ignore')

        # cosine similarity 계산, 클수록 좋다 => 음수를 붙였다.
        # 문제 : 배열이 이차원 배열임 => 계산 시 이차원 배열에서 헹 하나씩을 사용해야한다는 뜻.
        # 아무리 찾아봐도 반복문밖에 답이 없다.
        # 속도는 좀 느리겠지만!

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
    
    toon_list = pd.read_csv("https://raw.githubusercontent.com/SERi9124/YCTI_streamlit/main/data/toon_list.csv").T
    webtoon = pd.read_csv("https://raw.githubusercontent.com/SERi9124/YCTI_streamlit/main/data/webtoon.csv")

    wt_name = []
    wt_titleId = []
    url = []
    
    for label in df['label']:
        # label을 저장 label은 유사도웹툰 index번호
        wt_name.append(label)
        # st.write(label)
        # 추천하는웹툰의 titleId
        wt_titleId.append(webtoon[webtoon["title"].isin(toon_list[label])]["titleId"].values[0])
        # st.write(webtoon[webtoon["title"].isin(toon_list[label])]["titleId"].values)
        url.append(webtoon[webtoon["title"].isin(toon_list[label])]["url"].values[0])
    
    st.markdown('---')
    # col1, col2 = st.columns([5, 5])
    # with col1:
    st.header("🌞🌞 추천하는 웹툰 🌞🌞")
        # re_button = st.button("") 
    st.write("")

    col1, col2, col3, col4, col5 = st.columns([1, 3, 0.5, 3, 1])

    with col2:
        # st.header("1️⃣ 추천웹툰 ")
        st.subheader("1️⃣" + webtoon.loc[webtoon["titleId"] == wt_titleId[0]]["title"].values[0])
        st.image(rep_thumb[wt_name[0]])
        # st.write('제목 : ',webtoon.loc[webtoon["titleId"] == wt_titleId[0]]["title"].values[0])
        st.write(':pencil2: **작가** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[0]]["writer"].values[0])
        st.write(':face_with_monocle: **장르** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[0]]["genre"].values[0])
        st.write(':calendar: **연재요일** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[0]]["serial_day"].values[0])  
        st.markdown(f'[**보러가기** :dash::dash:]({url[0]})')
        st.write("")      
    with col4:
        # st.header("2️⃣추천웹툰")
        st.subheader("2️⃣" + webtoon.loc[webtoon["titleId"] == wt_titleId[1]]["title"].values[0])
        st.image(rep_thumb[wt_name[1]]) # 추천
        # st.write('제목 : ',webtoon.loc[webtoon["titleId"] == wt_titleId[1]]["title"].values[0])
        st.write(':pencil2: **작가** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[1]]["writer"].values[0])
        st.write(':face_with_monocle: **장르** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[1]]["genre"].values[0])
        st.write(':calendar: **연재요일** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[1]]["serial_day"].values[0])
        st.markdown(f'[**보러가기** :dash::dash:]({url[1]})')
        st.write("")

    col3, col4, col5 = st.columns(3)
    st.write("")
    st.write("")

    with col3:
        # st.header("3️⃣ 추천웹툰 ")
        st.subheader("3️⃣" + webtoon.loc[webtoon["titleId"] == wt_titleId[2]]["title"].values[0])
        st.image(rep_thumb[wt_name[2]]) # 추천
        # st.write('제목 : ',webtoon.loc[webtoon["titleId"] == wt_titleId[2]]["title"].values[0])
        st.write(':pencil2: **작가** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[2]]["writer"].values[0])
        st.write(':face_with_monocle: **장르** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[2]]["genre"].values[0])
        st.write(':calendar: **연재요일** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[2]]["serial_day"].values[0]) 
        st.markdown(f'[**보러가기** :dash::dash:]({url[2]})')
        # st.write("")       
    with col4:
        # st.header("4️⃣추천웹툰")
        st.subheader("4️⃣" + webtoon.loc[webtoon["titleId"] == wt_titleId[3]]["title"].values[0])
        st.image(rep_thumb[wt_name[3]]) # 추천
        # st.write('제목 : ',webtoon.loc[webtoon["titleId"] == wt_titleId[3]]["title"].values[0])
        st.write(':pencil2: **작가** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[3]]["writer"].values[0])
        st.write(':face_with_monocle: **장르** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[3]]["genre"].values[0])
        st.write(':calendar: **연재요일** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[3]]["serial_day"].values[0])
        st.markdown(f'[**보러가기** :dash::dash:]({url[3]})')
        # st.write("")
    with col5:
        # st.header("5️⃣추천웹툰")
        st.subheader("5️⃣" + webtoon.loc[webtoon["titleId"] == wt_titleId[4]]["title"].values[0])
        st.image(rep_thumb[wt_name[4]]) # 추천
        # st.write('제목 : ',webtoon.loc[webtoon["titleId"] == wt_titleId[4]]["title"].values[0])
        st.write(':pencil2: **작가** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[4]]["writer"].values[0])
        st.write(':face_with_monocle: **장르** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[4]]["genre"].values[0])
        st.write(':calendar: **연재요일** : ',webtoon.loc[webtoon["titleId"] == wt_titleId[4]]["serial_day"].values[0])
        st.markdown(f'[**보러가기** :dash::dash:]({url[4]})')

@st.cache
def title_id(select_title):
    user_pick = []
    for i in select_title:
        user_pick.append(web_title[web_title['0'] == i].index.item())
    return user_pick


# 세션 스테이트 초기화
if "next_button1" not in st.session_state:
    st.session_state["next_button1"] = False 
if "next_button2" not in st.session_state:
    st.session_state["next_button2"] = False
if "finish_button" not in st.session_state:
    st.session_state["finish_button"] = False
if "clear_button" not in st.session_state:
    st.session_state["clear_button"] = False


# 랜덤으로 웹툰 선택해주는 함수
# 캐시 적용(적용 안할 시 체크박스 클릭시마다 초기화)
@st.experimental_memo
def make_idx():
    idx_list = random.sample(range(0, 1297), 18)
    return idx_list

idx_list = make_idx()

select_title = []

# 진행 바 선언
info_area = st.empty()
i1 = info_area.container()

with i1:
    st.text("⭐ 최소 하나는 필수로 선택해주세요.")
    my_bar = st.progress(1/3) # 진행바

select_area = st.empty() # 구역 설정
c1, c2, c3 = select_area.columns([3, 3, 3])



# 페이지마다 썸네일 보여주는 함수

def show_thumbs(select_area, page):

    select_area.empty() # 구역 설정
    c1, c2, c3 = select_area.columns([3, 3, 3])

    # 1/3
    with c2:
        st.write("")
        
        toon3 = st.checkbox(web_title.iloc[idx_list[6 * page + 2]].values[0], key = 3 + (6 * page))
        if toon3: select_title.append(web_title.iloc[idx_list[6 * page + 2]].values[0])
        st.write("")  
        st.image(Image.fromarray(rep_thumb[idx_list[6 * page + 2]]))

        st.write("")
        st.write("")

        toon4 = st.checkbox(web_title.iloc[idx_list[6 * page + 3]].values[0], key = 4 + (6 * page))
        if toon4: select_title.append(web_title.iloc[idx_list[6 * page + 3]].values[0])
        st.write("")
        st.image(Image.fromarray(rep_thumb[idx_list[6 * page + 3]]))
        

    with c3:
        st.write("")
        
        toon5 = st.checkbox(web_title.iloc[idx_list[6 * page + 4]].values[0], key = 5 + (6 * page))
        if toon5: select_title.append(web_title.iloc[idx_list[6 * page + 4]].values[0])
        st.write("")
        st.image(Image.fromarray(rep_thumb[idx_list[6 * page + 4]]))

        st.write("")
        st.write("")

        toon6 = st.checkbox(web_title.iloc[idx_list[6 * page + 5]].values[0], key = 6 + (6 * page))
        if toon6: select_title.append(web_title.iloc[idx_list[6 * page + 5]].values[0])
        st.write("")
        st.image(Image.fromarray(rep_thumb[idx_list[6 * page + 5]]))
        
    with c1:
        st.write("")
        
        toon1 = st.checkbox(web_title.iloc[idx_list[6 * page + 0]].values[0], key = 1 + (6 * page))
        if toon1: select_title.append(web_title.iloc[idx_list[6 * page + 0]].values[0])
        st.write("")
        st.image(Image.fromarray(rep_thumb[idx_list[6 * page + 0]]))
        
        st.write("")
        st.write("")
        
        toon2 = st.checkbox(web_title.iloc[idx_list[6 * page + 1]].values[0], key = 2 + (6 * page))
        if toon2: select_title.append(web_title.iloc[idx_list[6 * page + 1]].values[0])
        st.write("")
        st.image(Image.fromarray(rep_thumb[idx_list[6 * page + 1]]))

        if page == 0:
            next_button1 = st.button("next", disabled=(toon1 + toon2 + toon3 + toon4 + toon5 + toon6 < 1), key="bt1")
            if next_button1:
                st.session_state["next_button1"] = True 
        
        elif page == 1:
            next_button2 = st.button("next", disabled=(toon1 + toon2 + toon3 + toon4 + toon5 + toon6 < 1), key="bt2")
            if next_button2:
                st.session_state["next_button2"] = True
                
        elif page == 2:
            finish_button = st.button("finish!", disabled=(toon1 + toon2 + toon3 + toon4 + toon5 + toon6 < 1))
            if finish_button:
                st.session_state["finish_button"] = True


# 동작부 : 버튼 누를때마다 if 문으로 동작
# 이때 session_state 사용

if ~(st.session_state["next_button1"] & st.session_state["next_button2"] & st.session_state["finish_button"]):
    show_thumbs(select_area, 0)

if st.session_state["next_button1"]:
    idx_list = make_idx()
    # select_area = st.empty()
    my_bar.progress(2/3)
    show_thumbs(select_area, 1)
    
if st.session_state['next_button2']:
    idx_list = make_idx()
    # select_area = st.empty()
    my_bar.progress(3/3)
    show_thumbs(select_area, 2)

if st.session_state['finish_button']:
    info_area.empty()
    select_area.empty()
    
    user_pick = title_id(select_title)

    with st.spinner(f'{select_title} 와 그림체가 유사한 웹툰을 검색중입니다.'): 
        df_rec = rank_similarity(df,user_pick,mode='l2-norm',top=10)
        show_recommendations(df_rec, user_pick, rep_thumb)
