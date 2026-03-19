import streamlit as st
from streamlit_echarts import st_echarts

score = 79

option = {
    "series": [
        {
            "type": "gauge",
            "startAngle": 180,
            "endAngle": 0,
            "progress": {
                "show": True,
                "width": 20,
                "roundCap": True
            },
            "axisLine": {
                "lineStyle": {
                    "width": 20,
                    "color": [[1, "#d1d5db"]]
                }
            },
            "detail": {"formatter": "{value}/100"},
            "data": [{"value": score}]
        }
    ]
}

st_echarts(option, height="300px")