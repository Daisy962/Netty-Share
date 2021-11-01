package com.example.jmh.nettytest.websocket.server;

import com.example.jmh.nettytest.websocket.initializer.ChatServerInitializer;
import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.Channel;
import io.netty.channel.ChannelFuture;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.group.ChannelGroup;
import io.netty.channel.group.DefaultChannelGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import io.netty.util.concurrent.ImmediateEventExecutor;

import javax.net.ssl.SSLException;
import java.net.InetSocketAddress;
import java.security.cert.CertificateException;

/**
 * @auther liuhe
 * @className ChatServer
 * @description TODO
 * @date 2021/4/27 1:05 下午
 */
public class ChatServer {

    private final ChannelGroup channelGroup = new DefaultChannelGroup(ImmediateEventExecutor.INSTANCE);
    private final EventLoopGroup group = new NioEventLoopGroup();
    private Channel channel;

    //配置监听并获取连接
    ChannelFuture start(InetSocketAddress inetSocketAddress) {
        ChannelFuture bind = new ServerBootstrap()
                .group(group)
                .channel(NioServerSocketChannel.class)
                .childHandler(getInit(channelGroup))
                .bind(inetSocketAddress);

        bind.syncUninterruptibly();

        channel = bind.channel();

        return bind;
    }

    protected ChannelInitializer<Channel> getInit(ChannelGroup channelGroup){
        return new ChatServerInitializer(channelGroup);
    }

    void destroy(){
        if (channel != null) {
            channel.close();
        }

        channelGroup.close();
        group.shutdownGracefully();
    }

    public static void main(String[] args) throws CertificateException, SSLException {
        ChatServer chatServer = new ChatServer();

        ChannelFuture start = chatServer.start(new InetSocketAddress(9999));

        //系统关闭时  关闭服务端
        Runtime.getRuntime().addShutdownHook(new Thread(chatServer::destroy));

        //阻塞等待连接关闭
        start.channel().closeFuture().syncUninterruptibly();
    }

}
