package com.example.jmh.nettytest.udp.handler;

import com.example.jmh.nettytest.udp.po.LogEvent;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;

/**
 * @auther liuhe
 * @className Log
 * @description TODO
 * @date 2021/4/28 7:51 下午
 */
public class LogEventHandler extends SimpleChannelInboundHandler<LogEvent> {
    @Override
    protected void channelRead0(ChannelHandlerContext ctx, LogEvent msg) throws Exception {
        StringBuilder append = new StringBuilder()
                .append(msg.getReceived())
                .append(" [")
                .append(msg.getSource().toString())
                .append("] [")
                .append(msg.getLogFile())
                .append("] : ")
                .append(msg.getMsg());
        System.out.println(append.toString());
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) throws Exception {
        cause.printStackTrace();
        ctx.close();
    }
}
