"""
UI: Google Analytics - Multi-website analytics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from config import GA_WEBSITES
from auth import get_analytics_data, get_popular_pages


def render_ga_ui(filtered, df):
    """GA mode wrapper - handles sidebar + render_ga"""
    st.sidebar.markdown("**📊 Google Analytics**")
    enable_comparison = st.sidebar.checkbox("⚖️ So sánh nhiều website", value=False)
    selected_websites = st.sidebar.multiselect(
        "🌐 Chọn website", 
        options=list(GA_WEBSITES.keys()), 
        default=[list(GA_WEBSITES.keys())[0]],
        max_selections=3
    )
    render_ga(selected_websites=selected_websites, enable_comparison=enable_comparison)


def render_ga(selected_websites, enable_comparison):
    """Render trang Google Analytics với so sánh websites"""

    st.markdown('<p class="section-header">📊 Google Analytics</p>', unsafe_allow_html=True)
    
    # Date inputs (shared for all sites)
    col1, col2 = st.columns(2)
    with col1:
        ga_start = st.date_input("Từ ngày", datetime.now() - timedelta(days=30))
    with col2:
        ga_end = st.date_input("Đến ngày", datetime.now())
    
    # Load data for selected websites
    ga_data = {}
    ga_pages = {}
    load_success = True
    
    if st.button(f"🔄 Tải dữ liệu ({len(selected_websites)} website{'s' if len(selected_websites)>1 else ''})"):
        with st.spinner("⏳ Đang tải dữ liệu GA..."):
            for site in selected_websites:
                PROPERTY_ID = GA_WEBSITES[site]
                get_analytics_data.clear()
                get_popular_pages.clear()
                
                data = get_analytics_data(PROPERTY_ID, ga_start.strftime("%Y-%m-%d"), ga_end.strftime("%Y-%m-%d"))
                pages = get_popular_pages(PROPERTY_ID, ga_start.strftime("%Y-%m-%d"), ga_end.strftime("%Y-%m-%d"))
                
                if data:
                    ga_data[site] = pd.DataFrame(data)
                    ga_pages[site] = pd.DataFrame(pages) if pages else pd.DataFrame()
                else:
                    load_success = False
                    st.error(f"❌ Không tải được dữ liệu cho {site}")
            
            if load_success:
                st.session_state.ga_data_multi = ga_data
                st.session_state.ga_pages_multi = ga_pages
                st.success(f"✅ Tải thành công {len(ga_data)}/{len(selected_websites)} websites")
    
    if not load_success or not st.session_state.get('ga_data_multi'):
        st.info("👆 Nhấn nút tải dữ liệu trước")
        return
    
    ga_data_multi = st.session_state.ga_data_multi
    ga_pages_multi = st.session_state.ga_pages_multi
    
    # Prepare ga_df for all tabs (always have Website column)
    if len(selected_websites) == 1:
        site = selected_websites[0]
        ga_df = ga_data_multi[site].copy()
        ga_df['Website'] = site
        pages_df = ga_pages_multi.get(site, pd.DataFrame())
    else:
        # Multi-site with Website index 
        dfs = []
        for site, df in ga_data_multi.items():
            df_site = df.copy()
            df_site['Website'] = site
            dfs.append(df_site)
        ga_df = pd.concat(dfs, ignore_index=True)
        pages_list = []
        for site, pages in ga_pages_multi.items():
            if not pages.empty:
                pages_site = pages.copy()
                pages_site['Website'] = site
                pages_list.append(pages_site)
        pages_df = pd.concat(pages_list, ignore_index=True) if pages_list else pd.DataFrame()
    
    # Metrics (aggregated)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("👥 Người dùng", f"{ga_df['Người dùng'].sum():,}")
    with col2:
        st.metric("🔄 Phiên", f"{ga_df['Phiên'].sum():,}")
    with col3:
        st.metric("📄 Lượt xem", f"{ga_df['Lượt xem'].sum():,}")
    with col4:
        st.metric("⏱️ Thời lượng TB", f"{ga_df['Thời lượng TB'].mean():.1f}s")
    with col5:
        st.metric("⚡ Tỷ lệ thoát TB", f"{ga_df['Tỷ lệ thoát'].mean():.1%}")
    
    # Dynamic tabs
    if enable_comparison and len(selected_websites) > 1:
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 Biểu đồ", "🌍 Quốc gia", "🏙️ Thành phố", "📱 Thiết bị", "🔥 Top trang", "📋 Dữ liệu", "⚖️ So sánh Website"])
    else:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Biểu đồ", "🌍 Quốc gia", "🏙️ Thành phố", "📱 Thiết bị", "🔥 Top trang", "📋 Dữ liệu"])
        tab7 = None
    
    with tab1:
        render_chart_tab(ga_df)
    
    with tab2:
        render_country_tab(ga_df)
    
    with tab3:
        render_city_tab(ga_df)
    
    with tab4:
        render_device_tab(ga_df)
    
    with tab5:
        render_pages_tab(pages_df)
    
    with tab6:
        render_data_tab(ga_df)
    
    if tab7 is not None:
        with tab7:
            render_comparison_tab(selected_websites, ga_data_multi)


def render_chart_tab(ga_df):
    """Render Biểu đồ tab content"""
    # Người dùng theo ngày
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📈 Người dùng theo ngày")
        daily_users = ga_df.groupby('Ngày')['Người dùng'].sum().reset_index()
        daily_users['Ngày'] = pd.to_datetime(daily_users['Ngày'], format='%Y%m%d')
        daily_users = daily_users.sort_values('Ngày')
        fig1 = px.line(daily_users, x='Ngày', y='Người dùng', markers=True, color_discrete_sequence=['#667eea'])
        fig1.update_layout(height=350, hovermode='x unified', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, width='stretch')
    
    with col_b:
        st.subheader("📊 Phiên theo ngày")
        daily_sessions = ga_df.groupby('Ngày')['Phiên'].sum().reset_index()
        daily_sessions['Ngày'] = pd.to_datetime(daily_sessions['Ngày'], format='%Y%m%d')
        daily_sessions = daily_sessions.sort_values('Ngày')
        fig2 = px.bar(daily_sessions, x='Ngày', y='Phiên', color='Phiên', color_continuous_scale='Viridis')
        fig2.update_layout(height=350, hovermode='x unified', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig2, width='stretch')

    # Source breakdown
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.subheader("🔗 Top Nguồn truy cập")
        source_data = ga_df.groupby('Nguồn')['Phiên'].sum().nlargest(8).reset_index()
        fig3 = px.bar(source_data, x='Phiên', y='Nguồn', orientation='h', color='Phiên', color_continuous_scale='Blues')
        fig3.update_layout(height=350, showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, width='stretch')
    
    with col_d:
        st.subheader("📋 Top Quốc gia")
        country_data = ga_df.groupby('Quốc gia')['Người dùng'].sum().nlargest(10).reset_index()
        fig4 = px.bar(country_data, x='Người dùng', y='Quốc gia', orientation='h', color='Người dùng', color_continuous_scale='Greens')
        fig4.update_layout(height=350, showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig4, width='stretch')


def render_country_tab(ga_df):
    """Render Quốc gia tab content"""
    st.subheader("🌍 Phân tích theo Quốc gia")
    country_detail = ga_df.groupby('Quốc gia').agg({
        'Người dùng': 'sum',
        'Phiên': 'sum',
        'Lượt xem': 'sum',
        'Thời lượng TB': 'mean',
        'Tỷ lệ thoát': 'mean'
    }).reset_index().sort_values('Người dùng', ascending=False)
    
    col_x, col_y = st.columns(2)
    with col_x:
        fig_country = px.pie(country_detail.head(10), values='Người dùng', names='Quốc gia', hole=0.4)
        fig_country.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_country, width='stretch')
    
    with col_y:
        st.dataframe(country_detail[['Quốc gia', 'Người dùng', 'Phiên', 'Lượt xem']].head(15), width='stretch')


def render_city_tab(ga_df):
    """Render Thành phố tab content"""
    st.subheader("🏙️ Phân tích theo Thành phố")
    city_detail = ga_df.groupby(['Quốc gia', 'Thành phố']).agg({
        'Người dùng': 'sum',
        'Phiên': 'sum',
        'Lượt xem': 'sum',
        'Thời lượng TB': 'mean',
        'Tỷ lệ thoát': 'mean'
    }).reset_index().sort_values('Người dùng', ascending=False)
    
    # Remove (not set) or empty cities
    city_detail = city_detail[city_detail['Thành phố'] != '(not set)'].copy()
    
    col_city1, col_city2 = st.columns(2)
    
    with col_city1:
        st.markdown("#### 🏙️ Top 10 Thành phố")
        top_cities = city_detail.head(10)
        if not top_cities.empty:
            fig_city = px.bar(top_cities, x='Người dùng', y='Thành phố', orientation='h', 
                             color='Người dùng', color_continuous_scale='Reds', text='Người dùng')
            fig_city.update_traces(textposition='outside')
            fig_city.update_layout(height=400, showlegend=False, plot_bgcolor='rgba(0,0,0,0)', 
                                 yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_city, width='stretch')
    
    with col_city2:
        st.markdown("#### 📊 Chi tiết Top thành phố")
        if not city_detail.empty:
            display_cities = city_detail.head(15)[['Quốc gia', 'Thành phố', 'Người dùng', 'Phiên', 'Lượt xem']].copy()
            display_cities.columns = ['Quốc gia', 'Thành phố', 'Người dùng', 'Phiên', 'Lượt xem']
            st.dataframe(display_cities, width='stretch', hide_index=True)
    
    # Country detail
    st.markdown("---")
    st.markdown("#### 🗺️ Chi tiết vị trí theo quốc gia")
    
    countries_list = sorted(ga_df['Quốc gia'].unique())
    selected_country_detail = st.selectbox("Chọn quốc gia để xem thành phố", countries_list)
    
    if selected_country_detail:
        country_cities = ga_df[ga_df['Quốc gia'] == selected_country_detail].groupby('Thành phố').agg({
            'Người dùng': 'sum',
            'Phiên': 'sum',
            'Lượt xem': 'sum'
        }).reset_index().sort_values('Người dùng', ascending=False)
        
        country_cities = country_cities[country_cities['Thành phố'] != '(not set)'].copy()
        
        if not country_cities.empty:
            st.markdown(f"**{selected_country_detail}** - Tổng {len(country_cities)} thành phố")
            st.dataframe(country_cities, width='stretch', hide_index=True)
        else:
            st.info(f"Không có dữ liệu chi tiết thành phố cho {selected_country_detail}")
    
    # City trend chart
    st.markdown("---")
    st.markdown("#### 📈 Xu hướng người dùng theo ngày (Top 5 thành phố)")
    
    top_5_cities = city_detail.head(5)['Thành phố'].tolist()
    
    if top_5_cities and len(ga_df) > 0:
        fig_city_trend = go.Figure()
        
        colors_palette = ['#667eea', '#ef4444', '#10b981', '#f59e0b', '#3b82f6']
        
        for idx, city_name in enumerate(top_5_cities):
            city_data = ga_df[ga_df['Thành phố'] == city_name].groupby('Ngày')['Người dùng'].sum().reset_index()
            city_data['Ngày'] = pd.to_datetime(city_data['Ngày'], format='%Y%m%d')
            city_data = city_data.sort_values('Ngày')
            
            if not city_data.empty:
                fig_city_trend.add_trace(go.Scatter(
                    x=city_data['Ngày'],
                    y=city_data['Người dùng'],
                    mode='lines+markers',
                    name=city_name,
                    line=dict(color=colors_palette[idx % len(colors_palette)], width=3),
                    marker=dict(size=8)
                ))
        
        fig_city_trend.update_layout(
            height=450,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Ngày',
            yaxis_title='Số người dùng',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig_city_trend, width='stretch')


def render_device_tab(ga_df):
    """Render Thiết bị tab content"""
    device_data = ga_df.groupby(['Website', 'Thiết bị'])['Người dùng'].sum().reset_index()
    fig4 = px.pie(device_data, values='Người dùng', names='Thiết bị', color='Website')
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, width='stretch')


def render_pages_tab(pages_df):
    """Render Top trang tab content"""
    if pages_df is not None and not pages_df.empty:
        st.dataframe(pages_df.reset_index(), width='stretch')
    else:
        st.info("No pages data")


def render_data_tab(ga_df):
    """Render Dữ liệu tab content"""
    st.markdown("### 📋 Dữ liệu thô")
    st.dataframe(ga_df.reset_index(), width='stretch', height=600)


def render_comparison_tab(selected_websites, ga_data_multi):
    """Render So sánh Website tab content"""
    st.subheader("⚖️ So sánh Website")
    
    # Overview comparison table
    st.markdown("#### 📊 So sánh Tổng quan")
    
    comparison_metrics = []
    for site in selected_websites:
        if site in ga_data_multi:
            df_temp = ga_data_multi[site]
            comparison_metrics.append({
                'Website': site,
                'Người dùng': f"{df_temp['Người dùng'].sum():,}",
                'Phiên': f"{df_temp['Phiên'].sum():,}",
                'Lượt xem': f"{df_temp['Lượt xem'].sum():,}",
                'Thời lượng TB': f"{df_temp['Thời lượng TB'].mean():.1f}s",
                'Tỷ lệ thoát': f"{df_temp['Tỷ lệ thoát'].mean():.1%}"
            })
    
    if comparison_metrics:
        comparison_df = pd.DataFrame(comparison_metrics)
        st.dataframe(comparison_df, width=800, hide_index=True)
    
    st.divider()
    
    # Comparison charts
    colors_list = ['#667eea', '#f59e0b', '#10b981', '#ef4444']
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### 📈 Người dùng theo ngày")
        daily_users_combined = []
        
        for idx, site in enumerate(selected_websites):
            if site in ga_data_multi:
                df_temp = ga_data_multi[site].copy()
                if df_temp['Ngày'].dtype == 'object':
                    df_temp['Ngày'] = pd.to_datetime(df_temp['Ngày'], format='%Y%m%d')
                
                daily = df_temp.groupby('Ngày')['Người dùng'].sum().reset_index()
                daily['Website'] = site
                daily_users_combined.append(daily)
        
        if daily_users_combined:
            combined_data = pd.concat(daily_users_combined, ignore_index=True)
            combined_data['Ngày'] = pd.to_datetime(combined_data['Ngày'])
            combined_data = combined_data.sort_values('Ngày')
            
            fig_users = px.line(
                combined_data,
                x='Ngày', y='Người dùng', color='Website',
                markers=True,
                color_discrete_sequence=colors_list[:len(selected_websites)]
            )
            fig_users.update_layout(height=450, hovermode='x unified')
            st.plotly_chart(fig_users, use_container_width=True)
    
    with col_chart2:
        st.markdown("#### 📊 Phiên theo ngày")
        daily_sessions_combined = []
        
        for site in selected_websites:
            if site in ga_data_multi:
                df_temp = ga_data_multi[site].copy()
                if df_temp['Ngày'].dtype == 'object':
                    df_temp['Ngày'] = pd.to_datetime(df_temp['Ngày'], format='%Y%m%d')
                
                daily = df_temp.groupby('Ngày')['Phiên'].sum().reset_index()
                daily['Website'] = site
                daily_sessions_combined.append(daily)
        
        if daily_sessions_combined:
            combined_sessions = pd.concat(daily_sessions_combined, ignore_index=True)
            combined_sessions['Ngày'] = pd.to_datetime(combined_sessions['Ngày'])
            combined_sessions = combined_sessions.sort_values('Ngày')
            
            fig_sessions = px.bar(
                combined_sessions,
                x='Ngày', y='Phiên', color='Website',
                barmode='group',
                color_discrete_sequence=colors_list[:len(selected_websites)]
            )
            fig_sessions.update_layout(height=450, hovermode='x unified')
            st.plotly_chart(fig_sessions, use_container_width=True)
    
    st.divider()
    
    # Top sources per site
    st.markdown("#### 🔗 Top Nguồn truy cập")
    cols = st.columns(min(3, len(selected_websites)))
    
    for idx, site in enumerate(selected_websites):
        with cols[idx % len(cols)]:
            if site in ga_data_multi:
                df_temp = ga_data_multi[site]
                st.markdown(f"**{site}**")
                source_data = df_temp.groupby('Nguồn')['Phiên'].sum().nlargest(5).reset_index()
                fig_src = px.bar(source_data, x='Phiên', y='Nguồn', orientation='h')
                fig_src.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig_src, use_container_width=True)
