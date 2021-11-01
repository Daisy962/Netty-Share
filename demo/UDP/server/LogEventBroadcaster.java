package com.example.jmh.nettytest.udp.server;

import com.example.jmh.nettytest.udp.handler.LogEventEncoder;
import com.example.jmh.nettytest.udp.po.LogEvent;
import io.netty.bootstrap.Bootstrap;
import io.netty.channel.Channel;
import io.netty.channel.ChannelOption;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.nio.NioDatagramChannel;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.net.InetSocketAddress;

/**
 * @auther liuhe
 * @className LogEventBroadcaster
 * @description UDP服务端启动类
 * @date 2021/4/28 7:17 下午
 */
public class LogEventBroadcaster {

    private final EventLoopGroup group;

    private final Bootstrap bootstrap;

    private final File file;

    public LogEventBroadcaster(InetSocketAddress address, File file) {
        this.group = new NioEventLoopGroup();
        this.bootstrap = new Bootstrap();

        bootstrap.group(group)
                //引导该NioDatagramChannel(无连接的)
                .channel(NioDatagramChannel.class)
                //设置广播模式
                .option(ChannelOption.SO_BROADCAST, true)
                .handler(new LogEventEncoder(address));

        this.file = file;
    }

    public void run() throws InterruptedException, IOException {
        Channel channel = bootstrap.bind(0).sync().channel();

        //文件读取标记位置
        long pointer = 0;

        for (;;) {
            long length = file.length();
            if (length < pointer) {
                //如果有必要  将文件指针设置到该文件的最后一个字节
                pointer = length;
            } else if (length > pointer){
                RandomAccessFile file = new RandomAccessFile(this.file, "r");

                //设置当前文件指针  以确保没有任何旧日志被发送
                file.seek(pointer);

                String line;
                while ((line = file.readLine()) != null) {
                    //对每个日志条目写入一个LogEvent到Channel中
                    channel.writeAndFlush(new LogEvent(this.file.getAbsolutePath(), line));
                }

                //更新文件指针
                pointer = file.getFilePointer();
                file.close();
            }

            try {
                //休眠1秒  如果被中断则退出循环  否则继续处理文件
                Thread.sleep(1000);
            } catch (InterruptedException exception) {
                Thread.interrupted();
                break;
            }
        }
    }

    public void stop() {
        group.shutdownGracefully();
    }

    public static void main(String[] args) {
        LogEventBroadcaster logEventBroadcaster = new LogEventBroadcaster(
                new InetSocketAddress("255.255.255.255", 7777),
                // 配置为监听的log
                new File("/Users/liuhe/Desktop/py/test.log"));

        try {
            logEventBroadcaster.run();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            logEventBroadcaster.stop();
        }
    }
}
