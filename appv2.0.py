import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimSong', 'Arial Unicode MS', 'Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']
matplotlib.rcParams["axes.unicode_minus"] = False
import streamlit as st
from CH4MOD import CH4Flux_day

# Streamlit应用界面
st.set_page_config(page_title="CH4MOD模型模拟工具", page_icon="🌾", layout="wide")
st.title("🌾 CH4MOD稻田甲烷排放模型模拟工具")

# 水分管理模式详细说明
water_regime_info = {
    1: {
        "name": "模式 1",
        "composition": "淹水-烤田-淹水-间歇灌溉",
        "description": "多见于华北和华东的单季稻",
        "region": "华北、华东地区"
    },
    2: {
        "name": "模式 2", 
        "composition": "淹水-烤田-间歇灌溉",
        "description": "多见于华南和西南的单、双季稻",
        "region": "华南、西南地区"
    },
    3: {
        "name": "模式 3",
        "composition": "淹水-间歇灌溉", 
        "description": "类似于模式2，但没有明显的烤田",
        "region": "多种稻区"
    },
    4: {
        "name": "模式 4",
        "composition": "淹水",
        "description": "排灌条件欠佳的高地稻田和盐碱稻田", 
        "region": "高地、盐碱稻田"
    },
    5: {
        "name": "模式 5",
        "composition": "间歇灌溉",
        "description": "低洼稻田，地下水位通常较高",
        "region": "低洼稻田"
    }
}

# 输入方式选择
st.sidebar.header("📋 选择输入方式")
input_method = st.sidebar.radio(
    "选择参数输入方式",
    options=["CSV文件输入 (与Run.py一致)", "手动参数输入"],
    help="选择使用CSV文件批量输入或手动输入单个参数"
)

# 水分管理模式说明面板
with st.sidebar.expander("💧 水分管理模式详细说明", expanded=True):
    st.subheader("五种水分管理模式")
    for regime_id, info in water_regime_info.items():
        st.markdown(f"**{info['name']}**: {info['composition']}")
        st.markdown(f"- 描述: {info['description']}")
        st.markdown(f"- 适用区域: {info['region']}")
        st.markdown("---")

if input_method == "CSV文件输入 (与Run.py一致)":
    # CSV文件输入方式 - 与Run.py保持一致
    st.sidebar.subheader("📁 CSV文件配置")
    
    # 参数文件上传
    param_file = st.sidebar.file_uploader(
        "上传参数CSV文件", 
        type=["csv"], 
        help="上传包含GrainYield(kg/ha),VI,SoilSand(%),OMN(kg/ha),OMS(kg/ha),WaterRegime,StartDay,EndDay,Year的CSV文件"
    )
    
    # 气温文件上传
    temp_file = st.sidebar.file_uploader(
        "上传气温数据文件", 
        type=["txt"], 
        help="上传每日气温数据文件，每行一个温度值(℃)"
    )
    
    if param_file is not None and temp_file is not None:
        try:
            # 读取参数文件
            data = pd.read_csv(param_file)
            
            # 读取气温数据
            temp_data = pd.read_csv(temp_file, header=None)
            Tair = temp_data[0].values
            
            # 提取参数（使用文档中的单位说明）
            GY = data['GrainYield'][0]  # kg/ha
            sand = data['SoilSand'][0]   # %
            OMN = data['OMN'][0]        # kg/ha
            OMS = data['OMS'][0]        # kg/ha
            IP = data['WaterRegime'][0] # 模式编号
            day_begin = data['StartDay'][0]
            day_end = data['EndDay'][0]
            
            # 显示参数信息（带单位）
            st.sidebar.success("✅ 文件读取成功")
            st.sidebar.write(f"**谷物产量 (GY):** {GY} kg/ha")
            st.sidebar.write(f"**土壤砂含量:** {sand}%")
            st.sidebar.write(f"**稻田外源有机质的易分解组分含量 (OMN):** {OMN} kg/ha")
            st.sidebar.write(f"**稻田外源有机质的难分解组分含量 (OMS):** {OMS} kg/ha")
            st.sidebar.write(f"**水分管理模式:** {water_regime_info[IP]['name']}")
            st.sidebar.write(f"**模拟日期:** {day_begin} - {day_end}")
            st.sidebar.write(f"**气温数据天数:** {len(Tair)}")
            
            # 显示当前选择的水分模式详情
            current_regime = water_regime_info[IP]
            st.sidebar.info(f"💧 **当前模式**: {current_regime['composition']}\n📝 {current_regime['description']}")
            
            # 主内容区域
            st.subheader("📊 CSV文件输入模式")
            st.info("💡 当前使用CSV文件输入模式，与Run.py调用方式完全一致")
            
            # 显示参数表格
            st.write("**参数文件内容:**")
            st.dataframe(data)
            
            st.write("**气温数据预览 (前30天, 单位: ℃):**")
            st.dataframe(pd.DataFrame({
                '日期': range(1, min(31, len(Tair) + 1)),
                '气温 (°C)': Tair[:30]
            }))
            
        except Exception as e:
            st.sidebar.error(f"❌ 文件读取错误: {str(e)}")
            st.stop()
    else:
        st.info("👆 请上传参数CSV文件和气温数据文件以开始模拟")
        st.stop()
        
