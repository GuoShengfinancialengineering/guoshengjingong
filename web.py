import streamlit as st
import time
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FuncFormatter
from matplotlib import ticker 
import altair as alt


plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False 

plt.rcParams['axes.unicode_minus'] = False  
matplotlib.rcParams['font.family']='SimHei'
plt.rcParams['text.color'] = 'black'
plt.rcParams['axes.labelcolor'] = 'black'
plt.rcParams['xtick.color'] = 'black'
plt.rcParams['ytick.color'] = 'black'


pio.templates.default = "plotly_white"  # 设置默认样式
pio.templates["plotly"]["layout"]["font"]["family"] = "SimHei"  # 设置字体为 Arial 或 sans-serif
pio.templates["plotly"]["layout"]["font"]["size"] = 12  # 设置字体大小
pio.templates["plotly"]["layout"]["font"]["color"] = "black"  # 设置字体颜色

# 预设的密码
correct_password = "0628"
placeholder2 = st.empty()
placeholder1 = st.empty()

# 输入密码框
placeholder2.title("欢迎来到国盛金工可视化查询系统！😃")
password = placeholder1.text_input("请输入密码", type="password")


# 检查输入的密码是否与预设的密码匹配
if password == correct_password:
    placeholder1.success("密码正确，解锁成功！")
    # 在解锁成功后，设置新的应用状态
    app_state = "unlocked"
    placeholder1.empty()
    placeholder2.empty()
else:
    if password != '':
        st.error("密码错误，请重试。")
    app_state = "locked"

