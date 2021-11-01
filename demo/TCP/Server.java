package com.example.jmh.nettytest.test;

import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.ChannelFuture;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.SocketChannel;
import io.netty.channel.socket.nio.NioServerSocketChannel;

import java.net.InetSocketAddress;

/**
 * @auther liuhe
 * @className Server
 * @description TODO
 * @date 2021/5/6 7:49 下午
 */
public class Server {

    public static void main(String[] args) throws InterruptedException {
        //创建Event-LoopGroup
        EventLoopGroup boss = new NioEventLoopGroup();
        EventLoopGroup work = new NioEventLoopGroup();

        try {
            //创建Bootstrap
            ServerBootstrap serverBootstrap = new ServerBootstrap();
            serverBootstrap.group(boss, work)
                    //指定所使用的NIO传输Channel
                    .channel(NioServerSocketChannel.class)
                    //使用指定端口设置套接字地址
                    .localAddress(new InetSocketAddress(9999))
                    //添加一个EchoServerHandler到子Channel的ChannelPipeline
                    .childHandler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        protected void initChannel(SocketChannel socketChannel) throws Exception {
                            //EchoServerHandler被标注为@Sharable，所以我们可以总是使用同样的实例
                            socketChannel.pipeline().addLast(new ByteBufPrintHandler());
                        }
                    });

            //异步的绑定服务器  调用sync()方法阻塞等待直到绑定完成
            ChannelFuture sync = serverBootstrap.bind().sync();

            //获取Channel的CloseFuture  并阻塞当前线程直到它完成
            sync.channel().closeFuture().sync();
        } catch (InterruptedException exception) {
            exception.printStackTrace();
        } finally {
            //关闭EventLoopGroup  释放所有的资源
            boss.shutdownGracefully().sync();
            work.shutdownGracefully().sync();
        }
    }

}
