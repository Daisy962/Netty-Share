package com.example.jmh.nettytest.udp.client;

import com.example.jmh.nettytest.udp.handler.LogEventDecoder;
import com.example.jmh.nettytest.udp.handler.LogEventHandler;
import io.netty.bootstrap.Bootstrap;
import io.netty.channel.Channel;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.ChannelOption;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.nio.NioDatagramChannel;

import java.net.InetSocketAddress;

/**
 * @auther liuhe
 * @className LogEventMonitor
 * @description TODO
 * @date 2021/4/28 7:55 下午
 */
public class LogEventMonitor1 {

    private final EventLoopGroup group;
    private final Bootstrap bootstrap;


    public LogEventMonitor1(InetSocketAddress address) {
        group = new NioEventLoopGroup();

        bootstrap = new Bootstrap();
        bootstrap.group(group)
                .channel(NioDatagramChannel.class)
                .option(ChannelOption.SO_BROADCAST, true)
                .option(ChannelOption.SO_REUSEADDR, true)
                .handler(new ChannelInitializer<Channel>() {
                    @Override
                    protected void initChannel(Channel ch) throws Exception {
                        ch.pipeline()
                                .addLast(new LogEventDecoder())
                                .addLast(new LogEventHandler());
                    }
                })
                .localAddress(address);
    }

    public Channel bind() {
        return bootstrap.bind().syncUninterruptibly().channel();
    }

    public void stop() {
        group.shutdownGracefully();
    }

    public static void main(String[] args) {
        LogEventMonitor1 logEventMonitor = new LogEventMonitor1(new InetSocketAddress(7777));

        try {
            Channel bind = logEventMonitor.bind();
            System.out.println("LogEventMonitor Running");
            bind.closeFuture().sync();
        } catch (InterruptedException exception) {
            exception.printStackTrace();
        } finally {
            logEventMonitor.stop();
        }
    }

}
