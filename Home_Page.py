import streamlit as st

st.title('Welcome to Stephany Reis\'s Astological Calculator')
           
st.write('This app provides all the tools you need to conduct your astrological studies just like Stephany Reis does daily for thousands of her followers on social media.')
ste_text, ste_image = st.columns([2,1])
ste_text.write('Stephany Reis is a well-known Brazilian astrologer specializing in modern and karmic astrology. Through years of study and observation, she has developed a unique approach to interpreting how the stars and planets influence our everyday lives.')
ste_text.write('She shares easy-to-understand insights on astrology through her Instagram, TikTok, and YouTube channels. Click below to follow and subscribe!')
ig, tt, yt = ste_text.columns(3)
ig.link_button("Instagram", "https://www.instagram.com/stephany_astrologa/")
tt.link_button("TikTok", "https://www.tiktok.com/@stephany.reis")
yt.link_button("Youtube", 'https://www.youtube.com/@Astrologastephany')
ste_image.image('assets/ste.jpg')