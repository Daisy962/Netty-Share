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
public class LogEventMonitor {

    private final EventLoopGroup group;
    private final Bootstrap bootstrap;


    public LogEventMonitor(InetSocketAddress address) {
        group = new NioEventLoopGroup();

        bootstrap = new Bootstrap();
        bootstrap.group(group)
                //设置UDP协议管道
                .channel(NioDatagramChannel.class)
                //设置广播模式
                .option(ChannelOption.SO_BROADCAST, true)
                //设置共享统一端口(本机测试使用)
                .option(ChannelOption.SO_REUSEADDR, true)
                .handler(new ChannelInitializer<Channel>() {
                    @Override
                    protected void initChannel(Channel ch) throws Exception {
                        ch.pipeline()
                                //添加解码器
                                .addLast(new LogEventDecoder())
                                //添加用于处理解码之后的 LogEvent 的Handler
                                .addLast(new LogEventHandler());
                    }
                })
                //绑定本地地址
                .localAddress(address);
    }

    public Channel bind() {
        //DatagramChannel是无连接的
        return bootstrap.bind().syncUninterruptibly().channel();
    }

    public void stop() {
        group.shutdownGracefully();
    }

    public static void main(String[] args) {
        //绑定本机端口
        LogEventMonitor logEventMonitor = new LogEventMonitor(new InetSocketAddress(7777));

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
