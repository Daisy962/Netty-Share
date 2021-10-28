import streamlit as st


def typesetting_1():
    st.markdown("** Netty 零拷贝技术是其重要特征之一，“零拷贝”是指计算机操作的过程中，CPU不需要为数据在内存之间的拷贝消耗资源。而它通常是指计算机在网络上发送文"
                "件时，不需要将文件内容拷贝到用户空间（User Space）而直接在内核空间（Kernel Space）中传输到网络的方式。零拷贝不仅提高了应用程序的性能，而且减少了内核态和用户态上下文切换。**")

    st.markdown("# 传统Read/Write模式")
    st.markdown("** 传统模式数据Copy方法： **")
    st.image("./images/zero_copy/img.png", width=700)
    st.markdown("""
    从上图可以看出，拷贝的操作需要4次用户模式和内核模式之间的上下文切换，而且在操作完成前数据被复制了4次。
    """)
    st.markdown("** 传统模式上下文切换： **")
    st.image("./images/zero_copy/img_1.png", width=700)
    st.markdown("** 从图中可以看出文件经历了4次copy过程： **")
    st.markdown("""
        1. 首先，调用read方法，文件从user模式拷贝到了kernel模式；（用户模式->内核模式的上下文切换，在内部发送sys_read() 从文件中读取数据，存储到一个内核地址空间缓存区中）\n
        2. 之后CPU控制将kernel模式数据拷贝到user模式下；（内核模式-> 用户模式的上下文切换，read()调用返回，数据被存储到用户地址空间的缓存区中）\n
        3. 调用write时候，先将user模式下的内容copy到kernel模式下的socket的buffer中（用户模式->内核模式，数据再次被放置在内核缓存区中，send（）套接字调用）\n
        4. 最后将kernel模式下的socket buffer的数据copy到网卡设备中；（send套接字调用返回）\n
        5. 从图1中看，两次copy是多余的，数据从kernel模式到user模式走了一圈，浪费了2次copy。
    """)
    st.markdown("---")

    st.markdown("# NIO零拷贝模式")
    st.markdown("** Netty 中零拷贝技术是通过 DefaultFileRegion 来实现的，本质上是封装了 NIO 包的 FileChannel，源码如下：**")
    st.code("""
public class DefaultFileRegion extends AbstractReferenceCounted implements FileRegion {
    ....

    @Override
    public long transferTo(WritableByteChannel target, long position) throws IOException {
        long count = this.count - position;
        if (count < 0 || position < 0) {
            throw new IllegalArgumentException(
                    "position out of range: " + position +
                    " (expected: 0 - " + (this.count - 1) + ')');
        }
        if (count == 0) {
            return 0L;
        }
        if (refCnt() == 0) {
            throw new IllegalReferenceCountException(0);
        }
        // Call open to make sure fc is initialized. This is a no-oop if we called it before.
        open();

        // 此处通过NIO包 FileChannel 的 transferTo(long position, long count, WritableByteChannel target)
        // 方法进行发送
        long written = file.transferTo(this.position + position, count, target);
        if (written > 0) {
            transferred += written;
        } else if (written == 0) {
            // If the amount of written data is 0 we need to check if the requested count is bigger then the
            // actual file itself as it may have been truncated on disk.
            //
            // See https://github.com/netty/netty/issues/8868
            validate(this, position);
        }
        return written;
    }

    ....
}
    """, language="java")

    st.markdown("** JDK NIO中 FileChannel 的 transferTo(long position, long count, WritableByteChannel target) "
                "方法实现依赖于操作系统底层的 sendFile() 实现的： **")
    st.image("./images/zero_copy/img_4.png", width=700)
    st.markdown("** 底层调用sendFile方法： **")
    st.code("""
#include <sys/socket.h>
ssize_t sendfile(int out_fd, int in_fd, off_t *offset, size_t count);
    """, language="c++")

    st.markdown("** 零拷贝模式数据Copy方法： **")
    st.image("./images/zero_copy/img_2.png", width=700)

    st.markdown("** 零拷贝模式上下文切换： **")
    st.image("./images/zero_copy/img_3.png", width=700)

    st.markdown("** 使用了zero-copy技术后，整个过程如下： **")
    st.markdown("""
    1. transferTo()方法使得文件的内容直接copy到了一个read buffer（kernel buffer）中\n
    2. 然后数据（kernel buffer）copy到socket buffer中\n
    3. 最后将socket buffer中的数据copy到网卡设备（protocol engine）中传输
    """)
    st.markdown("这个显然是一个伟大的进步：这里上下文切换从4次减少到2次，同时把数据copy的次数从4次降低到3次；")
    st.markdown("** 但是这是zero-copy么，答案是否定的! **")
    st.markdown("---")


def typesetting_2():
    st.markdown("# Linux内核对零拷贝的优化")
    st.markdown("** Linux 2.1 内核开始引入sendfile函数，用于将文件通过socket传输。**")
    st.code("""
sendfile(socket, file, len);
    """, language="c++")
    st.markdown("该函数通过一次系统调用完成了文件的传输，减少了原来read/write方式的模式切换。此外更是减少了数据的copy，sendfile的详细过程如图：")
    st.image("./images/zero_copy/img_5.png", width=700)
    st.markdown("""
    ** 通过sendfile传送文件只需要一次系统调用，当调用sendfile时：**\n
    1. 首先通过DMA将数据从磁盘读取到kernel buffer中\n
    2. 然后将kernel buffer数据拷贝到socket buffer中\n
    3. 最后将socket buffer中的数据copy到网卡设备中（protocol buffer）发送
    """)

    st.markdown("sendfile与read/write模式相比，少了一次copy。但是从上述过程中发现从kernel buffer中将数据copy到socket buffer是没有必要的。Linux2.4 "
                "内核对sendfile做了改进，如图：")
    st.image("./images/zero_copy/img_6.png", width=700)
    st.markdown("""
    ** 改进后的处理过程如下：**\n
    1. 将文件拷贝到kernel buffer中；(DMA引擎将文件内容copy到内核缓存区)\n
    2. 向socket buffer中追加当前要发送的数据在kernel buffer中的位置和偏移量\n
    3. 根据socket buffer中的位置和偏移量直接将kernel buffer的数据copy到网卡设备（protocol engine）中
    """)

    st.markdown("从图中看到，** linux 2.1内核中的 “数据被copy到socket buffer” 的动作，在Linux2.4 "
                "内核做了优化，取而代之的是只包含关于数据的位置和长度的信息的描述符被追加到了socket buffer 缓冲区中。DMA引擎直接把数据从内核缓冲区传输到协议引擎（protocol "
                "engine），从而消除了最后一次CPU copy。**经过上述过程，数据只经过了2次copy就从磁盘传送出去了。这个才是真正的Zero-Copy("
                "** 这里的零拷贝是针对kernel来讲的，数据在kernel模式下是Zero-Copy **)。")
    st.markdown("正是Linux2.4的内核做了改进，Java中的TransferTo()实现了Zero-Copy,如下图：")
    st.image("./images/zero_copy/img_7.png", width=700)


def zero_copy():
    typesetting_1()
    typesetting_2()
