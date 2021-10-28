import streamlit as st


def typesetting_1():
    st.markdown("## 使用要点")

    st.markdown("### 1. 合理设计报文结构 ")
    st.markdown("报文尽量精简，表达完整。参考 RocketMQ：")
    st.code("""
protected static int calMsgLength(int sysFlag, int bodyLength, int topicLength, int propertiesLength) {
    int bornhostLength = (sysFlag & MessageSysFlag.BORNHOST_V6_FLAG) == 0 ? 8 : 20;
    int storehostAddressLength = (sysFlag & MessageSysFlag.STOREHOSTADDRESS_V6_FLAG) == 0 ? 8 : 20;
    final int msgLen = 4 // 4字节消息总长度
        + 4 // 4字节魔数
        + 4 // 4字节CRC校验码
        + 4 // 4字节队列ID
        + 4 // 4字节标记位
        + 8 // 8字节消息队列偏移量
        + 8 // 8字节物理偏移量
        + 4 // 4字节系统标记
        + 8 // 8字节bornt存储时间戳
        + bornhostLength // 8 or 20 字节broken地址 包含端口
        + 8 // 8字节存储时间戳
        + storehostAddressLength // 8 or 20 字节存储地址 包含端口
        + 4 // 4字节消息重试重试次数
        + 8 // 8字节事务消息偏移量
        + 4 + (bodyLength > 0 ? bodyLength : 0) // 4 or bodyLength+4 字节body长度
        + 1 + topicLength // 1字节topic长度与topic内容
        + 2 + (propertiesLength > 0 ? propertiesLength : 0) // 2 or propertiesLength+2 字节消息属性长度
        + 0;
    return msgLen;
}
    """, language="java")
    st.markdown("---")

    st.markdown("### 2. 不要频繁创建 Bootstrap")
    st.markdown("Bootstrap 可以发起多次连接，后续操作可以使用 Channel 进行。")
    st.code("""
Bootstrap bootstrap = new Bootstrap();

bootstrap.group(ctx.channel().eventLoop())
        .channel(NioSocketChannel.class)
        .handler(new SimpleChannelInboundHandler<ByteBuf>() {
            @Override
            protected void channelRead0(ChannelHandlerContext ctx, ByteBuf msg) throws Exception {
                System.out.println("Received data");
            }
        });

Channel channel1 = bootstrap.connect(new InetSocketAddress("127.0.0.1", 9998)).channel();
Channel channel2 = bootstrap.connect(new InetSocketAddress("127.0.0.1", 9999)).channel();
    """, language="java")
    st.markdown("---")

    st.markdown("### 3. 通过 Channel 或 Context 来做数据传输")
    st.markdown("Channel 在Netty中就是一次连接的载体，后续该连接操作都可通过 Channel 进行。Context 可以指定从某个 Context 开始去走后续 OutBoundHandler。")
    st.code("""
//创建Bootstrap
Bootstrap bootstrap = new Bootstrap();

//指定EventLoopGroup以处理客户端事件  需要适用于NIO实现
bootstrap.group(eventExecutors)
        //适用于NIO传输的Channel类型
        .channel(NioSocketChannel.class)
        //在创建Channel时向ChannelPipeline中添加一个Echo-ClientHandler实例
        .handler(new ChannelInitializer<SocketChannel>() {
            @Override
            protected void initChannel(SocketChannel socketChannel) throws Exception {
                socketChannel.pipeline().addLast(new EchoClientHandler());
            }
        });

Channel channel = bootstrap.connect(new InetSocketAddress("127.0.0.1", 8888)).channel();
channel.writeAndFlush("Hello, Channel - 8888!");
ChannelHandlerContext context = channel.pipeline().context(EchoClientHandler.class);
if (Objects.nonNull(context)) {
    context.writeAndFlush("Hello, Context - 8888!");
}

Channel channel1 = bootstrap.connect(new InetSocketAddress("127.0.0.1", 9999)).channel();
channel1.writeAndFlush("Hello, 9999!");
    """, language="java")
    st.markdown("---")

    st.markdown("### 4. 注意使用 @Sharable 时的线程安全问题")
    st.markdown("共享 Handler 通常使用在全局统计中，如统计连接数量。使用该类型 Handler 时需要注意临界资源并发问题。")
    st.code("""
@ChannelHandler.Sharable
public class SharableHandler extends ChannelInboundHandlerAdapter {

    private static final AtomicLong REQ_COUNT = new AtomicLong(0);

    public static long getReqCount() {
        return REQ_COUNT.get();
    }

    @Override
    public void channelActive(ChannelHandlerContext ctx) throws Exception {
        // 连接激活时统计连接数
        REQ_COUNT.getAndIncrement();
        ctx.fireChannelActive();
    }
}
    """, language="java")
    st.markdown("---")

    st.markdown("### 5. 做中转连接时复用 EventLoop")
    st.code("""
public class BootstrapHandler extends SimpleChannelInboundHandler<ByteBuf> {

    private ChannelFuture connect;

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) throws Exception {
        super.exceptionCaught(ctx, cause);
    }

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, ByteBuf msg) throws Exception {
        //连接成功后执行操作
        if (connect.isDone()){

        }
    }

    //在handler中创建客户端发起其他连接   使用同一个EventLoopGroup
    @Override
    public void channelActive(ChannelHandlerContext ctx) throws Exception {
        Bootstrap bootstrap = new Bootstrap();

        bootstrap.group(ctx.channel().eventLoop())
                .channel(NioSocketChannel.class)
                .handler(new SimpleChannelInboundHandler<ByteBuf>() {
                    @Override
                    protected void channelRead0(ChannelHandlerContext ctx, ByteBuf msg) throws Exception {
                        System.out.println("Received data");
                    }
                });

        connect = bootstrap.connect(new InetSocketAddress("127.0.0.1", 9998));
        connect.addListener(new ChannelFutureListener() {
            @Override
            public void operationComplete(ChannelFuture future) throws Exception {
                if (future.isSuccess()){
                    System.out.println("连接成功");
                } else {
                    System.out.println("连接失败");
                    future.cause().printStackTrace();
                }
            }
        });
    }
}
    """, language="java")
    st.markdown("---")

    st.markdown("### 6. 通过EventLoop执行定时任务")
    st.markdown("EventLoop 本身具有 ScheduledExecutorService 相关功能，在 Handler 中如需创建定时任务可通过 EventLoop 执行。")
    st.code("""
public class EventLoopScheduleHandler extends ChannelInboundHandlerAdapter {

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
        //通过EventLoop执行定时任务
        Channel channel = ctx.channel();

        //60秒后Runnable实例将由分配给channel的EventLoop执行
        ScheduledFuture<?> schedule = channel
                .eventLoop()
                .schedule(() -> System.out.println("测试EventLoop.schedule()"), 60, TimeUnit.SECONDS);

        //每60秒执行一次
        ScheduledFuture<?> future = channel.eventLoop()
                .scheduleAtFixedRate(() -> System.out.println("每60秒执行一次"), 60, 60, TimeUnit.SECONDS);

        //取消定时任务
        schedule.cancel(false);
        future.cancel(false);
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) throws Exception {
        super.exceptionCaught(ctx, cause);
    }
}
    """, language="java")
    st.markdown("---")

    st.markdown("文章展示源码均为 ** 4.1 ** 版本")


def use_points():
    typesetting_1()