else:
    # 手动参数输入方式
    with st.sidebar:
        st.header("📋 手动输入参数")
        
        # 日期范围
        col1, col2 = st.columns(2)
        with col1:
            day_begin = st.number_input("起始日", min_value=1, max_value=365, value=160, help="模拟开始日期（1-365）")
        with col2:
            day_end = st.number_input("结束日", min_value=day_begin, max_value=365, value=280, help="模拟结束日期")
        
        # 水分管理模式选择（带详细说明）
        st.subheader("💧 水分管理模式")
        IP = st.selectbox(
            "选择水分管理模式",
            options=[1, 2, 3, 4, 5],
            index=1,
            format_func=lambda x: f"{water_regime_info[x]['name']}: {water_regime_info[x]['composition']}",
            help="选择不同的水分管理策略"
        )
        
        # 显示当前选择模式的详细信息
        current_info = water_regime_info[IP]
        st.info(f"**{current_info['name']}**: {current_info['composition']}\n📝 {current_info['description']}\n🌍 适用: {current_info['region']}")
        
        # 土壤参数（带单位）
        sand = st.slider("土壤砂含量 (%)", 0.0, 100.0, 30.0, help="土壤中砂粒含量的百分比")
        
        # 初始碳氮参数（带单位）
        st.subheader("🌱 有机质参数")
        col3, col4 = st.columns(2)
        with col3:
            OMS = st.number_input("稻田外源有机质的难分解组分含量 (OMS)", min_value=0.0, value=1300.0, help="单位: kg/ha")
        with col4:
            OMN = st.number_input("稻田外源有机质的易分解组分含量 (OMN)", min_value=0.0, value=1600.0, help="单位: kg/ha")
        
        # 产量参数（带单位）
        GY = st.number_input("谷物产量 (GY)", min_value=0.0, value=4000.0, help="单位: kg/ha")
        
        # 气温数据配置
        st.subheader("🌡️ 气温数据配置")
        temp_config_method = st.radio(
            "选择气温数据配置方式",
            options=["使用示例数据(长沙气温2003)", "手动输入气温数据", "上传气温数据文件"]
        )
        
        Tair = None
        
        if temp_config_method == "手动输入气温数据":
            temp_input = st.text_area(
                "每日气温 (℃)，用逗号分隔",
                value="5.3,4.0,1.2,1.4,1.4,-1.3,-0.9,-1.9,1.5,2.4,4.7,6.4,8.4,7.3,7.4,8.7,12.3,9.3,8.2,8.6,10.6,10.0,7.7,7.3,6.2,4.0,5.7,5.9,9.0,8.9",
                help="例如：25,26,27,28,... 按日序排列，使用英文逗号分隔，单位: ℃"
            )
            try:
                Tair = np.array([float(x.strip()) for x in temp_input.split(',') if x.strip()])
            except ValueError:
                st.error("气温数据格式错误，请确保所有值均为有效的数字")
                st.stop()
        elif temp_config_method == "上传气温数据文件":
            uploaded_file = st.file_uploader("上传气温数据文件（.txt格式）", type=["txt"])
            if uploaded_file is not None:
                try:
                    temp_data = np.loadtxt(uploaded_file, skiprows=0)
                    Tair = temp_data.flatten()
                except Exception as e:
                    st.error(f"文件解析错误: {str(e)}")
                    st.stop()
            else:
                st.info("请上传气温数据文件")
                st.stop()
        else:
            # 使用示例数据
            try:
                file_path = "长沙气温2003.txt"
                temp_data = np.loadtxt(file_path, skiprows=0)
                Tair = temp_data.flatten()
                st.success(f"✅ 已加载示例气温数据 (长沙气温2003，共{len(Tair)}天，单位: ℃)")
            except Exception as e:
                st.error(f"示例数据加载失败: {str(e)}")
                st.stop()
        
        # 验证气温数据长度
        dur_date = day_end - day_begin + 1
        if Tair is not None:
            if len(Tair) < dur_date:
                st.warning(f"气温数据长度不足 {dur_date} 天，当前为 {len(Tair)} 天")
                extended_Tair = np.zeros(dur_date)
                extended_Tair[:len(Tair)] = Tair
                extended_Tair[len(Tair):] = Tair[-1]
                Tair = extended_Tair
            elif len(Tair) > dur_date:
                Tair = Tair[:dur_date]
    
    # 主内容区域 - 手动输入模式
    st.subheader("📊 手动输入模式")
    st.info("💡 当前使用手动参数输入模式")
    
    # 显示当前参数（带单位）
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.write("**基本参数:**")
        st.write(f"- 起始日: {day_begin}")
        st.write(f"- 结束日: {day_end}")
        st.write(f"- 水分管理模式: {water_regime_info[IP]['name']}")
        st.write(f"- 土壤砂含量: {sand}%")
    with col_info2:
        st.write("**碳氮参数:**")
        st.write(f"- 稻田外源有机质的难分解组分含量 (OMS): {OMS} kg/ha")
        st.write(f"- 稻田外源有机质的易分解组分含量 (OMN): {OMN} kg/ha")
        st.write(f"- 谷物产量 (GY): {GY} kg/ha")
        st.write(f"- 气温数据天数: {len(Tair) if Tair is not None else 0}")

