import streamlit as st


def typesetting_1():
    st.markdown("# Netty简介")
    st.markdown("### Netty是一个异步事件驱动的网络应用程序框架，用于快速开发可维护的高性能协议服务器和客户端。JDK原生也有一套网络应用程序API，NIO，但是存在一些问题使得用起来不是很方便，主要如下：")
    st.markdown("1. NIO的类库和API繁杂，使用麻烦。使用时需要熟练掌握Selector、ServerSocketChannel、SocketChannel、ByteBuffer等")
    st.markdown("2. 需要具备其他的额外技能做铺垫。例如熟悉Java多线程编程，因为NIO编程涉及到Reactor模式，你必须对多线程和网络编程非常熟悉，才能编写出高质量的NIO程序")
    st.markdown(
        "3. 可靠性能力补齐，开发工作量和难度都非常大。例如客户端面临断连重连、网络闪断、半包读写、失败缓存、网络拥塞和异常码流的处理等等。NIO编程的特点是功能开发相对容易，但是可靠性能力补齐工作量和难度都非常大")
    st.markdown("4. JDK NIO的Bug。例如臭名昭著的Epoll Bug，它会导致Selector空轮询，最终导致CPU 100%。官方声称在JDK 1.6版本的update "
                "18修复了该问题，但是直到JDK1.7版本该问题仍旧存在，只不过该Bug发生概率降低了一些而已，它并没有被根本解决")
    st.write("")

    st.markdown("### Netty对JDK自带的NIO的API进行封装，解决上述问题，主要特点有：")
    st.markdown("1. 设计优雅，适用于各种传输类型的统一API阻塞和非阻塞Socket；基于灵活且可扩展的事件模型，可以清晰地分析关注点；高度可定制的线程模型-单线程，一个或多个线程池；真正的无连接数据报套接字支持")
    st.markdown("2. 使用方便，详细记录的Javadoc，用户指南和示例；没有其他依赖项，JDK5（Netty3.x）或6 (Netty4.x) 就足够了")
    st.markdown("3. 高性能，吞吐量更高，延迟更低；减少资源消耗；最小化不必要的内存复制")
    st.markdown("4. 安全，完整的SSL/TLS和StartTLS支持")
    st.markdown("5. 社区活跃，不断更新，社区活跃，版本迭代周期短，发现的Bug可以被及时修复，同时，更多的新功能会被加入")
    st.write("")

    st.markdown("### Netty常见的使用场景如下：")
    st.markdown("1. 互联网行业。在分布式系统中，各个节点之间需要远程服务调用，高性能的RPC框架必不可少，Netty作为异步高性能的通信框架，往往作为基础通信组件被这些RPC"
                "框架使用。典型的应用有：阿里分布式服务框架Dubbo的RPC框架使用Dubbo协议进行节点间通信，Dubbo协议默认使用Netty作为基础通信组件，用于实现各进程节点之间的内部通信")
    st.markdown("2. 游戏行业。无论是手游服务端还是大型的网络游戏，Java语言得到了越来越广泛的应用。Netty作为高性能的基础通信组件，它本身提供了TCP/UDP和HTTP"
                "协议栈。非常方便定制和开发私有协议栈，账号登录服务器，地图服务器之间可以方便的通过Netty进行高性能的通信")
    st.markdown("3. 大数据领域。经典的Hadoop的高性能通信和序列化组件Avro的RPC框架，默认采用Netty进行跨节点通信，它的Netty Service基于Netty框架二次封装实现")
    st.markdown("---")


