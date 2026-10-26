import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
a=st.text_input('이름을 입력해 주세요!')
b=st.selectbox('좋아하는 음식을 입력해주세요!',['막창','치킨','피자'])
if st.button('인사말 생성'):
  st.write('반갑습니다!')
  st.info(a+'님! 반갑습니다!')
  st.warning(b+'를 좋아하시나봐요! 저도 좋아합니다!')
  st.error('우리 잘지내봐요')
  st.balloons()
