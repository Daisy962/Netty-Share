import streamlit as st


def typesetting_1():
    st.markdown("# 自适应缓冲区分配策略与堆外缓冲区创建")
    st.markdown("### Netty 中 BossGroup 与 WorkerGroup 组 Channel 交互图如下：")
    st.image("./images/read_bytebuf_size/img.png", width=700)

    st.markdown("""
    BossGroup 将得到的 SelectedKyes 中的 Socketchannel 接收到，然后封装成 NioServerSocketChannel,
    NioServerSocketChannel 注册到 WorkerGroup 里边，最后客户端直接和 WorkerGroup 
    里边的 NioServerSocketChannel 通信交换信息，即 BossGroup 负责派发，WorkerGroup 负责真正数据的处理。
    """)
    st.markdown("---")

    st.markdown("** 读缓冲区的自适应分配必然涉及数据读写，我们从 NioServerSocketChannel 开始分析：**")
    with open("./images/read_bytebuf_size/NioServerSocketChannel.java", "r") as file:
        st.code(file.read(), language="java")

    st.markdown("** 进入 DefaultServerSocketChannelConfig 的构造器：**")
    with open("./images/read_bytebuf_size/DefaultServerSocketChannelConfig.java", "r") as file:
        st.code(file.read(), language="java")

    st.markdown("** DefaultChannelConfig 构造器：**")
    st.code("""
public DefaultChannelConfig(Channel channel) {
    // Channel是NioServerSocketChannel 
    this(channel, new AdaptiveRecvByteBufAllocator());
}
    """, language="java")

    st.markdown("** 这里见到一个新的类 AdaptiveRecvByteBufAllocator，适配的字节缓冲器：**")
    with open("./images/read_bytebuf_size/AdaptiveRecvByteBufAllocator.java", "r") as file:
        st.code(file.read(), language="java")

    st.markdown("** 进入 HandleImpl 的父类 MaxMessageHandle 之中，里边有一个申请缓冲区的重要方法： **")
    st.code("""
@Override
public ByteBuf allocate(ByteBufAllocator alloc) {
    // guess()方法得到预测值，用来设置当前缓冲区的大小
    return alloc.ioBuffer(guess());
}
    """, language="java")

    st.markdown("** alloc.ioBuffer(）有很多实现方法，我们拿 AbstractByteBufAllocator 举例。进入 AbstractByteBufAllocator ：**")
    st.code("""
/**
 PlatformDependent.hasUnsafe()会根据是否存在io.netty.noUnsafe配置返回boolean,
 如果是android系统返回false。
 */
public ByteBuf ioBuffer(int initialCapacity) {
    if (PlatformDependent.hasUnsafe()) {
        // 获取直接内存缓冲区(堆外)
        return directBuffer(initialCapacity);
    }
    // 获取堆缓冲区
    return heapBuffer(initialCapacity);
}
    """)

    st.markdown("** 两个申请方法链路较长，直接截取最底层实现： **")
    st.markdown("directBuffer(initialCapacity)：")
    st.code("""
// 可以看出Netty的直接内存申请是通过NIO的ByteBuffer来实现的
protected ByteBuffer allocateDirect(int initialCapacity) {
    return ByteBuffer.allocateDirect(initialCapacity);
}
    """, language="java")

    st.markdown("heapBuffer(initialCapacity)：")
    st.code("""
byte[] allocateArray(int initialCapacity) {
    return new byte[initialCapacity];
}
    """)
    st.markdown("---")


