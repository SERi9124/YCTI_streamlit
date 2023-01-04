import streamlit as st
from PIL import Image


# 그림체 기반 웹툰 추천 서비스
# 이용자가 즐겨보는 웹툰의 제목을 입력 받거나 썸네일을 선택 => 해당 정보를 기반으로 웹툰 추천

# 탭 설정
st.set_page_config(
    layout="wide",
    page_title="You Can Toon It",
    page_icon="img/logo.jpg"
)

# 상단 프로젝트 정보 입력
c1, c2 = st.columns([6.5, 3.5])
with c1:
    st.header("💪 You can toon it ✨")
    st.write("**🦁 멋쟁이 사자처럼 AI SCHOOL 7기**")

    st.markdown("[박경택](https://github.com/cryptnomy), [박예령](https://github.com/hi-Heidi), [손진선](https://github.com/Son-jinseon), [임종우](https://github.com/imngooh), [정세리](https://github.com/SERi9124)")
    
with c2:
    st.image(Image.open("https://github.com/SERi9124/YCTI_streamlit/blob/main/img/%EB%A1%9C%EA%B3%A0.jpg?raw=true"))
    # st.image(Image.open("img/photo1.jpg"))
    # st.markdown("[![YCTI](http://localhost:8501/media/30156d2a5e3b4d37c9e7bb9fc72c2831c0f25f6185d2f5c5dab6a91e.jpeg)](http://localhost:8501/media/8576adbcf0330a40db420987eda04ce8750b314555bb807fa4024de5.jpeg)")

st.write("---")

# 메인 페이지 내용
c1, c2, c3 = st.columns([0.5, 8, 0.5])
with c2:
    st.title("👉 야 너두? 웹툰 추천 받자 👉")

    image = Image.open("https://github.com/SERi9124/YCTI_streamlit/blob/main/img/ynd.jpg?raw=true")
    st.image(image)
    
    st.info("""- 이거 볼까, 저거 볼까 무수한 웹툰에 고민 된다면?
- 네이버 & 카카오, 플랫폼에 관계없이 찾고 싶다면?""")

st.write("")


c1, c2, c3, c4, c5 = st.columns([2, 4, 2, 4, 2])
with c2:
    image = Image.open("https://github.com/SERi9124/YCTI_streamlit/blob/main/img/naver.png?raw=true")
    image = image.resize((512, 512))
    st.image(image)
    st.markdown("[네이버 웹툰](https://comic.naver.com/webtoon/weekday)")


with c4:
    image = Image.open("https://github.com/SERi9124/YCTI_streamlit/blob/4dcccfd048e6971afb4878906456dd3528a3b719/img/kakao.png?raw=true")
    image = image.resize((512, 512))
    st.image(image)
    st.markdown("[카카오 웹툰](https://webtoon.kakao.com/original-webtoon)")



st.write("---")

st.subheader("나한테 맞는 웹툰 찾으러 가기")
st.markdown("[👉🏻 썸네일로 찾기](http://localhost:8501/thumbnail)")
st.markdown("[👉🏻 제목으로 찾기](http://localhost:8501/title)")