#根据应用状态显示不同内容
if app_state == "unlocked":
    #数据加载
    R_decomposition_result = pd.read_csv("【R_decomposition_result】.csv",index_col=0)
    style_ind_result = pd.read_csv("【style_ind_result】.csv",index_col=0)
    ind_GD_HS_result = pd.read_csv("【ind_GD_HS_result】.csv",index_col=0)



    #侧边栏
    category = st.sidebar.selectbox("选择类目", ["基金查询", "因子总览"])
    #主页面样式设置


    ##################
    #基金查询
    if category == "基金查询":
        # 在侧边栏中添加一个搜索框
        fund_name = st.sidebar.text_input("搜索基金名称", "")
        # 获取数据中的最小日期和最大日期
        min_date = min(R_decomposition_result['收益月份'])
        max_date = max(R_decomposition_result['收益月份'])
        # 将最小日期和最大日期转换为日期对象
        min_date = pd.to_datetime(min_date).date()
        max_date = pd.to_datetime(max_date).date()

        # 在侧边栏中添加一个时间选择框，并设置默认值为最小和最大日期
        start_date = st.sidebar.date_input("选择起始日期", min_value=min_date, max_value=max_date, value=min_date)
        end_date = st.sidebar.date_input("选择结束日期", min_value=min_date, max_value=max_date, value=max_date)

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    # 如果用户输入了基金名称和时间范围
    if fund_name and start_date and end_date:
        # 将输入的基金名称设置为大标题
        st.title(fund_name) 
        # 在大标题下显示起始日期和结束日期
        st.write(f"查询时间：{start_date} - {end_date}")
        st.markdown("---")
        # 进行基金名称过滤和日期比较
        R_decomposition_result['收益月份'] = pd.to_datetime(R_decomposition_result['收益月份'])
        if fund_name not in  R_decomposition_result['F_INFO_WINDCODE'].values :
            st.error("输入的编号不存在，请重新输入")
        else :
            filtered_data = R_decomposition_result[(R_decomposition_result['F_INFO_WINDCODE'] == fund_name) & (R_decomposition_result['收益月份']  >= start_date) & (R_decomposition_result['收益月份']  <= end_date)]
            code = str(fund_name)
            #绘图过滤器
            plot_functions = {
            "雷达图": 1,
            "风格收益类型": 2,
            "行业收益类型": 3,
            "基金收益分解": 4,
            "持仓与动态收益贡献": 5,
            "持仓收益拆解": 6,
        }
            selected_labels = st.sidebar.multiselect("选择交互图（默认静态）", list(plot_functions.keys()))


            #加载器
            with st.spinner('Wait for it...'):
                time.sleep(0.5)
            def calculate_product(series):
                product = 1
                for value in series:
                    product *= value
                return product - 1
            R_decomposition_Leida = R_decomposition_result[(R_decomposition_result['收益月份']>=start_date)&(R_decomposition_result['收益月份']<=end_date)]
            R_decomposition_Leida['收益月份'] = R_decomposition_result['收益月份'].dt.strftime('%Y-%m-%d %H:%M:%S')
            R_decomposition_Leida = R_decomposition_Leida.set_index(["F_INFO_WINDCODE","收益月份"])
            R_decomposition_Leida = (R_decomposition_Leida + 1)
            R_decomposition_Leida = R_decomposition_Leida.reset_index()
            R_decomposition_Leida = R_decomposition_Leida.drop(columns=['收益月份']).groupby("F_INFO_WINDCODE").prod() - 1
            R_decomposition_Leida = R_decomposition_Leida.rank(pct=True)*10
            R_decomposition_Leida = R_decomposition_Leida[['R_nav','R_dynamic','R_style','R_industry','R_alpha']]
            R_decomposition_Leida.columns = ["总体收益能力","动态能力","风格能力","行业能力","选股能力"]
            
            label = np.array(["总体收益能力","动态能力","风格能力","行业能力","选股能力"])
            stats = R_decomposition_Leida.loc[code,['总体收益能力','动态能力','风格能力','行业能力','选股能力']]
            angles = np.linspace(0,2*np.pi,len(label),endpoint=False)
            stats = np.concatenate((stats,[stats[0]])) #分数
            angles = np.concatenate((angles,[angles[0]])) #角度
            label = np.concatenate((label,[label[0]]))
            figa, ax = plt.subplots(figsize=(3.8,2),subplot_kw=dict(polar=True))#
            ax.plot(angles,stats,'o-',linewidth=2,color=(77/255, 128/255, 255/255))# 连线
            ax.fill(angles,stats,alpha=0.25,color=(77/255, 128/255, 255/255))# 填充
            ax.set_thetagrids(angles*180/np.pi,label,size=12)
            #st.pyplot(figa, transparent=True)
            
            score = pd.DataFrame(R_decomposition_Leida.loc[code,['总体收益能力','动态能力','风格能力','行业能力','选股能力']]).T
            data = {
                '能力': score.columns,
                '分数': score.iloc[0].values
            }
            leida = pd.DataFrame(data)
            # 使用Plotly Express绘制雷达图
            fig = px.line_polar(leida, r='分数', theta='能力', line_close=True)
            # 设置雷达图的标题
            fig.update_layout(title='能力雷达图')
            #fig.update_traces(fill='toself')
            fig.update_traces(line=dict(color='rgb(77, 128, 255)'))
            #st.plotly_chart(fig)
            

            #绘制柱状图    
            style_score = pd.DataFrame({
                '扬长':style_ind_result[['beta_y','momentum_y','growth_y']].mean(axis=1),
                '避短':style_ind_result[['volatility_y','liquidity_y']].mean(axis=1),
                '应变':style_ind_result[['size_y','nlsize_y','earnings_yield_y','value_y']].mean(axis=1)
            },index=style_ind_result.index)

            style_score = style_score.rank(pct=True)*10
            Y = style_score.loc[code,['扬长','避短','应变']]
            # #
            figb, ax = plt.subplots()
            X = [1,2,3]
            plt.axis([0,4,0,10])
            X_label = ['扬长','避短','应变']
            plt.bar(X,Y,color=(77/255, 128/255, 255/255))
            plt.xticks(X,X_label,size=12)
            plt.yticks(fontproperties='Arial', size=12)
            plt.title('风格收益类型({})'.format(code), fontsize=16)#标题
            #st.pyplot(figb, transparent=True)

            fig1 = px.bar(x=['扬长', '避短', '应变'], y=Y, color_discrete_sequence=['rgb(77, 128, 255)'])
            # 设置图表的标题和轴标签
            fig1.update_layout(
                title='风格收益类型({})'.format(code),
                xaxis_title='风格类型',
                yaxis_title='分数',
                xaxis=dict(tickfont=dict(size=20)),
                yaxis=dict(tickfont=dict(size=20)),
                font=dict(size=16),
            )
            fig1.update_layout(bargap=0.5)
            #st.plotly_chart(fig1)



            #绘制行业图
            ind_GD_HS_result['行业集中度'] = 1/ind_GD_HS_result['行业广度']
            ind_GD_HS_result['行业集中度'] = 10*ind_GD_HS_result['行业集中度'].rank(pct=True)
            ind_GD_HS_result['行业换手率'] = 10*ind_GD_HS_result['行业换手'].rank(pct=True)
            figc, ax = plt.subplots()
            plt.xlabel('行业集中度',fontsize=12)
            plt.ylabel('行业换手率',fontsize=12)
            for x in range(1,1000,1):
                plt.plot([x/200,x/200],[5,10],linewidth=0.5,color=(77/255, 128/255, 255/255),zorder=1)
            for y in range(1,1000,1):
                plt.plot([5,10],[y/200,y/200],linewidth=0.5,color=(254/255, 255/255, 179/255),zorder=1)
            for x in range(1,1000,1):
                plt.plot([x/200,x/200],[0,5],linewidth=0.5,color=(179/255, 255/255, 179/255),zorder=1)
            plt.scatter(ind_GD_HS_result.loc[code,'行业集中度'],ind_GD_HS_result.loc[code,'行业换手率'],color='red',zorder=2)
            plt.xticks(fontproperties='Arial', size=12)
            plt.yticks(fontproperties='Arial', size=12)
            plt.title('行业收益类型({})'.format(code), fontsize=16)
            #st.pyplot(figc, transparent=True)
            data = {
                '行业集中度': [ind_GD_HS_result.loc[code,'行业集中度']],
                '行业换手率': [ind_GD_HS_result.loc[code,'行业换手率']]
            }
            fig2 = px.scatter(data, x='行业集中度', y='行业换手率', color_discrete_sequence=['rgb(255,0,0)'])
            # 创建线条

            # 设置图表的标题和轴标签
            fig2.update_layout(
                title='行业收益类型({})'.format(code),
                xaxis_title='行业集中度',
                yaxis_title='行业换手率',
                xaxis=dict(tickfont=dict(size=12)),
                yaxis=dict(tickfont=dict(size=12)),
                font=dict(size=16),
                font_color='white' 
            )
            fig2.update_xaxes(showgrid=False)
            fig2.update_yaxes(showgrid=False)
            x_min, x_max = 0,10
            y_min, y_max = 0,10
            fig2.update_layout(xaxis=dict(range=[x_min,x_max]))
            fig2.update_layout(yaxis=dict(range=[y_min,y_max]))
            fig2.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # 设置图表背景色为透明
                paper_bgcolor='rgba(0, 0, 0, 0)'  # 设置画布背景色为透明
            )

            fig2.add_shape(
                type='rect',
                x0=0,  # 正方形左上角的 x 坐标
                y0=5,  # 正方形左上角的 y 坐标
                x1=5,  # 正方形右下角的 x 坐标
                y1=10,  # 正方形右下角的 y 坐标
                line=dict(color='rgba(0, 0, 0, 0)'), 
                fillcolor='rgba(77, 128, 255,1)',  # 正方形的填充颜色
                layer='below'
            )
            fig2.add_shape(
                type='rect',
                x0=10,  # 正方形左上角的 x 坐标
                y0=5,  # 正方形左上角的 y 坐标
                x1=5,  # 正方形右下角的 x 坐标
                y1=0,  # 正方形右下角的 y 坐标
                line=dict(color='rgba(0, 0, 0, 0)'), 
                fillcolor='rgba(254, 255, 179,1)',  # 正方形的填充颜色
                layer='below'
            )
            fig2.add_shape(
                type='rect',
                x0=0,  # 正方形左上角的 x 坐标
                y0=5,  # 正方形左上角的 y 坐标
                x1=5,  # 正方形右下角的 x 坐标
                y1=0,  # 正方形右下角的 y 坐标
                line=dict(color='rgba(0, 0, 0, 0)'), 
                fillcolor='rgba(179, 255, 179,1)',  # 正方形的填充颜色
                layer='below'
            )
            fig2.add_shape(
                type='rect',
                x0=5,  # 正方形左上角的 x 坐标
                y0=10,  # 正方形左上角的 y 坐标
                x1=10,  # 正方形右下角的 x 坐标
                y1=5,  # 正方形右下角的 y 坐标
                line=dict(color='rgba(0, 0, 0, 0)'),
                fillcolor='rgba(255, 255, 255,1)',  # 正方形的填充颜色
                layer='below'
            )
            # st.plotly_chart(fig2)




            #区间收益分解图
            #功能：获得3个图的数据
            def picture_getdata(code='004685.OF',T_begin = '2018-12-31',T_end = '2022-12-31'):
                cur_R = R_decomposition_result[R_decomposition_result['F_INFO_WINDCODE']==code]
                cur_R = cur_R.set_index(['收益月份'])
                cur_R = cur_R[(cur_R.index>=T_begin)&(cur_R.index<=T_end)]
                cur_R = cur_R.iloc[:,1:]
                cur_R_cum = (cur_R+1).cumprod()-1  #累计收益分解
                cur_R_cum['残差'] = cur_R_cum['R_nav']-cur_R_cum['R_dynamic']-cur_R_cum['R_market']-cur_R_cum['R_style']-cur_R_cum['R_industry'] 
                cur_R_result1 = pd.DataFrame({
                    '基金':cur_R_cum['R_nav'],
                    '动态':cur_R_cum['R_dynamic'],
                    '持仓':cur_R_cum['R_simulation']
                },index=cur_R_cum.index)
                cur_R_result2 = cur_R_cum[['R_market','R_style','R_industry','残差','R_dynamic','R_nav']].tail(1)
                cur_R_result2.columns = ['市场','风格','行业','alpha','动态','总计']
                cur_R_result3 = pd.DataFrame({
                    '持仓':cur_R_cum['R_simulation'],
                    '市场':cur_R_cum['R_market'],
                    '风格':cur_R_cum['R_style'],
                    '行业':cur_R_cum['R_industry'],
                    '残差':cur_R_cum['残差']
                },index=cur_R_cum.index)
                return cur_R_result1,cur_R_result2,cur_R_result3 
            y = picture_getdata(code=code,T_begin = start_date,T_end =end_date)[1].values[0] 
            
            figd, ax = plt.subplots()
            x = [1,2,3,4,5,6]
            label = ["市场","风格","行业","选股","动态","总计"]
            bottom = [0,y[0],y[0]+y[1],y[0]+y[1]+y[2],y[0]+y[1]+y[2]+y[3],0]
            color = []
            for i in range(0,6,1):
                if y[i]>0:
                    color.append((254/255, 0/255, 0/255))
                else:
                    color.append((77/255, 128/255, 255/255))
            ax = plt.bar(x,y,tick_label=label,bottom=bottom,color=color)
            for i in range(0,6,1):
                if y[i]>0:
                    plt.text(x[i],y[i]+0.005+bottom[i],format(y[i],'.2%'),ha="center",va="bottom",fontsize=12,fontproperties='Arial') #坐标轴x，y，string
                else:
                    plt.text(x[i],y[i]-0.005+bottom[i],format(y[i],'.2%'),ha="center",va="top",fontsize=12,fontproperties='Arial')
            plt.title("基金收益分解",size=16)
            plt.xticks(x,label,size=12)
            def to_percent(temp, position):
                return '%1.0f'%(100*temp) + '%'
            plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
            top_line = 1.2*max(bottom+y)
            bottom_line = -1.2*abs(min(y))
            plt.axis([0,7,bottom_line,top_line])
            #st.pyplot(figd, transparent=True)

            label = ["市场", "风格", "行业", "选股", "动态", "总计"]
            color = ['正值' if y_value > 0 else '负值' for y_value in y]

            bottom = [0] * 6
            for i in range(1, 6):
                bottom[i] = bottom[i - 1] + y[i - 1]
            # 创建DataFrame以便使用Plotly Express
            top_line = 1.2*max(bottom+y)
            bottom_line = -1.2*abs(min(y))
            data = pd.DataFrame({'x': label, 'y': y, '效应': color, 'bottom': bottom})

            color_dis = {
                '正值': 'rgb(254, 0, 0)',
                '负值': 'rgb(77,128,255)'
            }

            # 使用Plotly Express创建柱状图
            fig3 = px.bar(data, x='x', y='y',color='效应',
                        text='y', title='基金收益分解', labels={'y': '收益'}, height=400,base='bottom',
                        category_orders={'x':  ["市场", "风格", "行业", "选股", "动态", "总计"]},
                        color_discrete_map=color_dis)

            # 修改y轴标签为百分比
            fig3.update_layout(yaxis_tickformat='.0%')
            # 设置布局
            fig3.update_traces(texttemplate='%{text:.2%}', textposition='outside')
            fig3.update_xaxes(title_text='', tickvals=[0, 1, 2, 3, 4, 5], ticktext=label)
            fig3.update_yaxes(title_text='')
            fig3.update_yaxes(range=[bottom_line, top_line])
            fig3.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # 设置图表背景色为透明
                paper_bgcolor='rgba(0, 0, 0, 0)'  # 设置画布背景色为透明
            )
            # 去掉网格线
            fig3.update_yaxes(showgrid=False)
            fig3.update_layout(xaxis_showline=True, yaxis_showline=True)
            fig3.update_yaxes(zeroline=False)
            # st.plotly_chart(fig3)

            #基金持仓与动态收益图
            df = picture_getdata(code=code,T_begin = start_date,T_end = end_date)[0]
            first_begin = pd.DataFrame({'基金':[0.0],'动态':[0.0],'持仓':[0.0]},index = [df.index[0] +pd.offsets.MonthBegin(-1)])#第一个日期的月初
            df = pd.concat([first_begin,df])
            fige, ax = plt.subplots() 
            x = pd.to_datetime(df.index.tolist()) 
            y1 = np.array(df['基金'])
            y2 = np.array(df['持仓'])
            y3 = np.array(df['动态'])
            ax1 = plt.gca()
            ax1.set_title('基金的持仓与动态收益贡献', fontsize=16)
            ax1.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1,decimals=0))
            ax1.plot(x,y1,label='基金',color=(112/255,48/255,160/255),alpha=0.9) 
            ax1.fill_between( x, y1,color=(220/255,208/255,255/255),alpha=0.2)
            ax2 = plt.gca()
            ax2.plot(x,y2,label='持仓',color=(0/255,176/255,240/255),alpha=0.9)   
            ax2.fill_between( x, y2, color=(0/255,176/255,240/255), alpha=0.2)
            ax3 = plt.gca()
            ax3.plot(x,y3,label='动态',color=(255/255,192/255,0/255),alpha=0.9) 
            ax3.fill_between( x, y3, color=(255/255,255/255,120/255), alpha=0.2)
            ax1.legend(fontsize=12, ncol=1,loc='upper left') 
            plt.xticks(fontsize=12, horizontalalignment='center',rotation = 0)
            plt.yticks(fontsize=12)
            plt.xlim(x[0], x[-1]) 
            #st.pyplot(fige, transparent=True)

            fig4 = px.line(df, x=df.index, y=['基金', '持仓', '动态'], title='基金的持仓与动态收益贡献',
                        color_discrete_sequence=['rgb(112,48,160)', 'rgb(0,176,240)', 'rgb(255,192,0)'])
            fig4.update_yaxes(tickformat='.0%')
            fig4.update_traces(fill='tozeroy', line=dict(width=0.5))
            fig4.update_traces(line=dict(width=2))
            fig4.update_layout(legend=dict(font=dict(size=12), traceorder='normal'))
            fig4.update_xaxes(tickfont=dict(size=12))
            fig4.update_yaxes(tickfont=dict(size=12))
            fig4.update_xaxes(range=[df.index[0], df.index[-1]])
            fig4.update_xaxes(title_text='')
            fig4.update_yaxes(title_text='')
            fig4.update_layout(legend_title_text=" ",plot_bgcolor='white', xaxis_showgrid=False, yaxis_showgrid=False)
            #st.plotly_chart(fig4)


            #持仓收益拆解
            df = picture_getdata(code=code,T_begin = start_date,T_end = end_date)[2]
            first_begin = pd.DataFrame({'持仓':[0.0],'市场':[0.0],'风格':[0.0],'行业':[0.0],'残差':[0.0]},index = [df.index[0] +pd.offsets.MonthBegin(-1)])#第一个日期的月初
            df = pd.concat([first_begin,df])
            figf, ax = plt.subplots() 
            x = pd.to_datetime(df.index.tolist())
            y1 = np.array(df['持仓'])
            y2 = np.array(df['市场'])
            y3 = np.array(df['风格'])
            y4 = np.array(df['行业'])
            y5 = np.array(df['残差'])
            ax1 = plt.gca()
            ax1.set_title('基金的持仓收益拆解', fontsize=16)
            ax1.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1,decimals=0))
            ax1.plot(x,y1,linestyle='--',label='持仓',color="black",alpha=0.9) 
            ax2 = plt.gca()
            ax2.plot(x,y2,label='市场',color=(0/255,176/255,240/255),alpha=0.9)   
            ax2.fill_between( x, y2, color=(0/255,176/255,240/255), alpha=0.2) 
            ax3 = plt.gca()
            ax3.plot(x,y3,label='风格',color=(255/255,192/255,0/255),alpha=0.9) 
            ax3.fill_between( x, y3, color=(255/255,255/255,120/255), alpha=0.2)
            ax4 = plt.gca()
            ax4.plot(x,y4,label='行业',color=(112/255,48/255,160/255),alpha=0.9)   
            ax5 = plt.gca()
            ax5.plot(x,y5,label='选股',color=(191/255,191/255,191/255),alpha=0.9) 
            ax1.legend(fontsize=12, ncol=1,loc='upper left') 
            plt.xticks(fontsize=12, horizontalalignment='center',rotation = 0)
            plt.yticks(fontsize=12)
            plt.xlim(x[0], x[-1])
            #st.pyplot(figf, transparent=True)

            fig5 = px.line(df, x=df.index, y=['持仓', '市场', '风格', '行业', '残差'], title='基金的持仓收益拆解',
                        color_discrete_sequence=['rgb(112,48,160)', 'rgb(0,176,240)', 'rgb(255,192,0)','rgb(112,48,160)','rgb(191,191,191)'])
            fig5.update_yaxes(tickformat='.0%')
            fig5.update_traces(line=dict(width=2))
            fig5.update_xaxes(title_text='')
            fig5.update_yaxes(title_text='')

            # 去除背景颜色和网格线
            fig5.update_layout(plot_bgcolor='white', xaxis_showgrid=False, yaxis_showgrid=False)

            # 设置坐标轴标签字体大小
            fig5.update_xaxes(tickfont=dict(size=12))
            fig5.update_yaxes(tickfont=dict(size=12))

            # 设置x轴范围
            fig5.update_xaxes(range=[df.index[0], df.index[-1]])

            # 添加图例
            fig5.update_layout(legend=dict(font=dict(size=12), traceorder='normal', x=0, y=1))

            # 将图例放在图片的右侧外边
            fig5.update_layout(
                legend_title_text=" ",
                legend=dict(font=dict(size=12), traceorder='normal', x=1.1, y=1),
                margin=dict(l=20, r=200),  # 调整右侧边距以容纳图例
            )
            # 修改持仓线条为黑色虚线
            fig5.update_traces(line=dict(width=2, color='black', dash='dash'), selector=dict(name='持仓'))
            fig5.update_traces(fill='tozeroy', line=dict(width=2), selector=dict(name='市场'))
            fig5.update_traces(fill='tozeroy', line=dict(width=2), selector=dict(name='风格'))
            #st.plotly_chart(fig5)






            #选择的结果
            col1, col2 = st.columns(2)
            if selected_labels:
                for label in selected_labels:
                        if plot_functions[label] == 1:
                            st.plotly_chart(fig)
                        if plot_functions[label] == 2:
                            st.plotly_chart(fig1)
                        if plot_functions[label] == 3:
                            st.plotly_chart(fig2)
                        if plot_functions[label] == 4:
                            st.plotly_chart(fig3)
                        if plot_functions[label] == 5:
                            st.plotly_chart(fig4)
                        if plot_functions[label] == 6:
                            st.plotly_chart(fig5)

            else: 
                    
                    with col1:
                        st.pyplot(figa, transparent=True)
                        st.pyplot(figb, transparent=True)
                        st.pyplot(figc, transparent=True)
                    with col2:   
                        st.pyplot(figd, transparent=True)
                        st.pyplot(fige, transparent=True)
                        st.pyplot(figf, transparent=True)



    #未进行查询
    else:
            st.title("👈请在左侧输入查询内容")
            st.markdown("以下为原始数据💻：")
            # 显示原始数据表格
            tab1, tab2,tab3 = st.tabs(["R_decomposition_result", "ind_GD_HS_result","style_ind_result "])
            with tab1:st.dataframe(R_decomposition_result)
            with tab2:st.dataframe(ind_GD_HS_result) 
            with tab3:st.dataframe(style_ind_result)

else:

    # 解锁失败或默认状态的页面内容
    st.header("目前页面状态：锁定🔒")
    st.write("或咨询管理员:张国安")