def typesetting_2():
    st.markdown("# 堆外缓冲区回收")
    st.markdown("从上述文章中能够看出 Netty 中堆外缓冲区是通过 NIO 的 DirectByteBuffer "
                "来实现的，由于 JVM 中 GC 不负责堆外区域的内存申请与回收，所以直接内存的申请与释放是通过 Unsafe "
                "类的 allocateMemory 方法和 freeMemory 方法来实现的，且对于直接内存的释放，必须手工调用 freeMemory 方法。")
    st.code("""
public static ByteBuffer allocateDirect(int capacity) {
    return new DirectByteBuffer(capacity);
}
    """, language="java")

    st.markdown("""
    ** DirectByteBuffer 直接内存的申请：** \n
    在 DirectByteBuffer 实例通过构造方法创建的时候，会通过 Unsafe 类的 allocateMemory 方法帮我们申请直接内存资源。
    """)

    st.markdown("""
    ** DirectByteBuffer 直接内存的释放：** \n
    DirectByteBuffer 本身是一个Java对象，其是位于堆内存中的，JDK 的 GC 机制可以自动帮我们回收，但是其申请的直接内存，不再 GC 范围之内，
    无法自动回收。好在 JDK 提供了一种机制，可以为堆内存对象注册一个钩子函数(其实就是实现 Runnable 接口的子类)，当堆内存对象被 GC 回收的时候，
    会回调 run 方法，我们可以在这个方法中执行释放 DirectByteBuffer 引用的直接内存，即在 run 方法中调用 Unsafe 的 freeMemory 
    方法。注册是通过** sun.misc.Cleaner **类来实现的。 
    """)
    st.code("""
class DirectByteBuffer extends MappedByteBuffer  implements DirectBuffer{
    ....
    // 构造方法
    DirectByteBuffer(int cap) {                   // package-private
    
        super(-1, 0, cap, cap);
        boolean pa = VM.isDirectMemoryPageAligned();
        int ps = Bits.pageSize();
        // 对申请的直接内存大小，进行重新计算
        long size = Math.max(1L, (long)cap + (pa ? ps : 0));
        Bits.reserveMemory(size, cap);
    
        long base = 0;
        try {
            // 分配直接内存，base表示的是直接内存的开始地址
            base = unsafe.allocateMemory(size);
        } catch (OutOfMemoryError x) {
            // 记录JDK已经使用的直接内存的数量，当分配直接内存时，需要进行增加，当释放时，需要减少
            Bits.unreserveMemory(size, cap);
            throw x;
        }
        unsafe.setMemory(base, size, (byte) 0);
        if (pa && (base % ps != 0)) {
            // Round up to page boundary
            address = base + ps - (base & (ps - 1));
        } else {
            address = base;
        }
        
        // 注册钩子函数，释放直接内存。
        // 此处 this 将创建的 DirectByteBuffer 作为删除标记（也就是当前DirectByteBuffer被回收的时候，回调Deallocator的run方法）
        cleaner = Cleaner.create(this, new Deallocator(base, size, cap));
        att = null;
    
    }
    ....
}
    """, language="java")
    st.markdown("""
    ** 可以看到构造方法中的确是用了 unsafe.allocateMemory 方法帮我们分配了直接内存，另外，在构造方法的最后，通过 Cleaner.create 方法注册了一个钩子函数，用于清除直接内存的引用。**
    """)

    st.markdown("** Deallocator 就是用于清除 DirectByteBuffer 引用的直接内存，代码如下所示：**")
    st.code("""
private static class Deallocator implements Runnable {
 
    private static Unsafe unsafe = Unsafe.getUnsafe();
 
    private long address;
    private long size;
    private int capacity;
 
    // address -> 堆外内存地址  
    private Deallocator(long address, long size, int capacity) {
        assert (address != 0);
        this.address = address;
        this.size = size;
        this.capacity = capacity;
    }
 
    public void run() {
        if (address == 0) {
            // Paranoia
            return;
        }
        // 清除直接内存
        unsafe.freeMemory(address);
        address = 0;
        // 记录JDK已经使用的直接内存的数量，当分配直接内存时，需要进行增加，当释放时，需要减少
        Bits.unreserveMemory(size, capacity);
    }
 
}
    """, language="java")

    st.markdown("""
    ** 通过上面代码的分析，我们事实上可以认为 Bits 类是直接内存的分配担保，当有足够的直接内存可以用时，增加直接内存应用计数，否则，调用System.gc，
    进行垃圾回收，需要注意的是，System.gc只会回收堆内存中的对象，但是我们前面已经讲过，DirectByteBuffer 对象被回收时，那么其引用的直接内存
    也会被回收，试想现在刚好有其他的 DirectByteBuffer 可以被回收，那么其被回收的直接内存就可以用于本次 DirectByteBuffer 直接内存的分配。**
    """)

    st.markdown("""
    因此我们经常看到有一些文章讲解在使用NIO的时候，不要禁用 
    System.gc，也就是启动JVM的时候，不要传入-XX:+DisableExplicitGC参数，因为这样可能会造成直接内存溢出。道理很明显，因为直接内存的释放与获取比堆内存更加耗时，每次创建 
    DirectByteBuffer 实例分配直接内存的时候，都 调用System.gc，可以让已经使用完的 DirectByteBuffer 得到及时的回收。 
    """)


def read_bytebuf_size():
    typesetting_1()
    typesetting_2()
