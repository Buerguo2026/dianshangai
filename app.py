import streamlit as st
from zhipuai import ZhipuAI

# ========== 你的默认API Key（用户无需填写） ==========
DEFAULT_API_KEY = "68a3b840f392489c836839407335841a.OfYyPVKyni3xo4IZ"

# ========== 页面设置 ==========
st.set_page_config(page_title="电商文案AI", page_icon="🛍️")
st.title("🛍️ 电商爆款文案生成器")
st.markdown("不只是生成文案，而是生成**能出单**的文案")

# ========== 侧边栏：API Key设置 ==========
with st.sidebar:
    st.header("🔑 免费AI能力（已预填）")
    api_key = st.text_input("智谱API Key", 
                            value=DEFAULT_API_KEY,
                            type="password",
                            help="已为你预填，直接可用")
    
    st.markdown("新用户去 [open.bigmodel.cn](https://open.bigmodel.cn) 免费注册送额度")
    
    st.header("🎚️ 创意参数")
    temperature = st.slider("创意程度", 0.0, 1.5, 0.9, 0.1, 
                           help="0=保守安全，1.5=天马行空")
    
    style = st.selectbox("文案风格", 
                        ["小红书种草风", "知乎理性测评风", "朋友圈软广风", "淘宝详情页风"])
    
    st.header("🎯 目标人群")
    target_audience = st.selectbox("主要面向谁？",
                                  ["不指定", "宝妈", "学生党", "上班族", "精致女性", "中老年人", "送礼人群"])
    
    st.header("💪 文案强度")
    copy_mode = st.radio("生成模式",
                        ["通用版（安全不出错）", "爆款版（痛点+场景+强转化）"],
                        index=1)

# ========== 主界面 ==========
st.subheader("📝 输入商品信息")
col1, col2 = st.columns(2)
with col1:
    product = st.text_input("商品名称", placeholder="例如：婴儿睡袋、保温杯、素颜霜")
with col2:
    selling_point = st.text_input("核心卖点", placeholder="例如：恒温12小时、一抹提亮、A类纯棉")

optional_context = st.text_input("补充信息（选填）", 
                                 placeholder="例如：比同行便宜30%、李佳琦推荐过、适合敏感肌")

# ========== Prompt模板库 ==========
def build_prompt(style, audience, mode, product, selling_point, context):
    
    style_base = {
        "小红书种草风": "你是一个月薪3万的小红书爆款文案写手。",
        "知乎理性测评风": "你是一个有10年行业经验的消费品测评专家，知乎万粉大V。",
        "朋友圈软广风": "你是一个朋友圈卖货高手，每条文案都能带来私信询价。",
        "淘宝详情页风": "你是一个服务过100+天猫店铺的资深详情页策划。"
    }
    
    audience_hook = {
        "不指定": "",
        "宝妈": "你的读者是宝妈，最在意安全性、便利性、对宝宝好不好。",
        "学生党": "你的读者是学生，最在意性价比、颜值、宿舍能不能用。",
        "上班族": "你的读者是上班族，最在意效率、职场形象、解压放松。",
        "精致女性": "你的读者是精致女性，最在意生活品质、小众感、仪式感。",
        "中老年人": "你的读者是中老年人，最在意健康、简单操作、性价比。",
        "送礼人群": "你的读者正在挑选礼物，最在意体面、不出错、对方会不会喜欢。"
    }
    
    hardcore_rules = {
        "通用版（安全不出错）": """
基本要求：
1. 每条开头有emoji
2. 自然提到卖点
3. 带2-3个话题标签""",
        
        "爆款版（痛点+场景+强转化）": """
必须严格遵守以下铁律（缺一不可）：
1. 【痛点开头】用emoji+真实场景痛点或爽点开头（模板："谁懂啊/救大命/哭了/终于找到了/后悔没早买"）
2. 【具体体验】必须有可感知的使用体验（数字/触感/对比/时间），禁止说"很好/很棒/很舒服"这种空话
3. 【人群喊话】必须明确对一类人喊话（"XX党闭眼冲/XX人必入/给XX的忠告"）
4. 【行动指令】结尾必须有明确的购买暗示（"链接放这里了/还在犹豫的真的亏了/这个价只能锁三天"）
5. 【禁止词】严禁使用"真的超实用""赶快来试试""强烈推荐"这类废话，出现一次就算不合格"""
    }
    
    prompt = f"""
{style_base[style]}
{audience_hook[audience]}

请为商品【{product}】生成5条文案。
核心卖点：【{selling_point}】
{f"补充信息：【{context}】" if context else ""}

{hardcore_rules[mode]}

要求每条80字以内，带2-3个标签。
请直接输出5条，用数字序号分隔。
"""
    return prompt


# ========== 生成按钮 ==========
if st.button("🚀 生成文案", type="primary", use_container_width=True):
    
    if not api_key:
        st.error("❌ 请先在侧边栏填写API Key")
    elif not product:
        st.error("❌ 请输入商品名称")
    else:
        client = ZhipuAI(api_key=api_key)
        
        prompt = build_prompt(style, target_audience, copy_mode, product, selling_point, optional_context)
        
        with st.spinner("⏳ AI正在疯狂创作中..."):
            try:
                response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=800,
                )
                
                result = response.choices[0].message.content
                
                st.success("✅ 生成完成！")
                st.markdown("### 📝 生成的文案")
                st.markdown(result)
                
                if copy_mode == "爆款版（痛点+场景+强转化）":
                    st.info("💡 当前为爆款模式，文案已加入痛点场景和行动指令，更适合直接投放")
                
                st.download_button(
                    label="📥 下载文案（TXT）",
                    data=result,
                    file_name=f"{product}_文案.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"❌ 出错了：{e}")
                st.info("请检查：1. API Key是否正确 2. 网络是否畅通")

# ========== 页脚 ==========
st.markdown("---")
st.markdown("💪 爆款文案有了，下一步：批量生成 + 数据分析")
