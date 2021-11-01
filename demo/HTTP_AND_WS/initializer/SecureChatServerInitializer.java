package com.example.jmh.nettytest.websocket.initializer;

import io.netty.channel.Channel;
import io.netty.channel.group.ChannelGroup;
import io.netty.handler.ssl.SslContext;
import io.netty.handler.ssl.SslHandler;

import javax.net.ssl.SSLEngine;

/**
 * @auther liuhe
 * @className SecureChatServerInitializer
 * @description 添加SSL加解密
 * @date 2021/4/27 1:30 下午
 */
public class SecureChatServerInitializer extends ChatServerInitializer{

    private final SslContext context;

    public SecureChatServerInitializer(ChannelGroup channelGroup, SslContext context) {
        super(channelGroup);
        this.context = context;
    }

    @Override
    protected void initChannel(Channel ch) throws Exception {
        super.initChannel(ch);

        //配置SSL编解码器
        SSLEngine sslEngine = context.newEngine(ch.alloc());

        sslEngine.setUseClientMode(false);

        ch.pipeline().addFirst(new SslHandler(sslEngine));
    }
}
