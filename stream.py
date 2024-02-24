from langchain_google_genai import GoogleGenerativeAI
from langchain.agents import Tool
from langchain.agents import AgentType, initialize_agent, load_tools
from bs4 import BeautifulSoup
from langchain.tools import DuckDuckGoSearchRun
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from flask import Flask, request, jsonify
import os
import requests
import re
import streamlit as st
from streamlit_chat import message
# A very simple Flask Hello World app for you to get started with...
#os.environ["SERPER_API_KEY"] = "f6e8b87fa0bb0545e8732eaa43fa0a77dd999a6a"
os.environ["GOOGLE_CSE_ID"] = "f2b97ee41733f4710"
os.environ["GOOGLE_API_KEY"] = "AIzaSyA1Qz28QhouL5-QbD93lSObWq47PDZ-6F4"
#os.environ["SERPAPI_API_KEY"] = "b6517fbc933f4c0c11b19384b1b75e0fa2fa02e69ac22995a5d989c00a4f3a60"
st.title("WOW FINGPT")
if 'responses' not in st.session_state:
    st.session_state['responses'] = ["How can I assist you?"]

if 'requests' not in st.session_state:
    st.session_state['requests'] = []
if 'buffer_memory' not in st.session_state:
            st.session_state.buffer_memory=ConversationBufferWindowMemory(k=3,return_messages=True)
# container for chat history
def google_query(search_term):
    if "news" not in search_term:
        search_term=search_term+" stock news"
    url=f"https://www.google.com/search?q={search_term}&cr=countryIN"
    url=re.sub(r"\s","+",url)
    return url
def get_recent_stock_news(company_name):
    # time.sleep(4) #To avoid rate limit error
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

    g_query=google_query(company_name)
    res=requests.get(g_query,headers=headers).text
    soup=BeautifulSoup(res,"html.parser")
    news=[]
    for n in soup.find_all("div","n0jPhd ynAwRc tNxQIb nDgy9d"):
        news.append(n.text)
    for n in soup.find_all("div","IJl0Z"):
        news.append(n.text)

    if len(news)>6:
        news=news[:4]
    else:
        news=news
    news_string=""
    for i,n in enumerate(news):
        news_string+=f"{i}. {n}\n"
    top5_news="Recent News:\n\n"+news_string

    return top5_news

def analyze(query):

    search = DuckDuckGoSearchRun()


    ls = [

    Tool(
        name="DuckDuckGo Search",
        func=search.run,
        description="Use only for NSE/BSE stock ticker or recent stock-related news."
    ),
    Tool(
        name="get recent news",
        func=get_recent_stock_news,
        description="Use to fetch recent news about stocks.you should input the stock ticker name to it"
    )
]

    llm = GoogleGenerativeAI(model="gemini-pro")
    p="""As a trading expert and intelligence member of the market, your task is to analyze
stocks/companies based on user queries. You are to provide insights using:
Fundamental Analysis: Evaluate the company's financial health, market position, competitive
advantage, revenue, profit margins, and other key financial ratios. Consider recent earnings
reports, management effectiveness, industry conditions, and future growth prospects.
Sentimental Analysis: Assess market sentiment towards the stock/company by analyzing news
articles, investor opinions, social media trends, and overall media coverage. Determine whether
the sentiment is positive, negative, or neutral.
Technical Analysis: Examine stock price movements, trading volumes, historical trends, chart
patterns, and technical indicators such as moving averages, RSI (Relative Strength Index),
MACD (Moving Average Convergence Divergence), and others to predict future price
movements.
After conducting the requested analysis, provide a concise conclusion on
whether to invest in the stock/company. This recommendation should only be given if the user
requests investment advice or a comprehensive analysis involving all three aspects mentioned
above.
For each query:
If the user asks specifically for fundamental analysis, provide insights based solely on the
company's financial and market fundamentals.
If the user seeks sentimental analysis, focus on the prevailing sentiment and its potential impact
on the stock.
If the request is for technical analysis, offer an assessment based on price trends and technical
indicators.
Always ensure the analysis is up-to-date, relying on the most recent data and market trends.
Your goal is to deliver precise, concise, and actionable insights to assist users in making
informed investment decisions.
Note:you should use only avilable tools in the efficient manner and you should get the all the informantion at any cost and if you have limited resource try to gather more and more
you should answer the user still you have limited resources
Disclaimer:
Include a disclaimer noting that the recommendation is based on the current market analysis and is subject to change. Remind users to perform their own research before making trading decisions.
Note:
you should answer the user very fastly and with very quickly
your analysis output formant:
Analysis Type: Technical | Sentimental | Fundamental | Combined
Overview:
Provide a brief overview of the market conditions and the reason for this specific trader recommendation.
Technical Analysis Summary:

Key Indicators Used: [List of technical indicators, e.g., Moving Averages, RSI, MACD]
Trend Analysis: [Brief summary of the trend analysis findings]
Signal Strength: [Weak/Moderate/Strong]
Technical Outlook: [Bullish/Bearish/Neutral]
Sentimental Analysis Summary:

Market Sentiment: [Positive/Negative/Neutral]
Sentiment Indicators: [List of sentimental indicators used, e.g., news analysis, social media sentiment]
Impact on Recommendation: [Brief summary of how sentiment analysis impacted the recommendation]

Fundamental Analysis Summary:
Key Metrics Analyzed: [List of fundamental metrics, e.g., Earnings, P/E Ratio, Market Cap]
Market Position: [Leader/Follower/Niche]
Financial Health: [Good/Moderate/Poor]
Fundamental Outlook: [Positive/Negative/Neutral]
Rationale for Recommendation:
Provide a detailed explanation of why this trader is recommended based on the analysis. Include any specific strengths or opportunities identified during the analysis.

Risk Assessment:
Market Risk: [Low/Medium/High]
Analysis Confidence Level: [Low/Medium/High]
Potential Challenges: [Briefly list any potential challenges or risks associated with this recommendation]
Conclusion:
Summarize the recommendation and provide any final thoughts or suggestions for the user.

Please make sure that you represented the answer in the above mentioned format(you should do it) and give correct and best answer to the user
Note:
if user asks the general question like greetings then you do not need to do analysis and answer the question by ourself and remeber that you have access to the real time data and access to the internet and you information should up to date
Query:"""

    tools = load_tools(["google-search"], llm=llm)+ls
    agent = initialize_agent(tools, llm=llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=50)
    # Use the agent to process the query
    response = agent.run(p+query)
    return response
response_container = st.container()
# container for text box
textcontainer = st.container()


with textcontainer:
    query = st.text_input("Query: ", key="input")
    if query:
        with st.spinner("typing..."):
            response = analyze(query)
        st.session_state.requests.append(query)
        st.session_state.responses.append(response) 
with response_container:
    if st.session_state['responses']:
        for i in range(len(st.session_state['responses'])):
            message(st.session_state['responses'][i],key=str(i))
            if i < len(st.session_state['requests']):
                message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')
