import streamlit as st


def typesetting_1():
    st.markdown("# 半包粘包产生原因")
    st.markdown("### 半包：")
    st.markdown("""
    半包就是收到了半个包，它是由于发送包的大小比TCP发送缓存的容量大，具体说就是客户端发的数据大于套接字缓冲区大小，或者是大于协议的MTU
    (Maximum Transmission Unit )。这样数据包会分成多个包，通过Socket多次发送到服务端。服务端没法一次接收到整个包的数据，只接收了当前TCP
    缓存里面的部分，就是半包。所以说半包并不是严格意义上的收到了半个包，收到包的一部分都叫半包。 
    """)

    st.markdown("### 粘包：")
    st.markdown("""
    粘包和半包对应，就是多个包在一个TCP缓存里面一次发送过来了，这样如果服务端接收缓存相当于一次读了多个包进来，这就叫粘包。所以说粘包产生的根本
    原因在于客户端每次写入数据小于套接字缓冲区大小，还有就是接收方读取套接字缓冲区数据又不够及时，导致累积了多个包一起读。
    """)
    st.markdown("---")


def typesetting_2():
    st.markdown("# Netty 中解决办法")
    st.markdown("""
    既然半包和粘包产生的原因在于数据包没有一个一个的在服务端读取，那么要解决它就是把这个边界，或者说切分点找出来，把他分成或者是组合成一个个完
    整的数据包让客户端读取就好了。这个切分，主要采用封装成帧的方式：
    """)
    st.image("./images/halfpack_stickypack/img.png", width=700)
    st.write("")

    st.markdown("** Netty 中针对上述封装成帧的办法都做了具体实现：**")
    st.image("./images/halfpack_stickypack/img_1.png", width=700)
    st.markdown("---")

    st.markdown("### FixedLengthFrameDecoder(固定长度解码)：")
    st.code("""
@Override
protected void initChannel(Channel ch) throws Exception {
    ChannelPipeline pipeline = ch.pipeline();
    
    // 每128个字节作为一个完整帧处理
    pipeline.addLast(new FixedLengthFrameDecoder(128));
    
    pipeline.addLast(new FrameHandler());
}
    """, language="java")

    st.markdown("### DelimiterBasedFrameDecoder(分割符解码)：")
    st.code("""
@Override
protected void initChannel(Channel ch) throws Exception {
    ChannelPipeline pipeline = ch.pipeline();

    //分隔符解码器
    ByteBuf byteBuf = Unpooled.copiedBuffer("|".getBytes());
    pipeline.addLast(new DelimiterBasedFrameDecoder(64 * 1024, byteBuf));

    //将消息解码为CMD对象
    pipeline.addLast(new CmdDecoder(64 * 1024));
    //处理CMD对象
    pipeline.addLast(new CmdHandler());
}
    """, language="java")

    st.markdown("### LengthFieldBasedFrameDecoder(固定长度字段内容)：")
    st.code("""
@Override
protected void initChannel(Channel ch) throws Exception {
    ChannelPipeline pipeline = ch.pipeline();

    /*
    前2位字节封装报文长度信息，后续完整报文根据长度信息获取
    
    lengthFieldOffset   = 0
    lengthFieldLength   = 2
    lengthAdjustment    = 0
    initialBytesToStrip = 2 (= the length of the Length field)
      
    BEFORE DECODE (14 bytes)         AFTER DECODE (12 bytes)
    +--------+----------------+      +----------------+
    | Length | Actual Content |----->| Actual Content |
    | 0x000C | "HELLO, WORLD" |      | "HELLO, WORLD" |
    +--------+----------------+      +----------------+
     */
    pipeline.addLast(new LengthFieldBasedFrameDecoder(64 * 1024, 0, 2));

    pipeline.addLast(new FrameHandler());
}
    """, language="java")
    st.markdown("---")

    st.markdown("** 三者都是通过继承 ByteToMessageDecoder 作为解码器实现，核心方法入口都在解码入口 ** protected abstract void decode("
                "ChannelHandlerContext ctx, ByteBuf in, List<Object> out) throws Exception;  ** 中。其原理较为简单，就是按照规定规则"
                "处理字节、缓存字节。实际使用中我们可以按照需求自己实现编解码器 **")


def half_pack_sticky_pack():
    typesetting_1()
    typesetting_2()
