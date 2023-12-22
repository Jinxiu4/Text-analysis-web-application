import requests
from bs4 import BeautifulSoup
from pyecharts import options as opts
import streamlit as st
import re
import jieba
from pyecharts.charts import WordCloud
from collections import Counter
from pyecharts.charts import Bar, Line, Pie, Scatter, EffectScatter, Radar, Funnel
# 获取网页内容
def get_text_from_url(url):
    response = requests.get(url)
    # 确定编码
    encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None

    # 使用BeautifulSoup解析响应文本
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)
    # 获取所有的body标签内容
    text =soup.get_text()
    return text

def remove_numbers(text):
    return re.sub(r'\d+', '', text)

# 数据清洗，分词并统计词频
def get_word_frequency(text):
    chinese_text = remove_numbers(re.sub(r'[^\u4e00-\u9fa5]+', '', text))
    english_text = remove_numbers(re.sub(r'[\u4e00-\u9fa5]+', '', text))

    # 停用词处理
    stop_words = set(['的', '了', '是', '也', '将', '中', '和', '在', '或', '有'])  # 根据实际需要添加停用词
    chinese_words = [word for word in jieba.cut(chinese_text) if word not in stop_words]
    chinese_word_counts = Counter(chinese_words)

    # 英文处理（保留空格分隔的单词）
    english_words = re.findall(r'\b\w+\b', english_text)
    english_word_counts = Counter(english_words)
    # 合并中文和英文的词频数据
    merged_word_counts = chinese_word_counts + english_word_counts

    # 将词语及其频率存储在字典中
    return merged_word_counts.most_common()

# 绘制词云
def draw_word_cloud(words):
    wordcloud = (
        WordCloud()
        .add("", words, word_size_range=[20, 100])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="词云图示例"),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
    )
    return wordcloud

def toList(word_counts):
    if word_counts:
        keys_list, values_list = zip(*word_counts)
        keys_list = keys_list[:20]
        values_list = values_list[:20]
    else:
        # 处理字典为空的情况，可能是提供默认值或执行其他操作
        keys_list = values_list = []
    return keys_list,values_list
# 绘制词频排名前20的柱状图
def draw_bar_chart(keys_list,values_list):
    bar = (
        Bar()
        .add_xaxis(keys_list)
        .add_yaxis("", values_list)
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))  # 设置标签旋转角度为45度

        )
        .set_global_opts(title_opts=opts.TitleOpts(title="柱状图", pos_left="left", pos_top="top"))
    )
    return bar

# 绘制词频排名前20的饼状图
def draw_pie_chart(keys_list,values_list):
    min_length = min(len(keys_list), len(values_list))
    p_keys_list = keys_list[:min_length]
    p_values_list = values_list[:min_length]
    pie = (
        Pie()
        .add("饼状图", [list(z) for z in zip(p_keys_list, p_values_list)])
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="饼状图"),
            legend_opts=opts.LegendOpts(pos_left="12%"),
        )
    )
    return pie

# 绘制词频排名前20的折线图
def draw_line_chart(keys_list,values_list):
    line = (
        Line()
        .add_xaxis(list(keys_list))
        .add_yaxis("词频", list(values_list), is_smooth=True,
                   markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max", name="最大值")]))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="词频折线图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
        )
    )
    return line

def draw_scatter_chart(keys_list,values_list):
    scatter_chart = (
        Scatter()
        .add_xaxis(keys_list)
        .add_yaxis("", values_list)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="散点图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
        )
    )
    return scatter_chart

def effect_scatter_chart(keys_list,values_list):
    effect_scatter_chart = (
        EffectScatter()
        .add_xaxis(keys_list)
        .add_yaxis("", values_list)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="涟漪散点图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
        )
    )
    return effect_scatter_chart

def radar_chart(keys_list,values_list):
    radar_chart = (
        Radar()

        .add_schema(schema=[opts.RadarIndicatorItem(name=key, max_=max(values_list)) for key in keys_list])
        .add("展示", [values_list], color="blue")
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title="雷达图"))
    )
    return radar_chart

def funnel_chart(keys_list,values_list):
    funnel_chart = (
        Funnel()
        .add("", [list(z) for z in zip(keys_list, values_list)])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="漏斗图"),
            legend_opts=opts.LegendOpts(pos_left="12%"),
        )
    )
    return funnel_chart

# Streamlit 应用
def main():
    st.title("文本分析可视化")

    # 用户输入文章URL
    url = st.text_input("请输入url:")
    selected_chart = st.sidebar.selectbox("选择展示图表", ["柱状图", "词云图","饼状图","折线图","雷达图","漏斗图","散点图","涟漪散点图"])
    if url:
        # 请求URL抓取文本内容
        text = get_text_from_url(url)
        # 对文本分词，统计词频
        word_counter = get_word_frequency(text)
        keys_list, values_list=toList(word_counter)

        # 展示词频排名前20的词汇
        if selected_chart == "词云图":
            chart1=draw_word_cloud(word_counter)
        elif selected_chart == "柱状图":
            chart1=draw_bar_chart(keys_list, values_list)
        elif selected_chart=="饼状图":
            chart1=draw_pie_chart(keys_list, values_list)
        elif selected_chart=="折线图":
            chart1=draw_line_chart(keys_list, values_list)
        elif selected_chart=="雷达图":
            chart1=radar_chart(keys_list, values_list)
        elif selected_chart=="漏斗图":
            chart1=funnel_chart(keys_list, values_list)
        elif selected_chart=="散点图":
            chart1=draw_scatter_chart(keys_list, values_list)
        elif selected_chart=="涟漪散点图":
            chart1=effect_scatter_chart(keys_list, values_list)

        # streamlit_echarts.st_pyecharts(chart1)

        # 在 Streamlit 中展示 Pyecharts 图表
        pyecharts_html = chart1.render_embed()

        # 在 Streamlit 中展示 Pyecharts 图表
        st.components.v1.html(pyecharts_html, width=900, height=600)

# 运行 Streamlit 应用
if __name__ == "__main__":
    main()
