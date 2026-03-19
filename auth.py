"""
Xác thực Google Sheets và Google Analytics
"""

import streamlit as st
import json
import os
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest


# ===================== GOOGLE SHEETS AUTH =====================
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]


def has_secrets():
    """Kiểm tra nếu đang chạy trên Streamlit Cloud"""
    try:
        if hasattr(st, 'secrets') and st.secrets:
            return bool(st.secrets)
        return False
    except FileNotFoundError:
        return False
    except Exception:
        return False


def get_gcp_credentials():
    """Lấy GCP credentials từ secrets hoặc file local"""
    if has_secrets() and "gcp_service_account" in st.secrets:
        return st.secrets["gcp_service_account"]
    else:
        with open('credentials.json', 'r') as f:
            return json.load(f)


def get_sheets_client(creds_dict):
    """Tạo Google Sheets client"""
    import gspread
    
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    return gspread.authorize(creds)


def init_sheets_client():
    """Khởi tạo Google Sheets client - main entry point"""
    try:
        creds_dict = get_gcp_credentials()
        return get_sheets_client(creds_dict)
    except Exception as e:
        st.error(f"❌ Không thể tải credentials: {e}")
        st.info("💡 Để sử dụng Streamlit Cloud, thêm [gcp_service_account] vào .streamlit/secrets.toml")
        st.stop()


# ===================== GOOGLE ANALYTICS AUTH =====================
def get_ga_credentials():
    """Lấy credentials cho Google Analytics"""
    return get_gcp_credentials()


def get_ga_client():
    """Tạo Google Analytics client"""
    ga_creds = get_gcp_credentials()
    return service_account.Credentials.from_service_account_info(
        ga_creds,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )


@st.cache_data(ttl=600)
def get_analytics_data(property_id, start_date, end_date):
    """Lấy dữ liệu Google Analytics"""
    try:
        credentials = get_ga_client()
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="date"),
                Dimension(name="country"),
                Dimension(name="city"),
                Dimension(name="deviceCategory"),
                Dimension(name="sessionSource"),
            ],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate"),
            ],
        )
        
        response = client.run_report(request)
        data = []
        for row in response.rows:
            data.append({
                'Ngày': row.dimension_values[0].value,
                'Quốc gia': row.dimension_values[1].value,
                'Thành phố': row.dimension_values[2].value,
                'Thiết bị': row.dimension_values[3].value,
                'Nguồn': row.dimension_values[4].value,
                'Người dùng': int(row.metric_values[0].value),
                'Phiên': int(row.metric_values[1].value),
                'Lượt xem': int(row.metric_values[2].value),
                'Thời lượng TB': float(row.metric_values[3].value),
                'Tỷ lệ thoát': float(row.metric_values[4].value),
            })
        return data
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Google Analytics: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_popular_pages(property_id, start_date, end_date):
    """Lấy dữ liệu trang phổ biến từ Google Analytics"""
    try:
        credentials = get_ga_client()
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="activeUsers"),
                Metric(name="averageSessionDuration"),
            ],
            limit=10,
        )
        
        response = client.run_report(request)
        data = []
        for row in response.rows:
            data.append({
                'Đường dẫn': row.dimension_values[0].value,
                'Tiêu đề': row.dimension_values[1].value,
                'Lượt xem': int(row.metric_values[0].value),
                'Người dùng': int(row.metric_values[1].value),
                'Thời lượng TB': float(row.metric_values[2].value),
            })
        return data
    except Exception as e:
        st.error(f"❌ Lỗi khi lấy trang phổ biến: {str(e)}")
        return None