def typesetting_2():
    st.markdown("# Reactor模式的实现")
    st.markdown("### 关于Java NIO 构造Reator模式，Doug lea在《Scalable IO in Java》中给了很好的阐述，这里截取PPT对Reator模式的实现进行说明")
    st.markdown("### 1. 第一种实现模型如下：")
    st.image("./images/fundamental/img_1.png", width=700)
    st.markdown("这是最简单的Reactor单线程模型，由于Reactor模式使用的是异步非阻塞IO，所有的IO操作都不会被阻塞，理论上一个线程可以独立处理所有的IO操作。这时Reactor"
                "线程是个多面手，负责多路分离套接字，Accept新连接，并分发请求到处理链中。")
    st.markdown("对于一些小容量应用场景，可以使用到单线程模型。但对于高负载，大并发的应用却不合适，主要原因如下：")
    st.markdown("+ 当一个NIO线程同时处理成百上千的链路，性能上无法支撑，即使NIO线程的CPU负荷达到100%，也无法完全处理消息")
    st.markdown("+ 当NIO线程负载过重后，处理速度会变慢，会导致大量客户端连接超时，超时之后往往会重发，更加重了NIO线程的负载")
    st.markdown("+ 可靠性低，一个线程意外死循环，会导致整个通信系统不可用")
    st.write("")

    st.markdown("### 2. Reactor多线程模型：")
    st.image("./images/fundamental/img_2.png", width=700)
    st.markdown("相比上一种模式，该模型在处理链部分采用了多线程（线程池）")
    st.markdown("在绝大多数场景下，该模型都能满足性能需求。但是，在一些特殊的应用场景下，如服务器会对客户端的握手消息进行安全认证。这类场景下，单独的一个Acceptor"
                "线程可能会存在性能不足的问题。为了解决这些问题，产生了第三种Reactor线程模型")
    st.write("")

    st.markdown("### 3. Reactor主从模型：")
    st.image("./images/fundamental/img_3.png", width=700)
    st.markdown("该模型相比第二种模型，是将Reactor分成两部分，mainReactor负责监听server "
                "socket，accept新连接；并将建立的socket分派给subReactor。subReactor负责多路分离已连接的socket，读写网络数据，对业务处理功能，其扔给worker"
                "线程池完成。通常，subReactor个数上可与CPU个数等同。")
    st.markdown("---")

    st.markdown("** Netty模型为该模型的变种，这也是Netty NIO的默认模式。**")


