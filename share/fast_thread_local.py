import streamlit as st


def typesetting_1():
    st.markdown("# FastThreadLocal")
    st.markdown("Netty 设计之初就需要充分考虑超高并发场景，在高并发下每一项优化都至关重要。其实现需要大量依赖线程变量，研发团队认为以"
                "线性探测和再哈希算法实现的 ThreadLocal 有可优化之处，FastThreadLocal 应运而生。** FastThreadLocal 舍弃掉了 ThreadLocal "
                "的 HashTable 形式存储，改用数组存储，并通过下标访问，这就是两者的根本区别。 ** FastThreadLocal 在正确使用的情况下(** 通过 FastThreadLocalThread "
                "配合使用 **)性能比 ThreadLocal 快将近三倍，而如果通过普通 Thread 访问 FastThreadLocal 性能反而比 ThreadLocal 慢。")
    st.markdown("---")

    st.markdown("## 使用示例：")
    st.code("""
import io.netty.util.concurrent.FastThreadLocal;
import io.netty.util.concurrent.FastThreadLocalThread;


public class FastThreadLocalTest {
    private static FastThreadLocal<Integer> fastThreadLocal = new FastThreadLocal<>();

    public static void main(String[] args) {

        //if (thread instanceof FastThreadLocalThread) 使用FastThreadLocalThread更优，普通线程也可以
        new FastThreadLocalThread(() -> {
            for (int i = 0; i < 100; i++) {
                fastThreadLocal.set(i);
                System.out.println(Thread.currentThread().getName() + "====" + fastThreadLocal.get());
                try {
                    Thread.sleep(200);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }, "fastThreadLocal1").start();


        new FastThreadLocalThread(() -> {
            for (int i = 0; i < 100; i++) {
                System.out.println(Thread.currentThread().getName() + "====" + fastThreadLocal.get());
                try {
                    Thread.sleep(200);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }, "fastThreadLocal2").start();
    }
}
    """, language="java")

    st.markdown("** 测试结果：**")
    st.image("./images/fast_thread_local/img.png", width=700)

    st.markdown("** 可以看到 FastThreadLocal 在使用上与 ThreadLocal 差不多，只是不再需要手动 remove()，这是因为 FastThreadLocalThread "
                "帮我们做了这些处理：**")
    st.code("""
public FastThreadLocalThread(Runnable target, String name) {
    // 所有通过 FastThreadLocalThread 调用的 Runnable 都需要经过一层静态代理封装
    super(FastThreadLocalRunnable.wrap(target), name);
    cleanupFastThreadLocals = true;
}
    """, language="java")

    st.code("""
package io.netty.util.concurrent;

import io.netty.util.internal.ObjectUtil;

final class FastThreadLocalRunnable implements Runnable {
    private final Runnable runnable;

    private FastThreadLocalRunnable(Runnable runnable) {
        this.runnable = ObjectUtil.checkNotNull(runnable, "runnable");
    }

    @Override
    public void run() {
        try {
            // 执行原本的 Runnable
            runnable.run();
        } finally {
            // 删除线程数据
            FastThreadLocal.removeAll();
        }
    }

    static Runnable wrap(Runnable runnable) {
        return runnable instanceof FastThreadLocalRunnable ? runnable : new FastThreadLocalRunnable(runnable);
    }
}
    """, language="java")
    st.markdown("---")


def typesetting_2():
    st.markdown("## 原理解析：")
    st.markdown("** 参考文章 **: [Netty源码-FastThreadLocal原理](https://www.jianshu.com/p/6adfa89ed06e)")


def fast_thread_local():
    typesetting_1()
    typesetting_2()
