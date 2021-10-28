/**
 * Create a new instance
 * 默认构造器
 */
public NioServerSocketChannel() {
    this(newSocket(DEFAULT_SELECTOR_PROVIDER));
}

/**
 * Create a new instance using the given {@link ServerSocketChannel}.
 * 默认构造器调用带ServerSocketChannel参数的构造器
 */
public NioServerSocketChannel(ServerSocketChannel channel) {
    super(null, channel, SelectionKey.OP_ACCEPT);
    // javaChannel()  是ServerSocketChannel，
    // javaChannel().socket()就是一个ServerSocketChannel得到的ServerSocket。
    config = new NioServerSocketChannelConfig(this, javaChannel().socket());
}

// 获取无参构造器设置的ServerSocketChannel
@Override
protected ServerSocketChannel javaChannel() {
    return (ServerSocketChannel) super.javaChannel();
}

// 紧接着进入NioServerSocketChannelConfig的构造器，
// NioServerSocketChannelConfig是NioServerSocketChannel的内部类。
private final class NioServerSocketChannelConfig extends DefaultServerSocketChannelConfig {
    private NioServerSocketChannelConfig(NioServerSocketChannel channel, ServerSocket javaSocket) {
        super(channel, javaSocket);//调用DefaultServerSocketChannelConfig的构造器
    }

    @Override
    protected void autoReadCleared() {
        clearReadPending();
    }
}