package com.example.jmh.nettytest.udp.handler;

import com.example.jmh.nettytest.udp.po.LogEvent;
import io.netty.buffer.ByteBuf;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.socket.DatagramPacket;
import io.netty.handler.codec.MessageToMessageDecoder;
import io.netty.util.CharsetUtil;

import java.util.List;

/**
 * @auther liuhe
 * @className LogEventDecoder
 * @description TODO
 * @date 2021/4/28 7:40 下午
 */
public class LogEventDecoder extends MessageToMessageDecoder<DatagramPacket> {

    @Override
    protected void decode(ChannelHandlerContext ctx, DatagramPacket msg, List<Object> out) throws Exception {
        //获取DatagramPacket中的数据(ByteBuf)的引用
        ByteBuf content = msg.content();

        //获取到分隔符 SEPARATOR 的索引
        int i = content.indexOf(0, content.readableBytes(), LogEvent.SEPARATOR);

        //提取文件名
        String fileName = content.slice(0, i).toString(CharsetUtil.UTF_8);

        //提起日志数据
        String logMsg = content.slice(i + 1, content.readableBytes()).toString(CharsetUtil.UTF_8);

        //封装为logEvent
        LogEvent logEvent = new LogEvent(msg.sender(), fileName, logMsg, System.currentTimeMillis());

        out.add(logEvent);
    }
}
