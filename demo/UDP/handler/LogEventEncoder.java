package com.example.jmh.nettytest.udp.handler;

import com.example.jmh.nettytest.udp.po.LogEvent;
import io.netty.buffer.ByteBuf;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.socket.DatagramPacket;
import io.netty.handler.codec.MessageToMessageEncoder;
import io.netty.util.CharsetUtil;

import java.net.InetSocketAddress;
import java.util.List;

/**
 * @auther liuhe
 * @className LogEventEncoder
 * @description UDP传输编码类
 * @date 2021/4/28 1:31 下午
 */
public class LogEventEncoder extends MessageToMessageEncoder<LogEvent> {

    /**
     * LogEventEncoder创建了即将被发送到指定的InetSocketAddress的DatagramPacket消息
     */
    private final InetSocketAddress remoteAddress;

    public LogEventEncoder(InetSocketAddress remoteAddress) {
        this.remoteAddress = remoteAddress;
    }

    @Override
    protected void encode(ChannelHandlerContext ctx, LogEvent msg, List<Object> out) throws Exception {
        byte[] file = msg.getLogFile().getBytes(CharsetUtil.UTF_8);
        byte[] message = msg.getMsg().getBytes(CharsetUtil.UTF_8);

        ByteBuf buffer = ctx.alloc().buffer(file.length + message.length + 1);

        //将文件名写入到ByteBuf中
        buffer.writeBytes(file);
        //添加一个SEPARATOR
        buffer.writeByte(LogEvent.SEPARATOR);
        //将日志信息写入ByteBuf中
        buffer.writeBytes(message);

        //将一个拥有数据和目的地地址的新DatagramPacket添加到出站的消息列表中
        out.add(new DatagramPacket(buffer, remoteAddress));
    }
}
