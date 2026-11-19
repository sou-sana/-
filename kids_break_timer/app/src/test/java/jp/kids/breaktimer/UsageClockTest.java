package jp.kids.breaktimer;

import static org.junit.Assert.*;

import org.junit.Test;

public class UsageClockTest {
    static final long MIN = 60_000L;
    static final long T0 = 1_700_000_000_000L;

    /** stepMs ごとに tick しながら durationMs 進める */
    private long run(UsageClock c, long start, long durationMs, long stepMs, boolean inUse) {
        long t = start;
        while (t < start + durationMs) {
            t += stepMs;
            c.tick(t, inUse);
        }
        return t;
    }

    @Test
    public void breakStartsAfter45MinutesOfUse() {
        UsageClock c = new UsageClock(45 * MIN, 15 * MIN);
        c.tick(T0, true);
        long t = run(c, T0, 44 * MIN, 10_000, true);
        assertFalse(c.isOnBreak(t));
        t = run(c, t, MIN, 10_000, true);
        assertTrue(c.isOnBreak(t));
        assertEquals(15 * MIN, c.breakRemainingMs(t));
    }

    @Test
    public void breakLasts15MinutesThenUsageResets() {
        UsageClock c = new UsageClock(45 * MIN, 15 * MIN);
        c.tick(T0, true);
        long t = run(c, T0, 45 * MIN, 10_000, true);
        assertTrue(c.isOnBreak(t));
        // 休憩中に画面を付けていても休憩時間は実時間で減る
        t = run(c, t, 14 * MIN, 10_000, true);
        assertTrue(c.isOnBreak(t));
        t = run(c, t, MIN, 10_000, true);
        assertFalse(c.isOnBreak(t));
        assertEquals(0, c.usedMs);
        // また45分使える
        t = run(c, t, 44 * MIN, 10_000, true);
        assertFalse(c.isOnBreak(t));
    }

    @Test
    public void screenOffTimeDoesNotCount() {
        UsageClock c = new UsageClock(45 * MIN, 15 * MIN);
        c.tick(T0, true);
        long t = run(c, T0, 30 * MIN, 10_000, true);
        t = run(c, t, 10 * MIN, 10_000, false); // 10分OFF（休憩時間未満）
        assertEquals(30 * MIN, c.usedMs);
        t = run(c, t, 14 * MIN, 10_000, true);
        assertFalse(c.isOnBreak(t));
        t = run(c, t, MIN, 10_000, true);
        assertTrue(c.isOnBreak(t));
    }

    @Test
    public void longScreenOffCountsAsRest() {
        UsageClock c = new UsageClock(45 * MIN, 15 * MIN);
        c.tick(T0, true);
        long t = run(c, T0, 40 * MIN, 10_000, true);
        t = run(c, t, 15 * MIN, 10_000, false);
        assertEquals(0, c.usedMs);
    }

    @Test
    public void bigGapWhileOffResetsEvenWithoutTicks() {
        // 電源OFF・再起動などでtickが来なかった場合
        UsageClock c = new UsageClock(45 * MIN, 15 * MIN);
        c.tick(T0, true);
        long t = run(c, T0, 40 * MIN, 10_000, true);
        t += 3 * 60 * MIN;
        c.tick(t, false);
        assertEquals(0, c.usedMs);
    }

    @Test
    public void bigGapDoesNotAddHugeUsage() {
        UsageClock c = new UsageClock(45 * MIN, 15 * MIN);
        c.tick(T0, true);
        c.tick(T0 + 30 * MIN, true);
        assertEquals(UsageClock.MAX_TICK_MS, c.usedMs);
    }

    @Test
    public void clockSetBackwardDoesNotExtendBreak() {
        UsageClock c = new UsageClock(45 * MIN, 15 * MIN);
        c.tick(T0, true);
        long t = run(c, T0, 45 * MIN, 10_000, true);
        assertTrue(c.isOnBreak(t));
        // 時計を巻き戻しても休憩は最大15分のまま
        long back = t - 120 * MIN;
        c.tick(back, true);
        assertTrue(c.isOnBreak(back));
        assertTrue(c.breakRemainingMs(back) <= 15 * MIN);
    }

    @Test
    public void parentResetEndsBreak() {
        UsageClock c = new UsageClock(45 * MIN, 15 * MIN);
        c.tick(T0, true);
        long t = run(c, T0, 45 * MIN, 10_000, true);
        c.reset(t);
        assertFalse(c.isOnBreak(t));
        assertEquals(0, c.usedMs);
    }
}
