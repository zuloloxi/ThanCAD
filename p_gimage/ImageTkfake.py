"A fake ImageTk module in case ImageTk is not available."
import tkinter


def PhotoImage(im1):
    """This function returns a fake replacement of ImagTk.PhotoImage object.

    Since PhotoImage(im1) is compatible to Tkinter.PhotoImage, we return
    a Tkinter.PhotoImage."""
    return tkinter.PhotoImage(data=floppy())


def floppy(): return '\
    R0lGODlhMAAwAMZFAAAAAAAAEREAABEAEQARAAARERERERERIiIRIiIRMzMRMxEiIhEiMyIiIiIi\
    MyIiRDMiMzMiRDMiVUQiVSIzMyIzRDMzRDMzVTMzZkQzVUQzZkQzd1UzZjNEVTNEZkREVUREZkRE\
    d1VEZlVEd0RVZlVVVVVVZlVVd2ZmZoh3iIh3u4iId4iIiIiIqpmIu4iZqpmZqpmZu6qZu4iqqpmq\
    u6qqqqqqu6qqzLuqzLuq3aq7u7u7zLu73cy73bvMzLvM3czMzMzM3d3M3czd3d3d3f//////////\
    ////////////////////////////////////////////////////////////////////////////\
    ////////////////////////////////////////////////////////////////////////////\
    /////////////////////////////////////////////////////////////////////////yH+\
    EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAH8ALAAAAAAwADAAAAf+gH+Cg4SFhoeIiYQojI2Oj5CR\
    kpCGk5aXmCiFjACdnSUjJikrLCyjpaempKqoq6clnp0OMIOcAAQBBDAkI0W+v8DBwsIjJAAOD8hD\
    tSidAgADL6HD1NW/JiMACQ7cQswAuQMFu73W5sGhx8kPy4K2A9DSJuf0viYixw4QDkTfAQX/yNWj\
    V0ydsm/QCESbNtAcNgARHET05q6ZOHECG1pLJ7FChHZ/OCk0sHCexmr3IErk9+3iOF4nqxWs8MAj\
    SE4kScqLSe1hxAgRKIa0WOCAgYw80ZkA4LGChJvNcpZMKiwl0AgW+lUEYMDAgZflqP6aGcEpVK4D\
    vO4Uey0bVqz+QjkZPXAAKdt0Ti08/ebVAIK1bItYtYBV61AAdOnaFTtTQoULZ/36BczWp14LcZsl\
    XrCYKt4LoCMjOPA3VI7AOVJKuGxY7oIDnHmROE01h2wAoEN/I01aXqjf2IIDHy68eLbVEi5k1rYg\
    QfMav3lhk14suvXp1nHnhvxtAYLvzWOJH0+e/AQLoCdcaN3MuXMHDBIw4EYfGTIKycrqd8rf8fbt\
    GZx1gHsNJFCgA9two8BKPzEI1GXIQXiBehko9417CM5H3zrIPODhfmU5FuF/F2BwgQYnnlXgitsk\
    qA+DDHr0IFYRnlchhRdUyN4x8WlYHwwvwDADkEISOWSQRxb+iSQMAFSIogYqGtgifTCwaKWUV65Y\
    g3BNnpjBcvLVt84LCfzQgw9BmImmmmn2EEQPO+Bgww1FVLfUiR5A+c2BLu5T5ZnAlADEmT0MOmic\
    NsgQg2Ch4KNBBhp8sCM3HK4zQwJoFlHCpgCc2eabPsh5Aw2LnnBbBxqgehaC9C0Y0Z9AaMqpD4XW\
    iqiiLrzA6EOPaqDBcpV2FAGZZsoKy6dwikrqCy3UKR0Aeea5Kjf7NPinD8YCYGiyicaQawvNBueo\
    ryDsWClNHl2a6aawEBrqnMu28EKpt0ULwqoN/vQArNnSequ3zLbgAg27ZqMBCAcDK+wD+hHLQ7bc\
    jhoDs/N10oCDs+nkCcIGIIV0TL4PVomDDtn++63ANuCww66OgsBBuYYwVROIl+pwAyyeKDuxvDHQ\
    cEOmpha0MQghdDzIxwx7ZEGVMiRKQ9NQAwzuwCr3METBABy8AQhCFRIBEUQMAXY/JSSVAw9nqyA2\
    2Iq07fbbhQQCADs='
