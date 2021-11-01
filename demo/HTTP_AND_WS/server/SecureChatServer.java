package com.example.jmh.nettytest.websocket.server;

import com.example.jmh.nettytest.websocket.initializer.SecureChatServerInitializer;
import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.Channel;
import io.netty.channel.ChannelFuture;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.group.ChannelGroup;
import io.netty.handler.ssl.SslContext;
import io.netty.handler.ssl.SslContextBuilder;
import io.netty.handler.ssl.util.SelfSignedCertificate;

import javax.net.ssl.SSLException;
import java.net.InetSocketAddress;
import java.security.cert.CertificateException;

/**
 * @auther liuhe
 * @className SecureChatServer
 * @description SSL加密服务端
 * @date 2021/4/27 1:34 下午
 */
public class SecureChatServer extends ChatServer{

    private final SslContext sslContext;

    public SecureChatServer(SslContext sslContext) {
        this.sslContext = sslContext;
    }

    //重写初始化管线方法  使用添加了SSL加密的管线
    @Override
    protected ChannelInitializer<Channel> getInit(ChannelGroup channelGroup) {
        return new SecureChatServerInitializer(channelGroup, sslContext);
    }

    public static void main(String[] args) throws CertificateException, SSLException {
        //获取服务端SSL信息
        SelfSignedCertificate selfSignedCertificate = new SelfSignedCertificate();
        SslContext build = SslContextBuilder.forServer(selfSignedCertificate.certificate(), selfSignedCertificate.privateKey()).build();

        final SecureChatServer secureChatServer = new SecureChatServer(build);
        ChannelFuture start = secureChatServer.start(new InetSocketAddress(8888));

        Runtime.getRuntime().addShutdownHook(new Thread(secureChatServer::destroy));

        start.channel().closeFuture().syncUninterruptibly();
    }
}
