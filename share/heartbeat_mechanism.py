import streamlit as st


def typesetting_1():
    st.markdown("# 使用示例")
    st.markdown("Netty 提供了对心跳机制的天然支持，心跳可以检测远程端是否存活或者活跃，也可作为超时检测来使用。其实现的核心类为 "
                "** IdleStateHandler **，该类实现了 ** ChannelDuplexHandler **，所以本质上来说它即是 InBoundHandler 也是 OutBoundHandler。"
                "我们通过下列代码来初步了解该类使用：")
    st.image("./images/heartbeat_mechanism/img.png", width=700)
    st.markdown("我们在 ChannelPipeline 链中加入了 IdleSateHandler，第一个参数是3，单位是秒，那么这样做的意思就是：** 每隔3秒来检查一下 channelRead "
                "方法被调用的情况，如果在3秒内该链上的 channelRead 方法都没有被触发，就会调用 userEventTriggered 方法并传入 IdleStateEvent 事件。 ** "
                "使用时可以通过监听 IdleStateEvent 事件来做具体业务处理：")
    st.image("./images/heartbeat_mechanism/img_1.png", width=700)
    st.markdown("---")


def typesetting_2():
    st.markdown("# 原理解析")
    st.markdown("** IdleSateHandler 构造参数：**")
    st.code("""
public IdleStateHandler(boolean observeOutput,
        long readerIdleTime, long writerIdleTime, long allIdleTime,
        TimeUnit unit) {
    ObjectUtil.checkNotNull(unit, "unit");

    this.observeOutput = observeOutput;

    // 读超时时间
    if (readerIdleTime <= 0) {
        readerIdleTimeNanos = 0;
    } else {
        readerIdleTimeNanos = Math.max(unit.toNanos(readerIdleTime), MIN_TIMEOUT_NANOS);
    }

    // 写超时时间
    if (writerIdleTime <= 0) {
        writerIdleTimeNanos = 0;
    } else {
        writerIdleTimeNanos = Math.max(unit.toNanos(writerIdleTime), MIN_TIMEOUT_NANOS);
    }

    // 所有类型(读/写)超时时间
    if (allIdleTime <= 0) {
        allIdleTimeNanos = 0;
    } else {
        allIdleTimeNanos = Math.max(unit.toNanos(allIdleTime), MIN_TIMEOUT_NANOS);
    }
}
    """, language="java")
    st.markdown("""
    ** 三个的参数解释如下：**\n
    1. readerIdleTime：读超时时间（即测试端一定时间内未接受到被测试端消息）\n
    2. writerIdleTime：写超时时间（即测试端一定时间内向被测试端发送消息）\n
    3. allIdleTime：所有类型的超时时间
    """)
    st.write("")

    st.markdown("** 涉及事件监听必然要记录最新读写时间，从 write 方法和 channelReadComplete 方法入手：**")
    st.code("""
@Override
public void channelReadComplete(ChannelHandlerContext ctx) throws Exception {
    if ((readerIdleTimeNanos > 0 || allIdleTimeNanos > 0) && reading) {
        // 读取操作只是做了时间记录
        lastReadTime = ticksInNanos();
        reading = false;
    }
    ctx.fireChannelReadComplete();
}

@Override
public void write(ChannelHandlerContext ctx, Object msg, ChannelPromise promise) throws Exception {
    // Allow writing with void promise if handler is only configured for read timeout events.
    if (writerIdleTimeNanos > 0 || allIdleTimeNanos > 0) {
        // 写操作通过事件监听来记录时间
        ctx.write(msg, promise.unvoid()).addListener(writeListener);
    } else {
        ctx.write(msg, promise);
    }
}
    """, language="java")

    st.markdown("** writeListener 实现如下： **")
    st.code("""
// Not create a new ChannelFutureListener per write operation to reduce GC pressure.
private final ChannelFutureListener writeListener = new ChannelFutureListener() {
    @Override
    public void operationComplete(ChannelFuture future) throws Exception {
        lastWriteTime = ticksInNanos();
        firstWriterIdleEvent = firstAllIdleEvent = true;
    }
};
    """, language="java")

    st.markdown("** 很明显超时检测相关代码不在这些方法中，从激活方法 channelActive 入手发现了其初始化核心方法： **")
    st.code("""
@Override
public void channelActive(ChannelHandlerContext ctx) throws Exception {
    // This method will be invoked only if this handler was added
    // before channelActive() event is fired.  If a user adds this handler
    // after the channelActive() event, initialize() will be called by beforeAdd().
    // 该方法在激活、注册或添加处理器时都会调用
    initialize(ctx);
    super.channelActive(ctx);
}
    """, language="java")

    st.markdown("** 这里的 initialize 方法就是 IdleStateHandler 的精髓：**")
    st.code("""
private void initialize(ChannelHandlerContext ctx) {
    // Avoid the case where destroy() is called before scheduling timeouts.
    // See: https://github.com/netty/netty/issues/143
    switch (state) {
    case 1:
    case 2:
        return;
    }

    state = 1;
    initOutputChanged(ctx);

    /*
    // schedule 方法通过 EventExecutor 提交定时任务
    ScheduledFuture<?> schedule(ChannelHandlerContext ctx, Runnable task, long delay, TimeUnit unit) {
        return ctx.executor().schedule(task, delay, unit);
    }
     */
    lastReadTime = lastWriteTime = ticksInNanos();
    if (readerIdleTimeNanos > 0) {
        // ReaderIdleTimeoutTask 读超时检测任务
        readerIdleTimeout = schedule(ctx, new ReaderIdleTimeoutTask(ctx),
                readerIdleTimeNanos, TimeUnit.NANOSECONDS);
    }
    if (writerIdleTimeNanos > 0) {
        // WriterIdleTimeoutTask 写超时检测任务
        writerIdleTimeout = schedule(ctx, new WriterIdleTimeoutTask(ctx),
                writerIdleTimeNanos, TimeUnit.NANOSECONDS);
    }
    if (allIdleTimeNanos > 0) {
        // AllIdleTimeoutTask 所有超时检测任务
        allIdleTimeout = schedule(ctx, new AllIdleTimeoutTask(ctx),
                allIdleTimeNanos, TimeUnit.NANOSECONDS);
    }
}
    """, language="java")

    st.markdown("** ReaderIdleTimeoutTask、WriterIdleTimeoutTask 与 AllIdleTimeoutTask 都是 IdleStateHandler 方法的内部类，以 "
                "ReaderIdleTimeoutTask 为例解析源码：**")
    st.code("""
private final class ReaderIdleTimeoutTask extends AbstractIdleTask {

    ReaderIdleTimeoutTask(ChannelHandlerContext ctx) {
        super(ctx);
    }

    @Override
    protected void run(ChannelHandlerContext ctx) {
        // 获取最后一次读取时间
        long nextDelay = readerIdleTimeNanos;
        if (!reading) {
            // 用当前时间减去最后一次 channelRead 方法调用的时间，假如这个结果是6s，说明最后一次调用
            // channelRead 已经是6s之前的事情了，你设置的是5s，那么nextDelay则为-1，说明超时了
            nextDelay -= ticksInNanos() - lastReadTime;
        }

        if (nextDelay <= 0) {
            // Reader is idle - set a new timeout and notify the callback.
            // 更新读超时检测任务
            readerIdleTimeout = schedule(ctx, this, readerIdleTimeNanos, TimeUnit.NANOSECONDS);

            boolean first = firstReaderIdleEvent;
            firstReaderIdleEvent = false;

            try {
                // 创建读超时事件并通过 ctx.fireUserEventTriggered(evt); 传递给后续 Handler
                IdleStateEvent event = newIdleStateEvent(IdleState.READER_IDLE, first);
                channelIdle(ctx, event);
            } catch (Throwable t) {
                ctx.fireExceptionCaught(t);
            }
        } else {
            // Read occurred before the timeout - set a new timeout with shorter delay.
            // // 更新读超时检测任务
            readerIdleTimeout = schedule(ctx, this, nextDelay, TimeUnit.NANOSECONDS);
        }
    }
}
    """, language="java")

    st.markdown("** 以上就是 Netty 中心跳机制实现原理，其利用了 Handler 特性，将 IdleStateHandler 封装入 ChannelPipeline "
                "中。因为其本身是双向的，所以读写事件都能够监听到。**")


def heartbeat_mechanism():
    typesetting_1()
    typesetting_2()