# 运行模拟（两种模式通用）
if st.button("🚀 运行模拟", type="primary", use_container_width=True):
    with st.spinner("正在进行甲烷排放模拟计算..."):
        try:
            # 调试信息输出
            st.write("🔍 调试信息 - 输入参数:")
            debug_info = {
                "day_begin": day_begin,
                "day_end": day_end,
                "IP": IP,
                "sand": f"{sand}%",
                "OMS": f"{OMS} kg/ha",
                "OMN": f"{OMN} kg/ha",
                "GY": f"{GY} kg/ha",
                "Tair_length": len(Tair) if Tair is not None else 0,
                "input_method": input_method
            }
            st.json(debug_info)
            
            # 调用CH4Flux_day函数
            result_df = CH4Flux_day(
                day_begin=day_begin,
                day_end=day_end,
                IP=IP,
                sand=sand,
                Tair=Tair,
                OMS=OMS,
                OMN=OMN,
                GY=GY
            )
            
            # 显示结果
            st.success("✅ 模拟计算完成！")
            
            # 数据表格（带单位）
            st.subheader("📋 每日模拟结果")
            st.dataframe(result_df.round(4), use_container_width=True, height=300)
            
            # 关键指标可视化（带单位）
            st.subheader("📈 甲烷排放趋势")
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(result_df['DAT'], result_df['E'], label='总甲烷排放 (E, g/m²/d)', color='red', linewidth=2)
            ax.plot(result_df['DAT'], result_df['Ebl'], label='气泡排放 (Ebl, g/m²/d)', linestyle='--', color='blue', linewidth=2)
            ax.plot(result_df['DAT'], result_df['Ep'], label='植株传输 (Ep, g/m²/d)', linestyle='-.', color='green', linewidth=2)
            ax.set_xlabel('日序 (DAT)', fontsize=12)
            ax.set_ylabel('甲烷排放量 (g/m²/d)', fontsize=12)
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            
            # 辅助变量可视化（带单位）
            st.subheader("🌡️ 关键环境因子")
            fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
            ax1.plot(result_df['DAT'], result_df['Tsoil'], label='土壤温度', color='orange', linewidth=2)
            ax1.set_ylabel('土壤温度 (°C)', fontsize=12)
            ax1.legend(fontsize=10)
            ax1.grid(True, alpha=0.3)
            
            ax2.plot(result_df['DAT'], result_df['Eh'], label='氧化还原电位', color='purple', linewidth=2)
            ax2.set_xlabel('日序 (DAT)', fontsize=12)
            ax2.set_ylabel('氧化还原电位 (mV)', fontsize=12)
            ax2.legend(fontsize=10)
            ax2.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig2)
            
            # 生物量相关（带单位）
            st.subheader("🌱 生物量变化")
            fig3, ax = plt.subplots(figsize=(12, 6))
            ax.plot(result_df['DAT'], result_df['W'], label='地上生物量 (W, g/m²)', color='green', linewidth=2)
            ax.plot(result_df['DAT'], result_df['Wroot'], label='根系生物量 (Wroot, g/m²)', color='brown', linewidth=2)
            ax.set_xlabel('日序 (DAT)', fontsize=12)
            ax.set_ylabel('生物量 (g/m²)', fontsize=12)
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig3)
            
            # 总排放量统计（带单位）
            total_emission = result_df['E'].sum()
            ebl_percentage = result_df['Ebl'].sum() / total_emission * 100 if total_emission > 0 else 0
            ep_percentage = result_df['Ep'].sum() / total_emission * 100 if total_emission > 0 else 0
            
            st.subheader("📊 模拟结果统计")
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("总甲烷排放量", f"{total_emission:.2f} g/m²")
            with col_stat2:
                st.metric("气泡排放占比", f"{ebl_percentage:.1f}%")
            with col_stat3:
                st.metric("植株传输占比", f"{ep_percentage:.1f}%")
            
            # 数据导出功能
            st.subheader("💾 数据导出")
            csv = result_df.to_csv(index=False)
            st.download_button(
                label="📥 下载模拟结果CSV",
                data=csv,
                file_name=f"CH4MOD_simulation_IP{IP}_results.csv",
                mime="text/csv"
            )
            
            # 提供与Run.py类似的文本格式导出
            txt = result_df.to_csv(index=False, sep='\t')
            st.download_button(
                label="📥 下载模拟结果TXT (与Run.py格式一致)",
                data=txt,
                file_name=f"result_py.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"❌ 计算出错: {str(e)}")

# 页脚信息
st.markdown("---")
st.caption("🌾 CH4MOD稻田甲烷排放模型模拟工具 v2.0 | 支持CSV文件和手动输入两种模式 |")