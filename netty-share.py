"""
Netty 分享
"""
import streamlit as st

import share.fundamental as fundamental
import share.read_bytebuf_size as rbs
import share.zero_copy as zc
import share.heartbeat_mechanism as hm
import share.halfpack_stickypack as hs
import share.fast_thread_local as ftl
import share.use_points as up

st.sidebar.title('Netty')
choose = st.sidebar.radio('目录', ('基本原理',
                                 'Netty核心组件及设计',
                                 '缓冲区实现机制(ByteBuf)',
                                 '零拷贝',
                                 '心跳机制',
                                 '半包粘包',
                                 'FastThreadLocal实现原理',
                                 '使用要点'), index=0)

if choose == '基本原理':
    fundamental.fundamental()
if choose == 'Netty核心组件及设计':
    fundamental.typesetting_3()
if choose == '缓冲区实现机制(ByteBuf)':
    rbs.read_bytebuf_size()
if choose == '零拷贝':
    zc.zero_copy()
if choose == '心跳机制':
    hm.heartbeat_mechanism()
if choose == '半包粘包':
    hs.half_pack_sticky_pack()
if choose == 'FastThreadLocal实现原理':
    ftl.fast_thread_local()
if choose == '使用要点':
    up.use_points()