def typesetting_3():
    st.markdown("# Netty核心组件及设计")
    # Bootstrap 与 ServerBootstrap
    st.markdown("### 1. Bootstrap 与 ServerBootstrap")
    st.markdown("Netty中存在两个Bootstrap，从某种意义上而言可以说是Client端和Server端，他们都继承自AbstractBootstrap。顾名思义，两者是负责不同模式的初始化引导。类结构如下：")
    st.image("./images/fundamental/img_15.png", width=700)
    st.markdown("** AbstractBootstrap中提供了一些方法将Netty的相关组件串联起来： **")
    st.markdown("+ ** group(EventLoopGroup group) **： 提供EventLoop的线程池")
    st.markdown("+ ** channelFactory(io.netty.channel.ChannelFactory<? extends C> channelFactory) **： 创建Channel的工厂")
    st.markdown("+ ** option(ChannelOption<T> option, T value) ** ：Socket 提供相关配置")
    st.markdown("+ ** attr(AttributeKey<T> key, T value) ** ： 附加属性设置")
    st.markdown("+ ** handler(ChannelHandler handler) ** ： 关联Channel处理类")
    st.markdown("+ ** bind() ** ： 服务端执行端口绑定(ServerBootstrap使用，Bootstrap则调用其自身实现connect()方法进行连接)")
    st.markdown("---")

    # ByteBuf
    st.markdown("### 2. ByteBuf")
    st.markdown("ByteBuf是Netty中用于替换NIO的ByteBuffer实现的数据容器，ByteBuf提供了更丰富的API，通过读写下标来对数据进行顺序读写管理。先来看下ByteBuf的定义：")
    st.code("public abstract class ByteBuf implements ReferenceCounted, Comparable<ByteBuf>", language="java")
    st.markdown("ByteBuf实现了两个接口，分别是** ReferenceCounted ** 和** Comparable "
                "**。Comparable是JDK自带的接口，表示该类之间是可以进行比较的。而ReferenceCounted "
                "表示的是对象的引用统计。当一个ReferenceCounted被实例化之后，其引用count=1，每次调用retain() 方法，就会增加count，调用release() "
                "方法又会减少count。当count减为0之后，对象将会被释放，如果试图访问被释放过后的对象，则会报访问异常。")
    st.markdown("如果一个对象实现了ReferenceCounted，并且这个对象里面包含的其他对象也实现了ReferenceCounted，那么当容器对象的count=0"
                "的时候，其内部的其他对象也会被调用release()方法进行释放。")
    st.markdown("** ByteBuf的读写下标在顺序读写时能够提供准确的数据定位，其实现原理与Kafka的Partition数据同步原理异曲同工。通过下列源码中的注释来理解读写下标的具体作用：**")
    st.markdown("初始状态: ")
    st.image("./images/fundamental/img_16.png", width=700)
    st.markdown("释放已读数据: ")
    st.image("./images/fundamental/img_17.png", width=700)
    st.markdown("清空所有数据: ")
    st.image("./images/fundamental/img_18.png", width=700)
    st.markdown("---")

    # ChannelHandlerContext
    st.markdown("### 3. ChannelHandlerContext")
    st.markdown("ChannelHandlerContext里就包含着ChannelHandler中的上下文信息，每一个ChannelHandler被添加到ChannelPipeline"
                "中都会创建一个与其对应的ChannelHandlerContext。ChannelHandlerContext的功能就是用来管理它所关联的ChannelHandler"
                "和在同一个ChannelPipeline中ChannelHandler的交互。")
    st.markdown("如下图就是ChannelPipeline、Channel、ChannelHandler和ChannelHandlerContext之间的关系")
    st.image("./images/fundamental/img_19.png", width=700)
    st.markdown("ChannelHandlerContext可以做到尽量减少它不感兴趣的ChannelHandler"
                "所带来的的开销，比如某个逻辑只需要某几个处理器，因此可以不用从头开始处理，直接从需要的第一个的ChannelHandler的地方进行处理。")
    st.image("./images/fundamental/img_20.png", width=700)
    st.markdown("** 因为一个ChannelHandler可以同时属于多个ChannelPipeline，因此它也是可以有多个ChannelHandlerContext，这种用法的ChannelHandler"
                "就可以使用@Sharable注解，因此在使用Sharable注解的时候要确定自己的ChannelHandler是线程安全的。 **")
    st.markdown("ChannelHandlerContext默认类型为DefaultChannelHandlerContext，数据结构为双向链表。ChannelHandlerContext"
                "与ChannelPipeline实现了共同父类ChannelInboundInvoker，他们有一套相同API不过返回值不同，Pipeline"
                "处理的是管线级操作，而ChannelHandlerContext返回的为下一个Handler的Context。ChannelHandlerContext的"
                "ChannelPipeline pipeline()方法可以返回与之关联的Pipeline，两者都可使用fireChannelRead()方法来向下一个Handler传输数据。")
    st.markdown("---")

    # ChannelFuture
    st.markdown("### 4. ChannelFuture")
    st.markdown("Netty 中通道上的每个 IO 操作都是无阻塞的，如果使用 Java 库中的 Future 则为了获取结果需要保存每个 Future 做轮询处理，这就是 Netty 拥有自己的 "
                "ChannelFuture 接口的原因。我们可以将回调传递给 ChannelFuture，该回调将在操作完成时被调用。")
    st.image("./images/fundamental/img_21.png", width=700)
    st.markdown("ChannelFuture要么是未完成状态，要么是已完成状态。IO操作刚开始时，将创建一个新的Future对象。新的Future对象最初处于未完成的状态，因为IO"
                "操作尚未完成，所以既不会执行成功、执行失败，也不会取消执行。如果IO"
                "操作因为执行成功、执行失败或者执行取消导致操作完成，则将被标记为已完成的状态，并带有更多特定信息，例如失败原因。")
    st.image("./images/fundamental/img_22.png", width=700)
    st.markdown("** 总结一点：不管是失败还是取消对于Future来说都是属于完成的状态。 **")
    st.markdown("推荐使用addListener(GenericFutureListener)而不是await()，以便在完成IO操作并执行任何后续任务时得到通知。")
    st.image("./images/fundamental/img_23.png", width=700)
    st.markdown("addListener(GenericFutureListener)是非阻塞的。它只是将指定的ChannelFutureListener添加到ChannelFuture，并且与将来关联的IO"
                "操作完成时，IO线程将通知监听器。ChannelFutureListener完全不阻塞，因此可产生最佳的性能和资源利用率，但是如果不习惯事件驱动的编程，则实现顺序逻辑可能会比较棘手。")
    st.markdown("相反，await()是阻塞操作。一旦被调用，调用者线程将阻塞直到操作完成。使用await("
                ")实现顺序逻辑比较容易，但是调用者线程会不必要地阻塞直到完成IO操作为止，并且线程间通知的成本相对较高。** 此外，在特定情况下还可能出现死锁。 **")
    st.markdown("---")

    # EventLoop 与 EventLoopGroup
    st.markdown("### 5. EventLoop 与 EventLoopGroup")
    st.markdown("EventLoop在Netty中扮演着相当重要的角色，其实现类无论是NioEventLoop还是EpollEventLoop类结构基本一致，本身既有SingleThreadEventExecutor"
                "功能又具有ScheduledExecutorService相关功能。类结构如下: ")
    st.image("./images/fundamental/img_4.png", width=700)
    st.markdown("EventLoopGroup负责管理内部注册的EventLoop，两者协作构成了Netty处理线程模型：")
    st.image("./images/fundamental/img_5.png", width=700)
    st.markdown("---")

    # Channel 与 EventLoop
    st.markdown("### 6. Channel 与 EventLoop")
    st.markdown("Channel负责基本的I/O操作，在基于java的网络编程中，其基本的构造是 Socket，在jdk中Channel是通讯载体，在Netty中Channel被赋予了更多的功能。")
    st.markdown("常用Channel包括** NioSocketChannel、NioServerSocketChannel、EpollSocketChannel与EpollServerSocketChannel "
                "**。以NIO形式Channel举例，类结构如下：")
    st.image("./images/fundamental/img_6.png", width=700)
    st.image("./images/fundamental/img_7.png", width=700)

    st.markdown("在Netty中，Channel可视为一个会话载体(** 类似于Websocket的session **)，在其生命周期中会存在多种不同生命周期流转。")
    st.image("./images/fundamental/img_8.png", width=700)

    st.markdown("** 第一种是服务端用于绑定的channel，或者客户端发起绑定的channel,第二种是服务端接受的SocketChannel **")
    st.markdown("Channel 与 EventLoop 相结合共同构成了链接与处理绑定关系：")
    st.image("./images/fundamental/img_9.png", width=700)
    st.markdown("---")

    # ChannelHandler 与 ChannelPipeline
    st.markdown("### 7. ChannelHandler 与 ChannelPipeline")
    st.markdown("ChannelHandler是Netty处理器统一抽象，其通过子接口ChannelInboundHandler与ChannelOutboundHandler来限定处理方向。ChannelHandler"
                "就是我们在使用Netty时嵌入业务逻辑的地方，常见的编解码器就是通过实现不同方向的Handler来进行编解码处理。ChannelHandler实现关系如下：")
    st.image("./images/fundamental/img_10.png", width=700)
    st.markdown("ChannelHandler初始化在ChannelPipeline中，在整个执行周期中可以动态通过ChannelPipeline添加或删除ChannelHandler。ChannelPipeline"
                "与Channel是唯一性绑定的(** 这种设计使得整个Pipeline的执行是线程安全的 **)。ChannelHandler事件流转方向如下：")
    st.image("./images/fundamental/img_12.png", width=700)
    st.image("./images/fundamental/img_13.png", width=700)
    st.markdown("** 可以看出ChannelHandler的事件流转是通过 ChannelHandlerContext 进行的 **")
    st.markdown("---")

    # 将各组件放在一起来看
    st.markdown("### 8. 将各组件放在一起来看")
    st.markdown("Netty通过卓越的设计和细节优化造就了其超高的并发性能及拓展性，内部各组件在NIO包基础上进行的封装优化，帮助使用者屏蔽掉底层复杂性，专注精力于业务代码开发。从整体来看各组件协作关系如下(** "
                "服务端 **)：")
    st.image("./images/fundamental/img_14.png", width=700)


def fundamental():
    typesetting_1()
    typesetting_2()
