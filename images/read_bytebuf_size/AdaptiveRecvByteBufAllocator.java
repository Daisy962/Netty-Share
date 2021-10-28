/**
 * The {@link RecvByteBufAllocator} that automatically increases and
 * decreases the predicted buffer size on feed back.
 * <p>RecvByteBufAllocator是一个对buffer的大小根据反馈自动自动增长或者减少的这么一个类。
 * It gradually increases the expected number of readable bytes if the previous
 * read fully filled the allocated buffer.  It gradually decreases the expected
 * number of readable bytes if the read operation was not able to fill a certain
 * amount of the allocated buffer two times consecutively.  Otherwise, it keeps
 * returning the same prediction.
 * 如果前一次的缓冲区的申请大小满了，那么本次会自动增加容量，同样的道理如果上2次没有填满，那么本次的容量会减少。
 * */
public class AdaptiveRecvByteBufAllocator extends DefaultMaxMessagesRecvByteBufAllocator {

    static final int DEFAULT_MINIMUM = 64;
    static final int DEFAULT_INITIAL = 1024;
    static final int DEFAULT_MAXIMUM = 65536;

    private static final int INDEX_INCREMENT = 4;
    private static final int INDEX_DECREMENT = 1;

    private static final int[] SIZE_TABLE;

    // 静态代码块的作用是对SIZE_TABLE数组填写1~38的坐标的值是16，32，48....一直到65536
    // 自动减少或者增加的幅度就是来自于这个数组。具体逻辑在HandleImpl对的record方法。
    static {
        List<Integer> sizeTable = new ArrayList<Integer>();
        // 1~16的设置是16到（512-16）
        for (int i = 16; i < 512; i += 16) {
            sizeTable.add(i);
        }

        // 从512到65536
        for (int i = 512; i > 0; i <<= 1) {
            sizeTable.add(i);
        }

        // 填写到SIZE_TABLE数组
        SIZE_TABLE = new int[sizeTable.size()];
        for (int i = 0; i < SIZE_TABLE.length; i ++) {
            SIZE_TABLE[i] = sizeTable.get(i);
        }
    }

    /**
     * Creates a new predictor with the default parameters.  With the default
     * parameters, the expected buffer size starts from {@code 1024}, does not
     * go down below {@code 64}, and does not go up above {@code 65536}.
     */
    public AdaptiveRecvByteBufAllocator() {
        // 默认是是DEFAULT_MINIMUM（也是最小值，即64）
        // 初始大小DEFAULT_INITIAL（即1024），
        // 最大值是DEFAULT_MAXIMUM（即65536）
        this(DEFAULT_MINIMUM, DEFAULT_INITIAL, DEFAULT_MAXIMUM);
    }

....

    private final class HandleImpl extends MaxMessageHandle {
        private final int minIndex;
        private final int maxIndex;
        private int index;
        private int nextReceiveBufferSize;
        private boolean decreaseNow;

        public HandleImpl(int minIndex, int maxIndex, int initial) {
            this.minIndex = minIndex;
            this.maxIndex = maxIndex;

            // getSizeTableIndex()是一个二分算法，获取最贴近数值的容量下标
            /*
                private static int getSizeTableIndex(final int size) {
                   for (int low = 0, high = SIZE_TABLE.length - 1;;) {
                        if (high < low) {
                            return low;
                        }
                        if (high == low) {
                            return high;
                        }

                        int mid = low + high >>> 1;
                        int a = SIZE_TABLE[mid];
                        int b = SIZE_TABLE[mid + 1];
                        if (size > b) {
                            low = mid + 1;
                        } else if (size < a) {
                            high = mid - 1;
                        } else if (size == a) {
                            return mid;
                        } else {
                            return mid + 1;
                        }
                    }
                }
             */
            index = getSizeTableIndex(initial);
            nextReceiveBufferSize = SIZE_TABLE[index];
        }

        @Override
        // 得到预测值
        public int guess() {
            return nextReceiveBufferSize;
        }

       // 计算预测值
        private void record(int actualReadBytes) {
            if (actualReadBytes <= SIZE_TABLE[Math.max(0, index - INDEX_DECREMENT - 1)]) {
                if (decreaseNow) {
                    index = Math.max(index - INDEX_DECREMENT, minIndex);
                    nextReceiveBufferSize = SIZE_TABLE[index];
                    decreaseNow = false;
                } else {
                    decreaseNow = true;
                }
            } else if (actualReadBytes >= nextReceiveBufferSize) {
                index = Math.min(index + INDEX_INCREMENT, maxIndex);
                nextReceiveBufferSize = SIZE_TABLE[index];
                decreaseNow = false;
            }
        }

        @Override
        public void readComplete() {
            record(totalBytesRead());
        }
    }

....