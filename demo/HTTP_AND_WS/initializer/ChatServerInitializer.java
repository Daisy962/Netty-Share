package com.example.jmh.nettytest.websocket.initializer;

import com.example.jmh.nettytest.websocket.handler.HttpRequestHandler;
import com.example.jmh.nettytest.websocket.handler.TextWebSocketFrameHandler;
import io.netty.channel.Channel;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.group.ChannelGroup;
import io.netty.handler.codec.http.HttpObjectAggregator;
import io.netty.handler.codec.http.HttpRequestDecoder;
import io.netty.handler.codec.http.HttpRequestEncoder;
import io.netty.handler.codec.http.HttpServerCodec;
import io.netty.handler.codec.http.websocketx.WebSocketFrameDecoder;
import io.netty.handler.codec.http.websocketx.WebSocketFrameEncoder;
import io.netty.handler.codec.http.websocketx.WebSocketServerProtocolHandler;
import io.netty.handler.stream.ChunkedWriteHandler;

/**
 * @auther liuhe
 * @className ChatServerInitializer
 * @description TODO
 * @date 2021/4/26 1:22 下午
 *
 * HTTP请求时的管线：
 *          ___________________________ 
 *         ｜                          ｜
 *         ｜{@link HttpRequestDecoder}｜ 
 *         ｜__________________________｜
 *
 *          ___________________________
 *         ｜                          ｜
 *         ｜{@link HttpRequestEncoder}｜
 *         ｜__________________________｜
 *
 *         _____________________________
 *        ｜                            ｜
 *        ｜{@link HttpObjectAggregator}｜
 *        ｜____________________________｜
 *
 *          ___________________________
 *         ｜                          ｜
 *         ｜{@link HttpRequestHandler}｜
 *         ｜__________________________｜
 *
 *     _______________________________________
 *    ｜                                      ｜   
 *    ｜{@link WebSocketServerProtocolHandler}｜   
 *    ｜______________________________________｜
 *
 *       __________________________________        
 *      ｜                                 ｜      
 *      ｜{@link TextWebSocketFrameHandler}｜      
 *      ｜_________________________________｜
 *
 * WebSocket请求时的管线：
 *         ______________________________
 *        ｜                             ｜
 *        ｜{@link WebSocketFrameDecoder}｜
 *        ｜_____________________________｜
 *
 *         ______________________________
 *        ｜                             ｜
 *        ｜{@link WebSocketFrameEncoder}｜
 *        ｜_____________________________｜
 *
 *     _______________________________________
 *    ｜                                      ｜
 *    ｜{@link WebSocketServerProtocolHandler}｜
 *    ｜______________________________________｜
 *
 *       __________________________________
 *      ｜                                 ｜
 *      ｜{@link TextWebSocketFrameHandler}｜
 *      ｜_________________________________｜
 *
 *  当 WebSocket 协议升级完成之后
 *  WebSockertServerProtocolHandler将会把HttpRequestDecoder替换为WebSocketFrameDecoder
 *  将HttpResponseEncoder替换为WebSocketFrameEncoder
 *  为了性能最大化它将移除任何不再被WebSocket连接所需要的ChannelHandler
 *  包括HttpObjectAggregator和HttpRequestHandler
 */
public class ChatServerInitializer extends ChannelInitializer<Channel> {

    private final ChannelGroup channelGroup;

    public ChatServerInitializer(ChannelGroup channelGroup) {
        this.channelGroup = channelGroup;
    }

    @Override
    protected void initChannel(Channel ch) throws Exception {
        ch.pipeline()
                //HTTP消息编解码器  将字节解码为HttpRequest,HttpContent和LastHttpContent
                //并将HttpRequest,HttpContent和LastHttpContent编码为字节
                .addLast(new HttpServerCodec())
                //写一个文件内容
                .addLast(new ChunkedWriteHandler())
                //将一个HttpMessage和跟随它的多个HttpContent聚合为单个FullHttpRequest或者FullHttpResponse(取决于它是
                //被用来处理请求还是响应) 安装这个之后  管线中的下一个Handler将只会收到完整的Http请求或响应
                .addLast(new HttpObjectAggregator(64 * 1024))
                //处理FullHttpRequest(那些不发送到 /ws URL的请求)
                .addLast(new HttpRequestHandler("/ws"))
                //按照WebSocket规范的要求  处理WebSocket升级握手,PingWebSocketFrame,PongWebSocketFrame和
                //CloseWebSocketFrame等消息
                .addLast(new WebSocketServerProtocolHandler("/ws"))
                //处理TextWebSocketFrame和握手完成事件
                .addLast(new TextWebSocketFrameHandler(channelGroup));
    }
}
