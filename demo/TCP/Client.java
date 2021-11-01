package com.example.jmh.nettytest.test;

import ch.qos.logback.core.util.TimeUtil;
import com.example.jmh.nettytest.handler.EchoClientHandler;
import io.netty.bootstrap.Bootstrap;
import io.netty.buffer.ByteBuf;
import io.netty.channel.*;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.SocketChannel;
import io.netty.channel.socket.nio.NioSocketChannel;
import io.netty.handler.codec.MessageToByteEncoder;

import java.net.InetSocketAddress;
import java.util.concurrent.TimeUnit;

/**
 * @auther liuhe
 * @className Client
 * @description TODO
 * @date 2021/5/6 7:49 下午
 */
public class Client {

    public static void main(String[] args) throws InterruptedException {
        EventLoopGroup eventExecutors = new NioEventLoopGroup();
        try {
            //创建Bootstrap
            Bootstrap bootstrap = new Bootstrap();

            //指定EventLoopGroup以处理客户端事件  需要适用于NIO实现
            bootstrap.group(eventExecutors)
                    //适用于NIO传输的Channel类型
                    .channel(NioSocketChannel.class)
                    //设置服务器的连接地址
                    .remoteAddress(new InetSocketAddress("127.0.0.1", 9999))
                    //在创建Channel时向ChannelPipeline中添加一个Echo-ClientHandler实例
                    .handler(new ChannelInitializer<Channel>() {
                        @Override
                        protected void initChannel(Channel ch) throws Exception {
                            ch.pipeline().addLast(new MessageToByteEncoder<String>() {
                                @Override
                                protected void encode(ChannelHandlerContext ctx, String msg, ByteBuf out) throws Exception {
                                    out.writeBytes(msg.getBytes());
                                }
                            });
                        }
                    });

            //连接
            ChannelFuture channelFuture = bootstrap.connect().addListener((ChannelFutureListener) future -> {
                if (future.isSuccess()) {
                    System.out.println("连接成功");
                } else {
                    System.out.println("连接失败");
                }
            }).sync();

            //连接到远程节点  阻塞等待直到连接完成
//            ChannelFuture sync = bootstrap.connect();

            //阻塞直到Channel关闭
            Channel channel = channelFuture.channel();

            channel.writeAndFlush("Hello");
            channel.writeAndFlush("Netty");

//            TimeUnit.SECONDS.sleep(3);

            channel.writeAndFlush("你好");
            channel.writeAndFlush("NIO");

            channelFuture.sync();
        } finally {
            //关闭线程池并释放所有资源
            eventExecutors.shutdownGracefully().sync();
        }
    }

}
