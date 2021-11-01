package com.example.jmh.nettytest.websocket.handler;

import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.channel.group.ChannelGroup;
import io.netty.handler.codec.http.websocketx.TextWebSocketFrame;
import io.netty.handler.codec.http.websocketx.WebSocketServerProtocolHandler;

/**
 * @auther liuhe
 * @className TextWebSocketFrameHandler
 * @description TODO
 * @date 2021/4/26 1:14 下午
 */
public class TextWebSocketFrameHandler extends SimpleChannelInboundHandler<TextWebSocketFrame> {

    private final ChannelGroup channelGroup;

    public TextWebSocketFrameHandler(ChannelGroup channelGroup) {
        this.channelGroup = channelGroup;
    }

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, TextWebSocketFrame msg) throws Exception {
        //增加引用计数器(因为实现的为SimpleChannelInboundHandler.channelRead0()方法  处理完成之后会进行回收)
        //将消息输出给 ChannelGroup 中每一个已连接客户端
        channelGroup.writeAndFlush(msg.retain());
    }

    @Override
    public void userEventTriggered(ChannelHandlerContext ctx, Object evt) throws Exception {
        if (evt instanceof WebSocketServerProtocolHandler.HandshakeComplete) {
            //如果是该事件表示握手成功  则从该管线中移除 HttpRequestHandler 因为将不会接收到任何消息
            ctx.pipeline().remove(HttpRequestHandler.class);
            //通知所有已经连接的WebSocket客户端新的连接已经连接上
            channelGroup.writeAndFlush(new TextWebSocketFrame("新客户端 " + ctx.channel() + " 加入"));
            //将新的管道加入 ChannelGroup 以便它可以接受到所有消息
            channelGroup.add(ctx.channel());
        } else {
            super.userEventTriggered(ctx, evt);
        }
    }
}
