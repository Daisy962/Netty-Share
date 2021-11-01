package com.example.jmh.nettytest.websocket.handler;

import io.netty.channel.*;
import io.netty.handler.codec.http.*;
import io.netty.handler.ssl.SslHandler;
import io.netty.handler.stream.ChunkedNioFile;

import java.io.File;
import java.io.RandomAccessFile;
import java.net.URISyntaxException;
import java.net.URL;

/**
 * @auther liuhe
 * @className HttpRequestHandler
 * @description 聊天室服务器Handler  可处理HTTP及WebSocket请求
 * @date 2021/4/25 7:00 下午
 */
public class HttpRequestHandler extends SimpleChannelInboundHandler<FullHttpRequest> {

    private final String wsUri;
    private final static File INDEX = new File("/Users/liuhe/Desktop/py/index.html");

    public HttpRequestHandler(String wsUri) {
        this.wsUri = wsUri;
    }

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, FullHttpRequest request) throws Exception {
        if (wsUri.equalsIgnoreCase(request.uri())) {
            //如果请求了WebSocket  则增加引用计数(调用retain()方法) 并将请求传递给下一个InboundHandler
            ctx.fireChannelRead(request.retain());
        } else {
            //Http请求处理
            if (HttpUtil.is100ContinueExpected(request)){
                //符合100 Continue请求以符合HTTP 1.1规范
                send100Continue(ctx);
            }

            //读取文件
            RandomAccessFile file = new RandomAccessFile(INDEX, "r");

            //获取Http响应体
            HttpResponse defaultHttpResponse = new DefaultHttpResponse(request.protocolVersion(), HttpResponseStatus.OK);

            //设置请求头
            defaultHttpResponse.headers().set(HttpHeaderNames.CONTENT_TYPE, "text/html; charset=UTF-8");

            //如果请求添加了keep-alive属性  则添加需要的Header
            boolean keepAlive = HttpUtil.isKeepAlive(request);
            if (keepAlive) {
                defaultHttpResponse.headers().set(HttpHeaderNames.CONTENT_LENGTH, file.length());
                defaultHttpResponse.headers().set(HttpHeaderNames.CONNECTION, HttpHeaderValues.KEEP_ALIVE);
            }

            //将HttpResponse写到客户端(不进行刷新)
            ctx.write(defaultHttpResponse);

            //判断是否通过SSL加密
            if (ctx.pipeline().get(SslHandler.class) == null) {
                //如果不需要加解密或压缩  可以将文件内容存储到DefaultFileRegion中来达到最佳性能 (零Copy实现  不加载到内存)
                ctx.write(new DefaultFileRegion(file.getChannel(), 0, file.length()));
            } else {
                //使用ChunkedNioFile加载文件方便加解密或压缩
                ctx.write(new ChunkedNioFile(file.getChannel()));
            }

            ChannelFuture channelFuture = ctx.writeAndFlush(LastHttpContent.EMPTY_LAST_CONTENT);

            if (!keepAlive) {
                //如果没有请求 keep-alive 则在写操作完成后关闭Channel
                channelFuture.addListener(ChannelFutureListener.CLOSE);
            }
        }
    }

    private static void send100Continue(ChannelHandlerContext channelHandlerContext) {
        DefaultHttpResponse defaultHttpResponse = new DefaultHttpResponse(HttpVersion.HTTP_1_1, HttpResponseStatus.CONTINUE);
        channelHandlerContext.writeAndFlush(defaultHttpResponse);
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) throws Exception {
        cause.printStackTrace();
        ctx.close();
    }
}
